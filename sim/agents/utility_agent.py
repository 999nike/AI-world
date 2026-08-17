# sim/agents/utility_agent.py
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional
import math

from sim.agents.types import Observation, Action
from sim.core.rng import RNG


DEFAULT_WEIGHTS: Dict[str, float] = {
    "w_food": 3.0, "w_wood": 1.0, "w_stone": 1.0,
    "w_inv_food": 0.8, "w_inv_wood": 0.3, "w_inv_stone": 0.3, "inv_soft_cap": 6.0,
    "w_build_storage": 4.0, "w_build_hut": 3.5, "w_build_farm": 5.0,
    "w_build_granary": 4.5, "w_build_mine": 4.0, "w_build_road": 2.5,
    "w_build_workshop": 3.5, "w_build_barracks": 3.0,
    "w_build_market": 3.2, "w_build_temple": 3.0,
    "w_build_academy": 2.8, "w_build_walls": 3.6,
    "w_build_irrigation": 3.5, "w_build_library": 4.8, "w_build_foundry": 3.5,
    "w_build_hall": 3.4, "w_build_command": 4.0,
    "w_build_lab": 3.8, "w_build_observatory": 3.9,
    "w_move": 0.1, "w_explore": 0.2, "epsilon": 0.05,
    "w_food_pressure": 4.0, "w_avoid_build_when_hungry": 6.0,
}


def _diminishing(x: float, cap: float) -> float:
    return 1.0 - math.exp(-max(0.0, x) / max(1e-9, cap))


def _settlement_stocks(obs) -> tuple:
    nearest = obs.nearest_settlement or {}
    return float(nearest.get("wood_stock", 0) or 0), float(nearest.get("stone_stock", 0) or 0)


def _can_afford(inv, need_w: int, need_s: int, obs) -> float:
    aw = float(inv.get("wood", 0))
    ast = float(inv.get("stone", 0))
    if aw >= need_w and ast >= need_s:
        return 1.0
    sw, ss = _settlement_stocks(obs)
    if aw + sw >= need_w and ast + ss >= need_s:
        return 0.7
    return 0.25


