#!/usr/bin/env python3
"""God-view for AI-world (Era 4) — logs → visual playback.

Usage:
  python tools/god_view.py --rid latest --play
  python tools/god_view.py --rid latest --play --delay 0.5
  python tools/god_view.py --rid latest --step
  python tools/god_view.py --rid latest --final
"""

from __future__ import annotations

import argparse
import json
import os
import time
from collections import Counter
from pathlib import Path


ICON = {
    "agent": "A", "hut": "H", "storage": "S", "farm": "F", "granary": "G",
    "mine": "M", "road": "=", "workshop": "W", "barracks": "B",
    "market": "K", "temple": "T", "academy": "C", "walls": "#",
    "irrigation": "~", "library": "L", "foundry": "Y",
    "settlement": "@", "empty": ".",
}

KEY_EVENT_TYPES = {
    "age_transition", "subject_unlocked", "raid", "soldier_defend",
    "settlement_created",
}


def find_latest_run(runs_dir: Path) -> str | None:
    if not runs_dir.exists():
        return None
    dirs = [d for d in runs_dir.iterdir() if d.is_dir()]
    if not dirs:
        return None
    dirs.sort(key=lambda d: d.stat().st_mtime, reverse=True)
    return dirs[0].name


def load_snapshots(run_dir: Path) -> list[dict]:
    path = run_dir / "snapshots.jsonl"
    if not path.exists():
        print(f"No snapshots.jsonl in {run_dir}")
        return []
    snaps = []
    with path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                snaps.append(json.loads(line))
    return snaps


def load_summary(run_dir: Path) -> dict | None:
    path = run_dir / "summary.json"
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def load_key_events(run_dir: Path) -> list[dict]:
    path = run_dir / "events.jsonl"
    if not path.exists():
        return []
    out = []
    with path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                ev = json.loads(line)
            except json.JSONDecodeError:
                continue
            t = ev.get("type", "")
            if t in KEY_EVENT_TYPES:
                out.append(ev)
            elif t == "action_resolved" and str(ev.get("note", "")).startswith("built_"):
                b = str(ev.get("note", "")).replace("built_", "")
                if b in ("academy", "walls", "irrigation", "library", "foundry",
                         "temple", "barracks", "workshop"):
                    out.append(ev)
    return out


def events_in_range(events: list[dict], t0: int, t1: int) -> list[str]:
    lines = []
    defend_counts: Counter = Counter()
    for ev in events:
        tick = ev.get("tick")
        if tick is None or not (t0 < tick <= t1):
            continue
        typ = ev.get("type", "")
        if typ == "age_transition":
            lines.append(f"  ★ AGE {ev.get('from_era')} → {ev.get('to_era')}  ({ev.get('settlement_id')})")
        elif typ == "subject_unlocked":
            lines.append(f"  ★ SUBJECT  {ev.get('subject')}  ({ev.get('settlement_id')})")
        elif typ == "action_resolved":
            lines.append(f"  ★ BUILT  {str(ev.get('note','')).replace('built_','')}  @({ev.get('pos',{}).get('x')},{ev.get('pos',{}).get('y')})")
        elif typ == "raid":
            lines.append(f"  ★ RAID  {ev.get('attacker')} → {ev.get('target')}")
        elif typ == "settlement_created":
            lines.append(f"  ★ SETTLEMENT  {ev.get('settlement',{}).get('id','?')}")
        elif typ == "soldier_defend":
            defend_counts[ev.get("settlement_id", "?")] += 1
    for sid, n in defend_counts.items():
        lines.append(f"  ★ DEFEND  {sid} x{n}")
    return lines


def build_grid(snap: dict) -> list[list[str]]:
    width = snap.get("width", 32)
    height = snap.get("height", 32)
    grid = [[ICON["empty"] for _ in range(width)] for _ in range(height)]
    for st in snap.get("structures", []):
        x, y = int(st.get("x", 0)), int(st.get("y", 0))
        if 0 <= x < width and 0 <= y < height:
            grid[y][x] = ICON.get(st.get("type", ""), "?")
    for s in snap.get("settlements", []):
        x, y = int(s.get("x", 0)), int(s.get("y", 0))
        if 0 <= x < width and 0 <= y < height:
            if grid[y][x] in (ICON["empty"], ICON["road"]):
                grid[y][x] = ICON["settlement"]
    for a in snap.get("agents", []):
        x, y = int(a.get("x", 0)), int(a.get("y", 0))
        if 0 <= x < width and 0 <= y < height:
            grid[y][x] = ICON["agent"]
    return grid


def settlement_summary(snap: dict) -> str:
    parts = []
    for s in snap.get("settlements", []):
        subjects = ",".join(s.get("subjects") or []) or "-"
        parts.append(
            f"{s.get('id','?')}:e{s.get('era',2)} pop={s.get('population','?')} "
            f"f={round(float(s.get('food_stock',0)),1)} k={round(float(s.get('knowledge',0)),1)} [{subjects}]"
        )
    return " | ".join(parts) if parts else "no settlements"


def structure_counts(snap: dict) -> str:
    c = Counter(st.get("type") for st in snap.get("structures", []))
    order = ["farm", "storage", "hut", "granary", "mine", "road",
             "workshop", "barracks", "market", "temple", "academy", "walls",
             "irrigation", "library", "foundry"]
    bits = [f"{t}:{c[t]}" for t in order if c.get(t)]
    return "  ".join(bits) if bits else "none"


def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")


