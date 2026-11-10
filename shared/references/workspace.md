# The learner workspace

All skills share one folder per student. It is what lets the toolkit remember preferences, track
mastery and plan reviews across sessions.

## Where it lives

1. `$ALS_HOME` if set.
2. Otherwise `./study/` in the current working directory.

`python <plugin>/shared/scripts/als.py where` prints the resolved path. `als.py init` creates it.

## Layout

```
study/
  profile.md                  who the student is, goals, preferences, "Remember" list
  progress.json               spaced-repetition and mastery state (written only by the CLI)
  notes/                      notes the student dictates: YYYY-MM-DD-<slug>.md
  calendar/                   generated .ics files and imported LMS feeds (events.json)
  modules/<module-id>/
    module.md                 overview, assessment, exam date, sources, log
    topics.json               topic map with objectives and prerequisites
    errors.md                 error log: what went wrong, why, the fix
    sources/                  the student's material (PDFs, slides, downloads)
    data/                     JSON data files for templates (re-buildable, re-usable)
    out/                      built HTML, .apkg, .pdf, .ics
```

Module ids are lowercase kebab-case (`linear-algebra`, `phil-101-ethics`).

## profile.md

```markdown
---
name: Sam
programme: BSc Physics, year 2
timezone: Europe/Berlin
languages: en, de
theme: auto                # auto | blueprint | folio | clinic | ledger
session_minutes: 45
weekly_hours: 12
lms_url: https://moodle.example.edu
lesson_depth: medium        # brief | medium | deep
lesson_grounding: strict    # strict | extended
---

## Goals
- Pass Linear Algebra II with at least a 2.0

## How I learn best
- Worked examples before theory
- Short sessions, flashcards on the bus

## Remember
- 2026-11-10: Prefers German terms in brackets next to English ones.

## Avoid
- Long video recommendations (> 30 min)
```

Rules for skills:

- **Read `profile.md` before producing anything.** Respect `theme`, language, session length and the
  Remember/Avoid lists.
- **Lesson settings** (`lesson_depth`, `lesson_audience`, `lesson_grounding`, `lesson_order`, `lesson_ask`, `lesson_checks`,
  `lesson_visuals`, `lesson_notes`, `lesson_language`) live in the front matter here, or in a module's
  `module.md` to override them for that module. Read and change them with `als.py settings`.
- **Append, never rewrite**, when the student says "remember that…": add a dated bullet under
  `## Remember` (or `## Avoid`). Use `als.py remember "<text>"` so the format stays consistent.
- Never store passwords, tokens or the private Moodle calendar URL in the profile. Those stay in the
  student's environment (`ALS_MOODLE_ICS_URL`) or are pasted per session.

## module.md

```markdown
---
id: linear-algebra
title: Linear Algebra II
code: MATH-202
term: WS 2026/27
exam_date: 2027-02-14
theme: blueprint
lms_course_url: https://moodle.example.edu/course/view.php?id=123
---

## Overview
## Assessment
## Sources
| id | title | locator | file |
|---|---|---|---|
| L1 | Lecture 1: Vector spaces | slides 1-40 | sources/L01.pdf |

## Log
- 2026-11-10: Module set up from 6 lecture PDFs.
```

## topics.json

```json
{
  "als": "1",
  "kind": "topics",
  "module": "linear-algebra",
  "topics": [
    {
      "id": "eigen",
      "title": "Eigenvalues and eigenvectors",
      "objectives": ["Compute eigenvalues of a 3x3 matrix", "Explain geometric meaning"],
      "prereqs": ["determinants"],
      "sources": ["L3 s.4-12"],
      "weight": 2
    }
  ]
}
```

`weight` (1–3) reflects how heavily the topic counts in the assessment. It drives the planner.

## progress.json

Written only by `als.py progress import` and `als.py progress record`. Skills read it through
`als.py due` and `als.py status`, never by editing it directly.

```json
{
  "als": "1",
  "kind": "progress",
  "items":  { "linear-algebra/c12": { "box": 2, "due": "2026-11-14", "last": "2026-11-10", "seen": 3, "lapses": 1 } },
  "topics": { "linear-algebra/eigen": { "attempts": 14, "correct": 9, "last": "2026-11-10", "mastery": 0.61 } }
}
```

- **Items** (cards, questions) use Leitner boxes 0–5 with intervals of 1, 2, 4, 8, 16, 32 days. A
  correct answer moves up a box, a wrong one drops to box 0.
- **Topic mastery** is an exponentially weighted share of correct answers (recent attempts count more).
  Below 0.5 = weak, 0.5–0.8 = developing, above 0.8 = secure.

## errors.md

```markdown
## 2026-11-10 · eigen · q7
- **What happened:** Forgot to subtract λ on the diagonal.
- **Why:** Treated det(A) and det(A − λI) as the same.
- **Fix:** Write A − λI explicitly before expanding.
```

The practice skill appends here after grading. The coach reads it to recommend what to work on next.
