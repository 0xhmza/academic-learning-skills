# Lesson design reference

## File envelope

```json
{ "als": "1", "kind": "lesson", "title": "…", "subtitle": "…", "module": "<id>", "subject": "…",
  "grounding": "strict", "depth": "medium", "explain": "full", "lang": "en",
  "sources": [{ "id": "L3", "title": "Lecture 3", "file": "sources/L03.pdf" }],
  "macros": { "\\enc": "\\mathrm{enc}" },
  "slides": [ … ] }
```

- `grounding: "strict"` turns on the build checks: `sources` listed, `src` on every slide except
  `title`, `section` and `summary`, no `grounded: false`.
- `depth` is the depth the page opens at (`brief`, `medium`, `deep`; `standard` is an older name for `medium`).
- `explain` (`full`, `short`, `off`) is the `lesson_explain` setting; it sets how strict the thin-slide check is.
- `macros` are LaTeX shorthands usable in every maths string of the file. Define anything written more
  than twice.
- `lang` sets the interface language (`en`, `de`, `ar`) and, for Arabic, Hebrew, Persian or Urdu, a
  right-to-left page. `"view": "present"` opens the page in the compact view.
- Maths: `$inline$`, `$$display$$`; in JSON every backslash is doubled (`"$\\frac{a}{b}$"`). Text
  fields accept `**bold**`, `*italic*`, `` `code` ``, links and `- lists`.

## What every slide can carry

| Field | Where it shows | Write |
|---|---|---|
| `title` | heading | a statement or question, not a label: "Eigenvectors keep their direction", not "Eigenvectors" |
| `lead` | under the title | 1–2 sentences: what this slide is about and how it follows from the last |
| `explain` | beside the main element (below it on small screens) | what the lecturer would say: meaning, reason, connection, how to read the picture. Paragraphs allowed |
| `intuition` | labelled box "tutor's own" | your analogy or everyday example; only with `lesson_intuition: labelled` |
| `takeaway` | highlighted line at the bottom | the one sentence to remember |
| `more` | on demand (key E) | the long form for the curious: a second example from the source, the special case |
| `notes` | on demand (key N) | per `lesson_notes`; not a place for the explanation |
| `src`, `level` | source badge, depth tag | see below |

On a `code` slide `explain` is the list of per-step comments, so the overall explanation goes in `about`.
On a `check` slide `explain` is the feedback shown after answering.

## Layouts

| Layout | Fields | One → press reveals | Use for |
|---|---|---|---|
| `title` | `title`, `subtitle`, `kicker` | – | opening |
| `objectives` | `points[]` | an objective | "After this lesson you can…", 2–4 items from the source's headings |
| `section` | `title`, `lead`, `number` | – | start of a part in lessons over 10 slides |
| `points` | `points[]`: strings or `{text, detail}` | a point with its detail | motivation, properties, claims |
| `text` | `body` (paragraphs) | – | material that argues in prose; a passage explained |
| `definition` | `term`, `definition`, `example`, `kind` ("Theorem") | the example | key terms, theorems |
| `formula` | `formula`, `parts[]` of `{sym, means}`, `note` | a part | a central formula, symbol by symbol |
| `steps` | `steps[]` of `{text, math, why, level}`, optional `given`, `result` | a row (earlier rows dim) | derivations, proofs, worked examples, arguments |
| `table` | `columns[]`, `rows[][]`, `reveal: "all"` | a row | comparisons along several attributes |
| `compare` | `columns[]` of `{heading, text, points[]}` | a column | two or three confusable concepts |
| `timeline` | `events[]` of `{when, what, detail}` | an event | history, development of an idea |
| `code` | `lang`, `code`, `highlight[][]` (line numbers), `explain[]`, `about` | a highlight group | algorithms, programs |
| `quote` | `quote`, `by`, `comment` | – | wording that matters (theorem statements, primary texts) |
| `pitfall` | `wrong`, `why`, `right` | mistake, reason, correction | a misconception the source warns about |
| `recall` | `question`, `answer` | the answer | free recall, self-explanation ("why does…?") |
| `check` | `question`, `options[]`, `answer` (index), `explain` | the answer | multiple-choice retrieval |
| `summary` | `points[]` | a point | closing takeaways |
| `plot`, `flow`, `grid`, `layers`, `tree`, `bars`, `figure`, `diagram` | see `components.md` | a group of elements | visuals |

