#!/usr/bin/env python3
"""ALS command line: the deterministic half of the toolkit.

Claude writes small JSON data files; this tool validates them, builds themed HTML pages,
exports Anki decks and calendars, and keeps the learner workspace (profile, progress) consistent.

Run `python als.py <command> -h` for details.
"""
from __future__ import annotations

import argparse
import datetime as dt
import glob
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from als_lib import anki, build, extract, ics, paths, progress, report, settings, themes, workspace  # noqa: E402
from als_lib.validate import validate_file  # noqa: E402

for stream in (sys.stdout, sys.stderr):
    try:
        stream.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass


def ws_of(args) -> Path:
    return paths.workspace(getattr(args, "home", None))


def fail(msg: str, code: int = 1) -> int:
    print(f"error: {msg}", file=sys.stderr)
    return code


def expand(files: list[str]) -> list[str]:
    """Accept folders and glob patterns as well as files (PowerShell and cmd do not expand `*`)."""
    out: list[str] = []
    for f in files:
        path = Path(f)
        if path.is_dir():
            out += [str(x) for x in sorted(path.glob("*.json")) if x.name != "topics.json"]
        elif any(ch in f for ch in "*?["):
            out += sorted(glob.glob(f)) or [f]
        else:
            out.append(f)
    return out


# ---------------------------------------------------------------- commands

def cmd_where(args) -> int:
    ws = ws_of(args)
    print(ws)
    print("exists" if (ws / "profile.md").exists() else "not initialised (run: als.py init)")
    return 0


def cmd_init(args) -> int:
    ws = ws_of(args)
    created = workspace.init(ws, args.name or "", args.programme or "", args.timezone or "", args.languages or "en", args.goals or "")
    print(f"workspace: {ws}")
    for p in created:
        print(f"  created {p.relative_to(ws) if p != ws else p}")
    if not created:
        print("  already set up; nothing changed")
    return 0


def cmd_remember(args) -> int:
    p = workspace.remember(ws_of(args), args.text, "Avoid" if args.avoid else args.section)
    print(f"saved to {p}")
    return 0


def cmd_note(args) -> int:
    text = args.text if args.text != "-" else sys.stdin.read()
    p = workspace.add_note(ws_of(args), args.title, text, args.module)
    print(p)
    return 0


def cmd_module(args) -> int:
    ws = ws_of(args)
    if args.action == "new":
        if not args.title:
            return fail("--title is required")
        created = workspace.new_module(ws, args.id, args.title, args.code or "", args.term or "", args.exam_date or "", args.subject or "", args.theme or "")
        theme, why = themes.route(args.subject, args.title)
        print(f"module {args.id}: {paths.module_dir(ws, args.id)}")
        for p in created:
            print(f"  created {p.relative_to(ws)}")
        if not args.theme:
            print(f"  theme: {theme} ({why})")
        return 0
    if args.action == "list":
        for m in workspace.modules(ws):
            print(f"{m['id']:<28} {m.get('title', ''):<40} exam {m.get('exam_date') or '-':<10} topics {len(m.get('topics', []))}")
        return 0
    if args.action == "log":
        if not args.text:
            return fail("--text is required")
        workspace.log(ws, args.id, args.text)
        print("logged")
        return 0
    return fail(f"unknown action {args.action}")


def cmd_theme(args) -> int:
    if args.list:
        for name, t in themes.registry()["themes"].items():
            print(f"{name:<10} {t['label']:<10} {t['short']}")
        return 0
    name, why = themes.route(" ".join(args.subject))
    print(name)
    print(f"  {why}", file=sys.stderr)
    return 0


def cmd_validate(args) -> int:
    bad = 0
    for f in expand(args.files):
        errs, warns = validate_file(Path(f))
        status = "FAIL" if errs else "ok"
        print(f"{status:<4} {f}")
        for e in errs:
            print(f"     error   {e}")
        for w in warns:
            print(f"     warning {w}")
        bad += bool(errs)
    return 1 if bad else 0


