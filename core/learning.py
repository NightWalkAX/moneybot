import json
from pathlib import Path
from typing import Any, Dict

LEARNING_FILE = Path("memory/global/learning.json")


def _load_learning_state() -> Dict[str, Any]:
    LEARNING_FILE.parent.mkdir(parents=True, exist_ok=True)
    if not LEARNING_FILE.exists():
        return {"bad_patterns": [], "suggested_tools": [], "router_improvements": []}
    try:
        return json.loads(LEARNING_FILE.read_text(encoding="utf-8") or "{}")
    except json.JSONDecodeError:
        return {"bad_patterns": [], "suggested_tools": [], "router_improvements": []}


def analyze_and_improve(telemetry_entry: Dict[str, Any]) -> Dict[str, Any]:
    state = _load_learning_state()

    decision = telemetry_entry.get("decision", {})
    steps = telemetry_entry.get("steps", [])
    success = telemetry_entry.get("success", False)

    if decision.get("action") == "plan" and len(steps) <= 1:
        state["bad_patterns"].append("Unnecessary planning for simple request")
        state["router_improvements"].append("Prefer respond/tool for short direct prompts")

    if not success:
        state["bad_patterns"].append("Task failure detected")

    tool_steps = [s for s in steps if s.get("type") == "tool"]
    if any("unknown" in str(s.get("result", "")).lower() for s in tool_steps):
        state["bad_patterns"].append("Bad tool selection")
        state["router_improvements"].append("Check available tool names before choosing tool action")

    if any("manual" in str(s.get("result", "")).lower() for s in steps):
        state["suggested_tools"].append("Add dedicated automation tool for repeated manual operation")

    for key in ("bad_patterns", "suggested_tools", "router_improvements"):
        seen = set()
        deduped = []
        for item in state.get(key, []):
            if item not in seen:
                deduped.append(item)
                seen.add(item)
        state[key] = deduped[-100:]

    LEARNING_FILE.write_text(json.dumps(state, indent=2), encoding="utf-8")
    return state
