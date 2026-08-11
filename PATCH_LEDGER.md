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
| P0.2   | Remove dead code at end of `simloop.py`    | **Done**   | Unreachable code removed |
| P0.3   | Add minimal smoke-test helper              | Pending    | Optional but useful |

### Phase 1 – Structural Cleanup (Highest Leverage)

| ID     | Patch                                      | Status     | Goal |
|--------|--------------------------------------------|------------|------|
| P1.1   | Extract SettlementManager out of simloop   | **Done**   | `sim/world/settlements.py` created. Creation, linkage, deposits, farm harvest, population dynamics moved out. |
| P1.2   | Deduplicate nearest-settlement logic       | Pending    | Mostly done via SettlementManager.nearest(); remaining governors can be cleaned next |
| P1.3   | Clean & centralise build governors         | Pending    | Farm bootstrap, storage cap, hut food gate still live in simloop |
| P1.4   | Align `WorldState` / `Settlement` class    | Pending    | Stop having two competing settlement representations |
| P1.5   | Slim `simloop.py` to orchestration only    | Pending    | Significant progress made; further slimming after governors are cleaned |

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

**Completed today:**
- P0.1 Ledger created
- P0.2 Dead code removed
- **P1.1 SettlementManager extracted**
  - New file: `sim/world/settlements.py`
  - Owns: create, link, nearest, deposit, farm harvest, population dynamics
  - `simloop.py` now uses `sm = SettlementManager(...)` instead of nested functions + local dicts
  - Behaviour intentionally kept identical

**Next recommended:** P1.3 (clean build governors) or P1.2 residual cleanup, then P1.5 further slim.

**Risk note:** The build governors are still duplicated/complex inside the build branch of simloop. That is the next natural target.