@dataclass
class UtilityAgent:
    agent_id: str
    weights: Dict[str, float]
    governor_bias: Optional[Dict[str, float]] = None

    def act(self, obs: Observation, rng: RNG) -> Action:
        inv = obs.inventory
        structure = obs.structure
        structs = obs.structures or []

        if structure is None and len(structs) == 0:
            if inv.get("wood", 0) >= 2:
                return Action(type="build", building="farm")
            if obs.tile.get("wood", 0) > 0:
                return Action(type="gather", resource="wood")
            return self._random_action(obs, rng)

        if structure is None:
            has_farm = any(s.get("type") == "farm" for s in structs)
            has_storage = any(s.get("type") == "storage" for s in structs)
            if has_farm and not has_storage and inv.get("wood", 0) >= 3 and inv.get("stone", 0) >= 2:
                return Action(type="build", building="storage")

        types = {st.get("type") for st in structs}
        settlements = obs.settlements or ([obs.nearest_settlement] if obs.nearest_settlement else [])
        need_library = False
        for s in settlements:
            if not s:
                continue
            if "inquiry" in (s.get("subjects") or []) and int(s.get("era", 2)) >= 3:
                need_library = True
                break
        if need_library and "library" not in types:
            return Action(type="build", building="library")

        has_market = "market" in types
        has_temple = "temple" in types
        has_academy = "academy" in types
        has_library = "library" in types
        has_lab = "lab" in types
        has_obs = "observatory" in types
        has_barracks = "barracks" in types
        # E5.11c: civic/science hard-gates always (not blocked by hunger)
        era_ok = any(int((ss or {}).get("era", 2)) >= 3 for ss in settlements)
        if has_barracks and not has_market and era_ok:
            return Action(type="build", building="market")
        if has_market and not has_temple:
            return Action(type="build", building="temple")
        if has_temple and not has_academy:
            return Action(type="build", building="academy")
        if has_library and not has_lab:
            return Action(type="build", building="lab")
        if has_lab and not has_obs:
            return Action(type="build", building="observatory")

        eps = float(self.weights.get("epsilon", DEFAULT_WEIGHTS["epsilon"]))
        if rng.random() < eps:
            return self._random_action(obs, rng)

        candidates = self._enumerate_candidates(obs)
        best, best_u = None, -1e18
        for a in candidates:
            u = self._utility(obs, a)
            if u > best_u:
                best_u, best = u, a
        return best if best is not None else self._random_action(obs, rng)

    def _random_action(self, obs, rng) -> Action:
        tile = obs.tile
        for r in ("food", "wood", "stone"):
            if tile.get(r, 0) > 0:
                return Action(type="gather", resource=r)
        moves = [(1, 0), (0, 1), (-1, 0), (0, -1)]
        dx, dy = moves[rng.randint(0, len(moves) - 1)]
        return Action(type="move", dx=dx, dy=dy)

    def _enumerate_candidates(self, obs) -> List[Action]:
        c: List[Action] = []
        for r in ("food", "wood", "stone"):
            if obs.tile.get(r, 0) > 0:
                c.append(Action(type="gather", resource=r))
        if obs.structure is None:
            for b in ("farm", "storage", "hut", "granary", "mine", "road",
                      "workshop", "barracks", "market", "temple", "academy",
                      "walls", "irrigation", "library", "foundry", "hall", "command",
                      "lab", "observatory"):
                c.append(Action(type="build", building=b))
        for dx, dy in ((1, 0), (0, 1), (-1, 0), (0, -1)):
            c.append(Action(type="move", dx=dx, dy=dy))
        return c or [Action(type="move", dx=1, dy=0)]

    def _settlement_pressure(self, obs) -> float:
        nearest = obs.nearest_settlement
        if not nearest:
            return 0.0
        pop, food = float(nearest.get("population", 0)), float(nearest.get("food_stock", 0))
        if pop <= 0:
            return 0.0
        need = pop * 0.22
        if food >= need * 2:
            return 0.0
        if food <= 0:
            return 1.0
        return max(0.0, 1.0 - (food / (need * 2)))

    def _utility(self, obs, a) -> float:
        w = DEFAULT_WEIGHTS.copy()
        w.update({k: float(v) for k, v in self.weights.items() if isinstance(v, (int, float))})
        if self.governor_bias:
            w.update(self.governor_bias)

        inv, tile = obs.inventory, obs.tile
        structures = obs.structures or []
        pressure = self._settlement_pressure(obs)
        cap = float(w["inv_soft_cap"])
        inv_term = (
            float(w["w_inv_food"]) * _diminishing(float(inv.get("food", 0)), cap)
            + float(w["w_inv_wood"]) * _diminishing(float(inv.get("wood", 0)), cap)
            + float(w["w_inv_stone"]) * _diminishing(float(inv.get("stone", 0)), cap)
        )

        if a.type == "gather":
            r = a.resource or ""
            base = {"food": w["w_food"], "wood": w["w_wood"], "stone": w["w_stone"]}.get(r, -5.0)
            score = base * (0.5 + 0.5 * _diminishing(float(tile.get(r, 0)), 3.0)) + inv_term
            if r == "food":
                score += pressure * float(w["w_food_pressure"])
            return score

        if a.type == "build":
            b = a.building or ""
            types = {st.get("type") for st in structures}
            has_storage, has_farm = "storage" in types, "farm" in types
            has_granary, has_mine = "granary" in types, "mine" in types
            farm_count = sum(1 for st in structures if st.get("type") == "farm")
            hunger = pressure * float(w["w_avoid_build_when_hungry"])
            nearest = obs.nearest_settlement or {}
            era = int(nearest.get("era", 2))
            subjects = nearest.get("subjects") or []

            if b == "farm":
                if farm_count >= 6:
                    bonus = 0.2
                elif farm_count >= 3:
                    bonus = 0.8
                else:
                    bonus = 4.0 if not has_farm else 1.2
                can = 1.0 if inv.get("wood", 0) >= 2 else 0.3
                return w["w_build_farm"] * can + bonus + inv_term - hunger
            if b == "storage":
                bonus = 5.0 if not has_storage else 0.0
                can = 1.0 if inv.get("wood", 0) >= 3 and inv.get("stone", 0) >= 2 else 0.2
                return w["w_build_storage"] * can + bonus + inv_term - hunger
            if b == "hut":
                can = 1.0 if inv.get("wood", 0) >= 2 and inv.get("stone", 0) >= 1 else 0.2
                pen = -3.0 if not has_storage else 0.0
                return w["w_build_hut"] * can + pen + inv_term - hunger * 0.5
            if b == "granary":
                if not has_storage or not has_farm or has_granary:
                    return -3.0 if has_granary else -2.0
                can = _can_afford(inv, 3, 1, obs)
                return w["w_build_granary"] * can + 3.0 + inv_term - hunger * 0.3
            if b == "mine":
                if not has_storage or not has_farm or has_mine:
                    return -3.0 if has_mine else -2.0
                can = _can_afford(inv, 2, 3, obs)
                return w["w_build_mine"] * can + 2.5 + inv_term - hunger * 0.3
            if b == "road":
                if "inquiry" in subjects:
                    return -8.0
                if not has_storage or not has_farm:
                    return -2.0
                if not has_mine and len(structures) < 4:
                    return -1.0
                can = 1.0 if inv.get("wood", 0) >= 1 else 0.3
                return w["w_build_road"] * can + 1.5 + inv_term - hunger * 0.2
            if b == "workshop":
                has_workshop = "workshop" in types
                has_road = "road" in types
                if not has_mine or has_workshop:
                    return -3.0 if has_workshop else -2.0
                if not has_granary and not has_road:
                    return -1.5
                can = _can_afford(inv, 4, 2, obs)
                return w["w_build_workshop"] * can + 2.0 + inv_term - hunger * 0.25
            if b == "barracks":
                has_workshop = "workshop" in types
                has_barracks = "barracks" in types
                if not has_workshop or has_barracks:
                    return -3.0 if has_barracks else -1.5
                can = _can_afford(inv, 3, 3, obs)
                return w["w_build_barracks"] * can + 8.0 + inv_term - hunger * 0.15
            if b == "market":
                has_barracks = "barracks" in types
                has_market = "market" in types
                if not has_barracks or has_market:
                    return -3.0 if has_market else -1.5
                can = _can_afford(inv, 4, 3, obs)
                return w["w_build_market"] * can + 2.0 + inv_term - hunger * 0.2
            if b == "temple":
                has_market = "market" in types
                has_temple = "temple" in types
                if not has_market or has_temple:
                    return -3.0 if has_temple else -1.5
                can = _can_afford(inv, 3, 4, obs)
                return w["w_build_temple"] * can + 1.9 + inv_term - hunger * 0.200
            if b == "academy":
                has_temple = "temple" in types
                has_academy = "academy" in types
                if not has_temple or has_academy:
                    return -3.0 if has_academy else -1.5
                can = _can_afford(inv, 5, 4, obs)
                return w["w_build_academy"] * can + 1.7 + inv_term - hunger * 0.15
            if b == "walls":
                has_barracks = "barracks" in types
                has_walls = "walls" in types
                if not has_barracks or has_walls:
                    return -3.0 if has_walls else -1.5
                can = _can_afford(inv, 2, 3, obs)
                return w["w_build_walls"] * can + 2.4 + inv_term - hunger * 0.12
            if b == "irrigation":
                has_irrigation = "irrigation" in types
                if era < 4 or "agriculture" not in subjects or has_irrigation:
                    return -3.0 if has_irrigation else -1.5
                can = _can_afford(inv, 2, 2, obs)
                return w["w_build_irrigation"] * can + 3.0 + inv_term - hunger * 0.08
            if b == "library":
                has_library = "library" in types
                if era < 4 or "inquiry" not in subjects or has_library:
                    return -3.0 if has_library else -1.5
                can = _can_afford(inv, 3, 3, obs)
                priority = 12.0 if can >= 0.7 else 6.0
                return w["w_build_library"] * can + priority + inv_term - hunger * 0.03
            if b == "foundry":
                has_foundry = "foundry" in types
                if era < 4 or "craft" not in subjects or has_foundry:
                    return -3.0 if has_foundry else -1.5
                can = _can_afford(inv, 3, 3, obs)
                return w["w_build_foundry"] * can + 3.2 + inv_term - hunger * 0.06
            if b == "hall":
                has_hall = "hall" in types
                if era < 4 or "organisation" not in subjects or has_hall:
                    return -3.0 if has_hall else -1.5
                can = _can_afford(inv, 3, 3, obs)
                return w["w_build_hall"] * can + 3.1 + inv_term - hunger * 0.06
            if b == "command":
                has_command = "command" in types
                has_barracks = "barracks" in types
                if era < 4 or "strategy" not in subjects or not has_barracks or has_command:
                    return -3.0 if has_command else -1.5
                if pressure > 0.85:
                    return 0.5
                can = _can_afford(inv, 3, 4, obs)
                return w["w_build_command"] * can + 3.5 + inv_term - hunger * 0.10
            if b == "lab":
                has_lab = "lab" in types
                has_library = "library" in types
                if era < 4 or "inquiry" not in subjects or not has_library or has_lab:
                    return -3.0 if has_lab else -1.5
                can = _can_afford(inv, 4, 4, obs)
                return w["w_build_lab"] * can + 4.0 + inv_term - hunger * 0.05
            if b == "observatory":
                has_observatory = "observatory" in types
                has_lab = "lab" in types
                if era < 4 or not has_lab or has_observatory:
                    return -3.0 if has_observatory else -1.5
                can = _can_afford(inv, 5, 4, obs)
                return w["w_build_observatory"] * can + 4.2 + inv_term - hunger * 0.05
            return -5.0

        if a.type == "move":
            empty = 0.3 if any(tile.get(r, 0) > 0 for r in ("food", "wood", "stone")) else 1.0
            return w["w_move"] + w["w_explore"] * empty + inv_term
        return -10.0
