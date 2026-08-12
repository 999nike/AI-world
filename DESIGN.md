# AI-world Design Notes (Internal)

**Last updated:** 2026-08-12  
**Era 1:** LOCKED  
**Era 2:** COMPLETE  
**Era 3:** E3.0–E3.2 live (age-up, Market, Temple)

---

## Intent

Deterministic civilisation lab. Agents survive under scarcity. Humans can govern / scenario / drop-in. Long-term: trainable agents (deferred until stable).

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

## Era 3

### E3.0 Age transition
- Gate: workshop + barracks + pop ≥ 15
- Effect: era=3, +5 food, +0.25 farm yield/farm

### E3.1 Market
| Cost | Gate | Effect |
|------|------|--------|
| 4w 3s | era≥3 + barracks, max 1 | +0.5 wood/tick, +0.25 stone/tick |

### E3.2 Temple
| Cost | Gate | Effect |
|------|------|--------|
| 3w 4s | era≥3 + market, max 1 | +0.25 food/tick; growth surplus ticks 3 (was 5) |

---

## Dev rules

1. Determinism sacred  
2. One major axis at a time  
3. Small patches → ledger  
4. Learnable agents only when world is stable  
