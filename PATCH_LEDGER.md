# AI-world Patch Ledger

**Status:** Era 2 stages 0–4 + defense + raids live  
**Last updated:** 2026-08-12

---

## Snapshot (for next session)

- Era 1 LOCKED (32/32 stress pass)
- Era 2 LIVE: Granary ✓ Mine ✓ Roads ✓ Workshop ✓ Barracks ✓
- E2.5 Defense: soldiers absorb starve loss (cost 1.0)
- E2.6 Raids: every 25 ticks, strongest settlement (soldiers≥3) raids weakest; cost 2 soldiers, steals up to 3w/2s/2f
- Seed 42 @500: raid_events 4, loot 14, defend 54, score 1169
- Code for E2.6 in artifacts/AI-world-E2.6/ if push lag; settlements+simloop need final push
- Next: god-view polish, or raise stress thresholds

---

## Era 2 stages

| Stage | System | Patch | Status | Notes |
|-------|--------|-------|--------|-------|
| 0–4 | Buildings | E2.0–E2.4 | **Live** | Granary→Barracks |
| — | Defense | E2.5 | **Live** | soldiers absorb starve |
| — | Raids | E2.6 | **Live** | multi-settlement loot raids |

---

## Next session

1. God-view improvements
2. Optional: raise stress thresholds
3. Further combat polish if needed

Determinism still sacred. No learnable agents until world stays stable.
