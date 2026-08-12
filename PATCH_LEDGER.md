# AI-world Patch Ledger

**Status:** Era 2 in progress (stages 0–3 live)  
**Last updated:** 2026-08-12

---

## Era 1 validation (passed)

- Stress test: **32/32 PASS (100%)**
- Farm soft-cap fixed (P12.0)
- Bootstrap / seed-999 fixed (P13.0)
- Stress tool added (P14.0)

---

## Era 2 stages

| Stage | System | Patch | Status | Notes |
|-------|--------|-------|--------|-------|
| 0 | Granary | E2.0 | **Live** | +0.5 food/tick, softer starve; gate: storage+farm |
| 1 | Mine | E2.1 | **Live** | +0.75 stone/tick; gate: storage+farm |
| 2 | Roads | E2.2 | **Live** | Deposit range 2→3; gate: mine OR 4+ structures |
| 3 | Workshop | E2.3 | **Live** | Cost 4w2s; gate mine+(granary|road) max1; tools +0.4/tick; farm/mine bonus; gather +1 (tools consume) |

### Seed 42 @ 500 ticks (post E2.2)
- Score ~1012
- Roads 8, Mine 1, Granary 1, Farms 12, Storage 4, Huts 30
- Food deposited 82

---

## Session patches (summary)

| ID | What |
|----|------|
| P4–P11 | Tools, governor, scenario, drop-in, agents N, docs |
| P12 | Farm soft-cap fix |
| P13 | Bootstrap force-farm (seed 999) |
| P14 | stress_test.py |
| E2.0 | Granary |
| E2.1 | Mine |
| E2.2 | Roads |
| E2.3 | Workshop |

---

## Next session

1. Optional: re-run stress test under full Era 2 (incl. Workshop)
2. Later: military light / age transition gates
3. Validate multi-seed with Workshop present

Determinism still sacred. No learnable agents until world stays stable.
