#!/usr/bin/env python3
"""Multi-seed validation helper for AI-world (Era 4 aware)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sim.core.simloop import run_sim

DEFAULT_SEEDS = [42, 1, 7, 100, 999, 2026]


def load_summary(run_id: str) -> dict | None:
    path = Path("runs") / run_id / "summary.json"
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def main():
    p = argparse.ArgumentParser(description="AI-world multi-seed validation (Era 4)")
    p.add_argument("--seeds", type=int, nargs="+", default=DEFAULT_SEEDS)
    p.add_argument("--ticks", type=int, default=500)
    p.add_argument("--snapshot-every", type=int, default=50)
    args = p.parse_args()

    results = []
    print()
    print("=" * 96)
    print(f"  AI-WORLD MULTI-SEED VALIDATION (Era 4)  |  ticks={args.ticks}")
    print("=" * 96)
    print()

    for seed in args.seeds:
        print(f"→ Running seed {seed} ...", flush=True)
        score, run_id = run_sim(seed=seed, ticks=args.ticks,
                                snapshot_every=args.snapshot_every, return_score=True)
        summary = load_summary(run_id)
        if summary is None:
            print(f"  ERROR: no summary for {run_id}")
            continue

        m = summary.get("metrics", {})
        settlements = summary.get("final", {}).get("settlements", [])
        eras = [int(s.get("era", 2)) for s in settlements]
        max_era = max(eras) if eras else 2
        total_knowledge = sum(float(s.get("knowledge", 0)) for s in settlements)
        all_subjects = set()
        for s in settlements:
            for sub in (s.get("subjects") or []):
                all_subjects.add(sub)

        results.append({
            "seed": seed, "run_id": run_id, "score": summary.get("score"),
            "net_pop": m.get("population_net_change", 0),
            "starved": m.get("population_starved_events", 0),
            "max_era": max_era,
            "age_ups": m.get("age_up_events", 0),
            "age_up4": m.get("age_up4_events", 0),
            "academy": m.get("build_academy", 0),
            "walls": m.get("build_walls", 0),
            "irrigation": m.get("build_irrigation", 0),
            "subjects": m.get("subject_unlock_events", 0),
            "knowledge": round(total_knowledge, 1),
            "subject_list": sorted(all_subjects),
        })
        print(f"  done → score={summary.get('score')} era={max_era} "
              f"acad={m.get('build_academy',0)} wall={m.get('build_walls',0)} "
              f"irrig={m.get('build_irrigation',0)} rid={run_id}")
        print()

    print()
    print("=" * 96)
    print("  RESULTS")
    print("=" * 96)
    print(f"{'Seed':>6}  {'Score':>6}  {'NetPop':>6}  {'Starve':>6}  "
          f"{'Era':>3}  {'A4':>3}  {'Acad':>4}  {'Wall':>4}  {'Irrig':>5}  "
          f"{'Subj':>4}  {'Know':>5}  Run ID")
    print("-" * 96)
    for r in results:
        print(f"{r['seed']:>6}  {r['score']:>6}  {r['net_pop']:>6}  {r['starved']:>6}  "
              f"{r['max_era']:>3}  {r['age_up4']:>3}  {r['academy']:>4}  {r['walls']:>4}  "
              f"{r['irrigation']:>5}  {r['subjects']:>4}  {r['knowledge']:>5}  {r['run_id']}")
    print("-" * 96)
    print()

    for r in results:
        if r["subject_list"]:
            print(f"  seed {r['seed']} subjects: {', '.join(r['subject_list'])}")
    print()
    print("Done.")
    print()


if __name__ == "__main__":
    main()
