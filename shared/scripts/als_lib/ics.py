"""Write RFC 5545 calendars from ALS events, and read .ics feeds (e.g. a Moodle calendar export)."""
from __future__ import annotations

import datetime as dt
import hashlib
import re
import urllib.request
from pathlib import Path

PRODID = "-//academic-learning-skills//ALS//EN"


# ---------------------------------------------------------------- writing

def _esc(s: str) -> str:
    return str(s).replace("\\", "\\\\").replace(";", "\\;").replace(",", "\\,").replace("\r\n", "\\n").replace("\n", "\\n")


def _fold(line: str) -> str:
    """Fold to 75 octets per RFC 5545 without splitting UTF-8 sequences."""
    out, cur, size = [], "", 0
    for ch in line:
        n = len(ch.encode("utf-8"))
        if size + n > 75:
            out.append(cur)
            cur, size = " " + ch, 1 + n
        else:
            cur += ch
            size += n
    out.append(cur)
    return "\r\n".join(out)


def _tz(name: str | None):
    if not name:
        return None
    try:
        from zoneinfo import ZoneInfo
        return ZoneInfo(name)
    except Exception:  # zoneinfo or tz database unavailable (common on Windows without tzdata)
        return None


def parse_when(s: str) -> tuple[dt.datetime | dt.date, bool]:
    """Return (value, is_date). Accepts YYYY-MM-DD, YYYY-MM-DDTHH:MM[:SS][Z|±HH:MM]."""
    s = s.strip()
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", s):
        return dt.date.fromisoformat(s), True
    return dt.datetime.fromisoformat(s.replace("Z", "+00:00").replace(" ", "T")), False


