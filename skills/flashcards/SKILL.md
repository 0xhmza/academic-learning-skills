---
name: flashcards
description: Create and review flashcards. Use when a student wants flashcards, an Anki deck (.apkg), cloze cards, Quizlet or CSV export, interactive HTML flashcards, to "turn this lecture into cards", "make cards from my notes", "what's due for review", or to study cards with spaced repetition. Writes one JSON deck and builds a themed interactive HTML deck (flip, grade, relearn, due-today filter, print) plus Anki/Quizlet exports from the same file; imports review results to schedule the next reviews.
---

# Flashcards

One deck file, many outputs: interactive HTML, Anki `.apkg`, Anki text import, Quizlet, CSV.

**Toolkit.** `ALS` = `python "<this skill's base directory>/../../shared/scripts/als.py"`. Card
rules: `references/card-writing.md` (read before writing a deck). Format:
`../../shared/starters/deck.json`.

## Create a deck

1. Identify scope (lecture, topic or the student's notes) and read those source pages. Check the
   profile for language and Remember/Avoid preferences (e.g. bilingual terms).
2. `ALS new deck modules/<id>/data/deck-<scope>.json --title "…" --module <id> --subject "…"`, then
   replace the cards. Aim for 15–40 cards per lecture; prefer fewer, better cards.
3. Per card: stable `id` (`l3-01`, …; never reuse ids for different content: they key the review
   schedule), `type` (`basic`, `reverse` for term⇄definition, `cloze` for facts in context), `topic`
   from `topics.json`, `src` locator, `tags` for card kinds (`definition`, `formula`, `theorem`,
   `date`, `quote`, `vocab`).
4. Build and export:
   ```
   ALS build modules/<id>/data/deck-<scope>.json        # interactive HTML in modules/<id>/out/
   ALS anki  modules/<id>/data/deck-<scope>.json        # .apkg (or Anki text import without genanki)
   ALS anki  modules/<id>/data/deck-<scope>.json --format quizlet   # only if asked
   ```
5. Tell the student where the files are and how to use them in one or two lines: open the HTML (Space
   flips, 1–4 grades, "Save results" at the end), or double-click the `.apkg` to import into Anki (decks
   appear as `module::title`; re-importing updates the same notes rather than duplicating them).

## Review with spaced repetition

- `ALS due --module <id>` shows how many cards are due. `ALS build` embeds today's due ids, so the HTML
  deck opens on "Due today".
- After a session the page saves `…-results-YYYY-MM-DD.json` (usually in Downloads). Import it:
  `ALS progress import <file>`. Cards move through Leitner boxes (1, 2, 4, 8, 16, 32 days); "Again"
  resets to tomorrow.
- Students using Anki schedule there instead; then skip results import.
- One good answer is not mastery. A card is learned when it has been recalled correctly in several
  sessions on different days, so encourage finishing the due cards before making new ones.
- Decks in other languages: set `"lang"` (`"ar"`, `"de"`, …). Arabic decks are right-to-left on the
  page and in the Anki export; formulas stay left-to-right.

## Edit a deck

Edit the JSON (keep ids), rebuild, re-export. To merge decks, concatenate `cards` and check for duplicate
ids with `ALS validate`.

## Interactive review in chat

If the student wants to be quizzed in the conversation instead: ask one card at a time from the deck
(due cards first), wait for their answer, grade it against the back (be strict about meaning, lenient
about wording), and record a results file in the export format if they want progress tracked:
`{"als":"1","kind":"results","source":"deck","title":"…","module":"…","date":"YYYY-MM-DD","exported":"<ISO time>","items":[{"id":"l3-01","topic":"…","grade":"good"}]}`,
then `ALS progress import` it.
