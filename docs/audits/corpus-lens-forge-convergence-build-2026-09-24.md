# corpuslens report

> This run read 496 events (dropped 4877: 4849 not a turn by design, 28 that should have been a turn and failed; counted not hidden), ran 8 process analyzers under profile 'default', and was granted nothing beyond process analysis. No absolute calendar date, timezone, or filename left the wall; relative day and within-day tempo did — these preserve weekly cadence, and on a day a single thread spans for many hours they loosely bound the local time-of-day (never the timezone or the date). This run's authorship classifier reads the operator-role turns as a mix of human and agent, not one human (neither class reaches the 80% threshold (64.5% human, 0.2% agent of 496 turns) — this run's operator role mixes both) — an inferred belief, not a verified fact, and it can be wrong; nothing in this report proves who actually typed a turn, and every 'you'/'your' below should be read as shorthand for that belief.

> This report's battery fully answers two of GRADING.md's ten questions — question 1 (where the operator role's intent arrives) and question 2 (who writes the code) — and partly answers two more: question 3 (the operator role's deliberation share, but not whether those prompts pull longer, more structured responses) and question 4 (resumption gaps and thread span, but not a 30-day bucket, per-day/month counts, or whether a return was productive). 4 of the battery's 8 analyzers (authorship_mix, clarification_pull, signature_plurality, tempo) answer none of the ten numbered questions directly and are reported here as a supporting signal, not a rubric answer — each section below says exactly which case it is. Questions 5-8 (can a stored claim be demoted; when a negative result was last recorded; whether an agent can grant itself anything; whether checks fail closed) and questions 9-10 (whether the operator role's timestamps are a fingerprint; who carries the continuity across a session gap) are not corpus-measurable from session logs at all — GRADING.md gives each of those its own manual test, not a number this tool computes.

## What this run found

- **steering_density** — 84.9% of the operator role's prompt turns arrive mid-task rather than in a session's opening prompt.
- **thread_shape** — 68 thread(s), picked back up 0 time(s) after a gap of 2 days or more; at the busiest, 22 ran on the same day.
- **composition_mix** — The operator role authored code in 2.4% of the operator role's prompts and referred to existing code in 13.3%; 1.1% deliberate before building.
- **clarification_pull** — not computable on this corpus. no machine responses in corpus — this analyzer needs a claude-code corpus; the cursor adapter is prompt-only (no assistant turns)
- **tempo** — not computable on this corpus. no within-day tempo deltas in this corpus — every operator turn opens a thread, follows a censored midnight crossing, or comes from a store that does not clock prompts (cursor-store). Tempo is not computable here, and is not guessed at.
- **thread_span** — Half the operator role's threads span 1.0 day(s) or less; the longest stays open across 3.
- **authorship_mix** — Of the operator role's operator-role turns, 64.5% look human-authored, 0.2% look agent-authored, and 35.3% are unresolved.
- **signature_plurality** — This corpus's operator-role turns show 2 distinct authoring signatures (opaque index only — this does not say which one is the operator role, and it never distinguishes between two humans).

## steering_density

**84.9% of the operator role's prompt turns arrive mid-task rather than in a session's opening prompt.**

*GRADING.md: question 1.*

Out of operator prompt turns with >=12 characters (de-injected); n = 451.

*Reference withheld: this run's subject is inferred as 'mixed' (neither class reaches the 80% threshold (64.5% human, 0.2% agent of 496 turns) — this run's operator role mixes both). Every reference point this battery has — the measured N=1 human director, and the WildChat/OASST population aggregates — is itself a human reference point; comparing a non-human (or not-confidently-human) subject against one would be a category error this tool declines to make silently. No agent reference point is substituted, because none has been measured — 'no comparable reference exists for this subject' is itself the finding here, not a gap to paper over.*

