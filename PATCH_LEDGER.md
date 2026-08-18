# AI-world Patch Ledger

**Hand-off:** 2026-08-18 playable v2

## Snapshot

```
LIVE on e5-lib-global:
  E5.13 science path global (lib → lab → obs)
  Playable edicts: food / science / army
  Web god-view: tools/play_web.py — click edicts, watch the map
  Validate path unchanged (playable off)

Pass bar (no --playable):
  seeds 42,100,7,999,2026 @ 5000 → era4 + lib + lab + obs + 5 subjects
```

```bash
git fetch && git checkout e5-lib-global
python tools/multi_seed_validate.py --seeds 42 100 7 999 2026 --ticks 5000 --quiet
python tools/play_web.py --host 0.0.0.0 --port 8080
```
