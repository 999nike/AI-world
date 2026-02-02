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


@dataclass(frozen=True)
class Action:
    type: str  # "move" | "gather"
    dx: int = 0
    dy: int = 0
    resource: Optional[str] = None  # for gather: "food" | "wood" | "stone"

    def to_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {"type": self.type}
        if self.type == "move":
            d["dx"] = int(self.dx)
            d["dy"] = int(self.dy)
        if self.type == "gather":
            d["resource"] = self.resource
        return d