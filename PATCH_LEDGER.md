# AI-world Patch Ledger

**Hand-off:** 2026-08-17

## Snapshot

```
E5.9c LIVE (seed-7 Library fix):
  - Hard-gate scans ALL settlements for inquiry+era4 (not just nearest)
  - can_build_library / resolve_building same global inquiry check
  - Library may overwrite road tiles
  - road+hut redirected to Library once inquiry live
  - road utility -8 after inquiry

Seed 7 now builds Library. Seed 42 still full path.
Seed 100 still stuck pre-academy (separate issue).

Test:
  git pull
  python tools/multi_seed_validate.py --seeds 7 42 100 --ticks 3000 --quiet
```
