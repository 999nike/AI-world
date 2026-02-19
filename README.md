Good. If you’re putting this on GitHub, it should look intentional, not dumped.
Here’s a sharper, more “serious project” styled version.
Same content. Better structure. Better hierarchy. Cleaner tone.
You can paste this directly.
AI-world
Deterministic Agent Civilization Simulator
AI-world is a deterministic, tick-based multi-agent civilization simulator.
It is built as a systems laboratory first, and a game second.
Four autonomous agents operate under shared physical and economic constraints (food, wood, stone), attempting to survive, expand settlements, and manage long-term resource stability in a persistent world.
There is no player control loop.
This project studies emergence — not scripting.
🧠 Current State — v0 (Feb 2026)
Engine
Deterministic tick-based simulation core
Seed-controlled reproducibility
Grid world with deterministic resource regrowth
Headless CLI execution
JSONL event logging (events.jsonl)
Snapshot logging (snapshots.jsonl)
Structured run summary (summary.json)
Verified stability across 100–5000 tick multi-seed runs
Agents
Move / gather / build (hut, storage, farm)
Inventory system (food / wood / stone)
Utility-based baseline decision policy
Settlement-aware deposit behavior
Guarded build logic (anti-spam)
Infrastructure ordering (storage before expansion)
Settlements
Emergent creation from structures
Spatial anchor linkage
Population tracked per settlement
Shared resource stockpiles
Automatic agent deposits
Construction funded from:
Agent inventory
Tile storage
Settlement stock
Demographic Model
Food consumed per population per tick
3-tick starvation rule → population decline under sustained deficit
3-tick surplus rule → population growth under sustained surplus
Single-settlement survival loop confirmed stable
Economy (v0 – Lite but Stable)
Farms yield 1.0 food per tick
Shared settlement resource pooling
Logged inflow / outflow tracking
Growth and starvation metrics exposed
Multi-seed stability validation completed
Observability & Metrics
Settlements created
Structures built
Food deposited
Population growth events
Starvation events
Net population change
Aggregate score
Determinism + logging are first-class citizens.
🎯 Project Intent
AI-world is:
A deterministic civilization simulation
A research systems lab
A controlled environment for emergent multi-agent behavior
A foundation for long-horizon policy experimentation
It is not a game yet.
It is the simulation engine beneath one.
🚫 Out of Scope (For Now)
No player-controlled RTS loop
No narrative scripting
No reinforcement learning framework
No visual renderer (CLI only)
No tech-tree progression yet
No inter-settlement trade
▶ Run
Bash
Copy code
python -m compileall sim
python -m sim run --seed 42 --ticks 300
🟢 Status
Core economy stabilized.
Entering multi-settlement expansion phase.
That reads like:
A research engine.
Not a toy.
Not bloated.
Not amateur.
Now it looks deliberate.
If you want it to look even more serious, next step would be adding:
A tiny “Stability Snapshot” table from your 5k run
A small architecture diagram section
Or a badge row at the top (Python version / deterministic / CLI)
But this version is already professional.
No fluff. No cringe. Clean.
Your call.
