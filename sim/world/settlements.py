"""Settlement management for AI-world."""
from __future__ import annotations

from typing import Any, Dict, List, Optional


SETTLEMENT_RULES = {
    "starting_population": 1,
    "food_per_pop_per_tick": 0.25,
    "growth_food_buffer": 3,
    "max_pop_growth_per_tick": 1,
    "surplus_ticks_for_growth": 5,
    "starve_ticks_for_loss": 3,
    "farm_yield_per_tick": 1.5,
    "granary_food_per_tick": 0.5,
    "granary_starve_ticks": 4,
    "mine_stone_per_tick": 0.75,
    "deposit_range_default": 2,
    "deposit_range_with_road": 3,  # E2.2
}


def pos_key(x: int, y: int) -> str:
    return f"{x},{y}"


class SettlementManager:
    def __init__(self, metrics: Dict[str, Any], logger):
        self.settlements: Dict[str, Dict[str, Any]] = {}
        self.struct_to_settlement: Dict[str, str] = {}
        self.metrics = metrics
        self.logger = logger

    def create(self, x, y, owner_id, world, tick) -> str:
        sid = f"s{len(self.settlements) + 1}"
        self.settlements[sid] = {
            "id": sid, "x": x, "y": y, "owner_id": owner_id,
            "population": int(SETTLEMENT_RULES.get("starting_population", 1)),
            "food_stock": 0, "wood_stock": 0, "stone_stock": 0,
            "starve_ticks": 0, "surplus_ticks": 0,
        }
        try:
            tile0 = world.tile_at(x, y)
            starter = min(int(getattr(tile0, "food", 0)), 2)
            self.settlements[sid]["food_stock"] = starter
            if starter > 0:
                tile0.food = int(getattr(tile0, "food", 0)) - starter
        except Exception:
            self.settlements[sid]["food_stock"] = 2
        self.metrics["settlements_created"] += 1
        self.logger.event({"type": "settlement_created", "tick": tick, "settlement": self.settlements[sid]})
        return sid

    def settlement_at_structure(self, x, y, world, tick) -> str:
        k = pos_key(x, y)
        sid = self.struct_to_settlement.get(k)
        if sid:
            return sid
        if not self.settlements:
            sid = self.create(x, y, "system", world, tick)
            self.struct_to_settlement[k] = sid
            return sid
        best_sid = self.nearest(x, y)
        self.struct_to_settlement[k] = best_sid  # type: ignore
        return best_sid  # type: ignore

    def link_structure(self, x, y, owner_id, world, tick) -> str:
        if not self.settlements:
            sid = self.create(x, y, owner_id, world, tick)
            self.struct_to_settlement[pos_key(x, y)] = sid
            return sid
        sid = self.settlement_at_structure(x, y, world, tick)
        s_anchor = self.settlements[sid]
        if abs(x - s_anchor["x"]) + abs(y - s_anchor["y"]) >= 24:
            sid = self.create(x, y, owner_id, world, tick)
        self.struct_to_settlement[pos_key(x, y)] = sid
        return sid

    def nearest(self, x, y) -> Optional[str]:
        if not self.settlements:
            return None
        best_sid, best_d = None, 10**9
        for sid, s in self.settlements.items():
            d = abs(x - s["x"]) + abs(y - s["y"])
            if d < best_d:
                best_d, best_sid = d, sid
        return best_sid

    def distance_to(self, sid, x, y) -> int:
        s = self.settlements[sid]
        return abs(x - s["x"]) + abs(y - s["y"])

    def get(self, sid) -> Dict[str, Any]:
        return self.settlements[sid]

    def all(self) -> List[Dict[str, Any]]:
        return list(self.settlements.values())

    def count(self) -> int:
        return len(self.settlements)

    def structure_settlement_id(self, x, y) -> Optional[str]:
        return self.struct_to_settlement.get(pos_key(x, y))

    def settlement_has_road(self, sid, world) -> bool:
        return self.count_structures_of_type(sid, "road", world) >= 1

    def try_deposit(self, agent, tick, world=None) -> None:
        if not self.settlements:
            return
        nearest_sid = self.nearest(agent.x, agent.y)
        if nearest_sid is None:
            return
        # E2.2: roads extend deposit range
        dep_range = int(SETTLEMENT_RULES.get("deposit_range_default", 2))
        if world is not None and self.settlement_has_road(nearest_sid, world):
            dep_range = int(SETTLEMENT_RULES.get("deposit_range_with_road", 3))
        if self.distance_to(nearest_sid, agent.x, agent.y) > dep_range:
            return
        s = self.settlements[nearest_sid]
        if agent.inv_food > 0:
            deposited = agent.inv_food
            s["food_stock"] += deposited
            agent.inv_food = 0
            self.metrics["food_deposit_events"] += 1
            self.metrics["food_deposited_total"] += deposited
            self.logger.event({"type": "food_deposited", "tick": tick, "agent_id": agent.agent_id,
                               "settlement_id": nearest_sid, "amount": deposited, "food_stock": s["food_stock"]})
        if agent.inv_wood > 0:
            deposited = agent.inv_wood
            s["wood_stock"] += deposited
            agent.inv_wood = 0
            self.metrics["wood_deposit_events"] += 1
            self.metrics["wood_deposited_total"] += deposited
            self.logger.event({"type": "wood_deposited", "tick": tick, "agent_id": agent.agent_id,
                               "settlement_id": nearest_sid, "amount": deposited, "wood_stock": s["wood_stock"]})
        if agent.inv_stone > 0:
            deposited = agent.inv_stone
            s["stone_stock"] += deposited
            agent.inv_stone = 0
            self.metrics["stone_deposit_events"] += 1
            self.metrics["stone_deposited_total"] += deposited
            self.logger.event({"type": "stone_deposited", "tick": tick, "agent_id": agent.agent_id,
                               "settlement_id": nearest_sid, "amount": deposited, "stone_stock": s["stone_stock"]})

    def tick(self, world, tick: int) -> None:
        if not self.settlements:
            return
        cons = float(SETTLEMENT_RULES["food_per_pop_per_tick"])
        buffer_food = float(SETTLEMENT_RULES["growth_food_buffer"])
        max_growth = int(SETTLEMENT_RULES["max_pop_growth_per_tick"])
        surplus_needed = int(SETTLEMENT_RULES.get("surplus_ticks_for_growth", 5))
        starve_needed_default = int(SETTLEMENT_RULES.get("starve_ticks_for_loss", 3))
        yield_per_farm = float(SETTLEMENT_RULES.get("farm_yield_per_tick", 1.5))
        granary_food = float(SETTLEMENT_RULES.get("granary_food_per_tick", 0.5))
        granary_starve = int(SETTLEMENT_RULES.get("granary_starve_ticks", 4))
        mine_stone = float(SETTLEMENT_RULES.get("mine_stone_per_tick", 0.75))

        for sid, s in self.settlements.items():
            pop_before = int(s.get("population", 0))
            stock_at_start = float(s.get("food_stock", 0))
            farms = has_granary = has_mine = 0
            has_granary = has_mine = False
            for stx in world.structures:
                if self.structure_settlement_id(stx.x, stx.y) != sid:
                    continue
                if stx.type == "farm":
                    farms += 1
                elif stx.type == "granary":
                    has_granary = True
                elif stx.type == "mine":
                    has_mine = True

            farm_yield = farms * yield_per_farm if farms > 0 else 0.0
            bonus = granary_food if has_granary else 0.0
            if farm_yield > 0 or bonus > 0:
                s["food_stock"] = stock_at_start + farm_yield + bonus
                if farm_yield > 0:
                    self.metrics["farm_harvest_events"] += 1
                    self.metrics["farm_food_total"] += farm_yield
                if bonus > 0:
                    self.metrics["granary_food_total"] = self.metrics.get("granary_food_total", 0) + bonus
            if has_mine:
                s["stone_stock"] = float(s.get("stone_stock", 0)) + mine_stone
                self.metrics["mine_stone_total"] = self.metrics.get("mine_stone_total", 0) + mine_stone

            post_harvest = float(s.get("food_stock", 0))
            need = pop_before * cons
            starve_needed = granary_starve if has_granary else starve_needed_default
            if "surplus_ticks" not in s:
                s["surplus_ticks"] = 0
            if "starve_ticks" not in s:
                s["starve_ticks"] = 0

            if pop_before <= 0:
                s["starve_ticks"] = s["surplus_ticks"] = 0
            elif post_harvest >= need:
                s["food_stock"] = post_harvest - need
                s["starve_ticks"] = 0
                if float(s["food_stock"]) >= (need + buffer_food):
                    s["surplus_ticks"] = int(s.get("surplus_ticks", 0)) + 1
                    if int(s["surplus_ticks"]) >= surplus_needed:
                        s["population"] = pop_before + min(max_growth, 1)
                        s["surplus_ticks"] = 0
                else:
                    s["surplus_ticks"] = 0
            else:
                s["food_stock"] = 0.0
                s["surplus_ticks"] = 0
                s["starve_ticks"] = int(s.get("starve_ticks", 0)) + 1
                if int(s["starve_ticks"]) >= starve_needed:
                    s["population"] = max(0, pop_before - 1)
                    s["starve_ticks"] = 0

            if pop_before <= 0 and float(s.get("food_stock", 0)) >= (buffer_food + cons * 3):
                s["population"] = 1
                s["starve_ticks"] = s["surplus_ticks"] = 0

            pop_after = int(s.get("population", 0))
            food_after = float(s.get("food_stock", 0))
            if pop_after != pop_before:
                self.metrics["population_net_change"] += pop_after - pop_before
                if pop_after > pop_before:
                    self.metrics["population_grew_events"] += 1
                else:
                    self.metrics["population_starved_events"] += 1
            if pop_after != pop_before or food_after != stock_at_start:
                self.logger.event({
                    "type": "population_changed", "tick": tick, "settlement_id": sid,
                    "population_before": pop_before, "population_after": pop_after,
                    "food_before": stock_at_start, "food_after": food_after,
                    "farm_yield": farm_yield, "granary_bonus": bonus, "need": need,
                    "has_granary": has_granary, "has_mine": has_mine,
                })

    def count_structures_of_type(self, sid, structure_type, world) -> int:
        return sum(1 for stx in world.structures
                   if stx.type == structure_type and self.structure_settlement_id(stx.x, stx.y) == sid)
