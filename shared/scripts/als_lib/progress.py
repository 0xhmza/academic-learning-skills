"""Spaced repetition (Leitner boxes) and topic mastery."""
from __future__ import annotations

import datetime as dt
from pathlib import Path

from .paths import read_json, write_json

INTERVALS = [1, 2, 4, 8, 16, 32]  # days until next review, per box 0..5
ALPHA = 0.3                        # weight of the newest attempt in topic mastery
GRADE_SCORE = {"again": 0.0, "hard": 0.6, "good": 0.9, "easy": 1.0}


def empty() -> dict:
    return {"als": "1", "kind": "progress", "items": {}, "topics": {}, "imports": []}


def load(ws: Path) -> dict:
    p = ws / "progress.json"
    if not p.exists():
        return empty()
    data = read_json(p)
    for k, v in empty().items():
        data.setdefault(k, v)
    return data


def save(ws: Path, data: dict) -> None:
    write_json(ws / "progress.json", data)


def _date(s: str | None, fallback: dt.date) -> dt.date:
    try:
        return dt.date.fromisoformat(str(s)[:10])
    except (TypeError, ValueError):
        return fallback


def grade_of(result: dict) -> str:
    """Normalise a deck or quiz result row to again/hard/good/easy."""
    if result.get("grade") in GRADE_SCORE:
        return result["grade"]
    if result.get("unanswered") or not result.get("correct"):
        return "hard" if result.get("partial") else "again"
    if result.get("hintsUsed") or result.get("stepsViewed"):
        return "hard"
    return "good"


def schedule(item: dict | None, grade: str, on: dt.date) -> dict:
    item = dict(item or {"box": 0, "seen": 0, "lapses": 0})
    box = int(item.get("box", 0))
    if grade == "again":
        box = 0
        item["lapses"] = int(item.get("lapses", 0)) + 1
    elif grade == "good":
        box = min(box + 1, len(INTERVALS) - 1)
    elif grade == "easy":
        box = min(box + 2, len(INTERVALS) - 1)
    item["box"] = box
    item["seen"] = int(item.get("seen", 0)) + 1
    item["last"] = on.isoformat()
    item["due"] = (on + dt.timedelta(days=INTERVALS[box])).isoformat()
    return item


def update_topic(topic: dict | None, score: float, on: dt.date) -> dict:
    t = dict(topic or {"attempts": 0, "correct": 0})
    prev = t.get("mastery")
    t["mastery"] = round(score if prev is None else (1 - ALPHA) * prev + ALPHA * score, 3)
    t["attempts"] = int(t.get("attempts", 0)) + 1
    t["correct"] = int(t.get("correct", 0)) + (1 if score >= 0.6 else 0)
    t["last"] = on.isoformat()
    return t


def import_results(ws: Path, results: dict, module: str | None = None, fname: str = "") -> dict:
    """Apply one exported results file. Returns a summary."""
    if results.get("kind") != "results":
        raise ValueError("not an ALS results file (kind must be 'results')")
    data = load(ws)
    mod = module or results.get("module") or "general"
    on = _date(results.get("date"), dt.date.today())
    key_id = f"{mod}:{results.get('title')}:{results.get('exported')}"
    if key_id in data["imports"]:
        return {"skipped": True, "reason": "already imported", "module": mod}

    # aggregate per item: any 'again' in a session counts as a lapse, otherwise the last grade counts
    per_item: dict[str, list[str]] = {}
    per_topic: dict[str, list[float]] = {}
    for r in results.get("items", []):
        if not r.get("id"):
            continue
        g = grade_of(r)
        per_item.setdefault(r["id"], []).append(g)
        if r.get("topic"):
            per_topic.setdefault(r["topic"], []).append(GRADE_SCORE[g])
    for item_id, grades in per_item.items():
        final = "again" if "again" in grades else grades[-1]
        k = f"{mod}/{item_id}"
        data["items"][k] = schedule(data["items"].get(k), final, on)
    for topic, scores in per_topic.items():
        k = f"{mod}/{topic}"
        for s in scores:
            data["topics"][k] = update_topic(data["topics"].get(k), s, on)
    data["imports"].append(key_id)
    data["imports"] = data["imports"][-500:]
    save(ws, data)
    lapses = sum(1 for g in per_item.values() if "again" in g)
    return {"skipped": False, "module": mod, "items": len(per_item), "lapses": lapses, "topics": sorted(per_topic), "file": fname}


def due(ws: Path, module: str | None = None, on: dt.date | None = None, within_days: int = 0) -> dict[str, list[str]]:
    """{module: [item ids]} due on or before `on + within_days`."""
    on = on or dt.date.today()
    limit = on + dt.timedelta(days=within_days)
    out: dict[str, list[str]] = {}
    for key, item in load(ws)["items"].items():
        mod, _, item_id = key.partition("/")
        if module and mod != module:
            continue
        if _date(item.get("due"), on) <= limit:
            out.setdefault(mod, []).append(item_id)
    return out


def mastery(ws: Path, module: str | None = None) -> dict[str, dict]:
    out = {}
    for key, t in load(ws)["topics"].items():
        mod, _, topic = key.partition("/")
        if module and mod != module:
            continue
        out[key] = t
    return out


def label(m: float | None) -> str:
    if m is None:
        return "new"
    return "secure" if m >= 0.8 else "developing" if m >= 0.5 else "weak"
