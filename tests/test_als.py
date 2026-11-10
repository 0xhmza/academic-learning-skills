"""Tests for the ALS toolkit. Run: python -m unittest discover tests -v"""
from __future__ import annotations

import datetime as dt
import json
import re
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "shared" / "scripts"))

import als  # noqa: E402
from als_lib import anki, build, ics, paths, progress, report, themes, workspace  # noqa: E402
from als_lib.validate import validate_data, validate_file  # noqa: E402

STARTERS = sorted((ROOT / "shared" / "starters").glob("*.json"))
EXAMPLES = sorted(p for p in (ROOT / "examples").glob("*/*.json") if p.parent.name != "showcase")
TOKENS = ["--bg", "--bg-elev", "--bg-sunken", "--text", "--text-muted", "--text-faint", "--border", "--border-strong",
          "--accent", "--accent-contrast", "--accent-soft", "--accent-2", "--good", "--good-soft", "--bad", "--bad-soft",
          "--warn", "--warn-soft"]


class TempWS(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="als-test-"))
        self.ws = self.tmp / "study"

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)


class TestData(unittest.TestCase):
    def test_starters_and_examples_validate(self):
        self.assertTrue(STARTERS and EXAMPLES)
        for f in STARTERS + EXAMPLES:
            with self.subTest(f=f.name):
                errs, _ = validate_file(f)
                self.assertEqual(errs, [])

    def test_semantic_errors_are_caught(self):
        quiz = json.loads((ROOT / "shared/starters/quiz.json").read_text(encoding="utf-8"))
        quiz["questions"][0]["answer"] = 9
        quiz["questions"][4]["text"] = "only {{1}} here"
        quiz["questions"].append(dict(quiz["questions"][1]))
        errs, _ = validate_data(quiz)
        joined = "\n".join(errs)
        self.assertIn("out of range", joined)
        self.assertIn("cloze text has blanks [1]", joined)
        self.assertIn("duplicate question id", joined)

        lesson = json.loads((ROOT / "shared/starters/lesson.json").read_text(encoding="utf-8"))
        diag = next(s for s in lesson["slides"] if s["layout"] == "diagram")
        diag["steps"].append(["nope"])
        code = next(s for s in lesson["slides"] if s["layout"] == "code")
        code["highlight"].append([99])
        joined = "\n".join(validate_data(lesson)[0])
        self.assertIn("'nope'", joined)
        self.assertIn("highlight line 99", joined)

    def test_schema_errors(self):
        errs, _ = validate_data({"als": "1", "kind": "deck", "title": "x", "cards": [{"id": "a", "type": "basic", "front": "q"}]})
        self.assertTrue(any("back" in e for e in errs))
        errs, _ = validate_data({"als": "1", "kind": "nope"})
        self.assertTrue(errs)


class TestThemes(unittest.TestCase):
    def test_every_theme_defines_all_tokens_in_both_modes(self):
        for name in themes.names():
            css = (paths.DESIGN / f"{name}.css").read_text(encoding="utf-8")
            light = re.search(r'\[data-als-theme="%s"\]\s*\{(.*?)\n\}' % name, css, re.S).group(1)
            dark = re.search(r'\[data-als-theme="%s"\]\[data-als-mode="dark"\]\s*\{(.*?)\n\}' % name, css, re.S).group(1)
            for tok in TOKENS:
                with self.subTest(theme=name, token=tok):
                    self.assertRegex(light, re.escape(tok) + r"\s*:")
                    self.assertRegex(dark, re.escape(tok) + r"\s*:")

    def test_routing(self):
        cases = {"Linear Algebra II": "blueprint", "Kant's ethics": "folio", "Molecular biology": "clinic",
                 "Microeconomics": "ledger", "Constitutional law": "ledger", "Organic chemistry": "clinic",
                 "Spain travel": "blueprint", "Medieval history": "folio", "Machine learning": "blueprint"}
        for subject, want in cases.items():
            with self.subTest(subject=subject):
                self.assertEqual(themes.route(subject)[0], want)


