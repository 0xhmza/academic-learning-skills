"""Element ids produced by shared/templates/viz.js, mirrored so step lists can be validated.

Keep in sync with viz.js: the ids here are the ones a lesson's `steps` may reference.
"""
from __future__ import annotations

import re

KINDS = ("plot", "flow", "tree", "bars", "layers", "grid")
FUNCS = {"exp", "log", "ln", "log2", "log10", "sin", "cos", "tan", "tanh", "sqrt", "abs", "sign", "floor", "ceil",
         "max", "min", "pow", "sigmoid", "relu", "step"}
NAMES = {"x", "pi", "e"}
_EXPR = re.compile(r"^[0-9A-Za-z_+\-*/^().,\s]+$")
_ID = re.compile(r"^[A-Za-z_][\w.]*$")


def expr_error(fn) -> str | None:
    """Cheap check that a plot expression only uses what viz.js can evaluate."""
    if not isinstance(fn, str) or not fn.strip():
        return "needs 'fn' (an expression in x) or 'data' (a list of [x, y] pairs)"
    if not _EXPR.match(fn):
        return f"expression {fn!r} has characters outside digits, x, + - * / ^ ( ) and function names"
    if fn.count("(") != fn.count(")"):
        return f"expression {fn!r} has unbalanced brackets"
    for name in re.findall(r"[A-Za-z_]\w*", re.sub(r"\d+\.?\d*e[+-]?\d+", "0", fn, flags=re.I)):
        if name.lower() not in FUNCS and name.lower() not in NAMES:
            return f"expression {fn!r} uses unknown name {name!r}; allowed: x, pi, e, {', '.join(sorted(FUNCS))}"
    return None


def parse_node(n) -> dict:
    if isinstance(n, str):
        head, sep, tail = n.partition(":")
        return {"id": head.strip(), "label": (tail if sep else head).strip()}
    return n if isinstance(n, dict) else {}


def parse_edges(edges) -> list[tuple[str, str]]:
    out: list[tuple[str, str]] = []
    for e in edges or []:
        if isinstance(e, str):
            chain = [x.strip() for x in e.partition(":")[0].split(">")]
            out.extend(zip(chain, chain[1:]))
        elif isinstance(e, list) and len(e) >= 2:
            out.append((str(e[0]), str(e[1])))
        elif isinstance(e, dict):
            out.append((str(e.get("from", "")), str(e.get("to", ""))))
    return out


def tree_nodes(root) -> list[tuple[str, str | None]]:
    """(id, parent id) in the pre-order used by viz.js; unnamed nodes are n1, n2, ..."""
    out: list[tuple[str, str | None]] = []

    def walk(t, parent):
        if isinstance(t, str):
            given, kids = None, []
        elif isinstance(t, list):
            given, kids = None, t[1:]
        elif isinstance(t, dict):
            given, kids = t.get("id"), t.get("children") or []
        else:
            return
        nid = given or f"n{len(out) + 1}"
        out.append((nid, parent))
        for k in kids:
            walk(k, nid)

    walk(root, None)
    return out


def grid_list(s: dict) -> list[dict]:
    return s.get("grids") or [{"id": "", "cells": s.get("cells") or []}]


def _named(items, prefix: str) -> list[str]:
    return [str((it.get("id") if isinstance(it, dict) else None) or f"{prefix}{k + 1}") for k, it in enumerate(items or [])]


def ids(s: dict) -> tuple[set[str], list[str]]:
    """Return (ids, problems) for a visual-component slide."""
    layout = s.get("layout")
    found: list[str] = []
    problems: list[str] = []
    if layout == "plot":
        found.append("axes")
        for key, prefix in (("curves", "c"), ("scatter", "s"), ("lines", "l"), ("points", "p"), ("notes", "t")):
            found += _named(s.get(key), prefix)
        for k, c in enumerate(s.get("curves") or []):
            if isinstance(c, dict) and not c.get("data"):
                err = expr_error(c.get("fn"))
                if err:
                    problems.append(f"curves[{k}]: {err}")
        for key in ("x", "y"):
            rng = s.get(key)
            if rng is not None and not (isinstance(rng, list) and len(rng) == 2 and rng[0] < rng[1]):
                problems.append(f"'{key}' must be [min, max] with min < max")
    elif layout == "flow":
        nodes = [parse_node(n) for n in s.get("nodes") or []]
        names = [str(n.get("id", "")) for n in nodes]
        found += names
        for n in names:
            if not _ID.match(n):
                problems.append(f"node id {n!r} must start with a letter and use letters, digits, _ or .")
        for a, b in parse_edges(s.get("edges")):
            if a not in names or b not in names:
                problems.append(f"edge {a}>{b} names a node that is not in 'nodes'")
            else:
                found.append(f"{a}>{b}")
    elif layout == "tree":
        for nid, parent in tree_nodes(s.get("root")):
            found.append(nid)
            if parent:
                found.append(f"{parent}>{nid}")
    elif layout == "bars":
        vals, labels = s.get("values") or [], s.get("labels") or []
        if labels and len(labels) != len(vals):
            problems.append(f"{len(labels)} labels for {len(vals)} values")
        found += ["axes"] + [f"b{k + 1}" for k in range(len(vals))]
    elif layout == "layers":
        n = len(s.get("layers") or [])
        found += [f"L{k + 1}" for k in range(n)] + [f"E{k + 1}" for k in range(max(0, n - 1))]
    elif layout == "grid":
        grids = grid_list(s)
        if len(grids) > 1 and any(not g.get("id") for g in grids):
            problems.append("each entry of 'grids' needs an 'id'")
        for g in grids:
            pre = f"{g['id']}." if g.get("id") else ""
            found.append(g.get("id") or "grid")
            for i, row in enumerate(g.get("cells") or []):
                for j, v in enumerate(row):
                    if v is not None:
                        found.append(f"{pre}r{i + 1}c{j + 1}")
    seen: set[str] = set()
    for i in found:
        if i in seen:
            problems.append(f"id {i!r} is used twice")
        seen.add(i)
    return seen, problems


_ROW = re.compile(r"^row(\d+)$")
_COL = re.compile(r"^col(\d+)$")
_RANGE = re.compile(r"^r(\d+)c(\d+):r(\d+)c(\d+)$")


def grid_expand(s: dict, token: str) -> list[str]:
    """Mirror of viz.js gridExpand: 'in.row2', 'col1', 'k.r1c1:r3c3' -> cell ids ([] if nothing matches)."""
    gid, _, rest = token.rpartition(".")
    grid = next((g for g in grid_list(s) if (g.get("id") or "") == gid), None)
    if grid is None:
        return [token]
    rows = grid.get("cells") or []
    pre = f"{gid}." if gid else ""

    def cell(i: int, j: int) -> list[str]:
        ok = 1 <= i <= len(rows) and 1 <= j <= len(rows[i - 1]) and rows[i - 1][j - 1] is not None
        return [f"{pre}r{i}c{j}"] if ok else []

    m = _ROW.match(rest)
    if m:
        i = int(m.group(1))
        return [c for j in range(1, len(rows[i - 1]) + 1 if 1 <= i <= len(rows) else 1) for c in cell(i, j)]
    m = _COL.match(rest)
    if m:
        return [c for i in range(1, len(rows) + 1) for c in cell(i, int(m.group(1)))]
    m = _RANGE.match(rest)
    if m:
        a, b, c2, d = (int(x) for x in m.groups())
        return [c for i in range(a, c2 + 1) for j in range(b, d + 1) for c in cell(i, j)]
    return [token]
