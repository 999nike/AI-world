# sim/agents/utility_agent.py
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional
import math

from sim.agents.types import Observation, Action
from sim.core.rng import RNG


DEFAULT_WEIGHTS: Dict[str, float] = {
    # gathering preference
    "w_food": 3.0,
    "w_wood": 1.0,
    "w_stone": 1.0,

    # inventory shaping
    "w_inv_food": 0.8,
    "w_inv_wood": 0.3,
    "w_inv_stone": 0.3,
    "inv_soft_cap": 6.0,

    # build preference
    "w_build_storage": 4.0,
    "w_build_hut": 2.0,
    "w_build_farm": 5.0,

    # movement / exploration
    "w_move": 0.1,
    "w_explore": 0.2,

    # exploration rate
    "epsilon": 0.05,

    # P2.1 – settlement awareness
    "w_food_pressure": 4.0,
    "w_avoid_build_when_hungry": 6.0,
}


def _diminishing(x: float, cap: float) -> float:
    return 1.0 - math.exp(-max(0.0, x) / max(1e-9, cap))


@dataclass
class UtilityAgent:
    agent_id: str
    weights: Dict[str, float]

    def act(self, obs: Observation, rng: RNG) -> Action:
        inv = obs.inventory
        structure = obs.structure

        # --- Early bootstrap: first storage if none exist ---
        if structure is None:
            structs = obs.structures or []
            has_storage = any(s.get("type") == "storage" for s in structs)
            if not has_storage:
                if inv.get("wood", 0) >= 3 and inv.get("stone", 0) >= 2:
                    return Action(type="build", building="storage")

        # ε-greedy
        eps = float(self.weights.get("epsilon", DEFAULT_WEIGHTS["epsilon"]))
        if rng.random() < eps:
            return self._random_action(obs, rng)

        candidates = self._enumerate_candidates(obs)
        best = None
        best_u = -1e18
        for a in candidates:
            u = self._utility(obs, a)
            if u > best_u:
                best_u = u
                best = a

        return best if best is not None else self._random_action(obs, rng)

    def _random_action(self, obs: Observation, rng: RNG) -> Action:
        tile = obs.tile
        if tile.get("food", 0) > 0:
            return Action(type="gather", resource="food")
        if tile.get("wood", 0) > 0:
            return Action(type="gather", resource="wood")
        if tile.get("stone", 0) > 0:
            return Action(type="gather", resource="stone")

        moves = [(1, 0), (0, 1), (-1, 0), (0, -1)]
        dx, dy = moves[rng.randint(0, len(moves) - 1)]
        return Action(type="move", dx=dx, dy=dy)

    def _enumerate_candidates(self, obs: Observation) -> List[Action]:
        c: List[Action] = []

        for r in ("food", "wood", "stone"):
            if obs.tile.get(r, 0) > 0:
                c.append(Action(type="gather", resource=r))

        if obs.structure is None:
            c.append(Action(type="build", building="farm"))
            c.append(Action(type="build", building="storage"))
            c.append(Action(type="build", building="hut"))

        for dx, dy in ((1, 0), (0, 1), (-1, 0), (0, -1)):
            c.append(Action(type="move", dx=dx, dy=dy))

        return c if c else [Action(type="move", dx=1, dy=0)]

    def _settlement_pressure(self, obs: Observation) -> float:
        """0 = fine, 1 = critical food shortage."""
        nearest = obs.nearest_settlement
        if not nearest:
            return 0.0

        pop = float(nearest.get("population", 0))
        food = float(nearest.get("food_stock", 0))
        if pop <= 0:
            return 0.0

        # rough daily need (matches SETTLEMENT_RULES default 0.25)
        need = pop * 0.25
        if food >= need * 2:
            return 0.0
        if food <= 0:
            return 1.0
        return max(0.0, 1.0 - (food / (need * 2)))

    def _utility(self, obs: Observation, a: Action) -> float:
        w = DEFAULT_WEIGHTS.copy()
        w.update(
            {k: float(v) for k, v in self.weights.items() if isinstance(v, (int, float))}
        )

        inv = obs.inventory
        tile = obs.tile
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
            base = {
                "food": w["w_food"],
                "wood": w["w_wood"],
                "stone": w["w_stone"],
            }.get(r, -5.0)

            avail = float(tile.get(r, 0))
            score = base * (0.5 + 0.5 * _diminishing(avail, 3.0)) + inv_term

            # Strong boost for food when settlement is hungry
            if r == "food":
                score += pressure * float(w["w_food_pressure"])

            return score

        if a.type == "build":
            b = a.building or ""
            has_storage = any(st.get("type") == "storage" for st in structures)
            has_farm = any(st.get("type") == "farm" for st in structures)

            # Strongly discourage building when hungry
            hunger_penalty = pressure * float(w["w_avoid_build_when_hungry"])

            if b == "farm":
                bonus = 4.0 if not has_farm else 0.5
                can_pay = 1.0 if inv.get("wood", 0) >= 2 else 0.3
                return w["w_build_farm"] * can_pay + bonus + inv_term - hunger_penalty

            if b == "storage":
                bonus = 5.0 if not has_storage else 0.0
                can_pay = 1.0 if (inv.get("wood", 0) >= 3 and inv.get("stone", 0) >= 2) else 0.2
                return w["w_build_storage"] * can_pay + bonus + inv_term - hunger_penalty

            if b == "hut":
                can_pay = 1.0 if (inv.get("wood", 0) >= 2 and inv.get("stone", 0) >= 1) else 0.2
                penalty = -3.0 if not has_storage else 0.0
                # Extra penalty when hungry – huts increase pop pressure
                return w["w_build_hut"] * can_pay + penalty + inv_term - hunger_penalty * 1.5

            return -5.0

        if a.type == "move":
            emptiness = 1.0
            if tile.get("food", 0) > 0 or tile.get("wood", 0) > 0 or tile.get("stone", 0) > 0:
                emptiness = 0.3
            return w["w_move"] + w["w_explore"] * emptiness + inv_term

        return -10.0
