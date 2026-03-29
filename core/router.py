import json
import os
from typing import Any, Dict, List

from core.llm import chat_completion

ROUTER_MODEL = os.getenv("ROUTER_MODEL", "qwen/qwen2.5-7b-instruct:free")


def _default_decision(reason: str = "fallback to respond") -> Dict[str, Any]:
    return {"action": "respond", "tool_name": None, "reason": reason}


def route(user_input: str, available_tools: List[str]) -> Dict[str, Any]:
    system_prompt = (
        "You are a FAST ROUTER. Return strict JSON only with keys: action, tool_name, reason. "
        "Action must be one of: respond, tool, plan, create_skill, create_agent. "
        "Prefer simplest valid action. Avoid planning unless necessary. "
        "Prefer existing tools over creating new ones. Keep reason short."
    )
    user_prompt = json.dumps(
        {
            "user_input": user_input,
            "available_tools": available_tools,
            "schema": {
                "action": "respond | tool | plan | create_skill | create_agent",
                "tool_name": "optional",
                "reason": "short explanation",
            },
        }
    )

    raw = chat_completion(
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        model=ROUTER_MODEL,
        temperature=0.0,
        max_tokens=200,
        require_json=True,
    )
    try:
        decision = json.loads(raw)
    except json.JSONDecodeError:
        return _default_decision("invalid json from router")

    action = decision.get("action")
    if action not in {"respond", "tool", "plan", "create_skill", "create_agent"}:
        return _default_decision("invalid action from router")

    tool_name = decision.get("tool_name")
    if action == "tool" and (not tool_name or tool_name not in available_tools):
        return _default_decision("unknown tool selected")

    return {
        "action": action,
        "tool_name": tool_name,
        "reason": str(decision.get("reason", ""))[:200],
    }
