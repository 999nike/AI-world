#!/usr/bin/env python3
"""Watchable god-view. Same kernel. Human edicts hidden.

  PYTHONPATH=. python tools/play_web.py --host 0.0.0.0 --port 8080
"""
from __future__ import annotations

import argparse
import json
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from queue import Empty, Queue
from typing import Any, Dict, Optional
from urllib.parse import parse_qs, urlparse

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sim.core.simloop import run_sim  # noqa: E402

HTML = r"""<!DOCTYPE html>
<html lang="en"><head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>AI-world</title>
<style>
:root {
  --bg:#0b1016; --bg-elevated:#121821; --bg-subtle:#18202b;
  --fg:#e7eef6; --fg-muted:#8b9aab; --fg-subtle:#5d6b7a;
  --border: color-mix(in oklab, var(--fg) 10%, transparent);
  --accent:#c9d4e0; --accent-fg:#0b1016; --ok:#6fbf8a; --danger:#c45b55;
  --you:#d8d2c6; --them:#c47a62;
  --font-display:"Iowan Old Style", Palatino, Georgia, serif;
  --font-body:"Segoe UI", system-ui, sans-serif;
  --font-mono: ui-monospace, Menlo, Consolas, monospace;
}
*{box-sizing:border-box}
html,body{margin:0;background:var(--bg);color:var(--fg);font-family:var(--font-body);min-height:100%}
button,[role=button]{cursor:pointer} button:disabled{cursor:default;opacity:.4}
.shell{width:min(1280px,calc(100% - 24px));margin:0 auto;padding:16px 0 28px}
.topbar{display:flex;justify-content:space-between;align-items:center;gap:12px;margin-bottom:12px;flex-wrap:wrap}
h1{font-family:var(--font-display);font-weight:600;letter-spacing:-.03em;font-size:1.55rem;margin:0}
.sub{color:var(--fg-muted);font-size:.85rem;margin-top:2px}
.controls{display:flex;gap:8px;flex-wrap:wrap;align-items:center}
label.kicker{font-size:.68rem;letter-spacing:.1em;text-transform:uppercase;color:var(--fg-subtle);font-weight:600}
input[type=number]{height:38px;width:88px;background:var(--bg-subtle);color:var(--fg);border:1px solid var(--border);border-radius:8px;padding:0 10px;font:inherit;margin-left:6px}
.btn{height:38px;border:0;border-radius:8px;padding:0 14px;font:600 .88rem var(--font-body)}
.btn.primary{background:var(--accent);color:var(--accent-fg)}
.btn.ghost{background:transparent;color:var(--fg);border:1px solid var(--border)}
.btn.on{border-color:var(--ok);color:var(--ok)}
.hud{display:grid;grid-template-columns:repeat(6,1fr);gap:8px;margin-bottom:12px}
.stat{background:var(--bg-elevated);border:1px solid var(--border);border-radius:8px;padding:8px 10px}
.stat span{display:block;color:var(--fg-subtle);font-size:.68rem;letter-spacing:.08em;text-transform:uppercase}
.stat b{font-family:var(--font-mono);font-size:1.05rem;font-variant-numeric:tabular-nums}
.stat em{font-style:normal;color:var(--ok);font-size:.72rem;margin-left:4px}
.stat em.down{color:var(--danger)}
.ages{display:flex;margin-bottom:14px;overflow-x:auto;background:var(--bg-elevated);border:1px solid var(--border);border-radius:99px;padding:6px}
.age{flex:1;text-align:center;font-size:.68rem;letter-spacing:.08em;text-transform:uppercase;color:var(--fg-subtle);padding:6px 8px;white-space:nowrap;border-radius:99px}
.age.on{color:var(--fg);background:var(--bg-subtle)}
.age.now{color:var(--accent-fg);background:var(--accent);font-weight:700}
.stage{display:grid;grid-template-columns:260px 1fr 260px;gap:12px}
.panel{background:var(--bg-elevated);border:1px solid var(--border);border-radius:12px;padding:12px;min-width:0}
.kicker{font-size:.68rem;letter-spacing:.12em;text-transform:uppercase;color:var(--fg-subtle);font-weight:600;margin-bottom:8px}
.log{max-height:min(72vh,640px);overflow:auto;font-size:.82rem;line-height:1.4;color:var(--fg-muted)}
.log .ev{border-top:1px solid var(--border);padding:8px 0}
.log .ev b{display:block;color:var(--fg-subtle);font-size:.68rem;font-weight:600;letter-spacing:.06em}
.map-wrap{overflow:auto;background:#080c11;border-radius:10px;padding:10px}
#map{display:grid;gap:1px;width:max-content;margin:0 auto}
.cell{width:15px;height:15px;border-radius:2px;background:#15202c;display:flex;align-items:center;justify-content:center;font:7px/1 var(--font-mono);color:color-mix(in oklab,var(--fg) 70%,transparent);user-select:none}
#map.age-town .cell,#map.age-city .cell{width:16px;height:16px}
#map.age-science .cell{box-shadow:inset 0 0 0 1px color-mix(in oklab,#4a7a9a 18%,transparent)}
.cell.agent{background:var(--you);color:transparent}
.cell.rival-agent{background:var(--them);color:transparent}
.cell.settlement{background:#c4b8a4}.cell.farm{background:#4d6a45}.cell.storage{background:#6b5344}
.cell.hut{background:#8a6a4a}.cell.granary{background:#7a6238}.cell.mine{background:#5c5c5c}
.cell.road{background:#3a342c}.cell.workshop{background:#6e4f3a}.cell.barracks{background:#6a3d36}
.cell.market{background:#5a5e48}.cell.temple{background:#4a4e5c}.cell.academy{background:#3d5360}
.cell.walls{background:#2e2c2a}.cell.irrigation{background:#3d5a52}.cell.library{background:#4a6270}
.cell.foundry{background:#70483a}.cell.hall{background:#5a5044}.cell.command{background:#5a3a38}
.cell.lab{background:#3a5868}.cell.observatory{background:#2f3e55}
.cell.rival{box-shadow:inset 0 0 0 1px #a85a48}
.city h2{font-family:var(--font-display);font-size:1.2rem;margin:0 0 4px}
.city .lead{color:var(--fg-muted);margin:0 0 8px;font-size:.9rem}
.bar{height:4px;background:#080c11;border-radius:99px;overflow:hidden}
.bar>i{display:block;height:100%;background:var(--ok);width:0}
.bar.low>i{background:var(--danger)}
.meter{margin:8px 0}
.meter label{display:flex;justify-content:space-between;font-size:.75rem;color:var(--fg-muted)}
.meter .bar{margin:4px 0 0}
.chip{display:inline-block;font-size:.65rem;letter-spacing:.06em;text-transform:uppercase;color:var(--fg-subtle);border:1px solid var(--border);border-radius:99px;padding:2px 7px;margin:3px 4px 0 0}
.vs-line{font-size:.82rem;color:var(--fg-muted);margin:6px 0}
.legend{color:var(--fg-subtle);font-size:.7rem;line-height:1.45;margin-top:8px}
.banner{padding:8px 10px;border-radius:8px;background:var(--bg-subtle);margin-bottom:10px;font-size:.85rem}
.banner.win{border:1px solid color-mix(in oklab,var(--ok) 50%,transparent)}
.banner.lose{border:1px solid color-mix(in oklab,var(--danger) 50%,transparent)}
@media(max-width:980px){.stage{grid-template-columns:1fr}.hud{grid-template-columns:repeat(3,1fr)}.log{max-height:220px}}
</style></head>
<body>
<script>
(function(){try{if(window.parent===window)return;var ref=document.referrer||"",origin=null;
if(ref)origin=new URL(ref).origin;
if(!origin&&location.ancestorOrigins&&location.ancestorOrigins.length)origin=location.ancestorOrigins[0];
if(!origin)return;
var msg=function(type,extra){var o={channel:"grok-preview-bridge",version:1,type:type};if(extra)for(var k in extra)o[k]=extra[k];window.parent.postMessage(o,origin);};
msg("location",{path:location.pathname||"/",search:location.search,hash:location.hash});msg("ready");
window.addEventListener("message",function(ev){if(ev.source!==window.parent)return;if(!ev.data||ev.data.channel!=="grok-preview-bridge")return;
if(ev.data.type==="hello"){msg("location",{path:location.pathname||"/",search:location.search,hash:location.hash});msg("ready");}});}catch(e){}})();
</script>
<div class="shell">
  <div class="topbar">
    <div><h1>AI-world</h1><div class="sub">Watch the ages. Two peoples. Same map.</div></div>
    <div class="controls">
      <label class="kicker">Seed <input id="seed" type="number" value="42" min="1"/></label>
      <label class="kicker">Ticks <input id="ticks" type="number" value="8000" min="400" step="100"/></label>
      <button class="btn primary" id="begin">Watch</button>
      <button class="btn ghost" id="pauseBtn" disabled>Pause</button>
      <button class="btn ghost" data-speed="1">1×</button>
      <button class="btn ghost on" data-speed="2">2×</button>
      <button class="btn ghost" data-speed="4">4×</button>
      <button class="btn ghost" data-speed="0">Max</button>
    </div>
  </div>
  <div class="hud" id="hud"></div>
  <div class="ages" id="ages"></div>
  <div class="stage">
    <div class="panel"><div class="kicker">Event log</div><div class="log" id="log"></div></div>
    <div class="panel">
      <div id="statusBanner" class="banner">Pick a seed and watch.</div>
      <div class="map-wrap"><div id="map"></div></div>
      <div class="legend">Pale west · clay east · F farm · B barracks · L library · R lab · V observatory · + town</div>
    </div>
    <div class="panel city" id="city"></div>
  </div>
</div>
<script>
const $=id=>document.getElementById(id);
let timer=null,lastRaidTick=-1,lastTick=-1,lastOutcomeTick=-1,prevWorld=null,prevSample=null,paused=false,speed=2;
const GLYPH={farm:"F",storage:"S",hut:"H",granary:"G",mine:"M",road:".",workshop:"W",barracks:"B",market:"K",temple:"T",academy:"C",walls:"#",irrigation:"~",library:"L",foundry:"Y",hall:"O",command:"X",lab:"R",observatory:"V"};
const AGES=[["camp","Camp"],["era2","Settlement"],["era3","Town"],["era4","City"],["library","Library"],["lab","Lab"],["observatory","Observatory"]];
function logLine(tick,t){const d=document.createElement("div");d.className="ev";d.innerHTML=(tick==null?"":`<b>Tick ${tick}</b>`)+t;$("log").prepend(d);}
function splitTowns(world){const towns=(world&&world.settlements)||[];return{you:towns.filter(s=>(s.faction||"player")==="player"),them:towns.filter(s=>s.faction==="rival")};}
function foodDays(s){const need=Number(s.population||0)*0.22+Number(s.soldiers||0)*0.03;if(need<=0)return null;return Number(s.food_stock||0)/need;}
function capital(towns){if(!towns.length)return null;return towns.slice().sort((a,b)=>Number(b.population||0)-Number(a.population||0))[0];}
function ownStructs(world,fac){return (world.structures||[]).filter(s=>(s.faction||"player")===fac);}
function sum(list,k){return list.reduce((a,s)=>a+Number(s[k]||0),0);}
function fmtRate(cur,key){if(!prevSample)return "";const dt=Number(cur.tick||0)-Number(prevSample.tick||0);if(dt<=0)return "";const r=(Number(cur[key]||0)-Number(prevSample[key]||0))/dt*100;if(!isFinite(r)||Math.abs(r)<0.05)return "";return `${r>=0?"+":""}${r.toFixed(1)}`;}
function ageState(world){
  const {you}=splitTowns(world);const west=ownStructs(world,"player");const has=t=>west.some(s=>s.type===t);
  const era=you.reduce((a,s)=>Math.max(a,Number(s.era||2)),0);
  const on={camp:true,era2:you.length>0,era3:era>=3,era4:era>=4,library:has("library"),lab:has("lab"),observatory:has("observatory")};
  let now="camp";for(const [id] of AGES) if(on[id]) now=id; return {on,now};
}
function renderAges(world){
  const st=ageState(world||{});
  $("ages").innerHTML=AGES.map(([id,label])=>`<div class="age ${id===st.now?"now":(st.on[id]?"on":"")}">${label}</div>`).join("");
  const map=$("map"); map.classList.remove("age-town","age-city","age-science");
  if(st.on.library||st.on.lab||st.on.observatory) map.classList.add("age-science");
  else if(st.on.era4) map.classList.add("age-city");
  else if(st.on.era3) map.classList.add("age-town");
}
function sampleOf(world){const {you}=splitTowns(world);const tot=world.totals||{};return{tick:world.tick,food:tot.food??sum(you,"food_stock"),wood:tot.wood||0,stone:tot.stone||0,people:sum(you,"population"),soldiers:sum(you,"soldiers")};}
function renderHud(world){
  const s=sampleOf(world||{});
  const items=[["Food",s.food,fmtRate(s,"food")],["Wood",s.wood,fmtRate(s,"wood")],["Stone",s.stone,fmtRate(s,"stone")],["People",s.people,fmtRate(s,"people")],["Soldiers",Number(s.soldiers||0).toFixed(1),""],["Tick",s.tick??"—",""]];
  $("hud").innerHTML=items.map(([k,v,r])=>`<div class="stat"><span>${k}</span><b>${v}${r?`<em class="${String(r).startsWith("-")?"down":""}">${r}/100t</em>`:""}</b></div>`).join("");
}
function renderCity(world){
  const {you,them}=splitTowns(world||{});const cap=capital(you),rcap=capital(them);
  const people=sum(you,"population"),rp=sum(them,"population");const days=cap?foodDays(cap):null;
  const disc=sum(you,"discoveries");const west=ownStructs(world||{},"player");const has=t=>west.some(s=>s.type===t);
  let lead="The people are still walking.";
  if(cap&&days!=null&&days<1) lead=`${people} souls. Food is short.`; else if(cap) lead=`${people} souls in the west.`;
  const fill=days==null?0:Math.max(0,Math.min(100,(days/20)*100));const low=days!=null&&days<3;const mil=sum(you,"soldiers");
  const chips=((cap&&cap.subjects)||[]).map(sub=>`<span class="chip">${sub}</span>`).join("");
  $("city").innerHTML=`<div class="kicker">The west</div><h2>${cap?cap.id+" · era "+(cap.era||2):"No town yet"}</h2><p class="lead">${lead}</p>
    <div class="meter"><label><span>Food days</span><span>${days==null?"—":(days<1?"short":Math.floor(days)+"d")}</span></label><div class="bar${low?" low":""}"><i style="width:${fill.toFixed(0)}%"></i></div></div>
    <div class="meter"><label><span>Science path</span><span>${disc}/2 disc.</span></label><div class="bar"><i style="width:${Math.min(100,(has("library")?34:0)+(has("lab")?33:0)+(has("observatory")?33:0))}%"></i></div></div>
    <div class="meter"><label><span>Military</span><span>${mil.toFixed(1)}</span></label><div class="bar"><i style="width:${Math.min(100,mil*8)}%"></i></div></div>
    <div class="vs-line">${rcap?`East: ${rcap.id} era ${rcap.era||2} · ${rp} people`:"No rival town yet."}</div>${chips}`;
}
function cellClass(world,x,y){
  const agent=(world.agents||[]).find(a=>a.x===x&&a.y===y);
  if(agent) return agent.faction==="rival"?"rival-agent":"agent";
  const st=(world.structures||[]).find(s=>s.x===x&&s.y===y);
  if(st&&st.type) return st.faction==="rival"?st.type+" rival":st.type;
  const town=(world.settlements||[]).find(s=>s.x===x&&s.y===y);
  if(town) return town.faction==="rival"?"settlement rival":"settlement";
  return "";
}
function cellMark(world,x,y){
  if((world.agents||[]).some(a=>a.x===x&&a.y===y)) return "";
  const st=(world.structures||[]).find(s=>s.x===x&&s.y===y);
  if(st&&GLYPH[st.type]) return GLYPH[st.type];
  if((world.settlements||[]).some(s=>s.x===x&&s.y===y)) return "+";
  return "";
}
function cellTitle(world,x,y){
  const agent=(world.agents||[]).find(a=>a.x===x&&a.y===y);
  if(agent) return agent.faction==="rival"?"rival":"yours";
  const st=(world.structures||[]).find(s=>s.x===x&&s.y===y);
  if(st&&st.type) return st.type;
  const town=(world.settlements||[]).find(s=>s.x===x&&s.y===y);
  return town?town.id:"";
}
function renderMap(world){
  if(!world) return;
  const w=world.width||32,h=world.height||32,map=$("map");
  const size=(map.classList.contains("age-town")||map.classList.contains("age-city"))?16:15;
  map.style.gridTemplateColumns=`repeat(${w}, ${size}px)`;
  let html="";
  for(let y=0;y<h;y++) for(let x=0;x<w;x++){const t=cellTitle(world,x,y);html+=`<div class="cell ${cellClass(world,x,y)}"${t?` title="${t}"`:""}>${cellMark(world,x,y)}</div>`;}
  map.innerHTML=html;
}
function chronicleDiff(world){
  if(!prevWorld){prevWorld=world;return;}
  const tick=world.tick, oldBy={};
  for(const s of prevWorld.settlements||[]) oldBy[s.id]=s;
  for(const s of world.settlements||[]){
    const o=oldBy[s.id];
    if(!o){logLine(tick,`${s.faction==="rival"?"They founded":"We founded"} ${s.id}.`);continue;}
    if(Number(s.era||2)>Number(o.era||2)) logLine(tick,`${s.id} reached era ${s.era}.`);
    const had=new Set(o.subjects||[]);
    for(const sub of (s.subjects||[])) if(!had.has(sub)) logLine(tick,`${s.id} unlocked ${sub}.`);
    if(Number(s.discoveries||0)>Number(o.discoveries||0)) logLine(tick,`${s.id} made a discovery.`);
    if(Number(s.population||0)<Number(o.population||0)) logLine(tick,`${s.id} lost people.`);
  }
  const risen={library:"A library rose",lab:"A lab rose",observatory:"An observatory rose",barracks:"Barracks rose",academy:"An academy rose",farm:"Farms spread"};
  for(const [typ,line] of Object.entries(risen)){
    const n=(w,fac)=>(w.structures||[]).filter(s=>s.type===typ&&(s.faction||"player")===fac).length;
    if(n(world,"player")>n(prevWorld,"player")) logLine(tick,`${line} in the west.`);
    if(n(world,"rival")>n(prevWorld,"rival")) logLine(tick,`${line} in the east.`);
  }
  prevWorld=world;
}
function renderBanner(state){
  const banner=$("statusBanner");
  if(state.status==="done"){
    const o=state.outcome;
    if(o&&o.winner){banner.className="banner "+(o.winner==="player"?"win":(o.winner==="rival"?"lose":""));
      const title=o.winner==="player"?"The west holds":(o.winner==="rival"?"The east holds":"Even");
      banner.textContent=`${title} — ${o.kind||"survival"}. ${o.reason||""}`;}
    else {banner.className="banner";banner.textContent=`Finished. Score ${state.score??"—"}.`;}
  } else if(state.status==="error"){banner.className="banner lose";banner.textContent="Could not run. Hit Watch again.";$("begin").disabled=false;}
  else if(state.paused){banner.className="banner";banner.textContent="Paused.";}
  else if(state.status==="running"){banner.className="banner";banner.textContent="The ages are turning.";}
}
async function poll(){
  const state=await (await fetch("/api/state")).json();
  paused=!!state.paused; $("pauseBtn").textContent=paused?"Resume":"Pause";
  const world=state.world;
  if(world&&world.tick!==lastTick){
    lastTick=world.tick; renderAges(world); renderHud(world); renderMap(world); renderCity(world); chronicleDiff(world); prevSample=sampleOf(world);
    const raid=(world.metrics||{}).last_raid;
    if(raid&&raid.tick!==lastRaidTick){lastRaidTick=raid.tick;logLine(world.tick,`${raid.attacker_faction==="player"?"We raided":"They raided"} ${raid.target}.`);}
  }
  renderBanner(state);
  if(state.status==="done"){
    if(state.outcome&&state.outcome.reason&&lastOutcomeTick<0){
      lastOutcomeTick=state.outcome.tick??lastTick;
      const o=state.outcome; const title=o.winner==="player"?"The west holds":(o.winner==="rival"?"The east holds":"Even");
      logLine(lastOutcomeTick,`${title} — ${o.reason}`);
    }
    clearInterval(timer);timer=null;$("begin").disabled=false;$("pauseBtn").disabled=true;
  }
}
async function begin(){
  $("begin").disabled=true;$("pauseBtn").disabled=false;$("pauseBtn").textContent="Pause";
  $("log").innerHTML="";lastTick=-1;lastRaidTick=-1;lastOutcomeTick=-1;prevWorld=null;prevSample=null;paused=false;
  const seed=Number($("seed").value)||42, ticks=Number($("ticks").value)||8000;
  logLine(null,`Watching seed ${seed} · ${ticks} ticks`);
  try{const res=await fetch("/api/start",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({seed,ticks,speed})}); if(!res.ok) throw new Error("start");}
  catch(e){logLine(null,"Could not start. Hit Watch again.");$("begin").disabled=false;return;}
  if(timer) clearInterval(timer); timer=setInterval(poll,280); poll();
}
async function setControl(payload){await fetch("/api/control",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(payload)});}
$("begin").onclick=begin;
$("pauseBtn").onclick=()=>setControl({paused:!paused});
document.querySelectorAll("[data-speed]").forEach(btn=>{btn.onclick=()=>{speed=Number(btn.dataset.speed);document.querySelectorAll("[data-speed]").forEach(b=>b.classList.toggle("on",b===btn));setControl({speed});};});
renderAges({});renderHud({});renderCity({});
</script></body></html>
"""

