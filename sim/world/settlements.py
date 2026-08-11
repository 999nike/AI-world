"""Settlement management for AI-world.

Extracted from simloop.py in P1.1.
Owns creation, linkage, deposits, farm harvest, and population dynamics.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple


SETTLEMENT_RULES = {
    "starting_population": 1,
    "food_per_pop_per_tick": 0.25,
    "growth_food_buffer": 2,
    "max_pop_growth_per_tick": 1,
}


def pos_key(x: int, y: int) -> str:
    return f"{x},{y}"


class SettlementManager:
    def __init__(self, metrics: Dict[str, Any], logger):
        self.settlements: Dict[str, Dict[str, Any]] = {}
        self.struct_to_settlement: Dict[str, str] = {}
        self.metrics = metrics
        self.logger = logger

    # ------------------------------------------------------------------
    # Creation & linkage
    # ------------------------------------------------------------------

    def create(self, x: int, y: int, owner_id: str, world, tick: int) -> str:
        sid = f"s{len(self.settlements) + 1}"
        self.settlements[sid] = {
            "id": sid,
            "x": x,
            "y": y,
            "owner_id": owner_id,
            "population": int(SETTLEMENT_RULES.get("starting_population", 1)),
            "food_stock": 0,
            "wood_stock": 0,
            "stone_stock": 0,
            "starve_ticks": 0,
            "surplus_ticks": 0,
        }

        # Starter food so a brand-new settlement doesn't starve before first deposit
        try:
            tile0 = world.tile_at(x, y)
            starter = min(int(getattr(tile0, "food", 0)), 2)
            self.settlements[sid]["food_stock"] = starter
            if starter > 0:
                tile0.food = int(getattr(tile0, "food", 0)) - starter
        except Exception:
            self.settlements[sid]["food_stock"] = 2

        self.metrics["settlements_created"] += 1
        self.logger.event(
            {
                "type": "settlement_created",
                "tick": tick,
                "settlement": self.settlements[sid],
            }
        )
        return sid

    def settlement_at_structure(self, x: int, y: int, world, tick: int) -> str:
        k = pos_key(x, y)
        sid = self.struct_to_settlement.get(k)
        if sid:
            return sid

        if not self.settlements:
            sid = self.create(x, y, owner_id="system", world=world, tick=tick)
            self.struct_to_settlement[k] = sid
            return sid

        best_sid = self.nearest(x, y)
        self.struct_to_settlement[k] = best_sid  # type: ignore
        return best_sid  # type: ignore

    def link_structure(self, x: int, y: int, owner_id: str, world, tick: int) -> str:
        """Link a newly built structure to a settlement (create new if far enough)."""
        if not self.settlements:
            sid = self.create(x, y, owner_id=owner_id, world=world, tick=tick)
            self.struct_to_settlement[pos_key(x, y)] = sid
            return sid

        sid = self.settlement_at_structure(x, y, world, tick)
        s_anchor = self.settlements[sid]
        d = abs(x - s_anchor["x"]) + abs(y - s_anchor["y"])
        if d >= 24:
            sid = self.create(x, y, owner_id=owner_id, world=world, tick=tick)
        self.struct_to_settlement[pos_key(x, y)] = sid
        return sid

    # ------------------------------------------------------------------
    # Queries
    # ------------------------------------------------------------------

    def nearest(self, x: int, y: int) -> Optional[str]:
        if not self.settlements:
            return None
        best_sid = None
        best_d = 10**9
        for sid, s in self.settlements.items():
            d = abs(x - s["x"]) + abs(y - s["y"])
            if d < best_d:
                best_d = d
                best_sid = sid
        return best_sid

    def distance_to(self, sid: str, x: int, y: int) -> int:
        s = self.settlements[sid]
        return abs(x - s["x"]) + abs(y - s["y"])

    def get(self, sid: str) -> Dict[str, Any]:
        return self.settlements[sid]

    def all(self) -> List[Dict[str, Any]]:
        return list(self.settlements.values())

    def count(self) -> int:
        return len(self.settlements)

    def structure_settlement_id(self, x: int, y: int) -> Optional[str]:
        return self.struct_to_settlement.get(pos_key(x, y))

    # ------------------------------------------------------------------
    # Deposits
    # ------------------------------------------------------------------

    def try_deposit(self, agent, tick: int) -> None:
        """Auto-deposit inventory into nearest settlement if within radius 2."""
        if not self.settlements:
            return

        nearest_sid = self.nearest(agent.x, agent.y)
        if nearest_sid is None:
            return

        dist = self.distance_to(nearest_sid, agent.x, agent.y)
        if dist > 2:
            return

        sid = nearest_sid
        s = self.settlements[sid]

        if agent.inv_food > 0:
            deposited = agent.inv_food
            s["food_stock"] += deposited
            agent.inv_food = 0
            self.metrics["food_deposit_events"] += 1
            self.metrics["food_deposited_total"] += deposited
            self.logger.event(
                {
                    "type": "food_deposited",
                    "tick": tick,
                    "agent_id": agent.agent_id,
                    "settlement_id": sid,
                    "amount": deposited,
                    "food_stock": s["food_stock"],
                }
            )

        if agent.inv_wood > 0:
            deposited = agent.inv_wood
            s["wood_stock"] += deposited
            agent.inv_wood = 0
            self.metrics["wood_deposit_events"] += 1
            self.metrics["wood_deposited_total"] += deposited
            self.logger.event(
                {
                    "type": "wood_deposited",
                    "tick": tick,
                    "agent_id": agent.agent_id,
                    "settlement_id": sid,
                    "amount": deposited,
                    "wood_stock": s["wood_stock"],
                }
            )

        if agent.inv_stone > 0:
            deposited = agent.inv_stone
            s["stone_stock"] += deposited
            agent.inv_stone = 0
            self.metrics["stone_deposit_events"] += 1
            self.metrics["stone_deposited_total"] += deposited
            self.logger.event(
                {
                    "type": "stone_deposited",
                    "tick": tick,
                    "agent_id": agent.agent_id,
                    "settlement_id": sid,
                    "amount": deposited,
                    "stone_stock": s["stone_stock"],
                }
            )

    # ------------------------------------------------------------------
    # Population + farm tick
    # ------------------------------------------------------------------

    def tick(self, world, tick: int) -> None:
        if not self.settlements:
            return

        cons = float(SETTLEMENT_RULES["food_per_pop_per_tick"])
        buffer_food = float(SETTLEMENT_RULES["growth_food_buffer"])
        max_growth = int(SETTLEMENT_RULES["max_pop_growth_per_tick"])

        for sid, s in self.settlements.items():
            pop_before = int(s.get("population", 0))
            stock_at_start = float(s.get("food_stock", 0))

            # --- Farm harvest ---
            farms = 0
            for stx in world.structures:
                if stx.type == "farm" and self.structure_settlement_id(stx.x, stx.y) == sid:
                    farms += 1
            farm_yield = farms * 1.0 if farms > 0 else 0.0
            if farm_yield > 0:
                s["food_stock"] = stock_at_start + farm_yield
                self.metrics["farm_harvest_events"] += 1
                self.metrics["farm_food_total"] += farm_yield

            post_harvest = float(s.get("food_stock", 0))
            need = pop_before * cons

            if "surplus_ticks" not in s:
                s["surplus_ticks"] = 0
            if "starve_ticks" not in s:
                s["starve_ticks"] = 0

            # --- True net position after production ---
            # shortfall = cannot fully feed population this tick
            can_fully_feed = post_harvest >= need

            if pop_before <= 0:
                # No population — just hold stock, no starvation logic
                s["starve_ticks"] = 0
                s["surplus_ticks"] = 0
            elif can_fully_feed:
                # Fully fed
                s["food_stock"] = post_harvest - need
                s["starve_ticks"] = 0

                # Growth only if leftover still covers another full need + buffer
                if float(s["food_stock"]) >= (need + buffer_food):
                    s["surplus_ticks"] = int(s.get("surplus_ticks", 0)) + 1
                    if int(s["surplus_ticks"]) >= 3:
                        s["population"] = pop_before + min(max_growth, 1)
                        s["surplus_ticks"] = 0
                else:
                    s["surplus_ticks"] = 0
            else:
                # True deficit tick — cannot fully feed
                s["food_stock"] = 0.0
                s["surplus_ticks"] = 0
                s["starve_ticks"] = int(s.get("starve_ticks", 0)) + 1

                if int(s["starve_ticks"]) >= 3:
                    s["population"] = max(0, pop_before - 1)
                    s["starve_ticks"] = 0

            # Respawn rule: empty settlement recovers if it has enough food banked
            if pop_before <= 0 and float(s.get("food_stock", 0)) >= (buffer_food + (cons * 3)):
                s["population"] = 1
                s["starve_ticks"] = 0
                s["surplus_ticks"] = 0

            pop_after = int(s.get("population", 0))
            food_after = float(s.get("food_stock", 0))

            if pop_after != pop_before:
                self.metrics["population_net_change"] += pop_after - pop_before
                if pop_after > pop_before:
                    self.metrics["population_grew_events"] += 1
                else:
                    self.metrics["population_starved_events"] += 1

            if pop_after != pop_before or food_after != stock_at_start:
                self.logger.event(
                    {
                        "type": "population_changed",
                        "tick": tick,
                        "settlement_id": sid,
                        "population_before": pop_before,
                        "population_after": pop_after,
                        "food_before": stock_at_start,
                        "food_after": food_after,
                        "farm_yield": farm_yield,
                        "need": need,
                    }
                )

    # ------------------------------------------------------------------
    # Helpers used by build governors in simloop
    # ------------------------------------------------------------------

    def count_structures_of_type(self, sid: str, structure_type: str, world) -> int:
        count = 0
        for stx in world.structures:
            if stx.type == structure_type and self.structure_settlement_id(stx.x, stx.y) == sid:
                count += 1
        return count
