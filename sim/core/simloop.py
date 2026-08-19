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
from sim.core.build_governors import (
    resolve_building, can_build_hut, can_build_granary, can_build_mine, can_build_road,
    can_build_workshop, can_build_barracks, can_build_market, can_build_temple,
    can_build_academy, can_build_walls, can_build_irrigation, can_build_library,
    can_build_foundry, can_build_hall, can_build_command, can_build_lab, can_build_observatory,
)
from sim.core.governor import Governor
from sim.core.scenario import Scenario
from sim.agents.types import Observation, Action
from sim.agents.baseline_random import RandomAgent
from sim.agents.controlled_agent import ControlledAgent


BUILD_COSTS = {
    "hut": {"wood": 2, "stone": 1},
    "storage": {"wood": 3, "stone": 2},
    "farm": {"wood": 2, "stone": 0},
    "granary": {"wood": 3, "stone": 1},
    "mine": {"wood": 2, "stone": 3},
    "road": {"wood": 1, "stone": 0},
    "workshop": {"wood": 4, "stone": 2},
    "barracks": {"wood": 3, "stone": 3},
    "market": {"wood": 4, "stone": 3},
    "temple": {"wood": 3, "stone": 4},
    "academy": {"wood": 5, "stone": 4},
    "walls": {"wood": 2, "stone": 3},
    "irrigation": {"wood": 2, "stone": 2},
    "library": {"wood": 3, "stone": 3},
    "foundry": {"wood": 3, "stone": 3},
    "hall": {"wood": 3, "stone": 3},
    "command": {"wood": 3, "stone": 4},
    "lab": {"wood": 4, "stone": 4},
    "observatory": {"wood": 5, "stone": 4},
}

STACKABLE = {"storage", "farm", "granary", "mine", "road", "workshop", "barracks",
             "market", "temple", "academy", "walls", "irrigation", "library",
             "foundry", "hall", "command", "lab", "observatory"}


