from sim.agents.types import Observation, Action
from sim.core.rng import RNG


class RandomAgent:
    def __init__(self, agent_id: str):
        self.agent_id = agent_id

    def act(self, obs: Observation, rng: RNG) -> Action:
        inv = obs.inventory

        # If we can build and there is no structure here, build.
        # Costs (kept in simloop too): hut=wood2+stone1, storage=wood3+stone2
        if obs.structure is None:
            if inv.get("wood", 0) >= 3 and inv.get("stone", 0) >= 2:
                return Action(type="build", building="storage")
            if inv.get("wood", 0) >= 2 and inv.get("stone", 0) >= 1:
                return Action(type="build", building="hut")

        # Otherwise gather if possible.
        if obs.tile.get("food", 0) > 0:
            return Action(type="gather", resource="food")
        if obs.tile.get("wood", 0) > 0:
            return Action(type="gather", resource="wood")
        if obs.tile.get("stone", 0) > 0:
            return Action(type="gather", resource="stone")

        # Otherwise move randomly (4-neighborhood + stay)
        moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)]
        dx, dy = moves[rng.randint(0, len(moves) - 1)]
        return Action(type="move", dx=dx, dy=dy)