def cmd_build(args) -> int:
    ws = ws_of(args)
    rc = 0
    files = expand(args.files)
    for f in files:
        try:
            out, theme, why, warns = build.build_file(Path(f), Path(args.out) if args.out and len(files) == 1 else None, args.theme, ws, not args.no_due)
        except (build.BuildError, ValueError, OSError) as exc:
            print(f"FAIL {f}\n  {exc}", file=sys.stderr)
            rc = 1
            continue
        print(f"built {out}")
        print(f"  theme {theme} ({why})")
        for w in warns:
            print(f"  warning {w}")
    return rc


def _load_deck(path: str) -> dict:
    errs, _ = validate_file(Path(path))
    if errs:
        raise ValueError("deck is invalid:\n  " + "\n  ".join(errs))
    data = paths.read_json(Path(path))
    if data.get("kind") != "deck":
        raise ValueError("not a deck file (kind must be 'deck')")
    return data


def _out_for(src: str, out: str | None, suffix: str) -> Path:
    if out:
        return Path(out)
    p = Path(src).resolve()
    if p.parent.name == "data" and paths.module_of(p):
        return p.parent.parent / "out" / (p.stem + suffix)
    return p.with_suffix(suffix)


def cmd_anki(args) -> int:
    try:
        deck = _load_deck(args.deck)
    except ValueError as exc:
        return fail(str(exc))
    fmt = args.format
    if fmt == "apkg" and not anki.has_genanki():
        print("genanki is not installed (pip install genanki); writing an Anki text import instead.", file=sys.stderr)
        fmt = "anki-tsv"
    suffix = {"apkg": ".apkg", "anki-tsv": ".anki.txt", "quizlet": ".quizlet.txt", "csv": ".csv"}[fmt]
    out = _out_for(args.deck, args.out, suffix)
    fn = {"apkg": anki.to_apkg, "anki-tsv": anki.to_anki_tsv, "quizlet": anki.to_quizlet, "csv": anki.to_csv}[fmt]
    path, n = fn(deck, out)
    print(f"wrote {path} ({n} notes)")
    if fmt == "apkg":
        print("  import: double-click the file, or Anki > File > Import. Re-importing updates the same notes.")
    elif fmt == "anki-tsv":
        print("  import: Anki > File > Import, choose this file; note types and deck are read from its header.")
    return 0


def cmd_ics(args) -> int:
    src = Path(args.events)
    errs, _ = validate_file(src)
    if errs:
        return fail("events file is invalid:\n  " + "\n  ".join(errs))
    spec = paths.read_json(src)
    try:
        text, notes = ics.to_ics(spec)
    except ValueError as exc:
        return fail(str(exc))
    out = Path(args.out) if args.out else src.with_suffix(".ics")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(text.encode("utf-8"))
    print(f"wrote {out} ({len(spec['events'])} events)")
    for n in notes:
        print(f"  note: {n}")
    return 0


