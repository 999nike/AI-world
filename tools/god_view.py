#!/usr/bin/env python3
"""God-view for AI-world (Era 2 aware).

Reads snapshots.jsonl from a finished run and shows an ASCII grid
plus settlement / combat summary. Pure inspection — does not touch the sim.

Usage:
  python tools/god_view.py --rid latest
  python tools/god_view.py --rid 20260812_123456_abcdef --tick 120
  python tools/god_view.py --rid latest --list
  python tools/god_view.py --rid latest --step
  python tools/god_view.py --rid latest --final
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


ICON = {
    "agent": "A",
    "hut": "H",
    "storage": "S",
    "farm": "F",
    "granary": "G",
    "mine": "M",
    "road": "=",
    "workshop": "W",
    "barracks": "B",
    "market": "K",
    "temple": "T",
    "settlement": "@",
    "empty": ".",
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


def build_grid(snap: dict) -> list[list[str]]:
    width = snap.get("width", 32)
    height = snap.get("height", 32)
    grid = [[ICON["empty"] for _ in range(width)] for _ in range(height)]

    # Structures first (so agents can overwrite)
    for st in snap.get("structures", []):
        x, y = int(st.get("x", 0)), int(st.get("y", 0))
        typ = st.get("type", "")
        if 0 <= x < width and 0 <= y < height:
            grid[y][x] = ICON.get(typ, "?")

    for s in snap.get("settlements", []):
        x, y = int(s.get("x", 0)), int(s.get("y", 0))
        if 0 <= x < width and 0 <= y < height:
            # Only mark if tile still empty / not a key building
            if grid[y][x] in (ICON["empty"], ICON["road"]):
                grid[y][x] = ICON["settlement"]

    for a in snap.get("agents", []):
        x, y = int(a.get("x", 0)), int(a.get("y", 0))
        if 0 <= x < width and 0 <= y < height:
            grid[y][x] = ICON["agent"]

    return grid


def settlement_summary(snap: dict) -> str:
    settlements = snap.get("settlements", [])
    if not settlements:
        return "no settlements"
    parts = []
    for s in settlements:
        sid = s.get("id", "?")
        pop = s.get("population", "?")
        food = round(float(s.get("food_stock", 0)), 1)
        wood = s.get("wood_stock", 0)
        stone = s.get("stone_stock", 0)
        tools = round(float(s.get("tools_stock", 0)), 1)
        soldiers = round(float(s.get("soldiers", 0)), 1)
        parts.append(
            f"{sid}:pop={pop} food={food} w={wood} s={stone} tools={tools} sol={soldiers}"
        )
    return " | ".join(parts)


def structure_counts(snap: dict) -> str:
    from collections import Counter
    c = Counter(st.get("type") for st in snap.get("structures", []))
    order = ["farm", "storage", "hut", "granary", "mine", "road", "workshop", "barracks", "market", "temple"]
    bits = [f"{t}:{c[t]}" for t in order if c.get(t)]
    return "  ".join(bits) if bits else "none"


def print_grid(grid: list[list[str]], tick: int, summary: dict | None = None, snap: dict | None = None):
    height = len(grid)
    width = len(grid[0]) if height else 0

    print()
    print("=" * max(width + 4, 60))
    print(f"  GOD VIEW  |  tick {tick}")
    if summary:
        m = summary.get("metrics", {})
        print(
            f"  Score:{summary.get('score')}  "
            f"NetPop:{m.get('population_net_change', 0)}  "
            f"Defend:{m.get('soldier_defend_events', 0)}  "
            f"Raids:{m.get('raid_events', 0)}  "
            f"Loot:{m.get('raid_loot_total', 0)}"
        )
        print(
            f"  Builds  H:{m.get('build_hut', 0)} S:{m.get('build_storage', 0)} "
            f"F:{m.get('build_farm', 0)} G:{m.get('build_granary', 0)} "
            f"M:{m.get('build_mine', 0)} R:{m.get('build_road', 0)} "
            f"W:{m.get('build_workshop', 0)} B:{m.get('build_barracks', 0)}"
        )
    if snap:
        print(f"  Structs  {structure_counts(snap)}")
        print(f"  {settlement_summary(snap)}")
    print("=" * max(width + 4, 60))

    header = "  "
    for x in range(width):
        header += str(x % 10)
    print(header)

    for y, row in enumerate(grid):
        line = f"{y % 10} " + "".join(row)
        print(line)

    print()
    print("  Legend: A=agent  H=hut  S=storage  F=farm  G=granary  M=mine")
    print("          =road  W=workshop  B=barracks  K=market  T=temple  @=settlement  .=empty")
    print()


def main():
    p = argparse.ArgumentParser(description="AI-world god-view (Era 2)")
    p.add_argument("--rid", default="latest", help="Run ID or 'latest'")
    p.add_argument("--tick", type=int, default=None, help="Show specific tick")
    p.add_argument("--list", action="store_true", help="List available snapshot ticks")
    p.add_argument("--step", action="store_true", help="Interactive step through snapshots")
    p.add_argument("--final", action="store_true", help="Show final summary.json state (no grid)")
    p.add_argument("--runs", default="runs", help="Runs directory")
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
        print()
        print("=" * 60)
        print(f"  FINAL  |  {rid}")
        print(f"  Score: {summary.get('score')}  Seed: {summary.get('seed')}  Ticks: {summary.get('ticks')}")
        m = summary.get("metrics", {})
        print(f"  Defend:{m.get('soldier_defend_events', 0)}  Raids:{m.get('raid_events', 0)}  "
              f"Loot:{m.get('raid_loot_total', 0)}  Tools:{round(m.get('workshop_tools_total', 0),1)}  "
              f"Soldiers:{round(m.get('barracks_soldiers_total', 0),1)}")
        print(f"  Builds  H:{m.get('build_hut',0)} S:{m.get('build_storage',0)} F:{m.get('build_farm',0)} "
              f"G:{m.get('build_granary',0)} M:{m.get('build_mine',0)} R:{m.get('build_road',0)} "
              f"W:{m.get('build_workshop',0)} B:{m.get('build_barracks',0)}")
        final = summary.get("final", {})
        for s in final.get("settlements", []):
            print(f"  {s.get('id')}: pop={s.get('population')} food={round(float(s.get('food_stock',0)),1)} "
                  f"w={s.get('wood_stock')} s={s.get('stone_stock')} "
                  f"tools={round(float(s.get('tools_stock',0)),1)} sol={round(float(s.get('soldiers',0)),1)}")
        print("=" * 60)
        return

    snaps = load_snapshots(run_dir)
    if not snaps:
        return

    by_tick = {}
    for s in snaps:
        t = s.get("tick")
        if t is not None:
            by_tick[t] = s

    ticks = sorted(by_tick.keys())

    if args.list:
        print(f"Available snapshot ticks ({len(ticks)}):")
        print("  " + ", ".join(str(t) for t in ticks))
        return

    if args.step:
        idx = 0
        while True:
            t = ticks[idx]
            print_grid(build_grid(by_tick[t]), t, summary, by_tick[t])
            print(f"[{idx+1}/{len(ticks)}]  tick {t}")
            cmd = input("  [n]ext  [p]rev  [q]uit  or tick number > ").strip().lower()
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
                    print("  unknown command")
        return

    if args.tick is not None:
        if args.tick in by_tick:
            print_grid(build_grid(by_tick[args.tick]), args.tick, summary, by_tick[args.tick])
        else:
            closest = min(ticks, key=lambda x: abs(x - args.tick))
            print(f"Tick {args.tick} not found. Showing nearest: {closest}")
            print_grid(build_grid(by_tick[closest]), closest, summary, by_tick[closest])
    else:
        last = ticks[-1]
        print_grid(build_grid(by_tick[last]), last, summary, by_tick[last])


if __name__ == "__main__":
    main()
