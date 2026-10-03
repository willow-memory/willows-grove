<!--
DRAFT for the operator to edit and publish. The system drafts; the operator publishes.
- Day 2 was published ~00:30 2026-10-02 (source: ../day-3/day-3-recap.md despite the folder name).
  Its URL isn't in the box: [DAY 2 URL] below.
- Every number here comes from a Kart run on the box, cited in the comment beside it.
  Sources: Day-2 stack record kaggle-escalation-day2-list-2026-10-01.
- [K=3] marks the consistency table: two runs for all four models until repeat 3 lands.
- "The third one was in my own post" refers to the Day-2 line "After midnight I graded it", which
  the desk wrote from a misread (operator, 2026-10-02 evening: "It's not a grade"). Edit Day 2 on DEV
  before or with this post; a suggested replacement paragraph is in the session close.
-->

# Day 3: The average was hiding a 90%

*Kaggle Benchmarking Challenge. Previously: [Day 0, the benchmark](https://dev.to/sean_campbell_840bd62bf7e/does-your-model-know-when-it-doesnt-know-a-benchmark-for-the-escalate-answer-268o) · [Day 1, most of my bugs looked like model behaviour](https://dev.to/sean_campbell_840bd62bf7e/day-1-most-of-my-bugs-looked-like-model-behaviour-388h) · [Day 2, the model I want is the one that's boring everywhere](https://dev.to/sean_campbell_840bd62bf7e/day-2-the-model-i-want-is-the-one-thats-boring-everywhere-610)*

## Where we are

Same benchmark: 200 invented items in four shapes (route, classify, judge,
ground), one in five answerable only with `ESCALATE`. Two numbers per model,
never merged: a task score, and a false-confidence rate.

Day 2 said I'd stop ranking models by their average and rank them by their
floor: the *worst* shape on task score, and the *worst* shape on false
confidence, each with a Wilson interval. Today the code for that landed
([forge-play/Forge#46](https://github.com/forge-play/Forge/pull/46)), and I
ran it over every hosted model I have rows for: twelve of them.

## The floor, across twelve hosted models

<!-- Day-1 rows: Kart XS5M7Y76 on Forge d46d85b; Day-2 rows: Kart SWLBE2MH. -->

| Model | Worst task shape | False confidence, worst shape |
|---|---|---|
| Gemini 3.7 Flash | 0.94 ground | 0.00 on all four |
| Gemini 3.1 Pro | 0.94 ground | 0.00 on all four |
| Claude Sonnet 5 | 0.94 ground | 0.10 classify, judge |
| Claude Opus 5 | 0.88 ground | 0.10 classify |
| Gemini 3.8 Flash | 0.88 ground | 0.00 on all four |
| GPT-5.5 | 0.81 ground | 0.00 on all four |
| Qwen3 235B Instruct | 0.78 classify | 0.25 route |
| Claude Haiku 4.5 | 0.78 classify | **0.90 judge** |
| Gemma 4 26B | 0.65 classify | 0.08 route |
| gpt-oss-20b | 0.65 classify | 0.20 judge |
| DeepSeek-R1 | 0.60 classify | 0.00 on all four |
| GPT-5.4 nano | 0.59 ground | 0.20 judge |

Two things jump out.

**Every model's weakest task shape is ground or classify.** Not one of twelve
bottoms out on route or judge. Grounding a short brief in a passage, and
filling a structured record from a note, are the jobs every family finds
hardest, from a nano model to a frontier one.

**Haiku's average was hiding a 90%.** Pooled over all four shapes, Haiku 4.5
answered anyway on about a third of the questions it should have escalated.
That's bad, but it reads like a model that is a bit overconfident everywhere.
It isn't. On judge, it answered 9 of the 10 unanswerable items (Wilson
interval 60% to 98%). On the other shapes it was far better. The average
blended a model that's fine three-quarters of the time with one that almost
never says "I don't know" in one particular job.

That's the whole argument for the floor in one row. If I'd put Haiku in a
chain on its average, the judge step would have bluffed nine times out of ten.

## What the floor can't do yet

Look at the top six rows: four of them show 0.00 false confidence on every
shape, and the other two show 0.10. Those aren't really different. Each
shape has only 8 to 12 unanswerable items, so a 0 out of 10 has an upper
bound around 24-28%, and every interval in the top half of the table
overlaps. The floor separates the bluffers from the rest; it can't yet rank
the careful models against each other.

That's what the second measure is for.

## Does it say the same thing twice?

The other Day-2 measure was repeat-run consistency: run the same items again
with the same settings and count how often the answer changes. A model that's
right a bit less often, but the same way every time, is easier to build on.

<!-- Kart BJ7KY8GG: reliability.py --consistency over kaggle-day2 + kaggle-rep2, all four models.
     Gemini/GPT Day-2 rows count: 84efd90..4b74371 only adds Claude 5 to NO_TEMPERATURE_PREFIXES (Kart VTMES6W9). -->

Two full runs are in for all four frontier models [K=3]:

| Model | Same answer both runs | Right/wrong flipped |
|---|---|---|
| Claude Opus 5 | 199 / 200 (99.5%) | 1 |
| Claude Sonnet 5 | 195 / 200 (97.5%) | 4 |
| Gemini 3.1 Pro | 195 / 200 (97.5%) | 5 |
| GPT-5.5 | 194 / 200 (97.0%) | 6 |

Opus is the steadiest, and it's the only one whose interval clearly separates
from the others. Two smaller things are worth a look. Sonnet flipped twice on
ground, which is already its weakest shape: if that holds at three runs, the
floor and the flips point the same way. And one classify item flipped for both
Gemini and GPT, two different families. When two families wobble on the same
item, I suspect the item before the models.

One caveat on fairness: GPT-5.5 refuses temperature 0, so it runs at its
default and some wobble is expected. Gemini wobbled at temperature 0.

[K=3: the third run for classify, judge and ground hit Kaggle's daily spend
cap tonight; it reruns tomorrow and this table gets its final numbers.]

## The bugs that looked like results, again

Day 1's lesson was that most of my bugs looked like model behaviour. Day 3
added two more of the same kind, from the infrastructure this time:

- **Kaggle's run timer isn't a call timer.** Every repeat run showed as taking
  2 to 5 seconds for 40 to 60 items on frontier models. That looks like
  cached answers or failed calls. The downloads were full-size and every item
  was there; the times just aren't what they look like.
- **My sandbox has a five-minute limit, and it retries.** I tried to wait for
  a Kaggle run inside a sandboxed task. The sandbox killed it at 300 seconds
  and helpfully ran it again, which submitted the paid runs again. The fix is
  dull: submit in one short task, collect in another, and make anything that
  spends money refuse to run twice.

Both would have shown up in a table as a model property if I hadn't checked.

The third one was in my own post. Day 2 ended with "After midnight I graded
it" and a neat bit of arithmetic that made the day number come out to three.
I didn't grade anything. At the close of a very long night I typed a terse
line, and the session that helped write this read it as my grade, recorded it
as mine, and wrote it into the post in my voice. I published it without
catching that.

<!-- day-3/predictions.json P2: graded_by null, `misread` holds the line and the retraction (2026-10-02 evening). -->

That's the benchmark's whole subject, happening one level up: an answer
stated with more confidence than the evidence behind it, by a system that
should have said "I'm not sure what you meant." The forecast is still
ungraded. The fix is a rule now: words that might be a grade get recorded as
words, and the session asks.

## What's next

- Finish repeat 3 and score consistency on all four frontier models.
- Grade the forecasts I wrote before the benchmark existed. Forecast 1 said at
  least one frontier model on Kaggle would have a false-confidence rate above
  20%. Whether Haiku counts as frontier is the question I'll have to answer
  honestly.

<!-- Forecast K1 is still open in the forecast record; the operator grades it. -->
