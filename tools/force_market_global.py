#!/usr/bin/env python3
from pathlib import Path

def replace_func(src, name, new_body):
    needle = f"def {name}"
    i = src.find(needle)
    if i < 0:
        return src, f"MISS {name}"
    j = i + len(needle)
    while True:
        k = src.find("\ndef ", j)
        if k < 0:
            k = len(src)
            break
        if src[k+1:k+5] == "def ":
            break
        j = k + 1
    block = src[i:k]
    if "any_barracks = any" in block and name == "can_build_market":
        return src, f"already {name}"
    if "any_library = any" in block and name == "can_build_lab":
        return src, f"already {name}"
    if name == "can_build_observatory" and "any_lab = any" in block and "any_obs" in block:
        return src, f"already {name}"
    return src[:i] + new_body.rstrip() + "\n\n" + src[k:].lstrip("\n"), f"OK {name}"

p = Path("sim/core/build_governors.py")
s = p.read_text(encoding="utf-8")

market = '''def can_build_market(agent_x, agent_y, sm, world) -> Tuple[bool, str]:
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
    return True, ""
'''

lab = '''def can_build_lab(agent_x, agent_y, sm, world) -> Tuple[bool, str]:
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
    return True, ""
'''

obs = '''def can_build_observatory(agent_x, agent_y, sm, world) -> Tuple[bool, str]:
    if sm.count() == 0:
        return False, "observatory_needs_settlement"
    any_lab = any(sm.count_structures_of_type(sid, "lab", world) >= 1 for sid in sm.settlements)
    any_obs = any(sm.count_structures_of_type(sid, "observatory", world) >= 1 for sid in sm.settlements)
    if not any_lab:
        return False, "observatory_needs_lab"
    if any_obs:
        return False, "observatory_already_exists"
    return True, ""
'''

for name, body in [
    ("can_build_market", market),
    ("can_build_lab", lab),
    ("can_build_observatory", obs),
]:
    s, msg = replace_func(s, name, body)
    print(msg)

p.write_text(s, encoding="utf-8")
print("done")
