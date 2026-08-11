# AI-world Patch Ledger

**Status:** Active  
**Created:** 2026-08-12  
**Last updated:** 2026-08-12  
**Owner:** 999nike + Grok (SuperGrok session)

This file is the single source of truth for the current cleanup & stabilisation work.
Every patch should be small, reviewable, and leave the sim still runnable.

---

## Guiding Rules

1. Determinism is sacred. Never break seed reproducibility.
2. One major axis of change at a time.
3. Logs > visuals > polish.
4. Prefer extraction + cleanup over new features until the core is clean.
5. Every patch must keep `python -m sim run --seed 42 --ticks 100` working.

---

## Current Priority Queue

### Phase 0 – Safety & Visibility

| ID     | Patch                                      | Status     | Notes |
|--------|--------------------------------------------|------------|-------|
| P0.1   | Create this PATCH_LEDGER.md                | **Done**   | This file |
| P0.2   | Remove dead code at end of `simloop.py`    | **Done**   | |
| P0.3   | Add minimal smoke-test helper              | Pending    | Optional |

### Phase 1 – Structural Cleanup

| ID     | Patch                                      | Status     | Notes |
|--------|--------------------------------------------|------------|-------|
| P1.1   | Extract SettlementManager                  | **Done**   | `sim/world/settlements.py` |
| P1.2   | Deduplicate nearest-settlement logic       | **Done**   | Handled by SettlementManager.nearest() |
| P1.3   | Clean & centralise build governors         | **Done**   | New `sim/core/build_governors.py` with `resolve_building` + `can_build_hut` |
| P1.4   | Align `WorldState` / `Settlement` class    | Pending    | |
| P1.5   | Slim `simloop.py` further                  | Pending    | Already much cleaner; residual food/haul guards still inline |

### Phase 2 – Agent Observation & Decision Quality

| ID     | Patch                                      | Status     | Goal |
|--------|--------------------------------------------|------------|------|
| P2.1   | Enrich `Observation` with settlement data  | Pending    | Give UtilityAgent real food/pop signals |
| P2.2   | Reduce hard overrides in simloop           | Pending    | Move more intelligence into the agent |
| P2.3   | Soft roles / bias hints                    | Pending    | After observation is richer |

### Phase 3 – Balance & Stability

| ID     | Patch                                      | Status     | Goal |
|--------|--------------------------------------------|------------|------|
| P3.1   | Re-tune SETTLEMENT_RULES + farm yield      | Pending    | |
| P3.2   | Better build gating                        | Pending    | |
| P3.3   | Multi-seed long-run validation             | Pending    | |

### Phase 4 – Later

- Minimal CLI / ASCII replay viewer
- Inter-settlement courier / proto-trade
- Agent memory / lessons
- God-view

---

## Completed this session

- P0.1 Ledger
- P0.2 Dead code removal
- P1.1 SettlementManager extraction
- P1.2 Nearest-settlement dedup (via manager)
- **P1.3 Build governors centralised**
  - New file: `sim/core/build_governors.py`
  - `resolve_building()` – farm bootstrap + storage cap
  - `can_build_hut()` – storage + food stability gates
  - simloop build branch is now short and readable

**Next natural targets:** P1.5 (further slim) or P2.1 (richer Observation).
