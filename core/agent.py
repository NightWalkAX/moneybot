import time
from typing import Any, Dict, List

from core.executor import execute_plan
from core.learning import analyze_and_improve
from core.memory import load_memory, save_memory
from core.planner import generate_plan
from core.router import route
from core.skill_loader import load_skills
from core.telemetry import log_telemetry
from core.tools import create_agent, create_skill, get_tools


class AgentCore:
    def __init__(self, project: str = "default") -> None:
        self.project = project

    def process_input(self, user_input: str) -> str:
        start = time.time()
        context_memory = load_memory(self.project) or {}
        skills = load_skills()
        tools = get_tools(skills)

        decision = route(user_input, list(tools.keys()))
        steps: List[Dict[str, Any]] = []
        tools_used: List[str] = []
        errors: List[str] = []
        plan = None
        result = ""
        success = True

        try:
            action = decision["action"]
            if action == "respond":
                tools_used.append("ask_llm")
                result = tools["ask_llm"](user_input)
            elif action == "tool":
                tool_name = decision.get("tool_name")
                tool = tools.get(tool_name)
                if not tool:
                    result = f"Tool not found: {tool_name}"
                    success = False
                    errors.append(result)
                elif tool_name.startswith("skill:"):
                    tools_used.append(tool_name)
                    result = str(tool(user_input, {"project": self.project, "memory": context_memory}))
                elif tool_name == "create_skill":
                    tools_used.append(tool_name)
                    result = create_skill(user_input)
                elif tool_name == "create_agent":
                    tools_used.append(tool_name)
                    result = create_agent(user_input)
                else:
                    tools_used.append(tool_name)
                    result = str(tool(user_input))
            elif action == "plan":
                plan = generate_plan(user_input, context_memory)
                exec_result = execute_plan(plan, {"tools": tools, "project": self.project})
                steps = exec_result.get("steps", [])
                for step in steps:
                    if step.get("type") == "tool":
                        tools_used.append(step.get("phase", "unknown_tool_phase"))
                    if "error" in step:
                        errors.append(step["error"])
                result = exec_result.get("result", "")
            elif action == "create_skill":
                tools_used.append("create_skill")
                result = create_skill(user_input)
            elif action == "create_agent":
                tools_used.append("create_agent")
                result = create_agent(user_input)
            else:
                result = "Unsupported action"
                success = False
                errors.append(result)
        except Exception as exc:
            result = f"Error: {exc}"
            success = False
            errors.append(str(exc))

        duration = round(time.time() - start, 3)
        save_memory(self.project, "last_input", user_input)
        save_memory(self.project, "last_output", result)
        save_memory(self.project, "last_duration_seconds", duration)

        telemetry_entry: Dict[str, Any] = {
            "input": user_input,
            "decision": decision,
            "plan": plan,
            "steps": steps,
            "tools_used": tools_used,
            "execution_time": duration,
            "errors": errors,
            "result": result,
            "success": success,
        }
        logged = log_telemetry(telemetry_entry)
        analyze_and_improve(logged)

        return result
