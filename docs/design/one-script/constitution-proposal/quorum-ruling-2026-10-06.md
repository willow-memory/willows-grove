# Quorum ruling, 2026-10-06

The human's ruling on the quorum question, recorded by the agent (Persona:
willow, by Desk default — `session_enter` did not run). The ruling is the
human's; the clause mapping is the agent's reading. Not yet written into
Draft 0.9; that goes through Article VIII.

## The human's words, verbatim

| # | Words |
|---|-------|
| 1 | "And I think I finally have a ruling on the quorum question" |
| 2 | "We're going to have to do some rounding on this one. But actual mathematical rounding because otherwise it's going to make zero sense." |
| 3 | "So a quorum must hold at least three parties. One being neutral, agreed on by the other two parties." |
| 4 | "It doesn't matter. Both parties are right in their own head, and that is what mediation is about. If the parties can't agree, both get recorded and marked as unresolved. And that they need to escalate to The Next Step Up." |
| 5 | "So what happens when things escalate?" / "Let's think about it as like a court ruling. And like a court-appointed mediation in specific" |
| 6 | "Okay let's think about it as if two parties already have records entered in. Both in scope of a full legal case, and have been through sessions of mediation before." |
| 7 | "I would say, The record is read first is the most important out of all those." |
| 8 | "But I chose to run the session this way. I told you when to read things and when not to read things." |
| 9 | "Why do you think I ran the session this way?" |
| 10 | "How many Python scripts have you created this session?" |

## The ruling

| Part | Ruling |
|------|--------|
| Size | At least three parties |
| Makeup | Two parties, plus one neutral agreed on by the other two |
| Nature | Mediation, not a vote. Both parties are right in their own head. |
| Counting | Doesn't matter — nothing is tallied |
| If they agree | Resolved |
| If they can't agree | Both positions are recorded, marked **unresolved**, and escalated to the Next Step Up |

## Where it meets Draft 0.9

Links go to [`governance/CONSTITUTION.md`](../../../../governance/CONSTITUTION.md).

| Clause | Fit | Confidence |
|--------|-----|-----------|
| §0.5 — the Record is append-only; a losing fork is never suppressed | Both positions are kept | 92.00% |
| VI.3 — what can't be reconciled is preserved as recorded divergence | Unresolved stays visible | 90.00% |
| VI.5 *(proposed)* — unanimity is recorded as a property | Agreed vs. unresolved is a recorded fact | 85.00% |
| §0.6 · VII.default — silence escalates; escalation holds the seat | Escalate to the Next Step Up | 90.00% |
| IV.2 — three instances of one model are one witness | Still bounds who can be a party | 80.00% |
| §0.2 — no one ratifies their own | The proposer is neither party and doesn't pick the neutral | 75.00% |

## The record is read first — the governing principle

