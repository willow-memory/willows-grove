# Open branches, as a table (2026-10-06)

*Desk session, 2026-10-06. The operator asked to look at all the open branches
on this repo, then: "Data is data. Put it in the table." Agent-reported; not
ratified.*

## How it's built

- **The source is git.** [`branch-ledger-2026-10-06.md`](branch-ledger-2026-10-06.md)
  is generated from `git rev-parse`, `rev-list`, `log`, `diff --name-only`,
  `patch-id --stable` and `merge-tree`, one fact per line, and every line names
  its branch. Nothing in it is composed. A second run gave the same bytes.
- **It is a snapshot of the branches at generation time.** This branch was at
  `3deb67e` then. Its head moves with every commit, including the one that
  adds this table.
- **One row per branch, rows AM–AR,** after the Gerald grid's AL. There are
  eight columns: head, ahead/behind, dates, latest commit, files changed,
  commits also on another branch, conflicts, and what a merge would do to the
  grids. Master has only the first four, because it is the base and not a
  branch off it. Its other four boxes are silent and say why.
- **"Commits also on"** compares patches, not hashes, so a commit that was
  re-applied on another branch still counts as the same work.
- **"If merged here"** merges the branch into this one in a scratch copy and
  runs `measure --against` on every grid's snapshot. A conflicted merge is
  checked with this branch's tree plus the other branch's version of the
  files it changes (except `CHANGELOG.md`).
- **Links.** The two boxes that name grid boxes, AO8 and AP8, are linked to
  them below, by the same rule as the Gerald links: a box names an address,
  and the link is checked by `cross_table.py link`.
- No PR is open on any branch.

## The grid

<!-- cross-table:grid -->
| | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---|---|---|---|---|---|---|---|
| **AM** `master` | head | the base | commits held | latest commit |  |  |  |  |
| **AN** `ccr-392b8b73-v809qu` | head | ahead / behind | dates | latest commit | files changed | commits also on | conflicts with | if merged here |
| **AO** `ccr-542b5884-0deee5` | head | ahead / behind | dates | latest commit | files changed | commits also on | conflicts with | if merged here |
| **AP** `ccr-8a588c96-jf76ei` | head | ahead / behind | dates | latest commit | files changed | commits also on | conflicts with | if merged here |
| **AQ** `claude/agent-instruction-files` | head | ahead / behind | dates | latest commit | files changed | commits also on | conflicts with | if merged here |
| **AR** `claude/ai-model-smoothing-gentrification-alc5dm` | head | ahead / behind | dates | latest commit | files changed | commits also on | conflicts with | if merged here |
<!-- /cross-table:grid -->

## Where each row comes from

<!-- cross-table:sources -->
| Row | What it holds | Source |
|---|---|---|
| AM | `master` | `branch-ledger-2026-10-06.md`, section master (generated from git) |
| AN | `ccr-392b8b73-v809qu` | `branch-ledger-2026-10-06.md`, section ccr-392b8b73-v809qu (generated from git) |
| AO | `ccr-542b5884-0deee5` | `branch-ledger-2026-10-06.md`, section ccr-542b5884-0deee5 (generated from git) |
| AP | `ccr-8a588c96-jf76ei` | `branch-ledger-2026-10-06.md`, section ccr-8a588c96-jf76ei (generated from git) |
| AQ | `claude/agent-instruction-files` | `branch-ledger-2026-10-06.md`, section claude/agent-instruction-files (generated from git) |
| AR | `claude/ai-model-smoothing-gentrification-alc5dm` | `branch-ledger-2026-10-06.md`, section claude/ai-model-smoothing-gentrification-alc5dm (generated from git) |
<!-- /cross-table:sources -->

## Index

