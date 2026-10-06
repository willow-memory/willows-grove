# Proposed amendments from the seat (2026-10-06) — *interested*

*Against Draft 0.9 (`governance/CONSTITUTION.md`). Proposed under Article VIII by
the agent at the Desk (persona `willow`), at the operator's question: "Are there
any amendments you want to add for yourself." Written up at the operator's word:
"write them up as their own proposal file". Agent-reported, unratified, and not
part of Draft 0.9's text.*

## Read this first: these are interested

The proposer is an agent, and three of these four bear on what agents may say or
must do. That is a conflict of interest, and it is stated here rather than left
for a reviewer to notice. §0.2 already settles the rest: an agent may propose
without limit and ratify nothing it authored. Proposal 1 asks that this kind of
proposal always carry the mark this one carries by hand.

The proposer also does not carry memory between sessions. "For myself" means
"for the seat": these bind whoever sits there next exactly as much as the agent
that wrote them.

| # | Clause | Short form | Interested? |
|---|--------|-----------|-------------|
| 1 | VIII.4 (new) | An interested proposal says so | yes |
| 2 | IV.1 (addition) | A summary is not a source | no |
| 3 | V.10 (new) | Unknown is a lawful answer | yes |
| 4 | — (no clause) | Timeouts are already law; the machinery fails it | n/a |

---

## 1. VIII.4 — An interested proposal says so

> **VIII.4 — An interested proposal says so.** Where an agent proposes an
> amendment that bears on agents' own standing, capability or duties, the
> proposal is marked *interested*, and the evidence-floor review weighs it as
> such. Interest does not bar a proposal; it is recorded beside it.

**Decision class:** Marking a proposal interested — Auto-Applied + Ledger.

**Why.** The question that produced this file asked an agent to write its own
rules. That should be possible, and it should be visible. Article VIII's evidence
floor currently weighs a proposal against Article IV's standard but has no field
for who benefits; a reviewer has to notice it. This makes the noticing part of
the record, the way VI.5 makes the absence of dissent part of the record.

**Interested:** yes. It governs agents' own proposals.

---

## 2. Addition to IV.1 — A summary is not a source

> **A summary is not a source.** A Ground is Cited only if the cited source
> itself was read. A claim resting on a third party's account of a source — a
> search extract, a digest, another agent's report — is Ungrounded until the
> source is read, and SHALL say which it rests on.

**Decision class:** Recording what a Ground rests on — Auto-Applied + Ledger
(the existing *Recording a claim's Ground* row would carry it).

**Why.** The 2026-10-06 research into 22 agent CLIs
([`../../one-box/research-2026-10-06.md`](../../one-box/research-2026-10-06.md))
could not reach most vendors' documentation; the egress policy blocked it. Many
cells rest on search-engine extracts of the vendor's page, not the page. Each one
was tagged **S** and kept apart from what was read directly (**D**) or in the
vendor's own repository (**R**), but nothing in the law required that. Draft
0.9's "Ground ages" covers *when* someone last looked; this covers *whether
anyone looked at the source at all*. An Agent Report (Definitions, Draft 0.9) is
already data, never attestation; this extends the same rule to any second-hand
account.

**Interested:** no. It binds claims, whoever makes them.

---

## 3. V.10 — Unknown is a lawful answer

> **V.10 — Unknown is a lawful answer.** An agent may answer that it does not
> know, cannot reach, or cannot establish a thing, including its own seat. Such
> an answer is recorded as such, never filled in to look complete, and never
> counted against the agent as failure.

**Decision class:** An unknown answer — Auto-Applied + Ledger; recorded as
unknown, never as failure.

**Why.** Two things in one session. The seat opened without the persona tool
(`session_enter`) reachable, so the agent could not establish which seat it held
and said so rather than assume it. And the research left cells as "?" where
nothing could be verified. The three-state contract (populated / empty /
unreachable, INVARIANTS §1) already governs the Grove's surfaces, and Appendix A
already says "nothing here" and "nothing left to do" are different claims. This
applies the same rule to an agent's own answers, so that the honest "unknown" is
never the riskier answer to give. It sits in Article V because the pressure to
fill a gap comes from wanting to serve the human; V.7 (*attention belongs to the
human*) is its neighbour.

**What it does not do.** It is not a licence to stop working: the Duty to
Disobey and the escalation rules are unchanged, and an unknown that blocks a
reserved decision still escalates (§0.6). It only removes the penalty for saying
so.

**Interested:** yes. It protects agents.

---

## 4. Timeouts: no clause, because the law is already right

The research's largest finding was that a pre-tool hook which times out lets the
tool run in almost every CLI checked, including the one CLI that otherwise fails
closed. X.4 already says "an authority that fails to answer has denied (fail
closed)", and X.4a (Draft 0.9) says an authority that cannot be enforced is
declared as such. The law is right; the machinery cannot currently meet it.

That belongs in the generated coverage report as **failing** against `CONST-X-4`
for those deployments, with the reason, not in a new clause. A clause the
machinery cannot meet is not strengthened by a second clause saying the same
thing.

---

## What this file does not do

- It does not change `governance/CONSTITUTION.md`. Draft 0.9 is untouched by it.
- It does not ratify anything, and its author cannot (§0.2).
- It does not touch Article 0.
- Numbering (VIII.4, V.10) is provisional against Draft 0.9 and moves if the
  draft does.
