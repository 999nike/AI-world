from sim.core.rng import RNG
from sim.world.config import WorldConfig
from sim.world.state import Tile, WorldState, AgentState


def _spawn(rng, agents, n, prefix, faction, x0, x1, y0, y1):
    for i in range(int(n)):
        agents.append(
            AgentState(
                agent_id=f"{prefix}{i}",
                x=rng.randint(int(x0), int(x1)),
                y=rng.randint(int(y0), int(y1)),
                inv_food=0, inv_wood=0, inv_stone=0,
                faction=faction,
                role="walker",
            )
        )


def make_world(
    cfg: WorldConfig,
    rng: RNG,
    num_agents: int = 4,
    rival_agents: int = 0,
    pole_agents: int = 0,
) -> WorldState:
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
    poles = split and int(pole_agents) > 0

    if poles:
        # Four corners. Mid-coast boxes so the poles do not sit on each other.
        _spawn(rng, agents, n, "A", "player", 5, 13, 17, 31)
        _spawn(rng, agents, rival_agents, "R", "rival", 34, 42, 17, 31)
        _spawn(rng, agents, pole_agents, "N", "north", 17, 31, 5, 13)
        _spawn(rng, agents, pole_agents, "S", "south", 17, 31, 34, 42)
    elif split:
        for i in range(n):
            x = rng.randint(6, 16)
            y = rng.randint(6, max(6, cfg.height - 7))
            agents.append(
                AgentState(
                    agent_id=f"A{i}",
                    x=x, y=y,
                    inv_food=0, inv_wood=0, inv_stone=0,
                    faction="player",
                    role="walker",
                )
            )
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
    else:
        for i in range(n):
            agents.append(
                AgentState(
                    agent_id=f"A{i}",
                    x=rng.randint(0, cfg.width - 1),
                    y=rng.randint(0, cfg.height - 1),
                    inv_food=0, inv_wood=0, inv_stone=0,
                    faction="player",
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
