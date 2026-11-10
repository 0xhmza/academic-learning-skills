---
name: resources
description: Recommend and vet learning resources for a student's topic, such as textbooks, open textbooks, papers, lecture videos, YouTube explainers, online courses, problem collections, past papers, podcasts, encyclopedia entries and tools. Use when a student asks "what should I read/watch", "recommend a book/video/course on", "is there a better explanation of", "where can I find practice problems", "reading list", "literature for". Matches level and preferences from the profile, prefers open-access, checks every link before recommending it, and saves the list in the module.
---

# Resources

A short, verified, well-matched list beats a long one. Three to seven items, each with a reason.

**Toolkit.** `ALS` = `python "<this skill's base directory>/../../shared/scripts/als.py"`. Sources to
start from: `references/catalog.md`. Link and citation rules: `../../shared/references/grounding.md`.

## Workflow

1. **Pin the need**: topic (from `topics.json` if a module exists), level (first-year / advanced /
   graduate), purpose (first understanding, exam practice, depth, a different angle), format and length
   preferences (profile Remember/Avoid list: e.g. "no videos over 20 min"), language.
2. **Search** with the tools available (web search, the browser, a library catalogue the student names).
   Start from the catalog for the field; then look for topic-specific items.
3. **Verify each item** before listing it: open the page, check that it exists, matches the title and
   covers the topic at the right level. For videos note the length and the relevant timestamp range. For
   books, note edition and the specific chapter/section. Drop anything you could not verify, or mark it
   "unverified" if the student wants it anyway.
4. **Present** as a compact list, best first:
   `**Title** — author/channel, year · format, length · why this one: … · start at: ch. 4 / 03:10–14:20 · [link]`
   Mark open-access items. Include at most one "stretch" item above their level.
5. **Save** the list (Markdown) to `modules/<id>/resources.md` (append a dated section) so it survives the
   session. If the student says a source helped or did not, `ALS remember` the preference (e.g. "Likes
   3Blue1Brown-style visual explanations").

## Rules

- Never invent titles, authors, ISBNs, DOIs, timestamps or URLs. No link without a successful visit.
- Prefer the course's own recommended literature (syllabus, `module.md`) and the library's e-books
  before buying suggestions. Flag paywalled items and suggest the university library route.
- No pirated copies or shadow libraries.
- For research-level literature reviews, point to the academic-research-skills `deep-research` skill.