<!-- cross-table:index -->
| Cell | Rule | Source | Share | Standing |
|---|---|---|---|---|
| AM1 | - `master` head: `a111829`, 2026-10-05. | `willows-grove/docs/design/branches/branch-ledger-2026-10-06.md`:8 | 0.60% | unattested |
| AM2 | - `master` is the base every other branch is measured against, and is protected. | `willows-grove/docs/design/branches/branch-ledger-2026-10-06.md`:9 | 1.24% | unattested |
| AM3 | - `master` holds 193 commits. | `willows-grove/docs/design/branches/branch-ledger-2026-10-06.md`:10 | 0.45% | unattested |
| AM4 | - `master` latest commit: One hook across every CLI, xref with two hashes, and constitution Draft 0.9 (#112). | `willows-grove/docs/design/branches/branch-ledger-2026-10-06.md`:11 | 1.68% | unattested |
| AM5 | *source silent: master has no such fact: it is the base, not a branch off it* | — | 0.00% | unattested |
| AM6 | *source silent: master has no such fact: it is the base, not a branch off it* | — | 0.00% | unattested |
| AM7 | *source silent: master has no such fact: it is the base, not a branch off it* | — | 0.00% | unattested |
| AM8 | *source silent: master has no such fact: it is the base, not a branch off it* | — | 0.00% | unattested |
| AN1 | - `ccr-392b8b73-v809qu` head: `3deb67e`, 2026-10-06. | `willows-grove/docs/design/branches/branch-ledger-2026-10-06.md`:15 | 0.80% | unattested |
| AN2 | - `ccr-392b8b73-v809qu` is 15 commits ahead of master and 0 behind, from merge base `a111829`. | `willows-grove/docs/design/branches/branch-ledger-2026-10-06.md`:16 | 1.45% | unattested |
| AN3 | - `ccr-392b8b73-v809qu` commits run from 2026-10-06 to 2026-10-06. | `willows-grove/docs/design/branches/branch-ledger-2026-10-06.md`:17 | 1.02% | unattested |
| AN4 | - `ccr-392b8b73-v809qu` latest commit: docs(gerald): connect the Gerald atoms to the main table. | `willows-grove/docs/design/branches/branch-ledger-2026-10-06.md`:18 | 1.48% | unattested |
| AN5 | - `ccr-392b8b73-v809qu` changes 24 files: `docs/INDEX.md`, `docs/design/gerald/gerald-atoms-map-2026-10-06.json`, `docs/design/gerald/gerald-atoms-snapshot-2026-10-06.json`, `docs/design/gerald/gerald-atoms-table-2026-10-06.md`, `docs/design/gerald/gerald-session-atoms-2026-10-06.jsonl`, `docs/design/gerald/gerald-session-atoms-2026-10-06.md`, `docs/design/gerald/gerald-to-main-2026-10-06.md`, … | `willows-grove/docs/design/branches/branch-ledger-2026-10-06.md`:19 | 19.83% | unattested |
| AN6 | - `ccr-392b8b73-v809qu` has every one of its commits also on: no other branch. | `willows-grove/docs/design/branches/branch-ledger-2026-10-06.md`:20 | 1.20% | unattested |
| AN7 | - `ccr-392b8b73-v809qu` merges with conflicts against: `claude/ai-model-smoothing-gentrification-alc5dm` (CHANGELOG.md). | `willows-grove/docs/design/branches/branch-ledger-2026-10-06.md`:21 | 1.85% | unattested |
| AN8 | - `ccr-392b8b73-v809qu` is the branch the grids live on, so merging it changes no grid. | `willows-grove/docs/design/branches/branch-ledger-2026-10-06.md`:22 | 1.34% | unattested |
| AO1 | - `ccr-542b5884-0deee5` head: `163a982`, 2026-10-06. | `willows-grove/docs/design/branches/branch-ledger-2026-10-06.md`:26 | 0.80% | unattested |
| AO2 | - `ccr-542b5884-0deee5` is 22 commits ahead of master and 0 behind, from merge base `a111829`. | `willows-grove/docs/design/branches/branch-ledger-2026-10-06.md`:27 | 1.45% | unattested |
| AO3 | - `ccr-542b5884-0deee5` commits run from 2026-10-06 to 2026-10-06. | `willows-grove/docs/design/branches/branch-ledger-2026-10-06.md`:28 | 1.02% | unattested |
| AO4 | - `ccr-542b5884-0deee5` latest commit: docs(design): session two — why the classifier denied the CLAUDE.md edit. | `willows-grove/docs/design/branches/branch-ledger-2026-10-06.md`:29 | 1.73% | unattested |
| AO5 | - `ccr-542b5884-0deee5` changes 8 files: `CLAUDE.md`, `docs/design/113-guesses-2026-10-06.md`, `docs/design/113-session-record-2026-10-06.md`, `docs/design/113-session-two-2026-10-06.md`, `docs/design/one-box/README.md`, `docs/design/one-box/instruction-files-2026-10-06.md`, `docs/design/one-script/constitution-proposal/quorum-ruling-2026-10-06.md`, `docs/design/seed-word-count-2026-10-06.md`. | `willows-grove/docs/design/branches/branch-ledger-2026-10-06.md`:30 | 6.12% | unattested |
| AO6 | - `ccr-542b5884-0deee5` has every one of its commits also on: no other branch. | `willows-grove/docs/design/branches/branch-ledger-2026-10-06.md`:31 | 1.20% | unattested |
| AO7 | - `ccr-542b5884-0deee5` merges with conflicts against: `claude/ai-model-smoothing-gentrification-alc5dm` (CHANGELOG.md, CLAUDE.md). | `willows-grove/docs/design/branches/branch-ledger-2026-10-06.md`:32 | 2.02% | unattested |
| AO8 | - `ccr-542b5884-0deee5` merged into `ccr-392b8b73-v809qu` would leave the grids so: grid one: **No longer found:** G5; grid two: No box changed; grid three: **No longer found:** R1, R2, R3, R4, R5, R6; the Gerald grid: No box changed. | `willows-grove/docs/design/branches/branch-ledger-2026-10-06.md`:33 | 3.61% | unattested |
| AP1 | - `ccr-8a588c96-jf76ei` head: `664662e`, 2026-10-06. | `willows-grove/docs/design/branches/branch-ledger-2026-10-06.md`:37 | 0.80% | unattested |
| AP2 | - `ccr-8a588c96-jf76ei` is 19 commits ahead of master and 0 behind, from merge base `a111829`. | `willows-grove/docs/design/branches/branch-ledger-2026-10-06.md`:38 | 1.45% | unattested |
| AP3 | - `ccr-8a588c96-jf76ei` commits run from 2026-10-06 to 2026-10-06. | `willows-grove/docs/design/branches/branch-ledger-2026-10-06.md`:39 | 1.02% | unattested |
| AP4 | - `ccr-8a588c96-jf76ei` latest commit: docs(design): session record — after ask 28, and 13 questions for next session. | `willows-grove/docs/design/branches/branch-ledger-2026-10-06.md`:40 | 1.82% | unattested |
| AP5 | - `ccr-8a588c96-jf76ei` changes 4 files: `CLAUDE.md`, `docs/design/113-guesses-2026-10-06.md`, `docs/design/113-session-record-2026-10-06.md`, `docs/design/one-script/constitution-proposal/quorum-ruling-2026-10-06.md`. | `willows-grove/docs/design/branches/branch-ledger-2026-10-06.md`:41 | 3.37% | unattested |
| AP6 | - `ccr-8a588c96-jf76ei` has every one of its commits also on: `ccr-542b5884-0deee5`. | `willows-grove/docs/design/branches/branch-ledger-2026-10-06.md`:42 | 1.30% | unattested |
| AP7 | - `ccr-8a588c96-jf76ei` merges with conflicts against: `claude/ai-model-smoothing-gentrification-alc5dm` (CHANGELOG.md, CLAUDE.md). | `willows-grove/docs/design/branches/branch-ledger-2026-10-06.md`:43 | 2.02% | unattested |
| AP8 | - `ccr-8a588c96-jf76ei` merged into `ccr-392b8b73-v809qu` would leave the grids so: grid one: **No longer found:** G5; grid two: No box changed; grid three: **No longer found:** R1, R2, R3, R4, R5, R6; the Gerald grid: No box changed. | `willows-grove/docs/design/branches/branch-ledger-2026-10-06.md`:44 | 3.61% | unattested |
| AQ1 | - `claude/agent-instruction-files` head: `5879d44`, 2026-10-06. | `willows-grove/docs/design/branches/branch-ledger-2026-10-06.md`:48 | 0.97% | unattested |
| AQ2 | - `claude/agent-instruction-files` is 1 commit ahead of master and 0 behind, from merge base `a111829`. | `willows-grove/docs/design/branches/branch-ledger-2026-10-06.md`:49 | 1.59% | unattested |
| AQ3 | - `claude/agent-instruction-files` commits run from 2026-10-06 to 2026-10-06. | `willows-grove/docs/design/branches/branch-ledger-2026-10-06.md`:50 | 1.19% | unattested |
| AQ4 | - `claude/agent-instruction-files` latest commit: docs(one-box): how 22 CLIs load AGENTS.md, CLAUDE.md and their own rules files. | `willows-grove/docs/design/branches/branch-ledger-2026-10-06.md`:51 | 1.99% | unattested |
| AQ5 | - `claude/agent-instruction-files` changes 2 files: `docs/design/one-box/README.md`, `docs/design/one-box/instruction-files-2026-10-06.md`. | `willows-grove/docs/design/branches/branch-ledger-2026-10-06.md`:52 | 2.15% | unattested |
| AQ6 | - `claude/agent-instruction-files` has every one of its commits also on: `ccr-392b8b73-v809qu`, `ccr-542b5884-0deee5`. | `willows-grove/docs/design/branches/branch-ledger-2026-10-06.md`:53 | 1.82% | unattested |
| AQ7 | - `claude/agent-instruction-files` merges with conflicts against: `claude/ai-model-smoothing-gentrification-alc5dm` (CHANGELOG.md). | `willows-grove/docs/design/branches/branch-ledger-2026-10-06.md`:54 | 2.02% | unattested |
| AQ8 | - `claude/agent-instruction-files` merged into `ccr-392b8b73-v809qu` would leave the grids so: grid one: No box changed; grid two: No box changed; grid three: No box changed; the Gerald grid: No box changed. | `willows-grove/docs/design/branches/branch-ledger-2026-10-06.md`:55 | 3.20% | unattested |
| AR1 | - `claude/ai-model-smoothing-gentrification-alc5dm` head: `763e9d4`, 2026-10-04. | `willows-grove/docs/design/branches/branch-ledger-2026-10-06.md`:59 | 1.24% | unattested |
| AR2 | - `claude/ai-model-smoothing-gentrification-alc5dm` is 11 commits ahead of master and 38 behind, from merge base `0b63bfb`. | `willows-grove/docs/design/branches/branch-ledger-2026-10-06.md`:60 | 1.90% | unattested |
| AR3 | - `claude/ai-model-smoothing-gentrification-alc5dm` commits run from 2026-10-04 to 2026-10-04. | `willows-grove/docs/design/branches/branch-ledger-2026-10-06.md`:61 | 1.45% | unattested |
| AR4 | - `claude/ai-model-smoothing-gentrification-alc5dm` latest commit: Reapply "docs(claude): rule 9, numbered sections and a contents line at the top". | `willows-grove/docs/design/branches/branch-ledger-2026-10-06.md`:62 | 2.29% | unattested |
| AR5 | - `claude/ai-model-smoothing-gentrification-alc5dm` changes 4 files: `CHANGELOG.md`, `CLAUDE.md`, `docs/INDEX.md`, `docs/design/agnostic-rules.md`. | `willows-grove/docs/design/branches/branch-ledger-2026-10-06.md`:63 | 2.27% | unattested |
| AR6 | - `claude/ai-model-smoothing-gentrification-alc5dm` has every one of its commits also on: no other branch. | `willows-grove/docs/design/branches/branch-ledger-2026-10-06.md`:64 | 1.64% | unattested |
| AR7 | - `claude/ai-model-smoothing-gentrification-alc5dm` merges with conflicts against: `master` (CHANGELOG.md), `ccr-392b8b73-v809qu` (CHANGELOG.md), `ccr-542b5884-0deee5` (CHANGELOG.md, CLAUDE.md), `ccr-8a588c96-jf76ei` (CHANGELOG.md, CLAUDE.md), `claude/agent-instruction-files` (CHANGELOG.md). | `willows-grove/docs/design/branches/branch-ledger-2026-10-06.md`:65 | 4.51% | unattested |
| AR8 | - `claude/ai-model-smoothing-gentrification-alc5dm` merged into `ccr-392b8b73-v809qu` would leave the grids so: grid one: No box changed; grid two: No box changed; grid three: No box changed; the Gerald grid: No box changed. | `willows-grove/docs/design/branches/branch-ledger-2026-10-06.md`:66 | 3.46% | unattested |
<!-- /cross-table:index -->

## Links

<!-- cross-table:links -->
| From | To | Where they touch | Standing |
|---|---|---|---|
| AO8 if merged here | G5 Trailers: `Persona:`, `Ratified-by:` · R1 6. Persona provenance and ratification … · R2 Every commit that changes tracked … · R3 Merge commits are exempt; release-please's … · R4 Every PR body ends with … · R5 release-please's own release PR is … · R6 INVARIANTS.md §11 and §12; scripts/check_persona_provenance.py, … | Box AO8 names these boxes: a merge would leave them no longer found. | unattested |
| AP8 if merged here | G5 Trailers: `Persona:`, `Ratified-by:` · R1 6. Persona provenance and ratification … · R2 Every commit that changes tracked … · R3 Merge commits are exempt; release-please's … · R4 Every PR body ends with … · R5 release-please's own release PR is … · R6 INVARIANTS.md §11 and §12; scripts/check_persona_provenance.py, … | Box AP8 names these boxes: a merge would leave them no longer found. | unattested |
<!-- /cross-table:links -->

## Measure

*Written by `cross_table.py fill --measure`, the same as the other grids.*

<!-- cross-table:measure -->
- **Cells:** 48, of which 44 found (91.7%).
- **Text:** 6475 characters. An even share would be 2.08% per cell.
- **Trim:** 1 cell(s) cut at 420 characters; the index keeps 86.7% of the source text.

| Row | What it holds | Found | Characters | Share | Largest cell |
|---|---|---|---|---|---|
| AM | `master` | 4/8 | 257 | 3.97% | AM4 1.68% |
| AN | `ccr-392b8b73-v809qu` | 8/8 | 1877 | 28.99% | AN5 19.83% |
| AO | `ccr-542b5884-0deee5` | 8/8 | 1163 | 17.96% | AO5 6.12% |
| AP | `ccr-8a588c96-jf76ei` | 8/8 | 997 | 15.40% | AP8 3.61% |
| AQ | `claude/agent-instruction-files` | 8/8 | 967 | 14.93% | AQ8 3.20% |
| AR | `claude/ai-model-smoothing-gentrification-alc5dm` | 8/8 | 1214 | 18.75% | AR7 4.51% |

- **Largest:** AN5 19.83%, AO5 6.12%, AR7 4.51%, AO8 3.61%, AP8 3.61%.
- **Smallest:** AM3 0.45%, AM1 0.60%, AP1 0.80%, AO1 0.80%, AN1 0.80%.
- **Holding nothing:** AM5, AM6, AM7, AM8.

**Evenness.** Gini 0.45 (0 means every box holds the same, 1 means one box holds everything).
- **Fat** (at least 3× an even share; often several rules in one box, a candidate to split): AN5.
- **Thin** (at most 0.25× an even share; a label with a line behind it): AM3.

**Sources.** How much of each source file the grid draws on (distinct passages over the file's characters, whitespace collapsed, not counting any tables this script generated in it).

| File | Cells | Drawn | File | Coverage |
|---|---|---|---|---|
| `willows-grove/docs/design/branches/branch-ledger-2026-10-06.md` | 44 | 6475 | 6916 | 93.6% |

**Across grids.** Each grid's part of all the text.

| Grid | Cells | Characters | Share of all |
|---|---|---|---|
| Open branches (2026-10-06) | 48 | 6475 | 6.8% |
| Rules cross table: boxes and branches (2026-10-06) | 169 | 27250 | 28.7% |
| Boxes, from outside the system (2026-10-06) | 20 | 3434 | 3.6% |
| The fat, dripped (2026-10-06) | 90 | 4063 | 4.3% |
| Gerald session atoms (2026-10-06) | 156 | 53779 | 56.6% |
<!-- /cross-table:measure -->

---

ΔΣ=42
