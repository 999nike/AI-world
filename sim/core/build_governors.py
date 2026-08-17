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
    "shop": "workshop", "toolshed": "workshop", "ws": "workshop",
    "barrack": "barracks", "military": "barracks", "fort": "barracks",
    "trade": "market", "bazaar": "market", "shop_market": "market",
    "shrine": "temple", "church": "temple", "sanctuary": "temple",
    "school": "academy", "university": "academy", "college": "academy",
    "wall": "walls", "fortification": "walls", "rampart": "walls",
    "irrigate": "irrigation", "canal": "irrigation", "ditch": "irrigation",
    "archive": "library", "scriptorium": "library",
    "forge": "foundry", "smelter": "foundry", "foundary": "foundry",
    "civic": "hall", "townhall": "hall", "forum": "hall", "plaza": "hall",
    "hq": "command", "warroom": "command", "strategy_hq": "command", "cmd": "command",
    "science": "lab", "science_lab": "lab", "research": "lab", "laboratory": "lab",
    "obs": "observatory", "observe": "observatory", "telescope": "observatory",
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
    workshop = sm.count_structures_of_type(sid, "workshop", world)
    barracks = sm.count_structures_of_type(sid, "barracks", world)
    market = sm.count_structures_of_type(sid, "market", world)
    temple = sm.count_structures_of_type(sid, "temple", world)
    academy = sm.count_structures_of_type(sid, "academy", world)
    walls = sm.count_structures_of_type(sid, "walls", world)
    irrigation = sm.count_structures_of_type(sid, "irrigation", world)
    library = sm.count_structures_of_type(sid, "library", world)
    foundry = sm.count_structures_of_type(sid, "foundry", world)
    hall = sm.count_structures_of_type(sid, "hall", world)
    command = sm.count_structures_of_type(sid, "command", world)
    lab = sm.count_structures_of_type(sid, "lab", world)
    observatory = sm.count_structures_of_type(sid, "observatory", world)
    total = (farms + stor + gran + mine + road + workshop + barracks +
             market + temple + academy + walls + irrigation + library +
             foundry + hall + command + lab + observatory +
             sm.count_structures_of_type(sid, "hut", world))
    return (farms, stor, gran, mine, road, workshop, barracks, market, temple,
            academy, walls, irrigation, library, foundry, hall, command, lab, observatory, total)


