import json
from pathlib import Path
from typing import Any, Dict, Set


KEY_TYPES: Set[str] = {
    "run_started", "run_finished",
    "settlement_created", "age_transition", "subject_unlocked",
    "discovery",
    "raid", "soldier_defend",
    "scenario_event", "scenario_loaded", "scenario_start_inventory",
    "governor_command", "agent_controlled", "rival_governor",
    "decision_offered", "decision_taken",
    "build_funded",
    "outcome",
}


class RunLogger:
    def __init__(self, run_dir: Path, quiet: bool = False):
        self.run_dir = run_dir
        self.quiet = quiet
        self.events_path = run_dir / "events.jsonl"
        self.snapshots_path = run_dir / "snapshots.jsonl"

        self.run_dir.mkdir(parents=True, exist_ok=True)
        self._events_f = self.events_path.open("a", encoding="utf-8")
        self._snaps_f = self.snapshots_path.open("a", encoding="utf-8")

    def event(self, obj: Dict[str, Any]) -> None:
        if self.quiet:
            t = obj.get("type", "")
            if t in KEY_TYPES:
                pass
            elif t == "action_resolved" and str(obj.get("note", "")).startswith("built_"):
                pass
            else:
                return
        self._events_f.write(json.dumps(obj) + "\n")
        if not self.quiet:
            self._events_f.flush()

    def snapshot(self, obj: Dict[str, Any]) -> None:
        self._snaps_f.write(json.dumps(obj) + "\n")
        if not self.quiet:
            self._snaps_f.flush()

    def close(self) -> None:
        self._events_f.flush()
        self._snaps_f.flush()
        self._events_f.close()
        self._snaps_f.close()