def cmd_ics_import(args) -> int:
    ws = ws_of(args)
    source = args.source or os.environ.get("ALS_MOODLE_ICS_URL")
    if not source:
        return fail("give a file or URL, or set ALS_MOODLE_ICS_URL")
    try:
        text = ics.fetch(source)
    except Exception as exc:  # network, file and format errors all end here
        return fail(f"could not read the calendar: {exc}")
    events = ics.parse_ics(text)
    mapping = dict(m.split("=", 1) for m in (args.map or []) if "=" in m)
    for e in events:
        cat = e.get("lmsCategory", "")
        e["module"] = mapping.get(cat) or args.module or (cat or None)
    if args.since:
        events = [e for e in events if e["start"][:10] >= args.since]
    out = Path(args.out) if args.out else ws / "calendar" / "events.json"
    existing = []
    if out.exists() and not args.replace:
        try:
            existing = paths.read_json(out).get("events", [])
        except ValueError:
            existing = []
    by_key = {(e.get("id") or e["title"] + e["start"]): e for e in existing}
    for e in events:
        by_key[e.get("id") or e["title"] + e["start"]] = e
    merged = sorted(by_key.values(), key=lambda e: e["start"])
    paths.write_json(out, {"als": "1", "kind": "events", "calendar": "Imported LMS calendar", "events": merged})
    cats: dict[str, int] = {}
    for e in events:
        cats[e["category"]] = cats.get(e["category"], 0) + 1
    print(f"imported {len(events)} events into {out} ({', '.join(f'{v} {k}' for k, v in sorted(cats.items())) or 'none'})")
    unmapped = sorted({e.get("lmsCategory") for e in events if e.get("lmsCategory") and e.get("lmsCategory") not in mapping})
    if unmapped and not args.module:
        print("  LMS course labels without a module mapping: " + ", ".join(unmapped))
        print("  map them with --map 'LABEL=module-id'")
    return 0


def cmd_progress(args) -> int:
    ws = ws_of(args)
    if args.action == "import":
        rc = 0
        for f in args.files:
            try:
                res = progress.import_results(ws, paths.read_json(Path(f)), args.module, f)
            except (ValueError, OSError) as exc:
                print(f"FAIL {f}: {exc}", file=sys.stderr)
                rc = 1
                continue
            if res["skipped"]:
                print(f"skip {f} ({res['reason']})")
            else:
                print(f"ok   {f}: {res['items']} items in {res['module']}, {res['lapses']} forgotten, topics: {', '.join(res['topics']) or '-'}")
        return rc
    if args.action == "show":
        print(json.dumps(progress.load(ws), indent=2, ensure_ascii=False))
        return 0
    return fail(f"unknown action {args.action}")


def cmd_due(args) -> int:
    ws = ws_of(args)
    d = progress.due(ws, args.module, within_days=args.within)
    if args.json:
        print(json.dumps(d, indent=2))
        return 0
    if not d:
        print("nothing due")
        return 0
    for mod, ids in sorted(d.items()):
        print(f"{mod}: {len(ids)} due")
        if args.verbose:
            print("  " + ", ".join(ids))
    return 0


def cmd_status(args) -> int:
    ws = ws_of(args)
    if args.json:
        print(json.dumps(report.snapshot(ws), indent=2, ensure_ascii=False, default=str))
        return 0
    text = report.status_text(ws, max_lines=40)
    print(text or f"no workspace at {ws} (run: als.py init)")
    if text:
        recs = report.snapshot(ws)["next"]
        if recs:
            print("Next:")
            for r in recs:
                print("  - " + r.replace("**", "").replace("*", ""))
    return 0


def cmd_dashboard(args) -> int:
    ws = ws_of(args)
    if not (ws / "profile.md").exists():
        return fail(f"no workspace at {ws} (run: als.py init)")
    data = report.dashboard_data(ws)
    theme = args.theme or workspace.profile(ws).get("theme")
    if theme not in themes.names():
        theme = themes.registry()["default"]
    out = Path(args.out) if args.out else ws / "dashboard.html"
    build.build_data(data, out, theme)
    print(f"built {out}")
    return 0


def cmd_pdf(args) -> int:
    from als_lib.pdf import print_pdf
    src = Path(args.html)
    out = Path(args.out) if args.out else src.with_suffix(".pdf")
    try:
        p = print_pdf(src, out, args.query or "")
    except (RuntimeError, OSError) as exc:
        return fail(str(exc))
    print(f"wrote {p}")
    return 0


