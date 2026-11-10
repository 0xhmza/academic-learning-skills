# Lesson design reference

## Layouts and how they animate

| Layout | Fields | Steps (one per → press) | Best for |
|---|---|---|---|
| `title` | `title`, `subtitle`, `kicker` | 1 | opening |
| `points` | `title`, `points[]` | one per point | motivation, properties, claims |
| `definition` | `term`, `definition`, `example`, `kind` (e.g. "Theorem") | definition, then example | key terms, theorems |
| `steps` | `title`, `steps[]` of `{text, math}` | one per row; current row highlighted, earlier rows dimmed | derivations, proofs, calculations, argument reconstruction |
| `diagram` | `title`, `svg`, `steps[][]` of element ids, `captions[]` | one per group of ids | geometry, circuits, cells, processes, graphs, argument maps |
| `code` | `title`, `lang`, `code`, `highlight[][]` line numbers, `explain[]` | one per highlight group | algorithms, programs, SQL |
| `compare` | `title`, `columns[]` of `{heading, points[]}` | one per column | confusable concepts, schools of thought |
| `timeline` | `title`, `events[]` of `{when, what}` | one per event | history, literature, development of a theory |
| `quote` | `quote`, `by`, `comment` | 1 | primary texts in philosophy and literature |
| `check` | `question`, `options[]`, `answer`, `explain` | answer revealed on click or → | retrieval every 4–6 slides |
| `summary` | `title`, `points[]` | one per point | closing takeaways |

All slides accept `notes` (speaker notes, key N), `src` and `grounded`.

## Subject patterns

- **Maths/physics:** definition → geometric picture (`diagram`) → derivation (`steps`) → worked example
  (`steps`) → special cases (`compare`) → check.
- **CS:** problem → idea (`points`) → trace on an example (`diagram` of the data structure, step per
  operation) → code with line focus → complexity (`steps`) → check.
- **Biology/medicine:** structure (`diagram` with labels building up) → process (`diagram` or
  `timeline`) → regulation/failure (`compare`: normal vs pathology) → check.
- **Philosophy:** question → the text (`quote`) → argument reconstructed as premises and conclusion
  (`steps` without `math`) → objection and reply (`compare`) → check.
- **Literature/history:** context (`timeline`) → passage (`quote` with `comment`) → themes (`points`) →
  interpretations (`compare`) → check.
- **Economics/law:** case or model (`definition`) → mechanism (`diagram` of curves or a decision tree) →
  application to a case (`steps`) → check.

## SVG cookbook

```xml
<svg viewBox="0 0 600 300" xmlns="http://www.w3.org/2000/svg">
  <g id="axes"><line class="d-line" x1="50" y1="260" x2="570" y2="260"/><line class="d-line" x1="50" y1="260" x2="50" y2="30"/>
    <text class="d-text-muted" x="560" y="280">x</text></g>
  <path id="f" class="d-accent" stroke-width="3" d="M50 240 C 200 240, 300 60, 560 50"/>
  <g id="tangent"><line class="d-accent2" stroke-dasharray="6 4" x1="180" y1="250" x2="420" y2="80"/>
    <circle class="d-solid-accent" cx="300" cy="165" r="5"/><text class="d-text-accent" x="312" y="160">slope = f′(x₀)</text></g>
</svg>
```

with `"steps": [["axes"], ["f"], ["tangent"]]` and three captions.

- Boxes and arrows: `<rect class="d-fill" rx="8" …/>`, arrows as `<path class="d-line" marker-end="url(#arrow)"/>`
  with a `<defs><marker id="arrow" …><path class="d-line" d="M0 0 L8 4 L0 8"/></marker></defs>`.
- Keep text inside the viewBox; 12–16px; avoid more than ~25 elements per diagram.
