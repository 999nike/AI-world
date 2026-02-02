from dataclasses import dataclass
from typing import List, Dict, Any


@dataclass
class Tile:
    food: int
    wood: int
    stone: int

    def to_dict(self) -> Dict[str, int]:
        return {"food": self.food, "wood": self.wood, "stone": self.stone}


@dataclass
class AgentState:
    agent_id: str
    x: int
    y: int
    inv_food: int = 0
    inv_wood: int = 0
    inv_stone: int = 0

    def inv_dict(self) -> Dict[str, int]:
        return {"food": self.inv_food, "wood": self.inv_wood, "stone": self.inv_stone}


@dataclass
class WorldState:
    tick: int
    width: int
    height: int
    tiles: List[Tile]
    agents: List[AgentState]

    def idx(self, x: int, y: int) -> int:
        return y * self.width + x

    def tile_at(self, x: int, y: int) -> Tile:
        return self.tiles[self.idx(x, y)]

    def to_dict_summary(self) -> Dict[str, Any]:
        total_food = sum(t.food for t in self.tiles)
        total_wood = sum(t.wood for t in self.tiles)
        total_stone = sum(t.stone for t in self.tiles)

        return {
            "tick": self.tick,
            "width": self.width,
            "height": self.height,
            "agents": [
                {"id": a.agent_id, "x": a.x, "y": a.y, "inv": a.inv_dict()}
                for a in self.agents
            ],
            "totals": {"food": total_food, "wood": total_wood, "stone": total_stone},
        }