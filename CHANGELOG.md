# Changelog

## 0.2.0 — 2026-11-10

Visual lessons: faithful to the source, adjustable, cheaper to write.

- **Strict source grounding** is the default for lessons. A lesson with `"grounding": "strict"` lists its
  `sources`, cites `src` on every slide and may not contain added content; the build enforces it. The
  skill asks the student instead of guessing when the material is unclear.
- **Lesson settings** in `profile.md` or a module's `module.md`, read and changed with `als.py settings`:
  depth (brief, medium, deep; default medium), audience (first-time, revision), grounding, order, when to ask, checks, visuals, notes, language.
- **Depth switch** in the page (key D): slides and derivation rows tagged `level` are shown or hidden, so one
  file serves every depth. `more` adds an on-demand explanation per slide (key E).
- **Visual components**: `plot` (curves from expressions or data), `flow`, `grid` (with ranges such as
  `in.r1c1:r3c3`), `layers`, `tree`, `bars`, and `figure` (the lecturer's own image with spotlight marks,
  embedded at build time). Step tokens `-id` (hide) and `!id` (highlight), `focus`, self-drawing lines,
  built-in arrowheads.
- **New layouts**: `formula` (symbol by symbol), `table`, `pitfall`, `recall`; `steps` gains `given`,
  `result`, `why` and per-row `level`. LaTeX `macros` per file. German labels with `"lang": "de"`.
- **`/als-settings`** command shows or changes the saved settings; a depth word after `/als-lesson <topic>`
  applies to one run.
- **CLI**: `extract` (page-numbered text and page images from PDFs, build-up slides merged, figure-only
  pages reported), `settings`, `new lesson --outline/--source/--depth/--grounding`; `build` and `validate`
  accept folders and globs.

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
