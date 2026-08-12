#!/usr/bin/env python3
"""Minimal god-view for AI-world.

Reads snapshots.jsonl from a finished run and shows a simple ASCII grid
of the world at any tick. Pure inspection tool — does not touch the sim.

Usage:
  python tools/god_view.py --rid latest
  python tools/god_view.py --rid 20260812_123456_abcdef --tick 120
  python tools/god_view.py --rid latest --list          # list available snapshot ticks
  python tools/god_view.py --rid latest --step          # interactive step through
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

    # Settlements first (under everything)
    for s in snap.get("settlements", []):
        x, y = int(s.get("x", 0)), int(s.get("y", 0))
        if 0 <= x < width and 0 <= y < height:
            grid[y][x] = ICON["settlement"]

    # Structures
    for st in snap.get("structures", []):
        x, y = int(st.get("x", 0)), int(st.get("y", 0))
        typ = st.get("type", "")
        if 0 <= x < width and 0 <= y < height:
            if typ == "hut":
                grid[y][x] = ICON["hut"]
            elif typ == "storage":
                grid[y][x] = ICON["storage"]
            elif typ == "farm":
                grid[y][x] = ICON["farm"]

    # Agents on top
    for a in snap.get("agents", []):
        x, y = int(a.get("x", 0)), int(a.get("y", 0))
        if 0 <= x < width and 0 <= y < height:
            grid[y][x] = ICON["agent"]

    return grid


def print_grid(grid: list[list[str]], tick: int, summary: dict | None = None):
    height = len(grid)
    width = len(grid[0]) if height else 0

    print()
    print("=" * (width + 4))
    print(f"  GOD VIEW  |  tick {tick}")
    if summary:
        m = summary.get("metrics", {})
        print(f"  Score: {summary.get('score')}  |  "
              f"Huts:{m.get('build_hut', 0)}  Stor:{m.get('build_storage', 0)}  "
              f"Farms:{m.get('build_farm', 0)}  "
              f"NetPop:{m.get('population_net_change', 0)}")
    print("=" * (width + 4))

    # Column numbers (every 5)
    header = "  "
    for x in range(width):
        header += str(x % 10)
    print(header)

    for y, row in enumerate(grid):
        line = f"{y % 10} " + "".join(row)
        print(line)

    print()
    print("  Legend:  A=agent  H=hut  S=storage  F=farm  @=settlement  .=empty")
    print()


def main():
    p = argparse.ArgumentParser(description="AI-world minimal god-view")
    p.add_argument("--rid", default="latest", help="Run ID or 'latest'")
    p.add_argument("--tick", type=int, default=None, help="Show specific tick")
    p.add_argument("--list", action="store_true", help="List available snapshot ticks")
    p.add_argument("--step", action="store_true", help="Interactive step through snapshots")
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

    snaps = load_snapshots(run_dir)
    if not snaps:
        return

    summary = load_summary(run_dir)

    # Build tick → snap map
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
            print_grid(build_grid(by_tick[t]), t, summary)
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
                    # find closest
                    closest = min(ticks, key=lambda x: abs(x - target))
                    idx = ticks.index(closest)
                except ValueError:
                    print("  unknown command")
        return

    # Single tick mode
    if args.tick is not None:
        if args.tick in by_tick:
            print_grid(build_grid(by_tick[args.tick]), args.tick, summary)
        else:
            # nearest
            closest = min(ticks, key=lambda x: abs(x - args.tick))
            print(f"Tick {args.tick} not found. Showing nearest: {closest}")
            print_grid(build_grid(by_tick[closest]), closest, summary)
    else:
        # default: last snapshot
        last = ticks[-1]
        print_grid(build_grid(by_tick[last]), last, summary)


if __name__ == "__main__":
    main()
