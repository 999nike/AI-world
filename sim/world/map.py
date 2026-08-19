from sim.core.rng import RNG
from sim.world.config import WorldConfig
from sim.world.state import Tile, WorldState, AgentState


def make_world(cfg: WorldConfig, rng: RNG, num_agents: int = 4, rival_agents: int = 0) -> WorldState:
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
    n = max(1, int(num_agents))
    split = int(rival_agents) > 0
    for i in range(n):
        if split:
            x = rng.randint(6, 16)
            y = rng.randint(6, max(6, cfg.height - 7))
        else:
            x = rng.randint(0, cfg.width - 1)
            y = rng.randint(0, cfg.height - 1)
        agents.append(
            AgentState(
                agent_id=f"A{i}",
                x=x, y=y,
                inv_food=0, inv_wood=0, inv_stone=0,
                faction="player",
                role="walker",
            )
        )
    if split:
        for i in range(int(rival_agents)):
            agents.append(
                AgentState(
                    agent_id=f"R{i}",
                    x=rng.randint(cfg.width - 17, cfg.width - 7),
                    y=rng.randint(6, max(6, cfg.height - 7)),
                    inv_food=0, inv_wood=0, inv_stone=0,
                    faction="rival",
                    role="walker",
                )
            )

    return WorldState(
        tick=0,
        width=cfg.width,
        height=cfg.height,
        tiles=tiles,
        agents=agents,
        structures=[],
        settlements=[],
    )
