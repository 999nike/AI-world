#!/usr/bin/env python3
"""Automated seed stress testing for AI-world Era 1.

Runs a batch of seeds, applies pass/fail rules, and reports
weak or failing seeds clearly.

Usage:
  python tools/stress_test.py
  python tools/stress_test.py --seeds 50 --ticks 500
  python tools/stress_test.py --start 0 --count 30 --ticks 400
  python tools/stress_test.py --seeds 20 --json results.json
"""

from __future__ import annotations

import argparse
import json
import statistics
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sim.core.simloop import run_sim


# Pass/fail thresholds (Era 1)
MAX_FARMS_PER_RUN = 12          # soft-cap is 3/settlement; allow some multi-settlement
MIN_NET_POP = 0                 # must not end negative
MIN_SCORE = 30                  # below this = collapse-ish
MIN_FARMS = 1                   # at least one farm should appear


def load_summary(run_id: str) -> dict | None:
    path = Path("runs") / run_id / "summary.json"
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def evaluate(row: dict) -> list[str]:
    """Return list of failure reasons (empty = pass)."""
    fails = []
    if row["net_pop"] < MIN_NET_POP:
        fails.append(f"net_pop={row['net_pop']} < {MIN_NET_POP}")
    if row["score"] < MIN_SCORE:
        fails.append(f"score={row['score']} < {MIN_SCORE}")
    if row["farms"] < MIN_FARMS:
        fails.append(f"farms={row['farms']} < {MIN_FARMS}")
    if row["farms"] > MAX_FARMS_PER_RUN:
        fails.append(f"farms={row['farms']} > soft limit {MAX_FARMS_PER_RUN}")
    return fails


