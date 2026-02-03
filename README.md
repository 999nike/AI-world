
AI-world
Agent-Based Civilization Simulator (Research / Systems Lab)
AI-world is an agent-based civilisation simulator built as a learning laboratory first and a spectator system second.
Four AI agents operate under the same physical, economic, and temporal constraints, attempting to survive, grow settlements, and coordinate resource use in a persistent world.
Humans observe from a god-view; there is no player control loop.
This project is about emergence, not scripting.
Design Intent (Plain English)
Let simple agents operate under scarcity.
Make every decision costly in time or resources.
Log everything so behavior can be replayed, analysed, and criticised.
Add complexity only after stability is proven.
This is not a game yet.
It is the engine underneath one.
Core Principles
Deterministic Simulation
Every run is fully reproducible via seed + config.
Randomness affects initial conditions, not physics or rules.
Same inputs → same outcomes.
Partial Observability
Agents do not see the whole map.
Decisions are made from local knowledge + memory.
No omniscient policies.
Scarcity First
Food, labor, materials, and time are all constrained.
Growth is earned, not guaranteed.
Starvation and collapse are valid outcomes.
Emergence Over Scripting
No quest logic.
No narrative scaffolding.
Systems create pressure; agents respond.
Instrumentation as a Feature
Event logs are first-class.
Metrics are not an afterthought.
Replays matter more than visuals.
High-Level Simulation Loop
Each simulation advances in ticks.
Per tick:
World state updates (consumption, population, decay)
Each agent receives a partial observation
Agent proposes an action (may be invalid)
Resolver applies rules, costs, and conflicts
Settlements update (stocks, population)
Events and snapshots are logged
(Optional) Renderer consumes state
The simulation is fully headless by default.
World Model (v0)
Map
Grid-based world
Each tile contains:
food
wood
stone
Resources are finite per tile (regen is future work)
Time
Single tick scale (no seasons yet)
Population consumption happens every tick
Agents (Current Reality)
Each agent represents a civilisation brain, not a single person.
Agent Capabilities
Move on the grid
Gather food / wood / stone
Build structures (storage, huts)
Deposit resources into settlements
Follow simple priority-based logic
What Agents Do Not Yet Have
Long-term planning
Explicit roles
Trade or diplomacy
Memory beyond local observation
These absences are intentional for v0.
Settlements (v0 — Core System Complete)
Settlements are the primary economic unit.
Settlement State
Position (anchor tile)
Population
Food stock
Wood stock
Stone stock
Owned structures
Mechanics Implemented
Settlement creation
Automatic population assignment
Food consumption per tick
Starvation and population decline
Resource deposits by agents
Construction funded by settlement stockpiles
Settlement ↔ structure ownership mapping
Bootstrap Logic
Storage is prioritised before housing
Settlements begin with minimal food seeding
Early starvation is allowed but bounded
Economy (Lite but Functional)
Resources
Food
Wood
Stone
Flow
Agents gather from tiles
Agents deposit into settlements
Settlements consume food
Construction drains stockpiles
There is no trade yet.
All economics are local.
Data & Logging (Critical Feature)
Event Log (events.jsonl)
Append-only stream of:
action_attempted
action_resolved
settlement_created
resource_deposited
population_changed
starvation events
construction events
Snapshots
Periodic world summaries
Settlement state
Agent inventories
Summary
Final metrics
Aggregate score
End-of-run state
All outputs are designed to be:
grep-friendly
replayable
stable across versions
Metrics (v0)
Tracked explicitly:
Settlements created
Food deposited / consumed
Population growth & starvation
Structures built
Net population change
Metrics exist to debug systems, not to reward agents yet.
Known Limitations (Intentional)
No long-term agent planning
No explicit labor roles
No inter-settlement trade
No terrain movement costs
No decay or spoilage
No visualisation layer
These are design gaps, not bugs.
Development Rules (Hard Constraints)
One file at a time when possible
Determinism must never be broken
No micro-patch thrashing
Logs before visuals
Stability before ambition
Current Status
v0 core simulation is complete.
The system:
Runs deterministically
Produces valid logs
Supports replay
Exhibits early emergent survival behavior
Fails loudly when logic breaks (by design)
Next work is stabilisation, not expansion.
v0.1 Focus (Ordered)
Settlement survival stabilisation
Guaranteed bootstrap storage
Simple role bias (gatherer / builder)
Observation cleanup
Minimal replay renderer
Performance scaling
What This Project Is Not
Not a scripted RTS
Not a narrative generator
Not a reinforcement-learning benchmark (yet)
Not player-controlled
It is a systems lab.
Final note (important)
This README intentionally describes only what exists or is locked in.
Anything speculative belongs in DESIGN.md, not here.
Verdict (straight talk)
The README is good.
The amended version is honest.
It now matches the actual code instead of the dream version.
You can post this without embarrassment.
When you’re rested:
We can split this into README.md + DESIGN.md
Or write a short public-facing version and keep this as the internal truth
For now: stop.
You did real work tonight.


