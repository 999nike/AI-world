# AI-world Design Notes (Internal)

**Last updated:** 2026-08-12  
**Era 4:** E4.0–E4.4 LOCKED

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

## Next axis

E4.5 strategy subject building (TBD)

---

## God-view

`--play` auto-steps snapshots with key event callouts.  
Icons: C=academy #=walls ~=irrigation L=library Y=foundry O=hall

---

## Dev rules

1. Determinism sacred  
2. One axis at a time  
3. Logs first  
4. Min tokens while usage high  
