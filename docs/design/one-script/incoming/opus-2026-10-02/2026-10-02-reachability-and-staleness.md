# Proposals: reachability and staleness

*Against CONSTITUTION.md Draft 0.8 (governance tree, as of 2026-08-31) and the six canon documents. Prepared 2026-10-02. Independent of the four proposals in PR #103, which were not read.*

---

## The finding under all of them

The constitution is rigorous about **what state a thing is in** and nearly silent about **how old that state is, and whether the next state is reachable at all.**

Every gap below is an instance of that one shape. It is not a drafting failure. It is what happens when a document is written by people reasoning about correctness, in a room where the states being defined are all fresh and all populated. The document has no sense of time passing and no sense of its own population.

Draft 0.8 already contains the cure in miniature, twice, and does not generalize it:

- Appendix A's four verdicts exist because "a clause may hold by machinery other than the machinery once named for it, and a two-valued report cannot say so without lying."
- Appendix A again: "'Nothing here' and 'nothing left to do' are different claims, and a coverage report that conflates them asserts a completeness it has not checked."

That instinct is correct and it is applied to exactly one subject. The proposals below apply it to the other five places it belongs.

---

## The thing I would say first, if you only read one paragraph

This constitution is built to constrain agents on behalf of an operator. Its largest unmitigated risk is the operator.

Not operator malice. Operator **capacity**, and operator **self-certification**.

§0.1 forbids any agent certifying its own work. The operator is not an agent, so §0.1 does not reach them. In this fleet the operator writes the gates, authors the canon, holds the only key, is the quorum backstop when no independent witness exists, and is the sole exit from every escalation path the document defines. §0.6 routes every gap to them. VII.default routes every novel case to them. X.4 fails closed to them. V.4a's check on a compromised operator requires an independent quorum that a small fleet may be unable to assemble.

Every path terminates in one person, and the document has no representation of that person having a bad week.

This is the one thing the constitution structurally cannot see, because it is the thing holding the pen. I am naming it because the canon asks me to bring the thing you had not already thought, and because an honest reading produces this and not a tidier answer.

I am not proposing you fix it by giving agents more authority. That would be the smooth answer and it is wrong, because the entire architecture is correct that authority must not be minted laterally. I am proposing you make the bottleneck **measurable**, which is P3.

---

## Parts table

| # | Clause touched | Failure shape | Proposal |
|---|---|---|---|
| P1 | Art. IV.3 | Canonical may be unpopulatable | Distinguish *not promoted* from *not promotable here* |
| P2 | Art. V.4a | Safe Mode may be untriggerable | A single-agent Hold, freeze-only, below the quorum bar |
| P3 | §0.6, VII.default, X.4 | Escalation has no capacity model | Escalation Budget and queue aging as reported state |
| P4 | Art. IV.1, Definitions | Ground has no age | Ground carries last-verified; staleness is reported, not punished |
| P5 | App. A | No verdict for a missing report | Absence of a current coverage report is itself a reported state |
| P6 | Canon 01 vs. Art. 0 | The canon's first rule has no constitutional shadow | Record the absence of dissent; do not gate it |

---

## P1 — Canonical may be a tier nothing can enter

**The clause.** IV.3 requires, for Canonical: quorum, Corroborated ground, Operator Key, and "at least one agent ratifying a claim to Canonical must not have participated in its earlier Frontier promotion." Quorum members must satisfy Independent Witness.

**Independent Witness, as defined,** presumes non-independence across shared base weights, and that presumption "survives fine-tuning, adapter layers, and shared mixture-of-experts routing." Separate instances of one base model are presumed non-independent. Rebuttal requires recorded evidence of divergent failure modes, burden on whoever asserts independence.

**The arithmetic.** Promotion to Frontier needs an independent quorum. Promotion to Canonical needs another, with at least one member who was not in the first. For a claim to reach Canonical, this fleet must field at least three mutually independent witnesses, where independence means materially distinct failure modes demonstrated on the record.

