"""Workspace summaries: the short status line set, recommendations and the dashboard data."""
from __future__ import annotations

import datetime as dt
from pathlib import Path

from . import progress, workspace
from .paths import read_json


def _days(iso: str | None, on: dt.date) -> int | None:
    try:
        return (dt.date.fromisoformat(str(iso)[:10]) - on).days
    except (TypeError, ValueError):
        return None


def deadlines(ws: Path, on: dt.date, horizon: int = 60) -> list[dict]:
    out = []
    ev_file = ws / "calendar" / "events.json"
    if ev_file.exists():
        try:
            for e in read_json(ev_file).get("events", []):
                d = _days(e.get("start"), on)
                if d is not None and 0 <= d <= horizon and e.get("category") in ("deadline", "exam", None, "other"):
                    out.append({"title": e["title"], "date": e["start"][:10], "days": d, "module": e.get("module"), "category": e.get("category")})
        except ValueError:
            pass
    for m in workspace.modules(ws):
        d = _days(m.get("exam_date"), on)
        if d is not None and 0 <= d <= horizon:
            out.append({"title": f"Exam: {m.get('title', m['id'])}", "date": m["exam_date"], "days": d, "module": m["id"], "category": "exam"})
    seen, uniq = set(), []
    for x in sorted(out, key=lambda x: (x["date"], x["title"])):
        k = (x["title"], x["date"])
        if k not in seen:
            seen.add(k)
            uniq.append(x)
    return uniq


def snapshot(ws: Path, on: dt.date | None = None) -> dict:
    on = on or dt.date.today()
    mods = workspace.modules(ws)
    due_now = progress.due(ws, on=on)
    due_week = progress.due(ws, on=on, within_days=7)
    mastery = progress.mastery(ws)
    out_mods = []
    for m in mods:
        topics = []
        for t in m.get("topics", []):
            st = mastery.get(f"{m['id']}/{t['id']}", {})
            topics.append({"id": t["id"], "title": t.get("title", t["id"]), "weight": int(t.get("weight", 1) or 1), "prereqs": list(t.get("prereqs") or []),
                           "mastery": st.get("mastery"), "attempts": st.get("attempts", 0), "status": progress.label(st.get("mastery"))})
        # topics practised but not in the topic map still count
        known = {t["id"] for t in topics}
        for key, st in mastery.items():
            mod, _, tid = key.partition("/")
            if mod == m["id"] and tid not in known:
                topics.append({"id": tid, "title": tid, "weight": 1, "mastery": st.get("mastery"), "attempts": st.get("attempts", 0), "status": progress.label(st.get("mastery"))})
        # weakest practised topics first, then unpractised ones by exam weight
        topics.sort(key=lambda t: (t["mastery"] is None, t["mastery"] or 0, -t["weight"]))
        out_mods.append({"id": m["id"], "title": m.get("title", m["id"]), "examDate": m.get("exam_date") or None,
                         "examDays": _days(m.get("exam_date"), on), "due": len(due_now.get(m["id"], [])), "topics": topics})
    tracked = [t for m in out_mods for t in m["topics"] if t["mastery"] is not None]
    avg = round(sum(t["mastery"] for t in tracked) / len(tracked), 3) if tracked else None
    dls = deadlines(ws, on)
    exams = sorted((m for m in out_mods if m["examDays"] is not None and m["examDays"] >= 0), key=lambda m: m["examDays"])
    n_due = sum(len(v) for v in due_now.values())
    n_week = sum(len(v) for v in due_week.values()) - n_due
    return {
        "date": on.isoformat(),
        "profile": {k: v for k, v in workspace.profile(ws).items() if not k.startswith("_")},
        "modules": out_mods,
        "deadlines": dls,
        "summary": {
            "due": n_due, "dueSoon": max(0, n_week), "mastery": avg, "tracked": len(tracked),
            "nextDeadline": next(({"title": d["title"], "days": d["days"]} for d in dls), None),
            "nextExam": {"title": exams[0]["title"], "days": exams[0]["examDays"]} if exams else None,
        },
        "next": recommend(out_mods, dls, due_now),
    }


