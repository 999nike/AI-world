from sim.agents.types import Observation, Action
from sim.core.rng import RNG


class RandomAgent:
    def __init__(self, agent_id: str):
        self.agent_id = agent_id

    def act(self, obs: Observation, rng: RNG) -> Action:
        inv = obs.inventory
        tile = obs.tile
        structure = obs.structure

        # ---- PRIORITY 1: If on a structure, gather FOOD for settlement ----
        if structure is not None and tile.get("food", 0) > 0:
            return Action(type="gather", resource="food")

        # ---- PRIORITY 2: Build if we have enough resources ----
        # (simple heuristic, no planning yet)
        if structure is None:
            if inv.get("wood", 0) >= 3 and inv.get("stone", 0) >= 2:
                return Action(type="build", building="storage")
            if inv.get("wood", 0) >= 2 and inv.get("stone", 0) >= 1:
                return Action(type="build", building="hut")

        # ---- PRIORITY 3: Gather missing resources ----
        if tile.get("food", 0) > 0:
            return Action(type="gather", resource="food")
        if tile.get("wood", 0) > 0:
            return Action(type="gather", resource="wood")
        if tile.get("stone", 0) > 0:
            return Action(type="gather", resource="stone")

        # ---- FALLBACK: Move (biased, not fully random) ----
        # Bias movement to explore, not oscillate
        moves = [(1, 0), (0, 1), (-1, 0), (0, -1), (0, 0)]
        dx, dy = moves[rng.randint(0, len(moves) - 1)]
        return Action(type="move", dx=dx, dy=dy)