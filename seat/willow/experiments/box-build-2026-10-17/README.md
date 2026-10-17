---
kind: doc
name: box-build-2026-10-17
description: The record of the box build — deterministic prediction, one-script, boxes, flowering and the AI GM table joined, built in a sandbox and broken until it held.
b17: BOXB1
---

@markdownai v1.0

# Box build (2026-10-17)

§1 What this is · §2 Files · §3 The three PRs · §4 Run the end-to-end tests · §5 Limits

## §1 What this is

The desk's record of the build that joins the forecast lane, the seeded dice
stream, the exact-odds forecaster, the table's verdict rows, sealed lore, the
code-first table act and the seat's view of a table box. The design followed
`docs/design/forge-convergence.md` §6a and the 10-16 / 10-17 handoffs; where it
departs, `SPEC.md` §2 names the ruling (R1–R23a). Every ruling is a recorded
guess until the human ratifies it. Agent-reported; not ratified.

## §2 Files

| File | What |
|---|---|
| `PLAN.md` | The nine joins (J1–J9) and the build's constraints |
| `BRIEF.md` | What every builder and auditor read first (paths are the sandbox's) |
| `SPEC.md` | The merged spec: rulings R1–R23a, waves, open questions H1–H7 |
| `SPEC-documented.md` | Each join pinned to what the docs already say, conflicts C1–C19 |
| `SPEC-rival.md` | The rival design and the adversarial list T1–T16 |
| `SPEC-tools.md` | codebase-memory and MarkdownAI inside the deterministic flow |
| `e2e/` | The cross-repo tests: W1 loop, W2 rows, W3 act, W4 surface, W4 break (159 passed, 1 strict xfail at hand-off) |

## §3 The three PRs

The code lands in willow-bot (onescript and the deterministic chain),
safe-app-store (the-table) and this repo (the seat). Each PR body names the
others.

## §4 Run the end-to-end tests

They are not in this repo's `testpaths`. They need the three repos side by
side; `BOX_REPOS` points at a directory holding `willow-bot`, `safe-app-store`
and `willows-grove`, and `ONESCRIPT_CBM` at a codebase-memory binary for the
symbol-cite tests (they skip without it).

```sh
BOX_REPOS=<dir> ONESCRIPT_CBM=<cbm> python -m pytest -q e2e
```

## §5 Limits

The drand BLS signature is not verified (the beacon reader is trusted); one
forecast per round holds per box only (the strict xfail); a set-piece move
pick happens after the round is out; `--drand` reaches the network without the
T5 egress lease check.
