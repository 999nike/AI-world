# AI-world Design Notes (Internal)

**Last updated:** 2026-08-12  
**Era 1:** LOCKED  
**Era 2:** COMPLETE  
**Era 3:** COMPLETE (E3.0–E3.4)  
**Era 4:** E4.0–E4.1 live

---

## Intent & Long-term Vision

Deterministic multi-agent civilisation laboratory that becomes a **watchable game**.

- Systems first: headless, seed-controlled, fully logged.
- Human experience later: Settlers-style top-down god-view. Logs = animation pipeline.
- Ages progression (Civ flavour).
- Learning agents only after world is stable and interesting.

---

## Determinism (sacred)

Same seed + same code → same outcome. Logs are source of truth.

---

## Era 1 — Settlement Survival (LOCKED)

Farm, storage, hut. Population growth/starvation. Deposit range 2.

---

## Era 2 — Classical (COMPLETE)

Granary, Mine, Road, Workshop, Barracks + defense + raids.

---

## Era 3 (COMPLETE)

E3.0 age-up · E3.1 Market · E3.2 Temple · E3.3 Academy + Subjects · E3.4 Walls

---

## Era 4

### E4.0 Age transition
- Gate: era==3 + Inquiry subject + academy + pop ≥ 20
- Effect: era=4, +5 food, +0.1 farm yield/farm

### E4.1 Irrigation
| Cost | Gate | Max | Effect |
|------|------|-----|--------|
| 3w 2s | era≥4 + agriculture subject | 1 | +0.2 farm yield per farm |

Expands the Agriculture subject into a physical structure.

---

## Dev rules

1. Determinism sacred  
2. One major axis at a time  
3. Small patches → ledger → push  
4. Learnable agents only when world is stable  
5. Logs first — visuals come from logs  
6. Minimum tokens while usage is high  
