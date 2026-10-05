# The one script: proposals from session 2026-10-02

## Start here: the one script, stripped down (2026-10-05)

[`hashing-session-handoff-2026-10-05.md`](hashing-session-handoff-2026-10-05.md)
is an outside pass that saw only the tracked repo. It cuts the one script to
two steps:

1. **Take a picture.** Hash every file and keep the list of paths and hashes.
   One hash over the list is the picture's fingerprint.
2. **Compare.** Same fingerprint means nothing changed; otherwise each file is
   added, removed or changed.

Everything below waits until a real change asks for it, added back one at a
time: explain (every change carries a reason), accept (the new picture becomes
the baseline, chained to the last), seal (the human signs the fingerprint).
The same pass reviews the skeleton: the record chain can be truncated or
rehashed undetected, `h16` keeps 64 bits, and one garbled line crashes boot.
The desk checked those three against `onescript/record.py`, and they hold.
Agent-reported throughout; a proposal, not ratified as a build.

### The two steps already exist: file integrity checkers

*2026-10-05. The operator: "do you recall if there is already a script in the
world that already does what I want, just the simple?" Then: "if we took
tripwire from 1992, would all 4 needed to be added on to make a full package".
The desk's answer is from memory, with no web lookup; treat dates as claims to
verify.*

Picture and compare is a file integrity checker, and the idea predates AI by
decades: Tripwire (1992, Purdue), BSD `mtree` (about 1990), AIDE (1999). None
is on the box (Kart `JLCEV1NJ`: `aide`, `mtree`, `bsdtar`, `hashdeep` and
`tripwire` absent; no package installed). Adding one is an apt install, which
is egress and the operator's act.

**What the 1992 Tripwire already covers, against the handoff's add-backs:**

| Piece | 1992 Tripwire | Still to build |
|---|---|---|
| Picture + compare | has it: a baseline database, and a report of added, removed and changed files | nothing |
| Expected changes (the handoff's open question) | has it: a policy file sets what each path may change, and what to ignore | nothing |
| Attributes beyond content (`snap.py` review, problem 5) | has it: mode, owner, size, inode, timestamps | nothing |
| **1. Explain:** every change carries a reason | no: it reports a change, never why | **all of it** |
| **2. Accept:** the new picture becomes the baseline, chained to the last | half: update mode replaces the baseline and overwrites the old one | the chain: each baseline carries the previous fingerprint |
| **3. Seal:** the human signs the fingerprint | weak: in 1992 the protection was write-protected media; signed databases came with Tripwire 2.x (about 2000), keyed by a passphrase | a seal by the human's key, recorded as a human act |
| 4. Everything else | not its job | stays off until a real change asks for it |

**The catch with 1992 itself:** SHA-256 didn't exist until 2001. The original
Tripwire hashed with MD5, Snefru and CRC, and MD5 is broken. The pre-AI line
is March 2020, not 1992, so any pre-2020 release fits: AIDE (SHA-256), Open
Source Tripwire, or `snap.py` on Python 3.8.2, each checked by its published
hash.

**So the full package is an old checker plus two new pieces:** explain, and a
chained, sealed accept. Those are the two with the human in them.

**`snap.py`, if it's the checker** (desk review of the handoff's script):
- it fails to import on Python 3.8: `dict[str, str]` needs 3.9 or
  `from __future__ import annotations`
- it writes its baseline into the folder it photographs
- it reads each file whole into memory
- one unreadable file stops the run
- it sees content only, not mode or symlinks
- its baseline write isn't atomic

The fixes add about 20 lines, still stdlib only.

### What the box already has, and what that leaves (desk, agent-reported)

*The operator asked "anything else you would like to add?", then said
"please". Each point narrows the job.*

1. **The picture already exists.** `~/Forge/workshop/boxhash/box_hash.py`
   hashed 1,155,461 files (2026-10-03), with resumable batches and a hash per
   batch list. The missing half is the compare. One catch: its shards keep a
   120-character sample of every line's text, which is how secrets reached
   `out/` and `play/`. **A baseline holds hashes only, never content.**
2. **A picture only covers what it could see.** `box_hash.py` ran in Kart, so
   the vault and `~/.cache/huggingface` were never in it. From a sandboxed
   picture, "nothing changed" means "nothing visible changed". **Every
   picture records where it was taken from, and lists the paths it couldn't
   read as unreachable rather than leaving them out** (the three-state rule).
3. **Git already covers the repos.** For tracked files, a commit is the
   picture and `git status` is the compare. The checker is needed only where
   Git isn't: `$WILLOW_HOME`, the venvs, `~/.claude`, the Nest, untracked
   work.
