import json
from pathlib import Path

from sim.core.rng import RNG
from sim.world.config import WorldConfig
from sim.world.map import make_world
from sim.log.run_id import make_run_id
from sim.log.logger import RunLogger

from sim.agents.types import Observation
from sim.agents.baseline_random import RandomAgent


def run_sim(seed: int, ticks: int, snapshot_every: int) -> None:
    run_id = make_run_id()
    run_dir = Path("runs") / run_id
    logger = RunLogger(run_dir)

    cfg = WorldConfig()
    rng = RNG(seed)
    world = make_world(cfg, rng)

    # brains
    brains = {a.agent_id: RandomAgent(a.agent_id) for a in world.agents}

    # Save config used
    (run_dir / "config.json").write_text(
        json.dumps(
            {
                "seed": seed,
                "ticks": ticks,
                "snapshot_every": snapshot_every,
                "world": cfg.__dict__,
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    logger.event({"type": "run_started", "run_id": run_id, "seed": seed})

    for t in range(ticks):
        world.tick = t
        logger.event({"type": "tick_started", "tick": t})

        # deterministic regrowth
        if t % 5 == 0:
            for _ in range(10):
                x = rng.randint(0, world.width - 1)
                y = rng.randint(0, world.height - 1)
                tile = world.tile_at(x, y)
                tile.food = min(tile.food + 1, cfg.max_food)
                tile.wood = min(tile.wood + 1, cfg.max_wood)
                tile.stone = min(tile.stone + 1, cfg.max_stone)

        # agent loop
        for a in world.agents:
            tile = world.tile_at(a.x, a.y)
            obs = Observation(
                tick=t,
                self_id=a.agent_id,
                x=a.x,
                y=a.y,
                width=world.width,
                height=world.height,
                tile=tile.to_dict(),
                inventory=a.inv_dict(),
            )

            action = brains[a.agent_id].act(obs, rng)

            logger.event(
                {
                    "type": "action_attempted",
                    "tick": t,
                    "agent_id": a.agent_id,
                    "action": action.to_dict(),
                    "pos": {"x": a.x, "y": a.y},
                    "tile": tile.to_dict(),
                    "inv": a.inv_dict(),
                }
            )

            ok = True
            note = ""

            if action.type == "move":
                nx = a.x + int(action.dx)
                ny = a.y + int(action.dy)

                if nx < 0 or nx >= world.width or ny < 0 or ny >= world.height:
                    ok = False
                    note = "out_of_bounds"
                    nx, ny = a.x, a.y

                a.x, a.y = nx, ny

            elif action.type == "gather":
                res = action.resource
                if res not in ("food", "wood", "stone"):
                    ok = False
                    note = "bad_resource"
                else:
                    cur_tile = world.tile_at(a.x, a.y)
                    amount = 1

                    if res == "food":
                        if cur_tile.food >= amount:
                            cur_tile.food -= amount
                            a.inv_food += amount
                        else:
                            ok = False
                            note = "no_food"
                    elif res == "wood":
                        if cur_tile.wood >= amount:
                            cur_tile.wood -= amount
                            a.inv_wood += amount
                        else:
                            ok = False
                            note = "no_wood"
                    elif res == "stone":
                        if cur_tile.stone >= amount:
                            cur_tile.stone -= amount
                            a.inv_stone += amount
                        else:
                            ok = False
                            note = "no_stone"
            else:
                ok = False
                note = "unknown_action"

            # log resolution
            tile2 = world.tile_at(a.x, a.y)
            logger.event(
                {
                    "type": "action_resolved",
                    "tick": t,
                    "agent_id": a.agent_id,
                    "ok": ok,
                    "note": note,
                    "pos": {"x": a.x, "y": a.y},
                    "tile": tile2.to_dict(),
                    "inv": a.inv_dict(),
                }
            )

        # snapshot
        if snapshot_every > 0 and (t % snapshot_every) == 0:
            snap = world.to_dict_summary()
            logger.snapshot({"type": "snapshot", **snap})
            logger.event({"type": "snapshot_saved", "tick": t})

    summary = {
        "run_id": run_id,
        "seed": seed,
        "ticks": ticks,
        "final": world.to_dict_summary(),
    }
    (run_dir / "summary.json").write_text(
        json.dumps(summary, indent=2),
        encoding="utf-8",
    )

    logger.event({"type": "run_finished", "run_id": run_id})
    logger.close()

    print(f"Run complete: {run_id}")
    print(f"Outputs in: {run_dir}")