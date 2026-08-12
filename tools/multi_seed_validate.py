#!/usr/bin/env python3
"""Multi-seed validation helper for AI-world (Era 3 aware).

Runs several seeds, collects key metrics from summary.json,
and prints a clear comparison table including Academy / Walls / subjects.

Usage:
  python tools/multi_seed_validate.py
  python tools/multi_seed_validate.py --ticks 500
  python tools/multi_seed_validate.py --seeds 42 1 7 100 999 2026 --ticks 500
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Allow running from repo root
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sim.core.simloop import run_sim


DEFAULT_SEEDS = [42, 1, 7, 100, 999, 2026]


def load_summary(run_id: str) -> dict | None:
    path = Path("runs") / run_id / "summary.json"
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def main():
    p = argparse.ArgumentParser(description="AI-world multi-seed validation (Era 3)")
    p.add_argument("--seeds", type=int, nargs="+", default=DEFAULT_SEEDS,
                   help="Seeds to run (default: 42 1 7 100 999 2026)")
    p.add_argument("--ticks", type=int, default=500,
                   help="Ticks per run (default: 500)")
    p.add_argument("--snapshot-every", type=int, default=50,
                   help="Snapshot interval (default: 50)")
    args = p.parse_args()

    results = []

    print()
    print("=" * 88)
    print(f"  AI-WORLD MULTI-SEED VALIDATION (Era 3)  |  ticks={args.ticks}")
    print("=" * 88)
    print()

    for seed in args.seeds:
        print(f"→ Running seed {seed} ...", flush=True)
        score, run_id = run_sim(
            seed=seed,
            ticks=args.ticks,
            snapshot_every=args.snapshot_every,
            return_score=True,
        )
        summary = load_summary(run_id)
        if summary is None:
            print(f"  ERROR: no summary for {run_id}")
            continue

        m = summary.get("metrics", {})
        final = summary.get("final", {})
        settlements = final.get("settlements", [])

        # Aggregate era / knowledge / subjects across settlements
        eras = [int(s.get("era", 2)) for s in settlements]
        max_era = max(eras) if eras else 2
        total_knowledge = sum(float(s.get("knowledge", 0)) for s in settlements)
        all_subjects = set()
        for s in settlements:
            for sub in (s.get("subjects") or []):
                all_subjects.add(sub)

        results.append({
            "seed": seed,
            "run_id": run_id,
            "score": summary.get("score"),
            "settlements": m.get("settlements_created", 0),
            "huts": m.get("build_hut", 0),
            "farms": m.get("build_farm", 0),
            "net_pop": m.get("population_net_change", 0),
            "starved": m.get("population_starved_events", 0),
            "age_ups": m.get("age_up_events", 0),
            "academy": m.get("build_academy", 0),
            "walls": m.get("build_walls", 0),
            "subjects": m.get("subject_unlock_events", 0),
            "knowledge": round(total_knowledge, 1),
            "max_era": max_era,
            "subject_list": sorted(all_subjects),
        })
        print(f"  done → score={summary.get('score')}  era={max_era}  "
              f"academy={m.get('build_academy',0)} walls={m.get('build_walls',0)}  rid={run_id}")
        print()

    # ---- Summary table ----
    print()
    print("=" * 88)
    print("  RESULTS")
    print("=" * 88)
    print(f"{'Seed':>6}  {'Score':>6}  {'NetPop':>6}  {'Starve':>6}  "
          f"{'Era':>3}  {'AgeUp':>5}  {'Acad':>4}  {'Wall':>4}  "
          f"{'Subj':>4}  {'Know':>5}  Run ID")
    print("-" * 88)

    for r in results:
        print(f"{r['seed']:>6}  {r['score']:>6}  {r['net_pop']:>6}  {r['starved']:>6}  "
              f"{r['max_era']:>3}  {r['age_ups']:>5}  {r['academy']:>4}  {r['walls']:>4}  "
              f"{r['subjects']:>4}  {r['knowledge']:>5}  {r['run_id']}")

    print("-" * 88)
    print()

    # Subject detail
    any_subjects = False
    for r in results:
        if r["subject_list"]:
            any_subjects = True
            print(f"  seed {r['seed']} subjects: {', '.join(r['subject_list'])}")
    if any_subjects:
        print()

    # Quick reference
    ref = next((r for r in results if r["seed"] == 42), None)
    if ref:
        print(f"Reference (seed 42 @ {args.ticks} ticks): score={ref['score']}  "
              f"era={ref['max_era']}  academy={ref['academy']}  walls={ref['walls']}")
        print()

    print("Done. Use tools/view_run.py --rid <run_id> --log economy")
    print("     or tools/god_view.py --rid <run_id> --final")
    print()


if __name__ == "__main__":
    main()
