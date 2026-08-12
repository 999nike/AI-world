# AI-world Design Notes (Internal)

**Last updated:** 2026-08-12  
**Era 1:** LOCKED  
**Era 2:** COMPLETE  
**Era 3:** E3.0–E3.3 live (age-up, Market, Temple, Academy)

---

## Intent & Long-term Vision

Deterministic multi-agent civilisation laboratory that becomes a **watchable game**.

- **Systems first**: headless, seed-controlled, fully logged simulation.
- **Human experience later**: Settlers-style top-down god-view. Logs are the animation pipeline — once the skeleton is solid we generate simple visual playback (structures appear, resources move, population grows) from events.jsonl + snapshots.
- **Ages progression** (Civilization flavour): settlements advance through eras as they unlock buildings and knowledge.
- **Learning agents** introduced only after the world is stable and interesting. The game must have genuine long-term depth, not just a pretty face.

Humans can govern, design scenarios, or drop in and control an agent. The core remains a research lab for emergent multi-agent behaviour under scarcity.

---

## Determinism (sacred)

Same seed + same code → same outcome. Logs are the source of truth.

---

## Era 1 — Settlement Survival (LOCKED)

Farm, storage, hut. Population growth/starvation. Deposit range 2.

---

## Era 2 — Classical (COMPLETE)

Granary, Mine, Road, Workshop, Barracks + light defense + raids.

---

## Era 3

### E3.0 Age transition
- Gate: workshop + barracks + pop ≥ 15
- Effect: era=3, +5 food, +0.25 farm yield/farm

### E3.1 Market
| Cost | Gate | Effect |
|------|------|--------|
| 4w 3s | era≥3 + barracks, max 1 | +0.5 wood/tick, +0.25 stone/tick |

### E3.2 Temple
| Cost | Gate | Effect |
|------|------|--------|
| 3w 4s | era≥3 + market, max 1 | +0.25 food/tick; growth surplus ticks 3 (was 5) |

### E3.3 Academy
| Cost | Gate | Max |
|------|------|-----|
| 5w 4s | era≥3 + temple | 1 |

**Knowledge production:** +0.3 Knowledge / tick while Academy exists.

**Subjects** (permanent unlocks, stack):

| Subject | Knowledge cost | Immediate effect | Future expansion |
|---------|----------------|------------------|------------------|
| Agriculture | 8 | +0.15 farm yield (permanent) | Irrigation, crop rotation |
| Craft | 10 | +0.1 tools/tick | Better tools, industry |
| Organisation | 12 | Growth surplus ticks −1 (faster pop) | Administration, larger cities |
| Strategy | 15 | Soldiers defend value +0.1 | Tactics, military tech |
| Inquiry | 20 | Opens Era 4 age-up path | Research tree, advanced ages |

Subjects are stored on the settlement. Once unlocked they never reset. Academy is the single building that feeds the entire knowledge system.

---

## Future direction (post-E3)

1. Walls (defensive structure)
2. Polish + multi-seed validation
3. Minimal god-view (log → grid scrub / simple animation)
4. Era 4 (opened by Inquiry subject)
5. Learnable / thinking agents only when world is deep enough

---

## Dev rules

1. Determinism sacred  
2. One major axis at a time  
3. Small patches → ledger → push  
4. Learnable agents only when world is stable  
5. Logs first — visuals come from logs  
