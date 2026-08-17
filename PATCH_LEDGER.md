# AI-world Patch Ledger

**Hand-off snapshot:** 2026-08-17  
**Status:** Long-run durability + E5 science + discoveries LIVE

---

## Snapshot

```
Repo: https://github.com/999nike/AI-world
Branch: main

Era 1–3: complete
E4.0–E4.5: LOCKED (buildings live)
E5.0 Lab: LOCKED
E5.1 Observatory: LIVE
E5.2 Discoveries: LIVE (knowledge sink after Observatory)

Long-run tooling:
  quiet logging (auto when ticks >= 2000)
  soldier soft-cap + always-on food upkeep
  food durability retune
  science-path utility (Lib → Lab → Obs)
  specialisation utility (Foundry / Hall / Command)

God-view icons: C # ~ L Y O X R V
```

---

## Building table (Era 4 + E5)

| Building | Gate | Cost | Effect | Icon |
|----------|------|------|--------|------|
| Irrigation | agriculture | 2w 2s | +farm yield | ~ |
| Library | inquiry | 3w 3s | +0.2 knowledge/tick | L |
| Foundry | craft | 3w 3s | +0.15 tools/tick | Y |
| Hall | organisation | 3w 3s | +food + surplus help | O |
| Command | strategy + barracks | 3w 4s | +soldiers (food upkeep) | X |
| Lab | inquiry + library | 4w 4s | +0.40 knowledge/tick | R |
| Observatory | lab | 5w 4s | +0.50 knowledge/tick | V |

**Discoveries (E5.2):** needs Observatory; spend 40 knowledge → +1 discovery; +0.08 farm/farm each; max 8.

**Military long-run:** barracks 0.15 / command 0.10 soldiers per tick; soft-cap ~3× pop; upkeep 0.03 food/soldier always.

---

## Validation (5 seeds × 5000 ticks, quiet)

Typical recent batch:

- 4/5 seeds reach full Lib+Lab+Obs + Foundry/Hall/Command
- Seed 7 often strongest (score ~3000, low starve)
- Seed 100 sometimes Era 4 + subjects but skips building line (utility variance)
- Soldiers no longer unbounded (was 400–1100; now controlled)

```bash
git pull
python tools/multi_seed_validate.py --seeds 42 100 7 999 2026 --ticks 5000 --snapshot-every 250 --quiet
python tools/god_view.py --rid latest --play
```

---

## System status

| System | Status |
|--------|--------|
| Era 1–3 | Live |
| E4 stack | Locked / live |
| E5.0 Lab | Locked |
| E5.1 Observatory | Live |
| E5.2 Discoveries | Live |
| Quiet long-run mode | Live |
| God-view --play | Live |
| Learning agents | Not started (utility baseline only) |

---

## Suggested next axes (not committed)

1. Raid / military depth for long horizons  
2. Stronger Library push when inquiry unlocks (seed 100 class misses)  
3. Human-paced god-view / presentation  
4. Learning-agent interface later  

---

Determinism sacred. One axis at a time. Choices must be able to hurt.  
Ledger = status. DESIGN = vision.