def run_sim(
    seed: int, ticks: int, snapshot_every: int,
    agent_kind: str = "utility", policy_weights: dict = None, return_score: bool = False,
    governor_command: Optional[str] = None, scenario_commands: Optional[str] = None,
    control_agent_id: Optional[str] = None, control_policy: str = "idle", num_agents: int = 4,
    quiet: bool = False,
    playable: bool = False, choice_policy: str = "first", decision_picker=None,
    on_tick=None, on_tick_every: int = 4,
    rival_agents: int = 0,
    soft_outcome: bool = False,
):
    scenario = Scenario()
    if scenario_commands:
        scenario.apply_commands(scenario_commands)
    if scenario.seed is not None:
        seed = scenario.seed
    if scenario.ticks is not None:
        ticks = scenario.ticks
    if scenario.num_agents is not None:
        num_agents = scenario.num_agents

    run_id = make_run_id()
    run_dir = Path("runs") / run_id
    logger = RunLogger(run_dir, quiet=quiet)
    cfg = WorldConfig()
    rng = RNG(seed)
    world = make_world(cfg, rng, num_agents=num_agents, rival_agents=rival_agents)

    if scenario.start_food or scenario.start_wood or scenario.start_stone:
        for a in world.agents:
            a.inv_food, a.inv_wood, a.inv_stone = scenario.start_food, scenario.start_wood, scenario.start_stone
        logger.event({"type": "scenario_start_inventory", "tick": 0,
                      "food": scenario.start_food, "wood": scenario.start_wood, "stone": scenario.start_stone})

    gov = Governor()
    rival_gov = Governor()
    if governor_command:
        status = gov.apply_command(governor_command)
        logger.event({"type": "governor_command", "tick": 0, "command": governor_command,
                      "status": status, "state": gov.to_dict()})
    if rival_agents:
        rival_focus = "army" if (int(seed) % 2 == 0) else "science"
        rival_gov.apply_command(f"focus {rival_focus}")
        logger.event({"type": "rival_governor", "tick": 0, "command": f"focus {rival_focus}",
                      "state": rival_gov.to_dict()})
    if scenario_commands:
        logger.event({"type": "scenario_loaded", "tick": 0, "commands": scenario_commands, "state": scenario.to_dict()})

    if agent_kind == "utility":
        from sim.agents.utility_agent import UtilityAgent
        w = policy_weights or {}
        player_bias = gov.bias_weights()
        rival_bias = rival_gov.bias_weights()
        brains = {}
        for a in world.agents:
            bias = rival_bias if getattr(a, "faction", "player") == "rival" else player_bias
            brains[a.agent_id] = UtilityAgent(a.agent_id, w, governor_bias=bias)
    else:
        brains = {a.agent_id: RandomAgent(a.agent_id) for a in world.agents}

    if control_agent_id and control_agent_id in brains:
        brains[control_agent_id] = ControlledAgent(control_agent_id, policy=control_policy)
        logger.event({"type": "agent_controlled", "tick": 0, "agent_id": control_agent_id, "policy": control_policy})

    metrics = {
        "settlements_created": 0,
        "food_deposited_total": 0, "food_deposit_events": 0,
        "wood_deposited_total": 0, "wood_deposit_events": 0,
        "stone_deposited_total": 0, "stone_deposit_events": 0,
        "population_grew_events": 0, "population_starved_events": 0, "population_net_change": 0,
        "build_hut": 0, "build_storage": 0, "build_farm": 0,
        "build_granary": 0, "build_mine": 0, "build_road": 0, "build_workshop": 0, "build_barracks": 0,
        "build_market": 0, "build_temple": 0, "build_academy": 0, "build_walls": 0,
        "build_irrigation": 0, "build_library": 0, "build_foundry": 0, "build_hall": 0, "build_command": 0,
        "build_lab": 0, "build_observatory": 0,
        "farm_harvest_events": 0, "farm_food_total": 0,
        "granary_food_total": 0, "mine_stone_total": 0, "workshop_tools_total": 0, "barracks_soldiers_total": 0,
        "tools_boost_events": 0, "soldier_defend_events": 0, "raid_events": 0, "raid_loot_total": 0,
        "age_up_events": 0, "age_up4_events": 0,
        "market_wood_total": 0, "market_stone_total": 0, "temple_food_total": 0,
        "academy_knowledge_total": 0, "subject_unlock_events": 0,
        "discovery_events": 0,
    }
    sm = SettlementManager(metrics=metrics, logger=logger)
    drought_active = False
    play_state = None
    outcome = None
    headline = None
    founded: set = set()
    if playable:
        from sim.core.playable import PlayableState
        play_state = PlayableState(policy=choice_policy, seed=seed, picker=decision_picker)
        play_state.player_ids = {
            a.agent_id for a in world.agents if getattr(a, "faction", "player") == "player"
        }

    (run_dir / "config.json").write_text(json.dumps({
        "seed": seed, "ticks": ticks, "num_agents": num_agents, "snapshot_every": snapshot_every,
        "quiet": quiet, "rival_agents": rival_agents,
        "world": cfg.__dict__, "build_costs": BUILD_COSTS, "settlement_rules": SETTLEMENT_RULES,
        "governor": gov.to_dict(), "rival_governor": rival_gov.to_dict() if rival_agents else None,
        "scenario": scenario.to_dict(),
    }, indent=2), encoding="utf-8")

    logger.event({"type": "run_started", "run_id": run_id, "seed": seed, "num_agents": num_agents})

    for t in range(ticks):
        world.tick = t
        logger.event({"type": "tick_started", "tick": t})

        drought_this_tick = False
        for ev in scenario.pending_events(t):
            if ev.kind == "drought":
                drought_active = True
                drought_this_tick = True
            elif ev.kind == "boom":
                for _ in range(40):
                    x, y = rng.randint(0, world.width - 1), rng.randint(0, world.height - 1)
                    tile = world.tile_at(x, y)
                    tile.food = min(tile.food + 3, cfg.max_food)
                    tile.wood = min(tile.wood + 2, cfg.max_wood)
            ev.applied = True
            logger.event({"type": "scenario_event", "tick": t, "kind": ev.kind})

        if t % 5 == 0:
            for _ in range(3 if drought_active else 10):
                x, y = rng.randint(0, world.width - 1), rng.randint(0, world.height - 1)
                tile = world.tile_at(x, y)
                tile.food = min(tile.food + 1, cfg.max_food)
                tile.wood = min(tile.wood + 1, cfg.max_wood)
                tile.stone = min(tile.stone + 1, cfg.max_stone)

        for a in world.agents:
            fac = getattr(a, "faction", "player")
            sm.active_faction = fac if rival_agents else None
            tile = world.tile_at(a.x, a.y)
            st = world.structure_at(a.x, a.y)
            sm.try_deposit(a, tick=t, world=world)
            nearest_sid = sm.nearest(a.x, a.y)
            nearest_data = sm.get(nearest_sid) if nearest_sid else None
            own_settlements = list(sm.own().values()) if rival_agents else sm.all()
            own_structs = []
            if rival_agents:
                for stx in world.structures:
                    sid = sm.structure_settlement_id(stx.x, stx.y)
                    st_fac = sm.get(sid).get("faction", "player") if sid else "player"
                    if st_fac == fac:
                        own_structs.append(stx.to_dict())
            else:
                own_structs = [s.to_dict() for s in world.structures]

            obs = Observation(
                tick=t, self_id=a.agent_id, x=a.x, y=a.y,
                width=world.width, height=world.height,
                tile=tile.to_dict(), inventory=a.inv_dict(),
                structure=(st.to_dict() if st else None),
                structures=own_structs,
                settlements=own_settlements, nearest_settlement=nearest_data,
            )
            action = brains[a.agent_id].act(obs, rng)

            logger.event({"type": "action_attempted", "tick": t, "agent_id": a.agent_id,
                          "action": action.to_dict(), "pos": {"x": a.x, "y": a.y},
                          "tile": tile.to_dict(), "inv": a.inv_dict(),
                          "structure": (st.to_dict() if st else None)})

            ok, note = True, ""

            if action.type == "move":
                nx, ny = a.x + int(action.dx), a.y + int(action.dy)
                if nx < 0 or nx >= world.width or ny < 0 or ny >= world.height:
                    ok, note, nx, ny = False, "out_of_bounds", a.x, a.y
                a.x, a.y = nx, ny

            elif action.type == "gather":
                res = action.resource
                if res not in ("food", "wood", "stone"):
                    ok, note = False, "bad_resource"
                else:
                    cur = world.tile_at(a.x, a.y)
                    attr = {"food": "inv_food", "wood": "inv_wood", "stone": "inv_stone"}[res]
                    if getattr(cur, res) >= 1:
                        setattr(cur, res, getattr(cur, res) - 1)
                        setattr(a, attr, getattr(a, attr) + 1)
                        try:
                            nearest_sid = sm.nearest(a.x, a.y)
                            if nearest_sid is not None and sm.settlement_has_workshop(nearest_sid, world):
                                s = sm.get(nearest_sid)
                                tools = float(s.get("tools_stock", 0.0))
                                consume = float(SETTLEMENT_RULES.get("tools_consume_per_boost", 0.5))
                                if tools >= 1.0:
                                    setattr(a, attr, getattr(a, attr) + 1)
                                    s["tools_stock"] = tools - consume
                                    metrics["tools_boost_events"] = metrics.get("tools_boost_events", 0) + 1
                                    note = "tools_boost"
                        except Exception:
                            pass
                    else:
                        ok, note = False, f"no_{res}"

            elif action.type == "build":
                b, gov_note = resolve_building(action.building, a.x, a.y, sm, world)
                if gov_note:
                    note = gov_note

                if b == "hut":
                    allowed, gate_note = can_build_hut(a.x, a.y, sm, world)
                    if not allowed: ok, note = False, gate_note
                elif b == "granary":
                    allowed, gate_note = can_build_granary(a.x, a.y, sm, world)
                    if not allowed: ok, note = False, gate_note
                elif b == "mine":
                    allowed, gate_note = can_build_mine(a.x, a.y, sm, world)
                    if not allowed: ok, note = False, gate_note
                elif b == "road":
                    allowed, gate_note = can_build_road(a.x, a.y, sm, world)
                    if not allowed: ok, note = False, gate_note
                elif b == "workshop":
                    allowed, gate_note = can_build_workshop(a.x, a.y, sm, world)
                    if not allowed: ok, note = False, gate_note
                elif b == "barracks":
                    allowed, gate_note = can_build_barracks(a.x, a.y, sm, world)
                    if not allowed: ok, note = False, gate_note
                elif b == "market":
                    allowed, gate_note = can_build_market(a.x, a.y, sm, world)
                    if not allowed: ok, note = False, gate_note
                elif b == "temple":
                    allowed, gate_note = can_build_temple(a.x, a.y, sm, world)
                    if not allowed: ok, note = False, gate_note
                elif b == "academy":
                    allowed, gate_note = can_build_academy(a.x, a.y, sm, world)
                    if not allowed: ok, note = False, gate_note
                elif b == "walls":
                    allowed, gate_note = can_build_walls(a.x, a.y, sm, world)
                    if not allowed: ok, note = False, gate_note
                elif b == "irrigation":
                    allowed, gate_note = can_build_irrigation(a.x, a.y, sm, world)
                    if not allowed: ok, note = False, gate_note
                elif b == "library":
                    allowed, gate_note = can_build_library(a.x, a.y, sm, world)
                    if not allowed: ok, note = False, gate_note
                elif b == "foundry":
                    allowed, gate_note = can_build_foundry(a.x, a.y, sm, world)
                    if not allowed: ok, note = False, gate_note
                elif b == "hall":
                    allowed, gate_note = can_build_hall(a.x, a.y, sm, world)
                    if not allowed: ok, note = False, gate_note
                elif b == "command":
                    allowed, gate_note = can_build_command(a.x, a.y, sm, world)
                    if not allowed: ok, note = False, gate_note
                elif b == "lab":
                    allowed, gate_note = can_build_lab(a.x, a.y, sm, world)
                    if not allowed: ok, note = False, gate_note
                elif b == "observatory":
                    allowed, gate_note = can_build_observatory(a.x, a.y, sm, world)
                    if not allowed: ok, note = False, gate_note

                if ok and b not in BUILD_COSTS:
                    ok, note = False, "bad_building"
                elif ok and world.structure_at(a.x, a.y) is not None and b not in STACKABLE:
                    ok, note = False, "occupied"
                elif ok and world.structure_at(a.x, a.y) is not None and b in STACKABLE:
                    existing = world.structure_at(a.x, a.y)
                    if existing and existing.type == b:
                        ok, note = False, "occupied"

                if ok:
                    cost = BUILD_COSTS[b]
                    need_wood, need_stone = int(cost["wood"]), int(cost["stone"])
                    cur = world.tile_at(a.x, a.y)
                    use_wood = use_stone = 0

                    if b in STACKABLE:
                        if a.inv_wood + cur.wood < need_wood or a.inv_stone + cur.stone < need_stone:
                            ok, note = False, "insufficient_resources"
                        else:
                            use_wood = min(a.inv_wood, need_wood)
                            use_stone = min(a.inv_stone, need_stone)
                            a.inv_wood -= use_wood
                            a.inv_stone -= use_stone
                            need_wood -= use_wood
                            need_stone -= use_stone
                            if need_wood > 0:
                                cur.wood -= need_wood
                                need_wood = 0
                            if need_stone > 0:
                                cur.stone -= need_stone
                                need_stone = 0
                    else:
                        use_wood = min(a.inv_wood, need_wood)
                        use_stone = min(a.inv_stone, need_stone)
                        a.inv_wood -= use_wood
                        a.inv_stone -= use_stone
                        need_wood -= use_wood
                        need_stone -= use_stone

                    own_n = len(sm.own())
                    if (need_wood > 0 or need_stone > 0) and own_n == 0:
                        ok, note = False, "insufficient_resources"
                        a.inv_wood += use_wood
                        a.inv_stone += use_stone

                    funded_sid = None
                    if (need_wood > 0 or need_stone > 0) and own_n > 0:
                        best_sid = sm.nearest(a.x, a.y)
                        if best_sid is None:
                            ok, note = False, "insufficient_resources"
                            a.inv_wood += use_wood
                            a.inv_stone += use_stone
                        else:
                            funded_sid = best_sid
                            s = sm.get(best_sid)
                            if s["wood_stock"] >= need_wood and s["stone_stock"] >= need_stone:
                                s["wood_stock"] -= need_wood
                                s["stone_stock"] -= need_stone
                                need_wood = need_stone = 0
                            else:
                                ok, note = False, "insufficient_resources"
                                a.inv_wood += use_wood
                                a.inv_stone += use_stone

                    if ok and need_wood == 0 and need_stone == 0:
                        if world.structure_at(a.x, a.y) is None:
                            world.structures.append(Structure(type=b, x=a.x, y=a.y, owner_id=a.agent_id))
                            note = f"built_{b}"
                            metrics_key = f"build_{b}"
                            if metrics_key in metrics:
                                metrics[metrics_key] += 1
                            if funded_sid is not None:
                                logger.event({"type": "build_funded", "tick": t, "agent_id": a.agent_id,
                                              "settlement_id": funded_sid, "building": b})
                            sm.link_structure(a.x, a.y, owner_id=a.agent_id, world=world, tick=t)
                        else:
                            ok, note = False, "occupied"
            else:
                ok, note = False, "unknown_action"

            tile2 = world.tile_at(a.x, a.y)
            st2 = world.structure_at(a.x, a.y)
            sid2 = sm.structure_settlement_id(st2.x, st2.y) if st2 else None
            logger.event({"type": "action_resolved", "tick": t, "agent_id": a.agent_id, "ok": ok, "note": note,
                          "pos": {"x": a.x, "y": a.y}, "tile": tile2.to_dict(), "inv": a.inv_dict(),
                          "structure": (st2.to_dict() if st2 else None), "settlement_id": sid2})

        sm.active_faction = None
        sm.tick(world, tick=t)

        if rival_agents and headline is None:
            from sim.core.outcome import detect_early, side_from_world
            for s in sm.all():
                founded.add(s.get("faction", "player"))
            early = detect_early(
                t, side_from_world(sm, world, "player"),
                side_from_world(sm, world, "rival"), founded,
            )
            if early:
                headline = early
                logger.event(headline)
                if not soft_outcome:
                    outcome = early

        emit_view = on_tick is not None and (
            outcome is not None or
            t % max(1, int(on_tick_every)) == 0 or t == ticks - 1
        )
        if emit_view:
            snap = world.to_dict_summary()
            snap["settlements"] = sm.all()
            snap["metrics"] = dict(metrics)
            if headline:
                snap["outcome"] = headline
            tagged = []
            for st3 in snap.get("structures") or []:
                sid = sm.structure_settlement_id(st3["x"], st3["y"])
                fac = sm.get(sid).get("faction", "player") if sid else "player"
                tagged.append({**st3, "settlement_id": sid, "faction": fac})
            snap["structures"] = tagged
            on_tick(snap)

        if outcome:
            break

        if play_state is not None:
            from sim.core.playable import maybe_decide
            player_towns = [s for s in sm.all() if s.get("faction", "player") == "player"]
            maybe_decide(
                play_state, gov, brains, logger, t, metrics, player_towns,
                drought_this_tick=drought_this_tick,
            )

        if snapshot_every > 0 and (t % snapshot_every) == 0:
            snap = world.to_dict_summary()
            snap["settlements"] = sm.all()
            if "structures" in snap:
                snap["structures"] = [
                    {**st3, "settlement_id": sm.structure_settlement_id(st3["x"], st3["y"])}
                    for st3 in snap["structures"]
                ]
            logger.snapshot({"type": "snapshot", **snap})
            logger.event({"type": "snapshot_saved", "tick": t})

    if rival_agents and headline is None:
        from sim.core.outcome import detect_survival, side_from_world
        last_t = world.tick if ticks else 0
        headline = detect_survival(
            last_t, side_from_world(sm, world, "player"),
            side_from_world(sm, world, "rival"),
        )
        logger.event(headline)
    outcome = headline

    final = world.to_dict_summary()
    final["settlements"] = sm.all()
    total_pop = sum(int(s["population"]) for s in sm.all()) if sm.count() else 0
    score = (total_pop * 10 + sm.count() * 25 + len(world.structures) * 5
             + metrics["food_deposited_total"] - metrics["population_starved_events"] * 5)
    summary = {
        "run_id": run_id, "seed": seed, "ticks": ticks, "num_agents": num_agents,
        "ticks_ran": int(world.tick) + 1 if ticks else 0,
        "final": final, "metrics": metrics, "score": score,
        "governor": gov.to_dict(), "scenario": scenario.to_dict(),
        "rival_agents": rival_agents,
        "rival_governor": rival_gov.to_dict() if rival_agents else None,
        "outcome": outcome,
    }
    (run_dir / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    logger.event({"type": "run_finished", "run_id": run_id})
    logger.close()
    print(f"Run complete: {run_id}")
    print(f"Outputs in: {run_dir}")
    if outcome:
        print(f"Outcome: {outcome.get('winner')} / {outcome.get('kind')} — {outcome.get('reason')}")
    if return_score:
        return score, run_id
    return None
