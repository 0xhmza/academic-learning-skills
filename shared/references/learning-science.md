# Learning science the toolkit is built on

Every skill applies these defaults unless the student's profile says otherwise. They are among the
best-supported findings in cognitive and educational psychology (reading list at the end). Effect
sizes vary by study and setting; treat them as direction, not as guarantees.

## How memory is built

| Principle | What it means | Where the toolkit applies it |
|---|---|---|
| **Retrieval practice** (testing effect) | Recalling strengthens memory far more than re-reading. | Every explanation ends with 2–3 recall questions. Lessons include checks every 4–6 slides. Flashcards and the trainer are retrieval by design. |
| **Spacing** | Reviews spread over days beat one long session. | Leitner scheduling (1, 2, 4, 8, 16, 32 days) in `progress.json`; the planner books short reviews between study sessions. |
| **Successive relearning** | Recall an item correctly, then again in later sessions: retrieval and spacing combined. About three correct recalls across sessions give durable knowledge. | A card reaches the long intervals only after several correct recalls on different days; "Again" cards return in the same session; the coach recommends due reviews before new material. |
| **Interleaving** | Mixing problem types trains choosing the right method. | Mock exams and "mixed" trainer sets shuffle topics; the planner alternates modules. |
| **Pretesting** | Trying to answer before being taught improves learning of what follows, even when the attempt fails. | Lessons open with a prediction or recall question; `practice` offers a short diagnostic before a new topic. |

## How understanding is built

| Principle | What it means | Where the toolkit applies it |
|---|---|---|
| **Worked examples, then fading** | Novices learn faster from studying solutions; support is removed as skill grows. | Trainer solutions reveal one step at a time; lesson derivations give a reason per step; drills go from full example to completion problem to independent problem. |
| **Self-explanation** | Explaining to oneself why a step works beats re-reading it. | `recall` slides and written questions ask "why" and "what if"; `explain` has a Feynman check. |
| **Generative learning** | Learners understand more when they produce something: a summary, a map, a question, an explanation for someone else. | The coach ends sessions with a one-minute summary in the student's words; `explain` asks for teach-back; notes are saved as the student phrases them. |
| **Concrete examples and concreteness fading** | Start with a concrete case, move to the abstract rule. | Lessons show the source's example before its general statement; every definition gets an example. |
| **Engagement modes (ICAP)** | Interactive > constructive > active > passive: answering and explaining teach more than highlighting, which teaches more than reading. | Pages are built for doing: step-wise reveal, checks, graded hints, self-grading, results export. |
| **Productive failure** | Struggling with a problem before instruction can deepen later understanding, if feedback follows. | Hints are graded (nudge, method, near-answer); the full solution comes last. |
| **Error correction** | Confident errors, once corrected, are remembered especially well; errors without feedback are not. | Every wrong answer gets the reason and the fix; mistakes go to `errors.md` with the misconception named. |

## How material should be presented (multimedia learning)

These apply to self-paced pages. A lesson read alone needs its explanation as text on the page: the
advantage of spoken over written explanation holds for fast, system-paced presentations, not for
material the learner paces.

| Principle | What it means | Where the toolkit applies it |
|---|---|---|
| **Segmenting** | Learner-paced pieces beat one continuous stream. | One idea per slide, one claim per key press; the reader controls the pace. |
| **Signalling** | Cues that show the structure help: headings that state the point, highlights, summaries. | Statement titles, `section` slides, `takeaway` lines, highlighted diagram elements, the outline sidebar. |
| **Pre-training** | Know the names and parts before the process. | `definition` and `formula` (symbol by symbol) slides come before derivations. |
| **Spatial and temporal contiguity** | Put words next to the picture they describe, at the time it appears. | The explanation sits beside the visual; captions change with each step; labels are on the parts. |
| **Coherence** | Leave out interesting but irrelevant material. | No decorative images or filler slides; strict grounding keeps to the course. |
| **Personalisation** | Conversational wording ("you") teaches better than formal wording. | Explanations address the reader directly. |
| **Dual coding** | Words plus a meaningful visual beat words alone. | Plots, flows, grids and figures wherever the source has or describes one. |

