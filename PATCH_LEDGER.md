# AI-world Patch Ledger

**Hand-off:** 2026-08-18 E5.13 + playable v1

## Snapshot

```
LIVE on e5-lib-global:
  E5.12/13: science path is global (Library → Lab → Observatory)
  Playable v1: --playable pauses at opening / era4 / inquiry /
               first discovery / drought. Three edicts:
               focus food | focus build | focus expand.
               --choice-policy human|first|seeded
  Validate path unchanged (playable off).

Pass bar (no --playable):
  seeds 42,100,7,999,2026 @ 5000 → era4 + lib + lab + obs + 5 subjects
```

```bash
git fetch && git checkout e5-lib-global
python tools/multi_seed_validate.py --seeds 42 100 7 999 2026 --ticks 5000 --quiet
python -m sim run --playable --choice-policy seeded --seed 42 --ticks 2000
```
