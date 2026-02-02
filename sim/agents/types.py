from dataclasses import dataclass
from typing import Dict, Any

@dataclass(frozen=True)
class Observation:
    tick: int
    self_id: str
    x: int
    y: int
    width: int
    height: int

@dataclass(frozen=True)
class Action:
    type: str  # "move"
    dx: int
    dy: int

    def to_dict(self) -> Dict[str, Any]:
        return {"type": self.type, "dx": self.dx, "dy": self.dy}