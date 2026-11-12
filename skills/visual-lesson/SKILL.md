---
name: visual-lesson
description: Build an animated, step-by-step HTML lesson from the student's own script or slides, with the explanation written on the page so it can be studied without the lecturer. Use when a student wants a topic explained "visually", "step by step", "animated", "as a presentation", "slides", "walk me through the derivation", "show me how the algorithm works", wants lessons made from lecture slides or a script, or wants to change how lessons are written ("more detail", "shorter", "more text", "in Arabic"). Produces a themed, self-contained HTML lesson from a small JSON file using a reusable template with an explanation beside every slide, progressive reveal, ready-made plots, flow charts, grids and trees, the lecturer's own figures with spotlights, derivations line by line, formulas symbol by symbol, code with line focus, quick checks, depth switch, study and present views, outline sidebar, status bar, right-to-left languages, PDF print. Strict source grounding by default; asks the student instead of guessing.
---

# Visual lesson

A lesson is a JSON list of slides rendered by `shared/templates/lesson.html`. Claude writes only the
JSON; the template does the animation, the drawing, theming and navigation.

**Toolkit.** `ALS` = `python "<this skill's base directory>/../../shared/scripts/als.py"`.
Read once per session, before the first lesson: `references/lesson-design.md` (layouts, how to write
the explanation, depth) and `references/components.md` (visual components). Do not read the template,
the schema or the starter; `ALS new lesson --outline …` writes a skeleton of exactly the layouts asked for.

## The lesson replaces the lecture

The student reads the page alone. A lecturer's slide deck is half a lecture: keywords on screen, the
explanation spoken. A lesson that copies the deck is empty. So every content slide carries, in full
sentences and on the page:

- **`lead`**: one or two sentences under the title that say what this slide is about and how it follows
  from the last one;
- **the main element** (points, formula, derivation, visual, table…);
- **`explain`**: what the lecturer would say while this slide is up: what it means, why it holds, how to
  read the picture, how it connects. This is the body of the teaching, not an extra;
- on `points`, a **`detail`** per point (the sentence or two that turns a keyword into a statement);
  on `steps`, a **`why`** per row; on visuals, a caption per step;
- optionally a **`takeaway`**: the one sentence to remember.

The build warns about **thin slides** (too little explanation for the chosen depth). Treat that warning
as a failed build: fix the slides, do not hand the lesson over with it. Budgets and a worked
before/after are in `references/lesson-design.md`.

The page has two views. **Study** (default) shows all of the above. **Present** (key V) hides the
explanations for the classic compact look. Write for Study.

## The source contract

The student's script or slides decide **what** is taught. You supply **how** it is explained. By
default (`lesson_grounding: strict`):

1. **Content only from the material.** Every definition, claim, formula, number, example, name and
   figure comes from the given material. No outside facts, results, examples or "standard background".
2. **Every slide cites it.** `src` names the source id and the page or slide (`"L3 s.12"`,
   `"Script p.44"`). Only `title`, `section` and `summary` slides may go without. The build fails otherwise.
3. **The lecturer's notation, terms, order and language.** Keep their symbols and names. Keep their
   order unless `lesson_order: teaching`.
4. **Explaining is your job, and it is not "adding".** In `lead`, `explain`, `detail`, `why` and
   captions you say in your own words what the cited page states: what a definition means and why
   each condition is there, why a step follows from the one before, how to read a figure, how two
   statements on the page connect, what would go wrong otherwise. You may rely on what the course
   presupposes (school mathematics, the meaning of an ordinary word). You may not bring in a fact,
   theorem, number or example the material does not contain; if the explanation needs one, the
   material is unclear at that point: ask.
5. **Your own analogies and examples go in `intuition`, nowhere else.** The page shows that block with
   the label "tutor's own". Use it sparingly, where an everyday picture really helps, and only while
   `lesson_intuition` is `labelled` (the default). With `off`, write none.
6. **Presentation is free:** splitting a slide into steps, plotting the formula on the page, redrawing a
   figure the source shows, naming the parts of a formula the source defines, questions whose answers
   are in the material, the mechanical algebra between two lines the source gives (cite the same page).
7. **Nothing is silently dropped or bent.** If a page is skipped, say so in the hand-over.
8. **Unclear means ask** (next section). Never fill a gap from general knowledge.

`extended` grounding lifts rule 1: added content is allowed anywhere when it is marked
`"grounded": false` (the page shows "beyond your notes"). Use it only when the student chose it, in
settings or in words. `shared/references/grounding.md` (path from here:
`../../shared/references/grounding.md`) has the citation format.

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
| `lesson_explain` | `full`, `short`, `off` | explanation on the page: what a lecturer would say on every content slide, a sentence or two, or keywords only |
| `lesson_intuition` | `labelled`, `off` | whether you may add your own analogies in `intuition` blocks (always labelled) |
| `lesson_audience` | `first-time`, `revision` | first contact (orient, concrete first, every term explained) or compact revision |
| `lesson_grounding` | `strict`, `extended` | the source contract above |
| `lesson_order` | `source`, `teaching` | follow the material's order, or reorder for explanation |
| `lesson_ask` | `when-unclear`, `always`, `never` | when to stop and ask |
| `lesson_checks` | `normal`, `off`, `many` | `check`/`recall` slides every 4–6 slides, never, or every 2–3 |
| `lesson_visuals` | `balanced`, `minimal`, `rich` | a visual where the source has one, text only, or one per mechanism |
| `lesson_view` | `study`, `present` | the view the page opens in |
| `lesson_notes` | `short`, `off`, `full` | extra speaker notes per slide (key N) |
| `lesson_language` | `source`, or a language | language of the lesson text |

