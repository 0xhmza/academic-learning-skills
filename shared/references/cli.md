# `als.py` command reference

`ALS` below means `python "<plugin root>/shared/scripts/als.py"`. From a skill, the plugin root is two
levels above the skill's base directory (`<skill dir>/../..`). Add `--home <dir>` before the command
to use a workspace other than `$ALS_HOME` or `./study`.

## Workspace

| Command | Does |
|---|---|
| `ALS where` | Print the workspace path and whether it exists |
| `ALS init --name N --programme P --timezone TZ --languages "en, de" --goals "a; b"` | Create `profile.md`, `notes/`, `calendar/`, `modules/` |
| `ALS remember "text"` / `--avoid` | Append a dated bullet to `## Remember` / `## Avoid` in the profile |
| `ALS note "Title" "text"` (`-` for stdin) `--module id` | Save `notes/YYYY-MM-DD-title.md` |
| `ALS module new <id> --title T [--code C --term T --exam-date YYYY-MM-DD --subject S --theme X]` | Create a module folder |
| `ALS module list` | List modules |
| `ALS module log <id> --text "…"` | Append to the module's `## Log` |
| `ALS status` / `--json` | Due reviews, deadlines, weak topics, remembered preferences, next steps |
| `ALS dashboard` | Build `study/dashboard.html` |

## Producing material

| Command | Does |
|---|---|
| `ALS new <kind> <out.json> --title T --module id --subject S` | Copy a valid starter (deck, lesson, quiz, exam, sheet, events) |
| `ALS validate <files…>` | Schema + semantic checks; prints errors and warnings |
| `ALS build <files…> [-o out.html] [--theme X] [--no-due]` | Build themed, self-contained HTML. Files in `modules/<id>/data/` build to `modules/<id>/out/` |
| `ALS theme "<subject>"` / `--list` | Show which design system a subject routes to |
| `ALS anki <deck.json> [--format apkg\|anki-tsv\|quizlet\|csv] [-o out]` | Export a deck. `.apkg` needs `genanki`; falls back to Anki text import |
| `ALS pdf <page.html> [-o out.pdf] [--query "solutions=end"]` | Headless Chrome/Edge print. Query options: exam `solutions=off\|inline\|end`, `space=on\|off`; lesson and deck `print=1` |

## Calendar and progress

| Command | Does |
|---|---|
| `ALS ics <events.json> [-o out.ics]` | Write an RFC 5545 calendar (alarms, all-day deadlines, floating times without a tz database) |
| `ALS ics-import <file-or-URL> [--map "LABEL=module-id"] [--module id] [--since YYYY-MM-DD]` | Merge an `.ics` feed (e.g. Moodle export) into `calendar/events.json`, classifying deadlines and exams. URLs are never printed |
| `ALS progress import <results.json…> [--module id]` | Apply results exported from flashcard/trainer pages (idempotent) |
| `ALS due [--module id] [--within N] [-v] [--json]` | List items due for review |
| `ALS progress show` | Dump `progress.json` |

Exit code is non-zero on any error; read the message and fix the data rather than retrying blindly.
