# AI-world Patch Ledger

**Hand-off:** 2026-08-18 22:30 BST — canvas recipe for the next chat

## Snapshot

```
LIVE on e5-lib-global @ 5fe9d2f (+ canvas docs)
  E5.13 science path global (lib → lab → obs)
  Playable edicts: food / science / army
  Layer 3: rival civ + win/lose clock
  Watchable city: glyphs, days of food, chronicle sentences
  Validate path unchanged (rival_agents=0, playable off)
  Web: Begin always cancels a leftover paused run

Pass bar (no --playable, no --rival):
  seeds 42,100,7,999,2026 @ 5000 → era4 + lib + lab + obs + 5 subjects
  expected scores: 42=1205, 100=1600, 7=2207, 999=1267, 2026=1933
```

---

## NEW CHAT — PUT THE GAME IN THE RIGHT CANVAS FIRST

Read `CANVAS.md`. The user tests **only** in the Grok right-hand preview.

That preview = `python3 tools/play_web.py --host 0.0.0.0 --port 8080`.
Not Vite. Not a second frontend.

In the Grok App Builder sandbox:

1. Kernel at `/workspace/ai-world`. Persisted copy: `/workspace/artifacts/ai-world`.
2. If `play_web.py` / `simloop.py` / `settlements.py` is PLACEHOLDER or <1KB, copy artifacts over it. Codex wiped those on origin once.
3. `cp /workspace/artifacts/startup.sh /workspace/startup.sh && sh /workspace/startup.sh`
4. Success: page contains `AI-world` and a Begin button. Leave the process up.
5. Do not `npm run dev`. Do not `pkill -f`. Do not leave a sim paused on an edict.

User has no terminal. If they cannot click Begin on the right and see pale west / clay east agents, it is not running.

---

## NEW CHAT HANDOFF (kernel)

