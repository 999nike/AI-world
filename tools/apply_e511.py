#!/usr/bin/env python3
"""Apply E5.11. From repo root: python tools/apply_e511.py"""
from pathlib import Path

print("E5.11 applying...")

# --- settlements split age_up ---
sp = Path("sim/world/settlements.py")
ss = sp.read_text(encoding="utf-8")
if "has_ws and any_barracks" not in ss:
    a = "military = self.settlement_has_workshop(sid, world) and self.settlement_has_barracks(sid, world)"
    b = (
        "any_workshop = any(self.settlement_has_workshop(sid, world) for sid in self.settlements)\n"
        "            any_barracks = any(self.settlement_has_barracks(sid, world) for sid in self.settlements)\n"
        "            has_ws = self.settlement_has_workshop(sid, world)\n"
        "            has_br = self.settlement_has_barracks(sid, world)\n"
        "            military = (has_ws and has_br) or (has_ws and any_barracks) or (has_br and any_workshop)"
    )
    if a in ss:
        ss = ss.replace(a, b)
        sp.write_text(ss, encoding="utf-8")
        print("  OK settlements split age_up")
    else:
        c = "if not (self.settlement_has_workshop(sid, world) and self.settlement_has_barracks(sid, world)):\n                continue"
        d = (
            "any_workshop = any(self.settlement_has_workshop(sid, world) for sid in self.settlements)\n"
            "            any_barracks = any(self.settlement_has_barracks(sid, world) for sid in self.settlements)\n"
            "            has_ws = self.settlement_has_workshop(sid, world)\n"
            "            has_br = self.settlement_has_barracks(sid, world)\n"
            "            military = (has_ws and has_br) or (has_ws and any_barracks) or (has_br and any_workshop)\n"
            "            science = self.settlement_has_academy(sid, world)\n"
            "            if not (military or science):\n"
            "                continue"
        )
        if c in ss:
            ss = ss.replace(c, d)
            sp.write_text(ss, encoding="utf-8")
            print("  OK settlements split age_up (legacy)")
        else:
            print("  MISS settlements")
else:
    print("  already settlements")

# --- utility lab/obs gates ---
up = Path("sim/agents/utility_agent.py")
us = up.read_text(encoding="utf-8")
if "has_library and not has_lab" not in us:
    old = (
        '        if has_market and not has_temple:\n'
        '            return Action(type="build", building="temple")\n'
        '        if has_temple and not has_academy:\n'
        '            return Action(type="build", building="academy")\n\n'
        '        eps'
    )
    new = (
        '        has_library = "library" in types\n'
        '        has_lab = "lab" in types\n'
        '        has_obs = "observatory" in types\n'
        '        pressure = self._settlement_pressure(obs)\n'
        '        if pressure < 0.8:\n'
        '            if has_market and not has_temple:\n'
        '                return Action(type="build", building="temple")\n'
        '            if has_temple and not has_academy:\n'
        '                return Action(type="build", building="academy")\n'
        '            if has_library and not has_lab:\n'
        '                return Action(type="build", building="lab")\n'
        '            if has_lab and not has_obs:\n'
        '                return Action(type="build", building="observatory")\n\n'
        '        eps'
    )
    if old in us:
        us = us.replace(old, new)
        print("  OK utility lab/obs gates")
    else:
        print("  MISS utility gates")
    oldb = 'return w["w_build_barracks"] * can + 1.8 + inv_term - hunger * 0.2'
    newb = 'return w["w_build_barracks"] * can + 8.0 + inv_term - hunger * 0.15  # E5.11'
    if oldb in us:
        us = us.replace(oldb, newb, 1)
        print("  OK barracks boost")
    up.write_text(us, encoding="utf-8")
else:
    print("  already utility")

# --- simloop ---
lp = Path("sim/core/simloop.py")
ls = lp.read_text(encoding="utf-8")
if 'lab", "observatory"' not in ls:
    ls = ls.replace(
        'b == "library" and existing.type == "road"',
        'b in ("library", "temple", "academy", "lab", "observatory") and existing.type in ("road", "hut")',
    )
    ls = ls.replace(
        'b in ("library", "temple", "academy") and existing.type == "road"',
        'b in ("library", "temple", "academy", "lab", "observatory") and existing.type in ("road", "hut")',
    )
    ls = ls.replace('existing.type = "library"', "existing.type = b")
    ls = ls.replace('note = "built_library"', 'note = f"built_{b}"')
    ls = ls.replace(
        'metrics["build_library"] = metrics.get("build_library", 0) + 1',
        'metrics[f"build_{b}"] = metrics.get(f"build_{b}", 0) + 1',
    )
    ls = ls.replace('"building": "library"', '"building": b')
    lp.write_text(ls, encoding="utf-8")
    print("  OK simloop")
else:
    print("  already simloop")

# --- governors ---
gp = Path("sim/core/build_governors.py")
gs = gp.read_text(encoding="utf-8")
if "any_inquiry_subj" not in gs:
    old = (
        '    if b == "lab":\n'
        '        if lab >= 1:\n'
        '            return "hut", "lab_capped_to_hut"\n'
        '        if era < 4:\n'
        '            return "hut", "lab_needs_era4"\n'
        '        if "inquiry" not in subjects:\n'
        '            return "hut", "lab_needs_inquiry"\n'
        '        if library < 1:\n'
        '            return "library", "lab_needs_library"\n\n'
        '    if b == "observatory":\n'
        '        if observatory >= 1:\n'
        '            return "hut", "observatory_capped_to_hut"\n'
        '        if era < 4:\n'
        '            return "hut", "observatory_needs_era4"\n'
        '        if lab < 1:\n'
        '            return "lab", "observatory_needs_lab"'
    )
    new = (
        '    if b == "lab":\n'
        '        any_lab = any(sm.count_structures_of_type(sid, "lab", world) >= 1 for sid in sm.settlements)\n'
        '        any_library = any(sm.count_structures_of_type(sid, "library", world) >= 1 for sid in sm.settlements)\n'
        '        any_inquiry_subj = any("inquiry" in (ss.get("subjects") or []) for ss in sm.settlements.values())\n'
        '        if any_lab:\n'
        '            return "hut", "lab_capped_to_hut"\n'
        '        if not any_inquiry_subj:\n'
        '            return "hut", "lab_needs_inquiry"\n'
        '        if not any_library:\n'
        '            return "library", "lab_needs_library"\n\n'
        '    if b == "observatory":\n'
        '        any_obs = any(sm.count_structures_of_type(sid, "observatory", world) >= 1 for sid in sm.settlements)\n'
        '        any_lab = any(sm.count_structures_of_type(sid, "lab", world) >= 1 for sid in sm.settlements)\n'
        '        if any_obs:\n'
        '            return "hut", "observatory_capped_to_hut"\n'
        '        if not any_lab:\n'
        '            return "lab", "observatory_needs_lab"'
    )
    if old in gs:
        gs = gs.replace(old, new)
        gp.write_text(gs, encoding="utf-8")
        print("  OK governors")
    else:
        print("  MISS governors")
else:
    print("  already governors")

print("Done. Test:")
print("  python tools/multi_seed_validate.py --seeds 7 42 100 999 2026 --ticks 4000 --quiet")
