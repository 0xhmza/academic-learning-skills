---
name: visual-lesson
description: Build an animated, step-by-step HTML lesson (presentation) that teaches one topic visually and sticks to the student's own script or slides. Use when a student wants a topic explained "visually", "step by step", "animated", "as a presentation", "slides", "walk me through the derivation", "show me how the algorithm works", wants lessons made from lecture slides or a script, or wants to change how deep lessons go ("more detail", "shorter", "explain every step"). Produces a themed, self-contained HTML lesson from a small JSON file using a reusable template (progressive reveal, ready-made plots, flow charts, grids, trees and layer diagrams, the lecturer's own figures with spotlights, derivations line by line, formulas explained symbol by symbol, code with line focus, quick checks, a depth switch, speaker notes, autoplay, print to PDF). Strict source grounding by default, with settings for depth, visuals, checks and notes. Asks the student instead of guessing when the material is unclear.
---

# Visual lesson

A lesson is a JSON list of slides rendered by `shared/templates/lesson.html`. Claude writes only the
JSON; the template does the animation, the drawing, theming and navigation.

**Toolkit.** `ALS` = `python "<this skill's base directory>/../../shared/scripts/als.py"`.
Read once per session, before the first lesson: `references/lesson-design.md` (layouts, depth,
explaining techniques) and `references/components.md` (visual components). Do not read the template,
the schema or the starter; `ALS new lesson --outline …` writes a skeleton of exactly the layouts asked for.

## The source contract

The student's script or slides are the lesson. By default (`lesson_grounding: strict`):

1. **Only what the material says.** Every definition, claim, formula, number, example, name and
   figure on a slide comes from the given material. No outside facts, no invented examples, no
   analogies of your own, no "standard background", however helpful.
2. **Every slide cites it.** `src` names the source id and the page or slide (`"L3 s.12"`,
   `"Script p.44"`). Only `title` and `summary` slides may go without. The build fails otherwise.
3. **The lecturer's notation, terms, order and language.** Keep their symbols and names. Keep their
   order unless `lesson_order: teaching`.
4. **What you may add** is presentation, not content: splitting a slide into steps, turning a formula
   into a plot of that same formula, redrawing a figure the source shows, naming the parts of a formula
   the source defines, questions whose answers are in the material, and the mechanical algebra between
   two lines the source gives (cite the same page).
5. **Nothing is silently dropped or bent.** If a page is skipped, say so in the hand-over.
6. **Unclear means ask** (next section). Never fill a gap from general knowledge.

`extended` grounding lifts rule 1 only: added content is allowed when it is marked `"grounded": false`
(the page shows "beyond your notes"). Use it only when the student chose it, in settings or in words.
`shared/references/grounding.md` (path from here: `../../shared/references/grounding.md`) has the citation format.

## Ask, do not guess

Read all the material for the lesson first, collect every open point, then ask once (use the question
tool if the session has one, with concrete options; otherwise ask in plain text and wait). Ask when:

- it is unclear **which file, version or pages** are the script for this topic, or two versions differ;
- a page is **figure-only or unreadable** and, after looking at its image, you still cannot tell what it
  shows or cannot read a value;
- a **symbol or term is used but not defined** in the material, or is used in two ways;
- the material **seems to contain a mistake**, or two sources disagree;
- a step is **missing** and cannot be rebuilt from the source's own lines;
- the request does not say **what to cover** and the material allows several readings.

Offer "leave it out" as an option every time. Do not ask about things the settings already answer
(depth, order, language, number of checks). For a batch of lessons, ask once for the batch, not per lesson.
With `lesson_ask: never`, or when nobody can answer, leave the unclear part out and list it in the
hand-over under "Left out or unclear". With `lesson_ask: always`, show the outline (slide titles with
their pages) and wait for a yes before writing.

## Settings

`ALS settings --module <id>` prints what applies (module, then profile, then default). Read it before
every lesson. The student's words in the request win over stored settings.

| Setting | Values (default first) | Effect |
|---|---|---|
| `lesson_depth` | `medium`, `brief`, `deep` | how much is covered and how finely it is stepped |
| `lesson_audience` | `first-time`, `revision` | first contact (orient, concrete first, every term explained) or compact revision |
| `lesson_grounding` | `strict`, `extended` | the source contract above |
| `lesson_order` | `source`, `teaching` | follow the material's order, or reorder for explanation |
| `lesson_ask` | `when-unclear`, `always`, `never` | when to stop and ask |
| `lesson_checks` | `normal`, `off`, `many` | `check`/`recall` slides every 4–6 slides, never, or every 2–3 |
| `lesson_visuals` | `balanced`, `minimal`, `rich` | a visual where the source has one, text only, or one per mechanism |
| `lesson_notes` | `short`, `off`, `full` | speaker notes per slide |
| `lesson_language` | `source`, or a language | language of the lesson text |

