import json
from typing import Any, Dict

from core.llm import chat_completion

PLANNER_MODEL = "meta-llama/llama-3-8b-instruct"


def _validate_plan(plan: Dict[str, Any]) -> Dict[str, Any]:
    if not isinstance(plan, dict):
        raise ValueError("Plan must be an object")
    if "goal" not in plan or not isinstance(plan["goal"], str):
        raise ValueError("Plan missing goal")
    if "phases" not in plan or not isinstance(plan["phases"], list):
        raise ValueError("Plan missing phases")

    valid_types = {"analysis", "tool", "coding", "memory"}
    clean_phases = []
    for phase in plan["phases"]:
        if not isinstance(phase, dict):
            continue
        phase_type = phase.get("type")
        if phase_type not in valid_types:
            continue
        clean_phases.append(
            {
                "name": str(phase.get("name", "unnamed")),
                "description": str(phase.get("description", "")),
                "type": phase_type,
            }
        )
    if not clean_phases:
        raise ValueError("Plan has no valid phases")
    return {"goal": plan["goal"], "phases": clean_phases}


def generate_plan(user_input: str, context_memory: Dict[str, Any]) -> Dict[str, Any]:
    prompt = json.dumps(
        {
            "instruction": "Generate execution plan in strict JSON format.",
            "user_input": user_input,
            "context_memory": context_memory,
            "output_schema": {
                "goal": "string",
                "phases": [
                    {
                        "name": "string",
                        "description": "string",
                        "type": "analysis | tool | coding | memory",
                    }
                ],
            },
        }
    )
    raw = chat_completion(
        messages=[
            {"role": "system", "content": "You are a planning model that returns valid JSON only."},
            {"role": "user", "content": prompt},
        ],
        model=PLANNER_MODEL,
        temperature=0.1,
        max_tokens=800,
        require_json=True,
    )
    plan = json.loads(raw)
    return _validate_plan(plan)
