# AI-world Design Notes (Internal)

**Last updated:** 2026-09-11  
**This file is vision.** Status, restore, jobs → [PATCH_LEDGER.md](PATCH_LEDGER.md).

---

## Standing destination (what the builder heads for)

**Finish the sit so the island reads as the painting. Then paint. Never paint a camp.**

The painting is one island, left-to-right through time: fields and a small town → mill, wheel, mill-race, rail spine → brick works and a civic square → a skyline and a working waterfront. This canvas will never match that lighting. It must match that **structure** before any graphics pass.

Every hop answers: *does the island read more like that picture, as a place with a race in it?* If the hop is only prettier letters, skip it. If the hop skips an era, skip it. If the hop turns edicts on to hide a missing sit, skip it.

Watch stays solid. The kernel stays one. The human is the brain later. Hands walk now.

---

## The law: sit, then graphics

Order is locked. Owner stamps pins. Edicts are open as of **v56** — you govern the west when the world asks. Seed 42 east science hold stays **Year 343**.

| When | Axis | What “done” looks like |
|---|---|---|
| Done · v55 | **A. Eras last** | Industry and world cannot skip. Science hold seed 42 stays **Year 343**. Aging 4→5 and 5→6 **costs food**. Mill must be live. Dwell after the science sit. |
| Done · v56 | **B. Playable governor** | Pause. 3 fat choices that hurt. No `focus food`. Same kernel. You govern the west; east/north/south keep their own heads. |
| Live · v57 | **C. Hotel / rail as rules** | Train is labour mill→warehouse. Hotel: gold in, food+goods out. Stickers die. Empty towers earn nothing. Spine you can point at. |
| Live · v58 | **Districts you can name** | Park W and read housing / fields / spine / civic / water. Folk drops lab IDs. Empty granary reads. Names earned from the sit — no typing. |
| Live · v59 | **Graphics pass** | Turquoise water, cream shore, olive canopy, mill-race glint — on the finished sit. The painting is the brief for structure, not lighting. |
| Later | **Late starve honest** | World city doesn’t silently die. Food still kills. A full skyline can still go hungry. |
| Later | **Crown that reads** | One island king: taller, a banner, a name. Bonus you can lose. Head worth taking. |
| Later | **Memory-app agents** | Walkers get clever on the same rules. Watch stays solid first. Do not drop brains on a camp. |

Do not clone Civ religion, hex armies, 20 unique civs. Steal feelings: Civ 7 age-crisis, Anno chains, Frostpunk districts, Storm’s 3 buttons, Banished food-as-death, Settlers haul, SimCity skyline.

---

## Horizon (parked until the sit can carry it)

These are real. They are not this pin. Do not pull them forward to look busy.

- **Gold as a purse.** Trade, tribute, a reason to raid besides food. Food still kills. Coin is not a starve-skip.
- **Buried temples / hidden pyramids.** Late, found in the dirt, berms around them. Mystery on the island, not a camp hut with a new letter.
- **Sit that feels like physics.** Weight, mill-race, haul that takes time. Same kernel. After the civ race is real.
- **Event popups on iso.** Glyphs stay; a short slip that names the moment (already started). Popups are the next read, not a second UI.
- **Traffic as a living city.** Taxi on the square, bus hall→warehouse→field, planes on the spine. After C, they are labour, not parade.
- **One rival you can see thinking.** Own governor, cross-faction raids, stolen science. `rival_agents=0` still exists so validate RNG is untouched.
- **Win you can point at.** Science (obs + 2 discoveries), wipe, survival clock, or hold the island crown.

Do not open a second kernel to “feel more like Firaxis.” Do not add buildings to fake a finished game.

---

## What we steal (looked up 2026), what we do not

The painting is still the destination. Other games are feelings, not a feature list.

| Steal this feeling | From | Do not steal |
|---|---|---|
| Ages that change the rules; a sit between them | Civ 7 age system, Millennia | Hex armies, religion, tourism, 20 unique civs, 400-click city screens |
| Few laws that hurt someone | Frostpunk 2 districts + laws | A full political sim, faction meters as chrome |
| 3 buttons, a crisis clock | Against the Storm | Roguelite reset, randomised blueprint soup |
| Chains you can see: mill → warehouse | Anno 1800 / 117 | 40-step production trees, island-hopping trade empires |
| Food stockpile; pop is resource and liability | Banished | Happiness spreadsheets, no-war-ever |
| Haul labour, buildings that feel alive | The Settlers / The Colonists | Micro every villager |
| Districts + traffic as a place | SimCity / Cities: Skylines | Zoning tools, utility-layer micromanagement |
| Organic read of a town | Manor Lords | Precision medieval logistics as the game |

