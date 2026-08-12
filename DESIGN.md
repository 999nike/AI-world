# AI-world Design Notes (Internal)

This document describes current mechanics, limitations, and roadmap.
It is the internal truth for development sessions.

**Last locked:** 2026-08-12 (Era 1 stabilisation session)

---

## Intent

Civilisation simulation lab. Deterministic world where agents develop strategies under scarcity.
UI/visuals come later. Logging and replay are first-class.
Long-term vision: Civ-style ages (Stone → later eras with deeper systems, physics, monuments).

---

## Determinism (sacred)

- Seed controls all RNG
- Same seed + same code/config → same outcome
- Logs exist for replay and analysis

---

## Era 1 — Settlement Survival (LOCKED 2026-08-12)

### World
- 32×32 grid
- Tiles: food, wood, stone
- Deterministic regrowth every 5 ticks

### Agents
- 4 agents
- Actions: move / gather / build
- Inventory: food / wood / stone
- Brain: UtilityAgent (weighted utilities + ε-greedy)
- Observation includes: local tile, inventory, structures, **settlements**, **nearest_settlement**

### Buildings & costs
| Building | Wood | Stone | Notes |
|----------|------|-------|-------|
| farm     | 2    | 0     | Soft-capped at 3 per settlement |
| storage  | 3    | 2     | Max 1 per settlement |
| hut      | 2    | 1     | Requires storage; blocked while starving |

### Build governors
1. First building priority → farm (if none exist)
2. Storage capped at 1 → further storage attempts become huts
3. Farm soft-cap at 3 → further farm attempts become huts
4. Hut requires storage present + `starve_ticks == 0`

### Settlements
- Created when first structure is linked
- Stocks: food / wood / stone
- Agents auto-deposit when within distance 2 of settlement anchor
- Buildings can be funded from agent inventory, tile, or settlement stock

### Population rules (SETTLEMENT_RULES)
```
food_per_pop_per_tick   = 0.25
farm_yield_per_tick     = 1.5
growth_food_buffer      = 3
surplus_ticks_for_growth = 5
starve_ticks_for_loss    = 3
max_pop_growth_per_tick  = 1
starting_population      = 1
```

**Growth:** 5 consecutive ticks with food surplus ≥ need + buffer → +1 pop  
**Starvation:** 3 consecutive ticks where post-harvest food < need → −1 pop  
(Starvation uses **net deficit after farm yield**, not empty pantry before harvest.)

### Score (v0)
```
score = pop*10 + settlements*25 + structures*5 + food_deposited - starved_events*5
```

### Reference run (seed 42, 300 ticks, post-balance)
- Score ≈ 241
- Huts / Storage / Farms ≈ 12 / 1 / 3
- Net pop positive
- Starvation present but non-catastrophic

---

## Architecture (post-refactor)

```
sim/
  core/
    simloop.py          # tick loop (slimmed)
    build_governors.py  # resolve_building, can_build_hut
    rng.py
  world/
    settlements.py      # SettlementManager (create, deposit, tick, link)
    state.py / map.py / config.py
  agents/
    types.py            # Observation (includes settlements)
    utility_agent.py
  log/
  train/
tools/
  view_run.py           # filtered economy / build / pop viewer
PATCH_LEDGER.md         # patch history for this cleanup
```

---

## Known limitations (Era 1)

- Single settlement is the common case; multi-settlement under-tested
- No roles / specialisation
- No inter-settlement trade or couriers
- No tech / ages yet
- Hard food/haul guards still exist in simloop as safety net
- No god-view renderer (CLI + JSONL only)

---

## Roadmap (after Era 1 lock)

### Near
- Multi-seed validation (several seeds × 500–1000 ticks)
- Soften or remove remaining hard guards (P2.2)
- Minimal ASCII / CLI replay viewer improvements

### Era 2 direction (not started)
- Tech / ages progression
- Additional buildings (workshop, mine, …)
- Deeper production chains
- Soft agent roles
- Later: physics experiments, monuments (pyramids etc.) as long-horizon goals

---

## Dev rules

1. Determinism is sacred
2. One major axis of change at a time
3. Logs > visuals > polish
4. Prefer extraction + cleanup before new features
5. Small patches → approve → push → update ledger
