from dataclasses import dataclass
from typing import Dict, Any, Optional, Literal


Role = Literal["gatherer", "builder", "idle"]


@dataclass(frozen=True)
class Observation:
    tick: int
    self_id: str
    x: int
    y: int
    width: int
    height: int
    tile: Dict[str, int]        # {"food": int, "wood": int, "stone": int}
    inventory: Dict[str, int]   # {"food": int, "wood": int, "stone": int}
    structure: Optional[Dict[str, Any]]
    role: Optional[Role] = None  # future use (does nothing yet)


@dataclass(frozen=True)
class Action:
    type: str  # "move" | "gather" | "build"
    dx: int = 0
    dy: int = 0
    resource: Optional[str] = None     # gather
    building: Optional[str] = None     # build
    role_hint: Optional[Role] = None   # future use

    def to_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {"type": self.type}
        if self.type == "move":
            d["dx"] = int(self.dx)
            d["dy"] = int(self.dy)
        if self.type == "gather":
            d["resource"] = self.resource
        if self.type == "build":
            d["building"] = self.building
        if self.role_hint is not None:
            d["role_hint"] = self.role_hint
        return d