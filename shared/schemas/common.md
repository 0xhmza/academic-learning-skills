# Shared data conventions

Every generated artefact starts as a JSON data file. Templates and scripts read only that file, so Claude
never writes HTML, CSS or JavaScript for a study output.

## Envelope (all kinds)

| Field | Required | Meaning |
|---|---|---|
| `als` | yes | Format version, currently `"1"` |
| `kind` | yes | `deck`, `lesson`, `quiz`, `exam`, `sheet` (and `dashboard`, built by the CLI) |
| `title` | yes | Shown as the page title |
| `subtitle` | no | One line under the title |
| `module` | no | Module id from the workspace (`modules/<id>/`) |
| `subject` | no | Free text such as "Linear algebra"; used to pick a theme |
| `theme` | no | `blueprint`, `folio`, `clinic`, `ledger`; overrides routing |
| `lang` | no | BCP 47 tag, default `en` |
| `sources` | no | `[{ "id": "L3", "title": "Lecture 3 slides", "locator": "slides 4-12" }]` |

## Rich text

Any field described as *rich* accepts a small, safe Markdown subset:

- `**bold**`, `*italic*`, `` `code` ``, `[link](https://…)` (http/https only)
- blank line = new paragraph; lines starting with `- ` or `1. ` = lists
- `$inline math$` and `$$display math$$` in LaTeX (rendered with KaTeX when online)
- raw HTML is escaped, never rendered

## Grounding

Items may carry `"src": "L3 s.7"` pointing at an entry in `sources` plus a locator. Items with
`"grounded": false` are content Claude added beyond the student's material; templates mark them with a
small "beyond your notes" badge.

## Topics

Items may carry `"topic": "<topic-id>"` matching `modules/<id>/topics.json`. Results exported from the
flashcard and trainer pages are keyed by item id and topic, which is how mastery is tracked.

See the per-kind JSON Schemas in this folder. `python shared/scripts/als.py validate <file>` checks a file.
