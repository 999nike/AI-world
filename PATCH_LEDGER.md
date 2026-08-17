# AI-world Patch Ledger

**Hand-off snapshot:** 2026-08-17  
**Status:** E5.4 hard Library priority (seed-100 fix) + E6 military

---

## Snapshot

```
E5.3/E5.3b: inquiry 16 + Library weights
E5.4: hard priority (+12 / +6) for Library once inquiry unlocked
E6.0–E6.2: scaled raids + Command/Walls utility + god-view

Retest seed 100 especially.
```

---

## Validation

```bash
git pull
python tools/multi_seed_validate.py --seeds 42 100 7 999 2026 --ticks 5000 --snapshot-every 250 --quiet
```

Expect seed 100 to now show Lib=1 Lab=1 Obs=1.

---

Determinism sacred. Ledger = status. DESIGN = vision.
