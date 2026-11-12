"""Lesson settings the student can tweak: how deep, how strict, how visual.

Stored as `lesson_*` keys in the front matter of profile.md (all modules) or modules/<id>/module.md
(one module). Resolution: module.md, then profile.md, then the default.
"""
from __future__ import annotations

import re
from pathlib import Path

from . import workspace
from .paths import module_dir

# key -> (allowed values or None for free text, default, what it does)
LESSON: dict[str, tuple[list[str] | None, str, str]] = {
    "lesson_depth": (["brief", "medium", "deep"], "medium",
                     "brief = key ideas only; medium = ideas, mechanism, examples, checks; deep = every step, every symbol, pitfalls, more recall"),
    "lesson_audience": (["first-time", "revision"], "first-time",
                        "first-time = orient first, concrete case before the rule, every term explained on first use; revision = compact, more recall"),
    "lesson_grounding": (["strict", "extended"], "strict",
                         "strict = only what the material says, every slide cites it; extended = may add flagged background"),
    "lesson_order": (["source", "teaching"], "source",
                     "source = follow the order of the slides/script; teaching = reorder for explanation (still citing)"),
    "lesson_ask": (["when-unclear", "always", "never"], "when-unclear",
                   "when-unclear = ask before guessing; always = confirm the outline first; never = leave unclear parts out and list them"),
    "lesson_checks": (["off", "normal", "many"], "normal",
                      "how often recall questions appear: off, every 4-6 slides, or every 2-3 slides"),
    "lesson_visuals": (["minimal", "balanced", "rich"], "balanced",
                       "minimal = text and formulas; balanced = a visual where the source has one; rich = a visual for every mechanism the source describes"),
    "lesson_notes": (["off", "short", "full"], "short",
                     "speaker notes: none, one or two sentences, or the full spoken explanation"),
    "lesson_explain": (["full", "short", "off"], "full",
                       "explanation written on the slides: full = what a lecturer would say, on every content slide; short = a sentence or two; off = keywords only (classic slides)"),
    "lesson_intuition": (["labelled", "off"], "labelled",
                         "analogies and examples of the tutor's own, always marked as not from the material: labelled = allowed, off = never"),
    "lesson_view": (["study", "present"], "study",
                    "how the page opens: study = explanations on the slide, present = compact slides (the reader can switch with V)"),
    "lesson_language": (None, "source",
                        "source = same language as the material; or a language name, e.g. German"),
}


# older or looser names that mean the same value
ALIASES: dict[str, dict[str, str]] = {"lesson_depth": {"standard": "medium", "normal": "medium", "short": "brief", "detailed": "deep"}}


def normalise(key: str, value: str) -> str:
    value = str(value or "").strip()
    return ALIASES.get(key, {}).get(value.lower(), value)


def resolve(ws: Path | None, module: str | None = None) -> dict[str, dict[str, str]]:
    """Return {key: {value, from, help}} for every lesson setting."""
    prof = workspace.profile(ws) if ws and (ws / "profile.md").exists() else {}
    mod = workspace.module_info(ws, module) if ws and module else {}
    out: dict[str, dict[str, str]] = {}
    for key, (allowed, default, text) in LESSON.items():
        value, origin = default, "default"
        for source, label in ((prof, "profile.md"), (mod, f"modules/{module}/module.md")):
            v = normalise(key, source.get(key))
            if v and (allowed is None or v in allowed):
                value, origin = v, label
        out[key] = {"value": value, "from": origin, "help": text}
    return out


def check(key: str, value: str) -> tuple[str, str]:
    """Return the full key and the normalised value, or raise ValueError."""
    key = key.strip()
    if not key.startswith("lesson_"):
        key = "lesson_" + key
    if key not in LESSON:
        raise ValueError(f"unknown setting {key!r}; choose from {', '.join(LESSON)}")
    allowed = LESSON[key][0]
    value = normalise(key, value)
    if allowed is not None and value not in allowed:
        raise ValueError(f"{key} must be one of {', '.join(allowed)}; got {value!r}")
    if not value or "\n" in value:
        raise ValueError(f"{key} needs a one-line value")
    return key, value


def set_frontmatter(path: Path, values: dict[str, str]) -> None:
    """Set `key: value` lines in a file's front matter, keeping every other line as it is."""
    text = path.read_text(encoding="utf-8") if path.exists() else ""
    m = re.match(r"^(﻿?---\s*\n)(.*?)(\n---\s*(?:\n|$))", text, re.S)
    if m:
        head, body, tail, rest = m.group(1), m.group(2), m.group(3), text[m.end():]
    else:
        head, body, tail, rest = "---\n", "", "\n---\n\n", text
    lines = body.splitlines()
    for key, value in values.items():
        new = f"{key}: {value}"
        for i, line in enumerate(lines):
            if re.match(rf"^{re.escape(key)}\s*:", line):
                lines[i] = new
                break
        else:
            lines.append(new)
    path.write_text(head + "\n".join(lines) + tail + rest, encoding="utf-8")


def save(ws: Path, pairs: dict[str, str], module: str | None = None) -> Path:
    values = dict(check(k, v) for k, v in pairs.items())
    if module:
        target = module_dir(ws, module) / "module.md"
        if not target.exists():
            raise FileNotFoundError(f"no module {module!r} in {ws} (create it with: als.py module new {module} --title ...)")
    else:
        target = ws / "profile.md"
        if not target.exists():
            workspace.init(ws)
    set_frontmatter(target, values)
    return target