class TestBuild(TempWS):
    def test_build_every_kind_and_theme(self):
        for f in STARTERS:
            data = json.loads(f.read_text(encoding="utf-8"))
            if data["kind"] == "events":
                continue
            for theme in themes.names():
                with self.subTest(kind=data["kind"], theme=theme):
                    page = build.render(data, theme)
                    self.assertNotRegex(page, r"/\*ALS:|<!--ALS:|\{\{(title|lang|theme|version)\}\}")
                    self.assertIn(f'data-als-theme="{theme}"', page)
                    blob = re.search(r'<script type="application/json" id="als-data">(.*?)</script>', page, re.S).group(1)
                    self.assertEqual(json.loads(blob)["title"], data["title"])

    def test_data_cannot_break_out_of_script(self):
        data = {"als": "1", "kind": "sheet", "title": "</script><script>alert(1)</script>", "blocks": [{"type": "section", "body": "<!-- x"}]}
        page = build.render(data, "folio")
        blob = re.search(r'<script type="application/json" id="als-data">(.*?)</script>', page, re.S).group(1)
        self.assertEqual(json.loads(blob)["title"], data["title"])
        self.assertNotIn("<title></script>", page)

    def test_theme_priority(self):
        workspace.init(self.ws)
        workspace.new_module(self.ws, "ethics", "Ethics", subject="Philosophy", theme="ledger")
        data = {"als": "1", "kind": "sheet", "title": "x", "module": "ethics", "subject": "Linear algebra", "blocks": [{"type": "section"}]}
        self.assertEqual(build.choose_theme(data, self.ws)[0], "ledger")
        self.assertEqual(build.choose_theme(dict(data, theme="clinic"), self.ws)[0], "clinic")
        self.assertEqual(build.choose_theme(data, self.ws, "folio")[0], "folio")

    def test_module_output_path_and_due_embedding(self):
        workspace.init(self.ws)
        workspace.new_module(self.ws, "linear-algebra", "Linear Algebra")
        src = paths.module_dir(self.ws, "linear-algebra") / "data" / "deck.json"
        deck = json.loads((ROOT / "examples/linear-algebra/deck-eigenvalues.json").read_text(encoding="utf-8"))
        src.write_text(json.dumps(deck), encoding="utf-8")
        progress.import_results(self.ws, {"kind": "results", "module": "linear-algebra", "title": "t", "exported": "1",
                                          "date": (dt.date.today() - dt.timedelta(days=5)).isoformat(),
                                          "items": [{"id": "l7-01", "grade": "again"}]})
        out, theme, _, _ = build.build_file(src, ws=self.ws)
        self.assertEqual(out, paths.module_dir(self.ws, "linear-algebra") / "out" / "deck.html")
        self.assertEqual(theme, "blueprint")
        blob = re.search(r'id="als-data">(.*?)</script>', out.read_text(encoding="utf-8"), re.S).group(1)
        self.assertEqual(json.loads(blob)["_due"], ["l7-01"])


class TestProgress(TempWS):
    def results(self, items, date="2026-11-10", exported="a"):
        return {"als": "1", "kind": "results", "module": "m", "title": "Deck", "date": date, "exported": exported, "items": items}

    def test_leitner_schedule(self):
        on = dt.date(2026, 11, 10)
        item = progress.schedule(None, "good", on)
        self.assertEqual((item["box"], item["due"]), (1, "2026-11-12"))
        item = progress.schedule(item, "easy", on)
        self.assertEqual((item["box"], item["due"]), (3, "2026-11-18"))
        item = progress.schedule(item, "again", on)
        self.assertEqual((item["box"], item["due"], item["lapses"]), (0, "2026-11-11", 1))
        for _ in range(10):
            item = progress.schedule(item, "good", on)
        self.assertEqual(item["box"], 5)

    def test_import_is_idempotent_and_aggregates_sessions(self):
        r = self.results([{"id": "c1", "grade": "again", "topic": "t"}, {"id": "c1", "grade": "good", "topic": "t"}, {"id": "c2", "grade": "easy"}])
        s = progress.import_results(self.ws, r)
        self.assertEqual((s["items"], s["lapses"]), (2, 1))
        self.assertTrue(progress.import_results(self.ws, r)["skipped"])
        data = progress.load(self.ws)
        self.assertEqual(data["items"]["m/c1"]["box"], 0)
        self.assertEqual(data["items"]["m/c2"]["box"], 2)
        self.assertEqual(data["topics"]["m/t"]["attempts"], 2)

    def test_quiz_results_and_mastery(self):
        items = [{"id": "q1", "topic": "eigen", "correct": True}, {"id": "q2", "topic": "eigen", "correct": False},
                 {"id": "q3", "topic": "eigen", "correct": True, "hintsUsed": 2}, {"id": "q4", "topic": "eigen", "correct": False, "partial": True}]
        progress.import_results(self.ws, self.results(items, exported="b"))
        m = progress.mastery(self.ws)["m/eigen"]["mastery"]
        self.assertTrue(0.3 < m < 0.8, m)
        self.assertEqual(progress.label(m), "developing" if m >= 0.5 else "weak")
        self.assertEqual(progress.grade_of({"correct": True, "hintsUsed": 1}), "hard")
        self.assertEqual(progress.grade_of({"correct": False, "partial": True}), "hard")

    def test_due(self):
        progress.import_results(self.ws, self.results([{"id": "c1", "grade": "again"}], date="2026-01-01"))
        self.assertEqual(progress.due(self.ws), {"m": ["c1"]})
        self.assertEqual(progress.due(self.ws, on=dt.date(2025, 12, 1)), {})


