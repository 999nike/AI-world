# sim/agents/utility_agent.py
from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple
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
    "inv_soft_cap": 6.0,     # diminishing returns cap

    # build preference
    "w_build_storage": 4.0,
    "w_build_hut": 2.0,

    # movement / exploration
    "w_move": 0.1,
    "w_explore": 0.2,

    # exploration rate
    "epsilon": 0.05,
}

def _safe_get_list(obs: Observation, attr: str) -> Optional[List[Dict[str, Any]]]:
    # Observation doesn't declare these fields right now.
    # But if you add them later, this agent will use them.
    try:
        v = getattr(obs, attr)  # type: ignore
        if isinstance(v, list):
            return v
    except Exception:
        pass
    return None

def _diminishing(x: float, cap: float) -> float:
    # smooth saturating curve in [0, 1) as x grows
    return 1.0 - math.exp(-max(0.0, x) / max(1e-9, cap))

@dataclass
class UtilityAgent:
    agent_id: str
    weights: Dict[str, float]


    def act(self, obs: Observation, rng: RNG) -> Action:
    # --- STORAGE-FIRST BOOTSTRAP ---
    inv = obs.inventory
    structure = obs.structure

    # Attempt storage as soon as we have ANY building material.
    # Simloop will fund the remainder from settlement stock if available.
    if structure is None:
        if inv.get("wood", 0) > 0 or inv.get("stone", 0) > 0:
            return Action(type="build", building="storage")

    # ε-greedy: explore randomly sometimes
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
        # Simple safe fallback (never crashes)
        # Prefer any available gather, else move.
        tile = obs.tile
        if tile.get("food", 0) > 0:
            return Action(type="gather", resource="food")
        if tile.get("wood", 0) > 0:
            return Action(type="gather", resource="wood")
        if tile.get("stone", 0) > 0:
            return Action(type="gather", resource="stone")

        moves = [(1,0),(0,1),(-1,0),(0,-1)]
        dx, dy = moves[rng.randint(0, len(moves)-1)]
        return Action(type="move", dx=dx, dy=dy)

    def _enumerate_candidates(self, obs: Observation) -> List[Action]:
        c: List[Action] = []

        # gather candidates
        for r in ("food", "wood", "stone"):
            if obs.tile.get(r, 0) > 0:
                c.append(Action(type="gather", resource=r))

        # build candidates (only if no structure here)
        if obs.structure is None:
            c.append(Action(type="build", building="storage"))
            c.append(Action(type="build", building="hut"))

        # move candidates
        for dx, dy in ((1,0),(0,1),(-1,0),(0,-1)):
            c.append(Action(type="move", dx=dx, dy=dy))

        # If nothing, still return something
        return c if c else [Action(type="move", dx=1, dy=0)]

    def _utility(self, obs: Observation, a: Action) -> float:
        w = DEFAULT_WEIGHTS.copy()
        w.update({k: float(v) for k, v in self.weights.items() if isinstance(v, (int, float))})

        inv = obs.inventory
        tile = obs.tile

        # Some optional globals (if you later add them to Observation)
        structures = _safe_get_list(obs, "structures")
        settlements = _safe_get_list(obs, "settlements")

        # Inventory shaping (diminishing returns)
        cap = float(w["inv_soft_cap"])
        inv_term = (
            float(w["w_inv_food"]) * _diminishing(float(inv.get("food", 0)), cap) +
            float(w["w_inv_wood"]) * _diminishing(float(inv.get("wood", 0)), cap) +
            float(w["w_inv_stone"]) * _diminishing(float(inv.get("stone", 0)), cap)
        )

        # Encourage food early if global settlement pop is at risk (if visible)
        pop_pressure = 0.0
        if settlements:
            total_pop = sum(int(s.get("population", 0)) for s in settlements)
            total_food = sum(int(s.get("food_stock", 0)) for s in settlements)
            # crude: if food_stock < pop, increase food value
            if total_pop > 0 and total_food < total_pop:
                pop_pressure = (total_pop - total_food) / max(1.0, total_pop)

        # Action utility
        if a.type == "gather":
            r = a.resource or ""
            base = (
                w["w_food"] if r == "food" else
                w["w_wood"] if r == "wood" else
                w["w_stone"] if r == "stone" else
                -5.0
            )
            avail = float(tile.get(r, 0))
            # More available resource => better
            return base * (0.5 + 0.5 * _diminishing(avail, 3.0)) + inv_term + pop_pressure * (2.0 if r == "food" else 0.0)

        if a.type == "build":
            b = a.building or ""
            # If globals visible: prefer first storage anywhere
            has_storage = False
            if structures:
                has_storage = any(st.get("type") == "storage" for st in structures)

            if b == "storage":
                # Very high if no storage exists
                bonus = 5.0 if not has_storage else 0.0
                # Only good if we likely can pay cost (3 wood, 2 stone)
                can_pay = 1.0 if (inv.get("wood", 0) >= 3 and inv.get("stone", 0) >= 2) else 0.2
                return w["w_build_storage"] * can_pay + bonus + inv_term

            if b == "hut":
                # Only good if we likely can pay cost (2 wood, 1 stone)
                can_pay = 1.0 if (inv.get("wood", 0) >= 2 and inv.get("stone", 0) >= 1) else 0.2
                # If no storage exists and we know it, huts are less desirable
                penalty = -3.0 if (structures and not has_storage) else 0.0
                return w["w_build_hut"] * can_pay + penalty + inv_term

            return -5.0

        if a.type == "move":
            # Slight explore bias: moving is more valuable if tile is empty
            emptiness = 1.0
            if tile.get("food", 0) > 0 or tile.get("wood", 0) > 0 or tile.get("stone", 0) > 0:
                emptiness = 0.3
            return w["w_move"] + w["w_explore"] * emptiness + inv_term

        return -10.0