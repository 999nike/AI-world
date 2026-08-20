# AI-world Design Notes (Internal)

**Last updated:** 2026-08-20  
**Content ceiling (built):** Era 6 world city (airports, taxis, buses)  
**Content ceiling (vision):** sit + optional learning agents on the same rules

---

## Vision (look & feel)

**The Settlers** for human play: top-down, resource chains, haul labour, buildings that feel alive, watching a settlement grow.

**Civilization** for structure: ages, subjects/tech, long-horizon choices, guns-vs-butter tension.

**SimCity** for the late picture: districts you can read, streets, traffic, a city that looks like a place.

**Research lab** underneath: fully deterministic, seed-controlled, every decision logged. Logs become the animation / god-view pipeline. Humans watch or steer; later agents learn.

**Current product (2026-08-20):** watch-first. **Four peoples** (west / east / north / south), 10 hands a pole. Human edicts are **hidden**, not deleted. Default web run is `playable=False`, paced god-view. World city is on the canvas (**· v29**). Memory-app agents tried as v30 and **reverted**.

Not pure spreadsheet. Not pure action game.  
**Lab engine first → watchable city → industry → world city → optional learning agents on the same rules.**

---

## The route (eras)

Each era must **last**. It is a finished sit that *leads into* the next — not a skip. That is the upgrade / DLC workflow: ship an era as a complete picture, then unlock the next.

| Era | Name | Built? | What you should see |
|---|---|---|---|
| Camp | Walkers, no hearth | yes | Four hands, empty land |
| Settlement | First hut, shared stock | yes | A hearth, a yard |
| Town (3) | Workshop + barracks, 15 souls | yes | Streets starting, a camp |
| City (4) | Academy + inquiry, 20 souls | yes | Districts, houses, fields, food chain |
| Science | Library → lab → observatory | yes | Knowledge buildings, discoveries, *hold* |
| **5 Industry** | Rail, mills | **yes** | **Trains.** Goods move on lines. Mills and foundries work. Roads become rail. |
| **6 World city** | Airports, taxis, buses | **yes** | **Planes.** Cabs on the square. Buses on the spine. |

### What belongs in those later eras (not now)

- **Streets, bars, unis** — academy stands in for the uni until 5; market is the bar on the street
- **Pyramids / wonders** — one fat landmark per people, era 5+
- **Trains** — era 5 spine. Roads we paint now *become* rail
- **Planes / airports** — era 6, sit on the rail spine
- **Taxis, buses** — era 6 traffic, the city feels busy as fek
- **Housing / civic / industry / green districts** — started in the city picture, finished in 5–6

You do not jump to airports. Rail is the spine. Airports sit on the spine.

### What comes after the city can carry this

1. Memory-app agents — walkers get clever, same rules
2. More peoples — four tribes or four houses, after two tribes look like cities

Do not drop clever agents or extra players onto a camp with letters.

---

## Goals (hand-off)

### Near-term (city that plays like a city)
- Districts you can read (housing / civic / industry / fields / military)
- Food chain you can see: farm → granary → souls. Empty granary reads on the map
- Streets as a network (they become rail in era 5)
- Late sits that don’t silently starve and stall

### Mid-term (era 5)
- Industry: rail, mills, power
- One wonder slot (pyramid / landmark)
- Uni / bars as real buildings, not stand-ins

### Longer (era 6 + agents)
- Airports, highways, taxis, buses
- Learning / memory-app agents inside the same deterministic rules
- More peoples on the same island
- Playable governor layer (edicts still exist in the kernel)

### Non-goals (for now)
- Perfect balance for human multiplayer
- Replacing the utility agent with RL immediately
- DESIGN.md as a patch checklist (ledger owns status)
- Cloning Civ 6/7 systems (religion, tourism, great people, hex unit combat, 20 unique civs)
- Airports before rail

---

## Intent

Deterministic multi-agent civilisation lab → watchable Settlers × Civ × SimCity hybrid.  
Logs = animation pipeline. Ages progression. Learning agents later.  
One simulation kernel; lab and human UI are layers on top.

The utility agent is the **hands**. The human (later) is the **brain**.  
Do not micro villagers. Do not replace the kernel to “feel more like Firaxis.”

---

## Current content shape (vision, not checklist)

**Survival → specialisation → science → industry → world city**

- Early: farms, storage, food pressure
- Mid: workshop → barracks → civic chain → academy / subjects
- Era 4: subject buildings (irrigation, library, foundry, hall, command)
- Science: Lab → Observatory → discoveries (knowledge sink → permanent farm bonus)
- Later: rail, wonders, airports, traffic

Guns-vs-butter remains core: soldiers help raids/defend but always cost food; soft-cap vs population.

---

## The Civ spine we already have

Civ 6/7 are not “more buildings.” They are: a human makes a few costly choices, time moves, the world pushes back, and you can see it.

This project already has the spine those games sit on:

