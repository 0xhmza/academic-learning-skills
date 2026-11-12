# Question design reference

## Coverage

- Map each question to a topic and to one objective in `topics.json`. Cover the heavily weighted topics
  more, but touch every examinable topic in a mock exam.
- Climb the levels: **remember** (state, define) → **apply** (compute, use the method) → **analyse**
  (explain why, compare, find the error) → **evaluate/create** (judge, design, prove, argue). A good set has
  all four; exams in quantitative subjects are mostly apply/analyse.
- Interleave: in mixed sets, do not group by topic. The student must recognise which method applies.

## Multiple choice

- 3–5 options, one clearly best. Distractors come from **real misconceptions** (sign errors, confusing
  necessary/sufficient, the neighbouring concept), never from jokes or obviously absurd options.
- Options parallel in length and grammar; avoid "all of the above" and "none of the above".
- `explain` says why the answer is right **and** what thinking leads to each tempting distractor.
- Randomise the position of the correct answer across the set.

## Find the error

- Show a short worked solution in which exactly one step is wrong, and ask which step fails and why
  (`mcq` with the steps as options, or `text` with a model answer). Studying incorrect examples next to
  correct ones sharpens the conditions under which a method applies.
- Take the error from a real misconception (the entries in `errors.md` are the best source), never
  from an arithmetic slip that teaches nothing.
- The `explain` field names the misconception and gives the corrected step.

## Numeric

- State units and the required precision in the prompt ("to 2 significant figures").
- `tolerance` is absolute: set it from the precision asked (0.005 for two decimals). For answers that
  depend on rounding of intermediate steps, widen it.
- Give the `solution` as 3–6 steps; each step a line the student could have written.

## Written (text)

- One focused question, answerable in 2–6 sentences. The model `answer` is what full marks look like.
- `keywords`: 2–5 concepts a full answer must mention; the page shows which ones the student used, as a
  self-check aid (not automatic grading).
- Humanities: ask for a claim + reason + textual evidence; the model answer shows that structure.

## Cloze and order

- Cloze blanks test key terms or values, not filler words; list accepted alternatives (spelling variants,
  synonyms the course accepts, singular/plural).
- Ordering: 4–7 items with one defensible order (steps of a mechanism, a proof, historical events).

## Hints and solutions

- Hints escalate: (1) point to the relevant idea, (2) name the method or first step, (3) give the
  intermediate result. Never put the answer in a hint.
- Solutions are worked examples: they show the reasoning, not just the result, and end with a check
  (units, special case, sanity check) where it fits.

## Difficulty calibration

- 1 = warm-up: one step, direct recall or a standard application.
- 2 = core: what the exam mostly asks; 2–4 steps, one decision about method.
- 3 = challenge: combines topics, unfamiliar framing, or a proof/argument.

## Marking schemes (exams)

- Allocate points to method, intermediate results and final answer separately, so partial credit is
  defined. Note errors that are penalised only once ("follow-through").
- For essays: criteria with point bands (thesis, use of evidence, counter-arguments, structure).
