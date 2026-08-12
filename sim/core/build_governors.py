"""Build governors for AI-world.

Centralises farm-bootstrap / storage-cap / hut-gate / granary rules.
"""
from __future__ import annotations

from typing import Optional, Tuple

from sim.world.settlements import SettlementManager


BUILD_ALIASES = {
    "stor": "storage",
    "store": "storage",
    "warehouse": "storage",
    "house": "hut",
    "home": "hut",
    "grain": "granary",
    "gran": "granary",
}

FARM_SOFT_CAP = 3


def normalise_building_name(raw: Optional[str]) -> str:
    if raw is None:
        return ""
    b = str(raw).strip().lower()
    return BUILD_ALIASES.get(b, b)


def resolve_building(
    requested: Optional[str],
    agent_x: int,
    agent_y: int,
    sm: SettlementManager,
    world,
) -> Tuple[str, str]:
    """Apply build governors. Returns (final_building, note)."""
    b = normalise_building_name(requested)
    note = ""

    total_structures = len(getattr(world, "structures", []) or [])
    if sm.count() == 0 or total_structures == 0:
        if b != "farm":
            note = "bootstrap_force_farm"
        return "farm", note

    best_sid = sm.nearest(agent_x, agent_y)
    if best_sid is None:
        return "farm", "bootstrap_force_farm"

    farms_here = sm.count_structures_of_type(best_sid, "farm", world)
    stor_here = sm.count_structures_of_type(best_sid, "storage", world)
    gran_here = sm.count_structures_of_type(best_sid, "granary", world)

    if farms_here == 0:
        if b != "farm":
            note = "redirected_to_farm"
        return "farm", note

    # Storage cap
    if b == "storage" and stor_here >= 1:
        b = "hut"
        note = "storage_capped_to_hut"

    # Farm soft-cap
    if b == "farm" and farms_here >= FARM_SOFT_CAP:
        if stor_here >= 1:
            b = "hut"
            note = "farm_capped_to_hut"
        else:
            b = "storage"
            note = "farm_capped_to_storage"

    # Granary: max 1, requires storage + farm already
    if b == "granary":
        if gran_here >= 1:
            b = "hut"
            note = "granary_capped_to_hut"
        elif stor_here < 1 or farms_here < 1:
            # Not ready — push toward missing piece
            if stor_here < 1:
                b = "storage"
                note = "granary_needs_storage"
            else:
                b = "farm"
                note = "granary_needs_farm"

    return b, note


def can_build_hut(
    agent_x: int,
    agent_y: int,
    sm: SettlementManager,
    world,
) -> Tuple[bool, str]:
    if sm.count() == 0:
        return False, "hut_requires_storage"

    best_sid = sm.nearest(agent_x, agent_y)
    if best_sid is None:
        return False, "hut_requires_storage"

    if sm.count_structures_of_type(best_sid, "storage", world) == 0:
        return False, "hut_requires_storage"

    ss = sm.get(best_sid)
    if int(ss.get("starve_ticks", 0)) > 0:
        return False, "hut_blocked_while_starving"

    return True, ""


def can_build_granary(
    agent_x: int,
    agent_y: int,
    sm: SettlementManager,
    world,
) -> Tuple[bool, str]:
    """Granary requires storage + at least one farm, max 1."""
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
