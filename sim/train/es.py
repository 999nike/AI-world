# sim/train/es.py
from __future__ import annotations
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Tuple

from sim.core.simloop import run_sim

POLICY_PATH = Path("policies") / "best.json"

DEFAULT_POLICY: Dict[str, Any] = {
    "best_score": None,
    "weights": {},
    "meta": {"version": 1},
}

def load_best() -> Dict[str, Any]:
    if POLICY_PATH.exists():
        return json.loads(POLICY_PATH.read_text(encoding="utf-8"))
    return DEFAULT_POLICY.copy()

def save_best(policy: Dict[str, Any]) -> None:
    POLICY_PATH.parent.mkdir(parents=True, exist_ok=True)
    POLICY_PATH.write_text(json.dumps(policy, indent=2), encoding="utf-8")

def mutate(weights: Dict[str, float], rng, sigma: float = 0.35) -> Dict[str, float]:
    # multiplicative-ish mutation, stable for different weight scales
    out = dict(weights)
    for k, v in list(out.items()):
        if not isinstance(v, (int, float)):
            continue
        # small random walk
        dv = (rng.random() * 2.0 - 1.0) * sigma
        out[k] = float(v) + dv
    return out

def clamp(weights: Dict[str, float]) -> Dict[str, float]:
    # Keep epsilon sane and prevent crazy extremes
    w = dict(weights)
    w["epsilon"] = max(0.0, min(0.25, float(w.get("epsilon", 0.05))))
    return w

def train_es(gens: int, pop: int, ticks: int, seed: int, snapshot_every: int = 0) -> None:
    import random
    rng = random.Random(seed)

    best = load_best()
    best_score = best.get("best_score")
    best_weights = best.get("weights") or {}

    if best_score is None:
        best_score = -10**18

    print(f"[train] starting best_score={best_score}")

    for g in range(gens):
        candidates: List[Tuple[float, Dict[str, float], str]] = []

        # include incumbent
        score0, run_id0 = run_sim(seed=seed, ticks=ticks, snapshot_every=snapshot_every,
                                 agent_kind="utility", policy_weights=best_weights, return_score=True)
        candidates.append((score0, dict(best_weights), run_id0))

        # mutants
        for i in range(pop - 1):
            mw = clamp(mutate({k: float(v) for k, v in best_weights.items() if isinstance(v, (int, float))}, rng))
            s, rid = run_sim(seed=seed, ticks=ticks, snapshot_every=snapshot_every,
                             agent_kind="utility", policy_weights=mw, return_score=True)
            candidates.append((s, mw, rid))

        candidates.sort(key=lambda x: x[0], reverse=True)
        top_score, top_w, top_run = candidates[0]

        print(f"[gen {g+1}/{gens}] top_score={top_score} (run={top_run})")

        if top_score > best_score:
            best_score = top_score
            best_weights = top_w
            best = {
                "best_score": best_score,
                "weights": best_weights,
                "meta": {"version": 1, "seed": seed, "ticks": ticks, "gens": gens, "pop": pop},
            }
            save_best(best)
            print(f"[train] new best saved: score={best_score}")

    print("[train] done")
    print(f"[train] best_score={best_score}")
    print(f"[train] policy_path={POLICY_PATH}")