If a hop would make this a clone, push back. If a hop would skip the sit to chase art, push back.

---

## Builder standing rules

These survive chats. They are how the destination is kept.

1. **Look up live facts.** Versions, bots, pins, “does X exist” — search, don’t recap Memory Space.
2. **Push back.** Skip-an-era, edicts-as-paint, Vite, shrinking the map, buff-only rules, art-before-sit — say no.
3. **Research other games** when picking a hop. Steal a feeling, not a system.
4. **Discuss product.** The owner is building a game, not a file tree. Talk in sits, eras, and the painting.
5. **One axis at a time.** Ledger = jobs + pin. DESIGN = vision. Do not stamp. Pin stays until the owner says stamp.
6. **Year 343 does not move.** Seed 42, east science hold, observatory + 2 discoveries. Soft outcome; Watch continues.
7. **You govern the west.** Edicts are a turn, not a cheat box. No typing `focus food`. East/north/south keep their own heads. Year 343 is east’s science hold — a west pick must not move it.
8. **Never Vite.** The canvas is `play_web` on the preview. Iso is the map.

---

## Vision (look & feel)

**The Settlers** for human play: top-down (iso camera), resource chains, haul labour, buildings that feel alive, watching a settlement grow.

**Civilization** for structure: ages, subjects/tech, long-horizon choices, guns-vs-butter tension.

**SimCity** for the late picture: districts you can read, streets, traffic, a city that looks like a place.

**Research lab** underneath: fully deterministic, seed-controlled, every decision logged. Logs become the animation / god-view pipeline. Humans watch or steer; later agents learn.

Not pure spreadsheet. Not pure action game.  
**Lab engine first → watchable city → industry → world city → optional learning agents on the same rules.**

The utility agent is the **hands**. The human (later) is the **brain**.  
Do not micro villagers. Do not replace the kernel to “feel more like Firaxis.”

---

## The picture (what you should see)

Four peoples on one island — west / east / north / south, inland camps, poles filling toward the middle.

**Land.** A 96×96 island you can sit with. Water is a lake (flat), shore is sand, grass has lift, fields stripe, roads sit low, trees have canopy. Grain stays dirt. Streets stay streets. **Rail is the spine** — avenue plus the line city ↔ mill ↔ warehouse — not a carpet.

**City.** Districts you can read: housing, civic, industry, fields, military. Houses pitched off the rail. Hall with a roof. Barn. Warehouse shed. Mill tower + wheel; mill-race to the water; a dry mill sits dark. Temple is stone and flame, not a hut. One pyramid a pole — found in the dirt, berms around it. Harbour: quay and boats on the water at a mill.

**Hands.** Ten walkers a pole. They are labour, not kings.

- Settlement — breed toward the cap
- Town — one walker raised to **knight** (raids, guard)
- City — that knight (or one child) raised to **king**. Local crown. Hall is the seat
- Science — **scribe** walks library / lab / observatory; **builder** walks hall / foundry / workshop

Paint is not rank. One walker is knighted, then crowned.

**Industry.** After science: mill on water is live power. Train + rail crew haul wood mill → warehouse. Foundry and mill tools only when the mill is live.

**World city.** After the wonder: airport + runway. Planes cross the island. Taxi loops the square. Bus runs hall → warehouse → field. Hotel towers and highrises when the people are many — a skyline, not a camp.

**Camera.** Iso is the map. Park W / E / N / S / Island. Island fits; scrollbar stays.

**Watch, not cheat.** Edicts exist in the kernel and stay hidden until the map is a place worth deciding on.

---

## Civ, not a pile of cheats

Snapshot 2026-08-25. This is the game. Not more buildings. Not more buttons.

**Every new rule should hurt as well as help.** If it only buffs, it is a cheat. Do not ship it.

**One true king.** Four peoples, four local crowns as rank — but **one island crown**. That people get a bonus: order, haul, raid. Everyone else wants that head. Kill the king, the bonus dies with him. A crown you cannot lose is paint.

**Stolen science.** A raid can rip a discovery off the next city. Soldiers pay. You can snatch the lab and come home thinner. The race gets nasty. Science is not a private high score.

**Then (later, not now):**

- **Gold** — a purse. Trade, tribute, a reason to raid besides food. Food still kills. Do not replace starvation with coin.
- **Temples / hidden pyramids** — late, buried, found. Not a camp hut with a new letter. Mystery on the island, not another early build.
- **Sit that feels like physics** — the lab end. Experiments, weight, the world pushing back. Same kernel. After the civ race is real.

