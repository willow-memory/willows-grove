# The one script: proposals from session 2026-10-02

**Status:** draft proposals for the operator to read, edit and ratify. Nothing
here is built into a runtime or sealed. Assessments marked **agent-reported**
are unattested. This builds on the one-box plan (PR #102), and each proposal
is in its own commit so it can be kept, edited or dropped on its own.

| # | File | The proposal |
|---|---|---|
| 1 | [`workflow.md`](workflow.md), [`workflow-shape.mmd`](workflow-shape.mmd) | The workflow: data point 0, the truth rule, boot (B1–B3 and the hard close), every prompt as a bite, the repetition ladder (1 does it, 2 notices, 3 offers), the resolve ladder (the user's sources first, the model last), loops and the reverse pass, the 3B experiment, "the gate is the script", custom and chained gates |
| 2 | [`next-pile.md`](next-pile.md) | The runtime as one script: seven parts by purpose plus `run`, citing the constitution upward. Also: the stamp (who and standing, stamped at the door, never by the model); every change cites what it touches; reverse's triggers; the script-match check; the four close-time pieces; the overnight pool and the morning screen; what the script can't solve and the one who can; **the four gates the close needed** (tests, toolchain, freshness, reachability), with push as a grant card; and **three more layers**: claims (every checkable statement checked against the record before the human reads it), boundaries (everything crossing an edge classed by provenance and carded) and mandate (every act traced to the human words that authorise it, before it runs) |
| 3 | [`onescript/`](onescript/) | A runnable skeleton of #2: stdlib only, 47 tests. `record` (hash chain, stamp, open/close turns, pointers with provenance), `gate` (identity, citations, seals, grant cards, script match; **layer 5** claims, **layer 6** push cards by provenance, **layer 7** mandate), `resolve`, `predict`, `reverse` (three-way, four verdicts, witnesses by family), `boot` (probes and **the four gates**: tests, toolchain, freshness, reachability), `view` (the morning screen), `run` (`checkin`, `turn`, `act`, `say`, `checkout`). It uses [`scripts/scan/script_match.py`](scripts/scan/script_match.py) |
| — | [`day-3/`](day-3/) | Not a proposal: the Day 3 DEV post draft (the operator edits and publishes it), the 55 PRs since Day 0, the post sources, and `predictions.json` (P1, and P2 as graded by the operator: "1 + (2 + ε), where ε → 0") |
| 4 | [`constitution-proposal/`](constitution-proposal/) | Ten amendments and a neutral-language pass. **They are built on Draft 0.7 and must be redone against Draft 0.8** (which forbids downward references) before any of it goes forward |

**In the skeleton now:** the four gates and the three layers from #2, each
tested against what happened on 2026-10-02. Run for real on the session's box,
the gates reported: `ruff` 0.15.20 on PATH against the pinned 0.16.7; the
constitution proposals built on Draft 0.7 against the law's 0.8; the Forge's
reliability tests unable to run (no `aggregate` here); the system interpreter,
not a venv.

**Not yet:** `run.act` decides and cards; it never performs the act. Keys are
HMAC rather than passkeys. There's no socket or peer check. Mandate rows are
data the human supplies, never read out of their words by the model. It isn't
wired into Rat (D1 is unsealed).

**Kept local, not in this PR:** the session's map, marks and pile
(`workflow.md` cites `session-flow.md` and `marks.json`). They're built from
the session transcript and local memory, so publishing them is a separate
decision.

## Running the tests

```bash
cd onescript && python3 -m pytest -q tests   # 47 tests
```

The Grove's CI doesn't collect these (its `testpaths` is `tests/`). ruff lints
and formats them like everything else.