**Repo:** [999nike/AI-world](https://github.com/999nike/AI-world)  
**Branch:** `e5-lib-global` (tracking origin). Tip around `5fe9d2f`.  
**Do not use `main`.** `main` @ `d9ff28e` is later broken E5.11 civic-gate work. Do not merge it. Do not force-push main. Do not Frankenstein 1444db0 files onto E5.11.

**Locked-good historical commit:** `1444db0` (E5.7). We did **not** revert. We patched forward on this branch. Stay on `e5-lib-global`.

**User:** nike dang / GitHub 999nike. No extra terminal. They cook; **you test**. They tell Codex to `git fetch && git checkout e5-lib-global && git pull`. They watch the **in-browser live preview** (`tools/play_web.py` on 8080). That is the product. They cannot run the CLI.

**Two files, two jobs**
- `PATCH_LEDGER.md` = status (this file)
- `DESIGN.md` = vision (do not turn it into a checklist)
- `CANVAS.md` = how the right-hand preview gets the game

### What this branch is

Deterministic multi-agent settler sim. Utility agent = hands. Human = spirit of the settlement (edicts, not villager micro). Same kernel for lab and play.

| Layer | Status | What |
|---|---|---|
| Science path | shipped | Library → Lab → Observatory gates are **global** (`sm.own()`), not nearest-only. Seed 100 split-town is why. |
| Playable | shipped | Pause at opening / era4 / inquiry / discovery / drought. 3 edicts: food / science / army. `sim/core/playable.py` |
| Rival | shipped | `--rival` / web Begin: 4 player west + 4 rival east. `rival_agents=0` default = **identical spawn/RNG** to pre-rival. |
| Clock | shipped | Rival-on only. Science = own Observatory + 2 discoveries. Wipe = both founded, one pop 0. Clock end = era 4 AND more people. `sim/core/outcome.py` |
| Watchable | shipped | `tools/play_web.py` — glyphs, days of food, You/Rival, chronicle sentences. Presentation only. |

### Sacred contracts (do not break)

1. **Determinism.** No extra RNG on the validate path.
2. **One axis at a time.** Propose, then apply. No civic / hunger / age-up pile-on (that broke seed 42 on later main).
3. **Do not fork the kernel** to make a game. Playable sits on the sim.
4. **Validate path:** `rival_agents=0`, `playable=False`. Must still hit the scores above. If scores drift, you broke it.
5. **Edicts never touch rival brains.** `play_state.player_ids` + `apply_edict(..., player_ids=)`.
6. **`sm.active_faction`** scopes nearest / own / science gates / deposits when rival is on. `None` when off.
7. **Raids:** 2 factions → cross-faction only. 1 faction → old strongest-vs-weakest.

### Key files

```
sim/core/simloop.py          loop, rival_agents, outcome hook, faction obs
sim/core/playable.py         edicts, detect_reason on player towns
sim/core/outcome.py          detect_early / detect_survival
sim/core/governor.py         focus food|build|expand|science|army
sim/core/build_governors.py  science gates use sm.own()
sim/world/map.py             make_world(..., rival_agents=0)
sim/world/settlements.py     own/nearest/raids/last_raid
sim/world/state.py           AgentState.faction
tools/play_web.py            the product UI
tools/multi_seed_validate.py sacred bar
CANVAS.md                    right-hand preview recipe
```

### How to work in the Grok sandbox

- Git clone lives at `/tmp/ai-world` (or re-clone). Preview copy at `/workspace/ai-world`. Persisted: `/workspace/artifacts/ai-world`.
- After edits: copy those files to `/workspace/ai-world`, kill the old `play_web.py` **by PID** (do not `pkill -f`, it kills the wrapper), then `sh /workspace/startup.sh`.
- Preview = `0.0.0.0:8080`. Leave it running. User has no shell. If they can click Begin, you passed.
- Commit as `999nike <999nike@users.noreply.github.com>` on `e5-lib-global`. Push origin. Never force-push main.

### Next axis (Codex started, then wiped the kernel — do not take PLACEHOLDER)

Richer mid/late decisions after Observatory was proposed (farm bonus vs bank knowledge). Codex commits on origin (`4b12b64`..`f4bb5ed`) replaced `simloop.py` / `settlements.py` / `play_web.py` with the word PLACEHOLDER. **Do not pull that over a working tree.** Restore those three files from `5fe9d2f` first. Then, if you actually ship the discovery choice, do it as one axis on top of the restored kernel. Validate path must still match.

Do **not** start religion, unique civs, hex combat, RL agents, or a second frontend.

### Smoke that already passed (re-run if you touch kernel)

```
# validate (must match scores)
python tools/multi_seed_validate.py --seeds 42 100 7 999 2026 --ticks 5000 --quiet

# rival + playable, science edicts — seed 42 stopped ~tick 718, player science win
# (outcome.py SCIENCE_DISCOVERIES = 2)
```

### History (why seed 100 failed)

Nearest-only Library/Lab/Obs. Seed 100 is a split-town: inquiry on one settlement, library later on another. Fix was **global science chain**, not a revert. Working seed-100 mid-history was `db9ea00`. Regression `d2f40a3`. We patched `1444db0` forward: `244b36c` lib global, `006873f` lab/obs global.

### User voice

Short, casual, in command. “keep it moving if u tested.” They approve one axis. You test. You do not ask them to run commands.

---

## Watchable contract

- Presentation only. No kernel, edict, gate, or RNG change.
- Map glyphs match god-view letters. Food shown as days (pop * 0.22 + soldiers * 0.03).
- Chronicle diffs settlements / science buildings / raids into sentences.

## Clock contract

- Only when `rival_agents > 0`. Default 0 = no early stop, no outcome, validate identical.
- Science: own-faction Observatory + 2 discoveries. First one wins.
- Domination: both factions have founded; one side's total pop hits 0.
- Survival: clock expires. Win = era 4 AND more people.

## Layer 3 contract

- `rival_agents=0` (default): spawn + RNG identical to playable v2. Validate must match.
- `--rival` / web Begin: 4 player west (x 1–10) + 4 rival east (x width-11..width-2).
- Rival governor: seed even → army, odd → science. Edicts never touch rival brains.
- Two factions on the map → raids are cross-faction only.
