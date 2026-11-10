# Working on this repository

Academic Learning Skills is a Claude Code plugin: skills (Markdown instructions) plus a small Python CLI
and HTML templates that turn JSON data into study pages.

## Layout

```
.claude-plugin/        plugin.json, marketplace.json (keep versions equal)
skills/<name>/         SKILL.md (+ references/) — one folder per skill
commands/als-*.md      thin slash-command wrappers that name a skill and a mode
hooks/                 SessionStart hook: prints workspace status when a study/ folder exists
shared/
  scripts/als.py       CLI entry point; logic in shared/scripts/als_lib/
  templates/           core.js + one HTML template per kind (deck, lesson, quiz, exam, sheet, dashboard)
  design-systems/      base.css (component contract), <theme>.css, themes.json (registry + routing)
  schemas/             JSON Schemas per kind + common.md
  starters/            one valid example data file per kind (what Claude copies)
  references/          shared guidance read by several skills
examples/<module>/     showcase data; examples/showcase/ holds built pages (python tools/build_examples.py)
tests/                 unittest suite
```

## Conventions

- **Skills reference shared files relatively** from their own folder: `../../shared/...`. The test suite
  checks that every backticked `../../shared/...` and `references/...` path exists.
- **Front matter must be valid YAML.** Avoid `": "` inside unquoted values; command files quote all values.
  Skill `description` ≤ 1024 characters and carries the trigger phrases.
- **Templates:** only use classes from `base.css` plus template-local classes built on theme tokens. Never
  hard-code colours. Markers `/*ALS:EARLY*/`, `/*ALS:CSS*/`, `/*ALS:CORE*/`, `<!--ALS:DATA-->` and
  `{{title}}`, `{{lang}}`, `{{theme}}`, `{{version}}` are filled by `als_lib/build.py`.
- **Rich text** is rendered by `ALS.md` (core.js) and `richtext.py` (Anki); keep them in sync when adding syntax.
- **Data format changes** need: schema update, starter update, semantic checks in `validate.py` if needed,
  template support, `shared/references/data-formats.md`, and a test.
- **Python:** standard library only (genanki optional), 3.9+. Write files with `encoding="utf-8"`.
- **Safety rules** for skills live in `shared/references/integrity.md`; new skills must link it if they act
  on accounts, graded work or downloads.

## Before committing

```
python -m unittest discover tests
python tools/build_examples.py
```

Preview built pages with `python -m http.server 8642` from the repo root (the desktop app's preview reads
`.claude/launch.json`).
