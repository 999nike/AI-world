import json
from pathlib import Path
from typing import Dict, Any, List

from sim.core.rng import RNG
from sim.world.config import WorldConfig
from sim.world.map import make_world
from sim.log.run_id import make_run_id
from sim.log.logger import RunLogger

from sim.world.state import Structure
from sim.agents.types import Observation
from sim.agents.baseline_random import RandomAgent


BUILD_COSTS = {
    "hut": {"wood": 2, "stone": 1},
    "storage": {"wood": 3, "stone": 2},
}

# Settlement core parameters (tune later)
SETTLEMENT_RULES = {
    "starting_population": 2,
    "food_per_pop_per_tick": 1,     # consumption
    "growth_food_buffer": 5,        # if stock >= pop*consumption + buffer => grow
    "max_pop_growth_per_tick": 1,   # keep stable
}


def run_sim(seed: int, ticks: int, snapshot_every: int) -> None:
    run_id = make_run_id()
    run_dir = Path("runs") / run_id
    logger = RunLogger(run_dir)

    cfg = WorldConfig()
    rng = RNG(seed)
    world = make_world(cfg, rng)

    brains = {a.agent_id: RandomAgent(a.agent_id) for a in world.agents}

    # --- Settlement state kept HERE (single-file upgrade) ---
    # settlement_id -> dict
    settlements: Dict[str, Dict[str, Any]] = {}
    # structure (x,y) -> settlement_id
    struct_to_settlement: Dict[str, str] = {}
    settlement_counter = 0

    def pos_key(x: int, y: int) -> str:
        return f"{x},{y}"

    def create_settlement(x: int, y: int, owner_id: str) -> str:
        nonlocal settlement_counter
        sid = f"S{settlement_counter}"
        settlement_counter += 1
        settlements[sid] = {
            "id": sid,
            "name": f"Village_{sid}",
            "x": x,
            "y": y,
            "owner": owner_id,
            "population": int(SETTLEMENT_RULES["starting_population"]),
            "food_stock": 0,
        }
        logger.event(
            {
                "type": "settlement_created",
                "tick": world.tick,
                "settlement": settlements[sid],
            }
        )
        return sid

    def settlement_at_structure(x: int, y: int) -> str:
        # If this structure is already mapped, return it.
        k = pos_key(x, y)
        sid = struct_to_settlement.get(k)
        if sid:
            return sid

        # Otherwise, assign nearest settlement by anchor distance if any exists,
        # else create a new one at this point.
        if not settlements:
            sid = create_settlement(x, y, owner_id="system")
            struct_to_settlement[k] = sid
            return sid

        best_sid = None
        best_d = 10**9
        for sid2, s in settlements.items():
            d = abs(x - s["x"]) + abs(y - s["y"])
            if d < best_d:
                best_d = d
                best_sid = sid2

        # Attach to nearest
        struct_to_settlement[k] = best_sid  # type: ignore
        return best_sid  # type: ignore

    # Save config used
    (run_dir / "config.json").write_text(
        json.dumps(
            {
                "seed": seed,
                "ticks": ticks,
                "snapshot_every": snapshot_every,
                "world": cfg.__dict__,
                "build_costs": BUILD_COSTS,
                "settlement_rules": SETTLEMENT_RULES,
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
            st = world.structure_at(a.x, a.y)

            # attach structure to settlement if standing on one
            st_sid = None
            if st is not None:
                st_sid = settlement_at_structure(st.x, st.y)

                # auto-deposit FOOD only (keeps it simple + meaningful)
                if a.inv_food > 0:
                    settlements[st_sid]["food_stock"] += a.inv_food
                    deposited = a.inv_food
                    a.inv_food = 0
                    logger.event(
                        {
                            "type": "food_deposited",
                            "tick": t,
                            "agent_id": a.agent_id,
                            "settlement_id": st_sid,
                            "amount": deposited,
                            "food_stock": settlements[st_sid]["food_stock"],
                        }
                    )

            obs = Observation(
                tick=t,
                self_id=a.agent_id,
                x=a.x,
                y=a.y,
                width=world.width,
                height=world.height,
                tile=tile.to_dict(),
                inventory=a.inv_dict(),
                structure=(st.to_dict() if st else None),
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
                    "structure": (st.to_dict() if st else None),
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

            elif action.type == "build":
                b = action.building
                if b not in BUILD_COSTS:
                    ok = False
                    note = "bad_building"
                elif world.structure_at(a.x, a.y) is not None:
                    ok = False
                    note = "occupied"
                else:
                    cost = BUILD_COSTS[b]
                    if a.inv_wood < cost["wood"] or a.inv_stone < cost["stone"]:
                        ok = False
                        note = "insufficient_resources"
                    else:
                        a.inv_wood -= cost["wood"]
                        a.inv_stone -= cost["stone"]

                        # Build structure
                        world.structures.append(
                            Structure(type=b, x=a.x, y=a.y, owner_id=a.agent_id)
                        )
                        note = f"built_{b}"

                        # Settlement linkage: first structure at a location creates/attaches settlement
                        # If no settlements exist yet, create one anchored here owned by builder.
                        if not settlements:
                            sid = create_settlement(a.x, a.y, owner_id=a.agent_id)
                            struct_to_settlement[pos_key(a.x, a.y)] = sid
                        else:
                            # attach this new structure to nearest settlement by default
                            sid = settlement_at_structure(a.x, a.y)
                            # If this is very far from nearest, allow new settlement creation
                            # (simple threshold; keeps multi-village possible)
                            s_anchor = settlements[sid]
                            d = abs(a.x - s_anchor["x"]) + abs(a.y - s_anchor["y"])
                            if d >= 8:
                                sid = create_settlement(a.x, a.y, owner_id=a.agent_id)
                                struct_to_settlement[pos_key(a.x, a.y)] = sid

            else:
                ok = False
                note = "unknown_action"

            # resolution log
            tile2 = world.tile_at(a.x, a.y)
            st2 = world.structure_at(a.x, a.y)
            sid2 = None
            if st2 is not None:
                sid2 = settlement_at_structure(st2.x, st2.y)

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
                    "structure": (st2.to_dict() if st2 else None),
                    "settlement_id": sid2,
                }
            )

        # --- Settlement tick: consumption + growth/starvation ---
        if settlements:
            cons = int(SETTLEMENT_RULES["food_per_pop_per_tick"])
            buffer_food = int(SETTLEMENT_RULES["growth_food_buffer"])
            max_growth = int(SETTLEMENT_RULES["max_pop_growth_per_tick"])

            for sid, s in settlements.items():
                pop_before = int(s["population"])
                food_before = int(s["food_stock"])

                need = pop_before * cons
                if s["food_stock"] >= need:
                    s["food_stock"] -= need
                    # growth rule: if still plenty left, grow
                    # (deterministic, not random)
                    if s["food_stock"] >= (need + buffer_food) and pop_before > 0:
                        grow_by = min(max_growth, 1)
                        s["population"] = pop_before + grow_by
                else:
                    # starvation: consume what exists, drop population by 1
                    s["food_stock"] = 0
                    if pop_before > 0:
                        s["population"] = pop_before - 1

                pop_after = int(s["population"])
                food_after = int(s["food_stock"])

                if pop_after != pop_before or food_after != food_before:
                    logger.event(
                        {
                            "type": "population_changed",
                            "tick": t,
                            "settlement_id": sid,
                            "population_before": pop_before,
                            "population_after": pop_after,
                            "food_before": food_before,
                            "food_after": food_after,
                        }
                    )

        # snapshot (augment with settlements + mapped structures)
        if snapshot_every > 0 and (t % snapshot_every) == 0:
            snap = world.to_dict_summary()

            # add settlement info
            snap["settlements"] = list(settlements.values())

            # add structure->settlement mapping for readability
            if "structures" in snap:
                out_structs: List[Dict[str, Any]] = []
                for st in snap["structures"]:
                    sid = struct_to_settlement.get(pos_key(st["x"], st["y"]))
                    st2 = dict(st)
                    st2["settlement_id"] = sid
                    out_structs.append(st2)
                snap["structures"] = out_structs

            logger.snapshot({"type": "snapshot", **snap})
            logger.event({"type": "snapshot_saved", "tick": t})

    final = world.to_dict_summary()
    final["settlements"] = list(settlements.values())

    summary = {
        "run_id": run_id,
        "seed": seed,
        "ticks": ticks,
        "final": final,
    }
    (run_dir / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")

    logger.event({"type": "run_finished", "run_id": run_id})
    logger.close()

    print(f"Run complete: {run_id}")
    print(f"Outputs in: {run_dir}")