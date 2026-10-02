# Proposal: The Overnight Pool and Morning Screen

**Status:** Agent-reported, unattested. For the operator's review and decision.

**Cites:** CONST-IV (Knowledge & Canon), CONST-XII (Resource Envelopes), §0.4 (Human authority), workflow.md §4 (Loops and heartbeat), next-pile.md §Overnight

**Amends:** None. This formalizes and extends the overnight processing concept mentioned in next-pile.md §Overnight and §Morning screen, adding concrete structure, verdicts, and operator controls.

---

## The Problem and the Shape

When a system runs at 3am with no one awake, it must handle **continuous verification without bottlenecking on the human**. The morning screen must show the operator what changed overnight, what disagreed, what needs their decision, and what can wait.

Tonight's batch processing (operator, 2026-10-02: "the night has a budget"):

1. Every 3B model family, from several families, runs one narrow job on a slice of the record
2. Python compares their answers
3. Different families count as separate witnesses; same family counts as one
4. The big runs (multi-model, through egress) happen only under standing grant
5. Stamps and hashes chain upward to the Ledger
6. Everything is compared against the record, never against the biggest model

---

## The Overnight Pool *(Part 5.1 of resolve.py)*

The overnight pool is a **standing, resource-bounded, family-diverse verification layer** that runs queries from a queue built during the day.

### Queue and Jobs

| Phase | What | When | Who feeds |
|-------|------|------|-----------|
| **Build** | A job is added to the overnight queue when a claim is witnessed (ratified or marked by a human) or when a model output needs cross-checking | Every turn, at resolution | `resolve.py`, `reverse.py`, human marks |
| **Run** | Each job runs a single, narrow check on a slice of the record (not the whole) | Starting ~0100, every 15 min | A 3B scheduler (`night_pool.py`) |
| **Compare** | Results from different families are collected and a disagreement report is built | After all jobs finish, ~0500 | Python in `night_pool.py` |
| **Yield** | The pool stops all new jobs and returns immediately if `presence()` returns True (human awake) | Every 5 min during Run | The scheduler |

### Job Types (Agent-Reported Examples)

1. **Quote verification** — Does the cited text match the source? (Check against the record and the pile)
2. **Citation check** — Does the claim cite what it touches? (Compare against CONST-I through -XIII)
3. **Witness agreement** — Do two independent witnesses agree on this fact? (Run a second model on it)
4. **Prediction grade** — Did the predicted path happen? How close? (Compare `predictions.json` to what actually occurred)
5. **Floor and consistency** — How did this model do on tasks of this type? (Run a benchmark snippet from Appendix B)
6. **Drift detection** — Have hashes in the pile changed since they were recorded? (3-way check: recorded, on disk, in the ledger)
7. **Escalation worthiness** — Has this been asked three times? Is it a pattern? (Count from the record)

### Resource Envelope *(Article XII)*

The overnight pool runs **inside a recorded resource envelope:**

| Resource | Limit | Default | Adjustable | Notes |
|----------|-------|---------|------------|-------|
| **CPU per job** | User-configurable wall time | 2 minutes | Yes, Operator Key | A job that hits the wall stops and yields to presence |
| **Total pool hours** | Budget per night, resets at 0100 | 4 hours | Yes, Operator Key | Jobs in the queue when the budget is spent are parked for the next night |
| **Models allowed** | Families to use, by standing grant | 3B tier (5 families) | Yes, Operator Key | Cloud models only when explicitly granted (egress, §0.4) |
| **Presence backoff** | How quickly to stop if human detected | 5 min check, full yield when true | Yes | Once presence is detected, no new jobs start; running jobs finish if they can |

The envelope is recorded at overnight start (operator-key sealed entry to the Ledger) and the actual usage is reconciled at morning (recorded entry with counts).

---

## Witness Counting and Verdicts

A verdict is a 4-level assessment, not binary:

| Level | Name | Meaning | Stamps on ledger |
|-------|------|---------|------------------|
| **1** | Satisfied | All witnesses agree; no drift or breaks | `overnight: satisfied` |
| **2** | Differently | Witnesses agree on substance, differ on detail or tiering | `overnight: differently (detail)` |
| **3** | Not Applicable | The check doesn't apply to this kind of claim (e.g., quote check on a prediction) | `overnight: not_applicable (reason)` |
| **4** | Failing | Witnesses disagree, or a check found a break | `overnight: failing (count: witnesses-differ; detail)` |

**Witness counting rule:**

- Same family (e.g., two Llama-2 runs) = one witness
- Different families (e.g., Llama + Mistral + Phi) = three independent witnesses
- Verdicts combine: "3 agree, 1 differs" = Differently verdict
- "2 agree, 2 differ on what 'agree' means" (e.g., different quote extracts of the same passage) = Differently with detail

**No human seal in verdicts.** Verdicts from overnight are unattested. Only the human's seal (recorded separately in the Ledger, never as an edit) upgrades a verdict to **Ratified** in canon (CONST-IV).

---

## The Morning Screen *(Part 6.1 of view.py)*

The morning screen is deterministically ordered, with no smoothing:

```
Morning Screen
==============
1. [NEEDS YOU] — only the operator can do these
   - Open turns from the previous session (B2 hard close)
   - Grant cards pending human decision
   - A law change since yesterday (amendment ratified, precedent flipped)
   - A sealed human mark that contradicts a witnessed claim
   
2. [DISAGREEMENTS] — witnesses don't agree
   - Failing verdicts first (highest disagreement)
   - For each: the check, which witnesses disagreed, the detail
   - Sort by severity (prediction wrong > quote mismatch > detail differ)
   
3. [AGREED, NOT SEALED] — witnessed but not human-sealed
   - Satisfied and Differently verdicts (levels 1-2)
   - For each: how many witnesses, which families, the claim
   - These are candidates for the human to seal into canon or mark "good for now"
   
4. [GRADES] — model performance
   - Prediction accuracy from yesterday (P1 vs. what happened)
   - Floor scores for each family (Appendix B tasks)
   - Consistency (how do the same models do on similar tasks?)
   - Outliers first (models that did worse than expected)
   
5. [QUIET] — counts only
   - X overnight jobs run, Y succeeded, Z parked (out of budget)
   - A claims verified, B checked, C escalation-patterns found
   - No claims broke the Ledger or found drift
   - Envelope reconciliation: Xh Ymin of 4h budget used
```

