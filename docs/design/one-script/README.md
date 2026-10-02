# The one script: proposals from session 2026-10-02

**Status:** draft proposals for the operator to read, edit and ratify. Nothing
here is built into a runtime or sealed. Assessments marked **agent-reported**
are unattested. This builds on the one-box plan (PR #102), and each proposal
is in its own commit so it can be kept, edited or dropped on its own.

| # | File | The proposal |
|---|---|---|
| 1 | [`workflow.md`](workflow.md), [`workflow-shape.mmd`](workflow-shape.mmd) | The workflow: data point 0, the truth rule, boot (B1–B3 and the hard close), every prompt as a bite, the repetition ladder (1 does it, 2 notices, 3 offers), the resolve ladder (the user's sources first, the model last), loops and the reverse pass, the 3B experiment, "the gate is the script", custom and chained gates |
| 2 | [`next-pile.md`](next-pile.md) | The runtime as one script: seven parts by purpose plus `run`, citing the constitution upward. Also: the stamp (who and standing, stamped at the door, never by the model); every change cites what it touches; reverse's triggers; the script-match check; the four close-time pieces; the overnight pool and the morning screen; what the script can't solve and the one who can; **the four gates the close needed** (tests, toolchain, freshness, reachability), with push as a grant card; and **two more layers**: claims (every checkable statement checked against the record before the human reads it) and boundaries (everything crossing an edge classed by provenance and carded) |
| 3 | [`onescript/`](onescript/) | A runnable skeleton of #2: stdlib only, 29 tests. `record` (hash chain, stamp, open/close turns, pointers), `gate` (identity, citations, seals, grant cards, script match), `resolve`, `predict`, `reverse` (three-way, four verdicts, witnesses by family), `boot` (probes), `view` (the morning screen), `run`. It uses [`scripts/scan/script_match.py`](scripts/scan/script_match.py) |
| 4 | [`constitution-proposal/`](constitution-proposal/) | Ten amendments and a neutral-language pass. **They are built on Draft 0.7 and must be redone against Draft 0.8** (which forbids downward references) before any of it goes forward |

**Not yet in the skeleton:** the four gates and the two layers from #2. Push is still not a grant
card, keys are HMAC rather than passkeys, there's no socket or peer check, and
it isn't wired into Rat (D1 is unsealed).

**Kept local, not in this PR:** the session's map, marks and pile
(`workflow.md` cites `session-flow.md` and `marks.json`). They're built from
the session transcript and local memory, so publishing them is a separate
decision.

## Running the tests

```bash
cd onescript && python3 -m pytest -q tests   # 29 tests
```

The Grove's CI doesn't collect these (its `testpaths` is `tests/`). ruff lints
and formats them like everything else.
