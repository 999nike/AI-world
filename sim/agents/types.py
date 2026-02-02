from dataclasses import dataclass
from typing import Dict, Any, Optional


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
    structure: Optional[Dict[str, Any]]  # {"type","x","y","owner"} or None


@dataclass(frozen=True)
class Action:
    type: str  # "move" | "gather" | "build"
    dx: int = 0
    dy: int = 0
    resource: Optional[str] = None     # gather: "food"|"wood"|"stone"
    building: Optional[str] = None     # build: "hut"|"storage"

    def to_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {"type": self.type}
        if self.type == "move":
            d["dx"] = int(self.dx)
            d["dy"] = int(self.dy)
        elif self.type == "gather":
            d["resource"] = self.resource
        elif self.type == "build":
            d["building"] = self.building
        return d