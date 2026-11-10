# Design systems

Four themes share one component contract, so any page can switch theme (palette button in the top bar)
and light/dark mode without rebuilding. Fonts load from Google Fonts when online and fall back to system
fonts offline.

| Theme | For | Character |
|---|---|---|
| `blueprint` | maths, physics, CS, engineering, statistics | In the spirit of tailwindcss.com: near-black/white, sky accent, Inter + JetBrains Mono, hairline grid, dark code blocks, pill primary buttons, `//` mono kickers |
| `folio` | philosophy, literature, history, languages, arts, theology | Editorial: EB Garamond + Cormorant, paper tones, oxblood ink, small caps, ornamented dividers, drop caps |
| `clinic` | biology, medicine, chemistry, health, psychology, environment | IBM Plex, teal + violet, soft rounded cards, dot lattice, diagram-first |
| `ledger` | economics, business, law, politics, social science, education | Libre Franklin + Source Serif, navy + burgundy, tabular figures, heavy rules |

## How a theme is chosen (first match wins)

1. `--theme` flag on `als.py build`
2. `"theme"` in the data file
3. `theme:` in `modules/<id>/module.md`
4. `theme:` in `profile.md` (unless `auto`)
5. Keyword routing on `subject`, module title and page title (`shared/design-systems/themes.json`)
6. Default: `blueprint`

`als.py theme "<subject>"` shows what routing picks. Add keywords to `themes.json` to tune it.

## Diagram colours (lesson `diagram` slides)

Prefer the ready-made visual components (`plot`, `flow`, `grid`, `layers`, `tree`, `bars`, `figure`:
`skills/visual-lesson/references/components.md`); they already follow the theme. SVG drawn by hand for a
lesson should use these classes instead of hard-coded colours, so it follows the theme and
dark mode:

| Class | Use |
|---|---|
| `d-line` | main strokes (axes, outlines) |
| `d-muted` | secondary strokes (grid, guides) |
| `d-accent`, `d-accent2` | highlighted strokes |
| `d-good`, `d-bad` | correct / incorrect paths |
| `d-fill` | neutral filled shape (boxes) |
| `d-fill-accent` | highlighted filled shape |
| `d-solid-accent`, `d-solid-accent2`, `d-solid-line`, `d-solid-muted`, `d-solid-good`, `d-solid-bad` | solid fills: dots, bars, arrowheads in `<marker>` |
| `d-text`, `d-text-muted`, `d-text-accent` | labels (14px / 12px / 14px bold) |
| `d-halo` | added to a label: outline in the background colour, readable over lines |
| `ls-draw` | added to a `path` or `line`: it draws itself when its step arrives |

Arrowheads are built in: `marker-end="url(#als-arrow)"` (also `-accent`, `-accent2`, `-muted`, `-good`, `-bad`).

Rules for SVG: one `viewBox` (e.g. `0 0 600 320`), no fixed width/height, no scripts or event handlers
(stripped), stroke widths 1.5–3, labels ≥ 12px, every element to reveal gets an `id` referenced from the
slide's `steps`. Group parts that appear together in a `<g id="…">`.

## Adding a theme

1. Copy `shared/design-systems/folio.css` to `<name>.css`; redefine every token for light and
   `[data-als-mode="dark"]`; add motif rules sparingly.
2. Add an entry to `themes.json` with `label`, `short`, `description`, `fonts`, `swatch` and `subjects`.
3. Run `python -m unittest discover tests` — the theme test checks every token is defined in both modes.
