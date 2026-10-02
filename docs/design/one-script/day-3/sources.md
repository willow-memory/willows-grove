# Contest posts: what the box holds (2026-10-02)

**Occasion:** DEV × Kaggle Benchmarking Challenge. Submissions close
2026-10-11 23:59 PDT.

## Found on the open web (not previously in the box)

| Post | URL |
|---|---|
| Day 0: "Does your model know when it doesn't know? A benchmark for the ESCALATE answer" | https://dev.to/sean_campbell_840bd62bf7e/does-your-model-know-when-it-doesnt-know-a-benchmark-for-the-escalate-answer-268o |
| Day 1: "Day 1: Most of My Bugs Looked Like Model Behaviour" | https://dev.to/sean_campbell_840bd62bf7e/day-1-most-of-my-bugs-looked-like-model-behaviour-388h |

No Day 2 post was found, and neither was a public Kaggle benchmark page. A
broader search on 2026-10-02 did find an older post,
[Willow](https://dev.to/sean_campbell_840bd62bf7e/willow-local-first-ai-stack-phone-reads-desktop-kb-over-lan-no-cloud-relay-189c),
from the same account (joined DEV 2026-04-26), and the challenge page,
[dev.to/challenges/kaggle-2026-09-23](https://dev.to/challenges/kaggle-2026-09-23).

**Day 0's date:** 2026-09-30, per a search summary.

**PRs since then:** 55 across 6 repos. See `prs-since-day-0.md`.

## What couldn't be read, and why

- **The page text is missing.** `dev.to` is denied by this environment's
  network policy (`EGRESS_BLOCKED`), so neither post was read in full. To fix
  it, add `dev.to` to the environment's allowed domains.
- **Everything below is secondhand.** It comes from search-engine summaries
  of the two posts, not from the posts themselves. Its standing is
  unattested; check it against the posts before quoting.
  - 200 items in four shapes (route 60, classify 50, judge 50, ground 40), with
    20% of each shape answerable only by `ESCALATE`. This matches the Forge
    fixtures at `7c67f55`.
  - Day 1's local ladder: 8 models × 200 items, temperature 0, on a laptop.
  - The only local model that escalated on a large share of what it couldn't
    answer was qwen3.5 (9.7B).
  - "Every hosted model's false-confidence interval sits entirely below every
    local model's except qwen3.5's." The highest hosted upper bound was
    haiku's 54.2%, and the lowest local lower bound was 62.5%.
  - The local false-confidence range was roughly 37.5% to 95%. That's a
    search summary's paraphrase, so it's the least reliable line here.

## In the box already

- The plan: `willows-grove/governance/proposals/2026-09-30-kaggle-escalation-benchmark.md`
  (including the 2026-10-02 amendment: floor and consistency)
- The code: `Forge/benchmarks/escalation/` (head `7c67f55`, 2026-09-30)
- Staged, not landed: `session-flow/scripts/rel/reliability.py` and its
  tests, which wait for the day-two run
