# AI-world Design Notes (Internal)

**Last updated:** 2026-08-19  
**Content ceiling:** Era 4 + E5 science line + discoveries  
**Look north star:** the concept painting (dense city, farms, river, people) — not a Civ 6 screenshot.

Ledger owns status. This file owns vision. Memory Space owns long-term answers across chats — search it if stuck, propose into it when the north star moves.

---

## Vision (look & feel)

**The Settlers** for human play: top-down, resource chains, haul labour, buildings that feel alive, watching a settlement grow.

**Civilization** for structure: ages, subjects/tech, long-horizon choices, guns-vs-butter tension.

**Research lab** underneath: fully deterministic, seed-controlled, every decision logged. Logs become the animation / god-view pipeline. Humans watch or steer; later agents learn.

**Current product (2026-08-19 v10):** watch-first documentary. Human edicts are **hidden**, not deleted. Default web run is `playable=False`, rival on, paced god-view, `soft_outcome=True` so a science hold is a headline and the year keeps climbing. Layer 2 still exists in the kernel; the UI does not ask.

We are heading at the **long-watch city picture** (ages, event log, rates, a map that fills toward the painting), not more buttons.


Not pure spreadsheet. Not pure action game.  
**Lab engine first → watchable game → optional learning agents on the same rules.**

---

## Where we are (2026-08-19)

The old “not playable yet” list is done:

1. Stop time at a decision — shipped (hidden)
2. Pick one thing that hurts something else — shipped (hidden)
3. See a rival doing the same — shipped
4. Read the map as a place — started (v10 districts, plaza, farm rows). **Not the painting yet.**

Engine is roughly **80% of a Civ-shaped kernel**. Watch is roughly **30% of the painting**.  
The remaining product is not more victory conditions. It is **volume, labour, and a late game that still changes after Observatory**.

Seed 42 still tells the story: east holds science ~Year 708, west has more people, both sit in city + observatory, then thousands of years of raids and food. That late sit is the hole.

---

## Goals

### Near-term (watch)
- City picture denser toward the painting (building volume, districts, streets)
- Hour-scale clock you can leave running
- After the science hold, the map must still grow

### Mid-term (depth on the same kernel)
- Richer mid/late after Observatory (discoveries are the first sink — they should leave a mark)
- Military / raid depth worth caring about over long horizons
- Specialisation identities you can **see** (craft / organisation / strategy / inquiry)

### Longer vision
- Visible haul labour (Settlers) — people and paths, not villager micro
- Science labs → physics-style experiments / tech unlocks
- Later-age civic density (not a Civ modern-era dump)
- Learning agents that improve inside the same deterministic rules
- Playable governor layer stays on the kernel — unhide only after the watch is a painting

### Non-goals (for now)
- Perfect balance for human multiplayer
- Replacing the utility agent with RL immediately
- DESIGN.md as a patch checklist (ledger owns status)
- Cloning Civ 6/7 systems (religion, tourism, great people, hex unit combat, 20 unique civs)
- Unhiding edicts to “make it a game” while the map is still a glyph board

---

## Intent

Deterministic multi-agent civilisation lab → watchable Settlers × Civ hybrid.  
Logs = animation pipeline. Ages progression. Learning agents later.  
One simulation kernel; lab and human UI are layers on top.

The utility agent is the **hands**. The human (later) is the **brain**.  
Do not micro villagers. Do not replace the kernel to “feel more like Firaxis.”

---

## The painting vs the grid

The concept art is the look we are walking toward: a living town, mixed roof sizes, farm animals, river, smoke, people on paths.

The grid is 32×32. We will never paste that painting onto tiles. We steal:

- **Volume** — many roofs, not one hut per town
- **Edge** — farms and trees meet the city, not a hard square of yards
- **Labour** — dots that read as people with jobs
- **River as a place** — water already exists; boats / shore work later
- **Two palettes that become two cultures** — west pale wood, east clay, then craft vs inquiry should split the skyline

If a patch does not move the map toward that, it is not a watch patch.

---

## Current content shape (vision, not checklist)

**Survival → specialisation → science → civic life**

- Early: farms, storage, food pressure
- Mid: workshop → barracks → civic chain → academy / subjects
- Era 4: subject buildings (irrigation, library, foundry, hall, command)
- E5: Lab → Observatory → discoveries (knowledge sink → permanent farm bonus)
- **After the hold (missing):** the city keeps filling. Discoveries, foundry, hall, command, walls, roads, extra housing should read as a skyline, not a HUD chip.

Guns-vs-butter remains core: soldiers help raids/defend but always cost food; soft-cap vs population.

---

## The Civ spine we already have

Civ 6/7 are not “more buildings.” They are: a human makes a few costly choices, time moves, the world pushes back, and you can see it.

This project already has the spine those games sit on:

| Civ feeling | AI-world equivalent |
|---|---|
| Found / grow a city | Settlements, pop, food pressure, starve |
| Ages | Era 2 → 4 |
| Tech / civics | Subjects: agriculture, craft, organisation, strategy, inquiry |
| Districts / chains | Farm → workshop → barracks → civic → academy |
| Science victory line | Library → Lab → Observatory → discoveries |
| Guns vs butter | Soldiers cost food every tick |
| Production | Agents + settlement stocks + build gates |
| Replay / seed | Deterministic logs, seed-controlled runs |
| Watch | Dual age ribbon, chronicle, rival on one map |

A broken science path is not a game. Multi-seed reachability (era 4 + Library + Lab + Observatory) is the floor. That floor is shipped.

---

## Playable path (Settlers × Civ, not a Civ clone)

### The product