def print_grid(grid, tick, summary=None, snap=None, callouts=None):
    height = len(grid)
    width = len(grid[0]) if height else 0
    print("=" * max(width + 4, 72))
    print(f"  GOD VIEW  |  tick {tick}")
    if summary:
        m = summary.get("metrics", {})
        print(
            f"  Score:{summary.get('score')}  NetPop:{m.get('population_net_change',0)}  "
            f"AgeUp:{m.get('age_up_events',0)}  A4:{m.get('age_up4_events',0)}  "
            f"Subjects:{m.get('subject_unlock_events',0)}"
        )
        print(
            f"  Builds  C:{m.get('build_academy',0)} #:{m.get('build_walls',0)} "
            f"~:{m.get('build_irrigation',0)} L:{m.get('build_library',0)} "
            f"Y:{m.get('build_foundry',0)}"
        )
    if snap:
        print(f"  Structs  {structure_counts(snap)}")
        print(f"  {settlement_summary(snap)}")
    if callouts:
        print("-" * max(width + 4, 72))
        for line in callouts:
            print(line)
    print("=" * max(width + 4, 72))
    print("  " + "".join(str(x % 10) for x in range(width)))
    for y, row in enumerate(grid):
        print(f"{y % 10} " + "".join(row))
    print()
    print("  A=agent F=farm S=storage W=workshop B=barracks C=academy")
    print("  #=walls ~=irrigation L=library Y=foundry")
    print()


def main():
    p = argparse.ArgumentParser(description="AI-world god-view (Era 4)")
    p.add_argument("--rid", default="latest")
    p.add_argument("--tick", type=int, default=None)
    p.add_argument("--list", action="store_true")
    p.add_argument("--step", action="store_true")
    p.add_argument("--play", action="store_true")
    p.add_argument("--delay", type=float, default=0.45)
    p.add_argument("--final", action="store_true")
    p.add_argument("--runs", default="runs")
    args = p.parse_args()

    runs_dir = Path(args.runs)
    rid = args.rid
    if rid == "latest":
        rid = find_latest_run(runs_dir)
        if not rid:
            print("No runs found.")
            return
        print(f"Using latest run: {rid}")

    run_dir = runs_dir / rid
    if not run_dir.exists():
        print(f"Run folder not found: {run_dir}")
        return

    summary = load_summary(run_dir)

    if args.final:
        if not summary:
            print("No summary.json")
            return
        m = summary.get("metrics", {})
        print()
        print("=" * 72)
        print(f"  FINAL  |  {rid}")
        print(f"  Score: {summary.get('score')}  Seed: {summary.get('seed')}  Ticks: {summary.get('ticks')}")
        print(f"  AgeUp:{m.get('age_up_events',0)}  A4:{m.get('age_up4_events',0)}  "
              f"Subjects:{m.get('subject_unlock_events',0)}  "
              f"Irrig:{m.get('build_irrigation',0)} Lib:{m.get('build_library',0)} "
              f"Foundry:{m.get('build_foundry',0)}")
        for s in summary.get("final", {}).get("settlements", []):
            subjects = ",".join(s.get("subjects") or []) or "-"
            print(f"  {s.get('id')}: era={s.get('era',2)} pop={s.get('population')} "
                  f"k={round(float(s.get('knowledge',0)),1)} [{subjects}]")
        print("=" * 72)
        return

    snaps = load_snapshots(run_dir)
    if not snaps:
        return
    by_tick = {s["tick"]: s for s in snaps if s.get("tick") is not None}
    ticks = sorted(by_tick.keys())
    key_events = load_key_events(run_dir)

    if args.list:
        print(f"Available snapshot ticks ({len(ticks)}):")
        print("  " + ", ".join(str(t) for t in ticks))
        return

    if args.play:
        prev = -1
        for i, t in enumerate(ticks):
            clear_screen()
            callouts = events_in_range(key_events, prev, t)
            print_grid(build_grid(by_tick[t]), t, summary, by_tick[t], callouts)
            print(f"  PLAY  [{i+1}/{len(ticks)}]  tick {t}  (Ctrl+C stop)")
            prev = t
            if i < len(ticks) - 1:
                time.sleep(max(0.05, args.delay))
        return

    if args.step:
        idx = 0
        while True:
            t = ticks[idx]
            prev = ticks[idx - 1] if idx > 0 else -1
            callouts = events_in_range(key_events, prev, t)
            clear_screen()
            print_grid(build_grid(by_tick[t]), t, summary, by_tick[t], callouts)
            print(f"[{idx+1}/{len(ticks)}]  tick {t}")
            cmd = input("  [n]ext  [p]rev  [q]uit  or tick > ").strip().lower()
            if cmd in ("q", "quit", "exit"):
                break
            elif cmd in ("n", "", "next"):
                idx = min(idx + 1, len(ticks) - 1)
            elif cmd in ("p", "prev"):
                idx = max(idx - 1, 0)
            else:
                try:
                    target = int(cmd)
                    closest = min(ticks, key=lambda x: abs(x - target))
                    idx = ticks.index(closest)
                except ValueError:
                    print("  unknown")
        return

    if args.tick is not None:
        t = args.tick if args.tick in by_tick else min(ticks, key=lambda x: abs(x - args.tick))
        if t != args.tick:
            print(f"Tick {args.tick} not found. Nearest: {t}")
        print_grid(build_grid(by_tick[t]), t, summary, by_tick[t])
    else:
        t = ticks[-1]
        print_grid(build_grid(by_tick[t]), t, summary, by_tick[t])


if __name__ == "__main__":
    main()
