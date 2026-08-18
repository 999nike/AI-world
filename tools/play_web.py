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
.cell {
  width: 14px; height: 14px; border-radius: 2px; background: #1a1814;
  display: flex; align-items: center; justify-content: center;
  font: 7px/1 var(--font-mono); color: color-mix(in oklab, var(--fg) 72%, transparent);
  user-select: none;
}
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
.cell.rival-agent { background: #c47a62; color: transparent; }
.cell.agent { color: transparent; }
.cell.rival { box-shadow: inset 0 0 0 1px #a85a48; }
.town.rival { border-color: color-mix(in oklab, #c47a62 45%, transparent); }
.city { margin-bottom: var(--space-4); }
.city h2 { font-family: var(--font-display); font-size: 1.35rem; font-weight: 600; letter-spacing: -0.02em; margin: 0 0 4px; }
.city .lead { color: var(--fg-muted); margin: 0; font-size: 0.95rem; }
.chain { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 12px; }
.chain span { color: var(--fg-subtle); font-size: 0.8rem; }
.chain span.on { color: var(--fg); }
.bar { height: 4px; background: var(--bg); border-radius: 99px; margin-top: 10px; overflow: hidden; }
.bar > i { display: block; height: 100%; background: var(--ok); width: 0%; }
.bar.low > i { background: var(--danger); }
.chip {
  display: inline-block; font-size: 0.68rem; letter-spacing: 0.06em;
  text-transform: uppercase; color: var(--fg-subtle);
  border: 1px solid var(--border); border-radius: 99px;
  padding: 2px 7px; margin: 6px 4px 0 0;
}
.vs { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; }
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
.banner.win { border: 1px solid color-mix(in oklab, var(--ok) 50%, transparent); }
.banner.lose { border: 1px solid color-mix(in oklab, var(--danger) 50%, transparent); }
.banner.draw { border: 1px solid var(--border); }
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
        <div class="sub">Watch the settlement. When the world asks, you choose. The clock can end it.</div>
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
        The map is the city. Farms, libraries, people. Chronicle speaks in sentences.
        You hold the west. They hold the east. When the world asks, pick feed, science, or army.
      </p>
    </div>

    <div id="play" class="hidden">
      <div class="row">
        <div class="col" style="flex:1">
          <div class="panel">
            <div id="city"></div>
            <div class="stats" id="stats"></div>
            <div class="map-wrap" style="margin-top:16px"><div id="map"></div></div>
            <div class="legend">Pale people · clay rival · F farm · B barracks · L library · R lab · V observatory · + town</div>
          </div>
        </div>
        <div class="col side">
          <div class="panel">
            <div class="kicker">Edict</div>
            <div class="meta" style="color:var(--fg-muted);margin:6px 0 10px;font-size:0.8rem">Win: observatory + 2 discoveries, wipe them, or era 4 with more people when the clock ends.</div>
            <div id="askBox">
              <div class="banner" id="statusBanner">Running…</div>
              <div class="prompt" id="prompt"></div>
              <div class="edicts" id="edicts"></div>
            </div>
          </div>
          <div class="panel">
            <div class="kicker">Towns</div>
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
let lastRaidTick = -1;
let lastTick = -1;
let lastOutcomeTick = -1;
let prevWorld = null;

const GLYPH = {
  farm:"F", storage:"S", hut:"H", granary:"G", mine:"M", road:".",
  workshop:"W", barracks:"B", market:"K", temple:"T", academy:"C",
  walls:"#", irrigation:"~", library:"L", foundry:"Y", hall:"O",
  command:"X", lab:"R", observatory:"V",
};
const EDICT_LINE = {
  food: "You chose to feed the people.",
  science: "You chose to pursue science.",
  army: "You chose to raise the army.",
};

function logLine(t) {
  const el = $("log");
  const d = document.createElement("div");
  d.textContent = t;
  el.prepend(d);
}

function splitTowns(world) {
  const towns = (world && world.settlements) || [];
  return {
    you: towns.filter(s => (s.faction||"player") === "player"),
    them: towns.filter(s => s.faction === "rival"),
  };
}

function foodDays(s) {
  const pop = Number(s.population||0);
  const sold = Number(s.soldiers||0);
  const need = pop * 0.22 + sold * 0.03;
  const food = Number(s.food_stock||0);
  if (need <= 0) return null;
  return food / need;
}

function capital(towns) {
  if (!towns.length) return null;
  return towns.slice().sort((a,b) => Number(b.population||0) - Number(a.population||0))[0];
}

function ownStructs(world, fac) {
  return (world.structures||[]).filter(s => (s.faction||"player") === fac);
}

function renderCity(world) {
  const el = $("city");
  if (!el) return;
  const {you, them} = splitTowns(world);
  const cap = capital(you);
  const rcap = capital(them);
  const west = ownStructs(world, "player");
  const has = t => west.some(s => s.type === t);
  const disc = you.reduce((a,s)=>a + Number(s.discoveries||0), 0);
  const days = cap ? foodDays(cap) : null;
  const people = you.reduce((a,s)=>a + Number(s.population||0), 0);
  let lead;
  if (!cap) lead = "No town yet. The people are still walking.";
  else if (days == null) lead = `${people} people.`;
  else if (days < 1) lead = `${people} people. Food is short.`;
  else lead = `${people} people. ${Math.floor(days)} days of food.`;
  const title = cap ? `${cap.id} · era ${cap.era||2}` : "No town yet";
  const chain = [
    ["Library", has("library")],
    ["Lab", has("lab")],
    ["Observatory", has("observatory")],
    [disc + "/2 discoveries", disc >= 2],
  ];
  const rivalLine = rcap
    ? `Rival ${rcap.id} is era ${rcap.era||2}, ${them.reduce((a,s)=>a+Number(s.population||0),0)} people.`
    : "No rival town yet.";
  const fill = days == null ? 0 : Math.max(0, Math.min(100, (days / 20) * 100));
  const low = days != null && days < 3;
  el.innerHTML = `<h2>${title}</h2>
    <p class="lead">${lead}</p>
    <p class="lead" style="margin-top:4px">${rivalLine}</p>
    <div class="chain">${chain.map(([n,on]) => `<span class="${on?"on":""}">${n}</span>`).join("")}</div>
    <div class="bar${low?" low":""}"><i style="width:${fill.toFixed(0)}%"></i></div>`;
}

function renderStats(world) {
  const {you, them} = splitTowns(world);
  const daysList = you.map(foodDays).filter(d => d != null);
  const days = daysList.length ? Math.min(...daysList) : null;
  const items = [
    ["Tick", world ? world.tick : "—"],
    ["People", you.reduce((a,s)=>a + Number(s.population||0), 0)],
    ["Rival", them.reduce((a,s)=>a + Number(s.population||0), 0)],
    ["Food", days == null ? "—" : (days < 1 ? "short" : Math.floor(days) + "d")],
    ["Soldiers", you.reduce((a,s)=>a + Number(s.soldiers||0), 0).toFixed(1)],
    ["Raids", (world.metrics||{}).raid_events || 0],
  ];
  $("stats").innerHTML = items.map(([k,v]) => `<div class="stat"><span>${k}</span><b>${v}</b></div>`).join("");
}

function cellClass(world, x, y) {
  const agent = (world.agents||[]).find(a => a.x===x && a.y===y);
  if (agent) return agent.faction === "rival" ? "rival-agent" : "agent";
  const st = (world.structures||[]).find(s => s.x===x && s.y===y);
  if (st && st.type) return st.faction === "rival" ? st.type + " rival" : st.type;
  const town = (world.settlements||[]).find(s => s.x===x && s.y===y);
  if (town) return town.faction === "rival" ? "settlement rival" : "settlement";
  return "";
}

function cellMark(world, x, y) {
  const agent = (world.agents||[]).find(a => a.x===x && a.y===y);
  if (agent) return "";
  const st = (world.structures||[]).find(s => s.x===x && s.y===y);
  if (st && GLYPH[st.type]) return GLYPH[st.type];
  const town = (world.settlements||[]).find(s => s.x===x && s.y===y);
  if (town) return "+";
  return "";
}

function cellTitle(world, x, y) {
  const agent = (world.agents||[]).find(a => a.x===x && a.y===y);
  if (agent) return agent.faction === "rival" ? "rival" : "yours";
  const st = (world.structures||[]).find(s => s.x===x && s.y===y);
  if (st && st.type) return st.type;
  const town = (world.settlements||[]).find(s => s.x===x && s.y===y);
  if (town) return town.id;
  return "";
}

function renderMap(world) {
  if (!world) return;
  const w = world.width||32, h = world.height||32;
  const map = $("map");
  map.style.gridTemplateColumns = `repeat(${w}, 14px)`;
  let html = "";
  for (let y=0;y<h;y++) for (let x=0;x<w;x++) {
    const t = cellTitle(world,x,y);
    html += `<div class="cell ${cellClass(world,x,y)}"${t?` title="${t}"`:""}>${cellMark(world,x,y)}</div>`;
  }
  map.innerHTML = html;
}

function renderTowns(world) {
  const {you, them} = splitTowns(world);
  const block = (list, rival) => {
    if (!list.length) return `<div class="meta" style="color:var(--fg-muted)">${rival?"No rival town yet.":"None yet."}</div>`;
    return list.map(s => {
      const days = foodDays(s);
      const foodBit = days == null ? "no mouths" : (days < 1 ? "food is short" : Math.floor(days) + " days of food");
      const chips = (s.subjects||[]).map(sub => `<span class="chip">${sub}</span>`).join("");
      const fill = days == null ? 0 : Math.max(0, Math.min(100, (days / 20) * 100));
      const low = days != null && days < 3;
      return `<div class="town${rival?" rival":""}"><strong>${s.id}</strong> · era ${s.era||2}
        <div class="meta">${s.population||0} people · ${foodBit}${Number(s.soldiers||0)>0.5?` · ${Number(s.soldiers).toFixed(1)} soldiers`:""}</div>
        <div class="bar${low?" low":""}"><i style="width:${fill.toFixed(0)}%"></i></div>
        ${chips}</div>`;
    }).join("");
  };
  $("towns").innerHTML = `<div class="kicker" style="margin-bottom:6px">You</div>${block(you,false)}
    <div class="kicker" style="margin:12px 0 6px">Rival</div>${block(them,true)}`;
}

function chronicleDiff(world) {
  if (!prevWorld) { prevWorld = world; return; }
  const oldBy = {};
  for (const s of prevWorld.settlements||[]) oldBy[s.id] = s;
  for (const s of world.settlements||[]) {
    const o = oldBy[s.id];
    const whose = s.faction === "rival" ? "They founded" : "We founded";
    if (!o) { logLine(`${whose} ${s.id}.`); continue; }
    if (Number(s.era||2) > Number(o.era||2)) logLine(`${s.id} reached era ${s.era}.`);
    const had = new Set(o.subjects||[]);
    for (const sub of (s.subjects||[])) {
      if (!had.has(sub)) logLine(`${s.id} unlocked ${sub}.`);
    }
    if (Number(s.discoveries||0) > Number(o.discoveries||0)) logLine(`${s.id} made a discovery.`);
    if (Number(s.population||0) < Number(o.population||0)) logLine(`${s.id} lost people.`);
  }
  const risen = {
    library: "A library rose",
    lab: "A lab rose",
    observatory: "An observatory rose",
    barracks: "Barracks rose",
    academy: "An academy rose",
  };
  for (const [typ, line] of Object.entries(risen)) {
    const n = (w, fac) => (w.structures||[]).filter(s => s.type===typ && (s.faction||"player")===fac).length;
    if (n(world,"player") > n(prevWorld,"player")) logLine(`${line} in the west.`);
    if (n(world,"rival") > n(prevWorld,"rival")) logLine(`${line} in the east.`);
  }
  prevWorld = world;
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
    const o = state.outcome;
    const {you, them} = splitTowns(state.world);
    const yp = you.reduce((a,s)=>a+Number(s.population||0),0);
    const tp = them.reduce((a,s)=>a+Number(s.population||0),0);
    if (o && o.winner) {
      const cls = o.winner === "player" ? "win" : (o.winner === "rival" ? "lose" : "draw");
      const title = o.winner === "player" ? "You win" : (o.winner === "rival" ? "They win" : "Draw");
      banner.className = "banner " + cls;
      banner.textContent = `${title} — ${o.kind || "survival"}`;
      prompt.textContent = o.reason || "";
    } else {
      banner.className = "banner";
      const hold = yp > tp ? "You hold more people." : (tp > yp ? "The rival outgrew you." : "Even on people.");
      banner.textContent = `Finished. Score ${state.score ?? "—"}. ${hold}`;
      prompt.textContent = "";
    }
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
    renderCity(world);
    renderStats(world);
    renderMap(world);
    renderTowns(world);
    chronicleDiff(world);
    const raid = (world.metrics||{}).last_raid;
    if (raid && raid.tick !== lastRaidTick) {
      lastRaidTick = raid.tick;
      const us = raid.attacker_faction === "player";
      logLine(`${us ? "We raided" : "They raided"} ${raid.target}.`);
    }
  }
  renderDecision(state);
  if (state.status === "done") {
    if (state.outcome && state.outcome.reason && lastOutcomeTick < 0) {
      lastOutcomeTick = state.outcome.tick ?? lastTick;
      const o = state.outcome;
      const title = o.winner === "player" ? "You win" : (o.winner === "rival" ? "They win" : "Draw");
      logLine(`${title} — ${o.reason}`);
    }
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
  lastRaidTick = -1;
  lastOutcomeTick = -1;
  prevWorld = null;
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
  logLine(EDICT_LINE[id] || `You chose ${id}.`);
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
        self._set(status="running", world=None, decision=None, score=None, run_id=None, error=None, outcome=None)

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
                    rival_agents=4,
                )
                summary = None
                path = ROOT / "runs" / str(rid) / "summary.json"
                if path.exists():
                    summary = json.loads(path.read_text(encoding="utf-8"))
                world = None
                if summary:
                    world = summary.get("final") or {}
                    world["metrics"] = summary.get("metrics") or {}
                    world["tick"] = (summary.get("final") or {}).get("tick", summary.get("ticks_ran") or summary.get("ticks"))
                self._set(
                    status="done", score=score, run_id=rid, decision=None,
                    world=world or self.state.get("world"),
                    outcome=(summary or {}).get("outcome"),
                )
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
