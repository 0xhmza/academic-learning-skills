"""Validate ALS data files.

A small JSON Schema subset validator (type, const, enum, required, properties, items, minItems,
minLength, minimum, maximum, allOf, anyOf, if/then/else, $ref to #/$defs) plus semantic checks that
schemas cannot express (unique ids, answer indexes in range, cloze markers, SVG ids).
"""
from __future__ import annotations

import re
from pathlib import Path

from . import viz_ids
from .paths import SCHEMAS, read_json

KIND_SCHEMA = {
    "deck": "deck.schema.json",
    "lesson": "lesson.schema.json",
    "quiz": "quiz.schema.json",
    "exam": "exam.schema.json",
    "sheet": "sheet.schema.json",
    "events": "events.schema.json",
}

_TYPES = {
    "string": lambda v: isinstance(v, str),
    "number": lambda v: isinstance(v, (int, float)) and not isinstance(v, bool),
    "integer": lambda v: isinstance(v, int) and not isinstance(v, bool),
    "boolean": lambda v: isinstance(v, bool),
    "array": lambda v: isinstance(v, list),
    "object": lambda v: isinstance(v, dict),
    "null": lambda v: v is None,
}


def _resolve(ref: str, root: dict) -> dict:
    if not ref.startswith("#/"):
        raise ValueError(f"unsupported $ref {ref}")
    node = root
    for part in ref[2:].split("/"):
        node = node[part]
    return node


def check(value, schema: dict, root: dict, path: str = "$") -> list[str]:
    errs: list[str] = []
    if "$ref" in schema:
        return check(value, _resolve(schema["$ref"], root), root, path)
    t = schema.get("type")
    if t is not None:
        types = t if isinstance(t, list) else [t]
        if not any(_TYPES[x](value) for x in types):
            return [f"{path}: expected {' or '.join(types)}, got {type(value).__name__}"]
    if "const" in schema and value != schema["const"]:
        errs.append(f"{path}: must be {schema['const']!r}")
    if "enum" in schema and value not in schema["enum"]:
        errs.append(f"{path}: must be one of {schema['enum']}, got {value!r}")
    if isinstance(value, str) and len(value) < schema.get("minLength", 0):
        errs.append(f"{path}: must not be empty")
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        if "minimum" in schema and value < schema["minimum"]:
            errs.append(f"{path}: must be >= {schema['minimum']}")
        if "maximum" in schema and value > schema["maximum"]:
            errs.append(f"{path}: must be <= {schema['maximum']}")
    if isinstance(value, dict):
        for req in schema.get("required", []):
            if req not in value:
                errs.append(f"{path}: missing required field '{req}'")
        for key, sub in schema.get("properties", {}).items():
            if key in value:
                errs.extend(check(value[key], sub, root, f"{path}.{key}"))
    if isinstance(value, list):
        if len(value) < schema.get("minItems", 0):
            errs.append(f"{path}: needs at least {schema['minItems']} item(s)")
        if "items" in schema:
            for i, item in enumerate(value):
                errs.extend(check(item, schema["items"], root, f"{path}[{i}]"))
    for sub in schema.get("allOf", []):
        errs.extend(check(value, sub, root, path))
    if "anyOf" in schema:
        if all(check(value, sub, root, path) for sub in schema["anyOf"]):
            errs.append(f"{path}: does not match any allowed form")
    if "if" in schema:
        if not check(value, schema["if"], root, path):
            if "then" in schema:
                errs.extend(check(value, schema["then"], root, path))
        elif "else" in schema:
            errs.extend(check(value, schema["else"], root, path))
    return errs


def _dupes(ids) -> list[str]:
    seen, dup = set(), []
    for i in ids:
        if i in seen and i not in dup:
            dup.append(i)
        seen.add(i)
    return dup


CLOZE_MARK = re.compile(r"\{\{c\d+::")
BLANK_MARK = re.compile(r"\{\{(\d+)\}\}")
SVG_ID = re.compile(r"""\bid\s*=\s*["']([^"']+)["']""")


NO_SRC_NEEDED = {"title", "summary"}
LONG_POINT = 220


