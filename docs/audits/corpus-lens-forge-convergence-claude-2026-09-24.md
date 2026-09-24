# corpuslens report

> This run read 3040 events (dropped 140643: 140544 not a turn by design, 99 that should have been a turn and failed; counted not hidden), ran 8 process analyzers under profile 'default', and was granted nothing beyond process analysis. No absolute calendar date, timezone, or filename left the wall; relative day and within-day tempo did — these preserve weekly cadence, and on a day a single thread spans for many hours they loosely bound the local time-of-day (never the timezone or the date). This run's authorship classifier reads the operator-role turns as human (83.9% of 827 classified operator-role turns read as human (>= the 80% threshold for a predominant call)) — an inferred belief, not a verified fact, and it can be wrong; nothing in this report proves who actually typed a turn, and every 'you'/'your' below should be read as shorthand for that belief.

> This report's battery fully answers two of GRADING.md's ten questions — question 1 (where your intent arrives) and question 2 (who writes the code) — and partly answers two more: question 3 (your deliberation share, but not whether those prompts pull longer, more structured responses) and question 4 (resumption gaps and thread span, but not a 30-day bucket, per-day/month counts, or whether a return was productive). 4 of the battery's 8 analyzers (authorship_mix, clarification_pull, signature_plurality, tempo) answer none of the ten numbered questions directly and are reported here as a supporting signal, not a rubric answer — each section below says exactly which case it is. Questions 5-8 (can a stored claim be demoted; when a negative result was last recorded; whether an agent can grant itself anything; whether checks fail closed) and questions 9-10 (whether your timestamps are a fingerprint; who carries the continuity across a session gap) are not corpus-measurable from session logs at all — GRADING.md gives each of those its own manual test, not a number this tool computes.

## What this run found

- **steering_density** — 97.5% of your prompt turns arrive mid-task rather than in a session's opening prompt.
- **thread_shape** — 17 thread(s), picked back up 0 time(s) after a gap of 2 days or more; at the busiest, 4 ran on the same day.
- **composition_mix** — You authored code in 2.6% of your prompts and referred to existing code in 3.4%; 2.8% deliberate before building.
- **clarification_pull** — The machine asked a clarifying question you then answered in 0.72% of its turns.
- **tempo** — A median 61.8s passes before each of your prompts — measured from whatever the thread recorded last, usually the machine's reply, not from your previous prompt (measurable on 97.2% of eligible turns).
- **thread_span** — Half your threads span 1 day(s) or less; the longest stays open across 2.
- **authorship_mix** — Of your operator-role turns, 83.9% look human-authored, 0.6% look agent-authored, and 15.5% are unresolved.
- **signature_plurality** — This corpus's operator-role turns show 2 distinct authoring signatures (opaque index only — this does not say which one is you, and it never distinguishes between two humans).

## steering_density

**97.5% of your prompt turns arrive mid-task rather than in a session's opening prompt.**

*GRADING.md: question 1.*

Out of operator prompt turns with >=12 characters (de-injected); n = 686.

Reference:
- `measured_director`: 96.8% mid-task, 26-turn work sessions — the author's own corpus (N=1); a gap from this reference is a gap from one person, not a population.
- `swe_bench_tau_bench`: 0% mid-task by construction

*Until someone runs `corpuslens label` and `corpuslens score` on this corpus, there is no way to know how much of that N=1 gap is the operator and how much is the classifier's own error.*

```json
{
  "denominator": "operator prompt turns with >=12 characters (de-injected)",
  "analyzer_version": 1,
  "n": 686,
  "sessions": 17,
  "total_turns": 686,
  "mid_task_share_pct": 97.5,
  "single_turn_sessions_pct": 5.9,
  "single_turn_sessions_pct_denominator": "sessions (not turns) \u2014 this rate is per-session",
  "work_session_median_turns": 41.5,
  "opener_median_words": 3,
  "followup_median_words": 11
}
```

## thread_shape

**17 thread(s), picked back up 0 time(s) after a gap of 2 days or more; at the busiest, 4 ran on the same day.**

*GRADING.md: part of question 4 — it counts resumption gaps in disjoint 2-7/7-14/14+ day buckets and same-day concurrency, but GRADING.md also asks for a >=30-day bucket and monthly counts, and for whether a resumption was a PRODUCTIVE return, which this does not check.*

Out of threads with >=1 active day (relative days only); n = 17.

