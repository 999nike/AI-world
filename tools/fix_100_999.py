#!/usr/bin/env python3
"""One-shot fix for seeds 100/999. Run: python tools/fix_100_999.py"""
from pathlib import Path

print("fix_100_999 applying...")

# settlements
p = Path("sim/world/settlements.py")
s = p.read_text(encoding="utf-8")
s = s.replace('"age_up4_min_pop": 20', '"age_up4_min_pop": 15')
s = s.replace('age_up4_min_pop", 20)', 'age_up4_min_pop", 15)')
a = "military = self.settlement_has_workshop(sid, world) and self.settlement_has_barracks(sid, world)"
b = (
    "any_workshop = any(self.settlement_has_workshop(sid, world) for sid in self.settlements)\n"
    "            any_barracks = any(self.settlement_has_barracks(sid, world) for sid in self.settlements)\n"
    "            has_ws = self.settlement_has_workshop(sid, world)\n"
    "            has_br = self.settlement_has_barracks(sid, world)\n"
    "            military = (has_ws and has_br) or (has_ws and any_barracks) or (has_br and any_workshop)"
)
if a in s:
    s = s.replace(a, b)
    print("  OK settlements split")
else:
    print("  already/miss settlements split")
p.write_text(s, encoding="utf-8")
print("  age_up4 min_pop ->", "15" if '"age_up4_min_pop": 15' in s else "?")

# governors market + lab + obs + resolve
p = Path("sim/core/build_governors.py")
s = p.read_text(encoding="utf-8")
s = s.replace(
    'int(ss.get("era", 2)) >= 4 and "inquiry" in (ss.get("subjects") or [])',
    'int(ss.get("era", 2)) >= 3 and "inquiry" in (ss.get("subjects") or [])',
)
s = s.replace(
    'if int(s.get("era", 2)) >= 4 and "inquiry" in (s.get("subjects") or []):',
    'if int(s.get("era", 2)) >= 3 and "inquiry" in (s.get("subjects") or []):',
)

old_m = '''def can_build_market(agent_x, agent_y, sm, world) -> Tuple[bool, str]:
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
    return True, ""'''
new_m = '''def can_build_market(agent_x, agent_y, sm, world) -> Tuple[bool, str]:
    if sm.count() == 0:
        return False, "market_needs_settlement"
    any_barracks = any(sm.count_structures_of_type(sid, "barracks", world) >= 1 for sid in sm.settlements)
    any_market = any(sm.count_structures_of_type(sid, "market", world) >= 1 for sid in sm.settlements)
    any_era3 = any(int(s.get("era", 2)) >= 3 for s in sm.settlements.values())
    if not any_barracks:
        return False, "market_needs_barracks"
    if not any_era3:
        return False, "market_needs_era3"
    if any_market:
        return False, "market_already_exists"
    return True, ""'''
if old_m in s:
    s = s.replace(old_m, new_m)
    print("  OK can_build_market")
else:
    print("  already/miss can_build_market")

old_l = '''def can_build_lab(agent_x, agent_y, sm, world) -> Tuple[bool, str]:
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
    return True, ""'''
new_l = '''def can_build_lab(agent_x, agent_y, sm, world) -> Tuple[bool, str]:
    if sm.count() == 0:
        return False, "lab_needs_settlement"
    any_library = any(sm.count_structures_of_type(sid, "library", world) >= 1 for sid in sm.settlements)
    any_lab = any(sm.count_structures_of_type(sid, "lab", world) >= 1 for sid in sm.settlements)
    any_inquiry = any("inquiry" in (s.get("subjects") or []) for s in sm.settlements.values())
    if not any_inquiry:
        return False, "lab_needs_inquiry"
    if not any_library:
        return False, "lab_needs_library"
    if any_lab:
        return False, "lab_already_exists"
    return True, ""'''
if old_l in s:
    s = s.replace(old_l, new_l)
    print("  OK can_build_lab")
else:
    print("  already/miss can_build_lab")

old_o = '''def can_build_observatory(agent_x, agent_y, sm, world) -> Tuple[bool, str]:
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
    return True, ""'''
new_o = '''def can_build_observatory(agent_x, agent_y, sm, world) -> Tuple[bool, str]:
    if sm.count() == 0:
        return False, "observatory_needs_settlement"
    any_lab = any(sm.count_structures_of_type(sid, "lab", world) >= 1 for sid in sm.settlements)
    any_obs = any(sm.count_structures_of_type(sid, "observatory", world) >= 1 for sid in sm.settlements)
    if not any_lab:
        return False, "observatory_needs_lab"
    if any_obs:
        return False, "observatory_already_exists"
    return True, ""'''
if old_o in s:
    s = s.replace(old_o, new_o)
    print("  OK can_build_observatory")
else:
    print("  already/miss can_build_observatory")

old_r = '''    if b == "lab":
        if lab >= 1:
            return "hut", "lab_capped_to_hut"
        if era < 4:
            return "hut", "lab_needs_era4"
        if "inquiry" not in subjects:
            return "hut", "lab_needs_inquiry"
        if library < 1:
            return "library", "lab_needs_library"

    if b == "observatory":
        if observatory >= 1:
            return "hut", "observatory_capped_to_hut"
        if era < 4:
            return "hut", "observatory_needs_era4"
        if lab < 1:
            return "lab", "observatory_needs_lab"'''
new_r = '''    if b == "lab":
        any_lab = any(sm.count_structures_of_type(sid, "lab", world) >= 1 for sid in sm.settlements)
        any_library = any(sm.count_structures_of_type(sid, "library", world) >= 1 for sid in sm.settlements)
        any_inquiry_subj = any("inquiry" in (ss.get("subjects") or []) for ss in sm.settlements.values())
        if any_lab:
            return "hut", "lab_capped_to_hut"
        if not any_inquiry_subj:
            return "hut", "lab_needs_inquiry"
        if not any_library:
            return "library", "lab_needs_library"

    if b == "observatory":
        any_obs = any(sm.count_structures_of_type(sid, "observatory", world) >= 1 for sid in sm.settlements)
        any_lab = any(sm.count_structures_of_type(sid, "lab", world) >= 1 for sid in sm.settlements)
        if any_obs:
            return "hut", "observatory_capped_to_hut"
        if not any_lab:
            return "lab", "observatory_needs_lab"'''
if old_r in s:
    s = s.replace(old_r, new_r)
    print("  OK resolve lab/obs")
else:
    print("  already/miss resolve")

s = s.replace(
'''    if b == "market":
        if market >= 1:
            return "hut", "market_capped_to_hut"
        if barracks < 1:
            return "barracks", "market_needs_barracks"''',
'''    if b == "market":
        any_market = any(sm.count_structures_of_type(sid, "market", world) >= 1 for sid in sm.settlements)
        any_barracks = any(sm.count_structures_of_type(sid, "barracks", world) >= 1 for sid in sm.settlements)
        if any_market:
            return "hut", "market_capped_to_hut"
        if not any_barracks:
            return "barracks", "market_needs_barracks"'''
)
p.write_text(s, encoding="utf-8")
print("Done.")
print("python tools/multi_seed_validate.py --seeds 7 42 100 999 2026 --ticks 4000 --quiet")
