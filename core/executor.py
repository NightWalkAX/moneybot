from typing import Any, Dict, List

from core.llm import ask_llm, generate_code
from core.memory import save_memory


def execute_plan(plan: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
    steps: List[Dict[str, Any]] = []
    tools = context.get("tools", {})
    outputs = []

    for phase in plan.get("phases", []):
        phase_type = phase.get("type")
        name = phase.get("name", "unnamed")
        description = phase.get("description", "")
        step_record = {"phase": name, "type": phase_type, "description": description}

        try:
            if phase_type == "analysis":
                result = ask_llm(f"Analyze this phase: {description}")
            elif phase_type == "tool":
                tool_name = description.split()[0] if description else ""
                tool = tools.get(tool_name)
                if not tool:
                    result = f"unknown tool: {tool_name}"
                else:
                    result = str(tool(description))
            elif phase_type == "coding":
                result = generate_code(description)
            elif phase_type == "memory":
                project = context.get("project", "default")
                save_memory(project, name, description)
                result = "memory_saved"
            else:
                result = "unsupported_phase"

            step_record["result"] = result
            outputs.append(result)
        except Exception as exc:
            step_record["error"] = str(exc)
            outputs.append(f"error: {exc}")

        steps.append(step_record)

    return {"steps": steps, "result": "\n".join(str(x) for x in outputs)}
