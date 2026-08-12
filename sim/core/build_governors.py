"""Build governors for AI-world."""
from __future__ import annotations

from typing import Optional, Tuple

from sim.world.settlements import SettlementManager


BUILD_ALIASES = {
    "stor": "storage", "store": "storage", "warehouse": "storage",
    "house": "hut", "home": "hut",
    "grain": "granary", "gran": "granary",
    "quarry": "mine",
    "path": "road", "track": "road",
}

FARM_SOFT_CAP = 3


def normalise_building_name(raw: Optional[str]) -> str:
    if raw is None:
        return ""
    b = str(raw).strip().lower()
    return BUILD_ALIASES.get(b, b)


def _settlement_struct_counts(sid, sm, world):
    farms = sm.count_structures_of_type(sid, "farm", world)
    stor = sm.count_structures_of_type(sid, "storage", world)
    gran = sm.count_structures_of_type(sid, "granary", world)
    mine = sm.count_structures_of_type(sid, "mine", world)
    road = sm.count_structures_of_type(sid, "road", world)
    total = farms + stor + gran + mine + road + sm.count_structures_of_type(sid, "hut", world)
    return farms, stor, gran, mine, road, total


def resolve_building(requested, agent_x, agent_y, sm, world) -> Tuple[str, str]:
    b = normalise_building_name(requested)
    note = ""

    total_structures = len(getattr(world, "structures", []) or [])
    if sm.count() == 0 or total_structures == 0:
        return "farm", "bootstrap_force_farm" if b != "farm" else ""

    best_sid = sm.nearest(agent_x, agent_y)
    if best_sid is None:
        return "farm", "bootstrap_force_farm"

    farms, stor, gran, mine, road, total = _settlement_struct_counts(best_sid, sm, world)

    if farms == 0:
        return "farm", "redirected_to_farm" if b != "farm" else ""

    if b == "storage" and stor >= 1:
        return "hut", "storage_capped_to_hut"

    if b == "farm" and farms >= FARM_SOFT_CAP:
        if stor >= 1:
            return "hut", "farm_capped_to_hut"
        return "storage", "farm_capped_to_storage"

    if b == "granary":
        if gran >= 1:
            return "hut", "granary_capped_to_hut"
        if stor < 1:
            return "storage", "granary_needs_storage"
        if farms < 1:
            return "farm", "granary_needs_farm"

    if b == "mine":
        if mine >= 1:
            return "hut", "mine_capped_to_hut"
        if stor < 1:
            return "storage", "mine_needs_storage"
        if farms < 1:
            return "farm", "mine_needs_farm"

    if b == "road":
        # Gate: mine exists OR settlement has enough structures
        if mine < 1 and total < 4:
            if stor < 1:
                return "storage", "road_needs_base"
            return "farm", "road_needs_base"

    return b, note


def can_build_hut(agent_x, agent_y, sm, world) -> Tuple[bool, str]:
    if sm.count() == 0:
        return False, "hut_requires_storage"
    best_sid = sm.nearest(agent_x, agent_y)
    if best_sid is None:
        return False, "hut_requires_storage"
    if sm.count_structures_of_type(best_sid, "storage", world) == 0:
        return False, "hut_requires_storage"
    if int(sm.get(best_sid).get("starve_ticks", 0)) > 0:
        return False, "hut_blocked_while_starving"
    return True, ""


def can_build_granary(agent_x, agent_y, sm, world) -> Tuple[bool, str]:
    if sm.count() == 0:
        return False, "granary_needs_settlement"
    best_sid = sm.nearest(agent_x, agent_y)
    if best_sid is None:
        return False, "granary_needs_settlement"
    if sm.count_structures_of_type(best_sid, "storage", world) < 1:
        return False, "granary_needs_storage"
    if sm.count_structures_of_type(best_sid, "farm", world) < 1:
        return False, "granary_needs_farm"
    if sm.count_structures_of_type(best_sid, "granary", world) >= 1:
        return False, "granary_already_exists"
    return True, ""


def can_build_mine(agent_x, agent_y, sm, world) -> Tuple[bool, str]:
    if sm.count() == 0:
        return False, "mine_needs_settlement"
    best_sid = sm.nearest(agent_x, agent_y)
    if best_sid is None:
        return False, "mine_needs_settlement"
    if sm.count_structures_of_type(best_sid, "storage", world) < 1:
        return False, "mine_needs_storage"
    if sm.count_structures_of_type(best_sid, "farm", world) < 1:
        return False, "mine_needs_farm"
    if sm.count_structures_of_type(best_sid, "mine", world) >= 1:
        return False, "mine_already_exists"
    return True, ""


def can_build_road(agent_x, agent_y, sm, world) -> Tuple[bool, str]:
    if sm.count() == 0:
        return False, "road_needs_settlement"
    best_sid = sm.nearest(agent_x, agent_y)
    if best_sid is None:
        return False, "road_needs_settlement"
    farms, stor, gran, mine, road, total = _settlement_struct_counts(best_sid, sm, world)
    if mine < 1 and total < 4:
        return False, "road_needs_mine_or_growth"
    return True, ""
