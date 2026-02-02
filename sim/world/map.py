from sim.core.rng import RNG
from sim.world.config import WorldConfig
from sim.world.state import Tile, WorldState, AgentState


def make_world(cfg: WorldConfig, rng: RNG) -> WorldState:
    tiles = []
    for _ in range(cfg.width * cfg.height):
        tiles.append(
            Tile(
                food=rng.randint(0, cfg.max_food),
                wood=rng.randint(0, cfg.max_wood),
                stone=rng.randint(0, cfg.max_stone),
            )
        )

    agents = []
    for i in range(4):
        agents.append(
            AgentState(
                agent_id=f"A{i}",
                x=rng.randint(0, cfg.width - 1),
                y=rng.randint(0, cfg.height - 1),
            )
        )

    return WorldState(
        tick=0,
        width=cfg.width,
        height=cfg.height,
        tiles=tiles,
        agents=agents,
    )