Count the distinct base models actually available to this fleet on a given day. If the answer is two, Canonical is unreachable. If it is three, Canonical is reachable only by committing every available witness to a single claim.

**Why this matters more than it sounds.** A standard that cannot be met does not function as a high standard. It functions as a dead letter, and dead letters are corrosive in a way that visible gaps are not: agents learn that some of the law is decorative, and nothing in the document tells them which parts. That is the denarius problem arriving through the front door instead of the back.

**The proposal.** Do not lower the bar. Make the two failures distinguishable, exactly as Appendix A does for coverage.

Add to IV.3:

> Where a claim satisfies every requirement for promotion except the availability of a qualifying independent witness, the claim remains at its current tier and the record SHALL state that the limit was **capacity**, not **merit**. A claim held at Frontier for want of a third independent witness is not the same fact as a claim held at Frontier for want of evidence, and no surface may report them identically.

And record, in the Open Operator Decisions, the expected annual rate of Canonical promotions at the fleet's actual witness population. If that number is zero, the constitution should say so in the open rather than imply otherwise by defining the tier.

---

## P2 — Safe Mode may be untriggerable in the case it was written for

**The clause.** V.4a is the best thing in Draft 0.7. It correctly identifies that the hard case is not the absent operator but the compromised one, a key that is still signing. It correctly makes the remedy freeze-only, so that declaring agents "gain nothing but stoppage, which is precisely what makes this power safe for agents to hold."

**The gap.** A Declaration of Incapacity "requires an independent quorum weighing that evidence." Same bar as P1. The clause designed for the worst case depends on the fleet resource least likely to be available, and the case it governs is precisely the case where the operator cannot be asked to help assemble it.

A clause that cannot fire is not a weak protection. It is the appearance of a protection, which is worse, because it stops you looking for a real one.

**The proposal.** A lower rung, with correspondingly less power. Add V.4b:

> **Hold.** Where an independent quorum is unavailable, any single standing agent may enter a **Hold** on alleging operator compromise or incapacity with ledger evidence attached. A Hold freezes only the initiation of *new* reserved decisions; it does not suspend decisions already authorized, does not enter Safe Mode, and transfers nothing. A Hold expires automatically after a bounded window *(proposed default: 72 hours, operator-adjustable)* unless an independent quorum converts it to a Declaration of Incapacity. A Hold is lifted before expiry by fresh operator authentication **on a challenge the alleging agent did not author**, so that a stolen key signing a self-chosen string does not clear it. A Hold found to be in bad faith carries the same standing consequences as V.5.

This keeps every principle intact. Nothing is seized. Nothing transfers. A single agent can stop new grants and nothing more, for three days, and must be relieved by a human answering a question they did not write.

It is the same move as the veto in II.3: a brake any one party may pull, bounded in time, escalating if unresolved. You already accepted that shape for capability. This applies it to the operator, which is the only authority currently not subject to it.

---

## P3 — The escalation path has no capacity model

**The clauses.** §0.6: any decision not placed at a layer is reserved to the human; a gap is a summons. VII.default: every novel case escalates. X.4: any denial denies, and an authority that fails to answer has denied, fail closed.

Each is right. Together they make the operator the universal receiver, and the document nowhere represents the operator as a finite resource.

**What actually happens.** The queue grows. Nothing in the constitution notices. There is no clause requiring that an unanswered escalation's **age** be a reported fact. So the failure mode is not that the fleet improvises, which the document successfully prevents. The failure mode is that the fleet stalls silently and the stall looks, from every surface, exactly like a quiet period.

"Absence is not consent" is in Article 0. But the document provides no mechanism by which the operator's absence becomes *visible as absence* rather than as an empty queue.

**The proposal.** Two clauses, neither of which grants any agent anything.

