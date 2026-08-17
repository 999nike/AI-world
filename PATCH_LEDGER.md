# AI-world Patch Ledger

**Hand-off snapshot:** 2026-08-17  
**Status:** E5 science path + E6.0 raid depth + E6.1 god-view polish

---

## Snapshot

```
Repo: https://github.com/999nike/AI-world
Branch: main

Era 1–4 LOCKED | E5 science + discoveries LIVE
E5.3 / E5.3b: inquiry 16 + Library weight 4.8 / bonus 5.5
E6.0: scaled raid loot + strategy reduces loot
E6.1: god-view shows soldiers, discoveries, raid loot, discovery events

God-view icons: C # ~ L Y O X R V
```

---

## Key rules

**Subjects:** inquiry cost = 16  
**Library utility:** weight 4.8, bonus 5.5  
**Raids:** base loot ↑, scale with attacker soldiers, strategy cuts loot 25%, walls +cost  
**Military:** barracks 0.15 / command 0.10; soft-cap ~3×pop; upkeep 0.03

---

## Validation still needed

- Seed-100 Library line (E5.3b)
- Observe scaled raid loot + strategy effect on long runs

```bash
git pull
python tools/multi_seed_validate.py --seeds 42 100 7 999 2026 --ticks 5000 --snapshot-every 250 --quiet
python tools/god_view.py --rid latest --play
```

---

## System status

| System | Status |
|--------|--------|
| Era 1–4 | Live / Locked |
| E5 science + discoveries | Live |
| E5.3 / E5.3b Library push | Live |
| E6.0 Raid depth | Live |
| E6.1 God-view polish | Live |
| Quiet long-run | Live |
| Learning agents | Not started |

---

## Suggested next axes

1. Confirm science path (seed 100)  
2. Further military / presentation polish  
3. Learning-agent interface later  

---

Determinism sacred. One axis at a time. Ledger = status. DESIGN = vision.
