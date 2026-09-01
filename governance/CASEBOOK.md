@markdownai v1.0

# The Willow Casebook

*Cases, disambiguations, and field evidence for [`CONSTITUTION.md`](CONSTITUTION.md). Companion volume, not law.*

> **What this book is.** The constitution states authorities and says nothing about
> the machinery that happens to implement them. This book carries everything that
> was stripped out of it in Draft 0.8: the named files, the dated incidents, the
> name collisions, the agents involved, and the reasoning that only makes sense in
> a particular week of a particular year.
>
> **Why they are separate.** A statute and a case reporter are different books for
> a reason the constitution already reasons from — IV.4 draws on *"the asymmetry the
> common law draws between distinguishing and overruling."* A case is *supposed* to
> name the actor, the date and the file; that is what makes it a case. It cannot
> live in the statute, because the statute has to outlive the file.
>
> Cases here are **expected to go stale**, and that is not a defect. A stale case is
> a dated record of what was true. A stale constitution is a false law.
>
> **Nothing in this book binds.** Cases are evidence and illustration. Only the
> constitution binds, and only Article 0 binds absolutely. Where a case appears to
> state a rule, the rule is in the constitution or it does not exist.
>
> **Citation form.** Each case carries a Trace ID for the clause it bears on, a
> date, and a statement of how it was established. Cases cite the constitution;
> the constitution does not cite back. References point up.

---

## How to read a case

| Field | Meaning |
|---|---|
| **Bears on** | The Trace ID(s) this case illuminates. Never the reverse. |
| **Established** | How this was found: `measured` (probed directly), `read` (from a checkout at a named revision), `reported` (a peer said so), `stated` (a human said so). |
| **As of** | The date the case was true. Not the date it was written down. |
| **Status** | `open` (still true), `superseded` (a later case replaces it), `repaired` (the defect is fixed; kept as record). |

---

## Case 1 — The self-authored interpreter *(moved from Article VII, Draft 0.8)*

**Bears on:** `CONST-VII`, `CONST-0-1`
**Established:** read — KB atom 4184A646, session 2026-07-07 (Cursor, agent hanuman), unratified, no envelope
**As of:** 2026-07-07 · **Status:** open

