# AI-world Design Notes (Internal)

**Last updated:** 2026-08-12  
**Era 1:** LOCKED  
**Era 2:** COMPLETE  
**Era 3:** COMPLETE  
**Era 4:** skeleton locked (E4.0–E4.1)

---

## Intent & Long-term Vision

Deterministic multi-agent civilisation laboratory that becomes a **watchable game**.

- Systems first: headless, seed-controlled, fully logged.
- Human experience later: Settlers-style top-down god-view. Logs = animation pipeline.
- Ages progression (Civ flavour).
- Learning agents only after world is stable and interesting.

---

## Determinism (sacred)

Same seed + same code → same outcome. Logs are source of truth.

---

## Era summary

- **Era 1** LOCKED — farm/storage/hut survival
- **Era 2** COMPLETE — granary/mine/road/workshop/barracks/raids
- **Era 3** COMPLETE — age-up, market, temple, academy+subjects, walls
- **Era 4** skeleton — Inquiry age-up + Irrigation (Agriculture expansion)

### E4.1 Irrigation
| Cost | Gate | Max | Effect |
|------|------|-----|--------|
| 2w 2s | era≥4 + agriculture | 1 | +0.2 farm yield per farm |

---

## Next major axis

**God-view animation path** — turn events.jsonl + snapshots into simple step/scrub visual playback.

---

## Dev rules

1. Determinism sacred  
2. One major axis at a time  
3. Small patches → ledger → push  
4. Learnable agents only when world is stable  
5. Logs first — visuals come from logs  
6. Minimum tokens while usage is high  