class TestCalendar(unittest.TestCase):
    def test_write_and_read_roundtrip(self):
        spec = json.loads((ROOT / "shared/starters/events.json").read_text(encoding="utf-8"))
        spec["events"].append({"title": "Long title with commas, semicolons; and a very long description " * 3, "start": "2026-12-01T10:00", "description": "Line one\nLine two, with comma"})
        text, _ = ics.to_ics(spec)
        self.assertTrue(text.startswith("BEGIN:VCALENDAR\r\n") and text.endswith("END:VCALENDAR\r\n"))
        for line in text.split("\r\n"):
            self.assertLessEqual(len(line.encode("utf-8")), 75)
        events = ics.parse_ics(text)
        self.assertEqual(len(events), len(spec["events"]))
        by_title = {e["title"]: e for e in events}
        self.assertTrue(by_title["Problem sheet 4 due"]["allDay"])
        self.assertEqual(by_title["Problem sheet 4 due"]["start"], "2026-11-20")
        self.assertEqual(by_title["Problem sheet 4 due"]["category"], "deadline")
        long = next(e for e in events if e["title"].startswith("Long title"))
        self.assertIn("Line two, with comma", long["description"])
        self.assertEqual(long["start"], "2026-12-01T10:00")
        self.assertEqual(text.count("BEGIN:VALARM"), 4)

    def test_parse_moodle_style_feed(self):
        feed = ("BEGIN:VCALENDAR\r\nVERSION:2.0\r\nBEGIN:VEVENT\r\nUID:123@moodle.example.edu\r\nSUMMARY:Problem sheet 5 is due\r\n"
                "DESCRIPTION:Submit via the assign\r\n ment page\\, please\r\nCATEGORIES:MATH202\r\nDTSTART:20261120T225900Z\r\n"
                "DTEND:20261120T225900Z\r\nEND:VEVENT\r\nBEGIN:VEVENT\r\nSUMMARY:Final exam Ethics\r\nDTSTART;VALUE=DATE:20270210\r\nEND:VEVENT\r\nEND:VCALENDAR\r\n")
        events = ics.parse_ics(feed)
        self.assertEqual([e["category"] for e in events], ["deadline", "exam"])
        self.assertEqual(events[0]["lmsCategory"], "MATH202")
        self.assertEqual(events[0]["description"], "Submit via the assignment page, please")
        self.assertTrue(events[1]["allDay"])


class TestAnki(TempWS):
    def setUp(self):
        super().setUp()
        self.deck = json.loads((ROOT / "examples/linear-algebra/deck-eigenvalues.json").read_text(encoding="utf-8"))

    @unittest.skipUnless(anki.has_genanki(), "genanki not installed")
    def test_apkg(self):
        out, n = anki.to_apkg(self.deck, self.tmp / "d.apkg")
        self.assertEqual(n, len(self.deck["cards"]))
        self.assertGreater(out.stat().st_size, 1000)

    def test_text_exports(self):
        out, _ = anki.to_anki_tsv(self.deck, self.tmp / "d.txt")
        text = out.read_text(encoding="utf-8")
        self.assertTrue(text.startswith("#separator:tab\n#html:true\n"))
        self.assertIn(r"\(A\mathbf v = \lambda\mathbf v\)", text)
        self.assertIn("Cloze", text)
        q, n = anki.to_quizlet(self.deck, self.tmp / "q.txt")
        self.assertEqual(len(q.read_text(encoding="utf-8").strip().splitlines()), n)
        self.assertIn("____", q.read_text(encoding="utf-8"))


