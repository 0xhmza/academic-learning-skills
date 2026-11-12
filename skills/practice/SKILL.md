---
name: practice
description: Train and assess a student with practice questions, problem sets and mock exams. Use when a student wants to practise, be quizzed or tested, needs exercises with solutions, a mock or practice exam, a printable problem sheet with solutions (PDF), an interactive HTML trainer, help understanding mistakes, grading of their own answers, or "drill me on", "test me", "give me exercises", "past-paper style questions", "mark my answer", "why was I wrong". Builds an interactive trainer (MCQ, multiple answer, numeric with tolerance, written with model answer, cloze, ordering; graded hints, step-by-step worked solutions, timed test mode) or a printable exam with marking scheme, and keeps an error log.
---

# Practice

Testing is the main learning event, not just measurement. Every mode ends with feedback and the next step.

**Toolkit.** `ALS` = `python "<this skill's base directory>/../../shared/scripts/als.py"`. Question
design: `references/question-design.md` (read before writing questions). Formats:
`../../shared/starters/quiz.json`, `../../shared/starters/exam.json`. Integrity:
`../../shared/references/integrity.md` (no solving of graded work).

## Modes

| Request | Mode | Output |
|---|---|---|
| "quiz me", "practise X" (in chat) | **Live drill** | conversation |
| "interactive quiz", "trainer", "practice set" | **Trainer** | HTML (`quiz` kind) |
| "problem set", "exercises with solutions", "PDF" | **Problem set** | printable HTML/PDF (`exam` kind) |
| "mock exam", "practice exam" | **Mock exam** | printable exam, optionally a timed trainer too |
| student shares answers or a photo of work | **Mark** | feedback, error log |
| "what do I keep getting wrong?" | **Error review** | targeted drill from `errors.md` |

### Live drill

One question at a time, mixed difficulty, starting at the student's level (`ALS status` shows weak topics).
After each answer: verdict, the key reason, and the next question. Use worked-example fading: if they fail
twice on a type, show a full worked example, then a near-identical problem, then a fresh one. Stop after
~10 questions or on request; summarise and log mistakes.

Three habits that make a drill teach more:

- **Diagnose first.** On a topic the student has not practised, open with 2–3 questions before any
  explanation. A wrong first attempt, followed by feedback, improves what is learned next.
- **Ask for confidence** on about one question in three ("sure, fairly sure or guessing?") before
  giving the verdict. Point out confident errors: they are the ones worth a line in `errors.md`.
- **Ask why.** After a correct answer to a core question, ask once in a while why the method applies
  here or what would change if a condition were dropped.

### Trainer (interactive HTML)

1. `ALS new quiz modules/<id>/data/quiz-<scope>.json --title "…" --module <id> --subject "…"`.
2. Write 8–20 questions: roughly 30% warm-up (difficulty 1), 50% core (2), 20% challenge (3); mix
   types; every question has `topic`, `explain` or `solution` (or both), and 1–3 graded `hints`.
   Numeric questions always get a `tolerance` and `unit`. Include one or two find-the-error questions
   (a worked solution with one wrong step) per set. For a set in another language set `"lang"`
   (`"ar"` gives a right-to-left page with Arabic interface text).
3. `settings.mode`: `practice` (feedback after each question) or `test` (feedback at the end; set
   `timeLimitMin` for timed tests).
4. `ALS build …`. The page exports results ("Save results"); import with
   `ALS progress import <file>` to update topic mastery.

### Problem set and mock exam (print / PDF)

1. `ALS new exam modules/<id>/data/<name>.json …`. Mirror the real assessment from `module.md`
   (`## Assessment`) and past exams in `sources/`: same sections, point values, duration, allowed aids,
   question styles, and a topic spread weighted by `topics.json` weights.
2. Each question: `points`, answer `space`, a full `solution` and a `marking` scheme (how points are
   awarded, including partial credit and common errors that lose points).
3. `ALS build …` then PDFs as needed:
   ```
   ALS pdf modules/<id>/out/<name>.html -o modules/<id>/out/<name>-questions.pdf --query "solutions=off"
   ALS pdf modules/<id>/out/<name>.html -o modules/<id>/out/<name>-solutions.pdf --query "solutions=inline&space=off"
   ```
   Without a browser, tell the student to open the page, choose Solutions: Hidden / Inline / At the end,
   and print.
4. For a mock exam, suggest exam conditions: timer, allowed aids only, then self-mark with the scheme and
   send Claude the marks per question.

### Mark

Grade against the model solution and marking scheme. For each answer: points awarded, what earned them,
what lost them, the misconception (if any) and the fix. Be precise and fair; do not inflate. Then
append to `modules/<id>/errors.md` (format in `../../shared/references/workspace.md`) and record the
attempt for mastery by writing a results file and importing it:
`{"als":"1","kind":"results","source":"quiz","title":"<set>","module":"<id>","date":"YYYY-MM-DD","exported":"<ISO time>","items":[{"id":"q3","topic":"eigen","correct":false}]}`.

### Error review

Read `errors.md`, group by misconception, and build a short targeted set: one worked example per
misconception, then 2–3 fresh problems that trigger the same mistake. Retire an entry from future
reviews after two correct attempts (note it in the log).

## Never

- Never solve, in full, problems from a currently graded assignment (see integrity.md). Offer an analogous
  problem with different numbers instead and say why.
- Never invent past-exam questions and present them as real. Write "in the style of the 2024 exam".