def _step_tokens(p: str, s: dict, known: set[str], errs: list[str], warns: list[str]) -> None:
    """Check a diagram-like slide's steps: 'id' reveals, '-id' hides, '!id' emphasises for one step."""
    for g in s.get("steps") or []:
        for tok in g:
            name = tok[1:] if tok[:1] in "-!" else tok
            if s.get("layout") == "grid":
                cells = viz_ids.grid_expand(s, name)
                if not cells or any(c not in known for c in cells):
                    errs.append(f"{p}: step references {tok!r}, which matches no grid or cell")
            elif name not in known:
                where = "the SVG" if s.get("layout") == "diagram" else f"this {s.get('layout')} (ids: {', '.join(sorted(known)) or 'none'})"
                errs.append(f"{p}: step references id {name!r} which is not in {where}")
    caps = s.get("captions")
    if caps is not None and s.get("steps") and len(caps) != len(s["steps"]):
        warns.append(f"{p}: {len(caps)} captions for {len(s['steps'])} steps")


def _lesson(data: dict, errs: list[str], warns: list[str]) -> None:
    strict = data.get("grounding") == "strict"
    sources = data.get("sources") or []
    source_ids = [str(x.get("id")) for x in sources if isinstance(x, dict) and x.get("id")]
    if strict and not sources:
        errs.append("$.sources: a strict lesson lists the material it is built from, e.g. [{\"id\": \"L3\", \"title\": \"Lecture 3\", \"file\": \"sources/L03.pdf\"}]")
    for i, s in enumerate(data.get("slides", [])):
        p = f"$.slides[{i}]"
        layout = s.get("layout")
        src = str(s.get("src") or "").strip()
        if strict:
            if s.get("grounded") is False:
                errs.append(f"{p}: 'grounded: false' is not allowed in a strict lesson; remove the added content or ask the student to switch to extended grounding")
            if layout not in NO_SRC_NEEDED and not src:
                errs.append(f"{p}: strict grounding needs 'src' (where in the material this slide comes from)")
            if layout == "steps" and any(isinstance(r, dict) and r.get("grounded") is False for r in s.get("steps", [])):
                errs.append(f"{p}: a step is marked 'grounded: false' in a strict lesson")
        if src and source_ids and not any(part.strip().split(" ")[0] in source_ids for part in src.split(";")):
            warns.append(f"{p}: src {src!r} does not start with a listed source id ({', '.join(source_ids)})")
        if layout == "check":
            n = len(s.get("options", []))
            if isinstance(s.get("answer"), int) and s["answer"] >= n:
                errs.append(f"{p}: answer index {s['answer']} out of range for {n} options")
        known: set[str] | None = None
        if layout == "diagram":
            svg = s.get("svg", "")
            if not svg.lstrip().startswith("<svg"):
                errs.append(f"{p}: 'svg' must start with <svg")
            if re.search(r"<script|\bon\w+\s*=", svg, re.I):
                warns.append(f"{p}: scripts and event handlers are stripped from diagrams")
            known = set(SVG_ID.findall(svg))
        elif layout in viz_ids.KINDS:
            known, problems = viz_ids.ids(s)
            errs.extend(f"{p}: {msg}" for msg in problems)
        if known is not None:
            _step_tokens(p, s, known, errs, warns)
        if layout == "code":
            lines = len(str(s.get("code", "")).splitlines())
            for g in s.get("highlight", []):
                for ln in g:
                    if ln < 1 or ln > lines:
                        errs.append(f"{p}: highlight line {ln} outside 1..{lines}")
        if layout == "table":
            width = len(s.get("columns") or (s.get("rows") or [[]])[0])
            for k, row in enumerate(s.get("rows", [])):
                if len(row) != width:
                    errs.append(f"{p}: row {k + 1} has {len(row)} cells, expected {width}")
        if layout == "figure":
            for k, m in enumerate(s.get("marks", [])):
                if m.get("x", 0) + m.get("w", 0) > 100.5 or m.get("y", 0) + m.get("h", 0) > 100.5:
                    errs.append(f"{p}: mark {k + 1} leaves the image (x + w and y + h are percentages and must stay within 100)")
        if layout in ("points", "summary"):
            pts = s.get("points", [])
            if layout == "points" and len(pts) > 6:
                warns.append(f"{p}: {len(pts)} points on one slide; consider splitting (max ~6)")
            if any(len(str(x)) > LONG_POINT for x in pts):
                warns.append(f"{p}: a point is longer than {LONG_POINT} characters; slides hold short claims, move the rest to 'notes' or 'more'")


