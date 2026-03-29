import importlib.util
from pathlib import Path
from typing import Any, Callable, Dict

SKILLS_DIR = Path("skills")


def load_skills() -> Dict[str, Callable[[Any, Dict[str, Any]], Any]]:
    SKILLS_DIR.mkdir(parents=True, exist_ok=True)
    loaded: Dict[str, Callable[[Any, Dict[str, Any]], Any]] = {}

    for skill_file in SKILLS_DIR.glob("*.py"):
        if skill_file.name.startswith("_"):
            continue
        module_name = f"skill_{skill_file.stem}"
        spec = importlib.util.spec_from_file_location(module_name, skill_file)
        if spec is None or spec.loader is None:
            continue
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        run_func = getattr(module, "run", None)
        if callable(run_func):
            loaded[skill_file.stem] = run_func
    return loaded
