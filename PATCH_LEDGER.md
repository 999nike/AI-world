# AI-world Patch Ledger

**Hand-off:** 2026-08-17

## Snapshot

```
E5.9 LIVE:
  - utility_agent: Library hard-gate (empty tile = build; occupied = pure move)
  - road utility = -8 once inquiry unlocked
  - simloop: occupied tiles fail BEFORE resource spend (no silent drain)
  - full simloop restored from c98573c + E5.9 occupied patch

E5.5–E5.8: prior Library gates + STACKABLE cascade
E6: raid + military live

Test:
  git pull
  python tools/multi_seed_validate.py --seeds 7 42 100 --ticks 3000 --quiet
```
