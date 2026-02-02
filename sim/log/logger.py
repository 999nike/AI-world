cat > sim/log/logger.py << 'EOF'
import json
from pathlib import Path
from typing import Any, Dict

class RunLogger:
    def __init__(self, run_dir: Path):
        self.run_dir = run_dir
        self.events_path = run_dir / "events.jsonl"
        self.snapshots_path = run_dir / "snapshots.jsonl"

        self.run_dir.mkdir(parents=True, exist_ok=True)
        self._events_f = self.events_path.open("a", encoding="utf-8")
        self._snaps_f = self.snapshots_path.open("a", encoding="utf-8")

    def event(self, obj: Dict[str, Any]) -> None:
        self._events_f.write(json.dumps(obj) + "\n")
        self._events_f.flush()

    def snapshot(self, obj: Dict[str, Any]) -> None:
        self._snaps_f.write(json.dumps(obj) + "\n")
        self._snaps_f.flush()

    def close(self) -> None:
        self._events_f.close()
        self._snaps_f.close()
EOF