def resolve_building(requested, agent_x, agent_y, sm, world) -> Tuple[str, str]:
    b = normalise_building_name(requested)
    note = ""

    total_structures = len(getattr(world, "structures", []) or [])
    if sm.count() == 0 or total_structures == 0:
        return "farm", "bootstrap_force_farm" if b != "farm" else ""

    best_sid = sm.nearest(agent_x, agent_y)
    if best_sid is None:
        return "farm", "bootstrap_force_farm"

    (farms, stor, gran, mine, road, workshop, barracks, market, temple,
     academy, walls, irrigation, library, foundry, hall, command, lab, observatory, total) = _settlement_struct_counts(best_sid, sm, world)

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
        if mine < 1 and total < 4:
            if stor < 1:
                return "storage", "road_needs_base"
            return "farm", "road_needs_base"

    if b == "workshop":
        if workshop >= 1:
            return "hut", "workshop_capped_to_hut"
        if mine < 1:
            return "mine", "workshop_needs_mine"
        if gran < 1 and road < 1:
            return "granary", "workshop_needs_granary_or_road"

    if b == "barracks":
        if barracks >= 1:
            return "hut", "barracks_capped_to_hut"
        if workshop < 1:
            return "workshop", "barracks_needs_workshop"

    if b == "market":
        if market >= 1:
            return "hut", "market_capped_to_hut"
        if barracks < 1:
            return "barracks", "market_needs_barracks"

    if b == "temple":
        if temple >= 1:
            return "hut", "temple_capped_to_hut"
        if market < 1:
            return "market", "temple_needs_market"

    if b == "academy":
        if academy >= 1:
            return "hut", "academy_capped_to_hut"
        if temple < 1:
            return "temple", "academy_needs_temple"

    if b == "walls":
        if walls >= 1:
            return "hut", "walls_capped_to_hut"
        if barracks < 1:
            return "barracks", "walls_needs_barracks"

    if b == "irrigation":
        if irrigation >= 1:
            return "hut", "irrigation_capped_to_hut"
        s = sm.get(best_sid)
        if int(s.get("era", 2)) < 4:
            return "hut", "irrigation_needs_era4"
        if "agriculture" not in (s.get("subjects") or []):
            return "hut", "irrigation_needs_agriculture"

    if b == "library":
        if library >= 1:
            return "hut", "library_capped_to_hut"
        s = sm.get(best_sid)
        if int(s.get("era", 2)) < 4:
            return "hut", "library_needs_era4"
        if "inquiry" not in (s.get("subjects") or []):
            return "hut", "library_needs_inquiry"

    if b == "foundry":
        if foundry >= 1:
            return "hut", "foundry_capped_to_hut"
        s = sm.get(best_sid)
        if int(s.get("era", 2)) < 4:
            return "hut", "foundry_needs_era4"
        if "craft" not in (s.get("subjects") or []):
            return "hut", "foundry_needs_craft"

    if b == "hall":
        if hall >= 1:
            return "hut", "hall_capped_to_hut"
        s = sm.get(best_sid)
        if int(s.get("era", 2)) < 4:
            return "hut", "hall_needs_era4"
        if "organisation" not in (s.get("subjects") or []):
            return "hut", "hall_needs_organisation"

    if b == "command":
        if command >= 1:
            return "hut", "command_capped_to_hut"
        s = sm.get(best_sid)
        if int(s.get("era", 2)) < 4:
            return "hut", "command_needs_era4"
        if "strategy" not in (s.get("subjects") or []):
            return "hut", "command_needs_strategy"
        if barracks < 1:
            return "barracks", "command_needs_barracks"

    if b == "lab":
        if lab >= 1:
            return "hut", "lab_capped_to_hut"
        s = sm.get(best_sid)
        if int(s.get("era", 2)) < 4:
            return "hut", "lab_needs_era4"
        if "inquiry" not in (s.get("subjects") or []):
            return "hut", "lab_needs_inquiry"
        if library < 1:
            return "library", "lab_needs_library"

    if b == "observatory":
        if observatory >= 1:
            return "hut", "observatory_capped_to_hut"
        s = sm.get(best_sid)
        if int(s.get("era", 2)) < 4:
            return "hut", "observatory_needs_era4"
        if lab < 1:
            return "lab", "observatory_needs_lab"

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
    farms, stor, gran, mine, road, workshop, barracks, market, temple, academy, walls, irrigation, library, foundry, hall, command, lab, observatory, total = _settlement_struct_counts(best_sid, sm, world)
    if mine < 1 and total < 4:
        return False, "road_needs_mine_or_growth"
    return True, ""


def can_build_workshop(agent_x, agent_y, sm, world) -> Tuple[bool, str]:
    if sm.count() == 0:
        return False, "workshop_needs_settlement"
    best_sid = sm.nearest(agent_x, agent_y)
    if best_sid is None:
        return False, "workshop_needs_settlement"
    farms, stor, gran, mine, road, workshop, barracks, market, temple, academy, walls, irrigation, library, foundry, hall, command, lab, observatory, total = _settlement_struct_counts(best_sid, sm, world)
    if mine < 1:
        return False, "workshop_needs_mine"
    if gran < 1 and road < 1:
        return False, "workshop_needs_granary_or_road"
    if workshop >= 1:
        return False, "workshop_already_exists"
    return True, ""


def can_build_barracks(agent_x, agent_y, sm, world) -> Tuple[bool, str]:
    if sm.count() == 0:
        return False, "barracks_needs_settlement"
    best_sid = sm.nearest(agent_x, agent_y)
    if best_sid is None:
        return False, "barracks_needs_settlement"
    farms, stor, gran, mine, road, workshop, barracks, market, temple, academy, walls, irrigation, library, foundry, hall, command, lab, observatory, total = _settlement_struct_counts(best_sid, sm, world)
    if workshop < 1:
        return False, "barracks_needs_workshop"
    if barracks >= 1:
        return False, "barracks_already_exists"
    return True, ""


