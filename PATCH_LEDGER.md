# AI-world Patch Ledger

**Hand-off:** 2026-08-17 E5.11

## Snapshot

```
E5.11 LIVE:
  - age_up: workshop+barracks may be split across settlements
  - hard-gates: market→temple→academy, library→lab→observatory (food-pressure aware)
  - can_build/resolve: global for barracks/market/temple/academy/library/lab/obs
  - simloop: lib/temple/academy/lab/obs may overwrite road or hut
  - barracks utility boosted after workshop

Validated 4000 ticks:
  seeds 7,42,100,999,2026 → all era4 + lib + lab + obs + 5 subjects

Test:
  git pull
  python tools/multi_seed_validate.py --seeds 7 42 100 999 2026 --ticks 5000 --quiet
```
