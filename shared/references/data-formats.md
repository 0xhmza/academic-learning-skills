# Writing data files (token-cheap)

Never write HTML, CSS or JS for study pages. Write one JSON data file, then `ALS build` it.

1. Start from a starter: `ALS new <kind> modules/<id>/data/<name>.json --title "…" --module <id> --subject "…"`
   (or read `shared/starters/<kind>.json`, a valid example of every field). Replace its content.
2. `ALS build <file>` validates and builds. Fix any reported error and build again.
3. To change content later, edit the JSON and rebuild; the page keeps the student's theme choice.

Full contracts: `shared/schemas/*.schema.json` and `shared/schemas/common.md`. The essentials:

- **Envelope:** `als: "1"`, `kind`, `title`; optional `subtitle`, `module`, `subject`, `theme`, `lang`, `sources`.
- **Rich text** fields accept `**bold**`, `*italic*`, `` `code` ``, links, `- lists`, `$maths$`, `$$display$$`.
  In JSON, escape backslashes in LaTeX: `"$\\frac{a}{b}$"`.
- **Provenance:** `src` ("L3 s.12") and `grounded: false` on any item.
- **Topics:** `topic` on cards/questions = topic id from `topics.json` (drives mastery).

| Kind | Items | Notes |
|---|---|---|
| `deck` | `cards[]`: `basic` (front/back), `reverse` (also back→front), `cloze` (`text` with `{{c1::answer::hint}}`) | ids stable across edits; they key the review schedule |
| `lesson` | `slides[]` with `layout`: title, points, steps, diagram, code, compare, quote, check, summary, timeline, definition | each point/step/column/event is revealed one at a time |
| `quiz` | `questions[]` with `type`: mcq, multi, numeric (`tolerance`, `unit`), text (`answer`, `keywords`), cloze (`text` with `{{1}}` + `blanks`), order (`items` in correct order) | `hints[]` graded; `solution[]` revealed step by step; `difficulty` 1–3 |
| `exam` | `sections[].questions[]` with `points`, `space`, `solution`, `marking[]`, `parts[]` | printable; solutions hidden / inline / at the end |
| `sheet` | `blocks[]`: section, definition, formula, keypoints, example, warning, table, quote; `layout` notes or cheatsheet | notes get a contents list from 4 sections |
| `events` | `events[]` with `start` (date or datetime), `end`/`durationMin`, `allDay`, `category`, `alarmsMin[]` | input for `ALS ics` |

## Size guidance

- Deck: 15–40 cards per lecture. Lesson: 8–20 slides. Quiz: 8–20 questions. Exam: as long as the real one.
- Keep each string short; long strings cost tokens and hurt recall. A card front under ~150 characters.