def can_build_market(agent_x, agent_y, sm, world) -> Tuple[bool, str]:
    if sm.count() == 0:
        return False, "market_needs_settlement"
    best_sid = sm.nearest(agent_x, agent_y)
    if best_sid is None:
        return False, "market_needs_settlement"
    s = sm.get(best_sid)
    if int(s.get("era", 2)) < 3:
        return False, "market_needs_era3"
    farms, stor, gran, mine, road, workshop, barracks, market, temple, academy, walls, irrigation, library, foundry, hall, command, lab, observatory, total = _settlement_struct_counts(best_sid, sm, world)
    if barracks < 1:
        return False, "market_needs_barracks"
    if market >= 1:
        return False, "market_already_exists"
    return True, ""


def can_build_temple(agent_x, agent_y, sm, world) -> Tuple[bool, str]:
    if sm.count() == 0:
        return False, "temple_needs_settlement"
    best_sid = sm.nearest(agent_x, agent_y)
    if best_sid is None:
        return False, "temple_needs_settlement"
    s = sm.get(best_sid)
    if int(s.get("era", 2)) < 3:
        return False, "temple_needs_era3"
    farms, stor, gran, mine, road, workshop, barracks, market, temple, academy, walls, irrigation, library, foundry, hall, command, lab, observatory, total = _settlement_struct_counts(best_sid, sm, world)
    if market < 1:
        return False, "temple_needs_market"
    if temple >= 1:
        return False, "temple_already_exists"
    return True, ""


def can_build_academy(agent_x, agent_y, sm, world) -> Tuple[bool, str]:
    if sm.count() == 0:
        return False, "academy_needs_settlement"
    best_sid = sm.nearest(agent_x, agent_y)
    if best_sid is None:
        return False, "academy_needs_settlement"
    s = sm.get(best_sid)
    if int(s.get("era", 2)) < 3:
        return False, "academy_needs_era3"
    farms, stor, gran, mine, road, workshop, barracks, market, temple, academy, walls, irrigation, library, foundry, hall, command, lab, observatory, total = _settlement_struct_counts(best_sid, sm, world)
    if temple < 1:
        return False, "academy_needs_temple"
    if academy >= 1:
        return False, "academy_already_exists"
    return True, ""


def can_build_walls(agent_x, agent_y, sm, world) -> Tuple[bool, str]:
    if sm.count() == 0:
        return False, "walls_needs_settlement"
    best_sid = sm.nearest(agent_x, agent_y)
    if best_sid is None:
        return False, "walls_needs_settlement"
    s = sm.get(best_sid)
    if int(s.get("era", 2)) < 3:
        return False, "walls_needs_era3"
    farms, stor, gran, mine, road, workshop, barracks, market, temple, academy, walls, irrigation, library, foundry, hall, command, lab, observatory, total = _settlement_struct_counts(best_sid, sm, world)
    if barracks < 1:
        return False, "walls_needs_barracks"
    if walls >= 1:
        return False, "walls_already_exists"
    return True, ""


def can_build_irrigation(agent_x, agent_y, sm, world) -> Tuple[bool, str]:
    if sm.count() == 0:
        return False, "irrigation_needs_settlement"
    best_sid = sm.nearest(agent_x, agent_y)
    if best_sid is None:
        return False, "irrigation_needs_settlement"
    s = sm.get(best_sid)
    if int(s.get("era", 2)) < 4:
        return False, "irrigation_needs_era4"
    if "agriculture" not in (s.get("subjects") or []):
        return False, "irrigation_needs_agriculture"
    if sm.count_structures_of_type(best_sid, "irrigation", world) >= 1:
        return False, "irrigation_already_exists"
    return True, ""


