from dataclasses import dataclass
from typing import List, Dict, Any


@dataclass
class Tile:
    food: int
    wood: int
    stone: int


@dataclass
class AgentState:
    agent_id: str
    x: int
    y: int


@dataclass
class WorldState:
    tick: int
    width: int
    height: int
    tiles: List[Tile]
    agents: List[AgentState]

    def idx(self, x: int, y: int) -> int:
        return y * self.width + x

    def to_dict_summary(self) -> Dict[str, Any]:
        total_food = sum(t.food for t in self.tiles)
        total_wood = sum(t.wood for t in self.tiles)
        total_stone = sum(t.stone for t in self.tiles)
        return {
            "tick": self.tick,
            "width": self.width,
            "height": self.height,
            "agents": [{"id": a.agent_id, "x": a.x, "y": a.y} for a in self.agents],
            "totals": {"food": total_food, "wood": total_wood, "stone": total_stone},
        }