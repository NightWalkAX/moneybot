import json
from pathlib import Path
from typing import Any, Dict, Optional

MEMORY_ROOT = Path("memory/projects")


def _project_file(project: str) -> Path:
    safe_project = project.strip().replace("..", "_").replace("/", "_")
    project_dir = MEMORY_ROOT / safe_project
    project_dir.mkdir(parents=True, exist_ok=True)
    return project_dir / "memory.json"


def save_memory(project: str, key: str, value: Any) -> Dict[str, Any]:
    memory_file = _project_file(project)
    current = {}
    if memory_file.exists():
        current = json.loads(memory_file.read_text(encoding="utf-8") or "{}")
    current[key] = value
    memory_file.write_text(json.dumps(current, indent=2), encoding="utf-8")
    return current


def load_memory(project: str, key: Optional[str] = None) -> Any:
    memory_file = _project_file(project)
    if not memory_file.exists():
        return None if key else {}
    data = json.loads(memory_file.read_text(encoding="utf-8") or "{}")
    if key is None:
        return data
    return data.get(key)
