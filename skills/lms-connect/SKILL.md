---
name: lms-connect
description: Connect a student's Moodle (or similar LMS such as Canvas or ILIAS) to their study workspace. Use when a student asks to get deadlines or assignments from Moodle, sync or export their Moodle calendar, download lecture slides or course files from Moodle, "check what's due", "get my course material", "import my university calendar", or make an .ics of their deadlines. Uses the Moodle calendar export URL for deadlines, and the browser (with the student signed in themselves) to list and download course material into the module's sources folder. Read-only and never handles passwords.
---

# LMS connect (Moodle first)

Three routes, from safest to most involved. Use the first one that covers the request.

**Toolkit.** `ALS` = `python "<this skill's base directory>/../../shared/scripts/als.py"`. Detailed
steps and Moodle page structure: `references/moodle.md`. Rules: `../../shared/references/integrity.md`
(LMS section) — read it before using the browser.

## Route 1: deadlines via calendar export (no browser automation)

1. Ask the student to open Moodle → Calendar → **Export calendar** (or *Import or export calendars* →
   *Export calendar*), choose *All events* (or *Events related to courses*) and *Recent and next 60 days*
   (or a custom range), click **Get calendar URL** and paste the URL here. The URL contains a private
   token; treat it like a password: use it, never write it into workspace files, never echo it back.
2. Import:
   ```
   ALS ics-import "<url>" --since <today>
   ```
   The command prints the course labels it found (Moodle puts the course short name in CATEGORIES).
   Map them to module ids and re-run: `ALS ics-import "<url>" --map "MATH202=linear-algebra" --map "PHIL101=ethics"`.
   It merges into `study/calendar/events.json` and classifies events as deadline/exam/lecture/other.
3. If the student wants it in their calendar app: they can subscribe to the Moodle URL directly in
   Google/Outlook/Apple (updates automatically). Offer that first. Otherwise, build a filtered `.ics`
   with the planner skill.
4. Suggest saving the URL in an environment variable (`ALS_MOODLE_ICS_URL`) for next time, never in a file
   in the workspace.

If the student downloaded an `.ics` file instead, use its path in place of the URL.

## Route 2: course material via the browser

Use the browser that the session provides (prefer the student's own browser where they are already
signed in). Follow `references/moodle.md`:

1. Open the Moodle dashboard URL from the profile's `lms_url` (or ask for it). If a login page appears,
   ask the student to sign in themselves and tell you when done. Never type credentials, never complete
   MFA or CAPTCHA.
2. List enrolled courses, then for the chosen course read the course page: sections, resources (files,
   folders, pages, URLs), assignments with due dates.
3. Show the student what you found (count and names of files per section) and confirm which to download.
   Downloading counts as an action that needs their go-ahead.
4. Download into `modules/<id>/sources/` with the naming scheme from module-setup. Prefer a section's or
   folder's "Download folder" button when present. Skip files already there (same name and size).
5. Update `module.md` (`lms_course_url`, Sources table) and log the sync. Then offer `module-setup` to
   update the topic map from the new files.

## Route 3: Moodle web services token (optional, institution-dependent)

Some universities enable the Moodle mobile/web service for students. If the student has a token, an MCP
server for Moodle can be used instead of the browser. Do not ask for tokens proactively; mention the
option only if browser access is impractical.

## Never

- Submit assignments, start or answer quizzes, post to forums, change profile or notification settings.
- Store or print passwords, session cookies, tokens or the calendar export URL.
- Download other students' submissions or anything outside the student's own enrolled courses.
- Keep going when a page shows terms that forbid automated access: stop and use Route 1 or manual
  download instead.
