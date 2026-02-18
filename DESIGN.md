That’s clean.
That’s professional.
That’s GitHub-ready.

---

# 📘 `DESIGN.md` (Internal Truth)

### DESIGN.md (internal design + roadmap)

```bash
cat > DESIGN.md <<'EOF'
# AI-world Design Notes (Internal)

## Intent
This project is a **civilization simulation lab**.  
Goal: create a stable deterministic world where agents can develop strategies under scarcity.
UI/visuals come later. Logging/replay is first-class.

## Determinism
- Seed controls RNG.
- Same seed + same code/config => same outcome.
- Logs are for replay/analysis.

## Current mechanics (v0, Feb 2026)
### World
- 32x32 grid (config-driven)
- Tiles: food, wood, stone
- Simple regrowth every N ticks (deterministic)

### Agents
- Baseline agent kinds: random + utility agent
- Actions: move / gather / build
- Inventory: food/wood/stone

### Settlements
- Created when structures appear; linked via `struct_to_settlement`
- Stocks: food/wood/stone
- Population consumes food per tick
- Starvation can reduce population to zero
- Early “starter food” seeding exists to prevent immediate collapse

### Economy-lite
- Agents auto-deposit inventory into settlement stock when standing on a settlement-linked structure
- Buildings can be funded from agent inventory, tile resources (storage), and settlement stock (when present)

## Known issues (current)
- Population tends to collapse after early hut growth
- Starvation pressure is still high; needs tuning
- Huts may increase population pressure without productivity benefit
- Multiple settlements can form quickly (distance threshold / linkage logic)

## Current “working” milestone
We restored full run loop with:
- settlement creation
- deposit events
- building events (storage/hut)
- non-zero scores
- multiple settlements and structures appearing

Example recent run stats:
- score ~154
- settlements ~5
- storage built ~4, huts ~11
- starvation events ~5, net pop negative

## Next tuning levers (no new systems yet)
- Adjust `SETTLEMENT_RULES`:
  - `food_per_pop_per_tick`
  - `growth_food_buffer`
  - `starting_population`
- Policy tuning for UtilityAgent:
  - stop overbuilding huts when food stock is low
  - bias gather-food when settlement food below threshold
- Add simple “build gate”:
  - only allow hut build if settlement food_stock >= pop*(consumption)+buffer

## Next features (after stability)
- Minimal replay viewer (CLI -> ASCII grid or simple renderer)
- Role hints (gatherer/builder) as soft biases
- Memory v0 (JSONL lessons per agent) AFTER stability
EOF

We don’t trim it.
We don’t hide rough edges.
We keep the “Known Rough Edges” section.

At the top of DESIGN.md, add:

```markdown
# AI-world Design Notes (Internal)

This document describes current mechanics, limitations,
and forward roadmap. It may contain unstable or experimental
design details not reflected in the public README.
