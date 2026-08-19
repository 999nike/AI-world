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

HTML_PATH = Path(__file__).with_name("play_ui.html")
HTML = HTML_PATH.read_text(encoding="utf-8")


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
