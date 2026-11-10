"""The learner workspace: profile, modules, remembered preferences."""
from __future__ import annotations

import datetime as dt
import re
from pathlib import Path

from .paths import check_module_id, module_dir, read_json, write_json

PROFILE_TEMPLATE = """---
name: {name}
programme: {programme}
timezone: {timezone}
languages: {languages}
theme: auto
session_minutes: 45
weekly_hours: 10
lms_url:
lesson_depth: medium        # brief | medium | deep (all lesson settings: als.py settings)
---

## Goals
{goals}

## How I learn best

## Remember

## Avoid
"""

MODULE_TEMPLATE = """---
id: {id}
title: {title}
code: {code}
term: {term}
exam_date: {exam_date}
subject: {subject}
theme: {theme}
lms_course_url:
---

## Overview

## Assessment

## Sources
| id | title | locator | file |
|---|---|---|---|

## Log
- {today}: Module created.
"""


def today() -> str:
    return dt.date.today().isoformat()


def frontmatter(text: str) -> dict[str, str]:
    """Parse a simple `key: value` front-matter block. No nesting, no YAML dependency."""
    m = re.match(r"^﻿?---\s*\n(.*?)\n---\s*(\n|$)", text, re.S)
    out: dict[str, str] = {}
    if not m:
        return out
    for line in m.group(1).splitlines():
        if not line.strip() or line.lstrip().startswith("#") or ":" not in line:
            continue
        key, _, val = line.partition(":")
        val = re.sub(r"\s+#.*$", "", val).strip().strip('"').strip("'")
        out[key.strip()] = val
    return out


def sections(text: str) -> dict[str, list[str]]:
    """Map '## Heading' -> list of non-empty lines under it."""
    out: dict[str, list[str]] = {}
    cur = None
    for line in text.splitlines():
        h = re.match(r"^##\s+(.+?)\s*$", line)
        if h:
            cur = h.group(1).strip()
            out[cur] = []
        elif cur and line.strip():
            out[cur].append(line.rstrip())
    return out


def init(ws: Path, name: str = "", programme: str = "", timezone: str = "", languages: str = "en", goals: str = "") -> list[Path]:
    created: list[Path] = []
    for sub in ("notes", "calendar", "modules"):
        p = ws / sub
        if not p.exists():
            p.mkdir(parents=True)
            created.append(p)
    prof = ws / "profile.md"
    if not prof.exists():
        g = "\n".join(f"- {x.strip()}" for x in goals.split(";") if x.strip())
        prof.write_text(PROFILE_TEMPLATE.format(name=name, programme=programme, timezone=timezone, languages=languages, goals=g), encoding="utf-8")
        created.append(prof)
    return created


def profile(ws: Path) -> dict:
    p = ws / "profile.md"
    if not p.exists():
        return {}
    text = p.read_text(encoding="utf-8")
    fm = frontmatter(text)
    fm["_sections"] = sections(text)
    return fm


def remember(ws: Path, text: str, section: str = "Remember") -> Path:
    """Append a dated bullet under '## <section>' in profile.md, creating the section if needed."""
    p = ws / "profile.md"
    if not p.exists():
        init(ws)
    body = p.read_text(encoding="utf-8")
    bullet = f"- {today()}: {' '.join(text.split())}"
    lines = body.splitlines()
    head = f"## {section}"
    try:
        i = next(k for k, line in enumerate(lines) if line.strip() == head)
    except StopIteration:
        if lines and lines[-1].strip():
            lines.append("")
        lines += [head, bullet]
    else:
        j = i + 1
        while j < len(lines) and not lines[j].startswith("## "):
            j += 1
        k = j
        while k > i + 1 and not lines[k - 1].strip():
            k -= 1
        lines.insert(k, bullet)
    p.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    return p


def new_module(ws: Path, module_id: str, title: str, code: str = "", term: str = "", exam_date: str = "", subject: str = "", theme: str = "") -> list[Path]:
    check_module_id(module_id)
    if exam_date:
        dt.date.fromisoformat(exam_date)
    md = module_dir(ws, module_id)
    created: list[Path] = []
    for sub in ("sources", "data", "out"):
        p = md / sub
        if not p.exists():
            p.mkdir(parents=True)
            created.append(p)
    mfile = md / "module.md"
    if not mfile.exists():
        mfile.write_text(MODULE_TEMPLATE.format(id=module_id, title=title, code=code, term=term, exam_date=exam_date, subject=subject or title, theme=theme, today=today()), encoding="utf-8")
        created.append(mfile)
    tfile = md / "topics.json"
    if not tfile.exists():
        write_json(tfile, {"als": "1", "kind": "topics", "module": module_id, "topics": []})
        created.append(tfile)
    efile = md / "errors.md"
    if not efile.exists():
        efile.write_text(f"# Error log: {title}\n", encoding="utf-8")
        created.append(efile)
    return created


def modules(ws: Path) -> list[dict]:
    out = []
    base = ws / "modules"
    if not base.is_dir():
        return out
    for d in sorted(p for p in base.iterdir() if p.is_dir()):
        info = {"id": d.name, "title": d.name, "path": d}
        mf = d / "module.md"
        if mf.exists():
            info.update({k: v for k, v in frontmatter(mf.read_text(encoding="utf-8")).items() if v})
        tf = d / "topics.json"
        info["topics"] = []
        if tf.exists():
            try:
                info["topics"] = read_json(tf).get("topics", [])
            except ValueError:
                info["topics_error"] = True
        out.append(info)
    return out


def module_info(ws: Path, module_id: str | None) -> dict:
    if not module_id:
        return {}
    mf = module_dir(ws, module_id) / "module.md"
    return frontmatter(mf.read_text(encoding="utf-8")) if mf.exists() else {}


def log(ws: Path, module_id: str, text: str) -> None:
    """Append a dated line under '## Log' in module.md."""
    mf = module_dir(ws, module_id) / "module.md"
    if not mf.exists():
        raise FileNotFoundError(mf)
    body = mf.read_text(encoding="utf-8").rstrip() + "\n"
    if "\n## Log" not in body:
        body += "\n## Log\n"
    body += f"- {today()}: {' '.join(text.split())}\n"
    mf.write_text(body, encoding="utf-8")


def add_note(ws: Path, title: str, text: str, module_id: str | None = None) -> Path:
    slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")[:50] or "note"
    p = ws / "notes" / f"{today()}-{slug}.md"
    n = 2
    while p.exists():
        p = ws / "notes" / f"{today()}-{slug}-{n}.md"
        n += 1
    p.parent.mkdir(parents=True, exist_ok=True)
    head = f"---\ntitle: {title}\ndate: {today()}\nmodule: {module_id or ''}\n---\n\n"
    p.write_text(head + text.strip() + "\n", encoding="utf-8")
    return p
