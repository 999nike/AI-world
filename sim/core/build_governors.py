"""Build governors for AI-world.

Centralises the scattered farm-bootstrap / storage-cap / hut-gate rules
that previously lived as duplicated blocks inside simloop.py.
"""
from __future__ import annotations

from typing import Optional, Tuple

from sim.world.settlements import SettlementManager, SETTLEMENT_RULES


BUILD_ALIASES = {
    "stor": "storage",
    "store": "storage",
    "warehouse": "storage",
    "house": "hut",
    "home": "hut",
}

# After this many farms, further farm attempts are redirected
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
    """Apply all build governors and return (final_building, note).

    Order of priority:
    1. Normalise aliases
    2. Force first farm if none exists
    3. Cap storage at 1 (extra → hut)
    4. Soft-cap farms at FARM_SOFT_CAP
       - no storage yet → redirect to storage
       - storage exists → redirect to hut
    """
    b = normalise_building_name(requested)
    note = ""

    if sm.count() == 0:
        return b, note

    best_sid = sm.nearest(agent_x, agent_y)
    if best_sid is None:
        return b, note

    farms_here = sm.count_structures_of_type(best_sid, "farm", world)
    stor_here = sm.count_structures_of_type(best_sid, "storage", world)

    # Priority 1: establish agriculture first
    if farms_here == 0:
        if b in ("storage", "hut", "farm") or b == "":
            if b != "farm":
                note = "redirected_to_farm"
            b = "farm"
        return b, note

    # Priority 2: storage cap (max 1 per settlement)
    if b == "storage" and stor_here >= 1:
        b = "hut"
        note = "storage_capped_to_hut"

    # Priority 3: farm soft-cap (FIXED — applies even without storage)
    if b == "farm" and farms_here >= FARM_SOFT_CAP:
        if stor_here >= 1:
            b = "hut"
            note = "farm_capped_to_hut"
        else:
            b = "storage"
            note = "farm_capped_to_storage"

    return b, note


def can_build_hut(
    agent_x: int,
    agent_y: int,
    sm: SettlementManager,
    world,
) -> Tuple[bool, str]:
    """Hut gates (softened).

    Requires storage + not currently in a starvation streak.
    """
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
