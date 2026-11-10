# Learning science the toolkit is built on

Every skill applies these defaults unless the student's profile says otherwise. They are the
best-supported findings in cognitive and educational psychology (see the reading list at the end).

| Principle | What it means | Where the toolkit applies it |
|---|---|---|
| **Retrieval practice** | Recalling strengthens memory far more than re-reading. | Every explanation ends with 2–3 recall questions. Lessons include quick checks every 4–6 slides. Flashcards and the trainer are retrieval by design. |
| **Spacing** | Reviews spread over days beat one long session. | Leitner scheduling (1, 2, 4, 8, 16, 32 days) in `progress.json`; the planner books short reviews between study sessions. |
| **Interleaving** | Mixing problem types trains choosing the right method. | Mock exams and "mixed" trainer sets shuffle topics; the planner alternates modules. |
| **Worked examples, then fading** | Novices learn faster from studying solutions; support is removed as skill grows. | Trainer solutions reveal one step at a time; `practice` drills go from full example → completion problem → independent problem. |
| **Elaboration and self-explanation** | Asking "why?" and "how does this connect?" builds understanding. | `explain` Feynman mode; written questions with keyword checks. |
| **Concrete examples** | Abstract ideas stick when tied to several varied examples. | Every definition gets at least one example; lessons use the `definition` layout with `example`. |
| **Dual coding** | Words plus visuals beat words alone (when the visual carries meaning). | `visual-lesson` diagram slides; sheets use tables and formulas. Decorative images are avoided. |
| **Calibration (metacognition)** | Students over-estimate what they know. Testing shows the truth. | Confidence is never used as a mastery signal; only results update mastery. The coach shows weak topics plainly. |
| **Desirable difficulty** | Effortful recall is good; failure with feedback is part of learning. | Hints are graded (nudge → method → near-answer). "Again" cards come back in the same session. |

## Defaults for producing material

- **Atomic units.** One idea per card, one claim per bullet, one step per derivation row.
- **Ask before you tell.** When a student asks to "learn X", give a short orientation, then a question.
- **Short sessions.** Default to the profile's `session_minutes` (45). A session has a goal, retrieval,
  new material, and a closing check.
- **Errors are data.** Wrong answers go to `errors.md` with the misconception, not just "wrong".
- **No learning-styles matching.** "Visual/auditory learner" tailoring is not supported by evidence.
  Respect stated *preferences* (format, length), but choose methods by content.

## Reading list (for the resources skill and curious students)

- Dunlosky et al. (2013), *Improving Students' Learning With Effective Learning Techniques*, Psychological Science in the Public Interest 14(1).
- Roediger & Karpicke (2006), *Test-Enhanced Learning*, Psychological Science 17(3).
- Cepeda et al. (2006), *Distributed practice in verbal recall tasks*, Psychological Bulletin 132(3).
- Rohrer & Taylor (2007), *The shuffling of mathematics problems improves learning*, Instructional Science 35.
- Sweller, van Merriënboer & Paas (1998), *Cognitive Architecture and Instructional Design*, Educational Psychology Review 10.
- Brown, Roediger & McDaniel (2014), *Make It Stick*, Harvard University Press.
- Pashler et al. (2008), *Learning Styles: Concepts and Evidence*, Psychological Science in the Public Interest 9(3).
