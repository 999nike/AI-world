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
| P0.2   | Remove dead code at end of `simloop.py`    | **Done**   | Unreachable `logger.event` after return removed |
| P0.3   | Add minimal smoke-test helper              | Pending    | Optional but useful |

### Phase 1 – Structural Cleanup (Highest Leverage)

| ID     | Patch                                      | Status     | Goal |
|--------|--------------------------------------------|------------|------|
| P1.1   | Extract SettlementManager out of simloop   | **Next**   | Move settlements, create/link, deposit, pop dynamics into `sim/world/settlements.py` |
| P1.2   | Deduplicate nearest-settlement logic       | Pending    | Single helper used everywhere |
| P1.3   | Clean & centralise build governors         | Pending    | Farm bootstrap, storage cap, hut food gate |
| P1.4   | Align `WorldState` / `Settlement` class    | Pending    | Stop having two competing settlement representations |
| P1.5   | Slim `simloop.py` to orchestration only    | Pending    | Target < 400–500 lines of clear control flow |

### Phase 2 – Agent Observation & Decision Quality

| ID     | Patch                                      | Status     | Goal |
|--------|--------------------------------------------|------------|------|
| P2.1   | Enrich `Observation` with settlement data  | Pending    | Give UtilityAgent real food/pop signals |
| P2.2   | Reduce hard overrides in simloop           | Pending    | Move more intelligence into the agent |
| P2.3   | Soft roles / bias hints (gatherer/builder) | Pending    | After observation is richer |

### Phase 3 – Balance & Stability

| ID     | Patch                                      | Status     | Goal |
|--------|--------------------------------------------|------------|------|
| P3.1   | Re-tune SETTLEMENT_RULES + farm yield      | Pending    | Stable multi-settlement runs without constant guards |
| P3.2   | Better build gating (food buffer aware)    | Pending    | Stop hut → starvation spirals |
| P3.3   | Multi-seed long-run validation suite       | Pending    | 5 seeds × 2000 ticks as a check |

### Phase 4 – Later (After Core is Clean)

- Minimal CLI / ASCII replay viewer
- Inter-settlement courier / proto-trade
- Proper agent memory / lessons
- God-view (far future)

---

## Patch Protocol

1. Grok proposes the exact change + files.
2. User approves (or requests changes).
3. Patch is applied via GitHub.
4. Status in this ledger is updated.
5. Brief note of what changed and any remaining risk.

---

## Active Notes (2026-08-12)

- Main risk is `sim/core/simloop.py` size and duplicated logic.
- Population still tends to collapse after early growth (known from DESIGN.md).
- UtilityAgent is still heavily overridden by hard guards — this is a smell.
- Memory Space was not shared at the time of this ledger creation, so we are using the repo itself as the ledger.

**Completed today:**
- P0.1 Ledger created
- P0.2 Dead code removed from end of `simloop.py`

**Next:** P1.1 – Extract SettlementManager
