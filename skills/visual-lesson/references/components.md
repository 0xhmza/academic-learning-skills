# Visual components

Each component is a slide layout: a small spec in, a themed, animated SVG out. All of them accept
`title`, `steps`, `captions` (one per step), `caption`, `focus` and the usual `src`, `notes`, `more`,
`level`. Labels inside a drawing are plain text: use Unicode (σ, x₁, ŷ, ∂), not LaTeX.

## Steps

`steps` is a list of groups; each → press applies the next group. Omit it to get the automatic order
given below. A group lists element ids:

| Token | Effect |
|---|---|
| `"id"` | hidden until this step, then stays |
| `"-id"` | removed from this step on |
| `"!id"` | highlighted during this step only (visibility unchanged) |

`"focus": true` dims everything revealed earlier, so the newest step stands out. The build fails on an
id that does not exist and lists the valid ones.

## `plot`: curves, data and guide lines

```json
{ "layout": "plot", "title": "Sigmoid", "x": [-6, 6], "y": [0, 1], "xlabel": "z", "ylabel": "σ(z)",
  "curves": [{ "id": "sig", "fn": "1/(1+exp(-x))", "label": "σ(z)" }],
  "lines": [{ "y": 0.5, "label": "0.5" }], "points": [{ "at": [0, 0.5], "label": "(0, 0.5)" }],
  "captions": ["Axes.", "The curve.", "It crosses 0.5 at z = 0."] }
```

- `curves[]`: `fn` (expression in `x`) or `data` (`[[x, y], …]`, for values read from the source);
  `label`, `style`, `dash`, `from`, `to`. Functions: `exp log ln log2 log10 sin cos tan tanh sqrt abs
  sign floor ceil max min pow sigmoid relu step`; constants `pi`, `e`; operators `+ - * / ^`.
- `scatter[]`: `data`, `label`, `style`, `shape` (`"o"` or `"x"`): two classes of points.
- `lines[]`: `{ "x": v }` or `{ "y": v }` dashed guide with `label`. `points[]`: `at`, `label`.
  `notes[]`: `at`, `text` (free label).
- `ticks: { "x": […], "y": […] }`, `grid: true`, `legend: "left"`.
- Ids: `axes`; curves `c1, c2…`; scatter `s1…`; lines `l1…`; points `p1…`; notes `t1…`; or the `id` you give.
- Auto steps: axes, each curve, each scatter set, then lines, points and notes together.
- Styles everywhere: `accent`, `accent2`, `good`, `bad`, `muted`, `line`.

## `flow`: boxes and arrows, laid out automatically

```json
{ "layout": "flow", "title": "Forward pass", "dir": "right",
  "nodes": ["x: Input", { "id": "h", "label": "Hidden", "sub": "ReLU", "style": "accent" }, "y: Output"],
  "edges": ["x>h: W₁", "h>y: W₂"] }
```

- Node: `"id: Label"` or `{ id, label, sub, style: "accent", shape: "box"|"pill"|"circle", at: [column, row] }`.
- Edge: `"a>b"`, `"a>b: label"`, a chain `"a>b>c"`, or `["a", "b", "label"]`. Edges that point backwards
  (loops, feedback) are drawn curved.
- `dir`: `"right"` (default) or `"down"`. Columns come from the longest path; `at` overrides.
- Ids: node ids, and `a>b` for each edge. Auto steps: one node per step with the edges that join it to
  what is already shown.

## `grid`: matrices, arrays, windows, tables of cells

```json
{ "layout": "grid", "title": "Convolution", "grids": [
    { "id": "in", "label": "input", "cells": [[1, 2, 0], [0, 1, 3], [2, 1, 0]] },
    { "id": "k", "label": "kernel", "op": "∗", "cells": [[1, 0], [0, 1]] },
    { "id": "out", "label": "output", "op": "=", "cells": [[2, 5], [1, 1]] }],
  "steps": [["in", "k"], ["out", "!in.r1c1:r2c2", "!out.r1c1"], ["!in.r1c2:r2c3", "!out.r1c2"]] }
```

- One grid: `cells` at the top level (ids `r1c1`, `row2`, `col3`, `r1c1:r2c2`, whole grid `grid`).
- Several: `grids[]`, each with `id`, `cells`, `label`, `op` (symbol drawn before it), `style`.
  Ids are prefixed: `in.r1c1`, `in.row2`, `in.col3`, `in.r1c1:r2c2`, whole grid `in`.
- `null` leaves a cell empty. Rows and columns count from 1.
- No auto steps (everything shows at once). Walk through it with `!` highlights.