```json
{
  "denominator": "operator prompt turns with >=12 characters (de-injected)",
  "analyzer_version": 1,
  "n": 451,
  "sessions": 68,
  "total_turns": 451,
  "mid_task_share_pct": 84.9,
  "single_turn_sessions_pct": 67.6,
  "single_turn_sessions_pct_denominator": "sessions (not turns) \u2014 this rate is per-session",
  "work_session_median_turns": 9.5,
  "opener_median_words": 42.0,
  "followup_median_words": 19
}
```

## thread_shape

**68 thread(s), picked back up 0 time(s) after a gap of 2 days or more; at the busiest, 22 ran on the same day.**

*GRADING.md: part of question 4 — it counts resumption gaps in disjoint 2-7/7-14/14+ day buckets and same-day concurrency, but GRADING.md also asks for a >=30-day bucket and monthly counts, and for whether a resumption was a PRODUCTIVE return, which this does not check.*

Out of threads with >=1 active day (relative days only); n = 68.

```json
{
  "denominator": "threads with >=1 active day (relative days only)",
  "analyzer_version": 1,
  "n": 68,
  "threads": 68,
  "resumptions_2to6d": 0,
  "resumptions_7to13d": 0,
  "resumptions_ge14d": 0,
  "buckets": "disjoint day-gap ranges \u2014 sum them for total resumptions >=2d",
  "concurrency_median": 6,
  "concurrency_peak": 22,
  "note": "derived from log-field dates only; content dates once inflated this 10x. Day gaps are relative \u2014 they preserve weekly cadence but not calendar dates."
}
```

## composition_mix

**The operator role authored code in 2.4% of the operator role's prompts and referred to existing code in 13.3%; 1.1% deliberate before building.**

*GRADING.md: question 2 (authored_code_pct / code_ref_pct, against the domain population — GRADING.md's stated method exactly); and part of question 3 for delib_pct — it reports the discussion-channel share but not whether those prompts pull longer, more structured responses, which question 3 also asks for.*

Out of operator prompt turns with >=12 characters (de-injected); n = 451.

Against the reference: authored 2.4% vs 14.5% (below), code-ref 13.3% vs 36.0% (below), deliberation 1.1% vs 3.2% (near) — WildChat coding population.

> above the coding population on authored/read-ref = the operator role bring the code to the machine; well below it = the machine holds the code and the operator role direct. delib above the operator role's domain population = the operator role summon the teaching surface on purpose.

*Reference withheld: this run's subject is inferred as 'mixed' (neither class reaches the 80% threshold (64.5% human, 0.2% agent of 496 turns) — this run's operator role mixes both). Every reference point this battery has — the measured N=1 human director, and the WildChat/OASST population aggregates — is itself a human reference point; comparing a non-human (or not-confidently-human) subject against one would be a category error this tool declines to make silently. No agent reference point is substituted, because none has been measured — 'no comparable reference exists for this subject' is itself the finding here, not a gap to paper over.*

```json
{
  "denominator": "operator prompt turns with >=12 characters (de-injected)",
  "analyzer_version": 1,
  "n": 451,
  "n_turns": 451,
  "authored_code_pct": 2.4,
  "code_ref_pct": 13.3,
  "delib_pct": 1.1,
  "median_words": 21
}
```

## clarification_pull

**Not computable on this corpus.** no machine responses in corpus — this analyzer needs a claude-code corpus; the cursor adapter is prompt-only (no assistant turns)

Denominator would be: machine response turns (>=12 chars).

GRADING.md: none of GRADING.md's numbered questions directly — closest is question 3, but question 3 is about YOUR prompts opening a discussion channel; this measures the machine asking and you answering, the reverse direction, which GRADING.md does not pose as a question.

## tempo

**Not computable on this corpus.** no within-day tempo deltas in this corpus — every operator turn opens a thread, follows a censored midnight crossing, or comes from a store that does not clock prompts (cursor-store). Tempo is not computable here, and is not guessed at.

Denominator would be: operator prompt turns (>=12 chars) carrying a within-day tempo delta.