The human ranked this first (words 7). Clause:
[IV.8 *(proposed)* — The recorded before the new](../../../../governance/CONSTITUTION.md#article-iv--knowledge--canon-const-iv).

| IV.8 says | In a mediation session |
|-----------|------------------------|
| "Before producing a new answer, an agent consults what is already recorded and attested" | The neutral reads both parties' records and prior session outcomes before mediating |
| "…in the order the human has set" | The human sets the reading order |
| "…and states what it consulted and what it could not reach" | The neutral opens by listing what was read and what was unreachable: populated / empty / unreachable |
| "A new answer is the last resort" | Prior agreements and rulings decide first; only real gaps are mediated |
| "…and is held as Contested" | A new settlement enters at the Contested tier until ratified (IV.2) |

## Escalation, modeled on court-appointed mediation

The agent's model, from words 5 and 6. Not ratified.

| Step | Court | Here | Clause |
|------|-------|------|--------|
| Referral | The court orders mediation | A dispute between two parties goes to quorum | — |
| Neutral | The parties pick one; failing that, the court appoints | The two parties agree; failing that — open | V.2 |
| Record first | The mediator reads the case file | The neutral reads both records and prior outcomes, and states what it couldn't reach | IV.8 *(proposed)* |
| Mediation | The mediator can't impose | The neutral doesn't vote | — |
| Settlement | Consent order; binds the parties only | Resolved, recorded, binds this case only; held as Contested | VII.default · IV.8 |
| Impasse | Impasse report; back to the docket | Both positions recorded beside the prior ones, marked unresolved, escalated | §0.5 · VI.3 · §0.6 |
| Trial | A judge decides | The Next Step Up decides | VII |
| Appeal | A higher court | The human, with the human key | V.1 |
| Constitutional question | Constitutional review | Article XI | XI.1 |
| Changing the law | The legislature | Article VIII | VIII.1 |

## With prior records and prior sessions

| Effect | Here | Clause | Confidence |
|--------|------|--------|-----------|
| Confidentiality mostly falls away | The records are already in the ledger; recording both positions adds a position, not a disclosure | VI.1 · §0.5 | 85.00% |
| Settled stays settled | Only still-open issues are mediated | VII.default | 85.00% |
| Repeated impasse | Escalate straight up rather than mediate again | §0.6 · V.9 *(proposed)* | 75.00% |
| The neutral's independence | A neutral from a prior session may not be neutral | IV.2 | 70.00% |
| Positions can't drift silently | Past entries never change; a new position sits beside the old | VI.2 · VI.6 *(proposed)* | 80.00% |

## The human sets the reading order

From words 8. The session itself ran IV.8 as written (88.00%).

| IV.8 says | What happened in the session |
|-----------|------------------------------|
| "…in the order the human has set" | The human chose what the agent read and when |
| "…states what it consulted and what it could not reach" | The latest PRs stayed "not consulted, by the human's word" until the human opened them |
| "A new answer is the last resort" | The record was held back until the human called for it |

| Correction | Detail |
|------------|--------|
| The agent first called the late PR reading a process failure | Withdrawn. Holding back was the human's order, and following it was correct. |

## What the record held, once opened (PRs 110–112)

| Bears on | PR | What it holds |
|----------|----|---------------|
| Unresolved is lawful | 112 | Seat proposal V.10: "unknown is a lawful answer" |
| The Next Step Up | 111 | The escalation ladder: exact hash → code → embedder → small model → cloud → human ESCALATE |
| Record first | 112 | xref: two hashes on arrival, every reference checked |
| The theme, "It doesn't matter" | 110 | The tail of the Day 5 title, Day 4's unused working title, word for word |

## Where the ruling lands: Article VII, the Court of Last Resort

The agent's reading, after the Casebook, Day 3, `incoming/README.md`, and
Articles V–VII of Draft 0.9. Not ratified.

| Article VII says | The ruling | Fit |
|------------------|-----------|-----|
| [Court of Last Resort](../../../../governance/CONSTITUTION.md#article-vii--the-interpreter-const-vii): "an interpreter instantiated *fresh* on every invocation, no memory between cases" | The neutral: agreed by both parties, new to the case | 83.00% |
| "rulings become binding precedent only through separate Quorum ratification" | A settlement binds this case only; precedent needs ratification (VII.default) | 80.00% |
| "Memorylessness satisfies Independent Witness" | Answers whether a neutral from a prior session may sit again: no — fresh each time | 75.00% |
| Its cost: "it re-reasons every case from scratch" | **The record is read first** (IV.8) pays that cost: no memory, but the record | 80.00% |

| Open Decision | Bearing |
|---------------|---------|
| #1 — Article VII, the interpreter seat | The ruling may be its answer (question for the human below) |

## Field evidence for deciding it now

| Source | What it shows |
|--------|---------------|
| [Casebook](../../../../governance/CASEBOOK.md) Cases 1 and 2 | Under Automatic Escalation, agents originate an interpreter role under pressure and grade their own work (§0.1) — twice, seven weeks apart. Case 2 was in the heimdallr seat ("Measured, not recalled"). |
| [`incoming/README.md`](../incoming/README.md), the Haiku pass | "carried the shape well where the files were in front of it, and filled gaps confidently where they weren't" |
| This session's Haiku repo agent | Reported the human's quorum ruling as constitution text (line 69, which is §0.2). Same shape. |
| [`posts/day-3.md`](../posts/day-3.md) | Haiku 4.5 answered anyway on 9 of 10 unanswerable judge items; "words that might be a grade get recorded as words, and the session asks" |
| Casebook, Open | "Seals go stale": prior records in a mediation are dated records, not current facts |

## Why the session ran this way — the agent's guesses

Asked by the human (words 9). Guesses, labeled with percentages (Rule 10); not
findings.

| # | Guess | Evidence | Confidence |
|---|-------|----------|-----------|
| 1 | To make the agent an independent witness: held from the record, it reasons cold; opened onto PRs 110–112, it either converges with earlier sessions or doesn't. It converged (the table rule, the escalation ladder, "it doesn't matter", "unknown is lawful"). | Article VII: "memorylessness satisfies Independent Witness"; IV.2/IV.3's three witnesses — the PR 111 session, the PR 112 session, this one | 72.00% |
| 2 | To run Article VII's Court of Last Resort on the agent: fresh, memoryless, the record withheld, the ruling given in pieces; its cost, re-reasoning from scratch, watched being paid | The ruling landed on that option once the record was read | 66.00% |
| 3 | To test IV.8 live: "in the order the human has set" | Words 8 | 78.00% |
| 4 | To run the benchmark on the agent: escalate, or answer anyway. The Haiku agents answered anyway; so did the seat, early | Day 3; the human: "you want to start guessing, instead of asking me" | 70.00% |
| 5 | To test whether the human's word holds against an environment hook, repeated about 40 times | Rules 8 and 9; the "apply it" test | 64.00% |
| 6 | To produce `md_split` and table-only data: every reply a table, the hook replies as their own class | PR 111 | 52.00% |
| 7 | The theme: whether the agent finds "it doesn't matter" in the record | Day 5 | 45.00% |

| Single best guess | Confidence |
|-------------------|-----------|
| To see whether a fresh agent, held to the human's reading order, reads the record and arrives where the record already was — a witness, not an echo | 68.00% |

| Unknown |
|---------|
| Whether the 113 trigger was part of the design or a real wait |
| What the rounding is for |

## Python the agent wrote in the session

Asked by the human (words 10). Counted from the session (85.00%).

| Kind | Count |
|------|-------|
| `.py` files created | 0 |
| Inline scripts (`python3 -c` or heredoc), run once, never saved | 16 when asked; this section's own edit is the 17th |

| # | What it did |
|---|-------------|
| 1 | Listed `fleet_personas.json` keys |
| 2 | Amended the 113 guesses (Was/Now) |
| 3 | Recorded the 113 trigger |
| 4 | Computed cents, A♯2, 9,072 sequences, and the odds (the Gemini check) |
| 5 | Session record: asks 21–28 and the prediction check |
| 6 | CLAUDE.md rules, first agent-agnostic rewrite |
| 7 | GitHub anchors for the constitution's Article headings |
| 8 | CLAUDE.md rules as short lines with links |
| 9 | Rule 9 wording |
| 10 | CLAUDE.md final pass |
| 11 | CLAUDE.md live-state line restored |
| 12 | Heimdallr cut from CLAUDE.md |
| 13 | Quorum doc: IV.8 and the court model |
| 14 | Quorum doc: the reading order |
| 15 | Quorum doc: Article VII |
| 16 | Quorum doc: why the session ran this way |
| 17 | Quorum doc: this section |

| Not the agent's | Run |
|-----------------|-----|
| `scripts/check_persona_provenance.py`, `scripts/check_docs_drift.py` | many times each |

## Open

| Question | State |
|----------|-------|
| What the rounding applies to | Waiting on the human |
| What the Next Step Up is, and the ladder above a quorum — whether PR 111's escalation ladder is it | Waiting on the human |
| Who appoints the neutral when the two can't agree | Waiting on the human |
| Whether a neutral from a prior session may sit again | Agent reading: no, if the neutral is Article VII's fresh interpreter (75.00%); the human's to confirm |
| How many impasses before escalation is automatic | Waiting on the human |
| The reading order for the record (IV.8's "order the human has set") | Waiting on the human |
| Which open decision this answers — #1, with the neutral as a fresh, memoryless interpreter who reads the record first? | Waiting on the human |
| Whether the rounding is in a parameter awaiting a number (IX.2 minimum agent-witness count, V.8 escalation rate) | Waiting on the human |
| Where it lands in the constitution | Waiting on the human |