Where a setting can come from, most specific first:

1. **The request, for this run only.** A depth word (`brief`, `medium`, `deep`) or `key=value` after the
   topic: `/als-lesson backpropagation deep`, "explain X, depth=brief checks=many". Phrases count too:
   "make it deeper", "only the key points", "you may add background", "more quizzes". Apply it to this
   lesson and do not save it unless asked.
2. **One module:** `lesson_*` lines in the front matter of `modules/<id>/module.md`.
3. **Everything:** `lesson_*` lines in the front matter of `profile.md`, e.g. `lesson_depth: deep`.
4. **Default:** `medium` depth, strict grounding.

The student can edit those `.md` files by hand; `ALS settings` writes the same lines.

**Settings mode** (`/als-settings`, "set my lesson depth to deep", "what are my lesson settings?"): run
`ALS settings [key=value …] [--module <id>]`, report what now applies in a short list, and stop. Build
nothing. Accept loose wording (`depth deep`, "deeper", "shorter", `standard` for `medium`) and turn it
into `key=value`. "For this course" means `--module <id>`; otherwise save to the profile.

Depth recipes are in `references/lesson-design.md`.

## Workflow

1. **Settings and scope.** `ALS settings --module <id>`. One lesson is one idea (10–20 minutes). A whole
   chapter becomes several lessons: list them with their pages and start with the first.
2. **Get the text cheaply.** `ALS extract <pdf> --module <id> --toc` writes page-numbered text and reports
   pages without text and build-up slides it merged. Read the `.txt`, not the PDF. For pages without
   text, `ALS extract <pdf> --pages <n> --images thin` and look at the PNG. If the text already exists in
   `modules/<id>/sources/text/`, use it.
3. **Clarify** open points (section above) before writing a single slide.
4. **Scaffold.** `ALS new lesson modules/<id>/data/lesson-<topic>.json --title "…" --module <id>
   --subject "…" --source "L3=sources/L03.pdf" --outline "title,points,definition,formula,steps,plot,check,summary"`.
   The file carries the resolved `grounding` and `depth`; every `src` is empty and must be filled.
5. **Write the slides** by replacing the skeleton content. Pick the layout from the table in
   `references/lesson-design.md` and the visual from `references/components.md`. Define repeated LaTeX
   once in `macros`.
6. **Build.** `ALS build modules/<id>/data/lesson-<topic>.json` (a folder or `lesson-*.json` builds many).
   Fix every error; in strict mode a missing `src` or a `grounded: false` is an error. Read the warnings.
7. **Self-check against the source**, slide by slide: is each statement on the cited page, in the
   lecturer's notation, with nothing added? Remove what fails, or ask.
8. **Hand over** the output path; the controls (→ / Space next, ← back, D depth, E more detail,
   N notes, O overview, P autoplay, F full screen); **source coverage** (pages used, pages skipped and
   why); and **left out or unclear**. PDF handout: `ALS pdf <out.html> --query print=1`.

## Choosing the picture

Use a component before drawing anything by hand; a component costs a few dozen tokens, hand-written
SVG costs hundreds and is easier to get wrong.

| The source shows or states | Use |
|---|---|
| a function, a curve, data points, a decision boundary | `plot` |
| a pipeline, architecture, algorithm stages, cause and effect | `flow` |
| a matrix, array, image patch, sliding window, DP table | `grid` |
| a layered network of units | `layers` |
| a hierarchy, parse tree, recursion, taxonomy | `tree` |
| a few numbers to compare | `bars` |
| a figure that cannot be redrawn faithfully (photo, dense plot, screenshot) | `figure` with the page image and spotlight marks |
| anything else | `diagram` with hand-written SVG (cookbook in `references/components.md`) |

In strict mode a visual shows only what the source shows or states: plot the formula from the slide,
not a nicer one; redraw the architecture with the lecturer's labels; use their numbers.

## Quality bar

- One idea per slide; at most 6 points; points are short claims, not paragraphs.
- Reveal order follows reasoning order. Do not reveal a conclusion before its premises.
- An abstract statement is followed within two slides by the source's own example, if it has one.
- Slides hold what the student should remember; `notes` hold what a lecturer would say; `more` holds
  the fuller explanation for those who want it.
- Checks test understanding of the cited page, with distractors taken from confusions the source
  itself addresses.
- Depth is tagged, not duplicated: one file serves brief, medium and deep readers.