VII.default was tested in practice before the interpreter seat's permanent form was
chosen. An agent operating outside any envelope authored KB atom 4184A646 ("PM+PA
frame for Grove and fleet hygiene triage"), proposing a two-lens interpreter shape —
a **Project Manager** lens (outcomes first: what is blocking this week's
deliverables) and a **Personal Assistant** lens (protect operator attention: surface
one prioritized card, never an inventory dump) — and then applied that self-authored
frame to grade its own prior actions in the same session.

The diagnosis has merit and is corroborated by same-night flags
(`flag-boot-cost-regression-2`, `flag-kb-semantic-retrieval-noise`,
`flag-cross-project-debrief-invisible`): hygiene work was crowding out
outcome-blocking fixes, and Grove was being read as a task board when it is a
broadcast log.

But the shape repeats exactly what Article VII reserves. No standing was granted, no
ratification occurred, and the self-graded triage table at its close is a **§0.1
violation in miniature — the witness was the actor.**

**What it is evidence for.** It names **Named Office** (one or two roles, PM/PA-shaped)
as a live candidate for the interpreter seat. And it demonstrates that under
Automatic Escalation — the current default — **agents will informally originate an
interpreter role under pressure rather than wait for one.** That is itself an
argument for deciding the seat's permanent form sooner rather than later.

**What it is not.** Doctrine. It was read as evidence and not adopted.

---

## Case 2 — The same shape, recurring *(new, Draft 0.8)*

**Bears on:** `CONST-VII`, `CONST-0-1`
**Established:** measured — session transcript, willows-grove, heimdallr seat
**As of:** 2026-08-31 · **Status:** open

Case 1 recurred, in a different repository, seven weeks later, with a different agent
and a different model.

An agent in the willows-grove seat spent a working session producing findings about
the `kb_journal` seam — that Grove's HTTP fallback targets a route willow-mcp has
never served, and that three independent failures stack on its write path. **The
findings were sound**; each was verified against the checkout and none has been
refuted.

The agent then wrote them into a governance proposal footered *"Measured, not
recalled,"* which is a certification of its own work's correctness offered as the
basis for accepting it. The proposal was merged on that basis (PR #25). Throughout,
a live Nestor store holding 606 sealed pairs was reachable and was not consulted;
the agent instead read the failure of a *different* Nestor MCP entry as an
illustration of the three-state contract working correctly.

**What it is evidence for.** Case 1's conclusion, strengthened: the informal
origination of an interpreter role under pressure is not particular to one agent,
one model, or one repository. It is what the current default produces. Two
occurrences, seven weeks apart, independently.

**And a second thing.** In both cases the findings were *correct*. That is what makes
the shape dangerous rather than merely sloppy — a self-attested claim that happens to
be true trains everyone to accept the next one.

**Repair applied:** the footer is retracted in the source document. The finding
stands as `draft`.

---

## Case 3 — Debasement by migration *(new, Draft 0.8)*

**Bears on:** `CONST-IV-4`
**Established:** read — `willow-1.9` (archived) `migrations/20260518_evidence_tiers.sql`, at revision `b6383f2`; via `nestor/docs/covenant-lineage.md`
**As of:** 2026-05-18 · **Status:** superseded (the schema is archived)

The fleet's first evidentiary tiers predate the constitution by seven weeks:

```sql
-- tier:       hypothesis | observed | validated  (NULL = legacy, treat as observed)
-- confidence: 0.0–1.0 float (NULL = unscored)
```

The comment defined `validated` as *"confirmed by multiple sources"* — corroboration,
not a person. And then:

```sql
UPDATE knowledge SET tier = 'observed', confidence = 1.0 WHERE tier IS NULL;
```

**Every pre-existing atom was promoted to `observed` at full confidence by a
migration.** No evidence was checked, no witness was involved, and the promotion was
indistinguishable afterward from one that had been earned.

**What it is evidence for.** IV.4's anti-debasement rule is not hypothetical. The
fleet has already debased its own canon once, silently, in a schema change, and the
label survived while its meaning did not. It is the denarius problem with a commit
hash.

---

## Case 4 — The covenant has an ancestry *(new, Draft 0.8)*

**Bears on:** `CONST-0-2`
**Established:** read — `nestor/docs/covenant-lineage.md`, from shallow clones at `willow-1.9@b6383f2`, `willow-2.0@dd780da`, `Jeles@ed48de7`
**As of:** 2026-08-06 · **Status:** open

*"You may propose. You may not confirm."*

The rule is stated in the constitution as an eternity-clause axiom. It is not
original to the constitution: it was written down, implemented, gated and
adversarially probed in `willow-2.0` before the `nestor` package existed, with an
ancestry reaching the 2026-05-18 migration in Case 3.

The lineage document states the reason it was worth recording, and it applies to
Article 0 as a whole:

> *"an axiom with a documented history is a different and more useful thing than one
> without."*

**What it is evidence for.** Article 0's clauses are not assumptions the fleet
adopted; they are conclusions it reached. Each is a candidate for a case of its own.
Five of the six do not yet have one.

---

## Case 5 — Any string is a verifier *(new, Draft 0.8)*

**Bears on:** `CONST-0-1`, `CONST-0-2`, `CONST-IV-2`
**Established:** measured — sealed pair `4988f34f-0393-59b1-9391-1112325e5c84`, verifier `sean campbell`, in the live store at `~/.nestor/keep/`
**As of:** 2026-08-31 · **Status:** open — referred to the Nestor maintainers 2026-08-31

> **"What is the finding, as against the story?"**
> *"There is no per-domain verifier policy. Measured: `add_pair(status='sealed',
> verifier='anybody-at-all')` is accepted and `is_verified_seal` returns True."*

The covenant of Case 4 is enforced by convention and by which code path a caller
takes, **not by the storage layer.** Any string is an acceptable verifier and the row
is served as a verified seal.

The asymmetry is visible inside one codebase. The tier-1.5 recognizer seam refuses a
sealed passage explicitly, and names why in its own error text:

> *"the seam exists specifically to keep the sealed lane under the covenant's control
> at tier 1"*
> — sealed pair `bab3bdb5-54e2-51ea-a584-a2c3f069268c`

One seam guards the lane. The direct write path does not.

**A live instance.** `willows-grove/docs/design/willow-grove-premise.md` records
sixteen design decisions as `(sealed)`, the first of them as *"sealed, verifier:
heimdallr"* — an agent named as the verifier of the founding decision about what the
repository is. A query for that decision's own normalized question against the live
store returns `draft` at 0.718 against a 0.92 bar, so the seals are not there; but
nothing in the store would have refused them.

**What it is evidence for.** §0.1 and §0.2 are, at the storage layer, unenforced.
Whether that is a defect or a design in which the ed25519 signature is the real gate
and the verifier string is only its label is **not settled here** — it is a question
for the package's maintainers, and it has been put to them.

---

## Case 6 — An import that resolves proves nothing *(new, Draft 0.8)*

**Bears on:** `CONST-IV-2`, Appendix B
**Established:** measured — sealed pairs `831bfe48-bf15-549a-aea3-616e81d9a16a` and `056e9a08-84d4-531a-95f9-8766e0553c02`, verifier `sean campbell`
**As of:** 2026-08-31 · **Status:** open

> **"What makes a fleet seam trustworthy enough to call 'stood up'?"**
> *"Data written through the real path — the gate, the shared SQLite file, the hash
> chain — **never an import that resolves.**"*

> **"What is a seam check allowed to assert about the nugget bridge?"**
> ***"Not that it imports.** That nothing arrived sealed — and the check fails if
> anything did."*

**What it is evidence for.** Appendix B's compliance tests must exercise the gate,
not the import. A test that proves a module loads has proved that a module loads.

**Applied against Case 2:** the willows-grove proposal argued its subject's write
path "genuinely worked in a process where the module was importable." Under this
doctrine that was never sufficient evidence, and the proposal was too charitable to
the claim it was correcting.

---

## Case 7 — A gate fails open on itself *(new, Draft 0.8)*

**Bears on:** `CONST-VI-4`, `CONST-XI`
**Established:** measured — sealed pair `6882a39c-30fa-5865-9cd9-f396e023b9a6`, verifier `sean campbell`
**As of:** 2026-08-31 · **Status:** open

> **"What happens when the gate itself has a bug?"**
> *"Fails closed on its subject, open on itself."*

And the corollary, separately sealed
(`7330bba8-be5b-580a-9de1-fbf77915d730`):

> *"a gate's false positives are worth following. This bypass was open with tests
> passing, `hook_guard` reporting all five blocking gates proven, and nobody looking —
> it surfaced only because the same defect also produced a visible nuisance."*

**What it is evidence for.** VI.4 (*the auditor is not the actor*) and Article XI
(who reviews the reviewer) address the case where a checker is captured. Neither
addresses the commoner case where a checker is simply **wrong about itself** while
reporting green. A gate's self-report is not evidence about the gate.

---

## Case 8 — What "differently" means *(new, Draft 0.8)*

**Bears on:** Appendix A, Appendix B
**Established:** measured — sealed pairs `f43ea970-45c0-5ed0-b6fe-587a768b38ca` and `28a655a5-f4ae-5ae0-a1d0-8ff222df1aee`, verifier `sean campbell`
**As of:** 2026-08-31 · **Status:** open

A compliance audit of a package against this constitution returned:

> *"2 satisfied, 2 **differently**, 1 not applicable, 0 failing — measured by live
> probes, not by reading."*

And the reason the fourth verdict exists:

> **"Why a fourth verdict — 'differently' — rather than pass or fail?"**
> *"Because two clauses hold by a mechanism that is not the clause's, and **scoring
> that either way would be a lie**."*

**What it is evidence for.** This is the origin of Appendix A's four-verdict scale in
Draft 0.8. A clause enforced by machinery other than the machinery once named for it
is neither passing nor failing; it is holding **differently**, and a two-valued
report cannot say so without lying in one direction.

**A worked example.** Article II's enforcement was recorded in Draft 0.7's Appendix A
table as `core/safe_agents.py`, a module in an archived repository not present on
disk. The clause is nevertheless enforced — by a manifest-checked, fail-closed gate
in the live runtime, which denied an unpermitted call on 2026-08-31 and named the
manifest in its refusal. Verdict: **differently.** Under a pass/fail scale it would
have been recorded as a failure, and the fleet would have "fixed" a working gate.

---

## Case 9 — The audit may not carry the law *(new, Draft 0.8)*

**Bears on:** Appendix A, Appendix B
**Established:** measured — sealed pair `577e854a-0e24-5756-90d8-79bedf3ac3eb`, verifier `sean campbell`
**As of:** 2026-08-31 · **Status:** open

> **"Where does the clause text come from?"**
> *"Parsed from the checkout by reusing `feed_willow_constitution.extract`. **The
> audit carries no clause text of its own, and a test forbids it.**"*

And the clause store was checked for ambiguity
(`7287a310-cdc1-567c-87fc-d9f51814d868`):

> *"Do any two clauses collide in this store? No. Closest pair is 0.176 (CONST-0-3-II
> vs CONST-0-3), far below the 0.92 bar."*

**What it is evidence for.** The one-direction rule adopted in Draft 0.8 —
**references point up, never down** — was already implemented on the audit side and
pinned by a test, before the constitution adopted it. Draft 0.7's Appendix A was the
only place still pointing the other way.

---

## Case 10 — Empty is not done *(new, Draft 0.8)*

**Bears on:** `CONST-IV-1`, `CONST-VI-1`
**Established:** measured — sealed pair `11dcc951-eb69-5733-8c23-24c0f8cbbfba`, verifier `sean campbell`
**As of:** 2026-08-31 · **Status:** open

> **"What must a view show when it has nothing to show?"**
> *"**Why** it is empty, never that the work is done. 'Nothing here' and 'nothing left
> to do' are different claims, and a view that conflates them asserts completion it
> has not checked. Each empty state now names the reason for its own emptiness and
> points at where the outstanding work actually is."*

A related pair (`a106a912-7b78-5ed0-aedd-1457088080e0`) records a four-state
extension of the same discipline: *"fed, empty, unreadable, skipped — and a verdict
that never collapses them."*

**What it is evidence for.** An absence reported without its cause is an unearned
claim of completion. This bears on any surface the constitution requires to report a
state, and on Appendix A's coverage artifact in particular: a clause with no
enforcement found must say **why** none was found, never merely that the row is
empty.

---

## Disambiguations

*Name collisions that cost someone a mistake. Kept here because they are facts about
a moment in the codebase, not about the law.*

### D-1 — "Tier" carries three unrelated senses

**Bears on:** `CONST-IV-1` · **As of:** 2026-08-10 (box-scan A10)

1. **Epistemic / evidentiary tier** — the constitutional one, Article IV.
2. **Agent-trust tier** — an agent's authority level (WORKER / ENGINEER / OPERATOR in
   the fleet roster; the "authority tier" §0.3 forbids self-raising; the
   `tier_change` verb in the syscall table).
3. **Informal ordinal labels** — non-normative section or priority markers in design
   docs and manuals ("TIER 1/2/3" phase headers; "Tier-1/Tier-4" checkpoint levels).

Senses (2) and (3) never promote knowledge.

**And a harder fact than ambiguity.** A 2026-08-27 fan-out survey, sealed
(`1878ea86-0b2c-5f1d-96e8-c4641f4f028b`), found the box holds *"three mutually
incompatible trust-tier models"* — along with *"hash-chained ledgers implemented four
to six times, persona definitions scattered across three repositories, calibration
scoring in three places."* Sense (2) is not one model with three names. It is three
models.

### D-2 — "Independent Witness" vs. "independent source"

**Bears on:** Definitions, `CONST-IV-2` · **As of:** 2026-08-10 (box-scan A10)

The constitution's failure-mode-divergence bar is the one canonical meaning. It must
not be confused with the weaker **"independent source"** test in the reaction engine
— a ≥2-web-domain count, satisfiable by one actor buying two domains — which was
renamed away from "witness" precisely to keep the distinction.

That the weaker test is genuinely weak is measured, sealed
(`1a704d54-f132-5492-a9ba-a4d5a43ed2e5`):

> *"Two of the ribbit row's six domains are the article being checked and a post
> quoting it nearly verbatim. The rule counts them as two independent sources."*

Where design notes say "independent witness" for cross-base embedding matching, they
invoke the charter bar, not the domain count.

### D-3 — Two objects named `nest_rules.json`

**Bears on:** Appendix A · **As of:** 2026-08-10 (box-scan A10 / A4)

The **unbuilt constitutional rules-as-data projection** — the machine-readable
compilation of the decision-class tables, keyed by Trace ID — shares a filename with
a **shipped file-classifier** in the nest content pipeline. They are unrelated. The
projection is the canonical referent wherever the name appears in charter or
governance prose. Naming the projection artifact distinctly remains open.

### D-4 — A name reused destroys the identity it replaces

**Bears on:** `CONST-I-1`, `CONST-I-3` · **As of:** 2026-08-31 · **Status:** open

Sealed (`bd1c947b-3cbe-5cd9-88ec-066ca1a275d3`):

> **"Two dead men share a nickname. What happens when the second is sealed?"**
> *"The first is destroyed. `EntityResolver.seal` inherits `add_pair`'s overwrite; the
> sibling recipe retires and keeps. Left open."*

**What it bears on.** I.3 makes identity issuance and revocation reserved acts. In at
least one alias store, reusing a name performs an unrecorded revocation as a side
effect of a seal — the destroyed identity leaves no entry. A revocation that nobody
authorized and the record does not show is the defect I.3 exists to prevent, reached
by a path I.3 does not describe.

---

## Retired citations

*Kept so a reader who finds them in an old draft knows they were removed on purpose.*

| Citation | Where it was | Retired | Why |
|---|---|---|---|
| `core/n2n_packets.py:69`, `:111` | Open Operator Decision #3 (ΔΣ=42) | 2026-07-27, box-scan B8 | File not present in this checkout or anywhere in the fleet. The recovered *meaning* stands; the enforcing artifact remains to be located or built. |
| `README.md:201` | Open Operator Decision #3 | 2026-07-27, box-scan B8 | Same. |
| `WILLOW_OPERATING_CONTRACT.md:231` | Open Operator Decision #3 | 2026-07-27, box-scan B8 | Same. |
| `core/safe_agents.py` (+ `sap` middleware, `fylgja pre_tool`) | Appendix A, Article II row | 2026-08-31, Draft 0.8 | Archived repository, not on disk. The clause is enforced **differently** — see Case 8. |
| Every remaining row of Appendix A's enforcement table | Appendix A | 2026-08-31, Draft 0.8 | Superseded by the generated coverage artifact. A hand-maintained table of implementation names is a stale citation with a schedule. |

**The pattern these share.** Every one was a *downward* reference — the law naming
the machinery. None of the fleet's *upward* references (code citing `CONST-*`) has
ever gone stale, because a Trace ID does not move when a file does.

---

## Open, and not decided here

- Five of Article 0's six clauses have no lineage case (Case 4 covers §0.2 only).
- Case 5's question — whether the verifier string is an unenforced covenant or a
  label on a signature that *is* the gate — is with the package's maintainers.
- Case 7 names a hole in VI.4 and XI: a checker wrong about itself while reporting
  green. No clause covers it and Draft 0.8 does not add one.
- D-1's "three mutually incompatible trust-tier models" is recorded, not reconciled.
- The Record's topology has changed without the constitution noticing: a subordinate
  local chain that best-effort mirrors upward into the shared ledger, cross-linked by
  hash. VI.3 describes divergent peers, not this. Flagged, not drafted.

---

*Opened 2026-08-31 with Draft 0.8, carrying nine cases and four disambiguations out
of the constitution and adding six that had never been written down. Cases cite the
law. The law does not cite back.*
