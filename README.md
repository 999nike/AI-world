# AI-world

AI-world is a deterministic, tick-based agent civilization simulator.

It is built as a **systems laboratory first**, and a game second.

Four AI agents operate under shared physical and economic constraints
(food, wood, stone), attempting to survive, grow settlements, and manage resources
in a persistent world.

There is no player control loop.
This is about emergence, not scripting.

---

## Current State (v0 – Feb 2026)

### Core Simulation
- Deterministic tick-based engine
- Seeded, reproducible runs
- Grid world with resource regrowth
- Headless execution (CLI only)
- JSONL event logging
- Snapshot logging
- Summary metrics + score output

### Agents
- Move / gather / build (hut, storage)
- Inventory system
- Utility-based baseline policy
- Settlement-aware behavior
- Guarded build overrides to prevent spam

### Settlements
- Created from structures
- Linked to spatial anchors
- Population per settlement
- Food consumption per tick
- Starvation and collapse possible
- Automatic deposit of gathered resources
- Construction funded from inventory + tile + settlement stock

### Metrics
- Settlements created
- Structures built
- Food deposited
- Population growth & starvation
- Net population change
- Aggregate score

---

## What This Project Is

- A deterministic civilization simulation
- A research systems lab
- A foundation for emergent AI behavior

## What It Is Not (Yet)

- Not a player-controlled RTS
- Not a narrative generator
- Not a reinforcement learning benchmark
- Not a visual game (CLI only)

---

## Run

```bash
python -m compileall sim
python -m sim run --seed 42 --ticks 300
