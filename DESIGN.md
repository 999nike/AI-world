# AI-world Design Notes (Internal)

This document describes current mechanics, limitations, and roadmap.
It is the internal truth for development sessions.

**Last updated:** 2026-08-12 (human roles + tools session)  
**Era 1 status:** LOCKED  
**Era 2 status:** Draft only — do not implement until multi-seed validation is done and reviewed.

---

## Intent

Civilisation simulation lab. Deterministic world where agents develop strategies under scarcity.
Logging and replay are first-class. Humans can participate, not only spectate.

Long-term vision shaped by:
- **Civilization VI** — ages, tech gates, long time horizon, meaningful unlocks
- **The Settlers** — resource chains, haul labour, specialised buildings, roads

Pipeline: headless sim → rich logs → god-view → human roles.

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
- 4 agents (A0–A3)
- Actions: move / gather / build
- Inventory: food / wood / stone
- Brain: UtilityAgent (weighted utilities + ε-greedy)
- Observation includes: local tile, inventory, structures, settlements, nearest_settlement

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
(Starvation uses **net deficit after farm yield**.)

### Score (v0)
```
score = pop*10 + settlements*25 + structures*5 + food_deposited - starved_events*5
```

### Reference run (seed 42, 300 ticks)
- Score ≈ 241
- Huts / Storage / Farms ≈ 12 / 1 / 3
- Net pop positive, starvation present but controlled

---

## Architecture (current)

```
sim/
  core/
    simloop.py          # tick loop
    build_governors.py  # resolve_building, can_build_hut
    governor.py         # soft human preferences (P6.0)
    scenario.py         # starting conditions + timed events (P7.0)
    rng.py
  world/
    settlements.py      # SettlementManager
    state.py / map.py / config.py
  agents/
    types.py
    utility_agent.py
    controlled_agent.py # drop-in human control (P8.0)
  log/
  train/
tools/
  view_run.py           # economy / event log viewer
  multi_seed_validate.py
  god_view.py           # ASCII grid + tick scrub
PATCH_LEDGER.md
DESIGN.md
```

---

## Human participation (implemented)

All three roles exist in minimal form.

### 1. Governor (P6.0)
Soft bias on agent utilities. Never hard-forces (except true emergency food).

```bash
python -m sim run --governor "focus food"
python -m sim run --governor "build hut"
python -m sim run --governor "focus expand"
python -m sim run --governor "clear"
```

Commands: `focus food|build|expand`, `build farm|hut|storage|none`, `clear`

### 2. Scenario designer (P7.0)
Starting conditions + timed events.

```bash
python -m sim run --scenario "seed 42; start_food 6; event drought 120"
python -m sim run --scenario "seed 7; ticks 500; event boom 80"
```

Commands: `seed N`, `ticks N`, `start_food/wood/stone N`, `event drought TICK`, `event boom TICK`

### 3. Drop-in agent (P8.0)
Take direct control of one agent.

```bash
python -m sim run --control A0 --control-policy gather_food
python -m sim run --control A1 --control-policy build_hut
```

Policies: `gather_food`, `gather_wood`, `gather_stone`, `build_farm`, `build_hut`, `build_storage`, `idle`

---

## Tools

| Tool | Purpose |
|------|--------|
| `tools/view_run.py` | Filtered economy / build / pop log |
| `tools/multi_seed_validate.py` | Run several seeds and print comparison table |
| `tools/god_view.py` | ASCII grid + tick scrub from snapshots |

---

## Known limitations (Era 1)

- Single settlement is the common case; multi-settlement under-tested
- No roles / specialisation yet
- No inter-settlement trade or couriers
- No tech / ages yet
- God-view is ASCII only (no animation window)
- Governor / Scenario / Drop-in are minimal first versions

---

## Roadmap

### Remaining before Era 2
1. **Multi-seed validation** — run the tool, review results across seeds
2. (Optional) small polish on tools or human-role feedback

### Then
3. Implement Era 2 draft below
4. First military unit + light combat (logged)
5. Later eras (Medieval → Industrial → Modern → Future / nukes)

---

## Era 2 — Classical (DRAFT — not started)

Civ VI flavour + Settlers labour chains. Unlock only after Era 1 multi-seed validation.

### Design goals
- Tools and organisation, not just more huts
- Roads and haul matter (Settlers)
- First military option (Civ)
- Still fully deterministic and logged
- Short tech list (5–6 max)

### Tech spine

| Tech | Gate (suggested) | Unlocks |
|------|------------------|--------|
| Pottery | 1 storage + sustained food surplus | Granary |
| Mining | Stone stock threshold | Mine (tile improvement) |
| Wheel | Mine or 3+ structures | **Roads** |
| Craftsmanship | Wood stock + basic production | **Workshop** (tools) |
| Military Tradition | Workshop or pop ≥ 15 | First military unit |
| Early Empire | 2 settlements or road link | Second-settlement / border bonus |

### New buildings

| Building | Role | Notes |
|----------|------|-------|
| Granary | Food buffer, less waste | Softens starve pressure |
| Mine | Improves stone (later ore) | Tile improvement |
| Road | Faster movement, connectivity | Enables specialisation |
| Workshop | Wood/stone → tools | Tools boost gather/build |
| Barracks (tiny) | Enables unit training | Optional gate for military |

### Settlers-style rules
- Workshop needs delivered wood/stone (haul still matters)
- Roads reduce move cost / link settlements
- Specialisation can emerge: mine town + farm town + road

### Military (light)
- One unit type first (warrior / spearman)
- Cost: population + resources
- Actions: defend or (later) raid
- Events: `unit_trained`, `combat_resolved`
- Human governor can order train / stand down

### Age transition (Era 1 → Era 2)
Pick **one** primary gate for clarity in logs, e.g.:
- Tech “Craftsmanship” completed, **or**
- Total population ≥ 25 with ≥ 1 workshop, **or**
- Two settlements connected by road

### Frozen constraints
- Determinism unchanged
- Event log remains source of truth
- Era 1 rules do not change
- God-view only reads logs; never owns simulation state

---

## Dev rules

1. Determinism is sacred
2. One major axis of change at a time
3. Logs > visuals > polish
4. Prefer extraction + cleanup before new features
5. Small patches → approve → push → update ledger
6. No Era 2 code until Era 1 multi-seed validation passes
