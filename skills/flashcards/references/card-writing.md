# Writing good flashcards

Based on the minimum-information principle and retrieval-practice research. A card that takes more than
~8 seconds to answer is usually two cards.

## Rules

1. **Atomic.** One fact, one relationship, one step. Split "What are the 4 properties of X?" into four
   cards, or one cloze per property in a sentence.
2. **Ask for understanding, not recognition.** Prefer "Why does … imply …?" and "When can you apply …?"
   over "What is the name of …?" for core ideas. Keep pure-recall cards for definitions, formulas, dates.
3. **Context in the question.** The front must be answerable without seeing other cards:
   "(Linear algebra) An eigenvector of A is …" not "It is …".
4. **No lists or sets on the back.** Sets of more than 2 items are forgotten; use cloze or split.
5. **Cloze for facts in a sentence**, one blank per idea: `{{c1::…}}` and `{{c2::…}}` make two cards.
   Use the hint form `{{c1::answer::hint}}` when several answers would fit.
6. **Reverse only when both directions matter** (term ⇄ definition, word ⇄ translation, symbol ⇄ meaning).
7. **Formulas:** ask for the formula *and* for its use: "Formula for the variance of a sum of
   independent X, Y?" plus "When does Var(X+Y) = Var X + Var Y fail?"
8. **Examples on the back** (`extra`): one short concrete example or mnemonic. Not a paragraph.
9. **Interference:** for confusable pairs (mitosis/meiosis, Kant/Hume on causation), make explicit
   contrast cards: "Mitosis vs meiosis: number of daughter cells?"
10. **Stay grounded.** Lecturer's definitions and notation; `src` on every card; `grounded: false` for
    added context.

## By subject

| Subject | Good card kinds |
|---|---|
| Maths, physics | definition ⇄ term, theorem conditions, "what does this formula compute", first step of a standard method, units |
| CS | complexity of X, invariant of a data structure, what this snippet prints, when to use A vs B |
| Biology, medicine | structure → function, cause → effect, drug → mechanism → side effect, normal values (cloze) |
| Chemistry | reagent → product, mechanism step, conditions, trends in the periodic table |
| Philosophy | thinker + work → thesis, argument premise (cloze), objection → reply, term in a thinker's sense |
| Literature, history | work → author/year/movement, quotation → speaker/context, event → cause/consequence |
| Languages | word ⇄ translation (reverse), word in a sentence (cloze), gender/plural, false friends |
| Law, economics | rule → elements, case → principle, model → assumptions, curve shift → cause |

## Bad → good

- Bad: "What is photosynthesis?" → Good: "Photosynthesis: overall products?" and a cloze
  "Light reactions occur in the {{c1::thylakoid membrane}}."
- Bad: "Explain Kant's ethics." → Good: "Kant: first formulation of the categorical imperative?" and
  "Kant: why can lying not be universalised (in one sentence)?"