## `layers`: columns of fully connected units

```json
{ "layout": "layers", "layers": [{ "n": 3, "label": "Input" }, { "n": 4, "label": "Hidden", "style": "accent" }, { "n": 1, "label": "Output" }] }
```

- A layer is a number or `{ n, label, sub, style, nodes: ["x₁", "x₂", …] }`. More than `max` (6) units
  are drawn with an ellipsis.
- Ids: `L1, L2…` (layers) and `E1, E2…` (connections from layer i to i+1). Auto steps: layer by layer.

## `tree`

```json
{ "layout": "tree", "root": ["f(4)", ["f(3)", "f(2)", "f(1)"], "f(2)"] }
```

- A node is `"label"`, `["label", child, child…]` or `{ label, id, sub, style, children }`.
  `shape`: `box`, `pill`, `circle`.
- Ids: `n1, n2…` in reading order (parent before children, left to right) unless `id` is given; edges
  `parent>child`. Auto steps: level by level.

## `bars`

```json
{ "layout": "bars", "labels": ["train", "val", "test"], "values": [98, 91, 90], "unit": "%", "highlight": [2] }
```

Ids: `axes`, `b1, b2…`. `highlight` counts from 1. Options: `max`, `ylabel`. Auto steps: axes, then bar by bar.

## `figure`: the lecturer's own picture, with spotlights

```json
{ "layout": "figure", "title": "U-Net", "image": "../sources/text/L10-p014.png", "alt": "U-Net architecture",
  "caption": "The figure from the lecture.",
  "marks": [{ "x": 5, "y": 10, "w": 40, "h": 80, "text": "Contracting path: convolutions and pooling." },
            { "x": 55, "y": 10, "w": 40, "h": 80, "text": "Expanding path: up-convolutions." }], "src": "L10 s.14" }
```

- `image` is a path relative to the lesson file (png, jpg, gif, webp, svg); the build embeds it.
  Render pages with `ALS extract <pdf> --pages 14 --images all --dpi 80`.
- `marks[]`: rectangles in percent of the image (`x`, `y` = top-left corner; `w`, `h`), each with `text`
  and an optional `label`. Each → press spotlights the next mark and shows its text.
- Use it when a figure cannot be redrawn faithfully, or when the student should recognise the original.
  Look at the image before writing marks; estimate positions from what you see.

## `diagram`: hand-written SVG (last resort)

```json
{ "layout": "diagram", "svg": "<svg viewBox='0 0 600 300' xmlns='http://www.w3.org/2000/svg'>…</svg>",
  "steps": [["axes"], ["f"], ["tangent"]], "captions": ["…", "…", "…"] }
```

```xml
<svg viewBox="0 0 600 300" xmlns="http://www.w3.org/2000/svg">
  <g id="axes"><line class="d-line" x1="50" y1="260" x2="570" y2="260"/><line class="d-line" x1="50" y1="260" x2="50" y2="30"/></g>
  <path id="f" class="d-accent ls-draw" stroke-width="3" d="M50 240 C 200 240, 300 60, 560 50"/>
  <g id="tangent"><line class="d-accent2" stroke-dasharray="6 4" x1="180" y1="250" x2="420" y2="80"/>
    <circle class="d-solid-accent" cx="300" cy="165" r="5"/><text class="d-text-accent" x="312" y="160">slope = f′(x₀)</text></g>
  <line id="arrow" class="d-line" x1="100" y1="60" x2="200" y2="60" marker-end="url(#als-arrow)"/>
</svg>
```

- Colour classes (never hard-code colours): strokes `d-line`, `d-muted`, `d-accent`, `d-accent2`,
  `d-good`, `d-bad`; fills `d-fill`, `d-fill-accent`; solids `d-solid-accent`, `d-solid-accent2`,
  `d-solid-line`, `d-solid-muted`, `d-solid-good`, `d-solid-bad`; text `d-text`, `d-text-muted`,
  `d-text-accent`; `d-halo` gives a label a background-coloured outline so it stays readable over lines.
- Arrowheads are built in: `marker-end="url(#als-arrow)"`, or `#als-arrow-accent`, `-accent2`,
  `-muted`, `-good`, `-bad`. Do not write `<defs>` for them.
- `class="… ls-draw"` on a `path` or `line` makes it draw itself when its step arrives.
- One `viewBox`, no width or height, no scripts. Stroke widths 1.5–3, labels 12–16px, at most about
  25 elements. Give every element that appears later an `id`; group what appears together in a `<g id>`.