class TestWorkspace(TempWS):
    def test_init_remember_note_and_status(self):
        workspace.init(self.ws, name="Sam", programme="BSc Physics")
        workspace.remember(self.ws, "Prefers worked examples first")
        workspace.remember(self.ws, "Long videos", "Avoid")
        workspace.remember(self.ws, "Uses German terms")
        prof = workspace.profile(self.ws)
        self.assertEqual(prof["name"], "Sam")
        rem = prof["_sections"]["Remember"]
        self.assertEqual(len(rem), 2)
        self.assertTrue(rem[0].endswith("Prefers worked examples first"))
        self.assertIn("Long videos", prof["_sections"]["Avoid"][0])
        # sections keep their order: Remember is still before Avoid
        body = (self.ws / "profile.md").read_text(encoding="utf-8")
        self.assertLess(body.index("Uses German terms"), body.index("## Avoid"))
        note = workspace.add_note(self.ws, "Eigen intuition", "Directions that only stretch.")
        self.assertTrue(note.name.endswith("eigen-intuition.md"))
        self.assertIn("Prefers worked examples first", report.status_text(self.ws))

    def test_module_and_recommendations(self):
        workspace.init(self.ws)
        exam = (dt.date.today() + dt.timedelta(days=10)).isoformat()
        workspace.new_module(self.ws, "linear-algebra", "Linear Algebra", exam_date=exam)
        tfile = paths.module_dir(self.ws, "linear-algebra") / "topics.json"
        paths.write_json(tfile, {"als": "1", "kind": "topics", "module": "linear-algebra",
                                 "topics": [{"id": "eigen", "title": "Eigenvalues", "weight": 3}, {"id": "det", "title": "Determinants", "weight": 1}]})
        progress.import_results(self.ws, {"kind": "results", "module": "linear-algebra", "title": "q", "exported": "x", "date": dt.date.today().isoformat(),
                                          "items": [{"id": "q1", "topic": "eigen", "correct": False}]})
        snap = report.snapshot(self.ws)
        mod = snap["modules"][0]
        self.assertEqual(mod["examDays"], 10)
        self.assertEqual(mod["topics"][0]["id"], "eigen")
        text = " ".join(snap["next"])
        self.assertIn("Eigenvalues", text)
        self.assertIn("10 days", text)
        with self.assertRaises(ValueError):
            workspace.new_module(self.ws, "Bad Id", "x")


class TestCLI(TempWS):
    def run_cli(self, *args):
        return als.main(["--home", str(self.ws), *args])

    def test_cli_flow(self):
        self.assertEqual(self.run_cli("init", "--name", "Sam"), 0)
        self.assertEqual(self.run_cli("module", "new", "ethics", "--title", "Ethics", "--subject", "Philosophy"), 0)
        out = self.tmp / "s.json"
        self.assertEqual(self.run_cli("new", "sheet", str(out), "--title", "Kant", "--module", "ethics"), 0)
        self.assertEqual(self.run_cli("build", str(out)), 0)
        self.assertIn('data-als-theme="folio"', out.with_suffix(".html").read_text(encoding="utf-8"))
        self.assertEqual(self.run_cli("validate", str(out)), 0)
        self.assertEqual(self.run_cli("ics", str(ROOT / "shared/starters/events.json"), "-o", str(self.tmp / "p.ics")), 0)
        self.assertEqual(self.run_cli("ics-import", str(self.tmp / "p.ics"), "--map", "X=ethics"), 0)
        self.assertTrue((self.ws / "calendar" / "events.json").exists())
        self.assertEqual(self.run_cli("dashboard"), 0)
        self.assertTrue((self.ws / "dashboard.html").exists())
        self.assertEqual(self.run_cli("validate", str(ROOT / "README.md")), 1)


class TestPluginLayout(unittest.TestCase):
    def test_manifests(self):
        plugin = json.loads((ROOT / ".claude-plugin/plugin.json").read_text(encoding="utf-8"))
        market = json.loads((ROOT / ".claude-plugin/marketplace.json").read_text(encoding="utf-8"))
        self.assertEqual(plugin["name"], market["plugins"][0]["name"])
        self.assertEqual(plugin["version"], market["plugins"][0]["version"])
        hooks = json.loads((ROOT / "hooks/hooks.json").read_text(encoding="utf-8"))
        self.assertIn("SessionStart", hooks["hooks"])

    def test_skills_and_commands(self):
        skills = sorted(p.parent.name for p in (ROOT / "skills").glob("*/SKILL.md"))
        self.assertEqual(skills, ["explain", "flashcards", "lms-connect", "module-setup", "planner", "practice", "resources", "study-coach", "visual-lesson"])
        try:
            import yaml
        except ImportError:
            yaml = None
        for f in list((ROOT / "skills").glob("*/SKILL.md")) + list((ROOT / "commands").glob("*.md")):
            text = f.read_text(encoding="utf-8")
            m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
            with self.subTest(f=f.name):
                self.assertIsNotNone(m)
                if yaml:
                    meta = yaml.safe_load(m.group(1))
                    self.assertTrue(meta.get("description"))
                    if f.name == "SKILL.md":
                        self.assertEqual(meta["name"], f.parent.name)
                        self.assertLessEqual(len(meta["description"]), 1024)
                # every relative reference in a skill must exist
                for ref in re.findall(r"`(\.\./\.\./shared/[^`\s]+|references/[^`\s]+)`", text):
                    self.assertTrue((f.parent / ref).exists(), f"{f}: missing {ref}")
            for cmd_skill in re.findall(r"academic-learning-skills:([a-z-]+)", text):
                self.assertIn(cmd_skill, skills, f"{f} points to unknown skill {cmd_skill}")


if __name__ == "__main__":
    unittest.main()
