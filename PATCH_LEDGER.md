# AI-world Patch Ledger

**Hand-off:** 2026-08-20 10:28 BST — **v29-safe is the restore pin. Sit + art + painted sprites are on this commit.**

## New chat — read this first

You are continuing **AI-world**, watch-first, **four peoples**, same 48×48 island.

1. Restore **`v29-safe`**. Not `v19-safe`. Not `main`. Not older.
2. Read [DESIGN.md](DESIGN.md) — **Locked plan**. Do not invent a different one.
3. Read [CANVAS.md](CANVAS.md) — preview is play_web on **8080**. Build mode, not Expert. Never Vite.
4. Live stamp must be **· v29**. Prove: page contains `id="begin"` and `· v29`.
5. Sacred check: seed **42**, 10 a pole — east science hold **Year 342**. Soft watch after hold.
6. One axis at a time. Short patches.
7. **v30 memory walkers were reverted.** A JS paren error blanked the watch. Do not re-land memory until the watch stays solid.

Never `pkill -f`. If you must restart: SIGTERM the `python3 tools/play_web.py` PID only, then `sh /workspace/startup.sh`.

## Restore pin (v29 / 2.9)

| | |
|---|---|
| **Name** | `v29-safe` (alias **2.9**) |
| **Repo** | `999nike/AI-world` |
| **Branch** | `v29-safe` |
| **Commit** | `7e3cbfdd66dd69cdd296f5d00528c28d74afd7e5` |
| **Parent land** | `5ab70ae` (world-city kernel) · old note `754f701` |
| **Stamp** | · v29 |
| **Date** | 2026-08-20 |

Old pin `v19-safe` / `5ce0355` is king+hall only. **Do not restore it.**

## Product (now)

```
LIVE play_web · · v29
  Island 48×48 · four corners
  Sit: uni / bar · districts · park W E N S / Island
  Art: tiles not letters · roofs · water · cobbles · rail
  Sprites: mill wheel sheet · train · cab · bus · plane
  Walkers still dots
  Hold: seed 42 · east science Year 342
```

## Shipped on this pin

| Stamp | Axis |
|---|---|
| v20 | scribe + builder |
| v21 | north / south poles |
| v22 | start 10 a side |
| v23 | mill + trains |
| v24 | rail is the spine (not the carpet) |
| v25 | mill power / mill-race |
| v26 | warehouse · train mill → W |
| v27 | one wonder a pole |
| v28 | airport + planes · era 6 |
| v29 | taxi + bus |
| v29 canvas | sit + art pass + painted sprites (this commit) |
| v30 | **reverted** — memory walkers, JS broke watch |

## Locked next — start the game (Layer 2)

This is **the** next axis. Not a new era. Not memory. Not Vite. Stamp stays **· v29** until the owner says otherwise.

**What “start the game” means (DESIGN):** the human is the brain. Utility agents stay the hands. Pause at a fat moment. **3 buttons.** One pick that can hurt. Resume. Same seed 42. Same 10/10/10 watch.

Kernel already has it: [sim/core/playable.py](sim/core/playable.py) (`EDICTS`, `DISCOVERY_EDICTS`, `apply_edict`). Watch does **not**. `play_web.py` runs `playable=False`. `/api/choose` exists. The map never shows a decision.

### How to do it (one axis)

1. Restore this pin. Prove `id="begin"` and `· v29`. Sacred check still Year 342 **before** you change playable.
2. In `tools/play_web.py` only: `playable=True`, `PlayableState(policy="human")` (or the existing choose queue). Do **not** change `num_agents` / `rival_agents` / `pole_agents` defaults in `run_sim`. Watch still passes 10/10/10.
3. In `tools/play_ui.html` only: when `state.status==="decision"`, pause the film and show **three buttons** from `state.decision.choices` (title + hurt line). Click → `POST /api/choose` `{edict}`. No typing `focus food`.
4. Edicts are **west / player** only. East / north / south keep their governors. RNG untouched.
5. Fat moments already in kernel: opening, era 4, inquiry, discovery (farm / bank / auto), drought.
6. After one Watch on seed 42: east science hold must still be **Year 342**. If it moves, revert. Soft watch after hold stays.
7. Syntax-check the HTML JS (`node --check` on the extracted script) before leaving it up. v30 died here.

Do not add more edicts in the first patch. Three that exist are enough. Do not open memory agents. Do not pin v19-safe.

## Do not

- Do not restore `v19-safe` / `5ce0355`. That is an old rollback, not the game.
- Do not change `run_sim` defaults (`num_agents=4`, `rival_agents=0`, `pole_agents=0`). Watch passes 10/10/10 in `play_web.py`.
- Do not paint every path as rail. Grain stays dirt.

## Repo

999nike/AI-world · **v29-safe** (restore this) · stamp · v29
