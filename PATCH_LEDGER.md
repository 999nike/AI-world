# AI-world Patch Ledger

**Status:** Era 2 stages 0–3 live + validated  
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

### Validation (post E2.3)

**Multi-seed (5 seeds × 400 ticks)**  
42: 1138 · 7: 424 · 99: 683 · 1: 64 · 100: 594  
Workshop appeared + produced tools/boosts on 4/5 seeds.

**Stress (14 seeds × 350 ticks)**  
**14/14 PASS (100%)** under existing Era 1 thresholds.  
Score min/avg/max: 64 / 445 / 1181  
Reference seed 42: 1181

### Seed 42 reference (longer runs)
- ~300–500 ticks: Workshop builds, tools fire, score 800–1180 range

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

1. Light military / barracks (or age-transition gates)
2. Soften remaining hard food-haul guards in simloop if still present
3. Minimal god-view improvements
4. Optional: raise stress thresholds slightly for Era 2 richness

Determinism still sacred. No learnable agents until world stays stable.
