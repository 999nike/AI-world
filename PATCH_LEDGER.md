# AI-world Patch Ledger

**Hand-off:** 2026-08-17

## Snapshot

```
E5.9: Library hard-gate always attempts build; pure move off occupied tiles
      Road utility crushed once inquiry unlocked (-8)
      Occupied-tile builds fail BEFORE resource spend (no silent drain)
E5.5–E5.8: prior Library gates + STACKABLE cascade remain
E6: raid + military live

Goal: seed 7 / 100 / 999 finally reach Library after inquiry.
```

```bash
git pull
python tools/multi_seed_validate.py --seeds 42 100 7 999 2026 --ticks 5000 --snapshot-every 250 --quiet
```
