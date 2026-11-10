---
name: planner
description: Make study plans, exam countdowns, weekly schedules and calendar files for a student. Use when a student asks for a study plan, revision timetable, "plan my week", "I have an exam in 3 weeks", "how should I prepare", "schedule my reviews", "put this in my calendar", "export to .ics / Google Calendar / Outlook / Apple Calendar", or wants deadlines and study sessions as calendar events. Plans backwards from exams and deadlines with spaced reviews and interleaving, respects available hours, and exports an importable .ics file.
---

# Planner

Plans that a student can actually follow, delivered as a readable plan and an `.ics` calendar.

**Toolkit.** `ALS` = `python "<this skill's base directory>/../../shared/scripts/als.py"`. Method:
`references/planning.md`. Event format: `../../shared/starters/events.json`.

## Inputs (gather, don't interrogate)

- `ALS status --json`: modules, exam dates, deadlines (imported from Moodle by `lms-connect`), due
  reviews, weak topics, profile (`timezone`, `weekly_hours`, `session_minutes`).
- `modules/<id>/topics.json`: topics, weights, prerequisites.
- Ask only for what is missing: available days/times this period, fixed commitments, and how far they
  are through the material.

## Workflow

1. **Frame** the period (this week, until the exam, the semester) and the goal per module.
2. **Budget** hours: available hours × 0.8 (slack). Split across modules by urgency (days to exam) ×
   workload (weighted unmastered topics). State the split in one line.
3. **Plan backwards** from each exam (`references/planning.md`): learn new material first, then
   consolidation, then mock exams in the last 7–10 days, a light final day.
4. **Sessions** are `session_minutes` long with a stated goal and method: "50 min · Eigenvalues ·
   2 worked examples + 6 problems (practice)". Use the toolkit skill names so the student knows what to ask
   for. Add 10–15 minute review slots for due flashcards on most days.
5. **Write the plan** as `modules/<id>/data/plan-<period>.md` (or `study/plan-<period>.md` for several
   modules): a week-by-week table and today's first step.
6. **Calendar:** write `study/calendar/plan-<period>.events.json` (`kind: events`, `timezone` from the
   profile, categories `study`/`review`/`deadline`/`exam`, `alarmsMin` [10] for sessions and
   [1440, 10080] for exams), then:
   ```
   ALS ics study/calendar/plan-<period>.events.json -o study/calendar/plan-<period>.ics
   ```
   Tell the student how to import it: Google Calendar → Settings → Import & export; Outlook → Add
   calendar → Upload from file; Apple Calendar → File → Import. Suggest importing into a separate
   "Study" calendar so it can be removed in one step.
7. **Re-plan** when they fall behind: never stack missed sessions onto the next days. Drop or shorten
   lower-weight topics, keep the reviews and the mock exam, and say what was cut.

## Rules

- Never exceed `weekly_hours` or schedule outside the student's stated times without asking.
- At least one rest day per week and no study blocks longer than 2 hours without a break.
- Deadlines and exams come from imported calendars or the student. Never invent dates.
- If the plan is infeasible (too much material for the time), say so early and offer a triage: what to
  master, what to know roughly, what to skip.
