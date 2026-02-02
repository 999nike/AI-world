import json
from pathlib import Path

from sim.core.rng import RNG
from sim.world.config import WorldConfig
from sim.world.map import make_world
from sim.log.run_id import make_run_id
from sim.log.logger import RunLogger

def run_sim(seed: int, ticks: int, snapshot_every: int) -> None:
    run_id = make_run_id()
    run_dir = Path("runs") / run_id
    logger = RunLogger(run_dir)

    cfg = WorldConfig()
    rng = RNG(seed)
    world = make_world(cfg, rng)

    # Save config used
    (run_dir / "config.json").write_text(json.dumps({
        "seed": seed,
        "ticks": ticks,
        "snapshot_every": snapshot_every,
        "world": cfg.__dict__,
    }, indent=2))

    logger.event({"type": "run_started", "run_id": run_id, "seed": seed})

    for t in range(ticks):
        world.tick = t
        logger.event({"type": "tick_started", "tick": t})

        # v0 environment dynamics (tiny): resources slowly regrow
        # keep deterministic using rng only (no time-based randomness)
        if t % 5 == 0:
            # regrow a few random tiles
            for _ in range(10):
                x = rng.randint(0, world.width - 1)
                y = rng.randint(0, world.height - 1)
                tile = world.tiles[world.idx(x, y)]
                tile.food = min(tile.food + 1, cfg.max_food)
                tile.wood = min(tile.wood + 1, cfg.max_wood)
                tile.stone = min(tile.stone + 1, cfg.max_stone)

        if (t % snapshot_every) == 0:
            snap = world.to_dict_summary()
            logger.snapshot({"type": "snapshot", **snap})
            logger.event({"type": "snapshot_saved", "tick": t})

    summary = {
        "run_id": run_id,
        "seed": seed,
        "ticks": ticks,
        "final": world.to_dict_summary(),
    }
    (run_dir / "summary.json").write_text(json.dumps(summary, indent=2))

    logger.event({"type": "run_finished", "run_id": run_id})
    logger.close()

    print(f"Run complete: {run_id}")
    print(f"Outputs in: {run_dir}")