def cmd_new(args) -> int:
    """Copy a starter data file for a kind, so Claude edits a valid skeleton instead of writing from scratch."""
    starter = paths.SHARED / "starters" / f"{args.kind}.json"
    if not starter.exists():
        return fail(f"no starter for {args.kind}")
    out = Path(args.out)
    if out.exists() and not args.force:
        return fail(f"{out} exists (use --force to overwrite)")
    data = paths.read_json(starter)
    if args.title:
        data["title"] = args.title
    if args.module:
        data["module"] = args.module
    if args.subject:
        data["subject"] = args.subject
    if args.kind == "lesson":
        try:
            _lesson_scaffold(data, args)
        except ValueError as exc:
            return fail(str(exc))
    elif args.outline or args.source or args.depth or args.grounding:
        return fail("--outline, --source, --depth and --grounding only apply to lessons")
    paths.write_json(out, data)
    print(f"wrote {out}")
    if args.kind == "lesson":
        print(f"  grounding {data['grounding']}, depth {data['depth']}, {len(data['slides'])} slides: {', '.join(s['layout'] for s in data['slides'])}")
    return 0


def _lesson_scaffold(data: dict, args) -> None:
    """Apply the student's lesson settings and, with --outline, keep one skeleton slide per named layout."""
    ws = ws_of(args)
    cfg = settings.resolve(ws if ws.exists() else None, args.module)
    data["grounding"] = args.grounding or cfg["lesson_grounding"]["value"]
    data["depth"] = settings.normalise("lesson_depth", args.depth or cfg["lesson_depth"]["value"])
    if args.lang:
        data["lang"] = args.lang
    sources = []
    for item in args.source or []:
        sid, sep, rest = item.partition("=")
        if not sep or not sid.strip():
            raise ValueError(f"--source expects ID=path-or-title, got {item!r}")
        entry = {"id": sid.strip()}
        entry["file" if Path(rest).suffix else "title"] = rest.strip()
        sources.append(entry)
    if sources:
        data["sources"] = sources
    if args.outline:
        by_layout = {}
        for s in data["slides"]:
            by_layout.setdefault(s["layout"], s)
        slides = []
        for name in (x.strip() for x in args.outline.split(",")):
            if not name:
                continue
            if name not in by_layout:
                raise ValueError(f"unknown layout {name!r} in --outline; choose from {', '.join(by_layout)}")
            slide = json.loads(json.dumps(by_layout[name]))
            for key in ("notes", "more", "level"):
                slide.pop(key, None)
            if name not in ("title", "summary"):
                slide["src"] = ""  # must be filled in: a strict lesson does not build without it
            slides.append(slide)
        data["slides"] = slides
    if data["grounding"] != "strict":
        return
    for slide in data["slides"]:
        slide.pop("grounded", None)


def cmd_settings(args) -> int:
    ws = ws_of(args)
    if args.pairs:
        pairs = {}
        for item in args.pairs:
            key, sep, value = item.partition("=")
            if not sep:
                return fail(f"use key=value, got {item!r}")
            pairs[key] = value
        target = settings.save(ws, pairs, args.module)
        print(f"saved to {target}")
    cfg = settings.resolve(ws if ws.exists() else None, args.module)
    if args.json:
        print(json.dumps({k: v["value"] for k, v in cfg.items()}, indent=2))
        return 0
    for key, info in cfg.items():
        print(f"{key:<17} {info['value']:<13} ({info['from']})  {info['help']}")
    return 0


def cmd_extract(args) -> int:
    ws = ws_of(args)
    if args.out:
        out_dir = Path(args.out)
    elif args.module:
        out_dir = paths.module_dir(ws, args.module) / "sources" / "text"
    else:
        out_dir = ws / "extract"
    rc = 0
    for f in args.pdfs:
        try:
            rep = extract.extract(Path(f), out_dir, args.pages, args.images, args.dpi, args.keep_builds, args.layout)
        except (RuntimeError, OSError, ValueError) as exc:
            print(f"FAIL {f}: {exc}", file=sys.stderr)
            rc = 1
            continue
        print(f"text {rep['text']}")
        print(f"  {rep['pages']} pages, {rep['written']} written, {rep['chars']} characters ({rep['engine']})")
        if rep["merged"]:
            print(f"  build-up pages left out (their content is on a later page): {extract.ranges(list(rep['merged']))}")
        if rep["thin"]:
            print(f"  pages without text, probably figures: {extract.ranges(rep['thin'])}")
            if not rep["images"]:
                print("    re-run with --images thin to render them, then look at the PNGs before writing about them")
        for n, path in sorted(rep["images"].items()):
            print(f"  image p.{n}: {path}")
        if args.toc:
            for n, first, chars in rep["toc"]:
                print(f"  p.{n:<4} {chars:>5}  {first}")
    return rc


