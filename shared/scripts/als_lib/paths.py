"""Locations: plugin root, shared assets and the learner workspace."""
from __future__ import annotations

import json
import os
import re
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent
SHARED = SCRIPTS.parent
ROOT = SHARED.parent
TEMPLATES = SHARED / "templates"
DESIGN = SHARED / "design-systems"
SCHEMAS = SHARED / "schemas"

TEMPLATE_FOR_KIND = {
    "deck": "flashcards.html",
    "lesson": "lesson.html",
    "quiz": "trainer.html",
    "exam": "exam.html",
    "sheet": "sheet.html",
    "dashboard": "dashboard.html",
}


def version() -> str:
    try:
        return json.loads((ROOT / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))["version"]
    except (OSError, KeyError, ValueError):
        return "0"


def workspace(explicit: str | None = None) -> Path:
    """Resolve the learner workspace: --home flag, $ALS_HOME, else ./study."""
    if explicit:
        return Path(explicit).expanduser().resolve()
    env = os.environ.get("ALS_HOME")
    if env:
        return Path(env).expanduser().resolve()
    return (Path.cwd() / "study").resolve()


def module_dir(ws: Path, module_id: str) -> Path:
    return ws / "modules" / module_id


MODULE_ID = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def check_module_id(module_id: str) -> str:
    if not MODULE_ID.match(module_id or ""):
        raise ValueError(f"module id must be lowercase kebab-case, got {module_id!r}")
    return module_id


def module_of(path: Path) -> str | None:
    """If path is inside .../modules/<id>/..., return <id>."""
    parts = path.resolve().parts
    for i, p in enumerate(parts[:-1]):
        if p == "modules" and i + 1 < len(parts):
            return parts[i + 1]
    return None


def read_json(path: Path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def write_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    tmp.replace(path)
