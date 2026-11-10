# Grounding: tie material to the student's sources

Study material is most useful when it matches what the lecturer actually taught and is easy to check.

## Rules

1. **Prefer the student's material.** If `modules/<id>/sources/` or the conversation contains lecture
   slides, notes or a textbook chapter, base content on them. Read the relevant pages first.
2. **Cite with `src`.** Each card, question, slide or block derived from a source gets
   `"src": "<source id> <locator>"`, e.g. `"L3 s.12"` (slide), `"T ch.4 p.88"` (textbook page),
   `"N 2026-11-03"` (student note). Source ids are listed in the data file's `sources` array and in
   `module.md`.
3. **Flag additions.** Content Claude adds from general knowledge gets `"grounded": false`. Use it for
   helpful context, never to override the lecturer. Lessons are strict by default (`lesson_grounding`):
   in a strict lesson nothing is added at all, and the build rejects `grounded: false`.
   When the material is unclear, ask the student; do not fill the gap.
4. **Terminology and notation follow the course.** Use the lecturer's symbols (e.g. `T` vs `A` for a
   linear map), language and naming, even when another convention is more common. Mention the common
   alternative once if it helps the student read other texts.
5. **Conflicts are surfaced.** If sources disagree, or the material looks wrong, say so briefly and
   cite both.
6. **No fabricated references.** Never invent page numbers, DOIs, URLs, ISBNs or quotes. When a
   locator is unknown, omit it rather than guess.

## Links and recommendations (resources skill)

- A link is shown only after it has been fetched in this session and the page matches the title.
  Mark items "unverified" otherwise, or leave them out.
- For books and papers, give author, title, year and (if known) edition. Prefer open-access versions
  (publisher OA, arXiv, institutional repositories, OpenStax, Project Gutenberg) when they exist.
- For videos, give channel, title, length, and the specific timestamp range that is relevant.