*Small sample (n = 17): read the direction, not the decimal.*

```json
{
  "denominator": "threads with >=1 active day (relative days only)",
  "analyzer_version": 1,
  "n": 17,
  "threads": 17,
  "resumptions_2to6d": 0,
  "resumptions_7to13d": 0,
  "resumptions_ge14d": 0,
  "buckets": "disjoint day-gap ranges \u2014 sum them for total resumptions >=2d",
  "concurrency_median": 1,
  "concurrency_peak": 4,
  "note": "derived from log-field dates only; content dates once inflated this 10x. Day gaps are relative \u2014 they preserve weekly cadence but not calendar dates."
}
```

## composition_mix

**You authored code in 2.6% of your prompts and referred to existing code in 3.4%; 2.8% deliberate before building.**

*GRADING.md: question 2 (authored_code_pct / code_ref_pct, against the domain population — GRADING.md's stated method exactly); and part of question 3 for delib_pct — it reports the discussion-channel share but not whether those prompts pull longer, more structured responses, which question 3 also asks for.*

Out of operator prompt turns with >=12 characters (de-injected); n = 686.

Against the reference: authored 2.6% vs 14.5% (below), code-ref 3.4% vs 36.0% (below), deliberation 2.8% vs 3.2% (near) — WildChat coding population.

> above the coding population on authored/read-ref = you bring the code to the machine; well below it = the machine holds the code and you direct. delib above your domain population = you summon the teaching surface on purpose.

Reference:
- `wildchat_coding_population`: {"authored_pct": 14.5, "read_ref_pct": 36.0, "delib_pct": 3.2}
- `wildchat_all`: {"authored_pct": 3.0, "read_ref_pct": 12.3, "delib_pct": 6.6}
- `oasst_general_chat`: {"delib_pct": 7.3}
- `measured_director_n1`: {"authored_pct": 6.3, "read_ref_pct": 18.3, "delib_pct": 5.2} — the author's own corpus (N=1); a gap from this reference is a gap from one person, not a population.

*Until someone runs `corpuslens label` and `corpuslens score` on this corpus, there is no way to know how much of that N=1 gap is the operator and how much is the classifier's own error.*

```json
{
  "denominator": "operator prompt turns with >=12 characters (de-injected)",
  "analyzer_version": 1,
  "n": 686,
  "n_turns": 686,
  "authored_code_pct": 2.6,
  "code_ref_pct": 3.4,
  "delib_pct": 2.8,
  "median_words": 10.0
}
```

## clarification_pull

**The machine asked a clarifying question you then answered in 0.72% of its turns.**

*GRADING.md: none of GRADING.md's numbered questions directly — closest is question 3, but question 3 is about YOUR prompts opening a discussion channel; this measures the machine asking and you answering, the reverse direction, which GRADING.md does not pose as a question.*

Out of machine response turns (>=12 chars); n = 2209.

Reference:
- `measured_cli`: 3.4 — the author's own corpus (N=1); a gap from this reference is a gap from one person, not a population.
- `measured_cursor_note`: 2.47 — measured elsewhere; NOT computable here (cursor logs carry no assistant turns), shown for context only — the author's own corpus (N=1); a gap from this reference is a gap from one person, not a population.

*Until someone runs `corpuslens label` and `corpuslens score` on this corpus, there is no way to know how much of that N=1 gap is the operator and how much is the classifier's own error.*

```json
{
  "denominator": "machine response turns (>=12 chars)",
  "analyzer_version": 1,
  "n": 2209,
  "assistant_turns": 2209,
  "clarification_forks_pct": 0.72
}
```

## tempo

**A median 61.8s passes before each of your prompts — measured from whatever the thread recorded last, usually the machine's reply, not from your previous prompt (measurable on 97.2% of eligible turns).**

*GRADING.md: none of GRADING.md's numbered questions directly — thematically closest to question 1 (arrival) and question 4 (thread rhythm), but neither asks for second/minute-level inter-turn gaps; this is a supporting signal, not one of the ten measurements.*

Out of operator prompt turns (>=12 chars) carrying a within-day tempo delta; n = 667.

> high burst share = you steer in volleys, several corrections per thought; high resumed share = you leave the machine running and return. This is the rate at which YOUR turns arrive — on a cursor-store corpus it would be the machine's step rate, which is why that corpus reports no tempo at all.

```json
{
  "denominator": "operator prompt turns (>=12 chars) carrying a within-day tempo delta",
  "analyzer_version": 1,
  "n": 667,
  "n_deltas": 667,
  "eligible_turns": 686,
  "delta_coverage_pct": 97.2,
  "coverage_note": "uncovered turns open a thread, sit after a censored midnight crossing, or come from a corpus with no prompt clock \u2014 never imputed",
  "median_gap_s": 61.8,
  "p25_gap_s": 29.0,
  "p75_gap_s": 120.0,
  "burst_pct": 49.0,
  "burst_threshold_s": 60.0,
  "resumed_pct": 1.5,
  "resumed_threshold_s": 1800.0
}
```

## thread_span

**Half your threads span 1 day(s) or less; the longest stays open across 2.**

*GRADING.md: part of question 4 — span and density are the complement to thread_shape's resumption gaps, but GRADING.md's question 4 also asks for per-day/month activity counts and whether a return was productive, neither of which this reports.*

Out of threads with >=1 event (relative days only); n = 17.

*Small sample (n = 17): read the direction, not the decimal.*

> density near 1.0 = threads are worked and closed; a low median density with a long median span = you keep many threads open across weeks and return to them. Spans are relative-day differences: they preserve weekly cadence and carry no calendar date.

```json
{
  "denominator": "threads with >=1 event (relative days only)",
  "analyzer_version": 1,
  "n": 17,
  "threads": 17,
  "single_day_threads_pct": 58.8,
  "median_span_days": 1,
  "max_span_days": 2,
  "median_active_days": 1,
  "median_density": 1.0,
  "density_definition": "active days / (last day - first day + 1), per thread, median of that"
}
```

## authorship_mix

**Of your operator-role turns, 83.9% look human-authored, 0.6% look agent-authored, and 15.5% are unresolved.**

*GRADING.md: none of GRADING.md's numbered questions directly — question 1 ('where does your intent arrive') presupposes the operator role is a person; this analyzer checks that precondition rather than answering a numbered question of its own.*

Out of operator-role turns (AuthorClass.OPERATOR prompt events); n = 827.

> a high agent_pct on a corpus you believed was one person means the operator role is not consistently you — an automated dispatch loop, a benchmark harness, or a session mixing your own turns with agent prompts you dispatched. A high unknown_pct is the expected default, not a warning sign: this classifier is built to undercount rather than assert a label it cannot support (see corpuslens/authorship.py). This is not, and cannot become, a claim about WHICH person authored a turn.

```json
{
  "denominator": "operator-role turns (AuthorClass.OPERATOR prompt events)",
  "analyzer_version": 1,
  "n": 827,
  "human_pct": 83.9,
  "agent_pct": 0.6,
  "unknown_pct": 15.5,
  "human_n": 694,
  "agent_n": 5,
  "unknown_n": 128
}
```

## signature_plurality

**This corpus's operator-role turns show 2 distinct authoring signatures (opaque index only — this does not say which one is you, and it never distinguishes between two humans).**

*GRADING.md: none of GRADING.md's numbered questions — the rubric's ten questions assume one operator directing one machine (see IDEAS.md, 'Process when the work is delegated'); this analyzer checks that precondition rather than answering a numbered question, and is scoped to say nothing about people — only how many distinct operator-role signatures produced the corpus.*

Out of operator prompt turns with >=12 characters (de-injected), classified by the authorship contract (authorship.py); n = 686.

> 1 signature = this corpus's operator role reads as one uniform authoring process. More than 1 means it is not — it stopped after the first split it was confident about, so treat this count as a floor, never a ceiling: a real third or fourth source can hide inside a signature this analyzer merged away, but it will never invent one that is not there. It does not and cannot say whether an extra signature is a second agent or a second person — that question is out of scope for this tool by design (README: owner == subject).

```json
{
  "denominator": "operator prompt turns with >=12 characters (de-injected), classified by the authorship contract (authorship.py)",
  "analyzer_version": 1,
  "n": 686,
  "signature_count": 2,
  "signatures": [
    {
      "index": 0,
      "share_of_turns_pct": 0.7,
      "typical_length_band": "long"
    },
    {
      "index": 1,
      "share_of_turns_pct": 80.6,
      "typical_length_band": "medium"
    }
  ],
  "unclassified_turns_pct": 18.7
}
```

*Numbers are heuristics plus your own eyes: spot-check before citing them. Reference points are one measured N=1 plus public population aggregates.*