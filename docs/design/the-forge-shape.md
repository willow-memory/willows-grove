# The Forge — the shape, as talked out 2026-08-30

Captured from a working conversation, before it was lost. It lives here because
the architecture map is here; it may want to move into `forge-play/Forge` once
the shape settles. Nothing below is built unless it says so.

Written down for a specific reason: a survey the night before found the corpus
holds **8,340 claims about what the code does and none about why any of it
exists**, because the corpus extracts committed files and intent lives in
transcripts nothing reads. This is that failure being caught in the act.

---

## 1. What the Forge is

The place where 10,000 kinds of things get built — and the only part of the box
that was built to **find out** rather than to record. Everything else keeps
books: Nestor records what a human checked, FRANK records what happened, the
corpus records what the code says. The Forge states a confidence, builds the
thing, and learns whether it was right.

`forge/calibration_ledger.py` implements exactly that loop and **has never been
called once**. `~/.forge` does not exist because nothing has ever had a
prediction to record. The reason is not neglect: `stub_builder` emits
`hello_world_command` and nothing else, so there has never been a build real
enough to be wrong about.

An APK is the first target that isn't hello world. It compiles or it doesn't,
installs or it doesn't, runs on a device or it doesn't. **Ground truth arrives
on its own**, which is the input the calibration ledger has been waiting for.

## 2. The entry

The unit is a **project**, not a user — many projects live on one box.

A person opens the app or the CLI, and **Vishwakarma** asks:

> **What's the first bite?**

*Bite* is already the Forge's own unit of work (`bite 3 of the learning
layer`), so the onboarding question and the thing the checkpoint/FSRS machinery
schedules are the same object. No translation layer.

First run is onboarding: **scripted questions, model synthesis only at the
leaves.** What are your ideas, what do you want to accomplish. The questions do
not drift because they are not generated. Same discipline as the rest of the
box — the deterministic part stays deterministic.

## 3. From a sentence to a major

A real opening sentence contains almost no spec:

> *"I got sum kol sites for app to spin"*

That is not a reasoning problem. It contains **two keywords** — `site` and
`app` — and a regex finds both. They map to different majors: `site` → web;
`app` → web, mobile, or desktop.

Two candidates and no way to choose is **a detectable condition with a scripted
response: ask.** The next node is a disambiguating question, not a guess.

This is the three-state contract in a new place. Nestor answers `pending` when
nothing verified matched rather than improvising; Jeles returns `found: False`
with candidates. Ambiguity is information the flowchart consumes, never a
failure the model papers over.

**The first artifact to build is the keyword → major table.** A flat file
somebody can read and argue with.

## 4. The almanac gains a tech rung

Working name **`almanac-tech`** — not settled.

It holds two things, and holding them together is the point:

- **official documentation, pinned per version.** `c++ v0.0.0.1`,
  `windows dev v whatever`. The doc set for *that* version, held — not queried
  live. This is H-5 exactly: public reference data, held not fetched, the same
  for every household, names nobody. `as_of` must be a literal, or a pinned doc
  set quietly becomes a live feed wearing a version number.
- **the awesome lists, with their criteria.** `awesome-sovereign-software`
  moves here — 120 entries, 35 sections, a stated five-point test, and every
  entry documenting its exit plan.

**Why together:** it puts the accounting bar in one place. *Here is what the
docs say. Here is what the lists say.* A builder asking "what do I build this
with" gets both from the same shelf, and both carry their basis.

### Criteria are what make a list citable

A list with a stated test is a source you can quote and a reader can check. A
list without one is a pile of links wearing a badge. The Forge must never hand
those to a builder as if they were the same thing — that is the hollow
`verified_by` problem in a new costume.

So a **criteria registry** falls out, three columns and no more:

```
list · what it covers · does it state criteria (and what are they)
```

It stays a *registry*, not a curation project. "The best lists" needs taste and
maintenance and rots; "lists, and whether they state a bar" is checkable by
anyone and stale-proof, because a list either has a criteria section or it does
not. That is a fact, not an opinion.

The **major picks the list** — the same keyword table doing a second job.

## 5. How documents get in

**The Nest already solved this**, and it was built for something else.

> *"Dump your life and let the pigeon figure it out."* Walk a folder, extract
> text — OCR / PDF / docx / plaintext — classify fragments by meaning through a
> **regex → local-embedding → LLM cascade**, write a canonical SQLite DB.

Format-agnostic, no commit sha required. It answers the provenance question the
corpus extractors could not: `repo@sha:path#anchor` has no meaning for a PDF
pulled from an archive.