# AI-world## Agent-Based Civilization Simulator Lab
Got it. Here’s a clean, updated checklist that reflects what the system actually does now, including tonight’s fixes and the remaining rough edges. This is drop-in replacement text for the README section.
I’ve been strict: anything flaky, partial, or guarded-by-hacks is marked honestly.
v0 — Current State (Reality-Checked, Feb 2026)
Core Simulation ✅
[x] Deterministic tick-based simulation
[x] Seeded, replayable runs
[x] Discrete time (ticks)
[x] Event logging (events.jsonl)
[x] Periodic snapshots (snapshots.jsonl)
[x] Final run summary (summary.json)
[x] Metrics aggregation
[x] Simple global score function
Agents ✅
[x] Grid movement
[x] Resource gathering (food / wood / stone)
[x] Inventory system
[x] Building actions (hut / storage)
[x] Baseline agent policy (non-random, priority-based)
[x] Settlement-aware behavior (deposit bias)
[x] Infrastructure ordering rules (storage before huts)
[x] Guarded action override (build → gather when unfundable) ⚠️
Notes
Agents still attempt invalid builds, but guards now redirect many of these to gather.
No agent-level planning or intent persistence yet.
Settlements (CORE SYSTEM, STABLE) ✅
[x] Settlement creation
[x] Spatial settlement anchors
[x] Population per settlement
[x] Food stockpiles
[x] Wood & stone stockpiles
[x] Automatic agent deposits
[x] Food consumption per tick
[x] Starvation & population decline
[x] Settlement-linked structures
[x] Settlement funding of construction
[x] Settlement → structure ownership mapping
[x] Starter food seeding on settlement creation
Notes
Starter food prevents immediate zero-tick collapse.
Population can still hit zero if agents fail to sustain supply early.
Economy (Lite but Functional) ✅
[x] Shared settlement resource pools
[x] Resource inflow/outflow tracking
[x] Deposit & consumption events logged
[x] Build funding from inventory + tile + settlement
[x] Metrics visibility for tuning
Notes
No trade.
No spoilage.
No transport cost.
Economy is local and intentionally simple.
Analysis & Debugging ✅
[x] Human-readable JSON outputs
[x] Metrics counters (builds, starvation, growth, deposits)
[x] Grep-friendly logs
[x] Deterministic reproduction of runs
[x] Headless-first design
Known Limitations (Intentional for v0) ⚠️
No long-term agent planning
No explicit agent roles (farmer / builder / hauler)
No food spoilage or storage decay
No inter-settlement trade
No terrain movement costs
No seasons or climate
No visualisation layer (CLI only)
These are design gaps, not bugs.
Known Rough Edges (Acknowledged) ⚠️
Build-spam still occurs in some edge cases
Population growth is conservative and may stall
Settlement survival depends heavily on early agent luck
Guards exist but are not a replacement for policy learning
Metrics are descriptive, not reward-driven yet
These are acceptable for v0 but must not be hidden.
v0.1 Next Targets (Ordered, Minimal, High Impact)
Hard guarantee: one early storage per settlement
Simple per-settlement role bias
at least one food gatherer
at least one builder
Food buffer tuning (prevent zero-pop death spiral)
Reduce build-spam at policy level (not guards)
Observation cleanup (explicit settlement context)
Minimal replay renderer (grid + time scrub)
Project Scope (Unchanged)
This project is an agent-based civilisation simulator, focused on:
Emergent behavior
Resource-constrained growth
Economic feedback loops
Deterministic experimentation
AI policy evolution over time
It is not a game yet — it is the engine beneath one.
Dev Rules (Locked In)
No micro-patch spam
Large, meaningful changes only
One file at a time when possible
Determinism always preserved
Logs > visuals > polish
🟢 Status
v0 core is complete and stable enough to study.
The system now survives long enough to expose real behavioral problems — which is exactly where it should be.
If you want, next time we can:
Split this into README.md (public) and DESIGN.md (brutally honest)
Or add a “Known Failure Modes” section (very research-cred)
