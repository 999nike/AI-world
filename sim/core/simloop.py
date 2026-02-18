import json
from pathlib import Path
from typing import Dict, Any, List

from sim.core.rng import RNG
from sim.world.config import WorldConfig
from sim.world.map import make_world
from sim.log.run_id import make_run_id
from sim.log.logger import RunLogger

from sim.world.state import Structure
from sim.agents.types import Observation, Action
from sim.agents.baseline_random import RandomAgent


BUILD_COSTS = {
    "hut": {"wood": 2, "stone": 1},
    "storage": {"wood": 3, "stone": 2},
}

# Settlement core parameters (tune later)
SETTLEMENT_RULES = {
    "starting_population": 1,
    "food_per_pop_per_tick": 0.25,  # consumption (tuned)
    "growth_food_buffer": 2,        # if stock >= pop*consumption + buffer => grow
    "max_pop_growth_per_tick": 1,   # keep stable
}


def run_sim(
    seed: int,
    ticks: int,
    snapshot_every: int,
    agent_kind: str = "utility",
    policy_weights: dict = None,
    return_score: bool = False,
):
    run_id = make_run_id()
    run_dir = Path("runs") / run_id
    logger = RunLogger(run_dir)

    cfg = WorldConfig()
    rng = RNG(seed)
    world = make_world(cfg, rng)

    # --- brains ---
    if agent_kind == "utility":
        from sim.agents.utility_agent import UtilityAgent
        w = policy_weights or {}
        brains = {a.agent_id: UtilityAgent(a.agent_id, w) for a in world.agents}
    else:
        brains = {a.agent_id: RandomAgent(a.agent_id) for a in world.agents}

    # --- Metrics counters (new) ---
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
    }

    # --- Settlement state kept HERE (single-file settlement bundle) ---
    settlements: Dict[str, Dict[str, Any]] = {}
    struct_to_settlement: Dict[str, str] = {}
    settlement_counter = 0

    def pos_key(x: int, y: int) -> str:
        return f"{x},{y}"

    def create_settlement(x: int, y: int, owner_id: str) -> str:
        sid = f's{len(settlements) + 1}'
        settlements[sid] = {
            'id': sid,
            'x': x,
            'y': y,
            'owner_id': owner_id,
            'population': int(SETTLEMENT_RULES.get('starting_population', 2)),
            'food_stock': 0,
            'wood_stock': 0,
            'stone_stock': 0,
            'starve_ticks': 0,
            'surplus_ticks': 0,
        }

        # Starter food so a brand-new settlement doesn't starve before first deposit
        try:
            tile0 = world.tile_at(x, y)
            starter = min(int(getattr(tile0, 'food', 0)), 2)
            settlements[sid]['food_stock'] = starter
            # Optionally claim it from the tile so we don't duplicate food
            if starter > 0:
                tile0.food = int(getattr(tile0, 'food', 0)) - starter
        except Exception:
            settlements[sid]['food_stock'] = 2

        metrics['settlements_created'] += 1
        logger.event({
            'type': 'settlement_created',
            'tick': world.tick,
            'settlement': settlements[sid],
        })

        return sid

    def settlement_at_structure(x: int, y: int) -> str:
        k = pos_key(x, y)
        sid = struct_to_settlement.get(k)
        if sid:
            return sid

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

        struct_to_settlement[k] = best_sid  # type: ignore
        return best_sid  # type: ignore

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

            # auto-deposit FOOD / WOOD / STONE (economy-lite)
            # NEW RULE: if a settlement exists, allow deposit when near its anchor (not only on structures).
            deposit_sid = st_sid
            if deposit_sid is None and settlements:
                best_sid = None
                best_d = 10**9
                for sid2, ss in settlements.items():
                    d = abs(a.x - ss['x']) + abs(a.y - ss['y'])
                    if d < best_d:
                        best_d = d
                        best_sid = sid2
                # deposit if we're close enough to the settlement anchor (radius 2)
                if best_sid is not None and best_d <= 2:
                    deposit_sid = best_sid

            if deposit_sid is not None:
                if a.inv_food > 0:
                    settlements[deposit_sid]['food_stock'] += a.inv_food
                    deposited = a.inv_food
                    a.inv_food = 0
                    metrics['food_deposit_events'] += 1
                    metrics['food_deposited_total'] += deposited
                    logger.event({
                        'type': 'food_deposited',
                        'tick': t,
                        'agent_id': a.agent_id,
                        'settlement_id': deposit_sid,
                        'amount': deposited,
                        'food_stock': settlements[deposit_sid]['food_stock'],
                    })

                if a.inv_wood > 0:
                    settlements[deposit_sid]['wood_stock'] += a.inv_wood
                    deposited = a.inv_wood
                    a.inv_wood = 0
                    metrics['wood_deposit_events'] += 1
                    metrics['wood_deposited_total'] += deposited
                    logger.event({
                        'type': 'wood_deposited',
                        'tick': t,
                        'agent_id': a.agent_id,
                        'settlement_id': deposit_sid,
                        'amount': deposited,
                        'wood_stock': settlements[deposit_sid]['wood_stock'],
                    })

                if a.inv_stone > 0:
                    settlements[deposit_sid]['stone_stock'] += a.inv_stone
                    deposited = a.inv_stone
                    a.inv_stone = 0
                    metrics['stone_deposit_events'] += 1
                    metrics['stone_deposited_total'] += deposited
                    logger.event({
                        'type': 'stone_deposited',
                        'tick': t,
                        'agent_id': a.agent_id,
                        'settlement_id': deposit_sid,
                        'amount': deposited,
                        'stone_stock': settlements[deposit_sid]['stone_stock'],
                    })
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
            )

            action = brains[a.agent_id].act(obs, rng)
            ### GUARD: food/build override ###
            # Force survival first, then stop build-spam by redirecting to gather.
            try:
                # Find nearest settlement (if any)
                nearest_sid = None
                if settlements:
                    best_sid = None
                    best_d = 10**9
                    for sid2, ss in settlements.items():
                        d = abs(a.x - ss["x"]) + abs(a.y - ss["y"])
                        if d < best_d:
                            best_d = d
                            best_sid = sid2
                    nearest_sid = best_sid
                # 0) HAUL GUARD: if carrying food, walk it back to nearest settlement anchor (radius 2)
                if nearest_sid is not None and getattr(a, "inv_food", 0) > 0:
                    ss = settlements[nearest_sid]
                    ax, ay = int(a.x), int(a.y)
                    sx, sy = int(ss["x"]), int(ss["y"])
                    dist = abs(ax - sx) + abs(ay - sy)
                    if dist > 2 and action.type != "move":
                        dx = 0
                        dy = 0
                        if abs(sx - ax) >= abs(sy - ay):
                            dx = 1 if sx > ax else -1
                        else:
                            dy = 1 if sy > ay else -1
                        action = Action(type="move", dx=dx, dy=dy)

            
                # 1) FOOD GUARD: if settlement has people and is short on food, gather food now
                if nearest_sid is not None:
                    ss = settlements[nearest_sid]
                    pop = int(ss.get("population", 0))
                    cons = int(SETTLEMENT_RULES.get("food_per_pop_per_tick", 1))
                    buf  = int(SETTLEMENT_RULES.get("growth_food_buffer", 0))
                    if pop > 0:
                        need_food = pop * cons + buf
                        food_stock = int(ss.get("food_stock", 0))
                        emergency = food_stock < (pop * cons)

                        # EMERGENCY: never build/move while settlement is under daily consumption.
                        if emergency:
                            if not (action.type == "gather" and getattr(action, "resource", None) == "food"):
                                action = Action(type="gather", resource="food")

                        # SOFT PRESSURE: if below growth threshold, forbid building (but still allow moving/gathering).
                        elif food_stock < need_food and action.type == "build":
                            action = Action(type="gather", resource="food")
            
                # 2) BUILD GUARD: if build requested but can't be funded (inv+tile+settlement), gather missing mats
                if False and action.type == "build" and settlements:
                    b_try = action.building
                    cost = BUILD_COSTS.get(b_try)
                    if cost:
                        need_w = int(cost.get("wood", 0))
                        need_s = int(cost.get("stone", 0))
                        tile_now = world.tile_at(a.x, a.y)
                        have_w = int(getattr(tile_now, "wood", 0)) + int(getattr(a, "inv_wood", 0))
                        have_s = int(getattr(tile_now, "stone", 0)) + int(getattr(a, "inv_stone", 0))
                        if nearest_sid is not None:
                            ss = settlements[nearest_sid]
                            have_w += int(ss.get("wood_stock", 0))
                            have_s += int(ss.get("stone_stock", 0))
                        if have_w < need_w:
                            action = Action(type="gather", resource="wood")
                        elif have_s < need_s:
                            action = Action(type="gather", resource="stone")
            except Exception:
                # Never let guard crash the sim
                pass
            ### END GUARD ###


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
                # --- Build spam guard ---
                # If we cannot pay build costs locally, redirect to gather
                cost = BUILD_COSTS.get(b)
                if cost:
                    need_w = int(cost.get("wood", 0))
                    need_s = int(cost.get("stone", 0))

                    tile_now = world.tile_at(a.x, a.y)
                    have_w = a.inv_wood + int(getattr(tile_now, "wood", 0))
                    have_s = a.inv_stone + int(getattr(tile_now, "stone", 0))

                    if have_w < need_w:
                        ok = False
                        note = "insufficient_resources"
                    elif have_s < need_s:
                        ok = False
                        note = "insufficient_resources"


                # Hard rule: no huts until a storage exists in the nearest settlement
                if b == "hut" and settlements:
                    best_sid = None
                    best_d = 10**9
                    for sid2, s in settlements.items():
                        d = abs(a.x - s["x"]) + abs(a.y - s["y"])
                        if d < best_d:
                            best_d = d
                            best_sid = sid2

                    has_storage = any(
                        st.type == "storage"
                        and settlement_at_structure(st.x, st.y) == best_sid
                        for st in world.structures
                    )
                    if not has_storage:
                        ok = False
                        note = "hut_requires_storage"

                        # Hard rule: huts require food stability (prevents build-then-starve spiral)
                        if ok and b == 'hut' and settlements:
                            # use nearest settlement to decide food stability
                            best_sid = None
                            best_d = 10**9
                            for sid2, s in settlements.items():
                                d2 = abs(a.x - s['x']) + abs(a.y - s['y'])
                                if d2 < best_d:
                                    best_d = d2
                                    best_sid = sid2
                            if best_sid is not None:
                                ss = settlements[best_sid]
                                pop = int(ss.get('population', 0))
                                cons = int(SETTLEMENT_RULES.get('food_per_pop_per_tick', 1))
                                buf  = int(SETTLEMENT_RULES.get('growth_food_buffer', 5))
                                need = pop * cons + buf
                                if int(ss.get('food_stock', 0)) < need:
                                    ok = False
                                    note = 'hut_requires_food_stability'

                if ok:
                    if b not in BUILD_COSTS:
                        ok = False
                        note = "bad_building"
                    elif world.structure_at(a.x, a.y) is not None and b != "storage":
                        ok = False
                        note = "occupied"
                    else:
                        cost = BUILD_COSTS[b]
                        need_wood = int(cost["wood"])
                        need_stone = int(cost["stone"])

                                                # Spend from agent inventory first (and for storage, allow tile funding too)
                        cur_tile = world.tile_at(a.x, a.y)
                        if b == "storage":
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
                        # If still short and there are no settlements yet, the build fails (refund inventory).
                        if (need_wood > 0 or need_stone > 0) and not settlements:
                            ok = False
                            note = "insufficient_resources"
                            a.inv_wood += use_wood
                            a.inv_stone += use_stone


                        # If still short, try to fund the remainder from nearest settlement stockpile
                        funded_sid = None
                        if (need_wood > 0 or need_stone > 0) and settlements:
                            best_sid = None
                            best_d = 10**9
                            for sid2, s in settlements.items():
                                d = abs(a.x - s["x"]) + abs(a.y - s["y"])
                                if d < best_d:
                                    best_d = d
                                    best_sid = sid2
                            funded_sid = best_sid

                            s = settlements[best_sid]  # type: ignore
                            if s["wood_stock"] >= need_wood and s["stone_stock"] >= need_stone:
                                s["wood_stock"] -= need_wood
                                s["stone_stock"] -= need_stone
                                need_wood = 0
                                need_stone = 0
                            else:
                                ok = False
                                note = "insufficient_resources"
                                # Refund what we already took from agent inventory
                                a.inv_wood += use_wood
                                a.inv_stone += use_stone

                        # If costs fully covered, build it
                        if ok and need_wood == 0 and need_stone == 0:
                            world.structures.append(
                                Structure(type=b, x=a.x, y=a.y, owner_id=a.agent_id)
                            )
                            note = f"built_{b}"

                            if b == "hut":
                                metrics["build_hut"] += 1
                            elif b == "storage":
                                metrics["build_storage"] += 1

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

                            # settlement linkage
                            if not settlements:
                                sid = create_settlement(a.x, a.y, owner_id=a.agent_id)
                                struct_to_settlement[pos_key(a.x, a.y)] = sid
                            else:
                                sid = settlement_at_structure(a.x, a.y)
                                s_anchor = settlements[sid]
                                d = abs(a.x - s_anchor["x"]) + abs(a.y - s_anchor["y"])
                                if d >= 24:
                                    sid = create_settlement(a.x, a.y, owner_id=a.agent_id)
                                struct_to_settlement[pos_key(a.x, a.y)] = sid

            else:
                ok = False
                note = "unknown_action"

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

        # settlement tick: consumption + growth/starvation
        if settlements:
            cons = float(SETTLEMENT_RULES["food_per_pop_per_tick"])
            buffer_food = int(SETTLEMENT_RULES["growth_food_buffer"])
            max_growth = int(SETTLEMENT_RULES["max_pop_growth_per_tick"])

            for sid, s in settlements.items():
                pop_before = int(s["population"])
                food_before = int(s["food_stock"])

                
                need = pop_before * cons
                if s.get("food_stock", 0) >= need:
                    # consume
                    s["food_stock"] = int(s.get("food_stock", 0)) - int(need)
                    # reset starvation counter
                    s["starve_ticks"] = 0
                    # surplus logic: require sustained surplus before growth
                    if s.get("food_stock", 0) >= (need + buffer_food) and pop_before > 0:
                        s["surplus_ticks"] = int(s.get("surplus_ticks", 0)) + 1
                        if int(s["surplus_ticks"]) >= 3:
                            grow_by = min(max_growth, 1)
                            s["population"] = pop_before + grow_by
                            s["surplus_ticks"] = 0
                    else:
                        s["surplus_ticks"] = 0
                else:
                    # no food to cover consumption this tick
                    s["surplus_ticks"] = 0
                    s["food_stock"] = 0
                    s["starve_ticks"] = int(s.get("starve_ticks", 0)) + 1
                    # only lose population after several consecutive deficit ticks
                    if pop_before > 0 and int(s["starve_ticks"]) >= 3:
                        s["population"] = pop_before - 1
                        s["starve_ticks"] = 0
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

        # snapshot
        if snapshot_every > 0 and (t % snapshot_every) == 0:
            snap = world.to_dict_summary()
            snap["settlements"] = list(settlements.values())

            if "structures" in snap:
                out_structs: List[Dict[str, Any]] = []
                for st3 in snap["structures"]:
                    sid = struct_to_settlement.get(pos_key(st3["x"], st3["y"]))
                    st4 = dict(st3)
                    st4["settlement_id"] = sid
                    out_structs.append(st4)
                snap["structures"] = out_structs

            logger.snapshot({"type": "snapshot", **snap})
            logger.event({"type": "snapshot_saved", "tick": t})

    final = world.to_dict_summary()
    final["settlements"] = list(settlements.values())

    # simple score (bigger is better)
    total_pop = sum(int(s["population"]) for s in settlements.values()) if settlements else 0
    num_settlements = len(settlements)
    num_structures = len(world.structures)
    score = (
        total_pop * 10
        + num_settlements * 25
        + num_structures * 5
        + metrics["food_deposited_total"]
        - metrics["population_starved_events"] * 20
    )

    summary = {
        "run_id": run_id,
        "seed": seed,
        "ticks": ticks,
        "final": final,
        "metrics": metrics,
        "score": score,
    }
    (run_dir / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")

    logger.event({"type": "run_finished", "run_id": run_id})
    logger.close()

    print(f"Run complete: {run_id}")
    print(f"Outputs in: {run_dir}")

    if return_score:
        return score, run_id
    return None

    logger.event({"type": "run_started", "run_id": run_id, "seed": seed})

