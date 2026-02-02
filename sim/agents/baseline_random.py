from sim.agents.types import Observation, Action
from sim.core.rng import RNG


class RandomAgent:
    def __init__(self, agent_id: str):
        self.agent_id = agent_id

    def act(self, obs: Observation, rng: RNG) -> Action:
        inv = obs.inventory
        tile = obs.tile
        structure = obs.structure

        # ---- PRIORITY 0: Civilization bootstrap ----
        # If there are ANY settlements but NO storage anywhere, try hard to build storage first.
        # (This is the missing policy that unlocks stable populations.)
        if structure is None:
            has_storage = False
            if obs.structure is not None:
                # ignore, structure means current tile has something; storage check is global below
                pass

            # obs.structure is per-agent; we need global view.
            # If your Observation doesn't include structures, this will be skipped safely.
            try:
                has_storage = any(st["type"] == "storage" for st in obs.structures)  # type: ignore
            except Exception:
                has_storage = False

            if (not has_storage) and inv.get("wood", 0) >= 3 and inv.get("stone", 0) >= 2:
                return Action(type="build", building="storage")

        # ---- PRIORITY 1: If on a structure, gather FOOD for settlement ----
        if structure is not None and tile.get("food", 0) > 0:
            return Action(type="gather", resource="food")

        # ---- PRIORITY 2: Build if we have enough resources ----
        if structure is None:
            # Prefer storage over huts
            if inv.get("wood", 0) >= 3 and inv.get("stone", 0) >= 2:
                return Action(type="build", building="storage")
            if inv.get("wood", 0) >= 2 and inv.get("stone", 0) >= 1:
                return Action(type="build", building="hut")

        # ---- PRIORITY 3: Gather resources ----
        # Food first
        if tile.get("food", 0) > 0:
            return Action(type="gather", resource="food")
        if tile.get("wood", 0) > 0:
            return Action(type="gather", resource="wood")
        if tile.get("stone", 0) > 0:
            return Action(type="gather", resource="stone")

        # ---- FALLBACK: Move ----
        moves = [(1, 0), (0, 1), (-1, 0), (0, -1)]
        dx, dy = moves[rng.randint(0, len(moves) - 1)]
        return Action(type="move", dx=dx, dy=dy)