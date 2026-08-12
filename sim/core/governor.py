"""Minimal Governor for AI-world.

Soft preference layer only. Never hard-forces actions
(except the existing true emergency food rule in simloop).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Optional


VALID_FOCUS = {"food", "build", "expand"}
VALID_BUILD = {"farm", "hut", "storage", "none"}


@dataclass
class Governor:
    """Holds current soft preferences."""
    focus: Optional[str] = None          # food | build | expand
    preferred_building: Optional[str] = None  # farm | hut | storage | none

    def apply_command(self, cmd: str) -> str:
        """Parse and apply a command. Returns a short status string."""
        cmd = (cmd or "").strip().lower()
        if not cmd:
            return "empty"

        parts = cmd.split()
        if not parts:
            return "empty"

        verb = parts[0]

        if verb == "clear":
            self.focus = None
            self.preferred_building = None
            return "cleared"

        if verb == "focus" and len(parts) >= 2:
            target = parts[1]
            if target in VALID_FOCUS:
                self.focus = target
                return f"focus={target}"
            return f"unknown_focus:{target}"

        if verb == "build" and len(parts) >= 2:
            target = parts[1]
            if target in VALID_BUILD:
                self.preferred_building = target
                return f"build={target}"
            return f"unknown_build:{target}"

        return f"unknown_command:{cmd}"

    def bias_weights(self) -> Dict[str, float]:
        """Return weight multipliers / additives for UtilityAgent."""
        bias: Dict[str, float] = {}

        if self.focus == "food":
            bias["w_food"] = 6.0
            bias["w_build_farm"] = 7.0
            bias["w_food_pressure"] = 6.0

        elif self.focus == "build":
            bias["w_build_farm"] = 6.0
            bias["w_build_hut"] = 5.5
            bias["w_build_storage"] = 6.0
            bias["w_food"] = 2.0

        elif self.focus == "expand":
            bias["w_build_hut"] = 7.0
            bias["w_build_storage"] = 5.0
            bias["w_build_farm"] = 4.0

        if self.preferred_building == "farm":
            bias["w_build_farm"] = bias.get("w_build_farm", 5.0) + 3.0
        elif self.preferred_building == "hut":
            bias["w_build_hut"] = bias.get("w_build_hut", 3.5) + 3.0
        elif self.preferred_building == "storage":
            bias["w_build_storage"] = bias.get("w_build_storage", 4.0) + 3.0
        elif self.preferred_building == "none":
            bias["w_build_farm"] = 0.1
            bias["w_build_hut"] = 0.1
            bias["w_build_storage"] = 0.1

        return bias

    def to_dict(self) -> Dict[str, Optional[str]]:
        return {
            "focus": self.focus,
            "preferred_building": self.preferred_building,
        }
