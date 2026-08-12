"""Minimal Drop-in / Controlled agent for AI-world.

Replaces the normal brain for one agent with a simple fixed policy.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from sim.agents.types import Observation, Action
from sim.core.rng import RNG


VALID_POLICIES = {
    "gather_food",
    "gather_wood",
    "gather_stone",
    "build_farm",
    "build_hut",
    "build_storage",
    "idle",
}


@dataclass
class ControlledAgent:
    agent_id: str
    policy: str = "idle"

    def act(self, obs: Observation, rng: RNG) -> Action:
        policy = self.policy if self.policy in VALID_POLICIES else "idle"

        if policy == "gather_food":
            if obs.tile.get("food", 0) > 0:
                return Action(type="gather", resource="food")
            return self._wander(rng)

        if policy == "gather_wood":
            if obs.tile.get("wood", 0) > 0:
                return Action(type="gather", resource="wood")
            return self._wander(rng)

        if policy == "gather_stone":
            if obs.tile.get("stone", 0) > 0:
                return Action(type="gather", resource="stone")
            return self._wander(rng)

        if policy == "build_farm":
            if obs.structure is None:
                return Action(type="build", building="farm")
            return self._wander(rng)

        if policy == "build_hut":
            if obs.structure is None:
                return Action(type="build", building="hut")
            return self._wander(rng)

        if policy == "build_storage":
            if obs.structure is None:
                return Action(type="build", building="storage")
            return self._wander(rng)

        # idle / fallback
        return self._wander(rng)

    def _wander(self, rng: RNG) -> Action:
        moves = [(1, 0), (0, 1), (-1, 0), (0, -1), (0, 0)]
        dx, dy = moves[rng.randint(0, len(moves) - 1)]
        if dx == 0 and dy == 0:
            return Action(type="move", dx=0, dy=0)  # stay
        return Action(type="move", dx=dx, dy=dy)
