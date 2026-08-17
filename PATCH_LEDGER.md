# AI-world Patch Ledger

**Hand-off:** 2026-08-17 late

## Snapshot

```
E5.9c LIVE on main:
  utility_agent: hard-gate scans ALL settlements for inquiry+era4
  build_governors: any_inquiry global; road+hut redirect to Library
  simloop: library can overwrite road tiles; occupied fails before spend

Confirmed: seed 7 builds Library (lib=1) at 1000–1500 ticks.
Seed 42 full path still OK.
Seed 100 still pre-academy (separate).

Test:
  git pull
  python tools/multi_seed_validate.py --seeds 7 42 100 --ticks 3000 --quiet
```
