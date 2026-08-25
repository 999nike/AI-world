# How the right-hand Grok canvas gets the game

**If the right pane is a file tree, the user is in Expert mode.**
You cannot switch it. Tell them: bottom bar, next to `ai-world`, change **Expert → Build**. Then the globe / Publish / `/` preview appears. Do not debug ports for a file tree. Two full chats died on this.

The user has no terminal. They play in the **right-hand live preview**.
That preview is whatever this sandbox serves on `0.0.0.0:8080`.

```
python3 tools/play_web.py --host 0.0.0.0 --port 8080
```

That **is** the canvas. There is no second UI. Do not start Vite. Do not iframe (Grok already frames 8080; nested iframe is blank).

`play_web.py` loads `tools/play_ui.html` on every request. Both files must exist.
Sprites live in `tools/sprites/` (`/sprites/train.png` etc). If those 404, the mill/train/cab/bus/plane are missing.

## New Grok chat (same project)

1. User must be in **Build**, not Expert.
2. Restore branch **v40**. Stamp **· v40**.
3. Canvas live stamp is **· v40**.
4. Copy `/workspace/artifacts/ai-world` → `/workspace/ai-world` if the kernel is missing or `play_web.py` / `play_ui.html` is PLACEHOLDER / <1KB.
5. `/workspace/startup.sh` must start play_web, not `npm run dev`.
6. `sh /workspace/startup.sh` and leave it running.
7. Prove: page contains `id="begin"` and `· v40`. Prove `/sprites/train.png` is 200.
8. Tell the user to click **Watch**. The map is **Iso**. Park **W**.

Never `pkill -f`. Kill only the `python3 tools/play_web.py` PID (SIGTERM), then `sh /workspace/startup.sh`.

Live stamp: subtitle **Watch the ages. Four peoples. Same map. · v40**

If the right pane is blank HUD / empty World / no map at idle, the UI script crashed. Revert the last HTML edit; do not debug ports.

## Next chat

See [PATCH_LEDGER.md](PATCH_LEDGER.md). Live **· v40**. Edicts hidden. Never Vite.
