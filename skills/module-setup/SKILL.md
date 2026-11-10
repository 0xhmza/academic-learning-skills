---
name: module-setup
description: Set up a course module from the student's material. Use when a student shares lecture slides, PDFs, scripts, notes, a syllabus or a folder of course files and wants them organised, or says "set up my module", "here are my lectures", "make a topic map", "what's in this course", "add lecture 5". Creates the module folder, catalogues sources with ids, extracts a topic map with learning objectives, prerequisites and exam weights, and records the assessment format so the other skills (explain, flashcards, practice, planner) can work from it.
---

# Module setup

Turns a pile of course files into a structured module: `module.md` (overview, assessment, sources),
`topics.json` (topic map) and a tidy `sources/` folder. Everything else in the toolkit builds on this.

**Toolkit.** `ALS` = `python "<this skill's base directory>/../../shared/scripts/als.py"`.
Workspace layout: `../../shared/references/workspace.md`. Grounding rules:
`../../shared/references/grounding.md`.

## Workflow

1. **Locate the module.** `ALS module list`. If it does not exist:
   `ALS module new <id> --title "<title>" --code "<code>" --term "<term>" --exam-date YYYY-MM-DD --subject "<subject>"`.
   Ids are kebab-case (`linear-algebra`, `phil-101`). The command prints the theme routing; set
   `--theme` only if the student wants a different look.
2. **Collect sources.** Copy (never move) the student's files into `modules/<id>/sources/` with sortable
   names: `L01-vector-spaces.pdf`, `T-strang-ch4.pdf`, `S01-problem-sheet.pdf`, `N-own-notes.md`.
   Files downloaded from Moodle by `lms-connect` are already there.
3. **Read efficiently.** Use the Read tool on PDFs in page ranges (`pages: "1-20"`); for long scripts read
   the table of contents first, then each chapter's opening and summary pages. For `.pptx` use the pptx
   skill or `python -c` with python-pptx; for `.docx` the docx skill. Do not read every page of a 300-page
   textbook: read what the lectures cover.
4. **Catalogue sources** in the `## Sources` table of `module.md`:

   | id | title | locator | file |
   |---|---|---|---|
   | L1 | Lecture 1: Vector spaces | slides 1-42 | sources/L01-vector-spaces.pdf |

   Ids: `L<n>` lectures, `S<n>` problem sheets, `T` textbook, `E<year>` past exams, `N` notes. These ids
   are what every card and question cites in `src`.
5. **Build the topic map** in `topics.json` (format in workspace.md). Per topic:
   - `id` (kebab-case), `title` in the course's words
   - `objectives`: 2–4 verbs a student must be able to do ("compute…", "explain why…", "compare…").
     Use Bloom-style verbs; harvest them from the syllabus and past exams when available.
   - `prereqs`: topic ids within this module (or `other-module/topic`)
   - `sources`: locators (`"L3 s.4-18"`, `"T ch.5"`)
   - `weight` 1–3: how much it counts in the assessment. Base it on past exams and stated weightings;
     default 1, use 3 sparingly. Say what you based weights on.
   Aim for 8–25 topics per module; split topics a single 45-minute session cannot cover.
6. **Record assessment** under `## Assessment`: format (written/oral/MC/project), duration, allowed aids,
   grading, admission requirements, recurring question types from past exams.
7. **Write `## Overview`**: 4–8 sentences on what the course is about and how topics connect.
8. **Log it**: `ALS module log <id> --text "Set up from 9 lecture PDFs and 2 past exams; 17 topics."`
9. **Offer next steps** (one line each): a summary sheet (`explain`), first flashcard deck
   (`flashcards`), a study plan to the exam (`planner`).

## Adding material later

New lecture: add the file and source row, update or add topics (keep existing ids stable: progress is
keyed by them), log it. Never renumber existing source ids.

## Quality bar

- Topic titles and notation match the lecturer's, not a textbook's.
- Every objective is testable. "Understand X" is not an objective; "explain why X implies Y" is.
- If material is missing (no syllabus, no past exams), say what you could not determine.