The human is the **spirit of the settlement**. Villagers keep walking. You do not micro A0.

You only get decisions when the world asks. Agents execute. Logs already are the animation.

That is Settlers to look at, Civ to decide.  
Closer to Civ 7’s ages + crises than to Civ 6’s 400-click city screens. The tick engine wants **few, fat choices** — not a production queue of 40.

Watch-first means: the documentary is the face. Playable is the spine underneath. Do not surface 3 buttons until the map is worth sitting with.

### Choices that map onto systems we already have

- **Age up:** unlock Inquiry *or* Strategy. Not both for free.
- **Next build class:** Library / Foundry / Command / more farms. One slot.
- **Army:** raise soldiers (food tax goes up) or disband.
- **Discovery:** take the farm bonus *or* bank knowledge for the next one.
- **Crisis:** drought — ration, or keep growing and risk starve.

Every choice must be able to hurt (rule 5).

### What not to steal from Civ 6/7

Do **not** add religion, tourism, great people, diplomatic quarter, 20 unique civs, hex combat with 8 unit classes.

Those games are huge because they sell 100 hours. This is a 32×32 deterministic lab. Their surface would break the kernel.

Steal only this:

- Ages change the rules (we have this)
- One visible rival (Layer 3 — west / east, own governor, cross-faction raids)
- A victory you can point at (win / lose clock: science, wipe, or hold)
- Presentation that makes stocks feel like a city (watchable map + chronicle)

---

## Three layers. Ship in this order.

```
Now (lab)          Playable              Civ-shaped
─────────          ────────              ──────────
kernel             pause on decision     rival civ on same map   ← shipped
utility agents     governor choices      raids become someone    ← shipped
logs/snapshots     watchable map         win / lose clock        ← shipped
```

**Layer 1 — Watchable (shipped, still thin)**  
Paced god-view: one screen, events as sentences. v10: river, forest clumps, district radius, plaza, farm rows, west/east skins. Still a board. The painting is the remaining work.

**Layer 2 — Steerable (kernel shipped, UI hidden)**  
Pause. 3 buttons. No typing `focus food`. Human only biases the next goal. Same seeds, same agents, same rules. Stay hidden until Layer 1 looks like a city.

**Layer 3 — Contested (shipped)**  
Second civ on the same map, far side, own governor. `rival_agents=0` is the default so validate RNG is untouched. Edicts only move your people. Science gates and deposits are own-faction. When two factions exist, raids are strongest-of-one vs weakest-of-the-other — not weather.

Do not pile civic / hunger / age-up on top of this. One axis at a time.

### Win / lose (shipped)

- **Science:** your Observatory + 2 discoveries, first
- **Domination:** the other civ’s pop hits 0 after both have founded
- **Survival:** clock ends — era 4 and more people, or they outgrew you / you never reached era 4

Watch uses `soft_outcome=True`: first hold is a headline, sim runs to the clock.  
Validate stays `soft_outcome=False`. `rival_agents=0` still runs the full tick count.

That is a short Civ. That is enough victory. Do not add more win types to make it feel finished.

---

## Long-term axes (propose, then one at a time)

Ranked by how much they move the watch toward the painting. Approve one. Do not start two.

### 1. Civic volume after the hold *(highest — this is the empty late game)*

After Observatory the skyline freezes. Foundry / hall / command / walls / extra huts / roads already exist in the kernel; they do not read as a city. Each discovery should leave a mark (garden, wing, tower), not only `+0.08` farm. Presentation first if the structures already spawn; kernel only if they do not.

This is the ledger’s “more building volume toward the concept painting.”

### 2. Hour sit

Default clock long enough to leave in the corner. Named chapters (Camp → Town → City → After the hold). Soft outcome already lets Year 708 be a card, not an ending. Do not add a new victory. Just more years of the same rules, with axis 1 filling the map.

### 3. Visible labour

Agents as jobs: farmer, hauler, soldier. Paths from field to plaza. Smoke on workshops. No click-to-move. Settlers to look at, still Civ to decide.

### 4. Two peoples, not two palettes

West pale / east clay is a start. Specialisation should split the skyline: inquiry towns grow library/lab/observatory mass; strategy towns grow barracks/command/walls; craft grows foundry/workshop. Same kernel, different governor bias made visible.

### 5. Raid as a war you can watch

Cross-faction raids exist. They should read as a season (a year of raids in the log, a scar on a district), not a one-line “East raided s3.” Depth later; naming and map mark first.

### 6. Playable face *(after the painting)*

Unhide the three edicts only when sitting with the watch is already good. Do not use buttons to paper over a thin map.

### 7. Learning agents *(last)*

Same deterministic rules. Logs are the dataset. Do not fork the sim.

---

## God-view

`--play` auto-steps snapshots with key event callouts.  
Icons: C academy | # walls | ~ irrigation | L library | Y foundry | O hall | X command | R lab | V observatory

Web Watch is the god-view people actually see.

---

## Memory Space

Long-term answers live there across chats (product, contracts, next axis). If a new chat is stuck, search Memory Space before inventing a second product. Propose new north-star items there as well as here.

If Memory Space is not shared with the agent, DESIGN.md + PATCH_LEDGER.md + CANVAS.md are the fallback.

---

## Dev rules

1. Determinism sacred  
2. One axis at a time  
3. Logs first  
4. Min tokens while usage high  
5. Choices must be able to hurt  
6. Ledger = status; DESIGN = vision  
7. Utility agent stays the hands; human is the brain  
8. Playable layer sits on the kernel — do not fork the sim to make a game  
9. Watch patches must move the map toward the painting, or they are not watch patches  