def _fmt_dt(v: dt.datetime, tz) -> str:
    if v.tzinfo is None and tz is not None:
        v = v.replace(tzinfo=tz)
    if v.tzinfo is not None:
        return v.astimezone(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return v.strftime("%Y%m%dT%H%M%S")  # floating local time


def to_ics(spec: dict) -> tuple[str, list[str]]:
    """Build calendar text. Returns (ics, notes)."""
    notes: list[str] = []
    tz = _tz(spec.get("timezone"))
    if spec.get("timezone") and tz is None:
        notes.append(f"time zone database unavailable for {spec['timezone']!r}; times are written as floating local times, "
                     "which calendar apps show in the viewer's own zone")
    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    lines = ["BEGIN:VCALENDAR", "VERSION:2.0", f"PRODID:{PRODID}", "CALSCALE:GREGORIAN", "METHOD:PUBLISH"]
    if spec.get("calendar"):
        lines.append("X-WR-CALNAME:" + _esc(spec["calendar"]))
    for ev in spec["events"]:
        start, is_date = parse_when(ev["start"])
        all_day = bool(ev.get("allDay")) or is_date
        uid_src = ev.get("id") or f"{ev['title']}|{ev['start']}|{ev.get('module', '')}"
        uid = hashlib.sha1(uid_src.encode("utf-8")).hexdigest()[:24] + "@als"
        lines += ["BEGIN:VEVENT", f"UID:{uid}", f"DTSTAMP:{stamp}"]
        if all_day:
            d0 = start if isinstance(start, dt.date) and not isinstance(start, dt.datetime) else start.date()
            d1 = d0 + dt.timedelta(days=1)
            if ev.get("end"):
                e, _ = parse_when(ev["end"])
                e = e if not isinstance(e, dt.datetime) else e.date()
                d1 = max(d1, e + dt.timedelta(days=1)) if e >= d0 else d1
            lines += [f"DTSTART;VALUE=DATE:{d0.strftime('%Y%m%d')}", f"DTEND;VALUE=DATE:{d1.strftime('%Y%m%d')}"]
        else:
            if ev.get("end"):
                end, _ = parse_when(ev["end"])
                if not isinstance(end, dt.datetime):
                    raise ValueError(f"event {ev['title']!r}: end must include a time when start does")
            else:
                end = start + dt.timedelta(minutes=float(ev.get("durationMin", 60)))
            lines += [f"DTSTART:{_fmt_dt(start, tz)}", f"DTEND:{_fmt_dt(end, tz)}"]
        lines.append("SUMMARY:" + _esc(ev["title"]))
        desc = ev.get("description", "")
        if ev.get("module"):
            desc = (desc + "\n\n" if desc else "") + f"Module: {ev['module']}"
        if desc:
            lines.append("DESCRIPTION:" + _esc(desc))
        if ev.get("location"):
            lines.append("LOCATION:" + _esc(ev["location"]))
        if ev.get("url"):
            lines.append("URL:" + ev["url"])
        if ev.get("category"):
            lines.append("CATEGORIES:" + _esc(ev["category"].upper()))
        lines.append("TRANSP:" + ("TRANSPARENT" if ev.get("category") in ("deadline", "exam") and all_day else "OPAQUE"))
        for m in ev.get("alarmsMin", []) or []:
            lines += ["BEGIN:VALARM", "ACTION:DISPLAY", f"TRIGGER:-PT{int(m)}M", "DESCRIPTION:" + _esc(ev["title"]), "END:VALARM"]
        lines.append("END:VEVENT")
    lines.append("END:VCALENDAR")
    return "\r\n".join(_fold(ln) for ln in lines) + "\r\n", notes


# ---------------------------------------------------------------- reading

def _unesc(s: str) -> str:
    return re.sub(r"\\([\\;,nN])", lambda m: "\n" if m.group(1) in "nN" else m.group(1), s)


def _parse_dt(value: str, params: dict) -> tuple[str, bool]:
    if params.get("VALUE") == "DATE" or re.fullmatch(r"\d{8}", value):
        return f"{value[:4]}-{value[4:6]}-{value[6:8]}", True
    m = re.fullmatch(r"(\d{4})(\d{2})(\d{2})T(\d{2})(\d{2})(\d{2})?(Z)?", value)
    if not m:
        return value, False
    y, mo, d, h, mi, se, z = m.groups()
    iso = f"{y}-{mo}-{d}T{h}:{mi}"
    if z:
        utc = dt.datetime(int(y), int(mo), int(d), int(h), int(mi), int(se or 0), tzinfo=dt.timezone.utc)
        return utc.astimezone().replace(tzinfo=None).isoformat(timespec="minutes"), False
    return iso, False


def parse_ics(text: str) -> list[dict]:
    raw = text.replace("\r\n", "\n").replace("\r", "\n")
    raw = re.sub(r"\n[ \t]", "", raw)  # unfold
    events, cur = [], None
    for line in raw.split("\n"):
        if line == "BEGIN:VEVENT":
            cur = {}
            continue
        if line == "END:VEVENT":
            if cur is not None:
                events.append(cur)
            cur = None
            continue
        if cur is None or ":" not in line:
            continue
        head, _, value = line.partition(":")
        name, *ps = head.split(";")
        params = dict(p.split("=", 1) for p in ps if "=" in p)
        cur.setdefault(name.upper(), (value, params))
    out = []
    for e in events:
        if "DTSTART" not in e or "SUMMARY" not in e:
            continue
        start, is_date = _parse_dt(*e["DTSTART"])
        item = {"title": _unesc(e["SUMMARY"][0]).strip(), "start": start}
        if is_date:
            item["allDay"] = True
        if "DTEND" in e:
            end, _ = _parse_dt(*e["DTEND"])
            if not is_date and end != start:
                item["end"] = end
        for key, field in (("DESCRIPTION", "description"), ("LOCATION", "location"), ("URL", "url")):
            if key in e and e[key][0].strip():
                item[field] = _unesc(e[key][0]).strip()
        own = None
        if "CATEGORIES" in e:
            cat = _unesc(e["CATEGORIES"][0]).strip()
            if cat.lower() in OWN_CATEGORIES:
                own = cat.lower()          # a calendar this toolkit wrote
            else:
                item["lmsCategory"] = cat  # e.g. Moodle puts the course short name here
        if "UID" in e:
            item["id"] = e["UID"][0]
        item["category"] = own or classify(item["title"], item.get("description", ""))
        out.append(item)
    out.sort(key=lambda x: x["start"])
    return out


OWN_CATEGORIES = {"deadline", "exam", "study", "review", "lecture", "other"}


def classify(title: str, desc: str = "") -> str:
    t = (title + " " + desc[:200]).lower()
    if re.search(r"\b(exam|klausur|prüfung|midterm|final)\b", t):
        return "exam"
    if re.search(r"\b(due|deadline|abgabe|fällig|closes|submission|submit)\b", t):
        return "deadline"
    if re.search(r"\b(lecture|vorlesung|seminar|tutorial|übung|lab)\b", t):
        return "lecture"
    return "other"


def fetch(url_or_path: str, timeout: int = 20) -> str:
    """Read a local .ics file or download one. The URL is never logged (it may carry a private token)."""
    p = Path(url_or_path)
    if p.exists():
        return p.read_text(encoding="utf-8-sig", errors="replace")
    if not re.match(r"^https?://", url_or_path):
        raise FileNotFoundError(url_or_path)
    req = urllib.request.Request(url_or_path, headers={"User-Agent": "academic-learning-skills/ics-import", "Accept": "text/calendar, */*"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:  # noqa: S310 (user-supplied calendar URL)
        body = resp.read()
    text = body.decode("utf-8-sig", errors="replace")
    if "BEGIN:VCALENDAR" not in text:
        raise ValueError("the response is not an iCalendar feed (check that the export URL is complete and still valid)")
    return text