DELAY = {0: 0.0, 1: 0.12, 2: 0.05, 4: 0.02}


class Game:
    def __init__(self) -> None:
        self.lock = threading.Lock()
        self.choice_q: Queue = Queue()
        self.thread: Optional[threading.Thread] = None
        self.generation = 0
        self.paused = False
        self.speed = 2
        self.state: Dict[str, Any] = {
            "status": "idle", "world": None, "decision": None,
            "paused": False, "speed": 2,
        }

    def snapshot(self) -> Dict[str, Any]:
        with self.lock:
            return json.loads(json.dumps(self.state))

    def _set(self, **kwargs) -> None:
        with self.lock:
            self.state.update(kwargs)

    def set_control(self, paused: Optional[bool] = None, speed: Optional[int] = None) -> None:
        with self.lock:
            if paused is not None:
                self.paused = bool(paused)
                self.state["paused"] = self.paused
            if speed is not None:
                self.speed = int(speed)
                self.state["speed"] = self.speed

    def start(self, seed: int, ticks: int, speed: Optional[int] = None) -> None:
        self.generation += 1
        gen = self.generation
        if speed is not None:
            self.speed = int(speed)
        self.paused = False
        try:
            self.choice_q.put_nowait("food")
        except Exception:
            pass
        while True:
            try:
                self.choice_q.get_nowait()
            except Empty:
                break
        self._set(
            status="running", world=None, decision=None, score=None,
            run_id=None, error=None, outcome=None, paused=False, speed=self.speed,
        )

        class Cancelled(Exception):
            pass

        def pace() -> None:
            while True:
                if gen != self.generation:
                    raise Cancelled()
                with self.lock:
                    paused = self.paused
                    spd = self.speed
                if not paused:
                    break
                time.sleep(0.05)
            delay = DELAY.get(int(spd), 0.05)
            if delay:
                time.sleep(delay)

        def on_tick(snap):
            if gen != self.generation:
                raise Cancelled()
            with self.lock:
                self.state["world"] = snap
                if self.state.get("status") != "decision":
                    self.state["status"] = "running"
            pace()

        def run():
            try:
                score, rid = run_sim(
                    seed=int(seed),
                    ticks=int(ticks),
                    snapshot_every=0,
                    return_score=True,
                    quiet=True,
                    playable=False,
                    on_tick=on_tick,
                    on_tick_every=4,
                    rival_agents=4,
                )
            except Cancelled:
                return
            except Exception as exc:
                if gen != self.generation:
                    return
                self._set(status="error", error=str(exc), decision=None)
                return
            if gen != self.generation:
                return
            summary = None
            path = ROOT / "runs" / str(rid) / "summary.json"
            if path.exists():
                summary = json.loads(path.read_text(encoding="utf-8"))
            world = None
            if summary:
                world = summary.get("final") or {}
                world["metrics"] = summary.get("metrics") or {}
                world["tick"] = (summary.get("final") or {}).get(
                    "tick", summary.get("ticks_ran") or summary.get("ticks")
                )
            self._set(
                status="done", score=score, run_id=rid, decision=None,
                world=world or self.state.get("world"),
                outcome=(summary or {}).get("outcome"),
            )

        self.thread = threading.Thread(target=run, daemon=True)
        self.thread.start()

    def choose(self, edict: str) -> None:
        self._set(status="running", decision=None)
        self.choice_q.put(edict)


