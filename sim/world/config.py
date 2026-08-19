from dataclasses import dataclass


@dataclass(frozen=True)
class WorldConfig:
    width: int = 48
    height: int = 48
    max_food: int = 5
    max_wood: int = 5
    max_stone: int = 5
