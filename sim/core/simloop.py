import json
from pathlib import Path
from typing import Dict, Any, List, Optional

from sim.core.rng import RNG
from sim.world.config import WorldConfig
from sim.world.map import make_world
from sim.log.run_id import make_run_id
from sim.log.logger import RunLogger

from sim.world.state import Structure
from sim.world.settlements import SettlementManager, SETTLEMENT_RULES
from sim.core.build_governors import resolve_building, can_build_hut
from sim.core.governor import Governor
from sim.core.scenario import Scenario
from sim.agents.types import Observation, Action
from sim.agents.baseline_random import RandomAgent


BUILD_COSTS = {
    "hut": {"wood": 2, "stone": 1},
    "storage": {"wood": 3, "stone": 2},
    "farm": {"wood": 2, "stone": 0},
}


def run_sim(
    seed: int,
    ticks: int,
    snapshot_every: int,
    agent_kind: str = "utility",
    policy_weights: dict = None,
    return_score: bool = False,
    governor_command: Optional[str] = None,
    scenario_commands: Optional[str] = None,
):
    # P7.0 Scenario first so it can override seed/ticks
    scenario = Scenario()
    if scenario_commands:
        scenario.apply_commands(scenario_commands)

    if scenario.seed is not None:
        seed = scenario.seed
    if scenario.ticks is not None:
        ticks = scenario.ticks

    run_id = make_run_id()
    run_dir = Path("runs") / run_id
    logger = RunLogger(run_dir)

    cfg = WorldConfig()
    rng = RNG(seed)
    world = make_world(cfg, rng)

    # Apply starting inventory from scenario
    if scenario.start_food or scenario.start_wood or scenario.start_stone:
        for a in world.agents:
            a.inv_food = scenario.start_food
            a.inv_wood = scenario.start_wood
            a.inv_stone = scenario.start_stone
        logger.event({
            "type": "scenario_start_inventory",
            "tick": 0,
            "food": scenario.start_food,
            "wood": scenario.start_wood,
            "stone": scenario.start_stone,
        })

    # P6.0 Governor
    gov = Governor()
    if governor_command:
        status = gov.apply_command(governor_command)
        logger.event({
            "type": "governor_command",
            "tick": 0,
            "command": governor_command,
            "status": status,
            "state": gov.to_dict(),
        })

    if scenario_commands:
        logger.event({
            "type": "scenario_loaded",
            "tick": 0,
            "commands": scenario_commands,
            "state": scenario.to_dict(),
        })

    if agent_kind == "utility":
        from sim.agents.utility_agent import UtilityAgent
        w = policy_weights or {}
        bias = gov.bias_weights()
        brains = {
            a.agent_id: UtilityAgent(a.agent_id, w, governor_bias=bias)
            for a in world.agents
        }
    else:
        brains = {a.agent_id: RandomAgent(a.agent_id) for a in world.agents}

    metrics = {
        "settlements_created": 0,
        "food_deposited_total": 0,
        "food_deposit_events": 0,
        "wood_deposited_total": 0,
        "wood_deposit_events": 0,
        "stone_deposited_total": 0,
        "stone_deposit_events": 0,
        "population_grew_events": 0,
        "population_starved_events": 0,
        "population_net_change": 0,
        "build_hut": 0,
        "build_storage": 0,
        "build_farm": 0,
        "farm_harvest_events": 0,
        "farm_food_total": 0,
    }

    sm = SettlementManager(metrics=metrics, logger=logger)

    # Simple drought state (P7.0)
    drought_active = False

    (run_dir / "config.json").write_text(
        json.dumps(
            {
                "seed": seed,
                "ticks": ticks,
                "snapshot_every": snapshot_every,
                "world": cfg.__dict__,
                "build_costs": BUILD_COSTS,
                "settlement_rules": SETTLEMENT_RULES,
                "governor": gov.to_dict(),
                "governor_command": governor_command,
                "scenario": scenario.to_dict(),
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    logger.event({"type": "run_started", "run_id": run_id, "seed": seed})

    for t in range(ticks):
        world.tick = t
        logger.event({"type": "tick_started", "tick": t})

        # P7.0 Apply pending scenario events
        for ev in scenario.pending_events(t):
            if ev.kind == "drought":
                drought_active = True
                logger.event({"type": "scenario_event", "tick": t, "kind": "drought", "note": "food regrowth reduced"})
            elif ev.kind == "boom":
                # Spike resources on the map
                for _ in range(40):
                    x = rng.randint(0, world.width - 1)
                    y = rng.randint(0, world.height - 1)
                    tile = world.tile_at(x, y)
                    tile.food = min(tile.food + 3, cfg.max_food)
                    tile.wood = min(tile.wood + 2, cfg.max_wood)
                logger.event({"type": "scenario_event", "tick": t, "kind": "boom", "note": "resource spike"})
            ev.applied = True

        # Normal regrowth (reduced during drought)
        regrowth_count = 3 if drought_active else 10
        if t % 5 == 0:
            for _ in range(regrowth_count):
                x = rng.randint(0, world.width - 1)
                y = rng.randint(0, world.height - 1)
                tile = world.tile_at(x, y)
                tile.food = min(tile.food + 1, cfg.max_food)
                tile.wood = min(tile.wood + 1, cfg.max_wood)
                tile.stone = min(tile.stone + 1, cfg.max_stone)

        for a in world.agents:
            tile = world.tile_at(a.x, a.y)
            st = world.structure_at(a.x, a.y)

            nearest_sid = sm.nearest(a.x, a.y)
            sm.try_deposit(a, tick=t)

            nearest_data = sm.get(nearest_sid) if nearest_sid else None

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
                structures=[s.to_dict() for s in world.structures],
                settlements=sm.all(),
                nearest_settlement=nearest_data,
            )

            action = brains[a.agent_id].act(obs, rng)

            # P2.2: Only a true emergency override remains.
            try:
                nearest_sid = sm.nearest(a.x, a.y)
                if nearest_sid is not None:
                    ss = sm.get(nearest_sid)
                    food_stock = float(ss.get("food_stock", 0))
                    if food_stock < 1.0:
                        if not (action.type == "gather" and getattr(action, "resource", None) == "food"):
                            action = Action(type="gather", resource="food")
            except Exception:
                pass

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
                b, gov_note = resolve_building(
                    requested=action.building,
                    agent_x=a.x,
                    agent_y=a.y,
                    sm=sm,
                    world=world,
                )
                if gov_note:
                    note = gov_note

                if b == "hut":
                    allowed, gate_note = can_build_hut(a.x, a.y, sm, world)
                    if not allowed:
                        ok = False
                        note = gate_note

                if ok and b not in BUILD_COSTS:
                    ok = False
                    note = "bad_building"
                elif ok and world.structure_at(a.x, a.y) is not None and b not in ("storage", "farm"):
                    ok = False
                    note = "occupied"

                if ok:
                    cost = BUILD_COSTS[b]
                    need_wood = int(cost["wood"])
                    need_stone = int(cost["stone"])

                    cur_tile = world.tile_at(a.x, a.y)
                    use_wood = 0
                    use_stone = 0

                    if b in ("storage", "farm"):
                        avail_wood = a.inv_wood + cur_tile.wood
                        avail_stone = a.inv_stone + cur_tile.stone
                        if avail_wood < need_wood or avail_stone < need_stone:
                            ok = False
                            note = "insufficient_resources"
                        else:
                            use_wood = min(a.inv_wood, need_wood)
                            use_stone = min(a.inv_stone, need_stone)
                            a.inv_wood -= use_wood
                            a.inv_stone -= use_stone
                            need_wood -= use_wood
                            need_stone -= use_stone
                            if need_wood > 0:
                                cur_tile.wood -= need_wood
                                need_wood = 0
                            if need_stone > 0:
                                cur_tile.stone -= need_stone
                                need_stone = 0
                    else:
                        use_wood = min(a.inv_wood, need_wood)
                        use_stone = min(a.inv_stone, need_stone)
                        a.inv_wood -= use_wood
                        a.inv_stone -= use_stone
                        need_wood -= use_wood
                        need_stone -= use_stone

                    if (need_wood > 0 or need_stone > 0) and sm.count() == 0:
                        ok = False
                        note = "insufficient_resources"
                        a.inv_wood += use_wood
                        a.inv_stone += use_stone

                    funded_sid = None
                    if (need_wood > 0 or need_stone > 0) and sm.count() > 0:
                        best_sid = sm.nearest(a.x, a.y)
                        funded_sid = best_sid
                        s = sm.get(best_sid)  # type: ignore
                        if s["wood_stock"] >= need_wood and s["stone_stock"] >= need_stone:
                            s["wood_stock"] -= need_wood
                            s["stone_stock"] -= need_stone
                            need_wood = 0
                            need_stone = 0
                        else:
                            ok = False
                            note = "insufficient_resources"
                            a.inv_wood += use_wood
                            a.inv_stone += use_stone

                    if ok and need_wood == 0 and need_stone == 0:
                        world.structures.append(
                            Structure(type=b, x=a.x, y=a.y, owner_id=a.agent_id)
                        )
                        note = f"built_{b}"

                        if b == "hut":
                            metrics["build_hut"] += 1
                        elif b == "storage":
                            metrics["build_storage"] += 1
                        elif b == "farm":
                            metrics["build_farm"] += 1

                        if funded_sid is not None:
                            logger.event(
                                {
                                    "type": "build_funded",
                                    "tick": t,
                                    "agent_id": a.agent_id,
                                    "settlement_id": funded_sid,
                                    "building": b,
                                }
                            )

                        sm.link_structure(a.x, a.y, owner_id=a.agent_id, world=world, tick=t)

            else:
                ok = False
                note = "unknown_action"

            tile2 = world.tile_at(a.x, a.y)
            st2 = world.structure_at(a.x, a.y)

            sid2 = None
            if st2 is not None:
                sid2 = sm.structure_settlement_id(st2.x, st2.y)

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

        sm.tick(world, tick=t)

        if snapshot_every > 0 and (t % snapshot_every) == 0:
            snap = world.to_dict_summary()
            snap["settlements"] = sm.all()

            if "structures" in snap:
                out_structs: List[Dict[str, Any]] = []
                for st3 in snap["structures"]:
                    sid = sm.structure_settlement_id(st3["x"], st3["y"])
                    st4 = dict(st3)
                    st4["settlement_id"] = sid
                    out_structs.append(st4)
                snap["structures"] = out_structs

            logger.snapshot({"type": "snapshot", **snap})
            logger.event({"type": "snapshot_saved", "tick": t})

    final = world.to_dict_summary()
    final["settlements"] = sm.all()

    total_pop = sum(int(s["population"]) for s in sm.all()) if sm.count() > 0 else 0
    num_settlements = sm.count()
    num_structures = len(world.structures)
    score = (
        total_pop * 10
        + num_settlements * 25
        + num_structures * 5
        + metrics["food_deposited_total"]
        - metrics["population_starved_events"] * 5
    )

    summary = {
        "run_id": run_id,
        "seed": seed,
        "ticks": ticks,
        "final": final,
        "metrics": metrics,
        "score": score,
        "governor": gov.to_dict(),
        "scenario": scenario.to_dict(),
    }
    (run_dir / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")

    logger.event({"type": "run_finished", "run_id": run_id})
    logger.close()

    print(f"Run complete: {run_id}")
    print(f"Outputs in: {run_dir}")

    if return_score:
        return score, run_id
    return None