# ---------------------------------------------------------------- parser

def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="als.py", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--home", help="learner workspace (default: $ALS_HOME or ./study)")
    p.add_argument("--version", action="version", version=f"academic-learning-skills {paths.version()}")
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("where", help="print the workspace path")
    s.set_defaults(fn=cmd_where)

    s = sub.add_parser("init", help="create the learner workspace")
    s.add_argument("--name"); s.add_argument("--programme"); s.add_argument("--timezone"); s.add_argument("--languages"); s.add_argument("--goals", help="semicolon-separated")
    s.set_defaults(fn=cmd_init)

    s = sub.add_parser("remember", help="append a dated preference to profile.md")
    s.add_argument("text"); s.add_argument("--avoid", action="store_true", help="file under ## Avoid"); s.add_argument("--section", default="Remember")
    s.set_defaults(fn=cmd_remember)

    s = sub.add_parser("note", help="save a note to notes/YYYY-MM-DD-<title>.md")
    s.add_argument("title"); s.add_argument("text", help="note text, or - to read stdin"); s.add_argument("--module")
    s.set_defaults(fn=cmd_note)

    s = sub.add_parser("module", help="create, list or log modules")
    s.add_argument("action", choices=["new", "list", "log"]); s.add_argument("id", nargs="?", default="")
    s.add_argument("--title"); s.add_argument("--code"); s.add_argument("--term"); s.add_argument("--exam-date", dest="exam_date"); s.add_argument("--subject"); s.add_argument("--theme", choices=themes.names()); s.add_argument("--text")
    s.set_defaults(fn=cmd_module)

    s = sub.add_parser("theme", help="pick a design system for a subject")
    s.add_argument("subject", nargs="*"); s.add_argument("--list", action="store_true")
    s.set_defaults(fn=cmd_theme)

    s = sub.add_parser("validate", help="check data files against the schemas")
    s.add_argument("files", nargs="+")
    s.set_defaults(fn=cmd_validate)

    s = sub.add_parser("build", help="build themed HTML from data files")
    s.add_argument("files", nargs="+"); s.add_argument("-o", "--out"); s.add_argument("--theme", choices=themes.names()); s.add_argument("--no-due", action="store_true", help="do not embed today's due cards")
    s.set_defaults(fn=cmd_build)

    s = sub.add_parser("anki", help="export a deck to Anki (.apkg), Anki text, Quizlet or CSV")
    s.add_argument("deck"); s.add_argument("-o", "--out"); s.add_argument("--format", choices=["apkg", "anki-tsv", "quizlet", "csv"], default="apkg")
    s.set_defaults(fn=cmd_anki)

    s = sub.add_parser("ics", help="write an .ics calendar from an events file")
    s.add_argument("events"); s.add_argument("-o", "--out")
    s.set_defaults(fn=cmd_ics)

    s = sub.add_parser("ics-import", help="import an .ics file or URL (e.g. Moodle calendar export) into calendar/events.json")
    s.add_argument("source", nargs="?", help="path or URL (default: $ALS_MOODLE_ICS_URL); URLs are never printed"); s.add_argument("--module", help="assign all events to this module")
    s.add_argument("--map", action="append", help="LMS course label=module-id (repeatable)"); s.add_argument("--since", help="YYYY-MM-DD"); s.add_argument("-o", "--out"); s.add_argument("--replace", action="store_true")
    s.set_defaults(fn=cmd_ics_import)

    s = sub.add_parser("progress", help="import results exported from flashcard/trainer pages, or show progress")
    s.add_argument("action", choices=["import", "show"]); s.add_argument("files", nargs="*"); s.add_argument("--module")
    s.set_defaults(fn=cmd_progress)

    s = sub.add_parser("due", help="list items due for review")
    s.add_argument("--module"); s.add_argument("--within", type=int, default=0, help="include items due in the next N days"); s.add_argument("--json", action="store_true"); s.add_argument("-v", "--verbose", action="store_true")
    s.set_defaults(fn=cmd_due)

    s = sub.add_parser("status", help="workspace summary and recommendations")
    s.add_argument("--json", action="store_true")
    s.set_defaults(fn=cmd_status)

    s = sub.add_parser("dashboard", help="build the progress dashboard page")
    s.add_argument("-o", "--out"); s.add_argument("--theme", choices=themes.names())
    s.set_defaults(fn=cmd_dashboard)

    s = sub.add_parser("pdf", help="print a built page to PDF with headless Chrome/Edge")
    s.add_argument("html"); s.add_argument("-o", "--out"); s.add_argument("--query", help="page options, e.g. solutions=end or print=1")
    s.set_defaults(fn=cmd_pdf)

    s = sub.add_parser("new", help="start a data file from a valid starter")
    s.add_argument("kind", choices=["deck", "lesson", "quiz", "exam", "sheet", "events"]); s.add_argument("out")
    s.add_argument("--title"); s.add_argument("--module"); s.add_argument("--subject"); s.add_argument("--force", action="store_true")
    s.add_argument("--outline", help="lesson: comma-separated layouts, one skeleton slide each, e.g. title,points,formula,plot,check,summary")
    s.add_argument("--source", action="append", help="lesson: ID=file-or-title of the material (repeatable), e.g. L3=sources/L03.pdf")
    s.add_argument("--depth", choices=settings.LESSON["lesson_depth"][0] + ["standard"], help="lesson: default from `als.py settings` (medium unless changed)")
    s.add_argument("--grounding", choices=settings.LESSON["lesson_grounding"][0], help="lesson: default from `als.py settings`")
    s.add_argument("--lang", help="lesson: language code for built-in labels (en, de)")
    s.set_defaults(fn=cmd_new)

    s = sub.add_parser("settings", help="show or change lesson settings (depth, grounding, checks, visuals, ...)")
    s.add_argument("pairs", nargs="*", help="key=value to save, e.g. depth=deep checks=many"); s.add_argument("--module", help="read or save for one module")
    s.add_argument("--json", action="store_true")
    s.set_defaults(fn=cmd_settings)

    s = sub.add_parser("extract", help="lecture PDFs to page-numbered text (and page images) for citing")
    s.add_argument("pdfs", nargs="+"); s.add_argument("-o", "--out", help="output folder"); s.add_argument("--module", help="write to modules/<id>/sources/text")
    s.add_argument("--pages", help="e.g. 1-20,25"); s.add_argument("--images", choices=["none", "thin", "all"], default="none", help="render pages as PNG: those without text, or all")
    s.add_argument("--dpi", type=int, default=80); s.add_argument("--toc", action="store_true", help="list the first line of every page")
    s.add_argument("--keep-builds", action="store_true", help="keep slides that only add a line to the previous one"); s.add_argument("--layout", action="store_true", help="keep the page layout (wider text)")
    s.set_defaults(fn=cmd_extract)
    return p


def main(argv=None) -> int:
    args = parser().parse_args(argv)
    try:
        return args.fn(args) or 0
    except (ValueError, FileNotFoundError) as exc:
        return fail(str(exc))


if __name__ == "__main__":
    sys.exit(main())