def main():
    p = argparse.ArgumentParser(description="AI-world automated seed stress test")
    p.add_argument("--seeds", type=int, default=None,
                   help="Number of sequential seeds starting from --start")
    p.add_argument("--start", type=int, default=0,
                   help="First seed when using --seeds count (default 0)")
    p.add_argument("--count", type=int, default=20,
                   help="How many seeds to run if --seeds not set as list (default 20)")
    p.add_argument("--seed-list", type=int, nargs="+", default=None,
                   help="Explicit list of seeds (overrides --start/--count)")
    p.add_argument("--ticks", type=int, default=500,
                   help="Ticks per run (default 500)")
    p.add_argument("--snapshot-every", type=int, default=50)
    p.add_argument("--json", type=str, default=None,
                   help="Write full results to this JSON file")
    args = p.parse_args()

    if args.seed_list:
        seed_list = args.seed_list
    else:
        n = args.seeds if args.seeds is not None else args.count
        seed_list = list(range(args.start, args.start + n))

    # Always include known reference + previously weak seeds
    for extra in (42, 1, 999):
        if extra not in seed_list:
            seed_list.append(extra)

    results = []
    failures = []

    print()
    print("=" * 78)
    print(f"  AI-WORLD SEED STRESS TEST  |  ticks={args.ticks}  |  seeds={len(seed_list)}")
    print("=" * 78)
    print()

    for seed in seed_list:
        print(f"→ seed {seed} ...", end=" ", flush=True)
        try:
            score, run_id = run_sim(
                seed=seed,
                ticks=args.ticks,
                snapshot_every=args.snapshot_every,
                return_score=True,
            )
        except Exception as e:
            print(f"CRASH: {e}")
            row = {
                "seed": seed,
                "run_id": None,
                "score": 0,
                "net_pop": -999,
                "starved": 0,
                "huts": 0,
                "storage": 0,
                "farms": 0,
                "food_dep": 0,
                "settlements": 0,
                "fails": [f"exception: {e}"],
                "status": "FAIL",
            }
            results.append(row)
            failures.append(row)
            continue

        summary = load_summary(run_id)
        if summary is None:
            print("NO SUMMARY")
            row = {
                "seed": seed,
                "run_id": run_id,
                "score": 0,
                "net_pop": -999,
                "starved": 0,
                "huts": 0,
                "storage": 0,
                "farms": 0,
                "food_dep": 0,
                "settlements": 0,
                "fails": ["no summary.json"],
                "status": "FAIL",
            }
            results.append(row)
            failures.append(row)
            continue

        m = summary.get("metrics", {})
        row = {
            "seed": seed,
            "run_id": run_id,
            "score": summary.get("score", 0),
            "net_pop": m.get("population_net_change", 0),
            "starved": m.get("population_starved_events", 0),
            "huts": m.get("build_hut", 0),
            "storage": m.get("build_storage", 0),
            "farms": m.get("build_farm", 0),
            "food_dep": m.get("food_deposited_total", 0),
            "settlements": m.get("settlements_created", 0),
        }
        fails = evaluate(row)
        row["fails"] = fails
        row["status"] = "FAIL" if fails else "PASS"
        results.append(row)

        if fails:
            failures.append(row)
            print(f"FAIL  score={row['score']}  netpop={row['net_pop']}  farms={row['farms']}  ({', '.join(fails)})")
        else:
            print(f"PASS  score={row['score']}  netpop={row['net_pop']}  farms={row['farms']}  huts={row['huts']}")

    # ---- Table ----
    print()
    print("=" * 78)
    print("  RESULTS")
    print("=" * 78)
    print(f"{'Seed':>6}  {'Stat':<4}  {'Score':>6}  {'NetPop':>6}  {'Starved':>7}  "
          f"{'Huts':>5}  {'Stor':>4}  {'Farm':>4}  {'Food':>5}")
    print("-" * 78)
    for r in results:
        print(f"{r['seed']:>6}  {r['status']:<4}  {r['score']:>6}  {r['net_pop']:>6}  {r['starved']:>7}  "
              f"{r['huts']:>5}  {r['storage']:>4}  {r['farms']:>4}  {r['food_dep']:>5}")
    print("-" * 78)

    # ---- Stats ----
    scores = [r["score"] for r in results]
    netpops = [r["net_pop"] for r in results]
    farms = [r["farms"] for r in results]
    n = len(results)
    n_fail = len(failures)
    n_pass = n - n_fail

    print()
    print("=" * 78)
    print("  SUMMARY")
    print("=" * 78)
    print(f"  Runs          : {n}")
    print(f"  Passed        : {n_pass}")
    print(f"  Failed        : {n_fail}")
    if n:
        print(f"  Pass rate     : {100.0 * n_pass / n:.1f}%")
        print(f"  Score  min/avg/max : {min(scores)} / {statistics.mean(scores):.1f} / {max(scores)}")
        print(f"  NetPop min/avg/max : {min(netpops)} / {statistics.mean(netpops):.1f} / {max(netpops)}")
        print(f"  Farms  min/avg/max : {min(farms)} / {statistics.mean(farms):.1f} / {max(farms)}")
    print()

    if failures:
        print("  FAILED SEEDS:")
        for r in failures:
            print(f"    seed {r['seed']}: {', '.join(r['fails'])}")
        print()
    else:
        print("  All seeds passed.")
        print()

    # Reference
    ref = next((r for r in results if r["seed"] == 42), None)
    if ref:
        print(f"  Reference seed 42: score={ref['score']}  status={ref['status']}")
        print()

    if args.json:
        out = {
            "ticks": args.ticks,
            "thresholds": {
                "min_net_pop": MIN_NET_POP,
                "min_score": MIN_SCORE,
                "min_farms": MIN_FARMS,
                "max_farms": MAX_FARMS_PER_RUN,
            },
            "results": results,
            "pass_count": n_pass,
            "fail_count": n_fail,
        }
        Path(args.json).write_text(json.dumps(out, indent=2), encoding="utf-8")
        print(f"  Wrote {args.json}")
        print()

    # Exit code for CI-style use
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()