The reader can switch off the step-by-step build (key A) and see each slide whole.

## Writing the explanation

The explanation is where the teaching happens. Per content slide, counting `lead`, `explain`,
`detail`, `why`, captions and `takeaway` together:

| `lesson_depth` | Aim for | Build warns below |
|---|---|---|
| `brief` | 30–60 words | 12 |
| `medium` | 60–120 words | 35 |
| `deep` | 100–180 words | 55 |

`lesson_explain: short` halves these; `off` switches the check off (classic slides, by request only).
`title`, `section`, `objectives`, `quote`, `pitfall`, `check`, `recall` and `summary` slides are exempt.

What a good explanation does, in this order of usefulness:

1. **Says what it means** in plain words, before or after the formal statement.
2. **Gives the reason**: why it is true, why this step is allowed, why the definition has this condition.
3. **Connects**: to the previous slide, to the source's example, to what comes next.
4. **Tells how to read** a formula ("the fraction compares…") or a figure ("follow the blue curve from the left…").
5. **Names the trap** the source warns about.

It does not restate the bullets, praise the topic, or announce ("Now we will look at…").

Before (a professor's slide, copied):

```json
{ "layout": "points", "title": "Eigenvalues", "points": ["Av = λv", "v ≠ 0", "det(A − λI) = 0"], "src": "L7 s.5" }
```

After (a lesson slide; content from the same page):

```json
{ "layout": "points", "title": "An eigenvector keeps its direction under $A$",
  "lead": "Most vectors are turned when you multiply them by a matrix. The few that are not turn out to describe the matrix completely.",
  "points": [
    { "text": "$A\\mathbf v = \\lambda\\mathbf v$", "detail": "Multiplying by $A$ gives back the same vector, only scaled by the number $\\lambda$. $\\mathbf v$ is the eigenvector, $\\lambda$ its eigenvalue." },
    { "text": "$\\mathbf v \\neq \\mathbf 0$", "detail": "The zero vector is excluded because it satisfies the equation for every $\\lambda$ and so says nothing about $A$." },
    { "text": "$\\det(A - \\lambda I) = 0$", "detail": "Rewrite the first line as $(A - \\lambda I)\\mathbf v = \\mathbf 0$. A non-zero solution exists only if that matrix is singular, which is what a zero determinant means." }
  ],
  "explain": "Read the three lines as one chain. The first is the definition. The second rules out the trivial case. The third is how you find $\\lambda$ in practice: you never guess eigenvectors, you solve the determinant equation for $\\lambda$ first and get $\\mathbf v$ afterwards.",
  "takeaway": "Eigenvalues come from $\\det(A - \\lambda I) = 0$; eigenvectors from $(A - \\lambda I)\\mathbf v = \\mathbf 0$.",
  "src": "L7 s.5" }
```

Nothing in the second version is new content: each sentence unpacks a line of the page.

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

Depth changes how much of the material is covered and how finely it is stepped. It never lowers the
rule that each shown slide is explained. In strict mode deeper never means outside knowledge. If the
source itself is brief, the deep lesson is short: say so rather than padding.

Other settings in practice:

- `lesson_checks`: `normal` = a `check` or `recall` every 4–6 slides and one before the summary;
  `many` = every 2–3 slides, mixing both kinds; `off` = none.
- `lesson_visuals`: `minimal` = no visual slides except figures the lesson cannot do without;
  `balanced` = a visual wherever the source has a figure, plot or diagram; `rich` = also visualise each
  mechanism the source describes in words (still only what it describes).
- `lesson_notes`: `short` = one or two sentences on slides that need them; `full` = extra remarks for
  every slide; `off` = none.
- `lesson_order`: `source` = slide order follows the pages; `teaching` = reorder (for example concrete
  case before the general statement) and keep every `src`.

## Lesson arc

For a `first-time` audience (`lesson_audience`, the default) every lesson runs through five phases.
Each one is built from the material, so the arc holds in strict mode:

| Phase | Slides | Rule |
|---|---|---|
| Orient | `title`, then `objectives` | 2–4 things the reader can do afterwards, in "you can…" form, taken from the source's own headings |
| Activate | a `recall` or `check` on what this topic builds on, or a prediction question about the result to come | asking before teaching improves what is learned afterwards, even when the first answer is wrong; only ask what the material answers |
| Build | the body | one idea per slide; terms defined before the mechanism that uses them; the source's concrete case before its general rule; explanation beside every element |
| Check | `check`/`recall` | per `lesson_checks`; ask about earlier slides, not the one just shown; prefer "why" and "what happens if" over "what is" |
| Integrate | `summary` | what to remember, tied back to the objectives, and what the material does next |

Lessons over 10 slides get `section` slides so the outline shows the parts.

`revision` audience: skip Orient and Activate, compress Build into `formula`, `table` and `compare`
slides with short explanations (`lesson_explain: short` fits), and raise the share of `check`/`recall`.

## Explaining techniques

Each technique is a way of presenting source content, so all are allowed in strict mode as long as the
content itself is from the material. The names in brackets are the findings behind them
(`shared/references/learning-science.md`, path from here: `../../../shared/references/learning-science.md`).

| Technique | How | When |
|---|---|---|
| Segment (segmenting) | one idea per slide, one claim per → press | always |
| Signal (signalling) | titles that state the point, `section` slides, `takeaway`, `!id` highlights | always |
| Terms first (pre-training) | `definition` slides before the derivation that uses the terms | new vocabulary |
| Words next to the picture (spatial contiguity) | `explain` on every visual; captions per step; labels on the parts, not in a legend | every visual |
| Talk to the reader (personalisation) | "you", "we", present tense; no passive textbook voice | all explanation text |
| Concrete first (concreteness fading) | the source's example (`steps` with `given`/`result`, or a `grid`/`plot` of it) before the general rule | source has an example |
| Build the picture | reveal a visual in the order one would draw it: frame, object, annotation, conclusion | every visual |
| Name the parts | `formula` slide: the whole formula, then each symbol with its meaning | any formula with 3+ symbols |
| Justify each step (worked example) | `why` on every derivation row: the rule used and why it applies here | derivations |
| Fade the steps (fading) | first worked example fully stepped; in the next one tag routine rows `deep` | two similar examples |
| Contrast | `compare` or `table` for concepts the source sets against each other | confusable pairs |
| Spotlight the original | `figure` with `marks` on the lecturer's own picture | figures that carry meaning in their details |
| Predict, then reveal (pretesting) | `recall` or `check` placed before the result is shown | before a key result |
| Explain it yourself (self-explanation) | `recall` asking "why does this step work?" or "what would change if…?" | after a derivation or example |
| Retrieve (testing effect) | `check`/`recall` on earlier slides, not the one just shown | per `lesson_checks` |
| Name the trap | `pitfall` when the source flags a common error | source mentions one |
| Cut the decoration (coherence) | no filler slides, jokes, stock motivation or pictures that carry no content | always |

## Subject patterns

- **Maths/physics:** objectives → definition → picture (`plot`/`diagram`) → `formula` parts → derivation
  (`steps` with `why`) → worked example (`steps` with `given`/`result`) → special cases (`compare`) → check.
- **CS/ML:** problem → idea (`points` with details) → architecture or pipeline (`flow`, `layers`) → trace
  on the source's example (`grid` with `!` highlights, one step per operation) → `code` with line focus
  and `about` → cost or properties (`table`) → check.
- **Biology/medicine:** structure (`figure` with marks, or `diagram`) → process (`flow`/`timeline`) →
  regulation and failure (`compare`: normal vs pathology) → check.
- **Philosophy:** question → the text (`quote`) → the passage explained (`text`) → argument as premises
  and conclusion (`steps` without `math`) → objection and reply (`compare`) → check.
- **Literature/history:** context (`timeline` with details) → passage (`quote` with `comment`) → reading
  of it (`text`) → themes (`points`) → interpretations (`compare`) → check.
- **Economics/law:** case or model (`definition`) → mechanism (`plot` of the curves, `flow` or `tree`
  for a decision) → application (`steps`) → check.

## Token economy

- Scaffold with `--outline`; do not copy the starter or write boilerplate by hand.
- Read extracted text (`ALS extract`), never whole PDFs, and only the pages of the topic.
- Spend tokens on explanation, save them on drawing: components before hand-written SVG, auto steps
  before listing ids (omit `steps` when the default order is right).
- `macros` for repeated LaTeX; string shorthands for `flow` nodes and edges and `tree` nodes.
- One lesson file with `level` tags instead of separate brief and deep versions.
- Build many files in one call: `ALS build modules/<id>/data` or `ALS build "modules/<id>/data/lesson-*.json"`.
