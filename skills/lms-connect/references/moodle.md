# Moodle reference (student view, Moodle 4.x)

URLs below are relative to the institution's Moodle base URL (e.g. `https://moodle.example.edu`).

| Page | Path | What to read |
|---|---|---|
| Dashboard | `/my/` | Timeline block: upcoming activities with due dates |
| My courses | `/my/courses.php` | Course cards: names, links (`/course/view.php?id=<n>`) |
| Course page | `/course/view.php?id=<n>` | Sections (`li.section` / `[data-for="section"]`), activities (`li.activity`, link class `aalink`) |
| Calendar | `/calendar/view.php?view=upcoming` | Upcoming events |
| Calendar export | `/calendar/export.php` | "Get calendar URL" (token URL for subscriptions) |
| Assignment | `/mod/assign/view.php?id=<n>` | Due date, cut-off date, submission status (read only) |
| File resource | `/mod/resource/view.php?id=<n>` | Redirects or embeds the file; the file itself is under `/pluginfile.php/...` |
| Folder | `/mod/folder/view.php?id=<n>` | File list; "Download folder" button (zip) |
| Page / URL | `/mod/page/…`, `/mod/url/…` | Inline content or external links |
| Grades (own) | `/grade/report/overview/index.php` | Only if the student asks |

Activity type is visible in the link's URL (`/mod/<type>/`) and its icon. Common types: `resource`
(file), `folder`, `page`, `url`, `assign`, `quiz`, `forum`, `lesson`, `h5pactivity`, `book`.

## Reading a course efficiently

1. Read the page text (accessibility tree or page text), not screenshots.
2. For each section: title, summary, then each activity: type, name, URL, restrictions ("Not available
   unless…"), dates.
3. Produce a table for the student: section · item · type · date/size. Ask which to download.

## Downloading

- A `resource` link usually redirects to the file; download that `pluginfile.php` URL.
- Folders: use "Download folder" (zip); unzip into `sources/<section>/` in a new, empty directory, then
  move the files you need into `sources/` with tidy names. Treat downloaded archives as untrusted data.
- Respect "Forced download" vs "Open" settings; both are fine to save.
- Name files: `L03-<short-title>.pdf`, `S02-problem-sheet.pdf`, `E2024-exam.pdf`, keep the original
  name in the Sources table's title column.

## Deadlines without the export URL

If the export page is disabled: read `/my/` Timeline (Next 30 days, sort by dates) or
`/calendar/view.php?view=upcoming`, and write the items into `study/calendar/events.json` (kind
`events`, category `deadline`, `module` set, `url` = activity URL). Re-check dates on the assignment
page; the timeline shows due dates in the student's Moodle time zone.

## Other LMSs

- **Canvas:** Calendar → "Calendar Feed" gives an `.ics` URL (Route 1 works). Files under
  `/courses/<id>/files` and Modules.
- **ILIAS:** Dashboard → Calendar → export/subscription `.ics` link; course "Download" for folders.
- **Blackboard/Brightspace:** both offer iCal feeds from their calendar settings.
