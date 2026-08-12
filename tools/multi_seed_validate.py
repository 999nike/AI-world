#!/usr/bin/env python3
"""Multi-seed validation helper for AI-world Era 1.

Runs several seeds, collects key metrics from summary.json,
and prints a clear comparison table.

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
    p = argparse.ArgumentParser(description="AI-world multi-seed validation")
    p.add_argument("--seeds", type=int, nargs="+", default=DEFAULT_SEEDS,
                   help="Seeds to run (default: 42 1 7 100 999 2026)")
    p.add_argument("--ticks", type=int, default=500,
                   help="Ticks per run (default: 500)")
    p.add_argument("--snapshot-every", type=int, default=50,
                   help="Snapshot interval (default: 50)")
    args = p.parse_args()

    results = []

    print()
    print("=" * 72)
    print(f"  AI-WORLD MULTI-SEED VALIDATION  |  ticks={args.ticks}")
    print("=" * 72)
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
        results.append({
            "seed": seed,
            "run_id": run_id,
            "score": summary.get("score"),
            "settlements": m.get("settlements_created", 0),
            "huts": m.get("build_hut", 0),
            "storage": m.get("build_storage", 0),
            "farms": m.get("build_farm", 0),
            "food_dep": m.get("food_deposited_total", 0),
            "grew": m.get("population_grew_events", 0),
            "starved": m.get("population_starved_events", 0),
            "net_pop": m.get("population_net_change", 0),
        })
        print(f"  done → score={summary.get('score')}  rid={run_id}")
        print()

    # ---- Summary table ----
    print()
    print("=" * 72)
    print("  RESULTS")
    print("=" * 72)
    print(f"{'Seed':>6}  {'Score':>6}  {'NetPop':>6}  {'Starved':>7}  "
          f"{'Huts':>5}  {'Stor':>4}  {'Farm':>4}  {'FoodDep':>7}  Run ID")
    print("-" * 72)

    for r in results:
        print(f"{r['seed']:>6}  {r['score']:>6}  {r['net_pop']:>6}  {r['starved']:>7}  "
              f"{r['huts']:>5}  {r['storage']:>4}  {r['farms']:>4}  {r['food_dep']:>7}  {r['run_id']}")

    print("-" * 72)
    print()

    # Quick reference check for seed 42
    ref = next((r for r in results if r["seed"] == 42), None)
    if ref:
        print(f"Reference check (seed 42): score={ref['score']}  "
              f"(locked baseline was ~241 @ 300 ticks)")
        print()

    print("Done. Use tools/view_run.py --rid <run_id> --log economy to inspect any run.")
    print()


if __name__ == "__main__":
    main()
