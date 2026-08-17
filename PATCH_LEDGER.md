# AI-world Patch Ledger

**Hand-off snapshot:** 2026-08-17  
**Status:** E5 science + E5.3/E5.3b science-path consistency

---

## Snapshot

```
Repo: https://github.com/999nike/AI-world
Branch: main

Era 1–3 complete | E4 LOCKED | E5.0–E5.2 LIVE
E5.3: inquiry cost 20→16
E5.3b: library weight 4.0→4.8, bonus 4.0→5.5 (stronger seed-100 push)

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

**Discoveries:** Observatory → 40 knowledge → +1 discovery (+0.08 farm/farm), max 8.  
**Subjects:** inquiry cost = 16.

**Military:** barracks 0.15 / command 0.10 soldiers/tick; soft-cap ~3×pop; upkeep 0.03 food/soldier.

---

## Validation notes

Pre-E5.3b (after cost drop only): 4/5 seeds full science line; seed 100 still lib=0 lab=0 obs=0 despite full subjects + Era 4.

E5.3b applied — retest seed 100 class recommended before next axis.

```bash
git pull
python tools/multi_seed_validate.py --seeds 42 100 7 999 2026 --ticks 5000 --snapshot-every 250 --quiet
```

---

## System status

| System | Status |
|--------|--------|
| Era 1–4 | Live / Locked |
| E5 science + discoveries | Live |
| E5.3 / E5.3b Library push | Live |
| Quiet long-run | Live |
| God-view --play | Live |
| Learning agents | Not started |

---

## Suggested next axes

1. Raid / military depth for long horizons  
2. ~~Stronger Library push~~ → E5.3 + E5.3b  
3. Human-paced god-view / presentation  
4. Learning-agent interface later  

---

Determinism sacred. One axis at a time. Ledger = status. DESIGN = vision.
