# AI-world Patch Ledger

**Hand-off:** 2026-08-17

## Snapshot

```
E5.6: hard-gate in UtilityAgent.act()
  if era>=4 and inquiry unlocked and no Library:
    → force build library (if affordable) or gather missing wood/stone
E5.5 governor redirect still active
E6 raid + military utility live

This should finally close seed-100 science path.
```

```bash
git pull
python tools/multi_seed_validate.py --seeds 42 100 7 999 2026 --ticks 5000 --snapshot-every 250 --quiet
```