4. **Most explanations already exist.** A change the session made itself
   carries its reason in the record (the PostToolUse pointer, "every write
   adds its own pointer"). Only the unexplained remainder goes to the human,
   as "1 new item needed for authorized user". The same compare gives
   `deep_thought` its "only what's new" cut: the previous screen against the
   new one.

### The stack: hash, one script and the operator's words on top of each other

*2026-10-05, desk session c3d31e6e. The operator: "stack it all up, whatever
from just the hash, one script, human chunks of it", then "put the stack in
the one script doc". The merged-tables method ("what merges, what stands out
when the pile is on top of itself?", next-pile.md) run on the ideas
themselves. Sources: the hashing handoff, this folder (README, workflow.md,
next-pile.md, `onescript/`), the operator's words verbatim, and the flowering
experiment. Agent-reported; a reading, not ratified.*

A ✓ means the source says it. Height is how many sources stack on the row.

| # | Point | Hash handoff | One script | Operator's words | Flowering | Height |
|---|---|---|---|---|---|---|
| 1 | Every thing gets a hash, and the hash is its identity | ✓ fingerprint | ✓ pile pointers carry a hash; a hash check comes before keywords | ✓ "gave each plot it's own hash" | ✓ `link_id`, excerpt ids | **4** |
| 2 | New things cite older hashes, up the list | ✓ hash chain, Merkle | ✓ record chain | ✓ "plot 1 (hash#), plot 2 (hash) up the list" | ✓ a cite is an excerpt id or an earlier `link_id` | **4** |
| 3 | Pointers, not prose | ✓ "a baseline holds hashes only, never content" | ✓ "the pile holds pointers, not the full files" | ✓ "Not the prose, but just the points" | ✓ only `{excerpts, joins[]}` goes into the next call | **4** |
| 4 | Code first, model last | ✓ "Git already does steps 1 and 2" | ✓ "the agent is the last call" | ✓ "It starts when it's need. Ends when the job is done. ESCILATE." | ✓ D0 13/13 (10 against fixture gold, 3 routed against the ruling); ≤ 0.0 cloud per act on 15 counted acts, rubric pending (§13) | **4** |
| 5 | Only a human makes it true | ✓ "the human signs the fingerprint" | ✓ the seal is `COMMIT`; the truth rule | ✓ "by a human that only a human could produce" | ✓ the operator's rubric; "Lets keep the tree", sealed bfe001f7 | **4** |
| 6 | Three states, never collapsed | ✓ a hash per panel payload | ✓ the reachability gate | ✓ INVARIANTS §1 | ✓ the materials check | **4** |
| 7 | Pile it up; what stacks is what matters | ✓ identical records dedupe by hash | ✓ `merge_flows`; mass decides attention | ✓ "what merges, what stands out when the pile is on top of itself?" | — | **3** |
| 8 | The model's job is connections | — | ✓ "flowering on material already gathered" (workflow §2c) | ✓ "Making connection between a group of ideas that a human hasn't seen yet." | ✓ joins, chain depth | **3** |
| 9 | Picture and compare | ✓ `snap.py` | ✓ B2 state check, reverse three-way | ✓ "the simple", Tripwire | — | **3** |
| 10 | A pre-AI foundation | ✓ Python 3.8.2 by checksum | ✓ the VSOCK pre-AI gate | ✓ the operator's idea | — | **3** |
| 11 | The database builds itself | — | ✓ write-ahead log → views → `COMMIT` | ✓ "deterministic postgres that builds itself" | — | **2** |
| 12 | The 3 / 7 / 13 / 23 rollup | — | ✓ auto flags, the ladder | ✓ "grouping the 23's by 3" | — | **2** |
| 13 | Once / session / permanent | — | ✓ `gate.allow` | ✓ "Run Once. Run For session. Run perm." | — | **2** |

**The tallest stacks, read down, are the system in five sentences:**

1. Everything is a hash.
2. Everything new cites the hashes it rests on.
3. Only hashes and pointers move; prose stays where it lives.
4. Code does the work, and the model is called last, only to propose connections.
5. Nothing is true until a human seals it.

**What the overlay connects that no single source does:**

| Overlap | Connection |
|---|---|
| Row 2 on row 5 | The review's worst hole (the record chain can be cut or rehashed, because its tip is stored nowhere) is closed by the tallest stack: the human seals the tip hash at check-out. |
| Row 7 on row 8 | The model never searches for connections. Code stacks the tables; the model looks only at what stands out. |
| Row 3 on the boot | A boot built from rows 1–3 is a list of hashes. This session's `session_enter` returned 173,921 characters. |
| Row 9 on row 2 | Each picture cites the previous fingerprint (the handoff's "accept"), so picture, compare and chain are one mechanism. |

**Thin stacks, still open:** rungs 7 and 17 (the operator's to define);
explain, every change carries a reason (named, not built); T1b chain depth
(the one flowering measure never run); `h16` at 64 bits and the garbled-line
crash in `record.py` (desk-confirmed, not fixed).

**Stripped down, the one script is picture, cite, seal.** Everything else is
a view built on those three.

### The security core: the model never sees the box

*2026-10-05, desk session c3d31e6e. The operator: "what is security. It's just
a box that has to be filled out correctly. So if the model never even knows
the Box exists and is never given the opportunity to see any other box except
the one or the ones that it has scope too", then "That's the core of it", then
"add the security core to the one script doc". The readings and prior art
below are agent-reported; the prior art comes from abstracts only. Not
ratified.*

**The core, as one row:** the model is served only the points in its scope,
named by hashes it can't guess, and returns only proposed rows. Code fills
out every box, and the human seals. The model never sees a box, so it has
nothing to fill out wrong.

It needs no new row in the stack. It is what the five tallest rows add up to:

| Stack row | Security consequence |
|---|---|
| 1. Everything is a hash | Scope is a set of hashes |
| 3. Only hashes and pointers move | Serving is choosing which hashes |
| 4. Code first, model last | The model has no hands: no tools, no forms, no doors |
| 5. Only a human makes it true | The seal is the only write |

**Why the machinery shrinks.** MCP tools, the Kart sandbox, envelopes,
leases, hooks and session attestation exist because a model runs things. The
cross-session pile shows the cost: 1,699 waits, 163 + 163 grant churn and 247
refused shell calls (next-pile.md, "The pile on top of itself"). When code
drives, security is no longer "how do we stop the model doing harm with its
tools?" but "what are we willing to show it?"

**What is already in place:**

| Mechanism | Where |
|---|---|
| The model gets only `{excerpts, joins[]}` | flowering §1.3 |
| A cite outside the served pool is `link_fail`: caught by code and sent to flowering (addressed to willow), never accepted as an answer | flowering §13 |
| An act with any uncitable excerpt goes to flowering before any model call | flowering §13 (willow-bot #79) |
| A grant is answered only with the human's seal over exactly `allow:<capability>:<scope>` | next-pile.md, the capability door |

So scope is enforced by the same check that keeps joins honest: a hash the
model was never served is a name it can't know, and the validator catches it
and escalates the act rather than accepting it.

**Shared SOIL.** The operator, the same session: "I don't think were going to
need the shared soil anymore." The reading: each session's B1 store holds its
own record and pile; cross-session lookups are piles merged by hash
(`merge_flows`, a view rebuilt on demand); the one shared thing left is the
seal ledger, append-only and written only by the human.

**Where it can still leak: the content inside a served box.**

| Risk | Example | Answer in this design |
|---|---|---|
| Injection in served text | An excerpt says "ignore your instructions" | The model has no hands; the worst case is a bad proposed row, which stays unverified |
| Inference across boxes | Harmless points that, together, identify a person | Judge scope on the combination, not box by box (the mosaic rule) |
| Guessable hashes | A plain hash of low-entropy content (a PIN, a name) reverses by enumeration | Served ids are keyed (HMAC) or random, never plain content hashes; `h16` at 64 bits is too short |
| The text going to the human | A proposed row worded to talk the human into sealing | The seal stays a human act; the human reads the points, not only the model's sentence |
| Seal substitution | Janus (below): an approval keyed to an attempt was counted for a different proposal, 100 → 1,000,000 | **A seal binds to one hash, never to an attempt or a session** |
| The serving code | A bug serves the wrong box | The real attack surface. Keep it tiny, readable and sealed: the pre-AI foundation (stack row 10) |

**Prior art** (search 2026-10-05, Jeles first, then the web; abstracts only;
open question logged as gap `f8680acc08e6`):

| Piece | Published? | Where |
|---|---|---|
| The model sees only references | Yes | Dual LLM pattern (Willison, 2023); CaMeL (arXiv 2503.18813) |
| Code drives; the model never picks the path | Yes | Blueprint First, Model Second (arXiv 2508.02721) |
| Proposals and approvals in a signed hash chain before anything runs | Yes | Janus (arXiv 2609.38266) |
| Fixed-shape output from the model that touches data | Yes | APPA (arXiv 2607.24625) |
| Trust the architecture, not the model | Yes | LATTICE (Frontiers in AI, 2026) |
| Truth, not just action, made only by a human seal | Not found | Janus gates effects; a human answer is one input among validators |
| Scope chosen by stacking hashed piles | Not found | — |
| The model's only job is proposing connections | Not found | Elsewhere the model still does bounded tasks |
| A pre-AI foundation under the serving code | Not found | — |

The operator, after reading Blueprint First: "The way they were describing
the workflow that they were using. Trying as hard as they could to make it
most of it deterministic, instead of reasoning." The difference the desk
reads (agent-reported): their blueprint is written by an expert before the
first run; here the procedure accumulates from what repeats, offered at the
third ask and sealed by the human.

The papers are in `~/Forge/workshop/papers-agent-security-2026-10-05/`
(outside the repo), with `READING-ORDER.md`.

### Where the reading lands: one script, serve, one hook, one key

*2026-10-05, desk session 019xJcd52XquwTaeZYqKL8QH. The operator, sharing the
reading order: "All good deterministic work, but none of it has come together
in one place", then "Add it". The desk hasn't read the papers; this mapping
is from the operator's descriptions of each and the desk's memory of them.
Agent-reported; not ratified.*

The one place is four pieces. Three are built; serve is the one most of the
reading points at, and isn't.

| Piece | Who | Does | Status |
|---|---|---|---|
| One script | code | builds the tables from the record | skeleton in `onescript/` |
| **Serve** | code | writes only the tables in scope to one file the model reads; a table out of scope isn't named, counted or marked | **not built** |
| One hook | the model | Reads; Writes only if the human allows (`hook.py`, PR 107) | built, not wired |
| One key | the human | sets the scope and seals; nothing is true until then | the vault, handled separately |

| Piece | Reading that shapes it | What it takes |
|---|---|---|
| **One script** | Blueprint First; Anthropic, *Building Effective Agents* | Code picks the path, the model never does: a workflow, not an agent |
| | Kim and Spafford 1994, Tripwire | Picture and compare |
| | in-toto (USENIX 2019); RFC 9162, Certificate Transparency v2 | Each step signs what came in and what went out; an append-only hash log with proofs is the record |
| **Serve** | Willison 2023, the Dual LLM pattern | The model gets references, never the box |
| | Miller, Yee and Shapiro 2003; Miller 2006 | Holding a reference is the permission: the one served file is the model's only reference |
| | CaMeL, CaMeLoT, APPA | Capabilities on data: scope sits on the tables, not on tools |
| **One hook** | Saltzer and Schroeder 1975 | Economy of mechanism (about ten lines of code), fail-safe defaults (unknown tools denied), least privilege (Read only), complete mediation (matcher `*`) |
| | Meta, the Agents Rule of Two | The model holds untrusted input and sensitive data but no actions, so it passes by holding none |
| | LATTICE | No piece both decides and judges: the script decides, the model proposes, the key judges |
| | *Design Patterns* (2506.08837) | The six patterns: which is nearest, and what none of them do (open; the desk hasn't placed it) |
| **One key** | Janus | A seal binds to the bytes, never to the request: post-approval substitution moved an approval from 100 to 1,000,000 |
| | *Observability Gap* | Seal the visible points, not the results |
| **Under all four** | Thompson 1984, *Reflections on Trusting Trust* | The foundation: 3.9.0's source is signature-verified (`foundation/`), the compiler that built it is not |

**What the mapping shows:**

- Serve carries the most reading (Dual LLM, capabilities, CaMeL, the Rule of
  Two) and is the piece not built.
- Janus sets a rule for the key. The hook's `"Write": "ask"` approves a
  request; when the key comes in, the seal covers the exact bytes written, so
  an approval can't be moved to something else.
- What no paper does is still the prior-art table's "Not found" rows: truth
  made only by a human seal, scope chosen by stacking piles, and a pre-AI
  foundation.

## The proposals from 2026-10-02

**Status:** draft proposals for the operator to read, edit and ratify. Nothing
here is built into a runtime or sealed. Assessments marked **agent-reported**
are unattested. This builds on the one-box plan (PR #102), and each proposal
is in its own commit so it can be kept, edited or dropped on its own.

| # | File | The proposal |
|---|---|---|
| 1 | [`workflow.md`](workflow.md), [`workflow-shape.mmd`](workflow-shape.mmd) | The workflow: data point 0, the truth rule, boot (B1–B3 and the hard close), every prompt as a bite, the repetition ladder (1 does it, 2 notices, 3 offers), the resolve ladder (the user's sources first, the model last), loops and the reverse pass, the 3B experiment, "the gate is the script", custom and chained gates |
| 2 | [`next-pile.md`](next-pile.md) | The runtime as one script: seven parts by purpose plus `run`, citing the constitution upward. Also: the stamp (who and standing, stamped at the door, never by the model); every change cites what it touches; reverse's triggers; the script-match check; the four close-time pieces; the overnight pool and the morning screen; what the script can't solve and the one who can; **the four gates the close needed** (tests, toolchain, freshness, reachability), with push as a grant card; and **three more layers**: claims (every checkable statement checked against the record before the human reads it), boundaries (everything crossing an edge classed by provenance and carded) and mandate (every act traced to the human words that authorise it, before it runs) |
| 3 | [`onescript/`](onescript/) | A runnable skeleton of #2: stdlib only, 53 tests. `record` (hash chain, stamp, open/close turns, pointers with provenance), `gate` (identity, citations, seals, grant cards, script match; **layer 5** claims, **layer 6** push cards by provenance, **layer 7** mandate), `resolve`, `predict`, `reverse` (three-way, four verdicts, witnesses by family), `boot` (probes and **the four gates**: tests, toolchain, freshness, reachability), `view` (the morning screen), `run` (`checkin`, `turn`, `act`, `say`, `checkout`). It uses [`scripts/scan/script_match.py`](scripts/scan/script_match.py) |
| — | [`day-3/`](day-3/) | Not a proposal: the source of the published **Day 2** DEV post (despite the folder name), the 55 PRs since Day 0, the post sources, and `predictions.json` (P1 and P2, both ungraded; the desk misread a late-night line as P2's grade, retracted 2026-10-02) |
| — | [`posts/`](posts/) | The **Day 3** DEV post source ("The benchmark caught me too"), its cover prompt, and the Kaggle dataset metadata patch that was applied to `rudi193/escalation-benchmark` |
| — | [`incoming/`](incoming/) | Three outside passes, kept by provenance: an Opus 5 session's six proposals against Draft 0.8 (reachability and staleness), a cold Haiku 4.5 session's three proposals, and a pointer to the operator's paper "Basins, Not Walls". Its README reconciles them with this PR, cross-checked against the record, and says what the one script took from each |
| — | [`deep_thought.py`](deep_thought.py) | Read-only probe that carries the sealed Answer (D1, D2, D9, Q13) and measures the box against it. Prints the morning screen (NEEDS YOU → … → GRADES → CHOICES → QUIET). Stdlib only; needs `WILLOW_HOME`. See next-pile.md § "deep_thought.py". Three improvements after the first run: ledger-join seals, write-kind triage, GRADES |
| 4 | [`constitution-proposal/`](constitution-proposal/) | Ten amendments and a neutral-language pass. **They are built on Draft 0.7 and must be redone against Draft 0.8** (which forbids downward references) before any of it goes forward |

**In the skeleton now:** the four gates and the three layers from #2, each
tested against what happened on 2026-10-02. Run for real on the session's box,
the gates reported: `ruff` 0.15.20 on PATH against the pinned 0.16.7; the
constitution proposals built on Draft 0.7 against the law's 0.8; the Forge's
reliability tests unable to run (no `aggregate` here); the system interpreter,
not a venv.

**Taken from the incoming passes:** queue age reported as backpressure;
"enforcement status unknown" when no reconcile is on record; every agreed
claim recorded with `dissent: none recorded`; and a quote checker that reads
prose only. See [`incoming/README.md`](incoming/README.md).

**Not yet:** `run.act` decides and cards; it never performs the act. Keys are
HMAC rather than passkeys. There's no socket or peer check. Mandate rows are
data the human supplies, never read out of their words by the model. It isn't
in willow-bot yet, where D2 (sealed 2026-10-02) homes it.

**Kept local, not in this PR:** the session's map, marks and pile
(`workflow.md` cites `session-flow.md` and `marks.json`). They're built from
the session transcript and local memory, so publishing them is a separate
decision.

## Running the tests

```bash
cd onescript && python3 -m pytest -q tests   # 77 tests (24 for the capability door)
```

The Grove's CI doesn't collect these (its `testpaths` is `tests/`). ruff lints
and formats them like everything else.

## Running deep_thought

```bash
WILLOW_HOME=… python3 docs/design/one-script/deep_thought.py        # screen
WILLOW_HOME=… python3 docs/design/one-script/deep_thought.py --json  # rows
```

Read only. Without `WILLOW_HOME` the box probes report `unreachable` rather
than guessing a path. D2 homes the one script in willow-bot; this file sits
here until the operator moves it.
