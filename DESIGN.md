# AI-world Design Notes (Internal)

**Last updated:** 2026-08-17  
**Content ceiling:** Era 4 + E5 science line + discoveries

---

## Vision (look & feel)

**The Settlers** for human play: top-down, resource chains, haul labour, buildings that feel alive, watching a settlement grow.

**Civilization** for structure: ages, subjects/tech, long-horizon choices, guns-vs-butter tension.

**Research lab** underneath: fully deterministic, seed-controlled, every decision logged. Logs become the animation / god-view pipeline. Humans watch or steer; later agents learn.

Feel target when a human plays:  
“I am watching a living settlement make real choices. Bad priorities hurt. Good ones compound.”

Not pure spreadsheet. Not pure action game.  
**Lab engine first → watchable game → optional learning agents on the same rules.**

---

## Goals (hand-off)

### Near-term (engine)
- Long runs (5k–10k ticks) stable without log bottleneck
- Era 4 + science path reachable consistently under baseline utility agent
- Trade-offs that still matter late (army costs food, science delays economy, etc.)
- Quiet mode for batch experiments; full logs when debugging

### Mid-term (depth)
- Richer mid/late decisions after Observatory (discoveries are the first sink)
- Military / raid depth worth caring about over long horizons
- Clearer specialisation identities (craft / organisation / strategy / inquiry)

### Longer vision
- Science labs → physics-style experiments / tech unlocks
- Modern-era buildings as late content
- Human presentation layer (paced god-view, governor control)
- Learning agents that improve inside the same deterministic rules

### Non-goals (for now)
- Perfect balance for human multiplayer
- Replacing the utility agent with RL immediately
- DESIGN.md as a patch checklist (ledger owns status)

---

## Intent

Deterministic multi-agent civilisation lab → watchable Settlers × Civ hybrid.  
Logs = animation pipeline. Ages progression. Learning agents later.  
One simulation kernel; lab and human UI are layers on top.

---

## Current content shape (vision, not checklist)

**Survival → specialisation → science**

- Early: farms, storage, food pressure
- Mid: workshop → barracks → civic chain → academy / subjects
- Era 4: subject buildings (irrigation, library, foundry, hall, command)
- E5: Lab → Observatory → discoveries (knowledge sink → permanent farm bonus)

Guns-vs-butter remains core: soldiers help raids/defend but always cost food; soft-cap vs population.

---

## God-view

`--play` auto-steps snapshots with key event callouts.  
Icons: C academy | # walls | ~ irrigation | L library | Y foundry | O hall | X command | R lab | V observatory

---

## Dev rules

1. Determinism sacred  
2. One axis at a time  
3. Logs first  
4. Min tokens while usage high  
5. Choices must be able to hurt  
6. Ledger = status; DESIGN = vision  