Each section is sorted deterministically (by timestamp, by claim ID, by witness count). The same overnight data always produces the same screen bytes.

The operator can:
- Scroll past QUIET if there's no time
- Seal any AGREED claim into canon (one human-key action per claim)
- Decline any NEEDS YOU item and record the decline as precedent
- Adjust budgets or rules based on GRADES

---

## Open Decisions (Operator's Call)

1. **How tight is "presence" detection?** Is it "keyboard activity", "window focus", "any HTTP request to the box", or something else? How long does "human awake" last before it expires?

2. **What happens to parked jobs?** Do they stay in the queue for tomorrow night, or are they marked "could not verify" in the Ledger and surface on the morning screen as "Incomplete — overnight budget"?

3. **Can overnight jobs read the Ledger?** Or only the pile and the record? (Reading the Ledger could be a security boundary; the job index is one answer.)

4. **Model tiering:** Should 3B, 7B, and larger models each have their own job queue and budget? Or one mixed pool?

5. **Sealing from overnight:** Can a verdict that all witnesses agree on (Satisfied) be auto-sealed into canon, or does every claim require explicit human action? (Draft rules below suggest *only* human seals, but this is the operator's call.)

---

## Draft Rules (Agent-Proposed)

1. **Overnight jobs must cite what they touch.** If a job re-checks something, it Cites the original claim or the witness that produced it. Jobs that run with no citation are flagged as "reason lost" and surface on the morning screen.

2. **Verdicts are immutable once stamped.** A verdict can't be "taken back". If it was wrong, a new check produces a new verdict, which amends canon (if sealed).

3. **Presence overrides the budget.** The pool yields immediately if presence is detected, but a halfway-done job finishes if it can (within the wall time). This prevents missed windows from cascading work into the day.

4. **Disagreement is data.** A Failing verdict is not a bug — it's evidence that this claim needs the human's attention. Over time, families that disagree more often on real tasks (graded by human seal) might be weighted down.

5. **Morning screen is read-only.** The operator can't edit it. They can seal claims, mark decisions, and adjust budgets, but the screen itself is regenerated from the record every morning.

---

## Example: A Morning After

```
Overnight run: 2026-10-03 0100–0530
Budget: 4.0 hours; used: 3.7 hours (93 jobs run, 8 parked for tonight)

[NEEDS YOU] ────────────────────────────────────────────────
  • Operator decision needed: egress.web request for "climate migration 2024"
    WHO: jeles | WHAT: fetch data | WHERE: news sources | BYTES: 4.2 KB
    Granted yesterday for "climate", declined for "tech policy". Your precedent says?
    
  • Law change: CONST-III (Reach) amended 2026-10-03 0245
    Two grant types now require re-seal: egress.web and willow_web
    5 claims originally sealed under old rule; morning screen has them marked "new rule"
    Human action: re-seal or re-check?

[DISAGREEMENTS] ────────────────────────────────────────────
  • Prediction P1 grade: 0.62 ← operator's estimate was 0.71
    (Claude 3B: 0.58, Mistral 7B: 0.65, Phi 2: 0.61) [Failing]
    The outlier path (23-question loop) didn't happen. Plan path hit instead.
    
  • Quote check on "the one-box plan is Rat" [source: next-pile.md §1]
    Witness 1 (grep): exact match found
    Witness 2 (semantic): closest match is "Rat is proposed as the one runtime"
    [Differently: semantic boundary mismatch]

[AGREED, NOT SEALED] ────────────────────────────────────────
  • "The workflow uses a three-rung ladder before escalating"
    Witnessed by: 3B analysis + human mark T167 | [Satisfied]
    Seal into canon?
    
  • "The constitution forbids downward references"
    Witnessed by: grep (CONST-0.8) + semantic check | [Satisfied]
    Seal into canon?

[GRADES] ────────────────────────────────────────────────────
  Prediction accuracy (vs. operator's actual next step):
  • Yesterday's P1: 55% (median path predicted, but outlier was actual)
  • Family floors (on Appendix B snippets):
    Claude 3B: 0.71 | Mistral 7B: 0.74 | Phi 2: 0.68
  • Consistency (same-task repeats): all families held ±0.05
  
  [No models below expected floor]

[QUIET] ─────────────────────────────────────────────────────
  93 overnight jobs run | 85 completed | 8 parked (budget)
  201 claims checked | 187 satisfied | 12 differently | 2 failing
  No Ledger breaks | No pile drift detected
  Overnight budget: 3.7 / 4.0 hours | 8 jobs → tonight's queue
```

The operator spends 15 minutes, seals the agreed claims, decides "jeles.web can't proceed without new explicit grant" (overriding precedent), and marks the prediction discrepancy for next-bite review.

---

## References

- workflow.md §2c (repetition and escalation)
- workflow.md §4 (loops and the heartbeat)
- workflow.md §7 (open predictions and grading)
- next-pile.md §7 (reverse and witnesses)
- next-pile.md §Overnight (pool and morning)
- CONST-IV (Knowledge and Canon)
- CONST-XII (Resource Envelopes) — *note: this article is unwritten; this proposal assumes it exists*

