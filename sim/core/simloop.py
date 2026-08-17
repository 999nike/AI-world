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
    world = make_world(cfg, rng, num_agents=num_agents)

    if scenario.start_food or scenario.start_wood or scenario.start_stone:
        for a in world.agents:
            a.inv_food, a.inv_wood, a.inv_stone = scenario.start_food, scenario.start_wood, scenario.start_stone
        logger.event({"type": "scenario_start_inventory", "tick": 0,
                      "food": scenario.start_food, "wood": scenario.start_wood, "stone": scenario.start_stone})

    gov = Governor()
    if governor_command:
        status = gov.apply_command(governor_command)
        logger.event({"type": "governor_command", "tick": 0, "command": governor_command,
                      "status": status, "state": gov.to_dict()})
    if scenario_commands:
        logger.event({"type": "scenario_loaded", "tick": 0, "commands": scenario_commands, "state": scenario.to_dict()})

    from sim.agents.utility_agent import UtilityAgent, DEFAULT_WEIGHTS
    agents = []
    for i, a in enumerate(world.agents):
        if control_agent_id and a.agent_id == control_agent_id:
            agents.append(ControlledAgent(a.agent_id, control_policy))
        elif agent_kind == "random":
            agents.append(RandomAgent(a.agent_id))
        else:
            w = dict(DEFAULT_WEIGHTS)
            if policy_weights:
                w.update(policy_weights)
            agents.append(UtilityAgent(a.agent_id, w, gov.bias() if gov else None))

    sm = SettlementManager(logger=logger, metrics={})
    metrics = {
        "food_deposited_total": 0, "population_starved_events": 0,
        "build_farm": 0, "build_storage": 0, "build_hut": 0,
        "build_granary": 0, "build_mine": 0, "build_road": 0,
        "build_workshop": 0, "build_barracks": 0, "build_market": 0,
        "build_temple": 0, "build_academy": 0, "build_walls": 0,
        "build_irrigation": 0, "build_library": 0, "build_foundry": 0, "build_hall": 0, "build_command": 0,
        "build_lab": 0, "build_observatory": 0,
    }
    sm.metrics = metrics

    for t in range(ticks):
        world.tick = t
        scenario.apply_events(t, world, sm, logger)

        for a, agent in zip(world.agents, agents):
            tile = world.tile_at(a.x, a.y)
            st = world.structure_at(a.x, a.y)
            nearest_sid = sm.nearest(a.x, a.y)
            nearest = sm.get(nearest_sid) if nearest_sid else None
            structs = []
            if nearest_sid:
                for stx in world.structures:
                    if sm.structure_settlement_id(stx.x, stx.y) == nearest_sid:
                        structs.append(stx.to_dict())
            obs = Observation(
                agent_id=a.agent_id, tick=t,
                inventory=a.inv_dict(), tile=tile.to_dict(),
                structure=st.to_dict() if st else None,
                structures=structs,
                nearest_settlement=nearest,
            )
            action = agent.act(obs, rng)
            ok, note = True, ""
            b = None

            if action.type == "move":
                nx, ny = a.x + action.dx, a.y + action.dy
                if 0 <= nx < world.width and 0 <= ny < world.height:
                    a.x, a.y = nx, ny
                    note = "moved"
                else:
                    ok, note = False, "oob"
            elif action.type == "gather":
                r = action.resource
                amount = getattr(tile, r, 0)
                if amount > 0:
                    setattr(tile, r, amount - 1)
                    if r == "food": a.inv_food += 1
                    elif r == "wood": a.inv_wood += 1
                    elif r == "stone": a.inv_stone += 1
                    note = f"gathered_{r}"
                else:
                    ok, note = False, "empty"
            elif action.type == "build":
                b = action.building
                resolved, gnote = resolve_building(b, a.x, a.y, sm, world)
                if gnote:
                    b = resolved
                    note = gnote
                ok = True
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
                elif ok and world.structure_at(a.x, a.y) is not None:
                    # E5.9: never spend resources on occupied tiles (library is not stackable)
                    existing = world.structure_at(a.x, a.y)
                    if existing and (b not in STACKABLE or existing.type == b or b == "library"):
                        ok, note = False, "occupied"

                if ok:
                    cost = BUILD_COSTS[b]
                    need_wood, need_stone = int(cost["wood"]), int(cost["stone"])
                    cur = world.tile_at(a.x, a.y)
                    use_wood = use_stone = 0

                    # E5.8: inv → tile → settlement cascade
                    use_wood = min(a.inv_wood, need_wood)
                    use_stone = min(a.inv_stone, need_stone)
                    a.inv_wood -= use_wood
                    a.inv_stone -= use_stone
                    need_wood -= use_wood
                    need_stone -= use_stone
                    if need_wood > 0 and cur.wood > 0:
                        take = min(int(cur.wood), need_wood)
                        cur.wood -= take
                        need_wood -= take
                    if need_stone > 0 and cur.stone > 0:
                        take = min(int(cur.stone), need_stone)
                        cur.stone -= take
                        need_stone -= take

                    if (need_wood > 0 or need_stone > 0) and sm.count() == 0:
                        ok, note = False, "insufficient_resources"
                        a.inv_wood += use_wood
                        a.inv_stone += use_stone

                    funded_sid = None
                    if (need_wood > 0 or need_stone > 0) and sm.count() > 0:
                        best_sid = sm.nearest(a.x, a.y)
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

        sm.tick(world, tick=t)

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

    final = world.to_dict_summary()
    final["settlements"] = sm.all()
    total_pop = sum(int(s["population"]) for s in sm.all()) if sm.count() else 0
    score = (total_pop * 10 + sm.count() * 25 + len(world.structures) * 5
             + metrics["food_deposited_total"] - metrics["population_starved_events"] * 5)
    summary = {
        "run_id": run_id, "seed": seed, "ticks": ticks, "num_agents": num_agents,
        "final": final, "metrics": metrics, "score": score,
        "governor": gov.to_dict(), "scenario": scenario.to_dict(),
    }
    (run_dir / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    logger.event({"type": "run_finished", "run_id": run_id})
    logger.close()
    print(f"Run complete: {run_id}")
    print(f"Outputs in: {run_dir}")
    if return_score:
        return score, run_id
    return None
