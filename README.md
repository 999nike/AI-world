# AI-world
Alright — you’re describing an agent-based civilization simulator that’s built first as a learning laboratory, and only later gets a “god-view” visualizer so you (and humans) can watch the ants build empires.
Below is a master template README you can drop into a repo and build from. It’s opinionated, practical, and aimed at 4 AIs learning behaviors (economy, planning, cooperation, conflict, governance) inside a persistent world.
MASTER TEMPLATE README — “CIVSIM LAB”
Agent-based world simulator for 4 AI agents to progress, learn skills, build villages → cities, develop tech ages, and evolve an economy. Human-facing UI is a spectator “god view”, not a game.
0) Design goals
Primary
Train and observe emergent AI behavior under constraints (scarcity, risk, partial info).
Support long-horizon planning (days → decades → ages).
Generate high-quality logs for analysis and replay.
Secondary
“God view” visualization (spectator) for humans: watch, time-lapse, inspect agents.
Non-goals (early)
No handcrafted storylines, no scripted quests, no “player fun loop”.
No PvP twitch mechanics, no micro-management UI.
1) Core pillars
Lawful simulation
Same physics/econ rules every run. Random seeds only change initial conditions.
Partial observability
Agents don’t get the full map state. They must explore and infer.
Scarcity + tradeoffs
Time, labor, food, materials, safety, social trust. Everything costs something.
Emergence over scripting
Systems create problems; agents invent solutions.
Instrumented world
Every action produces events + metrics. Replays are first-class.
2) High-level loop
Simulation proceeds in ticks.
Per tick:
Environment updates (weather, crops growth, decay, NPC faction moves)
Each agent receives an observation (limited, noisy)
Each agent chooses actions (possibly invalid)
Resolver applies actions (costs, conflicts, movement, crafting)
World state updates (economy, population, health, buildings)
Log everything (events + snapshots)
Optionally render (headless early; later god-view)
3) World model
3.1 Map
Tile/grid or navmesh (start grid for simplicity)
Biomes: plains, forest, mountain, river, coast, desert
Resources distributed with regeneration rules:
renewable: wood, animals, fish
semi-renewable: soil fertility
non-renewable: ore, stone, rare metals
3.2 Time and ages
Use two time scales:
tick time: minute/hour equivalent
season/year time: drives farming, winter, disease, trade cycles
Ages are unlocked by tech prerequisites, not scripted:
Stone → Bronze → Iron → Medieval-ish → Early Industry (or whatever you choose)
4) Agents (your 4 AIs)
Each agent is a “civilization brain” controlling a group, not a single person (you can scale down later).
4.1 Agent state
Attributes: risk tolerance, cooperation tendency, planning horizon, curiosity, aggression
Memory: discovered tiles, known prices, known treaties, past conflicts
Resources: food, materials, tools, population, morale
Policy: decision-making model (RL, planning, LLM tool use, etc.)
Meta-learning: optional “rules to modify rules” (policy improvement)
4.2 Actions (minimum set)
Explore(tile)
Gather(resource)
Craft(item)
Build(structure)
AssignLabor(role, count)
Trade(offer, request, partner)
Diplomacy(propose treaty / break treaty / threaten)
Research(tech)
Tax/Redistribute(policy)
Defend/Attack(target) (optional; keep for later)
4.3 Observation (partial info)
Each tick, agent gets:
Local map in radius R (fog-of-war)
Own resources + population stats
Nearby settlements known (not all)
Market prices they’ve observed
Diplomatic messages received
Recent events (attacks, famine, disease)
5) Economy and production (simple first, deep later)
5.1 Goods
Start with a clean production graph:
Food (berries/fish/grain)
Wood
Stone
Ore
Tools
Housing
Luxuries (optional)
5.2 Production
Labor converts inputs → outputs with efficiencies
Tools increase efficiency (classic old-school loop)
Transport costs matter (distance adds friction)
5.3 Market
Two options (start easy):
Local markets per settlement (prices drift by scarcity + trade)
Global market (simpler but less realistic)
Let agents learn:
arbitrage
hoarding vs liquidity
long-term investment (tools/infrastructure)
6) Settlement growth: village → town → city
6.1 Buildings
Hut/House
Farm
Storage
Workshop
Mine
Market
Road (increases movement speed)
Wall/Guard post (later)
6.2 Growth constraints
Population grows if:
Food surplus
Housing available
Morale/health stable
Population shrinks if:
starvation, disease, war, cold exposure
7) “God view” spectator UI (later, but plan now)
Design the sim to be headless and render-optional.
UI goals
Time controls: pause, 1x, 5x, 20x, timelapse
Layers: terrain, resources, ownership, trade routes, happiness, tech
Click agent → see:
current goals
internal state (allowed subset)
memory map (what it knows)
recent decisions + rationale (if available)
Replay viewer: jump to tick, inspect events
Important: UI should never be required for the sim to run.
8) Data + logging (this is the secret sauce)
If you want to “learn from them,” logging is everything.
8.1 Event log (append-only)
Store every meaningful event:
action_attempted
action_resolved
trade_made
structure_built
tech_unlocked
treaty_signed/broken
famine_started/ended
conflict_started/ended
8.2 Snapshots
Every N ticks store:
full world state summary
per-agent summary
market state
8.3 Replays
A replay is:
seed
initial config
event log
deterministic sim version
If you do this right, you can re-render old worlds later.
9) Reward / learning signals (optional but recommended)
Don’t overfit the agents to dumb scores. Use multi-objective signals.
Possible metrics:
survival years
population health
tech progress rate
trade volume efficiency
stability (low rebellion, low famine)
diplomacy reputation (kept promises)
Also track “interestingness” for you:
novelty of strategies
diversity of policies
emergent cooperation/war cycles
10) Demonstration milestones (build order)
Here’s the build path that won’t collapse under ambition:
Milestone A — “Ants in a box”
Grid map + fog-of-war
Gather + move + build hut + food decay
4 agents run headless
Event logging + deterministic seed replay
Milestone B — “Villages”
Farms + seasons
Population growth
Craft tools improves efficiency
Local markets with price drift
Milestone C — “Towns & trade”
Trade routes (distance cost)
Specialization (mine town, farm town)
Diplomacy messaging API
Milestone D — “Ages”
Tech tree
Buildings unlock by tech
More goods + deeper production chains
Milestone E — “God view”
Minimal renderer (top-down)
Timeline scrubber + inspector panel
Replay playback
11) Repo template structure
Use something like:
/sim
/core (tick loop, determinism, RNG, scheduler)
/world (map, resources, buildings, rules)
/economy (goods, production, markets)
/agents
agent_interface
baseline_agents (random, greedy, planner)
/events (event schema, logger, replay)
/metrics (KPIs, charts exports)
/ui (later)
renderer
replay_viewer
/configs
world_small.yaml
world_medium.yaml
tech_tree.yaml
/docs
DESIGN.md
EVENT_SCHEMA.md
API.md
/runs (output logs, replays)
12) Agent API (clean contract)
Define a strict interface so you can swap brains:
Input: Observation
local tiles
visible entities
own stats
message inbox
known prices (optional)
Output: Action[]
structured actions
bounded per tick (e.g., max 5)
Simulator guarantees:
deterministic resolution given seed + actions
invalid actions return errors (logged)
13) Baseline agents you should ship day 1
These help you debug and benchmark:
Random walker
Greedy gatherer (food-first)
Builder (prioritizes housing/storage)
Trader (seeks price differences)
Pacifist diplomat vs aggressive raider (later)
If your learned AIs can’t beat these, you know you’ve got a systems or reward problem.
14) Launch checklist (your “game launch” but for sims)
Alpha (you only)
deterministic runs
event logs validated
1000-tick stable no crashes
replay reproduces same results
Beta (watchable)
god view basic
performance: 10k+ ticks fast-forward
inspector tools
Public demo
“seed of the day”
timelapse exports
curated scenarios (drought, resource-rich, hostile neighbors)
15) A sane first scenario
Start with:
small map
4 agents spawned far apart
mild climate
enough food sources to survive
scarce ore (forces trade/exploration)
no combat initially (combat later)
You want learning, not immediate extinction.