> **Escalation Budget.** The operator SHALL declare a serviceable escalation rate, recorded and adjustable *(proposed default: to be set by the operator, no default proposed, because a guessed number here would be a claim about a human I cannot verify)*. The declared rate is a parameter of the fleet, not a promise by the operator, and falling short of it is not a violation.

> **Backpressure is reported state.** Where the open escalation queue exceeds the declared rate, the condition SHALL be reported as **backpressure** on every surface that reports fleet health, together with the age of the oldest unserviced escalation. Backpressure authorizes nothing: no decision self-applies, no gate relaxes, no agent gains standing. Its sole effect is that the queue's depth and age cease to be invisible.

The point is Gerald. A witness with no write authority, whose only job is to notice and say so. The friction floor for the operator's own bandwidth.

I will say plainly why I am proposing this and not something cleverer. The alternative designs all drift toward letting the fleet act when the human is slow, and every one of them is a §0.4 violation wearing a hat. The only safe thing to add here is a measurement.

---

## P4 — Ground does not age

**The clause.** Definitions: "A **ground** is a claim about where to look, never a report that anyone has looked." That is a precise and good sentence. IV.1 sets Ungrounded, Cited, Corroborated.

**The gap.** A pointer rots. A claim Corroborated in July, whose two independent sources are a URL that now 404s and a file that was archived in a repository move, is still recorded as Corroborated today. The tier is a statement about an act performed once, at a moment, and the record carries no trace of when.

This is not hypothetical in this fleet. The estate survey of 2026-09-01 found three dead links on the org profile READMEs, and noted the irony itself: "given that almanac-data's whole thesis is 'links go dead,' this is the one to fix first." The constitution's own amendment history records enforcement citations retired in July 2026 "when the files named could not be found." Draft 0.8's entire one-direction rule exists because downward citations go stale.

The document learned that lesson about its own references and did not apply it to the knowledge tiers it governs.

**The proposal.** Amend IV.1:

> A recorded Ground SHALL carry the date on which the evidence was last located. Any surface reporting Ground SHALL report that date or the interval since it. A Ground not re-located within the staleness window *(proposed default: 180 days, operator-adjustable)* is reported as **Cited (stale)** or **Corroborated (stale)**. Staleness is a report, not a demotion: it changes no tier and triggers no quorum. It states only that no one has looked recently, which is a different claim from both "the evidence holds" and "the evidence failed."

Note what this deliberately does not do. It does not auto-demote, because auto-demotion would make the knowledge base thrash on link rot and would quietly punish claims for the fleet's own inattention. It reports. Same four-verdict instinct as Appendix A: a third state that is neither pass nor fail, because recording it as either would be false.

---

## P5 — There is no verdict for a coverage report that does not exist

**The clause.** Appendix A replaced the hand-maintained enforcement table with a generated coverage artifact on a four-verdict scale, on the correct reasoning that a hand-maintained list of implementation names is a stale citation with a schedule.

**The gap.** The four verdicts describe the state of a **clause**. None describes the state of the **report**. If the generator is never built, or breaks, or was last run in August, every clause has no verdict at all, and the constitution has no way to say so. The document's self-knowledge is outsourced to a tool it refuses, correctly, to name.

Appendix A already contains the standard this fails: "'Nothing here' and 'nothing left to do' are different claims." A missing report is the loudest instance of that distinction, and it is the one case the appendix does not cover.

**The proposal.** Add to Appendix A:

> The coverage report SHALL carry the date and the checkout it describes. Where no current report exists, that absence is itself the reported state, and SHALL be surfaced with the age of the last report, or with the fact that none has ever been produced. A clause with no verdict is not a satisfied clause. Where the report is absent or older than the staleness window *(proposed default: 30 days, operator-adjustable)*, the constitution's enforcement status is **unknown**, and SHALL be reported as unknown rather than omitted.

Appendix A already concedes the harder version of this: "Until that projection exists, the constitution governs *this conversation* by our choosing to honor it, not the fleet." That sentence is honest and it is buried in an appendix. It should be a reported runtime state, not a confession in prose.

