# AI-world Patch Ledger

**Status:** Active  
**Created:** 2026-08-12  
**Last updated:** 2026-08-12  
**Owner:** 999nike + Grok

---

## Guiding Rules

1. Determinism is sacred.
2. One major axis of change at a time.
3. Logs > visuals > polish.
4. Prefer extraction + cleanup over new features until core is clean.
5. Keep `python -m sim run --seed 42 --ticks 100` working.

---

## Completed this session

| ID   | Patch                                      | Status |
|------|--------------------------------------------|--------|
| P0.1 | Create PATCH_LEDGER.md                     | Done   |
| P0.2 | Remove dead code in simloop                | Done   |
| P1.1 | Extract SettlementManager                  | Done   |
| P1.2 | Deduplicate nearest-settlement             | Done   |
| P1.3 | Centralise build governors                 | Done   |
| P2.1 | Enrich Observation + UtilityAgent          | **Done** |

### P2.1 details
- `Observation` now carries `settlements` and `nearest_settlement`
- UtilityAgent uses settlement food/pop pressure:
  - Strongly prefers gathering food when hungry
  - Heavily penalises building (especially huts) when settlement is under pressure
  - Added farm as a first-class candidate with its own weight
- Hard guards in simloop remain as a safety net for now

---

## Remaining queue

| ID   | Patch                                      | Status  |
|------|--------------------------------------------|---------|
| P1.4 | Align WorldState / Settlement class        | Pending |
| P1.5 | Further slim simloop (move food/haul guards)| Pending |
| P2.2 | Reduce / remove hard overrides             | Pending |
| P2.3 | Soft roles                                 | Pending |
| P3.x | Balance tuning + multi-seed validation     | Pending |

---

**Suggested next step:** Run a few seeds (e.g. 42, 7, 99 × 300–500 ticks) and inspect scores + starvation events. Then decide whether to tune balance (P3) or continue structural cleanup.
