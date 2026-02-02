from dataclasses import dataclass

@dataclass(frozen=True)
class WorldConfig:
    width: int = 32
    height: int = 32
    max_food: int = 5
    max_wood: int = 5
    max_stone: int = 5