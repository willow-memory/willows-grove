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