# AI-world## Agent-Based Civilization Simulator Lab
v0 — Current State (Reality-Checked)
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
[x] Settlement-aware behavior (food delivery bias)
[x] Infrastructure ordering rules (storage before huts)
Settlements (CORE SYSTEM COMPLETE) ✅
[x] Settlement creation
[x] Spatial settlement anchors
[x] Population per settlement
[x] Food stockpiles
[x] Wood & stone stockpiles
[x] Automatic agent deposits
[x] Food consumption per tick
[x] Population growth logic
[x] Starvation & population decline
[x] Settlement-linked structures
[x] Settlement funding of construction
[x] Settlement → structure ownership mapping
Economy (Lite but Functional) ✅
[x] Shared settlement resource pools
[x] Resource inflow/outflow tracking
[x] Deposit & consumption events logged
[x] Build funding events (when applicable)
[x] Metrics visibility for tuning
Analysis & Debugging ✅
[x] Human-readable JSON outputs
[x] Metrics counters (builds, starvation, growth, deposits)
[x] Grep-friendly logs
[x] Deterministic reproduction of runs
Known Limitations (Intentional for v0) ⚠️
Agents have no long-term planning
No explicit roles (farmer / builder / hauler yet)
No food spoilage or storage decay
No trade between settlements
No terrain costs or physics constraints
No visualisation layer (CLI only)
These are design gaps, not bugs.
v0.1 Next Targets (Ordered, Minimal, High Impact)
Expose global structures + settlements cleanly in Observation (done / locking in)
Guarantee storage construction (bootstrap phase)
Role bias per settlement (1 gatherer / 1 builder)
Food buffer tuning (prevent early collapse)
Simple settlement growth stabilisation
Visual playback layer (grid renderer / replay)
Project Scope (What This Is)
This project is an agent-based civilisation simulator, focused on:
Emergent behavior
Resource-constrained growth
Economic feedback loops
Deterministic experimentation
AI policy evolution over time
It is not a game yet — it is the engine beneath one.
Physics, maths, and real-world constraints will be layered after the core economy stabilises.
Dev Rules (Locked In)
No micro-patch spam
Large, meaningful changes only
One file at a time when possible
Determinism always preserved
Logs > visuals > polish
🟢 Status:
v0 core is complete.
