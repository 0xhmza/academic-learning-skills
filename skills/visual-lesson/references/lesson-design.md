# Lesson design reference

## File envelope

```json
{ "als": "1", "kind": "lesson", "title": "…", "subtitle": "…", "module": "<id>", "subject": "…",
  "grounding": "strict", "depth": "medium", "lang": "en",
  "sources": [{ "id": "L3", "title": "Lecture 3", "file": "sources/L03.pdf" }],
  "macros": { "\\enc": "\\mathrm{enc}" },
  "slides": [ … ] }
```

- `grounding: "strict"` turns on the build checks: `sources` listed, `src` on every slide except
  `title` and `summary`, no `grounded: false`.
- `depth` is the depth the page opens at (`brief`, `medium`, `deep`; `standard` is an older name for `medium`).
- `macros` are LaTeX shorthands usable in every maths string of the file. Define anything written more
  than twice.
- `lang` switches the built-in labels (`en`, `de`).
- Maths: `$inline$`, and in JSON every backslash is doubled (`"$\\frac{a}{b}$"`). Text fields accept
  `**bold**`, `*italic*`, `` `code` ``.

## Layouts

Every slide accepts `title`, `src`, `notes` (key N), `more` (fuller explanation, key E) and `level`.

| Layout | Fields | One → press reveals | Use for |
|---|---|---|---|
| `title` | `title`, `subtitle`, `kicker` | – | opening |
| `points` | `points[]` | a point | motivation, properties, claims |
| `definition` | `term`, `definition`, `example`, `kind` ("Theorem") | the example | key terms, theorems |
| `formula` | `formula`, `parts[]` of `{sym, means}`, `note` | a part | a central formula, symbol by symbol |
| `steps` | `steps[]` of `{text, math, why, level}`, optional `given`, `result` | a row (earlier rows dim) | derivations, proofs, worked examples, arguments |
| `table` | `columns[]`, `rows[][]`, `reveal: "all"` | a row | comparisons along several attributes |
| `compare` | `columns[]` of `{heading, points[]}` | a column | two or three confusable concepts |
| `timeline` | `events[]` of `{when, what}` | an event | history, development of an idea |
| `code` | `lang`, `code`, `highlight[][]` (line numbers), `explain[]` | a highlight group | algorithms, programs |
| `quote` | `quote`, `by`, `comment` | – | wording that matters (theorem statements, primary texts) |
| `pitfall` | `wrong`, `why`, `right` | mistake, reason, correction | a misconception the source warns about |
| `recall` | `question`, `answer` | the answer | free recall without options |
| `check` | `question`, `options[]`, `answer` (index), `explain` | the answer | multiple-choice retrieval |
| `summary` | `points[]` | a point | closing takeaways |
| `plot`, `flow`, `grid`, `layers`, `tree`, `bars`, `figure`, `diagram` | see `components.md` | a group of elements | visuals |

## Depth

Untagged slides are **core** and always shown. `"level": "medium"` marks material hidden in the brief
view; `"level": "deep"` marks material shown only in the deep view. Rows of a `steps` slide take
`level` too. The page gets a depth switch (key D) whenever tags exist, so one file serves every reader.
Write up to the configured `lesson_depth` and tag as you go:

| `lesson_depth` | Write | Typical size |
|---|---|---|
| `brief` | core only: what it is, why it matters, the main definition, the main formula or result, one visual, summary | 6–10 slides |
| `medium` | core, plus `medium`-tagged mechanism: main derivation steps, the source's examples, comparisons, checks | 10–18 slides |
| `deep` | all of the above, plus `deep`-tagged: every intermediate step, each symbol named (`formula` parts), conditions and special cases the source states, pitfalls it mentions, `more` on dense slides, extra `recall` | 16–30 slides, or two lessons |

In strict mode deeper never means outside knowledge. It means covering more of what the material says
and unpacking what it states compactly. If the source itself is brief, the deep lesson is short: say so
rather than padding.

Other settings in practice:

- `lesson_checks`: `normal` = a `check` or `recall` every 4–6 slides and one before the summary;
  `many` = every 2–3 slides, mixing both kinds; `off` = none.
- `lesson_visuals`: `minimal` = no visual slides except figures the lesson cannot do without;
  `balanced` = a visual wherever the source has a figure, plot or diagram; `rich` = also visualise each
  mechanism the source describes in words (still only what it describes).
- `lesson_notes`: `short` = one or two sentences on slides that need them; `full` = the spoken
  explanation for every slide; `off` = none.
