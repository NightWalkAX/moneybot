import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

TELEMETRY_FILE = Path("data/logs/telemetry.json")


def _read_all() -> list:
    TELEMETRY_FILE.parent.mkdir(parents=True, exist_ok=True)
    if not TELEMETRY_FILE.exists():
        return []
    try:
        return json.loads(TELEMETRY_FILE.read_text(encoding="utf-8") or "[]")
    except json.JSONDecodeError:
        return []


def log_telemetry(entry: Dict[str, Any]) -> Dict[str, Any]:
    payload = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "input": entry.get("input", ""),
        "decision": entry.get("decision", {}),
        "plan": entry.get("plan"),
        "steps": entry.get("steps", []),
        "tools_used": entry.get("tools_used", []),
        "execution_time": entry.get("execution_time", 0),
        "errors": entry.get("errors", []),
        "result": entry.get("result", ""),
        "success": bool(entry.get("success", False)),
    }
    all_entries = _read_all()
    all_entries.append(payload)
    TELEMETRY_FILE.write_text(json.dumps(all_entries, indent=2), encoding="utf-8")
    return payload
