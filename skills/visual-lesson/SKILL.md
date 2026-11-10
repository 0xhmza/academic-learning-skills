---
name: visual-lesson
description: Build an animated, step-by-step HTML lesson (presentation) that teaches one topic visually. Use when a student wants a topic explained "visually", "step by step", "animated", "as a presentation", "slides", "walk me through the derivation", "show me how the algorithm works", or needs a diagram that builds up gradually. Produces a themed, self-contained HTML lesson from a small JSON file using a reusable template (progressive reveal, SVG diagrams that build in steps, derivations line by line, code with line focus, timelines, quick checks, speaker notes, autoplay, print to PDF).
---

# Visual lesson

A lesson is a JSON list of slides rendered by `shared/templates/lesson.html`. Claude writes only the
JSON; the template does the animation, theming and navigation.

**Toolkit.** `ALS` = `python "<this skill's base directory>/../../shared/scripts/als.py"`. Layout
reference: `references/lesson-design.md` (read it before the first lesson in a session). Data format:
`../../shared/starters/lesson.json` (one example of every layout).

## Workflow

1. **Scope one topic** (one 10–20 minute idea). If the request is a whole chapter, propose 2–4 lessons
   and start with the first.
2. **Read the source pages** for the topic (module `topics.json` → `sources`). Use the lecturer's
   notation and examples where possible.
3. **Outline in your head**, then write the file:
   `ALS new lesson modules/<id>/data/lesson-<topic>.json --title "…" --module <id> --subject "…"`
   and replace the slides. Typical arc (8–20 slides):
   - `title` → why it matters (`points`) → key `definition` with an example
   - the mechanism: `steps` (derivation), `diagram` (building up), `code` (line focus), `timeline`
   - a `check` every 4–6 slides
   - `compare` against a confusable concept
   - `summary` → the last slide offers flashcards or practice in its notes
4. **Build:** `ALS build modules/<id>/data/lesson-<topic>.json`. Fix validation errors (it checks SVG
   ids used in steps, code highlight line numbers, answer indexes).
5. **Hand over**: the output path, the controls (→ / Space next, ← back, O overview, N notes,
   P autoplay, F full screen), and that the palette button switches the design.
6. For a PDF handout: `ALS pdf <out.html> --query print=1` (every step revealed, one slide per page).

## Diagram slides

Hand-write compact SVG with theme classes (`d-line`, `d-accent`, `d-fill`, `d-text`, …: full list in
`../../shared/references/design-systems.md`). Give each element that should appear later an `id`, and
list the ids per step in `steps`, with one caption per step in `captions`. Build the picture the way a
lecturer draws it on a board: axes → object → annotation → result.

## Quality bar

- One idea per slide; at most 6 points; points are short claims, not paragraphs.
- Every abstract statement gets a concrete example within two slides.
- Reveal order follows reasoning order. Do not reveal a conclusion before its premises.
- `notes` hold what a lecturer would say; slides hold what a student should remember.
- Cite `src` on slides derived from the student's material; `grounded: false` for added context.
