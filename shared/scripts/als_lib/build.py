"""Assemble a self-contained HTML page from a template, the design systems and a JSON data file."""
from __future__ import annotations

import html
import json
from pathlib import Path

from . import progress, themes, workspace
from .paths import TEMPLATE_FOR_KIND, TEMPLATES, module_of, read_json, version
from .validate import validate_data

EARLY = (
    "(function(){try{var m=localStorage.getItem('als:mode')||'auto';"
    "var d=m==='dark'||(m==='auto'&&window.matchMedia&&matchMedia('(prefers-color-scheme: dark)').matches);"
    "document.documentElement.setAttribute('data-als-mode',d?'dark':'light');}catch(e){}})();"
)


class BuildError(Exception):
    pass


def _safe_json(data) -> str:
    """JSON that cannot close the surrounding <script> element."""
    s = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
    return s.replace("</", "<\\/").replace("<!--", "<\\u0021--").replace("\u2028", "\\u2028").replace("\u2029", "\\u2029")


def choose_theme(data: dict, ws: Path | None, override: str | None = None) -> tuple[str, str]:
    valid = set(themes.names())
    if override:
        if override not in valid:
            raise BuildError(f"unknown theme {override!r}; choose from {sorted(valid)}")
        return override, "chosen with --theme"
    if data.get("theme") in valid:
        return data["theme"], "set in the data file"
    mod = data.get("module")
    if ws and mod:
        mt = workspace.module_info(ws, mod).get("theme")
        if mt in valid:
            return mt, f"set in modules/{mod}/module.md"
    if ws:
        pt = workspace.profile(ws).get("theme")
        if pt in valid:
            return pt, "set in profile.md"
    mod_info = workspace.module_info(ws, mod) if ws and mod else {}
    return themes.route(data.get("subject"), mod_info.get("subject"), mod_info.get("title"), data.get("title"))


def render(data: dict, theme: str) -> str:
    kind = data.get("kind")
    tpl_name = TEMPLATE_FOR_KIND.get(kind)
    if not tpl_name:
        raise BuildError(f"no template for kind {kind!r}")
    tpl = (TEMPLATES / tpl_name).read_text(encoding="utf-8")
    core = (TEMPLATES / "core.js").read_text(encoding="utf-8")
    reg = json.dumps(themes.runtime_registry(), ensure_ascii=False)
    out = (
        tpl.replace("{{lang}}", html.escape(data.get("lang") or "en", quote=True))
        .replace("{{theme}}", theme)
        .replace("{{title}}", html.escape(data.get("title", "Study"), quote=False))
        .replace("{{version}}", version())
    )
    for marker, value in (
        ("/*ALS:EARLY*/", EARLY),
        ("/*ALS:CSS*/", themes.css_bundle()),
        ("/*ALS:CORE*/", "window.ALS_THEMES=" + reg + ";\n" + core),
    ):
        if marker not in out:
            raise BuildError(f"template {tpl_name} is missing marker {marker}")
        out = out.replace(marker, value, 1)
    if "<!--ALS:DATA-->" not in out:
        raise BuildError(f"template {tpl_name} is missing the data marker")
    out = out.replace("<!--ALS:DATA-->", '<script type="application/json" id="als-data">' + _safe_json(data) + "</script>", 1)
    return out


def default_output(src: Path) -> Path:
    src = src.resolve()
    if src.parent.name == "data" and module_of(src):
        return src.parent.parent / "out" / (src.stem + ".html")
    return src.with_suffix(".html")


def build_file(src: Path, out: Path | None = None, theme: str | None = None, ws: Path | None = None, embed_due: bool = True) -> tuple[Path, str, str, list[str]]:
    data = read_json(src)
    errs, warns = validate_data(data)
    if errs:
        raise BuildError("data file is invalid:\n  " + "\n  ".join(errs))
    if ws is not None and not ws.exists():
        ws = None
    if embed_due and ws and data.get("kind") == "deck" and data.get("module"):
        ids = progress.due(ws, data["module"]).get(data["module"], [])
        known = {c["id"] for c in data["cards"]}
        data["_due"] = [i for i in ids if i in known]
    chosen, reason = choose_theme(data, ws, theme)
    page = render(data, chosen)
    out = (out or default_output(src)).resolve()
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(page, encoding="utf-8")
    return out, chosen, reason, warns


def build_data(data: dict, out: Path, theme: str) -> Path:
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(render(data, theme), encoding="utf-8")
    return out