- `lesson_order`: `source` = slide order follows the pages; `teaching` = reorder (for example concrete
  case before the general statement) and keep every `src`.

## Lesson arc

For a `first-time` audience (`lesson_audience`, the default) every lesson runs through five phases.
Each one is built from the material, so the arc holds in strict mode:

| Phase | Slides | Rule |
|---|---|---|
| Orient | `title`, then one `points` slide "What this lesson covers" | at most 4 items, taken from the source's own headings |
| Activate | a `recall` on what this topic builds on | only if an earlier part of the material covers it (cite that part); the source's own motivating example or question goes here too |
| Build | the body | one idea per slide; the source's concrete case before its general rule; every term explained on first use with the source's definition |
| Check | `check`/`recall` | per `lesson_checks`; ask about earlier slides, not the one just shown |
| Integrate | `summary` | what to remember, and what the material does next |

Hooks, analogies and real-world stories that are not in the material belong to `extended` grounding
only, marked `grounded: false`. In strict mode, do not invent an anchor; start from the source's own.

`revision` audience: skip Orient and Activate, compress Build into `formula`, `table` and `compare`
slides, and raise the share of `check`/`recall`.

Text density: a point is a claim of about 12 words or fewer. These lessons are read without a
presenter, so the explanation still has to be on the page: put it in captions (visuals), `why`
(derivations), `more` (on demand) and `notes`, not in longer bullets.

## Explaining techniques

Each technique is a way of presenting source content, so all are allowed in strict mode as long as the
content itself is from the material.

| Technique | How | When |
|---|---|---|
| Segment | one idea per slide, one claim per → press | always |
| Signal | start a section with a `points` slide that names what comes; end with `summary` | lessons over 8 slides |
| Concrete first | show the source's example (`steps` with `given`/`result`, or a `grid`/`plot` of it) before the general rule | source has an example |
| Build the picture | reveal a visual in the order one would draw it: frame, object, annotation, conclusion; one caption per step | every visual |
| Name the parts | `formula` slide: the whole formula, then each symbol with its meaning | any formula with 3+ symbols |
| Justify each step | `why` on derivation rows ("chain rule", "by definition of …") | derivations |
| Fade the steps | first worked example fully stepped; in the next one tag routine rows `deep` | two similar examples |
| Contrast | `compare` or `table` for concepts the source sets against each other | confusable pairs |
| Emphasise, do not redraw | `!id` in a step lights an element for that step; `-id` removes it | walking through a `grid`, `flow` or figure |
| Spotlight the original | `figure` with `marks` on the lecturer's own picture | figures that carry meaning in their details |
| Predict, then reveal | `recall` or `check` placed before the result is shown | before a key result |
| Retrieve | `check`/`recall` on earlier slides, not the one just shown | per `lesson_checks` |
| Name the trap | `pitfall` when the source flags a common error | source mentions one |
| Layer the detail | keep the slide short; put the long form in `more`, the spoken form in `notes` | dense pages |

## Subject patterns

- **Maths/physics:** definition → picture (`plot`/`diagram`) → `formula` parts → derivation (`steps`
  with `why`) → worked example (`steps` with `given`/`result`) → special cases (`compare`) → check.
- **CS/ML:** problem → idea (`points`) → architecture or pipeline (`flow`, `layers`) → trace on the
  source's example (`grid` with `!` highlights, one step per operation) → `code` with line focus →
  cost or properties (`table`) → check.
- **Biology/medicine:** structure (`figure` with marks, or `diagram`) → process (`flow`/`timeline`) →
  regulation and failure (`compare`: normal vs pathology) → check.
- **Philosophy:** question → the text (`quote`) → argument as premises and conclusion (`steps` without
  `math`) → objection and reply (`compare`) → check.
- **Literature/history:** context (`timeline`) → passage (`quote` with `comment`) → themes (`points`) →
  interpretations (`compare`) → check.
- **Economics/law:** case or model (`definition`) → mechanism (`plot` of the curves, `flow` or `tree`
  for a decision) → application (`steps`) → check.

## Token economy

- Scaffold with `--outline`; do not copy the starter or write boilerplate by hand.
- Read extracted text (`ALS extract`), never whole PDFs, and only the pages of the topic.
- Components before hand-written SVG. Auto steps before listing ids: omit `steps` when the default
  order is right.
- `macros` for repeated LaTeX; string shorthands for `flow` nodes and edges and `tree` nodes.
- One lesson file with `level` tags instead of separate brief and deep versions.
- Build many files in one call: `ALS build modules/<id>/data` or `ALS build "modules/<id>/data/lesson-*.json"`.
