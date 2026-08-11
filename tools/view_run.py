#!/usr/bin/env python3
"""AI-world run viewer – filtered log for testing without the boredom.

Usage:
  python tools/view_run.py --rid latest
  python tools/view_run.py --rid 20260811_232726_9zalvx --log economy
  python tools/view_run.py --rid latest --log all
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def find_latest_run(runs_dir: Path) -> str | None:
    if not runs_dir.exists():
        return None
    dirs = [d for d in runs_dir.iterdir() if d.is_dir()]
    if not dirs:
        return None
    dirs.sort(key=lambda d: d.stat().st_mtime, reverse=True)
    return dirs[0].name


def load_events(run_dir: Path):
    path = run_dir / "events.jsonl"
    if not path.exists():
        print(f"No events.jsonl in {run_dir}")
        return []
    events = []
    with path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                events.append(json.loads(line))
    return events


def load_summary(run_dir: Path):
    path = run_dir / "summary.json"
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def print_header(rid: str, summary):
    print()
    print("=" * 60)
    print(f"  AI-WORLD RUN VIEWER  |  {rid}")
    print("=" * 60)
    if summary:
        m = summary.get("metrics", {})
        print(f"  Score          : {summary.get('score')}")
        print(f"  Settlements    : {m.get('settlements_created', 0)}")
        print(f"  Huts / Storage / Farms : {m.get('build_hut', 0)} / {m.get('build_storage', 0)} / {m.get('build_farm', 0)}")
        print(f"  Food deposited : {m.get('food_deposited_total', 0)}")
        print(f"  Pop grew       : {m.get('population_grew_events', 0)}")
        print(f"  Pop starved    : {m.get('population_starved_events', 0)}")
        print(f"  Net pop change : {m.get('population_net_change', 0)}")
    print("=" * 60)
    print()


def show_economy(events):
    print("=== ECONOMY / BUILD / POPULATION ===\n")
    for e in events:
        t = e.get("tick")
        typ = e.get("type")

        if typ == "settlement_created":
            s = e.get("settlement", {})
            print(f"[t{t:4}] SETTLEMENT + {s.get('id')} at ({s.get('x')},{s.get('y')}) pop={s.get('population')}")

        elif typ == "build_funded":
            print(f"[t{t:4}] BUILD     {e.get('building')}  (settlement {e.get('settlement_id')})")

        elif typ == "action_resolved" and str(e.get("note", "")).startswith("built_"):
            print(f"[t{t:4}] BUILT     {e.get('note')}  agent={e.get('agent_id')}")

        elif typ in ("food_deposited", "wood_deposited", "stone_deposited"):
            res = typ.replace("_deposited", "")
            print(f"[t{t:4}] DEPOSIT   {res} +{e.get('amount')}  -> {e.get('settlement_id')}  (stock now {e.get(res + '_stock', '?')})")

        elif typ == "population_changed":
            before = e.get("population_before")
            after = e.get("population_after")
            arrow = "↑" if after > before else "↓" if after < before else "="
            print(f"[t{t:4}] POP {arrow}     {before} -> {after}  food {e.get('food_before')} -> {e.get('food_after')}  ({e.get('settlement_id')})")

    print("\n=== END ===\n")


def show_all(events):
    print("=== ALL EVENTS (truncated) ===\n")
    for e in events:
        t = e.get("tick")
        typ = e.get("type")
        if typ in ("tick_started", "action_attempted", "snapshot_saved"):
            continue
        print(f"[t{t:4}] {typ:22} { {k: v for k, v in e.items() if k not in ('type', 'tick')} }")
    print("\n=== END ===\n")


def main():
    p = argparse.ArgumentParser(description="AI-world run log viewer")
    p.add_argument("--rid", default="latest", help="Run ID or 'latest'")
    p.add_argument("--log", default="economy", choices=["economy", "all"], help="Filter scope")
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
    events = load_events(run_dir)

    print_header(rid, summary)

    if args.log == "economy":
        show_economy(events)
    else:
        show_all(events)


if __name__ == "__main__":
    main()