GAME = Game()


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        return

    def _cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Cache-Control", "no-store")

    def _json(self, obj, code=200):
        raw = json.dumps(obj).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(raw)))
        self._cors()
        self.end_headers()
        self.wfile.write(raw)

    def _html(self, text):
        raw = text.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(raw)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(raw)

    def do_OPTIONS(self):
        self.send_response(204)
        self._cors()
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        if path in ("/", "/index.html"):
            self._html(HTML)
            return
        if path == "/api/state":
            self._json(GAME.snapshot())
            return
        if path == "/api/start":
            q = parse_qs(parsed.query)
            GAME.start(int((q.get("seed") or ["42"])[0] or 42), int((q.get("ticks") or ["8000"])[0] or 8000))
            self._json({"ok": True})
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
            GAME.start(
                int(data.get("seed") or 42),
                int(data.get("ticks") or 8000),
                speed=int(data["speed"]) if data.get("speed") is not None else None,
            )
            self._json({"ok": True})
            return
        if path == "/api/control":
            GAME.set_control(
                paused=bool(data["paused"]) if data.get("paused") is not None else None,
                speed=int(data["speed"]) if data.get("speed") is not None else None,
            )
            self._json({"ok": True, "paused": GAME.paused, "speed": GAME.speed})
            return
        if path == "/api/choose":
            GAME.choose(str(data.get("edict") or "food"))
            self._json({"ok": True})
            return
        self._json({"error": "not_found"}, 404)


def main():
    p = argparse.ArgumentParser(description="AI-world watchable web")
    p.add_argument("--host", default="0.0.0.0")
    p.add_argument("--port", type=int, default=8080)
    args = p.parse_args()
    httpd = ThreadingHTTPServer((args.host, args.port), Handler)
    print(f"AI-world watchable on http://{args.host}:{args.port}", flush=True)
    httpd.serve_forever()


if __name__ == "__main__":
    main()
