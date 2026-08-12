# AI-world Design Notes (Internal)

**Last updated:** 2026-08-12  
**Era 4:** E4.0–E4.4 LOCKED

---

## Vision (look & feel)

**The Settlers** for human play: top-down, resource chains, haul labour, buildings that feel alive, watching a settlement grow.

**Civilization** for structure: ages, subjects/tech, long-horizon choices, guns-vs-butter tension.

**Research lab** underneath: fully deterministic, seed-controlled, every decision logged. Logs become the animation / god-view pipeline. Humans watch or steer; later agents learn.

Feel target when a human plays:  
“I am watching a living settlement make real choices. Bad priorities hurt. Good ones compound.”

Not pure spreadsheet. Not pure action game. Lab first → watchable game.

---

## Intent

Deterministic multi-agent civilisation lab → watchable Settlers-style game.  
Logs = animation pipeline. Ages progression. Learning agents later.

---

## Era 4 (LOCKED)

### E4.0 Age-up
Inquiry + academy + pop≥20 → era 4

### E4.1 Irrigation
| Cost | Gate | Effect |
|------|------|--------|
| 2w 2s | era≥4 + agriculture | +0.2 farm/farm |

### E4.2 Library
| Cost | Gate | Effect |
|------|------|--------|
| 3w 3s | era≥4 + inquiry | +0.2 knowledge/tick |

### E4.3 Foundry
| Cost | Gate | Effect |
|------|------|--------|
| 3w 3s | era≥4 + craft | +0.15 tools/tick |

### E4.4 Hall
| Cost | Gate | Effect |
|------|------|--------|
| 3w 3s | era≥4 + organisation | +0.15 food/tick + surplus-1 |

---

## Next axis — E4.5 Command (strategy)

| Field | Value |
|-------|-------|
| Cost | 3w 4s |
| Gate | era≥4 + strategy subject |
| Max | 1 |
| Icon | X |
| Effect | +0.20 soldiers/tick |
| Trade-off | Soldiers consume 0.05 food each/tick |

Guns-vs-butter. Over-militarise → starvation risk. Under-militarise → weak to raids. Agents must choose.

Later strategy buildings can specialise (pure offence / pure defence).

---

## Longer vision (Era 6+)

Science labs → physics-style experiments / tech unlocks.  
Modern-era buildings as late content.  
Still pure lab-sim (deterministic + logged).

---

## God-view

`--play` auto-steps snapshots with key event callouts.  
Icons: C=academy #=walls ~=irrigation L=library Y=foundry O=hall  
Next: X=command

---

## Dev rules

1. Determinism sacred  
2. One axis at a time  
3. Logs first  
4. Min tokens while usage high  
5. Choices must be able to hurt  