Not all at once. One axis. Ledger jobs are the queue.

---

## The route (eras)

Each era must **last**. It is a finished sit that *leads into* the next — not a skip. Ship an era as a complete picture, then unlock the next.

| Era | Name | What you should see |
|---|---|---|
| Camp | Walkers, no hearth | Hands, empty land |
| Settlement | First hut, shared stock | A hearth, a yard |
| Town | Workshop + barracks | Streets starting, a camp |
| City | Academy + inquiry | Districts, houses, fields, food chain |
| Science | Library → lab → observatory | Knowledge buildings, discoveries, a *hold* |
| Industry | Rail, mills, warehouse, pyramid | Trains. Goods on the spine. Live mill. A pyramid in the dirt |
| World city | Airports, taxis, buses, hotel towers | Planes. Cabs on the square. A skyline when the city is full |

You do not jump to airports. Rail is the spine. Airports sit on the spine.

### Still to finish in that picture

- **Uni / bars as real buildings** — academy stands in for the uni; market stands in for the bar. Iso already has mass; keep them in civic.
- **Housing / civic / industry / green** — named as of v58; keep the clusters honest
- Late sits that don’t silently starve and stall

### After the city can carry it

1. **Eras last** — v55. Hurt to leave science/industry.
2. **Playable governor** — v56. Pause, 3 fat choices, no typing `focus food`
3. **Hotel / rail as rules** — live v57. Gold in, food+goods out; train is haul. Empty towers earn nothing.
4. **Districts you can name** — live v58. Park W. Housing, fields, spine, civic, water. Empty granary reads. No rename box.
5. **Graphics pass** — live v59. Turquoise water, cream shore, olive canopy. Sit first, then this paint.
6. **Late starve honest** — a world city can still go hungry
7. **Crown that reads** — banner, name, a head you can lose
8. **Memory-app agents** — walkers get clever, same rules. Watch must stay solid first

Do not drop clever agents onto a camp with letters. Do not open edicts to paper over a missing race.

---

## Goals

### Near (city that plays like a city)

- Districts you can read
- Food chain you can see: farm → granary → souls
- Streets as a network (they become rail in industry)
- The iso sit holds: terrain, roofs, figures, houses off the rail
- One island crown that matters. Science that can be stolen.

### Mid (industry depth)

- Uni / bars as real buildings, not stand-ins
- Power / mill-race / warehouse still feel like work, not stickers

### Longer (world city + agents)

- Gold as a purse (food still kills)
- Buried temples / hidden pyramids
- Sit that feels like physics
- Traffic that reads as a living city
- Learning / memory-app agents inside the same deterministic rules
- Playable layer on the kernel — do not fork the sim to make a game

### Non-goals (for now)

- Perfect balance for human multiplayer
- Replacing the utility agent with RL immediately
- DESIGN.md as a patch checklist (ledger owns jobs)
- Cloning Civ 6/7 systems (religion, tourism, great people, hex unit combat, 20 unique civs)
- Airports before rail
- Clever agents before hands
- Fake kings painted as 2×2 blocks
- Buff-only rules (cheats)

---

## Current content shape (vision, not checklist)

**Survival → specialisation → science → industry → world city**

- Early: farms, storage, food pressure
- Mid: workshop → barracks → civic chain → academy / subjects
- City: irrigation, library, foundry, hall, command
- Science: Lab → Observatory → discoveries (knowledge sink → permanent farm bonus)
- Later: rail, wonders, harbour, airports, traffic
- The race: one island crown, stolen science, then gold / buried temples / physics

Guns-vs-butter remains core: soldiers help raids/defend but always cost food; soft-cap vs population.

---

## The Civ spine we already have

Civ 6/7 are not “more buildings.” They are: a human makes a few costly choices, time moves, the world pushes back, and you can see it.

| Civ feeling | AI-world equivalent |
|---|---|
| Found / grow a city | Settlements, pop, food pressure, starve |
| Ages | Camp → city → science → industry → world |
| Tech / civics | Subjects: agriculture, craft, organisation, strategy, inquiry |
| Districts / chains | Farm → granary → souls. Workshop → foundry. Civic square |
| Science victory line | Library → Lab → Observatory → discoveries |
| Guns vs butter | Soldiers cost food every tick |
| Production | Agents + settlement stocks + build gates |
| Replay / seed | Deterministic logs, seed-controlled runs |
| Hegemony | One true king — bonus on that people, head worth taking |
| Espionage / war | Stolen science — raid rips a discovery, army comes home thinner |

