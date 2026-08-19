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

## New Grok chat (same project)

1. User must be in **Build**, not Expert.
2. Checkout `e5-lib-global` (later than `4c3c541`). Not `main`.
3. Copy `/workspace/artifacts/ai-world` → `/workspace/ai-world` if the kernel is missing or `play_web.py` / `play_ui.html` is PLACEHOLDER / <1KB.
4. `/workspace/startup.sh` must start play_web, not `npm run dev`.
5. `sh /workspace/startup.sh` and leave it running.
6. Prove: `curl -sf http://127.0.0.1:8080/` contains `id="begin"` and `· v10`.
7. Tell the user to click **Watch** in the right preview.

Never `pkill -f`.

Live stamp: subtitle **Watch the ages. Two peoples. Same map. · v10**
