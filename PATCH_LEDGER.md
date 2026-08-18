# AI-world Patch Ledger

**Hand-off:** 2026-08-18 watchable city

## Snapshot

```
LIVE on e5-lib-global:
  E5.13 science path global (lib → lab → obs)
  Playable edicts: food / science / army
  Layer 3: rival civ + win/lose clock
  Watchable city: glyphs, days of food, chronicle sentences
  Validate path unchanged (rival_agents=0, playable off)

Pass bar (no --playable, no --rival):
  seeds 42,100,7,999,2026 @ 5000 → era4 + lib + lab + obs + 5 subjects
  expected scores: 42=1205, 100=1600, 7=2207, 999=1267, 2026=1933
```

```bash
git fetch && git checkout e5-lib-global
python tools/multi_seed_validate.py --seeds 42 100 7 999 2026 --ticks 5000 --quiet
python tools/play_web.py --host 0.0.0.0 --port 8080
```

## Watchable contract

- Presentation only. No kernel, edict, gate, or RNG change.
- Map glyphs match god-view letters. Food shown as days (pop * 0.22).
- Chronicle diffs settlements / science buildings / raids into sentences.
- Do not start another axis until this is green.