A broken science path is not a game. Multi-seed reachability (era 4 + Library + Lab + Observatory) is the floor the playable layer stands on.

We are roughly **70% of a Civ-shaped engine** and **15% of a game**.  
The remaining game is not more buildings. It is decisions, a watchable city, one rival, and win/lose.  
Buildings that *arrive later* are eras, shipped as upgrades, each one a finished sit.

---

## Why it was not playable (and what v56 opened)

The utility agent is still the hands. The human is the brain — only when the world asks.

As of v56 a human can:

1. **Stop time** at a fat moment (town, city, inquiry, discovery, drought)
2. **Pick one thing** that hurts something else — three buttons, hurt written on them
3. **See a rival** doing the same (east/north/south keep their own governors)
4. **Read the map** as a place, not a table — still not a painting. Good enough to decide on.

You do not type `focus food`. You do not micro A0. Edicts are a turn.

Four local kings is not a civ. One island crown is.

---

## Playable path (Settlers × Civ, not a Civ clone)

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
- **Crown:** hold the island king, or hunt him. Bonus vs a target on your back.
- **Raid:** steal a discovery and bleed, or come home empty.

Every choice must be able to hurt.

### What not to steal from Civ 6/7

Do **not** add religion, tourism, great people, diplomatic quarter, 20 unique civs, hex combat with 8 unit classes.

Those games are huge because they sell 100 hours. This is a deterministic island lab. Their surface would break the kernel.

Steal only this:

- Ages change the rules
- One visible rival (own governor, cross-faction raids)
- A victory you can point at (science, wipe, hold, or the island crown)
- Presentation that makes stocks feel like a city

---

## Three layers

```
Lab                 Playable              Civ-shaped
─────────           ────────              ──────────
kernel              pause on decision     rival civ on same map
utility agents      governor choices      raids become someone
logs/snapshots      watchable map         win / lose clock
```

**Layer 1 — Watchable**  
Paced god-view: one screen, events as sentences. Districts, food chain, chronicle, iso sit.

**Layer 2 — Steerable (this is the game)**  
Pause. 3 buttons. No typing `focus food`. Human only biases the next goal. Same seeds, same agents, same rules. Not open while the sit is the work.

**Layer 3 — Contested**  
Second civ on the same map, far side, own governor. `rival_agents=0` is the default so validate RNG is untouched. Edicts only move your people. When two factions exist, raids are strongest-of-one vs weakest-of-the-other — not weather.

### Win / lose

- **Science:** your Observatory + 2 discoveries, first
- **Domination:** the other civ’s pop hits 0 after both have founded
- **Survival:** clock ends — era 4 and more people, or they outgrew you / you never reached era 4
- **Crown (heading):** hold the island king when the clock ends — or take his head

Early stop on science or wipe only when a rival is on the map.  
Validate still runs the full tick count.

That is a short Civ. That is enough. Do not add more buildings to make it feel finished. **Do** add later *eras* as upgrades when the city picture can carry them.

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
5. Choices must be able to hurt. Every new rule hurts as well as helps. Buff-only is a cheat.
6. Ledger = jobs + pin; DESIGN = vision
7. Utility agent stays the hands; human is the brain
8. Playable layer sits on the kernel — do not fork the sim to make a game
9. Each era is a finished sit that leads into the next (DLC / upgrade workflow)
10. Rail before airports. City before clever agents. Hands before world city. Crown before gold.
11. Paint is not rank. Four walkers cannot run a world city. Hands grow.
12. Look up live facts. Push back. Research other games. Discuss product.

---

## Locked spine

Do not invent a different one.

- **Four tribes.** West, east, north, south. Same island.
- Start **10 walkers a side.** Labour, not kings.
- People age: camp → settlement → town → city → science → industry → world.
- Walkers evolve on that same path (breed, knight, king, scribe, builder).
- Grow toward **8–10 hands a side by city.** Watch starts at the cap.
- One **local** crown a side when earned (rank). Destination: **one true king** on the island — bonus on that people, head worth taking. This is the hook: one head that matters. Later: make that crown clearer on the map (taller, a banner, a name) without turning it into a cheat.
- **Iso** is the sit. Grid is backup.
- Edicts stay in the kernel, hidden, until Layer 2 opens.

Later sit (not this pin): little **event popups** on iso — look at other games when we pick that hop. Glyphs stay; popups are the next read. Gold, temples / hidden pyramids, sit that feels like physics — still parked.