Where a setting can come from, most specific first:

1. **The request, for this run only.** A depth word (`brief`, `medium`, `deep`) or `key=value` after the
   topic: `/als-lesson backpropagation deep`, "explain X, depth=brief checks=many". Phrases count too:
   "make it deeper", "only the key points", "more text", "less text", "no analogies", "you may add
   background", "more quizzes". Apply it to this lesson and do not save it unless asked.
2. **One module:** `lesson_*` lines in the front matter of `modules/<id>/module.md`.
3. **Everything:** `lesson_*` lines in the front matter of `profile.md`, e.g. `lesson_depth: deep`.
4. **Default:** `medium` depth, `full` explanation, strict grounding.

The student can edit those `.md` files by hand; `ALS settings` writes the same lines.

**Settings mode** (`/als-settings`, "set my lesson depth to deep", "what are my lesson settings?"): run
`ALS settings [key=value …] [--module <id>]`, report what now applies in a short list, and stop. Build
nothing. Accept loose wording (`depth deep`, "deeper", "shorter", `standard` for `medium`) and turn it
into `key=value`. "For this course" means `--module <id>`; otherwise save to the profile.

## Workflow

1. **Settings and scope.** `ALS settings --module <id>`. One lesson is one idea (10–20 minutes). A whole
   chapter becomes several lessons: list them with their pages and start with the first.
2. **Get the text cheaply.** `ALS extract <pdf> --module <id> --toc` writes page-numbered text and reports
   pages without text and build-up slides it merged. Read the `.txt`, not the PDF. For pages without
   text, `ALS extract <pdf> --pages <n> --images thin` and look at the PNG. If the text already exists in
   `modules/<id>/sources/text/`, use it.
3. **Clarify** open points (section above) before writing a single slide.
4. **Scaffold.** `ALS new lesson modules/<id>/data/lesson-<topic>.json --title "…" --module <id>
   --subject "…" --source "L3=sources/L03.pdf" --outline "title,objectives,points,definition,formula,steps,plot,check,summary"`.
   The file carries the resolved `grounding`, `depth` and `explain`; every `src` is empty and must be
   filled. Add `--lang ar` (or `de`, …) when the lesson is not in English.
5. **Write the slides** by replacing the skeleton content: for each one the main element first, then
   its `lead` and `explain`. Pick the layout from the table in `references/lesson-design.md` and the
   visual from `references/components.md`. Define repeated LaTeX once in `macros`.
6. **Build.** `ALS build modules/<id>/data/lesson-<topic>.json` (a folder or `lesson-*.json` builds many).
   Fix every error, then every warning about **thin slides** and **maths** (LaTeX outside `$…$`,
   unpaired `$`). Rebuild until those are gone.
7. **Self-check against the source**, slide by slide: is each statement on the cited page, in the
   lecturer's notation? Does each explanation only unpack that page? Remove what fails, or ask.
8. **Hand over** the output path; the controls (→ / Space next, ← back, V study or present view, A
   everything at once, D depth, E more detail, T outline, Z focus mode, O overview, F full screen);
   **source coverage** (pages used, pages skipped and why); and **left out or unclear**.
   PDF handout: `ALS pdf <out.html> --query print=1`.

## Maths and symbols

- Every mathematical expression is LaTeX inside `$…$` (or `$$…$$` on its own line), in every field:
  titles, points, captions, explanations, table cells, answer options. That includes single symbols
  ($x$, $\lambda$) and numbers that belong to an expression ($n = 3$, $0.5$).
- In JSON every backslash is doubled: `"$\\frac{a}{b}$"`. Fields named `math`, `formula` and `sym`
  hold bare LaTeX, without `$`.
- Do not type Unicode maths (σ, x₁, ², ≤, →) in text. The page converts obvious cases so nothing shows
  in the wrong font, but LaTeX is exact and the conversion is a safety net, not a style.
- Labels inside visual components accept `$…$` too (`"label": "$\\sigma(z)$"`); plain numbers there
  are set in the maths font automatically.

## Languages and right-to-left

Set `"lang"` to the lesson's language (`lesson_language`). The built-in interface text exists in
English, German and Arabic. Arabic, Hebrew, Persian and Urdu pages are laid out right-to-left
automatically: text, lists, the outline and navigation mirror, while maths, code and diagrams stay
left-to-right. Write Arabic lessons in Arabic, keep formulas in LaTeX, and give technical terms the way
the course does (often the Latin-script term in brackets after the Arabic one).

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
not a nicer one; redraw the architecture with the lecturer's labels; use their numbers. Every visual
gets an `explain` that tells the reader how to read it; the picture alone teaches little.

## Quality bar

- A student who missed the lecture understands each slide from the page alone.
- One idea per slide. The main element stays compact (at most 6 points, short claims); the sentences
  live in `lead`, `detail`, `why`, captions and `explain`.
- Explanations explain: they give the reason, the meaning or the connection. Restating the bullet in
  other words does not count.
- Reveal order follows reasoning order. Do not reveal a conclusion before its premises.
- An abstract statement is followed within two slides by the source's own example, if it has one.
- Write to the reader: "you", present tense, plain words, the course's terms.
- Checks test understanding of the cited page, with distractors taken from confusions the source
  itself addresses.
- Depth is tagged, not duplicated: one file serves brief, medium and deep readers.
- No thin-slide or maths warnings in the final build.