def can_build_library(agent_x, agent_y, sm, world) -> Tuple[bool, str]:
    if sm.count() == 0:
        return False, "library_needs_settlement"
    best_sid = sm.nearest(agent_x, agent_y)
    if best_sid is None:
        return False, "library_needs_settlement"
    s = sm.get(best_sid)
    if int(s.get("era", 2)) < 4:
        return False, "library_needs_era4"
    if "inquiry" not in (s.get("subjects") or []):
        return False, "library_needs_inquiry"
    if sm.count_structures_of_type(best_sid, "library", world) >= 1:
        return False, "library_already_exists"
    return True, ""


def can_build_foundry(agent_x, agent_y, sm, world) -> Tuple[bool, str]:
    if sm.count() == 0:
        return False, "foundry_needs_settlement"
    best_sid = sm.nearest(agent_x, agent_y)
    if best_sid is None:
        return False, "foundry_needs_settlement"
    s = sm.get(best_sid)
    if int(s.get("era", 2)) < 4:
        return False, "foundry_needs_era4"
    if "craft" not in (s.get("subjects") or []):
        return False, "foundry_needs_craft"
    if sm.count_structures_of_type(best_sid, "foundry", world) >= 1:
        return False, "foundry_already_exists"
    return True, ""


def can_build_hall(agent_x, agent_y, sm, world) -> Tuple[bool, str]:
    if sm.count() == 0:
        return False, "hall_needs_settlement"
    best_sid = sm.nearest(agent_x, agent_y)
    if best_sid is None:
        return False, "hall_needs_settlement"
    s = sm.get(best_sid)
    if int(s.get("era", 2)) < 4:
        return False, "hall_needs_era4"
    if "organisation" not in (s.get("subjects") or []):
        return False, "hall_needs_organisation"
    if sm.count_structures_of_type(best_sid, "hall", world) >= 1:
        return False, "hall_already_exists"
    return True, ""


def can_build_command(agent_x, agent_y, sm, world) -> Tuple[bool, str]:
    if sm.count() == 0:
        return False, "command_needs_settlement"
    best_sid = sm.nearest(agent_x, agent_y)
    if best_sid is None:
        return False, "command_needs_settlement"
    s = sm.get(best_sid)
    if int(s.get("era", 2)) < 4:
        return False, "command_needs_era4"
    if "strategy" not in (s.get("subjects") or []):
        return False, "command_needs_strategy"
    if sm.count_structures_of_type(best_sid, "barracks", world) < 1:
        return False, "command_needs_barracks"
    if sm.count_structures_of_type(best_sid, "command", world) >= 1:
        return False, "command_already_exists"
    return True, ""


def can_build_lab(agent_x, agent_y, sm, world) -> Tuple[bool, str]:
    if sm.count() == 0:
        return False, "lab_needs_settlement"
    best_sid = sm.nearest(agent_x, agent_y)
    if best_sid is None:
        return False, "lab_needs_settlement"
    s = sm.get(best_sid)
    if int(s.get("era", 2)) < 4:
        return False, "lab_needs_era4"
    if "inquiry" not in (s.get("subjects") or []):
        return False, "lab_needs_inquiry"
    if sm.count_structures_of_type(best_sid, "library", world) < 1:
        return False, "lab_needs_library"
    if sm.count_structures_of_type(best_sid, "lab", world) >= 1:
        return False, "lab_already_exists"
    return True, ""


def can_build_observatory(agent_x, agent_y, sm, world) -> Tuple[bool, str]:
    if sm.count() == 0:
        return False, "observatory_needs_settlement"
    best_sid = sm.nearest(agent_x, agent_y)
    if best_sid is None:
        return False, "observatory_needs_settlement"
    s = sm.get(best_sid)
    if int(s.get("era", 2)) < 4:
        return False, "observatory_needs_era4"
    if sm.count_structures_of_type(best_sid, "lab", world) < 1:
        return False, "observatory_needs_lab"
    if sm.count_structures_of_type(best_sid, "observatory", world) >= 1:
        return False, "observatory_already_exists"
    return True, ""
