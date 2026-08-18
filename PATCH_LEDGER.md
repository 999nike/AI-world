# AI-world Patch Ledger

**Hand-off:** 2026-08-18 win / lose clock

## Snapshot

```
LIVE on e5-lib-global:
  E5.13 science path global (lib → lab → obs)
  Playable edicts: food / science / army
  Layer 3: rival civ on the far side (own governor)
  Win / lose: science (obs + 2 disc) / wipe / clock
  Web: You win / They win + chronicle
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

## Clock contract

- Only when `rival_agents > 0`. Default 0 = no early stop, no outcome, validate identical.
- Science: own-faction Observatory + 2 discoveries. First one wins. Same tick + same count = draw.
- Domination: both factions have founded; one side's total pop hits 0.
- Survival: only if the clock expires. Win = era 4 AND more people. More people without era 4, or fewer people = they win. Tie + era 4 = draw.
- Edicts, gates, spawn, RNG unchanged.
- Do not start another axis until this is green.
