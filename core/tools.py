import ast
import json
import re
from pathlib import Path
from typing import Any, Callable, Dict

from core.llm import ask_llm, generate_code
from core.memory import load_memory, save_memory
from core.planner import generate_plan
from core.skill_loader import load_skills

SKILLS_DIR = Path("skills")
AGENTS_DIR = Path("agents")


def _slugify(text: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9_]+", "_", text.strip().lower())
    return slug.strip("_") or "skill"


def create_skill(description: str) -> str:
    plan = generate_plan(description, context_memory={"scope": "skill_creation"})
    coding_phases = [p for p in plan.get("phases", []) if p.get("type") == "coding"]
    coding_context = "\n".join(f"- {p['name']}: {p['description']}" for p in coding_phases)

    prompt = (
        "Create a Python skill file that defines: def run(input, context): ...\n"
        "Return only Python code. No markdown.\n"
        "No system commands, no subprocess, no os.system.\n"
        f"Skill description: {description}\n"
        f"Coding phases:\n{coding_context or '- implement core logic'}\n"
    )
    code = generate_code(prompt)

    try:
        ast.parse(code)
    except SyntaxError as exc:
        raise ValueError(f"Generated code is invalid Python: {exc}")

    skill_name = f"generated_{_slugify(description)[:40]}"
    path = SKILLS_DIR / f"{skill_name}.py"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(code, encoding="utf-8")
    load_skills()
    return f"Skill created: {skill_name}"


def create_agent(name: str, description: str = "") -> str:
    AGENTS_DIR.mkdir(parents=True, exist_ok=True)
    safe = _slugify(name)
    agent_path = AGENTS_DIR / f"{safe}.json"
    payload = {
        "name": name,
        "description": description,
        "status": "created",
    }
    agent_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return f"Agent created: {safe}"


def get_tools(skills: Dict[str, Callable]) -> Dict[str, Callable]:
    tool_map: Dict[str, Callable] = {
        "create_skill": create_skill,
        "create_agent": create_agent,
        "ask_llm": ask_llm,
        "save_memory": save_memory,
        "load_memory": load_memory,
    }
    for skill_name, run_func in skills.items():
        tool_map[f"skill:{skill_name}"] = run_func
    return tool_map
