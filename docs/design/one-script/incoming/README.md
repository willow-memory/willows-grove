# Incoming: three outside passes, and what the one script took from them

*Added 2026-10-02 at the operator's word: "Add them in, in the way you best see
fit. I just your judgements,  at least as far as a draft goes." Everything in this
folder is agent-reported or third-party and unattested. Nothing here is sealed.*

| Pass | From | Where | Kept as |
|---|---|---|---|
| **Opus** | a Cowork session on Opus 5 that had read Draft 0.8 and the six canon documents, but **not** this PR | [`opus-2026-10-02/`](opus-2026-10-02/) | verbatim |
| **Haiku** | a Cowork session on Haiku 4.5, started cold, that read this PR's files but not the session record | [`haiku-2026-10-02/`](haiku-2026-10-02/) | verbatim (prose); the repo's formatter changed whitespace inside one Python code block |
| **The paper** | the operator's "Basins, Not Walls" (September 2026) | [`basins-not-walls.md`](basins-not-walls.md) | a pointer and a reading, not the PDF |

The files as received, by sha256/16:

| Hash | File |
|---|---|
| `b06497bf1cecdc7d` | Opus `2026-10-02-reachability-and-staleness.md` |
| `758b6e6b263a0415` | Haiku `proposal-heartbeat-and-loops.md` |
| `08a70231ca8fb60a` | Haiku `proposal-packet-stamp-chain.md` |
| `7c0bd2ef86321339` | Haiku `proposal-overnight-and-morning-screen.md` |
| `58bdc0ef9212c3e9` | Haiku `PROPOSALS-SUMMARY.md` |
| `bc9d8ec19f3b96b5` | the paper (PDF, not committed) |

## The Opus pass: six proposals against Draft 0.8

Its finding under all six: the constitution is rigorous about *what state* a
thing is in, and nearly silent about *how old* that state is and whether the
next state is *reachable*. Its first point is the operator as the one unchecked
risk (capacity and self-certification), answered by making the bottleneck
measurable rather than giving agents authority.

**Its citations were checked against the Grove's Draft 0.8:** II.3, X.4, V.4a,
the Independent Witness wording, the Appendix A sentence, and the canon files
in `governance/seed/canon/`. All hold. Only its estate-survey quote couldn't be
found in this repo.

| Opus | Against this PR's proposals | Judgment |
|---|---|---|
| **P4** Ground doesn't age; staleness is reported, not demoted | the freshness gate; pile hash drift; live files | **Two independent passes, one shape.** Theirs governs knowledge tiers, ours code and documents. Both belong. |
| **P6** VI.5: record the absence of dissent | our amendment VI.5 "No smoothing"; witnesses split first | **Two passes reached the same clause number.** Theirs is narrower and has a structural shadow. Prefer theirs. **Adopted in code.** |
| **P5** No verdict for a missing report | the reachability gate; reasons on failing rows | **This PR missed it.** It never applied the Appendix A distinction to the coverage report itself. **Adopted in code.** |
| **P3** Queue age as reported state | NEEDS YOU listed what's waiting, not how long | **This PR missed it.** **Adopted in code**, the second half only (as its own note suggests). The declared rate is the operator's number. |
| **P1** Canonical may be impossible to reach | `witnesses()` counts families | **This PR missed it.** With one witness per family (IV.2) and IV.3's non-repeat rule, Canonical needs three independent base models. A constitutional fix, not code. |
| **P2** Safe Mode can't trigger; a single-agent Hold | this session's demo story "The Last Door at Building 9" depends on an independent quorum declaring incapacity | **This PR missed it, and it undercuts that demo story.** A constitutional fix. The story should be revised to show the Hold. |
| **7th** a one-page exploded view, beside the constitution | the binding table moved out of the constitution; the one-box parts table | Same shape. A generated view, not law. |

**Recommended, not done:** record in the Casebook that two independent
passes converged on staleness and on VI.5. That's a governance act, so it's
left for the operator.

## The Haiku pass: three proposals and a summary, from the PR's files alone

It carried the shape well where the files were in front of it, and filled
gaps confidently where they weren't. Checked against the session record and
Draft 0.8:

- **Right:**
  - its operator quotes in the heartbeat proposal (your turns T84–T87 and
    T91, typos corrected)
  - the skeleton's facts (47 tests; the gaps list)
  - 3×7×13×23 = 6,279
  - the `b17:` counts (within one)
- **Wrong:**
  - **"the night has a budget" is attributed to the operator, but it's a
    model sentence.** The claims layer now catches this, using this file as
    the fixture.
  - ΔΣ=42 called undefined. Draft 0.8 resolved it on 2026-07-15 as the
    tamper-evidence seal.
  - Article XII called unwritten. XII.1–XII.3 exist.
  - Article XI called adversarial testing. XI is Constitutional Review; the
    adversarial tests are Appendix B.
  - V.4a called undrafted. It exists.
  - Draft 0.8 called not yet written in full.
  - "3 agree, 1 differs" treated as "differently", which smooths a split into
    agreement.
  - `WorkBeat` escalates every third ask of anything. The ladder counts the
    same procedure repeating.
  - A new `night_pool.py` file. The part already exists in `resolve`.
  - Proposed Trace IDs that collide: IV.3 is taken, and §0.5 is Article 0.
  - "17 open decisions". It lists 15, and 13 in its summary.
  - Proposal names P1–P7, which collide with predictions P1 and P2.

**Taken from it:** the defect it exposed in this PR's own quote checker. The
checker paired quote marks across code blocks and tables (18 rows on one
file, most of them code fragments). It now reads quotes in prose only (6 rows,
all real). Its packet stamp-chain draft is a usable first sketch for ΔΣ=42
between boxes, once corrected against the 0.8 definition.

## What changed in `onescript/` (6 new tests, 53 in all)

| From | Part | Change |
|---|---|---|
| Opus P3 | `reverse`, `view` | `backpressure`: the number of items waiting on the human and the oldest one's time. It's shown first in NEEDS YOU and authorises nothing. |
| Opus P5 | `boot`, `view` | `report`: "never" when no reconcile is on record. The screen says enforcement status is **unknown**, rather than omitting it. |
| Opus P6 | `reverse`, `view` | Every agreed claim carries `dissent: none recorded`, a fact on the row, not a quality. |
| Haiku | `gate` | Quotes are read in prose only: not inside code blocks, inline code or table rows. |

**Not in code yet:** staleness windows (P4's 180 days and P5's 30 days are
guesses, and the operator's numbers to set) and the Hold (P2), which is law
before it's code.