## How a tutor should behave

Guidance for the conversational skills (explain, practice, study-coach), in line with the principles
Google's LearnLM work derived from learning science:

- **Keep the learner active**: ask, wait, let them try; do not lecture when a question would do.
- **Manage cognitive load**: one step at a time, in the course's notation, examples before generalities.
- **Adapt**: start from what the profile and results show; go back to a prerequisite when it is shaky.
- **Stimulate curiosity**: connect to the student's goals and to what comes next in the course.
- **Deepen metacognition**: ask for a confidence estimate before revealing an answer and compare it with
  the result; name what the student did well in their reasoning, not only the outcome.
- **Calibration**: students over-estimate what they know. Only results update mastery, never confidence.

## Defaults for producing material

- **Atomic units.** One idea per card, one claim per bullet, one step per derivation row.
- **Explain on the page.** Material is read without a presenter; keywords without sentences teach little.
- **Ask before you tell.** When a student asks to "learn X", give a short orientation, then a question.
- **Prerequisites first.** A weak topic that rests on a weaker one is repaired from the bottom.
- **Short sessions.** Default to the profile's `session_minutes` (45). A session has a goal, retrieval,
  new material, and a closing check.
- **Errors are data.** Wrong answers go to `errors.md` with the misconception, not just "wrong".
- **No learning-styles matching.** "Visual/auditory learner" tailoring is not supported by evidence.
  Respect stated *preferences* (format, length), but choose methods by content.

## Reading list (for the resources skill and curious students)

- Dunlosky et al. (2013), *Improving Students' Learning With Effective Learning Techniques*, Psychological Science in the Public Interest 14(1).
- Roediger & Karpicke (2006), *Test-Enhanced Learning*, Psychological Science 17(3).
- Cepeda et al. (2006), *Distributed practice in verbal recall tasks*, Psychological Bulletin 132(3).
- Rawson & Dunlosky (2011), *Optimizing schedules of retrieval practice for durable and efficient learning: How much is enough?*, Journal of Experimental Psychology: General 140(3).
- Rohrer & Taylor (2007), *The shuffling of mathematics problems improves learning*, Instructional Science 35.
- Richland, Kornell & Kao (2009), *The pretesting effect*, Journal of Experimental Psychology: Applied 15(3).
- Sweller, van Merriënboer & Paas (1998), *Cognitive Architecture and Instructional Design*, Educational Psychology Review 10.
- Renkl (2014), *Toward an instructionally oriented theory of example-based learning*, Cognitive Science 38(1).
- Chi et al. (1989), *Self-explanations: How students study and use examples in learning to solve problems*, Cognitive Science 13(2).
- Chi & Wylie (2014), *The ICAP Framework*, Educational Psychologist 49(4).
- Fiorella & Mayer (2016), *Eight ways to promote generative learning*, Educational Psychology Review 28.
- Kapur (2008), *Productive failure*, Cognition and Instruction 26(3).
- Butterfield & Metcalfe (2001), *Errors committed with high confidence are hypercorrected*, Journal of Experimental Psychology: Learning, Memory, and Cognition 27(6).
- Mayer (2021), *Multimedia Learning* (3rd ed.), Cambridge University Press.
- LearnLM Team, Google (2024), *LearnLM: Improving Gemini for Learning*, arXiv:2412.16429; the pedagogy principles are set out in the team's earlier report, arXiv:2407.12687 (section 4.3).
- Brown, Roediger & McDaniel (2014), *Make It Stick*, Harvard University Press.
- Pashler et al. (2008), *Learning Styles: Concepts and Evidence*, Psychological Science in the Public Interest 9(3).
