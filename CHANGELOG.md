# Changelog

## 0.3.0 - 2026-11-12

Feedback round on the visual lessons: typography, animation, layout, design, accessibility, languages and
depth of explanation.

- **Maths is always typeset.** Plain-text maths is converted automatically: Unicode symbols (σ(z), x₁,
  O(n²), ∂L/∂w), equations of simple terms (f(3) = 6, p < 0.05), powers and subscripts (x^2, a_n), numbers
  next to maths, chemical formulas (H₂O) and `egin{...}` environments. Fields named `math`, `formula`
  and `sym` accept values wrapped in `$…$`. Diagram labels and plot ticks use the maths font; labels
  containing `$…$` are typeset by KaTeX inside the drawing. The build warns about LaTeX outside `$…$` and
  about unpaired `$`. Display formulas shrink to fit instead of scrolling.
- **No more flashing in animated diagrams.** A new slide starts in its final starting state with
  transitions suspended, so elements of later steps no longer appear and vanish.
- **No stray scrollbars; scrollbars follow the theme.** Slide content never scrolls horizontally; every
  scrollbar that remains uses the theme colours in light and dark mode.
- **Folio and Ledger redesigned.** Folio is now a literary quarterly (Fraunces and Newsreader, warm paper,
  plum ink); Ledger is the financial pages (DM Serif Display and DM Sans, newsprint, Oxford blue).
  Blueprint and Clinic keep their looks; all four have Arabic font stacks and a status bar colour.
- **Collapsible panels and a status bar.** Every page has hideable panels (header, outline sidebar,
  controls, status bar), a focus mode (Z) that hides them all, and small handles to bring them back. The
  status bar shows slide and step, depth, view and reading time left, a study timer, a 25/50 minute focus
  countdown, the clock and text size controls. Flashcards, the trainer, exams, sheets and the dashboard
  have it too, with data that fits them (accuracy and pace, correct answers and hints, reading time).
- **Arabic and right-to-left support in every template.** `"lang": "ar"` (or he, fa, ur) mirrors the page:
  text, lists, outline, navigation and key arrows; maths, code and diagrams stay left-to-right. Arabic
  interface text and German for all 245 strings (`shared/templates/i18n.js`, checked by
  `tools/i18n_keys.py`), Arabic font pairings per theme, Arabic subject names route to themes, and Anki
  exports of Arabic decks are right-to-left.
- **Lessons explain instead of outlining.** Slides carry `lead`, `explain`, per-point `detail`, `why` per
  derivation row and `takeaway`; `intuition` holds the tutor's own, labelled analogies. New `text`,
  `section` and `objectives` layouts. Study view (explanations on the page, default) and present view
  (compact, key V). Outline sidebar (key T), "all at once" switch (key A). The build warns about thin
  slides. New settings `lesson_explain`, `lesson_intuition`, `lesson_view`.
- **Skills updated from the research.** Retrieval, spacing and successive relearning, pretesting,
  self-explanation, generative learning, ICAP, multimedia principles and tutor behaviour from LearnLM's
  pedagogy principles (`shared/references/learning-science.md`). Practice adds diagnostic questions,
  confidence ratings, find-the-error questions and why-questions; the coach asks for a one-minute summary
  and recommends a weak topic's prerequisites first; flashcards count a card as learned only after
  recalls on several days.
- Examples: eigenvalue and Kant lessons rewritten with explanations, plus an Arabic lesson on the
  derivative. 38 tests (9 more) including Node tests for the maths conversion.

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