| Civ feeling | AI-world equivalent |
|---|---|
| Found / grow a city | Settlements, pop, food pressure, starve |
| Ages | Era 2 → 4, then science; 5–6 later |
| Tech / civics | Subjects: agriculture, craft, organisation, strategy, inquiry |
| Districts / chains | Farm → granary → souls. Workshop → foundry. Civic square |
| Science victory line | Library → Lab → Observatory → discoveries |
| Guns vs butter | Soldiers cost food every tick |
| Production | Agents + settlement stocks + build gates |
| Replay / seed | Deterministic logs, seed-controlled runs |

A broken science path is not a game. Multi-seed reachability (era 4 + Library + Lab + Observatory) is the floor the playable layer stands on.

We are roughly **70% of a Civ-shaped engine** and **15% of a game**.  
The remaining game is not more buildings. It is decisions, a watchable city, one rival, and win/lose.  
Buildings that *arrive later* (trains, planes, wonders) are eras, shipped as upgrades, each one a finished sit.

---

## Why it is not playable yet

Right now the utility agent is the player. A human watches. Governor text (`focus food`) is a cheat code, not a turn.

A human cannot yet:

1. **Stop time** at a decision
2. **Pick one thing** that hurts something else
3. **See a rival** doing the same
4. **Read the map** as a place, not a table

The first three exist. The map now carries districts, houses, a food chain, and a chronicle in sentences. Still not a painting. Good enough to watch.

---

## Playable path (Settlers × Civ, not a Civ clone)

### The product

The human is the **spirit of the settlement**. Villagers keep walking. You do not micro A0.

You only get decisions when the world asks. Agents execute. Logs already are the animation.

That is Settlers to look at, Civ to decide, SimCity to *see*.  
Closer to Civ 7’s ages + crises than to Civ 6’s 400-click city screens. The tick engine wants **few, fat choices** — not a production queue of 40.

### Choices that map onto systems we already have

- **Age up:** unlock Inquiry *or* Strategy. Not both for free.
- **Next build class:** Library / Foundry / Command / more farms. One slot.
- **Army:** raise soldiers (food tax goes up) or disband.
- **Discovery:** take the farm bonus *or* bank knowledge for the next one.
- **Crisis:** drought — ration, or keep growing and risk starve.

Every choice must be able to hurt (rule 5).

### What not to steal from Civ 6/7

Do **not** add religion, tourism, great people, diplomatic quarter, 20 unique civs, hex combat with 8 unit classes.

Those games are huge because they sell 100 hours. This is a 48×48 deterministic lab. Their surface would break the kernel.

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

**Layer 1 — Watchable (shipped)**  
Paced god-view: one screen, events as sentences. Districts, food chain, chronicle. The web map is this layer.

**Layer 2 — Steerable (this is the game)**  
Pause. 3 buttons. No typing `focus food`. Human only biases the next goal. Same seeds, same agents, same rules.

**Layer 3 — Contested (shipped)**  
Second civ on the same map, far side, own governor. `rival_agents=0` is the default so validate RNG is untouched. Edicts only move your people. Science gates and deposits are own-faction. When two factions exist, raids are strongest-of-one vs weakest-of-the-other — not weather.

Do not pile civic / hunger / age-up on top of this. One axis at a time.

### Win / lose (shipped)

- **Science:** your Observatory + 2 discoveries, first
- **Domination:** the other civ’s pop hits 0 after both have founded
- **Survival:** clock ends — era 4 and more people, or they outgrew you / you never reached era 4

Early stop on science or wipe only when a rival is on the map.  
`rival_agents=0` still runs the full tick count. Validate is untouched.

That is a short Civ. That is enough. Do not add more buildings to make it feel finished. **Do** add later *eras* as upgrades when the city picture can carry them.


### First playable patch (done)

Pause the sim → show 3 choices → apply one governor bias → resume.  
Same seeds. Same multi-seed validate. Then it started being a game.

---

## God-view

`--play` auto-steps snapshots with key event callouts.  
Icons: C academy | # walls | ~ irrigation | L library | Y foundry | O hall | X command | R lab | V observatory

God-view is the watchable layer. It is not the playable layer until it can pause and accept a choice.

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
9. Each era is a finished sit that leads into the next (DLC / upgrade workflow)  
10. Rail before airports. City before clever agents. Two tribes before more peoples.  
11. Four walkers cannot run a world city. Hands grow. One walker is knighted, then crowned. Paint is not rank.

---

## Locked plan (2026-08-19) — do not invent a different one

**Confirmed with the owner. This is the spine. Next chat starts here.**

Four bots cannot run a major city, trains, or an airport. Today the eight walkers are the only bodies. Souls and soldiers are numbers painted as houses and tents. A sim that wants to feel like the age it’s in must grow **hands**, not just the score.

### For now (gameplay solid)

- **Four tribes.** West, east, north, south. Same 48×48 island.
- Start **10 walkers a side.** They are labour, not kings.
- The **people** still age: camp → settlement → town → city → science.
- The **walkers evolve** on that same path:
  - Settlement — they **breed** up to the cap when a side starts smaller. Watch starts at the cap.
  - Town — one walker can be raised to **knight** (raids, guard). The others stay labour.
  - City — that knight (or one child) can be raised to **king**. **Government** starts (hall, one crown).
  - Science — specialists (scribe, builder). Same people, new jobs.
