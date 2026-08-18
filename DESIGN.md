# AI-world Design Notes (Internal)

**Last updated:** 2026-08-18  
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
- Playable governor layer on the same kernel (see Playable path)

### Non-goals (for now)
- Perfect balance for human multiplayer
- Replacing the utility agent with RL immediately
- DESIGN.md as a patch checklist (ledger owns status)
- Cloning Civ 6/7 systems (religion, tourism, great people, hex unit combat, 20 unique civs)

---

## Intent

Deterministic multi-agent civilisation lab → watchable Settlers × Civ hybrid.  
Logs = animation pipeline. Ages progression. Learning agents later.  
One simulation kernel; lab and human UI are layers on top.

The utility agent is the **hands**. The human (later) is the **brain**.  
Do not micro villagers. Do not replace the kernel to “feel more like Firaxis.”

---

## Current content shape (vision, not checklist)

**Survival → specialisation → science**

- Early: farms, storage, food pressure
- Mid: workshop → barracks → civic chain → academy / subjects
- Era 4: subject buildings (irrigation, library, foundry, hall, command)
- E5: Lab → Observatory → discoveries (knowledge sink → permanent farm bonus)

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

A broken science path is not a game. Multi-seed reachability (era 4 + Library + Lab + Observatory) is the floor the playable layer stands on.

We are roughly **70% of a Civ-shaped engine** and **10% of a game**.  
The remaining game is not more buildings. It is decisions, a watchable map, one rival, and win/lose.

---

## Why it is not playable yet

Right now the utility agent is the player. A human watches. Governor text (`focus food`) is a cheat code, not a turn.

A human cannot yet:

1. **Stop time** at a decision
2. **Pick one thing** that hurts something else
3. **See a rival** doing the same
4. **Read the map** as a place, not a table

Until those four exist, this is a lab with a god-view. Fine as a lab. Not Civ.

---

## Playable path (Settlers × Civ, not a Civ clone)

### The product

The human is the **spirit of the settlement**. Villagers keep walking. You do not micro A0.

You only get decisions when the world asks. Agents execute. Logs already are the animation.

That is Settlers to look at, Civ to decide.  
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

Those games are huge because they sell 100 hours. This is a 32×32 deterministic lab. Their surface would break the kernel.

Steal only this:

- Ages change the rules (we have this)
- One visible rival (Layer 3 — west / east, own governor, cross-faction raids)
- A victory you can point at (win / lose clock: science, wipe, or hold)
- Presentation that makes stocks feel like a city (we do not have this)

---

## Three layers. Ship in this order.

```
Now (lab)          Playable              Civ-shaped
─────────          ────────              ──────────
kernel             pause on decision     rival civ on same map   ← shipped
utility agents     governor choices      raids become someone    ← shipped
logs/snapshots     watchable map         win / lose clock        ← shipped
```

**Layer 1 — Watchable**  
Paced god-view: one screen, events as sentences. “s2 unlocked Inquiry.” “They raided s1.” The web map is this layer.

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

That is a short Civ. That is enough. Do not add more buildings to make it feel finished.


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
