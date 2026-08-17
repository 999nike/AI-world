"""Settlement management for AI-world."""
from __future__ import annotations

from typing import Any, Dict, List, Optional


SETTLEMENT_RULES = {
    "starting_population": 1,
    "food_per_pop_per_tick": 0.22,
    "growth_food_buffer": 3,
    "max_pop_growth_per_tick": 1,
    "surplus_ticks_for_growth": 5,
    "starve_ticks_for_loss": 4,
    "farm_yield_per_tick": 1.65,
    "granary_food_per_tick": 0.65,
    "granary_starve_ticks": 5,
    "mine_stone_per_tick": 0.75,
    "deposit_range_default": 2,
    "deposit_range_with_road": 3,
    "workshop_tools_per_tick": 0.4,
    "workshop_farm_bonus": 0.30,
    "workshop_mine_bonus": 0.25,
    "tools_consume_per_boost": 0.5,
    "barracks_soldiers_per_tick": 0.15,
    "command_soldiers_per_tick": 0.10,
    "soldier_food_consume": 0.03,
    "soldier_soft_cap_per_pop": 3.0,
    "soldier_defend_cost": 1.0,
    "raid_interval": 25,
    "raid_min_soldiers": 3.0,
    "raid_cost": 2.0,
    "raid_loot_wood": 3,
    "raid_loot_stone": 2,
    "raid_loot_food": 2,
    "age_up_min_pop": 15,
    "age_up_food_bonus": 5.0,
    "era3_farm_bonus": 0.30,
    "market_wood_per_tick": 0.5,
    "market_stone_per_tick": 0.25,
    "temple_food_per_tick": 0.35,
    "temple_surplus_ticks": 3,
    "academy_knowledge_per_tick": 0.3,
    "library_knowledge_per_tick": 0.2,
    "lab_knowledge_per_tick": 0.40,
    "observatory_knowledge_per_tick": 0.50,
    "foundry_tools_bonus": 0.15,
    "hall_food_per_tick": 0.20,
    "subject_agriculture_cost": 8,
    "subject_craft_cost": 10,
    "subject_organisation_cost": 12,
    "subject_strategy_cost": 15,
    "subject_inquiry_cost": 16,
    "agriculture_farm_bonus": 0.20,
    "craft_tools_bonus": 0.1,
    "organisation_surplus_reduction": 1,
    "strategy_defend_bonus": 0.1,
    "walls_defend_bonus": 0.25,
    "walls_raid_extra_cost": 1.0,
    "age_up4_min_pop": 20,
    "age_up4_food_bonus": 5.0,
    "era4_farm_bonus": 0.15,
    "irrigation_farm_bonus": 0.25,
    # E5.2 post-Observatory knowledge sink
    "discovery_cost": 40,
    "discovery_farm_bonus": 0.08,
    "discovery_max": 8,
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
            "tools_stock": 0.0, "soldiers": 0.0, "knowledge": 0.0,
            "discoveries": 0,
            "subjects": [], "era": 2, "starve_ticks": 0, "surplus_ticks": 0,
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

    def settlement_has_workshop(self, sid, world) -> bool:
        return self.count_structures_of_type(sid, "workshop", world) >= 1

    def settlement_has_barracks(self, sid, world) -> bool:
        return self.count_structures_of_type(sid, "barracks", world) >= 1

    def settlement_has_market(self, sid, world) -> bool:
        return self.count_structures_of_type(sid, "market", world) >= 1

    def settlement_has_temple(self, sid, world) -> bool:
        return self.count_structures_of_type(sid, "temple", world) >= 1

    def settlement_has_academy(self, sid, world) -> bool:
        return self.count_structures_of_type(sid, "academy", world) >= 1

    def settlement_has_walls(self, sid, world) -> bool:
        return self.count_structures_of_type(sid, "walls", world) >= 1

    def settlement_has_irrigation(self, sid, world) -> bool:
        return self.count_structures_of_type(sid, "irrigation", world) >= 1

    def settlement_has_library(self, sid, world) -> bool:
        return self.count_structures_of_type(sid, "library", world) >= 1

    def settlement_has_foundry(self, sid, world) -> bool:
        return self.count_structures_of_type(sid, "foundry", world) >= 1

    def settlement_has_hall(self, sid, world) -> bool:
        return self.count_structures_of_type(sid, "hall", world) >= 1

    def settlement_has_command(self, sid, world) -> bool:
        return self.count_structures_of_type(sid, "command", world) >= 1

    def settlement_has_lab(self, sid, world) -> bool:
        return self.count_structures_of_type(sid, "lab", world) >= 1

    def settlement_has_observatory(self, sid, world) -> bool:
        return self.count_structures_of_type(sid, "observatory", world) >= 1

    def try_deposit(self, agent, tick, world=None) -> None:
        if not self.settlements:
            return
        nearest_sid = self.nearest(agent.x, agent.y)
        if nearest_sid is None:
            return
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
        starve_needed_default = int(SETTLEMENT_RULES.get("starve_ticks_for_loss", 4))
        yield_per_farm = float(SETTLEMENT_RULES.get("farm_yield_per_tick", 1.65))
        granary_food = float(SETTLEMENT_RULES.get("granary_food_per_tick", 0.65))
        granary_starve = int(SETTLEMENT_RULES.get("granary_starve_ticks", 5))
        mine_stone = float(SETTLEMENT_RULES.get("mine_stone_per_tick", 0.75))
        workshop_tools = float(SETTLEMENT_RULES.get("workshop_tools_per_tick", 0.4))
        workshop_farm_bonus = float(SETTLEMENT_RULES.get("workshop_farm_bonus", 0.30))
        workshop_mine_bonus = float(SETTLEMENT_RULES.get("workshop_mine_bonus", 0.25))

        for sid, s in self.settlements.items():
            pop_before = int(s.get("population", 0))
            stock_at_start = float(s.get("food_stock", 0))
            farms = 0
            has_granary = has_mine = has_workshop = has_barracks = has_market = has_temple = has_academy = has_walls = has_irrigation = has_library = has_foundry = has_hall = has_command = has_lab = has_observatory = False
            for stx in world.structures:
                if self.structure_settlement_id(stx.x, stx.y) != sid:
                    continue
                if stx.type == "farm":
                    farms += 1
                elif stx.type == "granary":
                    has_granary = True
                elif stx.type == "mine":
                    has_mine = True
                elif stx.type == "workshop":
                    has_workshop = True
                elif stx.type == "barracks":
                    has_barracks = True
                elif stx.type == "market":
                    has_market = True
                elif stx.type == "temple":
                    has_temple = True
                elif stx.type == "academy":
                    has_academy = True
                elif stx.type == "walls":
                    has_walls = True
                elif stx.type == "irrigation":
                    has_irrigation = True
                elif stx.type == "library":
                    has_library = True
                elif stx.type == "foundry":
                    has_foundry = True
                elif stx.type == "hall":
                    has_hall = True
                elif stx.type == "command":
                    has_command = True
                elif stx.type == "lab":
                    has_lab = True
                elif stx.type == "observatory":
                    has_observatory = True

            subjects = list(s.get("subjects") or [])
            era = int(s.get("era", 2))
            discoveries = int(s.get("discoveries", 0))

            farm_yield = farms * yield_per_farm if farms > 0 else 0.0
            if has_workshop and farm_yield > 0:
                farm_yield += farms * workshop_farm_bonus
            if era >= 3 and farms > 0:
                farm_yield += farms * float(SETTLEMENT_RULES.get("era3_farm_bonus", 0.30))
            if era >= 4 and farms > 0:
                farm_yield += farms * float(SETTLEMENT_RULES.get("era4_farm_bonus", 0.15))
            if "agriculture" in subjects and farms > 0:
                farm_yield += farms * float(SETTLEMENT_RULES.get("agriculture_farm_bonus", 0.20))
            if has_irrigation and farms > 0:
                farm_yield += farms * float(SETTLEMENT_RULES.get("irrigation_farm_bonus", 0.25))
            if discoveries > 0 and farms > 0:
                farm_yield += farms * discoveries * float(SETTLEMENT_RULES.get("discovery_farm_bonus", 0.08))

            bonus = granary_food if has_granary else 0.0
            if farm_yield > 0 or bonus > 0:
                s["food_stock"] = stock_at_start + farm_yield + bonus
                if farm_yield > 0:
                    self.metrics["farm_harvest_events"] += 1
                    self.metrics["farm_food_total"] += farm_yield
                if bonus > 0:
                    self.metrics["granary_food_total"] = self.metrics.get("granary_food_total", 0) + bonus
            if has_mine:
                stone_add = mine_stone + (workshop_mine_bonus if has_workshop else 0.0)
                s["stone_stock"] = float(s.get("stone_stock", 0)) + stone_add
                self.metrics["mine_stone_total"] = self.metrics.get("mine_stone_total", 0) + stone_add
            if has_workshop or has_foundry:
                tools_add = 0.0
                if has_workshop:
                    tools_add += workshop_tools
                    if "craft" in subjects:
                        tools_add += float(SETTLEMENT_RULES.get("craft_tools_bonus", 0.1))
                if has_foundry:
                    tools_add += float(SETTLEMENT_RULES.get("foundry_tools_bonus", 0.15))
                s["tools_stock"] = float(s.get("tools_stock", 0.0)) + tools_add
                self.metrics["workshop_tools_total"] = self.metrics.get("workshop_tools_total", 0) + tools_add

            soldiers_now = float(s.get("soldiers", 0.0))
            pop_for_cap = max(1, pop_before)
            soft_cap = pop_for_cap * float(SETTLEMENT_RULES.get("soldier_soft_cap_per_pop", 3.0))
            recruit_scale = 1.0
            if soldiers_now >= soft_cap:
                recruit_scale = 0.15
            elif soldiers_now >= soft_cap * 0.7:
                recruit_scale = 0.4

            if has_barracks:
                barracks_soldiers = float(SETTLEMENT_RULES.get("barracks_soldiers_per_tick", 0.15)) * recruit_scale
                s["soldiers"] = soldiers_now + barracks_soldiers
                soldiers_now = float(s["soldiers"])
                self.metrics["barracks_soldiers_total"] = self.metrics.get("barracks_soldiers_total", 0) + barracks_soldiers
            if has_command:
                cmd_soldiers = float(SETTLEMENT_RULES.get("command_soldiers_per_tick", 0.10)) * recruit_scale
                s["soldiers"] = soldiers_now + cmd_soldiers
                soldiers_now = float(s["soldiers"])
                self.metrics["command_soldiers_total"] = self.metrics.get("command_soldiers_total", 0) + cmd_soldiers

            if has_market:
                mw = float(SETTLEMENT_RULES.get("market_wood_per_tick", 0.5))
                ms = float(SETTLEMENT_RULES.get("market_stone_per_tick", 0.25))
                s["wood_stock"] = float(s.get("wood_stock", 0) or 0) + mw
                s["stone_stock"] = float(s.get("stone_stock", 0) or 0) + ms
                self.metrics["market_wood_total"] = self.metrics.get("market_wood_total", 0) + mw
                self.metrics["market_stone_total"] = self.metrics.get("market_stone_total", 0) + ms
            if has_temple:
                tf = float(SETTLEMENT_RULES.get("temple_food_per_tick", 0.35))
                s["food_stock"] = float(s.get("food_stock", 0) or 0) + tf
                self.metrics["temple_food_total"] = self.metrics.get("temple_food_total", 0) + tf
            if has_hall:
                hf = float(SETTLEMENT_RULES.get("hall_food_per_tick", 0.20))
                s["food_stock"] = float(s.get("food_stock", 0) or 0) + hf
                self.metrics["hall_food_total"] = self.metrics.get("hall_food_total", 0) + hf

            k_add = 0.0
            if has_academy:
                k_add += float(SETTLEMENT_RULES.get("academy_knowledge_per_tick", 0.3))
            if has_library:
                k_add += float(SETTLEMENT_RULES.get("library_knowledge_per_tick", 0.2))
            if has_lab:
                k_add += float(SETTLEMENT_RULES.get("lab_knowledge_per_tick", 0.40))
            if has_observatory:
                k_add += float(SETTLEMENT_RULES.get("observatory_knowledge_per_tick", 0.50))
            if k_add > 0:
                s["knowledge"] = float(s.get("knowledge", 0.0)) + k_add
                self.metrics["academy_knowledge_total"] = self.metrics.get("academy_knowledge_total", 0) + k_add
                if has_academy:
                    self._try_unlock_subjects(sid, s, tick)
                if has_observatory:
                    self._try_discovery(sid, s, tick)

            post_harvest = float(s.get("food_stock", 0))
            soldiers_now = float(s.get("soldiers", 0.0))
            soldier_upkeep = soldiers_now * float(SETTLEMENT_RULES.get("soldier_food_consume", 0.03))
            need = pop_before * cons + soldier_upkeep
            starve_needed = granary_starve if has_granary else starve_needed_default
            local_surplus_needed = int(SETTLEMENT_RULES.get("temple_surplus_ticks", 3)) if has_temple else surplus_needed
            if "organisation" in subjects:
                local_surplus_needed = max(1, local_surplus_needed - int(SETTLEMENT_RULES.get("organisation_surplus_reduction", 1)))
            if has_hall:
                local_surplus_needed = max(1, local_surplus_needed - 1)

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
                    if int(s["surplus_ticks"]) >= local_surplus_needed:
                        s["population"] = pop_before + min(max_growth, 1)
                        s["surplus_ticks"] = 0
                else:
                    s["surplus_ticks"] = 0
            else:
                s["food_stock"] = 0.0
                s["surplus_ticks"] = 0
                s["starve_ticks"] = int(s.get("starve_ticks", 0)) + 1
                if int(s["starve_ticks"]) >= starve_needed:
                    soldiers = float(s.get("soldiers", 0.0))
                    defend_cost = float(SETTLEMENT_RULES.get("soldier_defend_cost", 1.0))
                    if "strategy" in subjects:
                        defend_cost = max(0.5, defend_cost - float(SETTLEMENT_RULES.get("strategy_defend_bonus", 0.1)))
                    if has_walls:
                        defend_cost = max(0.4, defend_cost - float(SETTLEMENT_RULES.get("walls_defend_bonus", 0.25)))
                    if soldiers >= defend_cost:
                        s["soldiers"] = soldiers - defend_cost
                        s["starve_ticks"] = 0
                        self.metrics["soldier_defend_events"] = self.metrics.get("soldier_defend_events", 0) + 1
                        self.logger.event({
                            "type": "soldier_defend", "tick": tick, "settlement_id": sid,
                            "soldiers_before": soldiers, "soldiers_after": s["soldiers"],
                            "pop_saved": pop_before,
                        })
                    else:
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
                    "has_granary": has_granary, "has_mine": has_mine, "has_workshop": has_workshop,
                    "has_barracks": has_barracks, "has_academy": has_academy, "has_walls": has_walls,
                    "has_irrigation": has_irrigation, "has_library": has_library,
                    "has_foundry": has_foundry, "has_hall": has_hall, "has_command": has_command,
                    "has_lab": has_lab, "has_observatory": has_observatory,
                    "subjects": subjects, "era": era,
                })

        self._try_raids(world, tick)
        self._try_age_up(world, tick)
        self._try_age_up4(world, tick)

    def _try_discovery(self, sid: str, s: Dict[str, Any], tick: int) -> None:
        """Spend knowledge for permanent farm bonus (Observatory sink)."""
        cost = float(SETTLEMENT_RULES.get("discovery_cost", 40))
        max_d = int(SETTLEMENT_RULES.get("discovery_max", 8))
        discoveries = int(s.get("discoveries", 0))
        knowledge = float(s.get("knowledge", 0.0))
        while discoveries < max_d and knowledge >= cost:
            discoveries += 1
            knowledge -= cost
            s["discoveries"] = discoveries
            s["knowledge"] = knowledge
            self.metrics["discovery_events"] = self.metrics.get("discovery_events", 0) + 1
            self.logger.event({
                "type": "discovery", "tick": tick, "settlement_id": sid,
                "discoveries": discoveries, "cost": cost,
                "knowledge_remaining": knowledge,
            })

    def _try_unlock_subjects(self, sid: str, s: Dict[str, Any], tick: int) -> None:
        subjects = list(s.get("subjects") or [])
        knowledge = float(s.get("knowledge", 0.0))
        candidates = [
            ("agriculture", float(SETTLEMENT_RULES.get("subject_agriculture_cost", 8))),
            ("craft", float(SETTLEMENT_RULES.get("subject_craft_cost", 10))),
            ("organisation", float(SETTLEMENT_RULES.get("subject_organisation_cost", 12))),
            ("strategy", float(SETTLEMENT_RULES.get("subject_strategy_cost", 15))),
            ("inquiry", float(SETTLEMENT_RULES.get("subject_inquiry_cost", 16))),
        ]
        for name, cost in candidates:
            if name in subjects:
                continue
            if knowledge >= cost:
                subjects.append(name)
                s["subjects"] = subjects
                s["knowledge"] = knowledge - cost
                knowledge = float(s["knowledge"])
                self.metrics["subject_unlock_events"] = self.metrics.get("subject_unlock_events", 0) + 1
                self.logger.event({
                    "type": "subject_unlocked", "tick": tick, "settlement_id": sid,
                    "subject": name, "cost": cost, "knowledge_remaining": knowledge,
                    "subjects_now": list(subjects),
                })

    def _try_raids(self, world, tick: int) -> None:
        interval = int(SETTLEMENT_RULES.get("raid_interval", 25))
        if tick % interval != 0 or self.count() < 2:
            return
        min_soldiers = float(SETTLEMENT_RULES.get("raid_min_soldiers", 3.0))
        base_cost = float(SETTLEMENT_RULES.get("raid_cost", 2.0))
        loot_w = int(SETTLEMENT_RULES.get("raid_loot_wood", 3))
        loot_s = int(SETTLEMENT_RULES.get("raid_loot_stone", 2))
        loot_f = int(SETTLEMENT_RULES.get("raid_loot_food", 2))
        all_s = list(self.settlements.items())
        ranked = sorted(all_s, key=lambda x: float(x[1].get("soldiers", 0)), reverse=True)
        atk_sid, atk = ranked[0]
        if float(atk.get("soldiers", 0)) < min_soldiers:
            return
        others = [(sid, s) for sid, s in all_s if sid != atk_sid]
        if not others:
            return
        tgt_sid, tgt = min(others, key=lambda x: float(x[1].get("soldiers", 0)))
        cost = base_cost
        if self.settlement_has_walls(tgt_sid, world):
            cost += float(SETTLEMENT_RULES.get("walls_raid_extra_cost", 1.0))
        if float(atk.get("soldiers", 0)) < cost:
            return
        take_w = min(loot_w, int(tgt.get("wood_stock", 0)))
        take_s = min(loot_s, int(tgt.get("stone_stock", 0)))
        take_f = min(loot_f, int(float(tgt.get("food_stock", 0))))
        if take_w + take_s + take_f == 0:
            return
        atk["soldiers"] = float(atk.get("soldiers", 0)) - cost
        tgt["wood_stock"] = int(tgt.get("wood_stock", 0)) - take_w
        tgt["stone_stock"] = int(tgt.get("stone_stock", 0)) - take_s
        tgt["food_stock"] = float(tgt.get("food_stock", 0)) - take_f
        atk["wood_stock"] = int(atk.get("wood_stock", 0)) + take_w
        atk["stone_stock"] = int(atk.get("stone_stock", 0)) + take_s
        atk["food_stock"] = float(atk.get("food_stock", 0)) + take_f
        self.metrics["raid_events"] = self.metrics.get("raid_events", 0) + 1
        self.metrics["raid_loot_total"] = self.metrics.get("raid_loot_total", 0) + take_w + take_s + take_f
        self.logger.event({
            "type": "raid", "tick": tick, "attacker": atk_sid, "target": tgt_sid,
            "cost_soldiers": cost, "loot": {"wood": take_w, "stone": take_s, "food": take_f},
            "attacker_soldiers_after": atk["soldiers"],
            "target_had_walls": self.settlement_has_walls(tgt_sid, world),
        })

    def _try_age_up(self, world, tick: int) -> None:
        min_pop = int(SETTLEMENT_RULES.get("age_up_min_pop", 15))
        food_bonus = float(SETTLEMENT_RULES.get("age_up_food_bonus", 5.0))
        for sid, s in self.settlements.items():
            if int(s.get("era", 2)) >= 3:
                continue
            if int(s.get("population", 0)) < min_pop:
                continue
            if not (self.settlement_has_workshop(sid, world) and self.settlement_has_barracks(sid, world)):
                continue
            s["era"] = 3
            s["food_stock"] = float(s.get("food_stock", 0)) + food_bonus
            self.metrics["age_up_events"] = self.metrics.get("age_up_events", 0) + 1
            self.logger.event({
                "type": "age_transition", "tick": tick, "settlement_id": sid,
                "from_era": 2, "to_era": 3, "population": s.get("population"),
                "food_bonus": food_bonus,
            })

    def _try_age_up4(self, world, tick: int) -> None:
        min_pop = int(SETTLEMENT_RULES.get("age_up4_min_pop", 20))
        food_bonus = float(SETTLEMENT_RULES.get("age_up4_food_bonus", 5.0))
        for sid, s in self.settlements.items():
            if int(s.get("era", 2)) != 3:
                continue
            if int(s.get("population", 0)) < min_pop:
                continue
            if "inquiry" not in (s.get("subjects") or []):
                continue
            if not self.settlement_has_academy(sid, world):
                continue
            s["era"] = 4
            s["food_stock"] = float(s.get("food_stock", 0)) + food_bonus
            self.metrics["age_up4_events"] = self.metrics.get("age_up4_events", 0) + 1
            self.logger.event({
                "type": "age_transition", "tick": tick, "settlement_id": sid,
                "from_era": 3, "to_era": 4, "population": s.get("population"),
                "food_bonus": food_bonus,
            })

    def count_structures_of_type(self, sid, structure_type, world) -> int:
        return sum(1 for stx in world.structures
                   if stx.type == structure_type and self.structure_settlement_id(stx.x, stx.y) == sid)
