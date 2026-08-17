# AI-world Patch Ledger

**Status:** Long-run durability pass + Era4/E5 utility tuning  
**Last updated:** 2026-08-17

---

## Snapshot

```
Era 1–3 complete
E4.0–E4.5 LOCKED (buildings live)
E5.0 Lab LOCKED
E5.1 Observatory LIVE

Long-run tools:
  quiet logging (auto on ticks>=2000)
  soldier soft-cap + always-on upkeep
  food durability retune
  science path utility (Lib→Lab→Obs)
  specialisation utility (Foundry/Hall/Command)

God-view icons: C # ~ L Y O X R V

Repo: https://github.com/999nike/AI-world
```

---

## Building pattern (Era 4 + E5)

| Building | Gate | Cost | Effect | Icon |
|----------|------|------|--------|------|
| Irrigation | agriculture | 2w 2s | +farm yield | ~ |
| Library | inquiry | 3w 3s | +0.2 knowledge | L |
| Foundry | craft | 3w 3s | +0.15 tools | Y |
| Hall | organisation | 3w 3s | +food + surplus help | O |
| Command | strategy + barracks | 3w 4s | +soldiers (food upkeep) | X |
| Lab | inquiry + library | 4w 4s | +0.40 knowledge | R |
| Observatory | lab | 5w 4s | +0.50 knowledge | V |

---

## Long-run notes (2026-08-17)

- 5k-tick batches viable with `--quiet`
- Soldiers no longer explode unbounded
- Science line much more consistent after utility pass
- Next depth: post-Observatory goals / richer mid-late trade-offs

Determinism sacred. One axis at a time. Choices must be able to hurt.