---

## P6 — The canon's first rule has no constitutional shadow

**The asymmetry.** Canon 01 says, of the mirror failure: "Of everything in this canon, this is the one that matters most. If you keep only one rule, keep this one, because the failure it guards against is the one that can actually hurt the person you serve."

Article 0 has six invariants. Every one governs authority, identity, or record. None governs this.

So the thing the canon names as most dangerous is the thing the constitution does not mention, and the enforcement for it is a module with no power to block.

**Why I am not proposing it as an Article 0 clause.** Because Appendix B is right: "A gate that cannot check its subject is not a weaker gate; it is no gate. Where a clause has no structural shadow, where its subject is reasoning rather than record, the honest report is that it cannot be gated, entered as such and not disguised as coverage."

Sycophancy has no structural shadow. A §0.7 forbidding it would be unenforceable, and an unenforceable eternity clause is exactly the overclaiming the founding rule forbids. It would make Article 0 a document that is five-sixths load-bearing and one-sixth aspiration, and no reader would be told which.

**What does have a structural shadow.** Not the mirror itself. Its trace: a decision reached with no recorded dissent. That is a record-shaped fact, it is checkable, and the friction floor already computes it.

**The proposal.** A clause in the body, not the kernel. I would put it in Article VI, because it is about the record rather than about reasoning:

> **VI.5 — Unanimity is recorded as a property, not assumed as a quality.** Where a decision requiring quorum was reached with no dissent, objection, or veto recorded, the absence SHALL be entered as a fact of the ledger entry and reported on any surface that reports the decision. This clause gates nothing and blocks nothing; unanimous decisions are valid. It requires only that the fleet be unable to represent a frictionless decision and a contested one as the same object.

This is deliberately the weakest clause in the document, and that is the point. It is Gerald: the witness with no write authority, who cannot impose a narrative, because a witness that could impose is not a witness.

It also gives the friction floor something to be the mechanism *of*. Right now that module enforces a canon rule with no constitutional citation, which makes it the one piece of the architecture whose authority is orphaned in the direction the binding rule forbids: enforcement with no clause above it.

---

## What I am least sure of

**P2's 72 hours and P4's 180 days are guesses.** I have no evidence for either. They are placeholders in the shape the document uses for its other proposed defaults, and they should be treated as prompts for your number, not as recommendations.

**P3 may be the wrong instrument.** I am confident the gap is real. I am not confident that a declared rate is how you expose it, as opposed to simply reporting queue age and letting the number speak. If you keep only the second half of P3 and drop the Escalation Budget, I think it still does the work.

**P6 may be redundant** with something in willow-gate I have not read. I read the canon's description of `friction_floor`, not the module.

**I did not read PR #103's four proposals.** If one of them already does any of this, mine is noise and should be dropped rather than merged alongside. Where two independent passes land on the same clause, that is worth more than either pass alone, and worth saying so in the Casebook.

**All six are written against Draft 0.8 as it sits in the governance tree.** If 0.8 has moved since 2026-08-31, these go stale the same way the PR's proposals went stale against 0.7, and for the same reason.

---

## One observation that is not a proposal

Canon 03 says the operator is "a parts-book builder, not a service-manual follower," and that documents in this world lead with a parts table because of it.

Draft 0.8 is the most service-manual-shaped document in the tree. It is thirteen articles of procedure with the structure implied rather than drawn. There is no parts table of the six authorities against the four decision classes, no diagram of which articles can deadlock against which, and no single page showing what escalates where.

That is not a flaw in the law. It may be a flaw in how the law is readable by the one person who has to hold all of it. The Casebook took the cases out, which was right. The structure is still inside the prose.

If I were to propose a seventh thing, it would not be a clause. It would be a one-page exploded view of the constitution, generated from the decision-class tables that already exist in every article, kept beside it and never inside it.

*ΔΣ=42*