GRADING.md: none of GRADING.md's numbered questions directly — thematically closest to question 1 (arrival) and question 4 (thread rhythm), but neither asks for second/minute-level inter-turn gaps; this is a supporting signal, not one of the ten measurements.

## thread_span

**Half the operator role's threads span 1.0 day(s) or less; the longest stays open across 3.**

*GRADING.md: part of question 4 — span and density are the complement to thread_shape's resumption gaps, but GRADING.md's question 4 also asks for per-day/month activity counts and whether a return was productive, neither of which this reports.*

Out of threads with >=1 event (relative days only); n = 68.

> density near 1.0 = threads are worked and closed; a low median density with a long median span = the operator role keep many threads open across weeks and return to them. Spans are relative-day differences: they preserve weekly cadence and carry no calendar date.

```json
{
  "denominator": "threads with >=1 event (relative days only)",
  "analyzer_version": 1,
  "n": 68,
  "threads": 68,
  "single_day_threads_pct": 92.6,
  "median_span_days": 1.0,
  "max_span_days": 3,
  "median_active_days": 1.0,
  "median_density": 1.0,
  "density_definition": "active days / (last day - first day + 1), per thread, median of that"
}
```

## authorship_mix

**Of the operator role's operator-role turns, 64.5% look human-authored, 0.2% look agent-authored, and 35.3% are unresolved.**

*GRADING.md: none of GRADING.md's numbered questions directly — question 1 ('where does your intent arrive') presupposes the operator role is a person; this analyzer checks that precondition rather than answering a numbered question of its own.*

Out of operator-role turns (AuthorClass.OPERATOR prompt events); n = 496.

> a high agent_pct on a corpus the operator role believed was one person means the operator role is not consistently the operator role — an automated dispatch loop, a benchmark harness, or a session mixing the operator role's own turns with agent prompts the operator role dispatched. A high unknown_pct is the expected default, not a warning sign: this classifier is built to undercount rather than assert a label it cannot support (see corpuslens/authorship.py). This is not, and cannot become, a claim about WHICH person authored a turn.

```json
{
  "denominator": "operator-role turns (AuthorClass.OPERATOR prompt events)",
  "analyzer_version": 1,
  "n": 496,
  "human_pct": 64.5,
  "agent_pct": 0.2,
  "unknown_pct": 35.3,
  "human_n": 320,
  "agent_n": 1,
  "unknown_n": 175
}
```

## signature_plurality

**This corpus's operator-role turns show 2 distinct authoring signatures (opaque index only — this does not say which one is the operator role, and it never distinguishes between two humans).**

*GRADING.md: none of GRADING.md's numbered questions — the rubric's ten questions assume one operator directing one machine (see IDEAS.md, 'Process when the work is delegated'); this analyzer checks that precondition rather than answering a numbered question, and is scoped to say nothing about people — only how many distinct operator-role signatures produced the corpus.*

Out of operator prompt turns with >=12 characters (de-injected), classified by the authorship contract (authorship.py); n = 451.

> 1 signature = this corpus's operator role reads as one uniform authoring process. More than 1 means it is not — it stopped after the first split it was confident about, so treat this count as a floor, never a ceiling: a real third or fourth source can hide inside a signature this analyzer merged away, but it will never invent one that is not there. It does not and cannot say whether an extra signature is a second agent or a second person — that question is out of scope for this tool by design (README: owner == subject).

```json
{
  "denominator": "operator prompt turns with >=12 characters (de-injected), classified by the authorship contract (authorship.py)",
  "analyzer_version": 1,
  "n": 451,
  "signature_count": 2,
  "signatures": [
    {
      "index": 0,
      "share_of_turns_pct": 29.9,
      "typical_length_band": "long"
    },
    {
      "index": 1,
      "share_of_turns_pct": 70.1,
      "typical_length_band": "medium"
    }
  ],
  "unclassified_turns_pct": 0.0
}
```

*Numbers are heuristics plus the operator role's own eyes: spot-check before citing them. Reference points are one measured N=1 plus public population aggregates.*