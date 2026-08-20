import json
from pathlib import Path
from typing import Dict, Any, List, Optional

from sim.core.rng import RNG
from sim.world.config import WorldConfig
from sim.world.map import make_world
from sim.log.run_id import make_run_id
from sim.log.logger import RunLogger

from sim.world.state import Structure, AgentState
from sim.world.settlements import SettlementManager, SETTLEMENT_RULES


# Fixed offsets for bred walkers — no main-RNG draws (determinism).
_BREED_OFFSETS = (
    (0, 1), (1, 0), (0, -1), (-1, 0),
    (1, 1), (-1, 1), (1, -1), (-1, -1),
    (2, 0), (0, 2), (-2, 0), (0, -2),
)


def _next_agent_id(world, prefix: str) -> str:
    nums = []
    for a in world.agents:
        aid = a.agent_id
        if aid.startswith(prefix):
            tail = aid[len(prefix):]
            if tail.isdigit():
                nums.append(int(tail))
    n = (max(nums) + 1) if nums else 0
    return f"{prefix}{n}"


def _hands_target(pop: int) -> int:
    start = int(SETTLEMENT_RULES.get("walker_start", 4))
    cap = int(SETTLEMENT_RULES.get("walker_cap", 10))
    step = max(1, int(SETTLEMENT_RULES.get("breed_pop_step", 4)))
    return min(cap, start + max(0, (int(pop) - 1) // step))


def _capital(towns):
    return max(towns, key=lambda s: int(s.get("population", 0) or 0))


def _bred_index(agent) -> int:
    aid = str(getattr(agent, "agent_id", "") or "")
    if len(aid) < 2 or aid[0] not in ("A", "R", "N", "S"):
        return -1
    tail = aid[1:]
    return int(tail) if tail.isdigit() else -1


def _step_toward(agent, tx: int, ty: int):
    dx = int(tx) - int(agent.x)
    dy = int(ty) - int(agent.y)
    if dx == 0 and dy == 0:
        return None
    if abs(dx) >= abs(dy):
        return Action(type="move", dx=1 if dx > 0 else -1, dy=0)
    return Action(type="move", dx=0, dy=1 if dy > 0 else -1)


_SCIENCE_PREF = {"observatory": 0, "lab": 1, "library": 2}
_WORKS_PREF = {"hall": 0, "foundry": 1, "workshop": 2}
_CREW_PREF = {"mill": 0, "warehouse": 1, "foundry": 2, "workshop": 3}


def _job_target(agent, world, sm, pref):
    """Nearest own workplace, preferring the higher building."""
    fac = getattr(agent, "faction", "player")
    best = None
    best_key = None
    for stx in world.structures:
        if stx.type not in pref:
            continue
        sid = sm.structure_settlement_id(stx.x, stx.y)
        if not sid:
            continue
        if sm.get(sid).get("faction", "player") != fac:
            continue
        d = abs(int(agent.x) - int(stx.x)) + abs(int(agent.y) - int(stx.y))
        key = (pref[stx.type], d, int(stx.y), int(stx.x))
        if best_key is None or key < best_key:
            best_key = key
            best = stx
    return best


def _faction_has_job(world, sm, fac, pref) -> bool:
    for stx in world.structures:
        if stx.type not in pref:
            continue
        sid = sm.structure_settlement_id(stx.x, stx.y)
        if sid and sm.get(sid).get("faction", "player") == fac:
            return True
    return False


def _maybe_home_action(agent, sm, world):
    """Keep ranks at their seats. Extra hands stay off the map edge.

    No RNG. Original A0–A3 / R0–R3 walkers keep their utility brain.
    """
    fac = getattr(agent, "faction", "player")
    towns = [s for s in sm.all() if s.get("faction", "player") == fac]
    if not towns:
        return None
    cap = _capital(towns)
    dist = abs(int(agent.x) - int(cap["x"])) + abs(int(agent.y) - int(cap["y"]))
    role = getattr(agent, "role", "walker")
    if role == "king":
        return _step_toward(agent, cap["x"], cap["y"]) or Action(type="move", dx=0, dy=0)
    if role == "scribe":
        job = _job_target(agent, world, sm, _SCIENCE_PREF)
        if job:
            step = _step_toward(agent, job.x, job.y)
            if step:
                return step
        return None
    if role == "builder":
        job = _job_target(agent, world, sm, _WORKS_PREF)
        if job:
            step = _step_toward(agent, job.x, job.y)
            if step:
                return step
        return None
    if role == "crew":
        job = _job_target(agent, world, sm, _CREW_PREF)
        if job:
            step = _step_toward(agent, job.x, job.y)
            if step:
                return step
        return None
    if _bred_index(agent) >= 4 and dist > 12:
        return _step_toward(agent, cap["x"], cap["y"])
    return None


def try_breed_and_knight(world, sm, brains, t, metrics, logger, rival_agents, agent_kind, policy_weights, gov, rival_gov, play_state, pole_agents=0, govs=None):
    """Grow hands with the town; knight at town; king at city; specialists at science.

    At most one breed / knight / king / scribe / builder per faction per tick.
    No main RNG draws.
    """
    if pole_agents:
        factions = ("player", "rival", "north", "south")
    elif rival_agents:
        factions = ("player", "rival")
    else:
        factions = ("player",)
    prefixes = {"player": "A", "rival": "R", "north": "N", "south": "S"}
    govs = govs or {"player": gov, "rival": rival_gov}
    for fac in factions:
        towns = [s for s in sm.all() if s.get("faction", "player") == fac]
        if not towns:
            continue
        pop = sum(int(s.get("population", 0) or 0) for s in towns)
        max_era = max(int(s.get("era", 2) or 2) for s in towns)
        hands = [a for a in world.agents if getattr(a, "faction", "player") == fac]
        target = _hands_target(pop)
        cap = _capital(towns)

        if len(hands) < target:
            prefix = prefixes.get(fac, "A")
            aid = _next_agent_id(world, prefix)
            idx = len(hands)
            ox, oy = _BREED_OFFSETS[idx % len(_BREED_OFFSETS)]
            x = max(0, min(world.width - 1, int(cap["x"]) + ox))
            y = max(0, min(world.height - 1, int(cap["y"]) + oy))
            child = AgentState(
                agent_id=aid, x=x, y=y,
                inv_food=0, inv_wood=0, inv_stone=0,
                faction=fac, role="walker",
            )
            world.agents.append(child)
            if agent_kind == "utility":
                from sim.agents.utility_agent import UtilityAgent
                w = policy_weights or {}
                g = govs.get(fac) or gov
                brains[aid] = UtilityAgent(aid, w, governor_bias=g.bias_weights())
            else:
                brains[aid] = RandomAgent(aid)
            if play_state is not None and fac == "player":
                play_state.player_ids.add(aid)
            metrics["walker_born"] = metrics.get("walker_born", 0) + 1
            metrics["last_breed"] = {
                "tick": t, "agent_id": aid, "faction": fac,
                "pop": pop, "hands_after": len(hands) + 1, "target": target,
            }
            logger.event({
                "type": "walker_born", "tick": t, "agent_id": aid,
                "faction": fac, "x": x, "y": y,
                "population": pop, "hands_after": len(hands) + 1,
            })
            hands = [a for a in world.agents if getattr(a, "faction", "player") == fac]

        has_king = any(getattr(a, "role", "walker") == "king" for a in hands)
        has_knight = any(getattr(a, "role", "walker") == "knight" for a in hands)

        min_knight = int(SETTLEMENT_RULES.get("knight_min_era", 3))
        if (not has_king) and (not has_knight) and max_era >= min_knight:
            has_barracks = False
            for stx in world.structures:
                if stx.type != "barracks":
                    continue
                sid = sm.structure_settlement_id(stx.x, stx.y)
                if not sid:
                    continue
                if sm.get(sid).get("faction", "player") == fac:
                    has_barracks = True
                    break
            if has_barracks:
                walkers = sorted(
                    [a for a in hands if getattr(a, "role", "walker") == "walker"],
                    key=lambda a: a.agent_id,
                )
                if walkers:
                    chosen = walkers[0]
                    chosen.role = "knight"
                    has_knight = True
                    metrics["knight_events"] = metrics.get("knight_events", 0) + 1
                    metrics["last_knight"] = {
                        "tick": t, "agent_id": chosen.agent_id, "faction": fac, "era": max_era,
                    }
                    logger.event({
                        "type": "knight_raised", "tick": t,
                        "agent_id": chosen.agent_id, "faction": fac, "era": max_era,
                    })

        min_king = int(SETTLEMENT_RULES.get("king_min_era", 4))
        if (not has_king) and max_era >= min_king:
            ranked = sorted(hands, key=lambda a: (
                0 if getattr(a, "role", "walker") == "knight" else 1,
                a.agent_id,
            ))
            if ranked:
                chosen = ranked[0]
                chosen.role = "king"
                cap["government"] = True
                cap["crown"] = chosen.agent_id
                metrics["king_events"] = metrics.get("king_events", 0) + 1
                metrics["last_king"] = {
                    "tick": t, "agent_id": chosen.agent_id, "faction": fac,
                    "settlement_id": cap.get("id"), "era": max_era,
                }
                logger.event({
                    "type": "king_crowned", "tick": t,
                    "agent_id": chosen.agent_id, "faction": fac,
                    "settlement_id": cap.get("id"), "era": max_era,
                })
        elif has_king:
            king = next(a for a in hands if getattr(a, "role", "walker") == "king")
            cap["government"] = True
            cap["crown"] = king.agent_id

        hands = [a for a in world.agents if getattr(a, "faction", "player") == fac]
        has_scribe = any(getattr(a, "role", "walker") == "scribe" for a in hands)
        has_builder = any(getattr(a, "role", "walker") == "builder" for a in hands)
        min_spec = int(SETTLEMENT_RULES.get("specialist_min_era", 4))
        has_science = _faction_has_job(world, sm, fac, _SCIENCE_PREF)
        if max_era >= min_spec and has_science:
            walkers = sorted(
                [a for a in hands if getattr(a, "role", "walker") == "walker"],
                key=lambda a: a.agent_id,
            )
            if (not has_scribe) and walkers:
                chosen = walkers[0]
                chosen.role = "scribe"
                walkers = walkers[1:]
                metrics["scribe_events"] = metrics.get("scribe_events", 0) + 1
                metrics["last_scribe"] = {
                    "tick": t, "agent_id": chosen.agent_id, "faction": fac, "era": max_era,
                }
                logger.event({
                    "type": "scribe_named", "tick": t,
                    "agent_id": chosen.agent_id, "faction": fac, "era": max_era,
                })
            if (not has_builder) and walkers:
                chosen = walkers[0]
                chosen.role = "builder"
                metrics["builder_events"] = metrics.get("builder_events", 0) + 1
                metrics["last_builder"] = {
                    "tick": t, "agent_id": chosen.agent_id, "faction": fac, "era": max_era,
                }
                logger.event({
                    "type": "builder_named", "tick": t,
                    "agent_id": chosen.agent_id, "faction": fac, "era": max_era,
                })

        hands = [a for a in world.agents if getattr(a, "faction", "player") == fac]
        has_crew = any(getattr(a, "role", "walker") == "crew" for a in hands)
        min_ind = int(SETTLEMENT_RULES.get("industry_min_era", 5))
        if (not has_crew) and max_era >= min_ind:
            walkers = sorted(
                [a for a in hands if getattr(a, "role", "walker") == "walker"],
                key=lambda a: a.agent_id,
            )
            if walkers:
                chosen = walkers[0]
                chosen.role = "crew"
                metrics["crew_events"] = metrics.get("crew_events", 0) + 1
                metrics["last_crew"] = {
                    "tick": t, "agent_id": chosen.agent_id, "faction": fac, "era": max_era,
                }
                logger.event({
                    "type": "crew_named", "tick": t,
                    "agent_id": chosen.agent_id, "faction": fac, "era": max_era,
                })
from sim.core.build_governors import (
    resolve_building, can_build_hut, can_build_granary, can_build_mine, can_build_road,
    can_build_workshop, can_build_barracks, can_build_market, can_build_temple,
    can_build_academy, can_build_walls, can_build_irrigation, can_build_library,
    can_build_foundry, can_build_hall, can_build_command, can_build_lab, can_build_observatory,
    can_build_mill, can_build_warehouse, can_build_wonder, can_build_airport,
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
    "mill": {"wood": 4, "stone": 4},
    "warehouse": {"wood": 4, "stone": 3},
    "wonder": {"wood": 6, "stone": 6},
    "airport": {"wood": 6, "stone": 5},
}

STACKABLE = {"storage", "farm", "granary", "mine", "road", "workshop", "barracks",
             "market", "temple", "academy", "walls", "irrigation", "library",
             "foundry", "hall", "command", "lab", "observatory", "mill", "warehouse", "wonder", "airport"}


def _train_waypoints(world, sm, fac):
    pts = []
    seen = set()
    towns = sorted(
        [s for s in sm.all() if s.get("faction", "player") == fac],
        key=lambda s: str(s.get("id") or ""),
    )
    for s in towns:
        xy = (int(s["x"]), int(s["y"]))
        if xy not in seen:
            seen.add(xy)
            pts.append(xy)
    jobs = []
    for stx in world.structures:
        if stx.type not in ("warehouse", "mill", "foundry"):
            continue
        sid = sm.structure_settlement_id(stx.x, stx.y)
        if not sid:
            continue
        if sm.get(sid).get("faction", "player") != fac:
            continue
        rank = {"warehouse": 0, "mill": 1, "foundry": 2}[stx.type]
        jobs.append((rank, int(stx.y), int(stx.x)))
    for _, y, x in sorted(jobs):
        xy = (x, y)
        if xy not in seen:
            seen.add(xy)
            pts.append(xy)
    return pts


def _faction_has_warehouse(world, sm, fac) -> bool:
    for stx in world.structures:
        if stx.type != "warehouse":
            continue
        sid = sm.structure_settlement_id(stx.x, stx.y)
        if sid and sm.get(sid).get("faction", "player") == fac:
            return True
    return False


def _train_stop(world, sm, tr):
    st = world.structure_at(int(tr["x"]), int(tr["y"]))
    sid = sm.nearest(int(tr["x"]), int(tr["y"]), faction=tr.get("faction"))
    if sid is None:
        return
    s = sm.get(sid)
    if st is not None and st.type == "mill" and int(tr.get("cargo", 0) or 0) == 0:
        if not s.get("mill_live"):
            return
        wood = int(s.get("wood_stock", 0) or 0)
        if wood >= 1:
            s["wood_stock"] = wood - 1
            tr["cargo"] = 1
        return
    if int(tr.get("cargo", 0) or 0) <= 0:
        return
    has_wh = _faction_has_warehouse(world, sm, tr.get("faction"))
    if st is not None and st.type == "warehouse":
        goods = int(tr["cargo"])
        s["wood_stock"] = int(s.get("wood_stock", 0) or 0) + goods
        s["goods_stock"] = int(s.get("goods_stock", 0) or 0) + goods
        tr["cargo"] = 0
        return
    if not has_wh and (st is None or st.type != "mill"):
        s["wood_stock"] = int(s.get("wood_stock", 0) or 0) + int(tr["cargo"])
        tr["cargo"] = 0


def step_trains(world, sm, t, metrics, logger):
    """One train a pole after industry. No RNG. Roads are the line."""
    if getattr(world, "trains", None) is None:
        world.trains = []
    industrial = set()
    for s in sm.all():
        if int(s.get("era", 2) or 2) >= 5:
            industrial.add(s.get("faction", "player"))
    have = {tr.get("faction") for tr in world.trains}
    prefixes = {"player": "TW", "rival": "TE", "north": "TN", "south": "TS"}
    for fac in industrial:
        if fac in have:
            continue
        towns = [s for s in sm.all() if s.get("faction", "player") == fac]
        if not towns:
            continue
        cap = _capital(towns)
        tr = {
            "id": prefixes.get(fac, "T") + "0",
            "faction": fac,
            "x": int(cap["x"]),
            "y": int(cap["y"]),
            "target": 1,
            "cargo": 0,
        }
        world.trains.append(tr)
        metrics["train_events"] = metrics.get("train_events", 0) + 1
        metrics["last_train"] = {"tick": t, "train_id": tr["id"], "faction": fac}
        logger.event({
            "type": "train_rolled", "tick": t,
            "train_id": tr["id"], "faction": fac,
            "x": tr["x"], "y": tr["y"],
        })
    w, h = int(world.width), int(world.height)
    for tr in world.trains:
        pts = _train_waypoints(world, sm, tr.get("faction", "player"))
        if len(pts) < 2:
            continue
        ti = int(tr.get("target", 0) or 0) % len(pts)
        tx, ty = pts[ti]
        if int(tr["x"]) == tx and int(tr["y"]) == ty:
            _train_stop(world, sm, tr)
            tr["target"] = (ti + 1) % len(pts)
            tx, ty = pts[tr["target"]]
        if int(tr["x"]) != tx:
            tr["x"] = int(tr["x"]) + (1 if tx > int(tr["x"]) else -1)
        elif int(tr["y"]) != ty:
            tr["y"] = int(tr["y"]) + (1 if ty > int(tr["y"]) else -1)
        tr["x"] = max(0, min(w - 1, int(tr["x"])))
        tr["y"] = max(0, min(h - 1, int(tr["y"])))


def _airports(world):
    order = {"player": 0, "rival": 1, "north": 2, "south": 3}
    found = []
    for stx in world.structures:
        if stx.type != "airport":
            continue
        sid = None
        found.append(stx)
    found.sort(key=lambda st: (order.get(getattr(st, "faction", "player"), 9), int(st.y), int(st.x)))
    # faction from nearest settlement later; sort by position for stability
    found.sort(key=lambda st: (int(st.y), int(st.x)))
    return found


def _airport_faction(world, sm, stx):
    sid = sm.structure_settlement_id(stx.x, stx.y)
    if not sid:
        return "player"
    return sm.get(sid).get("faction", "player")


def step_planes(world, sm, t, metrics, logger):
    """One plane a pole after an airport. No RNG. Flies the island, 2 tiles a tick."""
    if getattr(world, "planes", None) is None:
        world.planes = []
    airs = []
    for stx in world.structures:
        if stx.type != "airport":
            continue
        fac = _airport_faction(world, sm, stx)
        airs.append((fac, int(stx.x), int(stx.y)))
    airs.sort(key=lambda r: ({"player": 0, "rival": 1, "north": 2, "south": 3}.get(r[0], 9), r[2], r[1]))
    have = {p.get("faction") for p in world.planes}
    prefixes = {"player": "PW", "rival": "PE", "north": "PN", "south": "PS"}
    for fac, x, y in airs:
        if fac in have:
            continue
        pl = {
            "id": prefixes.get(fac, "P") + "0",
            "faction": fac,
            "x": x, "y": y,
            "target": 1,
        }
        world.planes.append(pl)
        metrics["plane_events"] = metrics.get("plane_events", 0) + 1
        metrics["last_plane"] = {"tick": t, "plane_id": pl["id"], "faction": fac}
        logger.event({
            "type": "plane_rolled", "tick": t,
            "plane_id": pl["id"], "faction": fac, "x": x, "y": y,
        })
    pts = [(x, y) for _f, x, y in airs]
    if len(pts) < 1:
        return
    w, h = int(world.width), int(world.height)
    for pl in world.planes:
        if len(pts) == 1:
            dests = pts + pts
        else:
            dests = pts
        ti = int(pl.get("target", 0) or 0) % len(dests)
        tx, ty = dests[ti]
        if int(pl["x"]) == tx and int(pl["y"]) == ty:
            pl["target"] = (ti + 1) % len(dests)
            tx, ty = dests[pl["target"]]
        for _ in range(2):
            if int(pl["x"]) == tx and int(pl["y"]) == ty:
                break
            if int(pl["x"]) != tx:
                pl["x"] = int(pl["x"]) + (1 if tx > int(pl["x"]) else -1)
            elif int(pl["y"]) != ty:
                pl["y"] = int(pl["y"]) + (1 if ty > int(pl["y"]) else -1)
            pl["x"] = max(0, min(w - 1, int(pl["x"])))
            pl["y"] = max(0, min(h - 1, int(pl["y"])))


def _own_struct(world, sm, fac, kind):
    for stx in world.structures:
        if stx.type != kind:
            continue
        if _airport_faction(world, sm, stx) == fac:
            return stx
    return None


def _step_vehicle(veh, pts, w, h, speed=1):
    if len(pts) < 2:
        return
    ti = int(veh.get("target", 0) or 0) % len(pts)
    tx, ty = pts[ti]
    if int(veh["x"]) == tx and int(veh["y"]) == ty:
        veh["target"] = (ti + 1) % len(pts)
        tx, ty = pts[veh["target"]]
    for _ in range(speed):
        if int(veh["x"]) == tx and int(veh["y"]) == ty:
            break
        if int(veh["x"]) != tx:
            veh["x"] = int(veh["x"]) + (1 if tx > int(veh["x"]) else -1)
        elif int(veh["y"]) != ty:
            veh["y"] = int(veh["y"]) + (1 if ty > int(veh["y"]) else -1)
        veh["x"] = max(0, min(w - 1, int(veh["x"])))
        veh["y"] = max(0, min(h - 1, int(veh["y"])))


def step_traffic(world, sm, t, metrics, logger):
    """One taxi and one bus a pole after the airport. No RNG. Streets stay streets."""
    if getattr(world, "taxis", None) is None:
        world.taxis = []
    if getattr(world, "buses", None) is None:
        world.buses = []
    live = set()
    for s in sm.all():
        if int(s.get("era", 2) or 2) >= 6:
            live.add(s.get("faction", "player"))
    for stx in world.structures:
        if stx.type == "airport":
            live.add(_airport_faction(world, sm, stx))
    have_t = {v.get("faction") for v in world.taxis}
    have_b = {v.get("faction") for v in world.buses}
    tpre = {"player": "CW", "rival": "CE", "north": "CN", "south": "CS"}
    bpre = {"player": "BW", "rival": "BE", "north": "BN", "south": "BS"}
    for fac in ("player", "rival", "north", "south"):
        if fac not in live:
            continue
        towns = [s for s in sm.all() if s.get("faction", "player") == fac]
        if not towns:
            continue
        cap = _capital(towns)
        cx, cy = int(cap["x"]), int(cap["y"])
        if fac not in have_t:
            cab = {"id": tpre.get(fac, "C") + "0", "faction": fac, "x": cx, "y": cy, "target": 1}
            world.taxis.append(cab)
            metrics["taxi_events"] = metrics.get("taxi_events", 0) + 1
            metrics["last_taxi"] = {"tick": t, "taxi_id": cab["id"], "faction": fac}
            logger.event({"type": "taxi_rolled", "tick": t, "taxi_id": cab["id"], "faction": fac})
        if fac not in have_b:
            bus = {"id": bpre.get(fac, "B") + "0", "faction": fac, "x": cx, "y": cy, "target": 1}
            world.buses.append(bus)
            metrics["bus_events"] = metrics.get("bus_events", 0) + 1
            metrics["last_bus"] = {"tick": t, "bus_id": bus["id"], "faction": fac}
            logger.event({"type": "bus_rolled", "tick": t, "bus_id": bus["id"], "faction": fac})
    w, h = int(world.width), int(world.height)
    for cab in world.taxis:
        towns = [s for s in sm.all() if s.get("faction", "player") == cab.get("faction")]
        if not towns:
            continue
        cap = _capital(towns)
        cx, cy = int(cap["x"]), int(cap["y"])
        hall = _own_struct(world, sm, cab.get("faction"), "hall")
        pts = [(cx, cy), (min(w - 1, cx + 2), cy), (cx, max(0, cy - 2)), (max(0, cx - 2), cy)]
        if hall:
            pts.append((int(hall.x), int(hall.y)))
        _step_vehicle(cab, pts, w, h, 1)
    for bus in world.buses:
        fac = bus.get("faction")
        towns = [s for s in sm.all() if s.get("faction", "player") == fac]
        if not towns:
            continue
        cap = _capital(towns)
        pts = [(int(cap["x"]), int(cap["y"]))]
        for kind in ("warehouse", "airport", "hall"):
            st = _own_struct(world, sm, fac, kind)
            if st:
                xy = (int(st.x), int(st.y))
                if xy not in pts:
                    pts.append(xy)
        _step_vehicle(bus, pts, w, h, 1)


def run_sim(
    seed: int, ticks: int, snapshot_every: int,
    agent_kind: str = "utility", policy_weights: dict = None, return_score: bool = False,
    governor_command: Optional[str] = None, scenario_commands: Optional[str] = None,
    control_agent_id: Optional[str] = None, control_policy: str = "idle", num_agents: int = 4,
    quiet: bool = False,
    playable: bool = False, choice_policy: str = "first", decision_picker=None,
    on_tick=None, on_tick_every: int = 4,
    rival_agents: int = 0,
    pole_agents: int = 0,
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
    world = make_world(cfg, rng, num_agents=num_agents, rival_agents=rival_agents, pole_agents=pole_agents)

    if scenario.start_food or scenario.start_wood or scenario.start_stone:
        for a in world.agents:
            a.inv_food, a.inv_wood, a.inv_stone = scenario.start_food, scenario.start_wood, scenario.start_stone
        logger.event({"type": "scenario_start_inventory", "tick": 0,
                      "food": scenario.start_food, "wood": scenario.start_wood, "stone": scenario.start_stone})

    gov = Governor()
    rival_gov = Governor()
    north_gov = Governor()
    south_gov = Governor()
    if governor_command:
        status = gov.apply_command(governor_command)
        logger.event({"type": "governor_command", "tick": 0, "command": governor_command,
                      "status": status, "state": gov.to_dict()})
    if rival_agents:
        rival_focus = "army" if (int(seed) % 2 == 0) else "science"
        rival_gov.apply_command(f"focus {rival_focus}")
        logger.event({"type": "rival_governor", "tick": 0, "command": f"focus {rival_focus}",
                      "state": rival_gov.to_dict()})
    if pole_agents:
        logger.event({"type": "poles", "tick": 0, "north": int(pole_agents), "south": int(pole_agents)})
    govs = {"player": gov, "rival": rival_gov, "north": north_gov, "south": south_gov}
    if scenario_commands:
        logger.event({"type": "scenario_loaded", "tick": 0, "commands": scenario_commands, "state": scenario.to_dict()})

    if agent_kind == "utility":
        from sim.agents.utility_agent import UtilityAgent
        w = policy_weights or {}
        player_bias = gov.bias_weights()
        rival_bias = rival_gov.bias_weights()
        north_bias = north_gov.bias_weights()
        south_bias = south_gov.bias_weights()
        brains = {}
        bias_of = {
            "player": player_bias, "rival": rival_bias,
            "north": north_bias, "south": south_bias,
        }
        for a in world.agents:
            fac = getattr(a, "faction", "player")
            brains[a.agent_id] = UtilityAgent(a.agent_id, w, governor_bias=bias_of.get(fac, player_bias))
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
        "build_lab": 0, "build_observatory": 0, "build_mill": 0, "build_warehouse": 0, "build_wonder": 0, "build_airport": 0,
        "farm_harvest_events": 0, "farm_food_total": 0,
        "granary_food_total": 0, "mine_stone_total": 0, "workshop_tools_total": 0, "barracks_soldiers_total": 0,
        "tools_boost_events": 0, "soldier_defend_events": 0, "raid_events": 0, "raid_loot_total": 0,
        "age_up_events": 0, "age_up4_events": 0,
        "market_wood_total": 0, "market_stone_total": 0, "temple_food_total": 0,
        "academy_knowledge_total": 0, "subject_unlock_events": 0,
        "discovery_events": 0,
        "walker_born": 0, "knight_events": 0, "king_events": 0,
        "scribe_events": 0, "builder_events": 0,
        "crew_events": 0, "train_events": 0, "plane_events": 0, "taxi_events": 0, "bus_events": 0, "age_up5_events": 0, "age_up6_events": 0,
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
        "quiet": quiet, "rival_agents": rival_agents, "pole_agents": pole_agents,
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
            sm.active_faction = fac if (rival_agents or pole_agents) else None
            tile = world.tile_at(a.x, a.y)
            st = world.structure_at(a.x, a.y)
            sm.try_deposit(a, tick=t, world=world)
            nearest_sid = sm.nearest(a.x, a.y)
            nearest_data = sm.get(nearest_sid) if nearest_sid else None
            own_settlements = list(sm.own().values()) if (rival_agents or pole_agents) else sm.all()
            own_structs = []
            if rival_agents or pole_agents:
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
            action = _maybe_home_action(a, sm, world)
            if action is None:
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
                elif b == "mill":
                    allowed, gate_note = can_build_mill(a.x, a.y, sm, world)
                    if not allowed: ok, note = False, gate_note
                elif b == "warehouse":
                    allowed, gate_note = can_build_warehouse(a.x, a.y, sm, world)
                    if not allowed: ok, note = False, gate_note
                elif b == "wonder":
                    allowed, gate_note = can_build_wonder(a.x, a.y, sm, world)
                    if not allowed: ok, note = False, gate_note
                elif b == "airport":
                    allowed, gate_note = can_build_airport(a.x, a.y, sm, world)
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
        try_breed_and_knight(
            world, sm, brains, t, metrics, logger, rival_agents,
            agent_kind, policy_weights, gov, rival_gov, play_state,
            pole_agents=pole_agents, govs=govs,
        )
        step_trains(world, sm, t, metrics, logger)
        step_planes(world, sm, t, metrics, logger)
        step_traffic(world, sm, t, metrics, logger)

        if (rival_agents or pole_agents) and headline is None:
            from sim.core.outcome import detect_early, side_from_world
            for s in sm.all():
                founded.add(s.get("faction", "player"))
            facs = ("player", "rival", "north", "south") if pole_agents else (("player", "rival") if rival_agents else ("player",))
            sides = {f: side_from_world(sm, world, f) for f in facs}
            early = detect_early(t, sides, founded)
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

    if (rival_agents or pole_agents) and headline is None:
        from sim.core.outcome import detect_survival, side_from_world
        last_t = world.tick if ticks else 0
        facs = ("player", "rival", "north", "south") if pole_agents else (("player", "rival") if rival_agents else ("player",))
        sides = {f: side_from_world(sm, world, f) for f in facs}
        headline = detect_survival(last_t, sides)
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
        "pole_agents": pole_agents,
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