def semantic(data: dict) -> tuple[list[str], list[str]]:
    """Return (errors, warnings) the schema cannot express."""
    errs: list[str] = []
    warns: list[str] = []
    kind = data.get("kind")
    if kind == "deck":
        cards = data.get("cards", [])
        for d in _dupes([c.get("id") for c in cards]):
            errs.append(f"duplicate card id {d!r}")
        for i, c in enumerate(cards):
            if c.get("type") == "cloze" and not CLOZE_MARK.search(c.get("text", "")):
                errs.append(f"$.cards[{i}]: cloze text needs at least one {{{{c1::answer}}}} marker")
            if c.get("type") != "cloze" and len(str(c.get("front", ""))) > 400:
                warns.append(f"$.cards[{i}]: front is long ({len(c['front'])} chars); atomic cards are recalled better")
    elif kind == "quiz":
        qs = data.get("questions", [])
        for d in _dupes([q.get("id") for q in qs]):
            errs.append(f"duplicate question id {d!r}")
        for i, q in enumerate(qs):
            p = f"$.questions[{i}]"
            n = len(q.get("options", []) or [])
            if q.get("type") == "mcq" and isinstance(q.get("answer"), int) and q["answer"] >= n:
                errs.append(f"{p}: answer index {q['answer']} is out of range for {n} options")
            if q.get("type") == "multi" and isinstance(q.get("answer"), list):
                bad = [a for a in q["answer"] if not isinstance(a, int) or a >= n]
                if bad:
                    errs.append(f"{p}: answer indexes {bad} out of range for {n} options")
            if q.get("type") == "cloze":
                marks = sorted({int(m) for m in BLANK_MARK.findall(q.get("text", ""))})
                want = list(range(1, len(q.get("blanks", [])) + 1))
                if marks != want:
                    errs.append(f"{p}: cloze text has blanks {marks} but 'blanks' defines {want}; use {{{{1}}}}, {{{{2}}}}, ...")
            if q.get("type") == "numeric" and "tolerance" not in q:
                warns.append(f"{p}: numeric question without tolerance; only near-exact answers count as correct")
            if q.get("type") != "text" and not q.get("explain") and not q.get("solution"):
                warns.append(f"{p}: no explanation or worked solution")
    elif kind == "lesson":
        _lesson(data, errs, warns)
    elif kind == "exam":
        ids = [q.get("id") for sec in data.get("sections", []) for q in sec.get("questions", [])]
        for d in _dupes(ids):
            errs.append(f"duplicate question id {d!r}")
    elif kind == "events":
        for i, e in enumerate(data.get("events", [])):
            if not re.match(r"^\d{4}-\d{2}-\d{2}", str(e.get("start", ""))):
                errs.append(f"$.events[{i}].start: use ISO format YYYY-MM-DD or YYYY-MM-DDTHH:MM")
    return errs, warns


def validate_data(data) -> tuple[list[str], list[str]]:
    if not isinstance(data, dict):
        return ["top level must be a JSON object"], []
    kind = data.get("kind")
    if kind not in KIND_SCHEMA:
        if kind == "dashboard":
            return [], []
        return [f"$.kind: unknown kind {kind!r}; expected one of {sorted(KIND_SCHEMA)}"], []
    schema = read_json(SCHEMAS / KIND_SCHEMA[kind])
    errs = check(data, schema, schema)
    if errs:
        return errs, []
    e2, warns = semantic(data)
    return e2, warns


def validate_file(path: Path) -> tuple[list[str], list[str]]:
    try:
        data = read_json(path)
    except ValueError as exc:
        return [f"invalid JSON: {exc}"], []
    return validate_data(data)
