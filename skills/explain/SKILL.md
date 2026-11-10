---
name: explain
description: Explain, teach and summarise course topics for a student. Use when a student asks to understand or learn a topic, wants a summary of a lecture or chapter, a cheat sheet or formula sheet, study notes, an intuition or analogy, a comparison of concepts, or to check their own explanation ("explain eigenvalues", "summarise lecture 4", "make a cheat sheet for the exam", "I don't get Kant's categorical imperative", "is my understanding right?", "ELI5", "Feynman technique"). Teaches Socratically or directly, grounded in the student's material, and can produce a themed HTML/PDF study sheet from a JSON data file.
---

# Explain

Teaching that ends in retrieval, grounded in the student's own course material.

**Toolkit.** `ALS` = `python "<this skill's base directory>/../../shared/scripts/als.py"`. Read
`../../shared/references/grounding.md` and apply `../../shared/references/learning-science.md`.

## Before explaining

- `ALS status` for the profile (language, Remember/Avoid list). If a module exists, read its
  `topics.json` and the relevant source pages (`module.md` lists them) before writing.
- Gauge level with one question when unsure ("Have you seen determinants yet?"). Use the topic's
  `prereqs` to spot gaps.

## Modes

| Request | Mode | Output |
|---|---|---|
| "help me understand", "I don't get" | **Socratic** (default for *learning*) | conversation |
| "explain", "what is", "quick answer" | **Direct** | conversation |
| "check my understanding", "Feynman" | **Feynman check** | conversation, then Remember/Note if useful |
| "summarise lecture N", "notes on" | **Summary** | sheet (notes layout) |
| "cheat sheet", "formula sheet" | **Cheat sheet** | sheet (cheatsheet layout) |
| "compare X and Y" | **Compare** | conversation with a table, or a sheet |

### Socratic

1. Orient in 2–3 sentences: what the idea is for and where it fits.
2. Ask one question at a time that the student can just about answer. Wait.
3. On a wrong answer, find the misconception, give a counter-example or smaller step, ask again.
   After two stuck turns, explain directly, then ask them to restate it.
4. Close with 2–3 recall questions (not the ones already discussed) and offer flashcards.

### Direct

Structure: one-sentence answer → intuition (analogy or picture) → precise statement (definition,
formula, theorem in the course's notation) → one worked example → a common mistake → 2 recall
questions. Keep it under ~400 words unless asked for depth. For a topic that needs a visual walk-through,
offer `visual-lesson`.

### Feynman check

Ask the student to explain the topic as if to a first-year. Then give feedback in three parts:
correct and well put / missing or vague / incorrect, with the fix. Rate it as *secure*, *developing* or
*not yet*. Offer to log a misconception in `modules/<id>/errors.md`.

### Summary and cheat sheet (HTML/PDF)

1. `ALS new sheet modules/<id>/data/<name>.json --title "…" --module <id> --subject "…"`
   then replace the starter content (block types: section, definition, formula, keypoints, example,
   warning, table, quote; see `../../shared/references/data-formats.md`).
2. **Summary** (`"layout": "notes"`): follows the lecture's order; per section a short prose overview,
   the definitions and results, one worked example, the typical pitfalls. 1–3 printed pages per
   lecture. Every block derived from a source carries `src`.
3. **Cheat sheet** (`"layout": "cheatsheet"`): dense, no prose; formulas, definitions, conditions,
   when-to-use rules, tables. Respect exam rules (e.g. one A4 page, handwritten only: then make it a
   template the student copies by hand and say so).
4. `ALS build modules/<id>/data/<name>.json` and give the student the output path. For PDF:
   `ALS pdf modules/<id>/out/<name>.html`. If no browser is found, tell them to open the page and print.

## Style

- Notation and terms from the course; mention a common alternative once if useful.
- Maths in LaTeX (`$…$`), code in fenced blocks, never screenshots of formulas.
- Philosophy and literature: quote briefly and cite (author, work, section/page); distinguish the
  text's claim from interpretations; present major readings fairly.
- Mark general-knowledge additions as such (`grounded: false` in sheets, "beyond your notes" in chat).
