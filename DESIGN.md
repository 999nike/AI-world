# AI-world Design Notes (Internal)

**Last updated:** 2026-08-12  
**Era 1:** VALIDATED (32/32 stress pass)  
**Era 2:** Complete (Granary, Mine, Roads, Workshop, Barracks + defense/raids)  
**Era 3:** Age transition live (E3.0)

---

## Intent

Deterministic civilisation lab. Agents survive under scarcity. Humans can govern / scenario / drop-in. Long-term: trainable agents (deferred until stable).

---

## Determinism (sacred)

Same seed + same code → same outcome. Logs are source of truth.

---

## Era 1 — Settlement Survival (LOCKED)

- 32×32, food/wood/stone, 4 agents default
- Buildings: farm, storage, hut
- Settlements, deposit range 2, population growth/starvation

---

## Era 2 — Classical (COMPLETE)

| Stage | Building | Cost | Gate | Effect |
|-------|----------|------|------|--------|
| 0 | granary | 3w 1s | storage + farm, max 1 | +0.5 food/tick; starve ticks 4 |
| 1 | mine | 2w 3s | storage + farm, max 1 | +0.75 stone/tick |
| 2 | road | 1w | mine OR 4+ structs | deposit range → 3 |
| 3 | workshop | 4w 2s | mine + (granary\|road), max 1 | tools +0.4/tick; farm/mine bonus; gather boost |
| 4 | barracks | 3w 3s | workshop, max 1 | soldiers +0.25/tick |
| — | defense | — | soldiers ≥1 | absorb starve loss (cost 1.0) |
| — | raids | — | soldiers ≥3, multi-settlement | every 25 ticks steal loot |

---

## Era 3 — Age Transition (E3.0 live)

**Gate:** workshop + barracks + population ≥ 15  
**On age-up:** `era = 3`, +5 food, log `age_transition`  
**Passive:** +0.25 farm yield per farm while era ≥ 3

Settlements start at era 2. First Era 3 buildings TBD.

---

## Dev rules

1. Determinism sacred  
2. One major axis at a time  
3. Small patches → ledger  
4. Learnable agents only when world is stable  

See PATCH_LEDGER.md for patch history.
