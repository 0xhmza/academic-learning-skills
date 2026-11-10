# Academic Learning Skills

A complete study toolkit for students, built as [Claude](https://claude.com) skills. Drop in your lecture
slides, and Claude sets up the module, explains topics, builds animated lessons, flashcards (HTML and
Anki), interactive practice and mock exams, plans your weeks up to the exam with an `.ics` calendar, pulls
deadlines and files from Moodle, recommends vetted resources, and remembers how you like to learn.

Inspired by [academic-research-skills](https://github.com/imbad0202/academic-research-skills) (research and
paper writing). This toolkit covers the other half of university life: **learning the material**.

## What it does

| Skill | You say | You get |
|---|---|---|
| `study-coach` | "help me study", "what next?", "remember that I…" | onboarding, learner profile, recommendations, dashboard, results import |
| `module-setup` | "here are my lectures" | module folder, source catalogue, topic map with objectives and exam weights |
| `explain` | "I don't get X", "summarise lecture 4", "cheat sheet" | Socratic or direct teaching, Feynman checks, themed summary / cheat-sheet pages (HTML/PDF) |
| `visual-lesson` | "show me step by step" | animated HTML lesson built strictly from your slides or script: plots, flow charts, grids and the lecturer's own figures that build up, derivations, formulas symbol by symbol, quick checks, a depth switch (brief, medium, deep); settings via `als.py settings` |
| `flashcards` | "make cards from lecture 3" | interactive HTML deck (flip, grade, relearn, due today) + Anki `.apkg` + Quizlet/CSV |
| `practice` | "quiz me", "mock exam" | interactive trainer (6 question types, graded hints, step-by-step solutions, timed tests) or printable exam with marking scheme; error log |
| `planner` | "I have an exam in 3 weeks" | backward plan with spaced reviews and interleaving, `.ics` export |
| `lms-connect` | "get my deadlines from Moodle" | Moodle calendar import, course files downloaded into your module (you sign in yourself) |
| `resources` | "a good video on…" | 3–7 verified books, papers, videos and courses matched to your level |

Slash commands for quick access: `/als-start`, `/als-setup`, `/als-learn`, `/als-summary`, `/als-lesson`, `/als-settings`,
`/als-cards`, `/als-practice`, `/als-exam`, `/als-mark`, `/als-plan`, `/als-moodle`, `/als-resources`,
`/als-remember`, `/als-note`, `/als-status`, `/als-review`.

## How it saves tokens

Claude never writes HTML, CSS or JavaScript for your study pages. It writes a small JSON file (cards,
slides, questions), and `shared/scripts/als.py build` merges it with a reusable template and the design
systems into one self-contained page. A 30-card deck is ~5 KB of JSON instead of ~70 KB of page. Editing
means changing the JSON and rebuilding.

## Design systems

Every page picks a design from its subject and can switch theme and light/dark mode in the page itself.

| Theme | Subjects | Look |
|---|---|---|
| **Blueprint** | maths, physics, CS, engineering | inspired by tailwindcss.com: near-black/white, sky accent, Inter + mono labels, hairline grid |
| **Folio** | philosophy, literature, history, languages, arts | editorial book typography, Garamond, paper tones, oxblood ink |
| **Clinic** | biology, medicine, chemistry, psychology | IBM Plex, teal and violet, soft cards, diagram-first |
| **Ledger** | economics, business, law, social science | Libre Franklin + Source Serif, navy and burgundy, tabular figures |

See `examples/showcase/` for one page of each (build them with `python tools/build_examples.py`).

## Install

### Claude Code (CLI, desktop app or IDE)

```
/plugin install academic-learning-skills --marketplace 0xhmza/academic-learning-skills
```

On older Claude Code versions, add the marketplace first:

```
/plugin marketplace add 0xhmza/academic-learning-skills
/plugin install academic-learning-skills
```

Or from a local clone: `/plugin marketplace add ./academic-learning-skills`.

### Requirements

- Python 3.9+ (standard library only)
- Optional: `pip install genanki` for `.apkg` export (without it you get an Anki text import file)
- Optional: Chrome, Edge, Chromium or Brave for one-command PDF export (otherwise use the page's Print button)
- Optional: a browser connection for Claude (Claude in Chrome or the desktop app's browser) for Moodle file downloads

### claude.ai

Skills that only talk (explain, practice live drills, resources, planning advice) work as uploaded skills.
Building pages, Anki files and calendars needs code execution with the `shared/` folder available, and
Moodle access needs a browser connection, so the full toolkit is meant for Claude Code and the desktop app.

## Quick start

1. Open Claude Code in a folder where you want your study files.
2. `/als-start`. Claude asks a few questions and creates `study/profile.md`.
3. `/als-setup Linear Algebra II` and point it at your lecture PDFs (or `/als-moodle files` to fetch them).
4. Then, for example:
   - `/als-lesson eigenvalues`: an animated lesson
   - `/als-cards lecture 7`: flashcards + Anki deck
   - `/als-practice eigenvalues`: an interactive trainer
   - `/als-plan until the exam on 14 Feb`: a plan and `.ics`
5. After studying with a page, click **Save results**, then `/als-review <file>` to update your progress.

## Your study workspace

```
study/
  profile.md        who you are, goals, "Remember" and "Avoid" preferences
  progress.json     spaced-repetition and mastery state
  notes/            notes you dictate
  calendar/         imported deadlines, generated .ics files
  modules/<id>/     module.md, topics.json, errors.md, sources/, data/ (JSON), out/ (pages, decks, PDFs)
```

It is plain Markdown and JSON in your own folder: readable, editable, and yours. Set `ALS_HOME` to keep
it somewhere else. A session-start hook shows Claude a short status (due reviews, deadlines, your
preferences) when you open Claude in a folder that has a workspace.

## Learning science

The defaults follow well-replicated findings: retrieval practice, spacing (Leitner intervals 1–32 days),
interleaving, worked examples with fading, elaboration, concrete examples, dual coding and honest
calibration. See `shared/references/learning-science.md`.

## Integrity and privacy

- For graded work, Claude coaches rather than producing your submission (`shared/references/integrity.md`).
- Claude never types your passwords; you sign in to Moodle yourself. The private calendar URL is never
  written to files.
- Material is grounded in your sources with slide/page references; anything added beyond your notes is
  marked.

## Command-line helper

All deterministic work goes through one script, usable on its own:

```
python shared/scripts/als.py --help
python shared/scripts/als.py build examples/linear-algebra/lesson-eigenvalues.json -o lesson.html
python shared/scripts/als.py anki examples/linear-algebra/deck-eigenvalues.json
python shared/scripts/als.py ics shared/starters/events.json
```

Reference: `shared/references/cli.md`.

## Development

```
python -m unittest discover tests -v     # 22 tests: schemas, build, themes, SRS, ICS, Anki, workspace, CLI, plugin layout
python tools/build_examples.py           # rebuild examples/showcase/
```

Repository layout and conventions: [CLAUDE.md](CLAUDE.md). Changes: [CHANGELOG.md](CHANGELOG.md).

## Credits

- Concept inspired by *Academic Research Skills* by Cheng-I Wu (CC BY-NC 4.0). No text or code is copied from it.
- Blueprint colours come from the MIT-licensed Tailwind CSS palette; Tailwind is a trademark of Tailwind Labs, and this project is not affiliated with it.
- Fonts (Inter, JetBrains Mono, EB Garamond, Cormorant Garamond, IBM Plex, Libre Franklin, Source Serif 4) are served by Google Fonts under the SIL Open Font License. Maths is rendered with KaTeX (MIT).

## License

MIT, see [LICENSE](LICENSE).