**One inversion.** The Nest's wall exists because its source is a person:

> *"relative/structural shape is process (shareable); absolute content is
> person (walled)"*

Correct for journals, backwards for a C++ spec. Public documentation has no
person in it — the content **is** the shareable part, and structure-only
promotion yields a taxonomy of a manual you still cannot quote. The Apple IIe
case needs the actual opcode table, not a count of opcode-shaped fragments.

So: same engine, and **which side of the wall you land on is a property of the
source, not of the reader.**

Jeles is the fetcher. It already reaches institutional sources with provenance
and rungs; what is missing is that it *gives to the almanac*.

## 6. Nestor at the centre — the connections, not the pairs

Nestor has never stood at the centre of anything, and the reason is visible:

```
decision_edges       0 rows
decision_evidence    0 rows
decision_warrants    0 rows
```

Plus `memory_lineage`, `memory_edges_to/from`, `superseded_by` — the whole
connection layer, built and never populated. All 599 seals are pairs. **Nothing
has ever been an edge.** 11,061 corpus claims, not one relation between two of
them.

### The test case that cannot be solved by search

Reproducing something built in 1982 on an Apple IIe. The docs and lineage
documentation still exist, in parts. To rebuild it you need: this instruction
in this manual → that opcode → this emulator's implementation → that flag which
changed in 1987. **Every hop is a lineage question.** A blob can hold the manual
and cannot hold *"this and that are the same thing thirty years apart."*

### So the division

- **the almanac holds the documents** — pinned, public, identical for everyone
- **the project's nestor holds the connections** — every dep, module, runtime
  and doc that Kart will actually run, and the edges between them, added one at
  a time as the build grows

Per-project is the right grain: not the fleet store with its 599 seals, but a
store whose whole content is *this build's world* — disposable, portable, ships
with the project. The same property that made `willow_personal` its own
database rather than a column.

### And the blob plan dies

- a blob makes the agent read the manual
- a corpus makes the agent **ask the manual and get a cited answer**
- edges let it ask **across** manuals, which is the only part a blob cannot do

The corpus lane is already correct for this by accident of design: all 11,061
claims are `draft`, none sealed, because it is *"one non-authoritative corpus
lane… exposed only as attributed, authority-free drafting context."* **You do
not seal the C++ spec. You cite it.** Seals and documents never touch.

### The dogfooding is what makes this reproducible

19 of 24 repositories are pinned to one extractor digest. One extractor,
nineteen codebases, same claims, same provenance. That generality was not
designed; it fell out of having to eat 24 repos that disagreed about
everything. The intake contract it produced:

- a source, anything walkable
- a declared extractor, content-hashed with `provenance.py`
- claims with resolvable origin
- a refresh plan **derived from what is stored**, never a maintained list
- honest refusals — dirty tree, missing checkout, unresolvable toolchain
- tombstones — retired reads *retired with a forwarding pointer*, not *refused*
- a miss log — what was asked that nothing answered

**The domains are arbitrary.** `symbol → docstring` is not privileged.
`opcode → mnemonic`, `error_code → cause`, `api_version → successor`,
`flag → semantics_in_1987` — same two columns, same machinery. The corpus never
knew it was about code; it only knew it was about pairs with provenance.

## 7. The Socratic method, explained

Held back from promotion because it *"was tested and working and I never
understood how."* Here is how, and **there is no questioner anywhere** — which
is why it was hard to see.

1. A checkpoint makes the maker **decide** (D8), and D9's thesis is that the
   deciding has to be real, not a rubber-stamp.
2. The maker writes a **rationale**.
3. `friction_score(text, context)` scores how *other* it is on [0,1] — pushback
   markers, grounding markers, **novelty** (`len(a_words - u_words) /
   len(a_words)`, the unechoed fraction), asking.
4. Same scorer, pointed the other way. willow-mcp aims it at an **agent's**
   turns to catch mirroring. The Forge aims the identical vendored scorer at
   the **maker's own rationale**. *"Yes, sounds good"* scores near 0.
5. The score feeds the scheduler:

```
RUBBER_STAMP_FLOOR   = 0.34
_HARD_MAX_ENGAGEMENT = RUBBER_STAMP_FLOOR    (imported, not a second literal)
_EASY_MIN_ENGAGEMENT = 0.66

engagement < 0.34  →  Hard  →  FSRS resurfaces it SOONER
engagement > 0.66  →  Easy  →  pushed OUT
```

**Wave a decision through and it comes back sooner. Argue it and it goes away
longer.** The Socratic feel is emergent — the system returns to what you did not
think about. It is not detecting whether you were *right*; it detects whether
you *engaged*, and lets FSRS do the rest.

Three refusals it is careful about:

- **it never blocks** — *"a gate that blocked a seal on a low score would be
  exactly the frictionless-in-reverse coercion the friction primitive refuses
  to become"*
- **deterministic and model-free** — pure stdlib. *"A sandboxed build cannot
  game a scorer that never runs inside it."*
- **it runs outside the party it watches** — the store scores the maker.
  *"A mirror cannot audit itself."*

## 8. What flows back

**Not people's apps. The shape of how things connected.**

That is the Nest's wall, already decided, unchanged in a word — structure is
process and travels; content is person and stays. It is the fourth independent
arrival at that line, after the Nest's bridge, corpus-lens's Guard, and
homestead's I-31 (counts only, categories that fail a re-identification check
going **absent, not zero**).

Three properties follow:

- **It cannot leak, structurally.** Not a promise — there is nothing to look at.
  `this dep + that runtime + this doc version → worked` does not contain an app.
- **It is the part that compounds.** Ten thousand apps teach nothing. Ten
  thousand *builds* teach which combinations work, which docs were wrong, which
  dep breaks against which runtime, which 1982 manual maps onto which emulator
  flag.
- **A shape contribution needs no review.** A code PR needs a human to read it;
  an edge is either reproducible or it is not — and the machinery to say which
  exists, because a claim carries its origin and a warrant carries a recipe and
  an expected digest. Contribution stops being a social process and becomes a
  measurement. Nobody has to *decide* to contribute; the build already knows
  what it connected.

### And it is an exit plan

`awesome-sovereign-software`'s premise is *"if the vendor vanished tomorrow,
everything still works,"* and every entry documents how you walk away with your
data. A Forge user's exit plan is trivially satisfiable: **they keep everything
they made, and the only thing that ever left was topology they could regenerate
anyway.** The Forge would pass the test its own list publishes.

## 9. Which model runs it

Not one large model. The job was already shrunk seven times, by seven authors,
for seven separate reasons:

| piece | what it removes from the model |
|---|---|
| Nest cascade | regex → embedding → LLM; most fragments reach no model |
| Jeles' judges | may only demote, veto, phrase — never create, propose, cite |
| `friction_floor` | model-free entirely; the Socratic loop needs no model |
| onboarding | fixed questions; synthesis only at the leaves |
| the flowchart | the graph is decided, the language is not |
| nestor edges | a precomputed connection is a traversal, not an inference |
| the corpus | ask and get a cited passage instead of reading a blob |

Convergent arrival, same shape as decision `0227`: **make the model's job small
enough that being wrong is cheap and visible.**

What still wants a large model, honestly: turning a person's opening sentence
into a real project shape — though §3 shows even that is mostly keywords plus a
disambiguation tree — and **writing the code**. Two expensive calls, at the top
and at the point of writing; twenty cheap steps around them. A very different
bill from "an agent runs the Forge."

---

## Decisions taken

- The awesome list **moves** — into the almanac's tech rung, beside the docs,
  so the accounting bar sits in one place.
- Contribution is **shape, never content**.
- The project store is **per-project nestor**, not the fleet store.
- Documents are **cited, never sealed**.

## Open

- The name. `almanac-tech` is not settled.
- Whether this document belongs here or in `forge-play/Forge`.
- `plan.py` has no notion of majors; a second major forces it.
- The toolchain bind — nothing binds `forge-play` into Kart (68 binds, zero
  mention). See `governance/architecture/willow-v08-toolchain-path.drawio`.
- `~/.forge` symlink missing; `forge-play/.forge` exists and is empty.
- `promotion.json` carries `host_repointed: false` — the recorded reason the
  Forge was never fully promoted.
- Documentation and GitHub both need updating for the list's move.