- Grow toward **8–10 hands a side by city.** Watch now **starts at 10.**
- v17 gold/silver “kings” are **paint only**. Undo that lie when rank is real. One crown a side, when earned.

### Later (not this next patch)

- Memory-app agents (smarter walkers, same rules) — **v30 reverted**, watch must stay solid first
- Playable governor / edicts still exist in the kernel; UI stays watch-first until we open them

### Sit (canvas, still · v29 — not a new era)

Uni / bars painted as buildings. Housing / civic / industry / military / fields. Corner poles fill inward. Camera W/E/N/S.

### Art pass (canvas, still · v29)

Same 48×48 kernel. CSS tiles: grass, water, roofs, mill-wheel, warehouse, runway. Building letters off. Walkers stay dots.

### Sprites (canvas, still · v29)

Train / cab / bus / plane are shapes that face the move. Live mill spins. No new rules. Walkers still dots.

### What this is not

- Not 2×2 fake kings + villagers (v17 paint).
- Not 4 walkers forever.
- Not airports before rail. Not clever agents before hands.

### Shipped v18 — hands + knight

Hands breed with population (cap 10). One knight a side at town + barracks. Fake king paint removed.

### Shipped v19 — king + hall government

City era crowns one king a side (the knight if they exist). Capital tagged government. Hall is the seat when it rises. Event log is wired to last_breed / last_knight / last_king.

### Shipped v20 — science specialists

Library names one **scribe** and one **builder** a side from existing walkers. Scribe walks to library / lab / observatory. Builder walks to hall / foundry / workshop. Same 10-hand cap. Paint and city panel follow `role`. Seed 42 east science is **Year 382** (specialists pull two hands toward their seats).

### Shipped v21 — north / south poles

Four peoples, four corners, same 48×48 island. West / east / north / south. Each starts 4 walkers, breeds to 10, same ranks (knight, king, scribe, builder). Watch stamp **· v21**. `pole_agents=0` keeps the two-tribe kernel. Seed 42 east science is **Year 354**.

### Shipped v22 — 10 a side

Watch starts **10 walkers a pole** (40 hands on the island). Cap stays 10. Two-tribe `num_agents=4` still breeds up. Stamp **· v22**. Seed 42 east science is **Year 342**.

### Shipped v23 — industry trains

After observatory a **mill** can rise. Mill + city → era 5. Streets become rail. One **rail crew** and one **train** a pole. Train walks the towns and mill, hauls a little wood. No RNG. Stamp **· v23**.

### Shipped v24 — rail spine

Industry sit. Rail is only the avenue and the line city ↔ mill ↔ other industry towns. Streets stay streets. Grain roads stay dirt. Trains already walk that spine. Stamp **· v24**.

### Shipped v25 — mill power

Mill on water (or irrigation, reach 4) is **live**. Power on the city. Foundry and mill tools only when live. Train loads only at a live mill. Mill-race painted to the water. Dry mill sits dark. Stamp **· v25**. Seed 42 hold stays **Year 342**.

### Shipped v26 — warehouse

After mill + 2 discoveries a **warehouse** can rise. Train loads at a live mill and drops at **W**. Goods sit on the spine. Stamp **· v26**. Seed 42 hold stays **Year 342**.

### Shipped v27 — wonder

One **wonder** a pole after warehouse + 3 discoveries. Fat landmark (3×3 pyramid). Stamp **· v27**. Seed 42 hold stays **Year 342**.

Industry sit is finished: mill, power, rail, warehouse, wonder.

### Shipped v28 — airports

After a wonder, one **airport** a pole. Planes fly the island (2 tiles a tick, no RNG). Runway painted. Era 6 **world**. Stamp **· v28**. Seed 42 hold stays **Year 342**.

### Shipped v29 — taxis / buses

After the airport, one **taxi** loops the square and one **bus** runs hall → warehouse → field. No RNG. Stamp **· v29**. Seed 42 hold stays **Year 342**.

World city sit: planes, cabs, buses.

### Reverted v30 — memory walkers

Labour walkers remembering resource tiles. JS syntax error in map paint blanked the watch (HUD, seed, map never ran). **Fully reverted.** Live stamp back to **· v29**. Do not re-land until script-checked.

### Restore pin (do not lose this)

**Name:** `v29-safe` · alias **2.9**  
**Repo:** `999nike/AI-world` · branch `v29-safe`  
**Commit:** `7e3cbfdd66dd69cdd296f5d00528c28d74afd7e5`  
**Stamp:** **· v29**  
**Date:** 2026-08-20  

Sit + art pass + painted sprites are on this pin (canvas). Kernel land is still the world-city pin.

Next chat: restore **v29-safe**, not v19-safe, not main. **Start the game (Layer 2)** — see PATCH_LEDGER locked next. Pause, 3 edict buttons, resume. Not memory. Not a new era.

Old pin `v19-safe` / `5ce0355` is king+hall only. Keep it as archaeology, not as the restore.

### Next patch (when a new chat picks it up)

Sit with the world city. Memory-app agents broke the watch (v30 reverted). Uni / bars if the sit still needs them. Not a new era.
