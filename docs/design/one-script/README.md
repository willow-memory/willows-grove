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
