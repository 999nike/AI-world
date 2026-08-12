"""Minimal Scenario designer for AI-world.

Lets the human set starting conditions and simple timed events.
All effects are deterministic and logged.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


@dataclass
class ScenarioEvent:
    tick: int
    kind: str          # "drought" | "boom"
    applied: bool = False


@dataclass
class Scenario:
    seed: Optional[int] = None
    ticks: Optional[int] = None
    start_food: int = 0
    start_wood: int = 0
    start_stone: int = 0
    events: List[ScenarioEvent] = field(default_factory=list)

    def apply_commands(self, raw: str) -> List[str]:
        """Parse a semicolon-separated command string. Returns status messages."""
        statuses = []
        if not raw:
            return statuses

        for part in raw.split(";"):
            cmd = part.strip().lower()
            if not cmd:
                continue
            statuses.append(self._apply_one(cmd))
        return statuses

    def _apply_one(self, cmd: str) -> str:
        parts = cmd.split()
        if not parts:
            return "empty"

        verb = parts[0]

        if verb == "seed" and len(parts) >= 2:
            try:
                self.seed = int(parts[1])
                return f"seed={self.seed}"
            except ValueError:
                return f"bad_seed:{parts[1]}"

        if verb == "ticks" and len(parts) >= 2:
            try:
                self.ticks = int(parts[1])
                return f"ticks={self.ticks}"
            except ValueError:
                return f"bad_ticks:{parts[1]}"

        if verb == "start_food" and len(parts) >= 2:
            try:
                self.start_food = int(parts[1])
                return f"start_food={self.start_food}"
            except ValueError:
                return f"bad_start_food:{parts[1]}"

        if verb == "start_wood" and len(parts) >= 2:
            try:
                self.start_wood = int(parts[1])
                return f"start_wood={self.start_wood}"
            except ValueError:
                return f"bad_start_wood:{parts[1]}"

        if verb == "start_stone" and len(parts) >= 2:
            try:
                self.start_stone = int(parts[1])
                return f"start_stone={self.start_stone}"
            except ValueError:
                return f"bad_start_stone:{parts[1]}"

        if verb == "event" and len(parts) >= 3:
            kind = parts[1]
            try:
                tick = int(parts[2])
            except ValueError:
                return f"bad_event_tick:{parts[2]}"

            if kind in ("drought", "boom"):
                self.events.append(ScenarioEvent(tick=tick, kind=kind))
                return f"event {kind} @{tick}"
            return f"unknown_event:{kind}"

        return f"unknown_command:{cmd}"

    def pending_events(self, tick: int) -> List[ScenarioEvent]:
        return [e for e in self.events if e.tick == tick and not e.applied]

    def to_dict(self) -> Dict:
        return {
            "seed": self.seed,
            "ticks": self.ticks,
            "start_food": self.start_food,
            "start_wood": self.start_wood,
            "start_stone": self.start_stone,
            "events": [{"tick": e.tick, "kind": e.kind} for e in self.events],
        }
