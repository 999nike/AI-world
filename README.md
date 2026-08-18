# AI-world

Deterministic civilisation simulation lab.

Four (or more) agents survive, build, and manage settlements under scarcity.
Everything is seed-controlled and fully logged. Humans can steer, design scenarios, or take control of an agent. The long-term goal includes using this as a training environment for learnable agents.

**Era 1 status: LOCKED** (2026-08-12)

---

## Quick start

```bash
# Basic run
python -m sim run --seed 42 --ticks 300

# More agents
python -m sim run --agents 6 --seed 42

# Soft human guidance
python -m sim run --governor "focus food"

# Scenario + event
python -m sim run --scenario "seed 42; start_food 6; event drought 120"

# Take control of one agent
python -m sim run --control A0 --control-policy gather_food

# Playable: pause at fat moments, pick an edict
python -m sim run --playable --seed 42 --ticks 2000
python -m sim run --playable --choice-policy seeded --seed 42 --ticks 2000
```

On Windows if `python` is not on PATH:
```bash
%LocalAppData%\Programs\Python\Python312\python.exe -m sim run --seed 42 --ticks 300
```

---

## Tools

```bash
# Economy / build / population log
python tools/view_run.py --rid latest --log economy

# ASCII god-view (step through ticks)
python tools/god_view.py --rid latest --step

# Multi-seed comparison table
python tools/multi_seed_validate.py
```

---

## Human roles (minimal versions)

| Role | Flag | Purpose |
|------|------|--------|
| **Governor** | `--governor "focus food"` | Soft bias on all agents |
| **Playable** | `--playable` | Pause at fat moments; pick food / science / army |
| **Scenario** | `--scenario "..."` | Starting conditions + timed events |
| **Drop-in** | `--control A0 --control-policy gather_food` | Direct control of one agent |

Playable: `--choice-policy human|first|seeded` (human asks; first always feeds; seeded is deterministic)  
Web: `python tools/play_web.py --host 0.0.0.0 --port 8080`  
Governor commands: `focus food|build|expand|science|army`, `build farm|hut|storage|none`, `clear`  

Scenario commands: `seed N`, `ticks N`, `agents N`, `start_food/wood/stone N`, `event drought TICK`, `event boom TICK`  
Control policies: `gather_food`, `gather_wood`, `gather_stone`, `build_farm`, `build_hut`, `build_storage`, `idle`

---

## Current systems (Era 1)

- 32×32 grid, food / wood / stone
- Deterministic regrowth
- Buildings: farm, storage, hut (with soft caps and gates)
- Settlements with shared stock + population
- Growth / starvation rules (net deficit after farm yield)
- Score based on pop, settlements, structures, food deposited, starvation events
- Full event + snapshot logging

Reference (seed 42, 300 ticks, 4 agents): score ≈ 241

---

## Project direction

1. Keep Era 1 stable
2. Multi-seed validation
3. Era 2 (tech, roads, light military) — only after validation
4. Much later: learnable / thinking agents (research path)

Determinism is sacred. Logs are the source of truth. Visuals come after systems.

See `DESIGN.md` for full internal notes and `PATCH_LEDGER.md` for patch history.
