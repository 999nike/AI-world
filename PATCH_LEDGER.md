# AI-world Patch Ledger

**Status:** Active  
**Last updated:** 2026-08-12

---

## Completed this session

| ID   | Patch                                      | Status |
|------|--------------------------------------------|--------|
| P0.1 | Create PATCH_LEDGER.md                     | Done   |
| P0.2 | Remove dead code in simloop                | Done   |
| P1.1 | Extract SettlementManager                  | Done   |
| P1.2 | Deduplicate nearest-settlement             | Done   |
| P1.3 | Centralise build governors                 | Done   |
| P2.1 | Enrich Observation + UtilityAgent          | Done   |
| —    | Restore tools/view_run.py                  | Done   |
| **P3.0** | **Fix starvation logic (net deficit)** | **Done** |

### P3.0 – Starvation fix

**Bug:** Farm harvest was applied before the starve check, and `food_before` was overwritten with the post-harvest value. As long as farms existed, `food_before <= 0` was almost never true, so `starve_ticks` never accumulated and population never declined even under permanent food deficit.

**Fix:** Starvation now triggers on **true net shortfall** (`post_harvest_food < need`). Three consecutive deficit ticks → lose 1 population. Growth still requires sustained surplus after feeding.

---

## Remaining queue

| ID   | Patch                                      | Status  |
|------|--------------------------------------------|---------|
| P1.4 | Align WorldState / Settlement class        | Pending |
| P1.5 | Further slim simloop                       | Pending |
| P2.2 | Reduce hard overrides                      | Pending |
| P3.1 | Re-tune rules after starvation fix         | Pending |
| P3.2 | Soften hut gating (0 huts in last run)     | Pending |

---

**Next test:**
```
git pull
python -m sim run --seed 42 --ticks 300
python tools/view_run.py --rid latest --log economy
```
Expect: population should now decline once farms cannot cover consumption.
