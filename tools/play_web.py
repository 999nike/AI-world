#!/usr/bin/env python3
"""Playable web layer for AI-world. Same kernel. Click edicts. Watch the map.

  PYTHONPATH=. python tools/play_web.py --host 0.0.0.0 --port 8080
"""
from __future__ import annotations

import argparse
import json
import sys
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from queue import Empty, Queue
from typing import Any, Dict, Optional
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sim.core.simloop import run_sim  # noqa: E402


HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>AI-world</title>
<style>
:root {
  --bg: #0c0b09;
  --bg-elevated: #161410;
  --bg-subtle: #1e1b16;
  --fg: #efe8dc;
  --fg-muted: #9a9186;
  --fg-subtle: #6f6860;
  --border: color-mix(in oklab, var(--fg) 12%, transparent);
  --accent: #d7d2c8;
  --accent-fg: #0c0b09;
  --danger: #b4554a;
  --ok: #6f8f6a;
  --radius-sm: 8px;
  --radius-md: 12px;
  --radius-lg: 20px;
  --space-2: 8px;
  --space-3: 12px;
  --space-4: 16px;
  --space-5: 24px;
  --space-6: 32px;
  --font-display: "Iowan Old Style", "Palatino Linotype", Palatino, Georgia, serif;
  --font-body: "Segoe UI", system-ui, sans-serif;
  --font-mono: ui-monospace, "SF Mono", Menlo, Consolas, monospace;
  --motion-fast: 250ms;
  --motion-quick: 150ms;
  --ease: cubic-bezier(0.22, 1, 0.36, 1);
}
* { box-sizing: border-box; }
html, body { margin: 0; background: var(--bg); color: var(--fg); font-family: var(--font-body); min-height: 100%; }
button, [role="button"] { cursor: pointer; }
button:disabled { cursor: default; opacity: 0.45; }
body { display: flex; flex-direction: column; min-height: 100vh; }
.wrap { width: min(1120px, calc(100% - 32px)); margin: 0 auto; padding: var(--space-5) 0 var(--space-6); }
header { display: flex; justify-content: space-between; align-items: flex-end; gap: var(--space-4); margin-bottom: var(--space-5); }
h1 { font-family: var(--font-display); font-weight: 600; letter-spacing: -0.03em; font-size: clamp(1.6rem, 1.2rem + 1.4vw, 2.2rem); margin: 0; }
.sub { color: var(--fg-muted); font-size: 0.92rem; margin-top: 4px; }
.row { display: flex; gap: var(--space-5); align-items: flex-start; }
.col { min-width: 0; }
.col.side { width: 320px; flex: 0 0 320px; }
.panel { background: var(--bg-elevated); border: 1px solid var(--border); border-radius: var(--radius-lg); padding: var(--space-4); }
.panel + .panel { margin-top: var(--space-4); }
.kicker { font-size: 0.72rem; letter-spacing: 0.12em; text-transform: uppercase; color: var(--fg-subtle); font-weight: 600; }
.stats { display: grid; grid-template-columns: repeat(3, 1fr); gap: var(--space-3); }
.stat { background: var(--bg-subtle); border-radius: var(--radius-sm); padding: 10px 12px; }
.stat b { display: block; font-variant-numeric: tabular-nums; font-family: var(--font-mono); font-size: 1.05rem; }
.stat span { color: var(--fg-muted); font-size: 0.75rem; }
.map-wrap { overflow: auto; border-radius: var(--radius-md); background: #0a0908; padding: 10px; }
#map { display: grid; gap: 1px; width: max-content; }
.cell { width: 13px; height: 13px; border-radius: 2px; background: #1a1814; }
.cell.agent { background: var(--accent); }
.cell.settlement { background: #c4b8a4; }
.cell.farm { background: #4d6a45; }
.cell.storage { background: #6b5344; }
.cell.hut { background: #8a6a4a; }
.cell.granary { background: #7a6238; }
.cell.mine { background: #5c5c5c; }
.cell.road { background: #3a342c; }
.cell.workshop { background: #6e4f3a; }
.cell.barracks { background: #6a3d36; }
.cell.market { background: #5a5e48; }
.cell.temple { background: #4a4e5c; }
.cell.academy { background: #3d5360; }
.cell.walls { background: #2e2c2a; }
.cell.irrigation { background: #3d5a52; }
.cell.library { background: #4a6270; }
.cell.foundry { background: #70483a; }
.cell.hall { background: #5a5044; }
.cell.command { background: #5a3a38; }
.cell.lab { background: #3a5868; }
.cell.observatory { background: #2f3e55; }
.settlements { display: flex; flex-direction: column; gap: 8px; }
.town { border: 1px solid var(--border); border-radius: var(--radius-sm); padding: 10px 12px; }
.town strong { font-family: var(--font-display); }
.town .meta { color: var(--fg-muted); font-size: 0.8rem; margin-top: 4px; }
.legend { color: var(--fg-subtle); font-size: 0.72rem; line-height: 1.5; margin-top: 10px; }
.controls { display: flex; gap: 8px; flex-wrap: wrap; align-items: center; }
input[type="number"] {
  height: 44px; width: 96px; background: var(--bg-subtle); color: var(--fg);
  border: 1px solid var(--border); border-radius: var(--radius-sm); padding: 0 12px;
  font: inherit;
}
.btn {
  height: 44px; border: 0; border-radius: var(--radius-sm); padding: 0 16px;
  font: 600 0.95rem var(--font-body); transition: transform var(--motion-quick) var(--ease), opacity var(--motion-quick) var(--ease);
}
.btn:active { transform: scale(0.98); }
.btn.primary { background: var(--accent); color: var(--accent-fg); }
.btn.ghost { background: transparent; color: var(--fg); border: 1px solid var(--border); }
.edicts { display: flex; flex-direction: column; gap: 8px; }
.edict {
  text-align: left; background: var(--bg-subtle); color: var(--fg);
  border: 1px solid var(--border); border-radius: var(--radius-md);
  padding: 12px 14px; transition: border-color var(--motion-quick) var(--ease);
}
.edict:hover { border-color: color-mix(in oklab, var(--fg) 28%, transparent); }
.edict b { display: block; font-family: var(--font-display); font-size: 1.05rem; }
.edict small { color: var(--fg-muted); }
.prompt { font-family: var(--font-display); font-size: 1.15rem; margin: 8px 0 12px; }
.log { max-height: 180px; overflow: auto; color: var(--fg-muted); font-size: 0.82rem; line-height: 1.45; }
.log div { border-top: 1px solid var(--border); padding: 6px 0; }
.banner { padding: 10px 12px; border-radius: var(--radius-sm); background: var(--bg-subtle); margin-bottom: 12px; }
.banner.ask { border: 1px solid color-mix(in oklab, var(--accent) 35%, transparent); }
.hidden { display: none !important; }
@media (max-width: 880px) {
  .row { flex-direction: column; }
  .col.side { width: 100%; flex: none; }
  header { flex-direction: column; align-items: flex-start; }
}
@media (prefers-reduced-motion: reduce) {
  .btn, .edict { transition: none; }
}
</style>
</head>
<body>
  <div class="wrap">
    <header>
      <div>
        <h1>AI-world</h1>
        <div class="sub">You are the spirit of the settlement. Villagers walk. You choose when the world asks.</div>
      </div>
      <div class="controls" id="startRow">
        <label class="kicker">Seed <input id="seed" type="number" value="42" min="1"/></label>
        <label class="kicker">Ticks <input id="ticks" type="number" value="2500" min="200" step="100"/></label>
        <button class="btn primary" id="begin">Begin</button>
      </div>
    </header>

    <div id="idleNote" class="panel">
      <div class="kicker">Watchable</div>
      <p style="margin:8px 0 0;color:var(--fg-muted);max-width:56ch">
        Same deterministic kernel. At opening, era 4, first discovery, and drought you pick one edict:
        feed the people, pursue science, or raise the army. Each one hurts something else.
      </p>
    </div>

    <div id="play" class="hidden">
      <div class="row">
        <div class="col" style="flex:1">
          <div class="panel">
            <div class="stats" id="stats"></div>
            <div class="map-wrap" style="margin-top:16px"><div id="map"></div></div>
            <div class="legend">F farm · S store · H hut · W workshop · B barracks · L library · R lab · V observatory · pale = agent</div>
          </div>
        </div>
        <div class="col side">
          <div class="panel">
            <div class="kicker">Edict</div>
            <div id="askBox">
              <div class="banner" id="statusBanner">Running…</div>
              <div class="prompt" id="prompt"></div>
              <div class="edicts" id="edicts"></div>
            </div>
          </div>
          <div class="panel">
            <div class="kicker">Settlements</div>
            <div class="settlements" id="towns"></div>
          </div>
          <div class="panel">
            <div class="kicker">Chronicle</div>
            <div class="log" id="log"></div>
          </div>
        </div>
      </div>
    </div>
  </div>
<script>
const $ = (id) => document.getElementById(id);
let timer = null;
let lastTick = -1;

function logLine(t) {
  const el = $("log");
  const d = document.createElement("div");
  d.textContent = t;
  el.prepend(d);
}

function renderStats(world, extra) {
  const m = (world && world.metrics) || {};
  const towns = (world && world.settlements) || [];
  const era = towns.reduce((a,s)=>Math.max(a, Number(s.era||2)), 2);
  const pop = towns.reduce((a,s)=>a + Number(s.population||0), 0);
  const food = towns.reduce((a,s)=>a + Number(s.food_stock||0), 0);
  const items = [
    ["Tick", world ? world.tick : "—"],
    ["Era", era],
    ["Pop", pop],
    ["Food", Math.round(food)],
    ["Library", m.build_library||0],
    ["Lab", m.build_lab||0],
    ["Observatory", m.build_observatory||0],
    ["Soldiers", towns.reduce((a,s)=>a+Number(s.soldiers||0),0).toFixed(1)],
    ["Starve", m.population_starved_events||0],
  ];
  $("stats").innerHTML = items.map(([k,v]) => `<div class="stat"><span>${k}</span><b>${v}</b></div>`).join("");
}

function cellClass(world, x, y) {
  const agent = (world.agents||[]).some(a => a.x===x && a.y===y);
  if (agent) return "agent";
  const st = (world.structures||[]).find(s => s.x===x && s.y===y);
  if (st && st.type) return st.type;
  const town = (world.settlements||[]).find(s => s.x===x && s.y===y);
  if (town) return "settlement";
  return "";
}

function renderMap(world) {
  if (!world) return;
  const w = world.width||32, h = world.height||32;
  const map = $("map");
  map.style.gridTemplateColumns = `repeat(${w}, 13px)`;
  let html = "";
  for (let y=0;y<h;y++) for (let x=0;x<w;x++) {
    html += `<div class="cell ${cellClass(world,x,y)}"></div>`;
  }
  map.innerHTML = html;
}

function renderTowns(world) {
  const towns = (world && world.settlements) || [];
  if (!towns.length) { $("towns").innerHTML = '<div class="meta" style="color:var(--fg-muted)">None yet.</div>'; return; }
  $("towns").innerHTML = towns.map(s => {
    const sub = (s.subjects||[]).join(", ") || "—";
    return `<div class="town"><strong>${s.id}</strong> · era ${s.era||2}
      <div class="meta">pop ${s.population||0} · food ${Math.round(s.food_stock||0)} · ${sub}</div></div>`;
  }).join("");
}

function renderDecision(state) {
  const banner = $("statusBanner");
  const edicts = $("edicts");
  const prompt = $("prompt");
  if (state.status === "decision" && state.decision) {
    banner.className = "banner ask";
    banner.textContent = `Tick ${state.decision.tick} — ${state.decision.reason}`;
    prompt.textContent = state.decision.prompt || "";
    edicts.innerHTML = (state.decision.choices||[]).map(c =>
      `<button class="edict" data-id="${c.id}"><b>${c.title}</b><small>${c.hurt}</small></button>`
    ).join("");
    edicts.querySelectorAll(".edict").forEach(btn => {
      btn.onclick = () => choose(btn.dataset.id);
    });
  } else if (state.status === "done") {
    banner.className = "banner";
    const m = (state.world && state.world.metrics) || {};
    const sci = (m.build_library&&m.build_lab&&m.build_observatory) ? "Science path complete." : "Science path incomplete.";
    banner.textContent = `Finished. Score ${state.score ?? "—"}. ${sci}`;
    prompt.textContent = "";
    edicts.innerHTML = "";
  } else {
    banner.className = "banner";
    banner.textContent = state.status === "running" ? "The settlement is working." : (state.status||"");
    prompt.textContent = "";
    edicts.innerHTML = "";
  }
}

async function poll() {
  const res = await fetch("/api/state");
  const state = await res.json();
  const world = state.world;
  if (world && world.tick !== lastTick) {
    lastTick = world.tick;
    renderStats(world);
    renderMap(world);
    renderTowns(world);
  }
  renderDecision(state);
  if (state.status === "done") {
    clearInterval(timer);
    timer = null;
    $("begin").disabled = false;
  }
}

async function begin() {
  $("idleNote").classList.add("hidden");
  $("play").classList.remove("hidden");
  $("begin").disabled = true;
  $("log").innerHTML = "";
  lastTick = -1;
  const seed = Number($("seed").value)||42;
  const ticks = Number($("ticks").value)||2500;
  logLine(`Began seed ${seed} · ${ticks} ticks`);
  await fetch("/api/start", {
    method: "POST",
    headers: {"Content-Type":"application/json"},
    body: JSON.stringify({seed, ticks})
  });
  if (timer) clearInterval(timer);
  timer = setInterval(poll, 280);
  poll();
}

async function choose(id) {
  logLine(`Edict: ${id}`);
  $("edicts").innerHTML = "";
  await fetch("/api/choose", {
    method: "POST",
    headers: {"Content-Type":"application/json"},
    body: JSON.stringify({edict: id})
  });
}

$("begin").onclick = begin;
</script>
</body>
</html>
"""


class Game:
    def __init__(self) -> None:
        self.lock = threading.Lock()
        self.choice_q: Queue = Queue()
        self.thread: Optional[threading.Thread] = None
        self.state: Dict[str, Any] = {"status": "idle", "world": None, "decision": None}

    def snapshot(self) -> Dict[str, Any]:
        with self.lock:
            return json.loads(json.dumps(self.state))

    def _set(self, **kwargs) -> None:
        with self.lock:
            self.state.update(kwargs)

    def start(self, seed: int, ticks: int) -> None:
        if self.thread and self.thread.is_alive():
            return
        while True:
            try:
                self.choice_q.get_nowait()
            except Empty:
                break
        self._set(status="running", world=None, decision=None, score=None, run_id=None, error=None)

        def picker(payload):
            self._set(status="decision", decision=payload)
            return self.choice_q.get()

        def on_tick(snap):
            with self.lock:
                self.state["world"] = snap
                if self.state.get("status") != "decision":
                    self.state["status"] = "running"

        def run():
            try:
                score, rid = run_sim(
                    seed=int(seed),
                    ticks=int(ticks),
                    snapshot_every=0,
                    return_score=True,
                    quiet=True,
                    playable=True,
                    choice_policy="human",
                    decision_picker=picker,
                    on_tick=on_tick,
                    on_tick_every=4,
                )
                summary = None
                path = ROOT / "runs" / str(rid) / "summary.json"
                if path.exists():
                    summary = json.loads(path.read_text(encoding="utf-8"))
                world = None
                if summary:
                    world = summary.get("final") or {}
                    world["metrics"] = summary.get("metrics") or {}
                    world["tick"] = summary.get("ticks")
                self._set(status="done", score=score, run_id=rid, decision=None, world=world or self.state.get("world"))
            except Exception as exc:
                self._set(status="error", error=str(exc), decision=None)

        self.thread = threading.Thread(target=run, daemon=True)
        self.thread.start()

    def choose(self, edict: str) -> None:
        self._set(status="running", decision=None)
        self.choice_q.put(edict)


GAME = Game()


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        return

    def _json(self, obj, code=200):
        raw = json.dumps(obj).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(raw)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(raw)

    def _html(self, text):
        raw = text.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def do_GET(self):
        path = urlparse(self.path).path
        if path in ("/", "/index.html"):
            self._html(HTML)
            return
        if path == "/api/state":
            self._json(GAME.snapshot())
            return
        self._json({"error": "not_found"}, 404)

    def do_POST(self):
        path = urlparse(self.path).path
        length = int(self.headers.get("Content-Length") or 0)
        body = self.rfile.read(length) if length else b"{}"
        try:
            data = json.loads(body.decode("utf-8") or "{}")
        except json.JSONDecodeError:
            self._json({"error": "bad_json"}, 400)
            return
        if path == "/api/start":
            GAME.start(int(data.get("seed") or 42), int(data.get("ticks") or 2500))
            self._json({"ok": True})
            return
        if path == "/api/choose":
            GAME.choose(str(data.get("edict") or "food"))
            self._json({"ok": True})
            return
        self._json({"error": "not_found"}, 404)


def main():
    p = argparse.ArgumentParser(description="AI-world playable web")
    p.add_argument("--host", default="0.0.0.0")
    p.add_argument("--port", type=int, default=8080)
    args = p.parse_args()
    httpd = ThreadingHTTPServer((args.host, args.port), Handler)
    print(f"AI-world playable on http://{args.host}:{args.port}", flush=True)
    httpd.serve_forever()


if __name__ == "__main__":
    main()