def recommend(mods: list[dict], dls: list[dict], due_now: dict) -> list[str]:
    recs: list[tuple[int, str]] = []
    for mod, ids in due_now.items():
        if ids:
            recs.append((90, f"Review **{len(ids)}** due cards in *{mod}* (about {max(5, round(len(ids) * 0.4))} min)."))
    for d in dls:
        if d["days"] <= 3 and d.get("category") != "exam":
            recs.append((100 - d["days"], f"**{d['title']}** is due in {d['days']} day{'s' if d['days'] != 1 else ''}."))
    for m in mods:
        weak = [t for t in m["topics"] if t["mastery"] is not None and t["mastery"] < 0.5]
        new_heavy = [t for t in m["topics"] if t["mastery"] is None and t["weight"] >= 2]
        if m["examDays"] is not None and 0 <= m["examDays"] <= 21:
            target = (weak or new_heavy or m["topics"][:1])
            if target:
                recs.append((95 - m["examDays"], f"Exam in *{m['title']}* in {m['examDays']} days: practise **{target[0]['title']}** with a timed mock test."))
        if weak:
            w = sorted(weak, key=lambda t: (-t["weight"], t["mastery"]))[0]
            # a weak topic often rests on a weaker prerequisite: repair that first
            by_id = {t["id"]: t for t in m["topics"]}
            shaky = [by_id[x] for x in w.get("prereqs", []) if x in by_id and (by_id[x]["mastery"] is None or by_id[x]["mastery"] < 0.5)]
            if shaky:
                pre = sorted(shaky, key=lambda t: t["mastery"] if t["mastery"] is not None else -1)[0]
                recs.append((82 + 5 * w["weight"], f"**{w['title']}** builds on **{pre['title']}**, which is not secure yet: go through that first (explain, then 5 questions) in *{m['title']}*."))
            recs.append((70 + 5 * w["weight"], f"Strengthen **{w['title']}** ({round(w['mastery'] * 100)}% mastery) in *{m['title']}*: a worked-example drill, then 5 fresh questions."))
        elif new_heavy:
            recs.append((60, f"Start **{new_heavy[0]['title']}** in *{m['title']}*: it carries a lot of weight and has not been practised yet."))
    recs.sort(key=lambda x: -x[0])
    seen, out = set(), []
    for _, r in recs:
        if r not in seen:
            seen.add(r)
            out.append(r)
    return out[:6]


def status_text(ws: Path, max_lines: int = 12) -> str:
    """Compact plain-text status for the session-start hook and the coach."""
    if not (ws / "profile.md").exists():
        return ""
    s = snapshot(ws)
    prof = s["profile"]
    lines = [f"Study workspace: {ws}" + (f" (student: {prof.get('name')})" if prof.get("name") else "")]
    sm = s["summary"]
    if sm["due"]:
        per = ", ".join(f"{m['id']} {m['due']}" for m in s["modules"] if m["due"])
        lines.append(f"Reviews due today: {sm['due']} ({per})")
    up = [f"{d['title']} in {d['days']}d" for d in s["deadlines"][:4]]
    if up:
        lines.append("Upcoming: " + "; ".join(up))
    weak = [f"{m['id']}/{t['title']} {round(t['mastery'] * 100)}%" for m in s["modules"] for t in m["topics"] if t["mastery"] is not None and t["mastery"] < 0.5][:4]
    if weak:
        lines.append("Weak topics: " + ", ".join(weak))
    sec = workspace.profile(ws).get("_sections", {})
    rem = [ln.lstrip("- ").strip() for ln in sec.get("Remember", []) if ln.strip().startswith("-")][-5:]
    avoid = [ln.lstrip("- ").strip() for ln in sec.get("Avoid", []) if ln.strip().startswith("-")][-3:]
    if rem:
        lines.append("Remember: " + " | ".join(rem))
    if avoid:
        lines.append("Avoid: " + " | ".join(avoid))
    return "\n".join(lines[:max_lines])


def dashboard_data(ws: Path) -> dict:
    s = snapshot(ws)
    name = s["profile"].get("name")
    return {
        "als": "1", "kind": "dashboard",
        "title": f"{name}'s study dashboard" if name else "Study dashboard",
        "subtitle": s["profile"].get("programme") or None,
        "generated": s["date"],
        "summary": s["summary"], "modules": s["modules"], "deadlines": s["deadlines"][:12], "next": s["next"],
    }
