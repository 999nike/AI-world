# AI-world Patch Ledger

**Hand-off:** 2026-08-18 Layer 3 rival civ

## Snapshot

```
LIVE on e5-lib-global:
  E5.13 science path global (lib → lab → obs)
  Playable edicts: food / science / army
  Layer 3: rival civ on the far side (own governor)
  Web god-view: You / Rival, clay cells, raid chronicle
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

## Layer 3 contract

- `rival_agents=0` (default): spawn + RNG identical to playable v2. Validate must match.
- `--rival` / web Begin: 4 player west (x 1–10) + 4 rival east (x width-11..width-2).
- Rival governor: seed even → army, odd → science. Edicts never touch rival brains.
- `sm.active_faction` scopes nearest / own / science gates / deposits.
- Two factions on the map → raids are cross-faction only. One faction → old strongest-vs-weakest.
- Do not start another axis until this is green.
