# AI-world Patch Ledger

**Hand-off:** 2026-08-19 17:50 BST — v18 hands grow + knight

## New chat — read this first

You are continuing **AI-world**, watch-first, two peoples, same 48×48 island.

1. Read [DESIGN.md](DESIGN.md) — **Locked plan**. Do not invent a different one.
2. Live stamp is **· v18**. Preview must show it.
3. Sacred check: seed **42** — re-measure after v18 (more hands change the path). Soft watch after hold.
4. One axis at a time. Do not Vite. `artifacts/ai-world` is truth. `startup.sh` starts play_web.

## Product (now)

Hide human edicts. Spectator watch. West vs east.

```
LIVE play_web · · v18
  Island 48×48, zoom + / − / Fit
  Districts, streets, food chain, city food floor
  Start 4 walkers a side (labour)
  Breed: hands grow with population toward 8–10 by city
  Town + barracks → one knight a side (real role, not paint)
  Fake 2×2 gold/silver kings removed
```

## Shipped this patch (v18)

- `AgentState.role`: walker | knight
- Breed after settlement tick: target hands = min(10, 4 + (pop-1)//4)
- At most one birth per faction per tick; spawn at capital offsets (no extra RNG)
- Knight when max era ≥ 3 and side has barracks; lowest agent_id walker promoted
- UI paints role; chronicle logs births and knighting
- King / crown / government **not** built yet

## Locked next (not built)

- City: that knight (or child) → **king**. One crown a side. Hall / government starts.
- Then specialists at science. N/S poles later. Trains era 5. Airports era 6.

## Do not

- Do not add four corners / four kingdoms yet.
- Do not jump to trains, airports, or memory-app agents.
- Do not change WorldConfig size unless the axis needs it.

## Repo

999nike/AI-world · e5-lib-global
