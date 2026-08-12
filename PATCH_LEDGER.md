# AI-world Patch Ledger

**Status:** Era 2 in progress (stages 0–2 live)  
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
| 3 | Workshop | — | **Next** | Tools / production boost |

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

---

## Next session

1. Stage 3: **Workshop** (wood+stone → tools, boost gather/build)
2. Optional: re-run stress test under Era 2 buildings
3. Later: military light / age transition gates

Determinism still sacred. No learnable agents until world stays stable.
