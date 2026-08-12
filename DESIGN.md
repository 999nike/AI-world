# AI-world Design Notes (Internal)

**Last updated:** 2026-08-12  
**Era 1:** VALIDATED (32/32 stress pass)  
**Era 2:** Stages 0–3 live + validated (Granary, Mine, Roads, Workshop). Stress 14/14 pass under Workshop.

---

## Intent

Deterministic civilisation lab. Agents survive under scarcity. Humans can govern / scenario / drop-in. Long-term: trainable agents (deferred until stable).

---

## Determinism (sacred)

Same seed + same code → same outcome. Logs are source of truth.

---

## Era 1 — Settlement Survival (LOCKED + validated)

- 32×32, food/wood/stone, 4 agents default (configurable)
- Buildings: farm, storage, hut
- Settlements, deposit range 2, population growth/starvation
- Farm soft-cap 3/settlement; first building forced to farm
- Reference: stress 100% pass; seed 42 healthy

---

## Era 2 — Classical (IN PROGRESS)

| Stage | Building | Cost | Gate | Effect |
|-------|----------|------|------|--------|
| 0 | **granary** | 3w 1s | storage + farm, max 1 | +0.5 food/tick; starve ticks 4 |
| 1 | **mine** | 2w 3s | storage + farm, max 1 | +0.75 stone/tick |
| 2 | **road** | 1w | mine OR 4+ structs | deposit range → 3 |
| 3 | **workshop** | 4w 2s | mine + (granary OR road), max 1 | tools_stock +0.4/tick; farm +0.25/farm; mine +0.25; gather +1 extra when tools≥1 (consume 0.5) |

Human roles (Governor, Scenario, Drop-in) and tools (view_run, god_view, multi_seed, stress_test) remain as implemented.

---

## Dev rules

1. Determinism sacred  
2. One major axis at a time  
3. Small patches → ledger  
4. Learnable agents only when world is stable  

See PATCH_LEDGER.md for patch history.
