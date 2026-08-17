# AI-world Patch Ledger

**Hand-off snapshot:** 2026-08-17  
**Status:** E5 science path + E6.0 raid depth

---

## Snapshot

```
Repo: https://github.com/999nike/AI-world
Branch: main

Era 1–4 LOCKED | E5 science + discoveries LIVE
E5.3 / E5.3b: inquiry cost 16 + Library weight 4.8 / bonus 5.5
E6.0: scaled raid loot (attacker strength) + strategy reduces loot taken

God-view icons: C # ~ L Y O X R V
```

---

## Key rules (current)

**Subjects:** inquiry cost = 16  
**Library utility:** weight 4.8, bonus 5.5  
**Raids (E6.0):**
- base loot raised (4w/3s/3f)
- extra loot = floor(attacker_soldiers / 8), capped
- defender with strategy subject: loot ×0.75
- walls still add +1 cost

**Military:** barracks 0.15 / command 0.10 /tick; soft-cap ~3×pop; upkeep 0.03 food/soldier

---

## Validation

Science path (E5.3b) still needs seed-100 confirmation.  
Raid depth is new — observe loot totals + strategy effect on long runs.

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
| E6.0 Raid depth | Live |
| Quiet long-run | Live |
| God-view --play | Live |
| Learning agents | Not started |

---

## Suggested next axes

1. ~~Raid / military depth~~ → E6.0  
2. Confirm science path (seed 100)  
3. Human-paced god-view / presentation  
4. Learning-agent interface later  

---

Determinism sacred. One axis at a time. Ledger = status. DESIGN = vision.
