# How the right-hand Grok canvas gets the game

The user has no terminal. They play in the **right-hand live preview**.
That preview is whatever this sandbox serves on `0.0.0.0:8080`.

```
python3 tools/play_web.py --host 0.0.0.0 --port 8080
```

That **is** the canvas. There is no second UI. Do not start Vite.

## New Grok chat (same project)

1. Copy `/workspace/artifacts/ai-world` → `/workspace/ai-world` if the kernel is missing or `play_web.py` is PLACEHOLDER / <1KB.
2. `/workspace/startup.sh` must start play_web, not `npm run dev`. A copy lives at `/workspace/artifacts/startup.sh`.
3. `sh /workspace/startup.sh` and leave it running.
4. Prove: `curl -sf http://127.0.0.1:8080/ | grep AI-world`
5. Tell the user to click **Begin**.

If 8080 is already a Vite/React blank, kill **that PID** and start play_web. Never `pkill -f`.

## Why the last chat “couldn’t”

- New sandbox defaults to the Vite scaffold. That steals 8080. Canvas shows the wrong app.
- Codex pushed PLACEHOLDER over `tools/play_web.py`, `sim/core/simloop.py`, `sim/world/settlements.py`. A git pull of a dead tree blanks the game.
- A background test left the sim paused on the opening edict, so Begin did nothing.

`Game.start` must cancel any in-flight run. Do not leave a picker blocked.

## Git

`999nike/AI-world` · `e5-lib-global` · not `main`.
Restore kernel from `5fe9d2f` if GitHub files are 11 bytes.
