# Changelog

## 0.1.0 — 2026-11-10

First release.

- Nine skills: study-coach, module-setup, explain, visual-lesson, flashcards, practice, planner,
  lms-connect, resources; 16 slash commands.
- Learner workspace (`study/`): profile with Remember/Avoid preferences, notes, modules with topic maps and
  error logs, Leitner spaced repetition and topic mastery in `progress.json`.
- Templates: flashcards, animated lesson, interactive trainer, printable exam, study sheet, dashboard.
- Four design systems (Blueprint, Folio, Clinic, Ledger) with light and dark modes, in-page switching
  and subject routing.
- CLI `shared/scripts/als.py`: init, remember, note, module, validate, build, anki (.apkg / Anki text /
  Quizlet / CSV), ics, ics-import (Moodle calendar export), progress import, due, status, dashboard, pdf,
  new.
- SessionStart hook with a compact study status.
- Examples for linear algebra, ethics, cell biology and microeconomics; 22 tests.
