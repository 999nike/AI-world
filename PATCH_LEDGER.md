# AI-world Patch Ledger

**Status:** Era 2 stages 0–4 live on main  
**Last updated:** 2026-08-12

---

## Snapshot (for next session)

- Era 1 LOCKED (32/32 stress pass)
- Era 2 LIVE: Granary ✓ Mine ✓ Roads ✓ Workshop ✓ Barracks ✓
- All code + DESIGN on `main`
- Seed 42 @400 ticks: barracks 1, workshop 1, soldiers ~58, score 1059
- Hard food-force guard removed (P2.2)
- Next: combat/raid light, or god-view polish

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
| 3 | Workshop | E2.3 | **Live** | Cost 4w2s; gate mine+(granary|road) max1; tools +0.4/tick; farm/mine bonus; gather +1 |
| 4 | Barracks | E2.4 | **Live** | Cost 3w3s; gate workshop max1; soldiers +0.25/tick |

### Validation notes
- Post E2.3 stress: 14/14 PASS
- Post E2.4 seed 42 @400: barracks built, soldiers ~58, score 1059

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
| P2.2 | Removed hard food-force override |
| E2.4 | Barracks (light military foundation) |

---

## Next session

1. Combat / raid light mechanics (use soldiers)
2. God-view improvements
3. Optional: raise stress thresholds for Era 2 richness

Determinism still sacred. No learnable agents until world stays stable.
