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

# FILE TOO LARGE FOR THIS FALLBACK - SEE LOCAL
