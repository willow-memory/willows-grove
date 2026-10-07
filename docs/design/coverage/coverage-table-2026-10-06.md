# Coverage: every clause of Draft 0.9 against the three repos (2026-10-06)

*Desk session, 2026-10-06. Thinking out the grids with the operator: once the
columns are generated, the table becomes a query, and the constitution's own
Appendix A asks for exactly this one ("coverage is generated, never tabled").
At the operator's word: "yes, build". Agent-reported; not ratified.*

## How it's built

- **The source is the box's own coverage report,** after the fix that taught
  it every spelling of a citation (Trace ID, a link to an article's heading,
  and the eternity clauses' section sign).
- **It already existed.** The constitution's generated coverage artifact is
  a script in `governance/scripts/`. It defines the clauses by parsing the
  constitution, finds every citation in the scanned trees, and takes each clause's **verdict** from a
  declarations file a human keeps. It does not guess verdicts from text. It
  was run over all three repos, and [`coverage-ledger-2026-10-06.md`](coverage-ledger-2026-10-06.md)
  copies its rows. The only thing added is the split by repo and by kind:
  tests, docs (`.md`), and code (everything else).
- **The ledger cites nothing.** It writes clauses the way the constitution
  prints them (0.1, IV.5, Article IV): never as Trace IDs, and the eternity
  clauses without their section sign. A first draft of
  this report wrote Trace IDs, and the box's script counted it as citing every
  clause, so a report about citations would have made itself the evidence. The
  rebuilt ledger contains none, and the script's results are the same with it
  in the tree.
- **Rows BG–EG,** after the handoffs grid's BF: 78 clauses (13 articles plus
  Article 0, its six eternity clauses, and every numbered clause, including
  VII.default), and one row for IDs that are cited but name no clause.
  Columns: 1 the clause, 2 its verdict, 3–11 each repo's code, tests and docs.
- **A zero is a finding.** "0 files cite it" is a filled box: someone looked
  and found none. All 861 found boxes were checked to be exactly their own
  clause's line. The 8 silent boxes are the tail of the unknown-ID row.

## How full it comes out

The grid is **99% full** (861 of 869 boxes). The law is not. Only **82 of the
702** repo boxes name a citing file.

| | Code | Tests | Code and tests | Docs only | Nothing |
|---|---|---|---|---|---|
| 64 clauses | 8 | 10 | 6 | 12 | **40** |
| 14 articles | 9 | 10 | 8 | 3 | 0 |

Before the fix, when only Trace IDs were read, these were 74 boxes, and 6
clauses with tests, 3 with both, and 13 with docs only. The difference is
willow-mcp's code and tests citing the eternity clauses by section sign.

- **Appendix A's binding rule** ("every constitutional clause SHALL possess at
  least one deterministic enforcement artifact … that references its governing
  clause by Trace ID") is met by 8 of 64 clauses, counting any code citation
  as an artifact, which is generous.
- **Appendix B** ("every Article SHALL possess at least one deterministic
  compliance test") is met by 10 of 14 articles. VIII, IX, XI and XIII have
  none.
- **40 clauses are cited nowhere,** not even in a doc. They include most of
  Article V (the human and delegation), all of Article IX, and X.1–X.3.
- **Verdicts:** 77 of 78 are *undeclared*. X.4 is declared *differently*.
  Deciding the rest is the human's part. The report says so rather than guess.
- **By repo:** willows-grove cites 38 rows, willow-mcp 9, and willow-bot none.
- **Three cited IDs name no clause:** a sub-part of eternity clause 0.3 (a
  compliance case's ID), an "X.N" placeholder, and an eternity clause 0.7,
  cited by an incoming proposal, that the law doesn't have. All are recorded
  in the unknown row.
- **The third axis,** this report at every branch head, is
  [`coverage-layers-table-2026-10-06.md`](coverage-layers-table-2026-10-06.md).

## The grid

<!-- cross-table:grid -->
| | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| **BG** Article 0 | the clause | verdict | willows-grove code | willows-grove tests | willows-grove docs | willow-mcp code | willow-mcp tests | willow-mcp docs | willow-bot code | willow-bot tests | willow-bot docs |
| **BH** 0.1 | the clause | verdict | willows-grove code | willows-grove tests | willows-grove docs | willow-mcp code | willow-mcp tests | willow-mcp docs | willow-bot code | willow-bot tests | willow-bot docs |
| **BI** 0.2 | the clause | verdict | willows-grove code | willows-grove tests | willows-grove docs | willow-mcp code | willow-mcp tests | willow-mcp docs | willow-bot code | willow-bot tests | willow-bot docs |
| **BJ** 0.3 | the clause | verdict | willows-grove code | willows-grove tests | willows-grove docs | willow-mcp code | willow-mcp tests | willow-mcp docs | willow-bot code | willow-bot tests | willow-bot docs |
| **BK** 0.4 | the clause | verdict | willows-grove code | willows-grove tests | willows-grove docs | willow-mcp code | willow-mcp tests | willow-mcp docs | willow-bot code | willow-bot tests | willow-bot docs |
| **BL** 0.5 | the clause | verdict | willows-grove code | willows-grove tests | willows-grove docs | willow-mcp code | willow-mcp tests | willow-mcp docs | willow-bot code | willow-bot tests | willow-bot docs |
| **BM** 0.6 | the clause | verdict | willows-grove code | willows-grove tests | willows-grove docs | willow-mcp code | willow-mcp tests | willow-mcp docs | willow-bot code | willow-bot tests | willow-bot docs |
| **BN** Article I | the clause | verdict | willows-grove code | willows-grove tests | willows-grove docs | willow-mcp code | willow-mcp tests | willow-mcp docs | willow-bot code | willow-bot tests | willow-bot docs |
| **BO** I.1 | the clause | verdict | willows-grove code | willows-grove tests | willows-grove docs | willow-mcp code | willow-mcp tests | willow-mcp docs | willow-bot code | willow-bot tests | willow-bot docs |
| **BP** I.2 | the clause | verdict | willows-grove code | willows-grove tests | willows-grove docs | willow-mcp code | willow-mcp tests | willow-mcp docs | willow-bot code | willow-bot tests | willow-bot docs |
| **BQ** I.3 | the clause | verdict | willows-grove code | willows-grove tests | willows-grove docs | willow-mcp code | willow-mcp tests | willow-mcp docs | willow-bot code | willow-bot tests | willow-bot docs |
| **BR** I.4 | the clause | verdict | willows-grove code | willows-grove tests | willows-grove docs | willow-mcp code | willow-mcp tests | willow-mcp docs | willow-bot code | willow-bot tests | willow-bot docs |
| **BS** I.5 | the clause | verdict | willows-grove code | willows-grove tests | willows-grove docs | willow-mcp code | willow-mcp tests | willow-mcp docs | willow-bot code | willow-bot tests | willow-bot docs |
| **BT** Article II | the clause | verdict | willows-grove code | willows-grove tests | willows-grove docs | willow-mcp code | willow-mcp tests | willow-mcp docs | willow-bot code | willow-bot tests | willow-bot docs |
| **BU** II.1 | the clause | verdict | willows-grove code | willows-grove tests | willows-grove docs | willow-mcp code | willow-mcp tests | willow-mcp docs | willow-bot code | willow-bot tests | willow-bot docs |
| **BV** II.2 | the clause | verdict | willows-grove code | willows-grove tests | willows-grove docs | willow-mcp code | willow-mcp tests | willow-mcp docs | willow-bot code | willow-bot tests | willow-bot docs |
| **BW** II.3 | the clause | verdict | willows-grove code | willows-grove tests | willows-grove docs | willow-mcp code | willow-mcp tests | willow-mcp docs | willow-bot code | willow-bot tests | willow-bot docs |
| **BX** Article III | the clause | verdict | willows-grove code | willows-grove tests | willows-grove docs | willow-mcp code | willow-mcp tests | willow-mcp docs | willow-bot code | willow-bot tests | willow-bot docs |
| **BY** III.1 | the clause | verdict | willows-grove code | willows-grove tests | willows-grove docs | willow-mcp code | willow-mcp tests | willow-mcp docs | willow-bot code | willow-bot tests | willow-bot docs |
| **BZ** III.2 | the clause | verdict | willows-grove code | willows-grove tests | willows-grove docs | willow-mcp code | willow-mcp tests | willow-mcp docs | willow-bot code | willow-bot tests | willow-bot docs |
| **CA** III.3 | the clause | verdict | willows-grove code | willows-grove tests | willows-grove docs | willow-mcp code | willow-mcp tests | willow-mcp docs | willow-bot code | willow-bot tests | willow-bot docs |
| **CB** III.4 | the clause | verdict | willows-grove code | willows-grove tests | willows-grove docs | willow-mcp code | willow-mcp tests | willow-mcp docs | willow-bot code | willow-bot tests | willow-bot docs |
| **CC** III.5 | the clause | verdict | willows-grove code | willows-grove tests | willows-grove docs | willow-mcp code | willow-mcp tests | willow-mcp docs | willow-bot code | willow-bot tests | willow-bot docs |
| **CD** Article IV | the clause | verdict | willows-grove code | willows-grove tests | willows-grove docs | willow-mcp code | willow-mcp tests | willow-mcp docs | willow-bot code | willow-bot tests | willow-bot docs |
| **CE** IV.1 | the clause | verdict | willows-grove code | willows-grove tests | willows-grove docs | willow-mcp code | willow-mcp tests | willow-mcp docs | willow-bot code | willow-bot tests | willow-bot docs |
| **CF** IV.2 | the clause | verdict | willows-grove code | willows-grove tests | willows-grove docs | willow-mcp code | willow-mcp tests | willow-mcp docs | willow-bot code | willow-bot tests | willow-bot docs |
| **CG** IV.3 | the clause | verdict | willows-grove code | willows-grove tests | willows-grove docs | willow-mcp code | willow-mcp tests | willow-mcp docs | willow-bot code | willow-bot tests | willow-bot docs |
| **CH** IV.5 | the clause | verdict | willows-grove code | willows-grove tests | willows-grove docs | willow-mcp code | willow-mcp tests | willow-mcp docs | willow-bot code | willow-bot tests | willow-bot docs |
| **CI** IV.6 | the clause | verdict | willows-grove code | willows-grove tests | willows-grove docs | willow-mcp code | willow-mcp tests | willow-mcp docs | willow-bot code | willow-bot tests | willow-bot docs |
| **CJ** IV.4 | the clause | verdict | willows-grove code | willows-grove tests | willows-grove docs | willow-mcp code | willow-mcp tests | willow-mcp docs | willow-bot code | willow-bot tests | willow-bot docs |
| **CK** IV.7 | the clause | verdict | willows-grove code | willows-grove tests | willows-grove docs | willow-mcp code | willow-mcp tests | willow-mcp docs | willow-bot code | willow-bot tests | willow-bot docs |
| **CL** IV.8 | the clause | verdict | willows-grove code | willows-grove tests | willows-grove docs | willow-mcp code | willow-mcp tests | willow-mcp docs | willow-bot code | willow-bot tests | willow-bot docs |
| **CM** Article V | the clause | verdict | willows-grove code | willows-grove tests | willows-grove docs | willow-mcp code | willow-mcp tests | willow-mcp docs | willow-bot code | willow-bot tests | willow-bot docs |
| **CN** V.1 | the clause | verdict | willows-grove code | willows-grove tests | willows-grove docs | willow-mcp code | willow-mcp tests | willow-mcp docs | willow-bot code | willow-bot tests | willow-bot docs |
| **CO** V.2 | the clause | verdict | willows-grove code | willows-grove tests | willows-grove docs | willow-mcp code | willow-mcp tests | willow-mcp docs | willow-bot code | willow-bot tests | willow-bot docs |
| **CP** V.3 | the clause | verdict | willows-grove code | willows-grove tests | willows-grove docs | willow-mcp code | willow-mcp tests | willow-mcp docs | willow-bot code | willow-bot tests | willow-bot docs |
| **CQ** V.4 | the clause | verdict | willows-grove code | willows-grove tests | willows-grove docs | willow-mcp code | willow-mcp tests | willow-mcp docs | willow-bot code | willow-bot tests | willow-bot docs |
| **CR** V.4a | the clause | verdict | willows-grove code | willows-grove tests | willows-grove docs | willow-mcp code | willow-mcp tests | willow-mcp docs | willow-bot code | willow-bot tests | willow-bot docs |
| **CS** V.4b | the clause | verdict | willows-grove code | willows-grove tests | willows-grove docs | willow-mcp code | willow-mcp tests | willow-mcp docs | willow-bot code | willow-bot tests | willow-bot docs |
| **CT** V.5 | the clause | verdict | willows-grove code | willows-grove tests | willows-grove docs | willow-mcp code | willow-mcp tests | willow-mcp docs | willow-bot code | willow-bot tests | willow-bot docs |
| **CU** V.6 | the clause | verdict | willows-grove code | willows-grove tests | willows-grove docs | willow-mcp code | willow-mcp tests | willow-mcp docs | willow-bot code | willow-bot tests | willow-bot docs |
| **CV** V.7 | the clause | verdict | willows-grove code | willows-grove tests | willows-grove docs | willow-mcp code | willow-mcp tests | willow-mcp docs | willow-bot code | willow-bot tests | willow-bot docs |
| **CW** V.8 | the clause | verdict | willows-grove code | willows-grove tests | willows-grove docs | willow-mcp code | willow-mcp tests | willow-mcp docs | willow-bot code | willow-bot tests | willow-bot docs |
| **CX** V.9 | the clause | verdict | willows-grove code | willows-grove tests | willows-grove docs | willow-mcp code | willow-mcp tests | willow-mcp docs | willow-bot code | willow-bot tests | willow-bot docs |
| **CY** Article VI | the clause | verdict | willows-grove code | willows-grove tests | willows-grove docs | willow-mcp code | willow-mcp tests | willow-mcp docs | willow-bot code | willow-bot tests | willow-bot docs |
| **CZ** VI.1 | the clause | verdict | willows-grove code | willows-grove tests | willows-grove docs | willow-mcp code | willow-mcp tests | willow-mcp docs | willow-bot code | willow-bot tests | willow-bot docs |
| **DA** VI.2 | the clause | verdict | willows-grove code | willows-grove tests | willows-grove docs | willow-mcp code | willow-mcp tests | willow-mcp docs | willow-bot code | willow-bot tests | willow-bot docs |
| **DB** VI.3 | the clause | verdict | willows-grove code | willows-grove tests | willows-grove docs | willow-mcp code | willow-mcp tests | willow-mcp docs | willow-bot code | willow-bot tests | willow-bot docs |
| **DC** VI.4 | the clause | verdict | willows-grove code | willows-grove tests | willows-grove docs | willow-mcp code | willow-mcp tests | willow-mcp docs | willow-bot code | willow-bot tests | willow-bot docs |
| **DD** VI.5 | the clause | verdict | willows-grove code | willows-grove tests | willows-grove docs | willow-mcp code | willow-mcp tests | willow-mcp docs | willow-bot code | willow-bot tests | willow-bot docs |
| **DE** VI.6 | the clause | verdict | willows-grove code | willows-grove tests | willows-grove docs | willow-mcp code | willow-mcp tests | willow-mcp docs | willow-bot code | willow-bot tests | willow-bot docs |
| **DF** Article VII | the clause | verdict | willows-grove code | willows-grove tests | willows-grove docs | willow-mcp code | willow-mcp tests | willow-mcp docs | willow-bot code | willow-bot tests | willow-bot docs |
| **DG** VII.default | the clause | verdict | willows-grove code | willows-grove tests | willows-grove docs | willow-mcp code | willow-mcp tests | willow-mcp docs | willow-bot code | willow-bot tests | willow-bot docs |
| **DH** Article VIII | the clause | verdict | willows-grove code | willows-grove tests | willows-grove docs | willow-mcp code | willow-mcp tests | willow-mcp docs | willow-bot code | willow-bot tests | willow-bot docs |
| **DI** VIII.1 | the clause | verdict | willows-grove code | willows-grove tests | willows-grove docs | willow-mcp code | willow-mcp tests | willow-mcp docs | willow-bot code | willow-bot tests | willow-bot docs |
| **DJ** VIII.2 | the clause | verdict | willows-grove code | willows-grove tests | willows-grove docs | willow-mcp code | willow-mcp tests | willow-mcp docs | willow-bot code | willow-bot tests | willow-bot docs |
| **DK** VIII.3 | the clause | verdict | willows-grove code | willows-grove tests | willows-grove docs | willow-mcp code | willow-mcp tests | willow-mcp docs | willow-bot code | willow-bot tests | willow-bot docs |
| **DL** Article IX | the clause | verdict | willows-grove code | willows-grove tests | willows-grove docs | willow-mcp code | willow-mcp tests | willow-mcp docs | willow-bot code | willow-bot tests | willow-bot docs |
| **DM** IX.1 | the clause | verdict | willows-grove code | willows-grove tests | willows-grove docs | willow-mcp code | willow-mcp tests | willow-mcp docs | willow-bot code | willow-bot tests | willow-bot docs |
| **DN** IX.2 | the clause | verdict | willows-grove code | willows-grove tests | willows-grove docs | willow-mcp code | willow-mcp tests | willow-mcp docs | willow-bot code | willow-bot tests | willow-bot docs |
| **DO** IX.3 | the clause | verdict | willows-grove code | willows-grove tests | willows-grove docs | willow-mcp code | willow-mcp tests | willow-mcp docs | willow-bot code | willow-bot tests | willow-bot docs |
| **DP** IX.4 | the clause | verdict | willows-grove code | willows-grove tests | willows-grove docs | willow-mcp code | willow-mcp tests | willow-mcp docs | willow-bot code | willow-bot tests | willow-bot docs |
| **DQ** Article X | the clause | verdict | willows-grove code | willows-grove tests | willows-grove docs | willow-mcp code | willow-mcp tests | willow-mcp docs | willow-bot code | willow-bot tests | willow-bot docs |
| **DR** X.1 | the clause | verdict | willows-grove code | willows-grove tests | willows-grove docs | willow-mcp code | willow-mcp tests | willow-mcp docs | willow-bot code | willow-bot tests | willow-bot docs |
| **DS** X.2 | the clause | verdict | willows-grove code | willows-grove tests | willows-grove docs | willow-mcp code | willow-mcp tests | willow-mcp docs | willow-bot code | willow-bot tests | willow-bot docs |
| **DT** X.3 | the clause | verdict | willows-grove code | willows-grove tests | willows-grove docs | willow-mcp code | willow-mcp tests | willow-mcp docs | willow-bot code | willow-bot tests | willow-bot docs |
| **DU** X.4 | the clause | verdict | willows-grove code | willows-grove tests | willows-grove docs | willow-mcp code | willow-mcp tests | willow-mcp docs | willow-bot code | willow-bot tests | willow-bot docs |
| **DV** X.4a | the clause | verdict | willows-grove code | willows-grove tests | willows-grove docs | willow-mcp code | willow-mcp tests | willow-mcp docs | willow-bot code | willow-bot tests | willow-bot docs |
| **DW** Article XI | the clause | verdict | willows-grove code | willows-grove tests | willows-grove docs | willow-mcp code | willow-mcp tests | willow-mcp docs | willow-bot code | willow-bot tests | willow-bot docs |
| **DX** XI.1 | the clause | verdict | willows-grove code | willows-grove tests | willows-grove docs | willow-mcp code | willow-mcp tests | willow-mcp docs | willow-bot code | willow-bot tests | willow-bot docs |
| **DY** XI.2 | the clause | verdict | willows-grove code | willows-grove tests | willows-grove docs | willow-mcp code | willow-mcp tests | willow-mcp docs | willow-bot code | willow-bot tests | willow-bot docs |
| **DZ** XI.3 | the clause | verdict | willows-grove code | willows-grove tests | willows-grove docs | willow-mcp code | willow-mcp tests | willow-mcp docs | willow-bot code | willow-bot tests | willow-bot docs |
| **EA** Article XII | the clause | verdict | willows-grove code | willows-grove tests | willows-grove docs | willow-mcp code | willow-mcp tests | willow-mcp docs | willow-bot code | willow-bot tests | willow-bot docs |
| **EB** XII.1 | the clause | verdict | willows-grove code | willows-grove tests | willows-grove docs | willow-mcp code | willow-mcp tests | willow-mcp docs | willow-bot code | willow-bot tests | willow-bot docs |
| **EC** XII.2 | the clause | verdict | willows-grove code | willows-grove tests | willows-grove docs | willow-mcp code | willow-mcp tests | willow-mcp docs | willow-bot code | willow-bot tests | willow-bot docs |
| **ED** XII.3 | the clause | verdict | willows-grove code | willows-grove tests | willows-grove docs | willow-mcp code | willow-mcp tests | willow-mcp docs | willow-bot code | willow-bot tests | willow-bot docs |
| **EE** XII.4 | the clause | verdict | willows-grove code | willows-grove tests | willows-grove docs | willow-mcp code | willow-mcp tests | willow-mcp docs | willow-bot code | willow-bot tests | willow-bot docs |
| **EF** Article XIII | the clause | verdict | willows-grove code | willows-grove tests | willows-grove docs | willow-mcp code | willow-mcp tests | willow-mcp docs | willow-bot code | willow-bot tests | willow-bot docs |
| **EG** unknown | what this row is | id 0.3.II | id X.N |  |  |  |  |  |  |  |  |
<!-- /cross-table:grid -->

## Where each row comes from

<!-- cross-table:sources -->
| Row | What it holds | Source |
|---|---|---|
| BG | Article 0 | `coverage-ledger-2026-10-06.md`, section Article 0 (copied from the box's coverage report) |
| BH | 0.1 | `coverage-ledger-2026-10-06.md`, section 0.1 (copied from the box's coverage report) |
| BI | 0.2 | `coverage-ledger-2026-10-06.md`, section 0.2 (copied from the box's coverage report) |
| BJ | 0.3 | `coverage-ledger-2026-10-06.md`, section 0.3 (copied from the box's coverage report) |
| BK | 0.4 | `coverage-ledger-2026-10-06.md`, section 0.4 (copied from the box's coverage report) |
| BL | 0.5 | `coverage-ledger-2026-10-06.md`, section 0.5 (copied from the box's coverage report) |
| BM | 0.6 | `coverage-ledger-2026-10-06.md`, section 0.6 (copied from the box's coverage report) |
| BN | Article I | `coverage-ledger-2026-10-06.md`, section Article I (copied from the box's coverage report) |
| BO | I.1 | `coverage-ledger-2026-10-06.md`, section I.1 (copied from the box's coverage report) |
| BP | I.2 | `coverage-ledger-2026-10-06.md`, section I.2 (copied from the box's coverage report) |
| BQ | I.3 | `coverage-ledger-2026-10-06.md`, section I.3 (copied from the box's coverage report) |
| BR | I.4 | `coverage-ledger-2026-10-06.md`, section I.4 (copied from the box's coverage report) |
| BS | I.5 | `coverage-ledger-2026-10-06.md`, section I.5 (copied from the box's coverage report) |
| BT | Article II | `coverage-ledger-2026-10-06.md`, section Article II (copied from the box's coverage report) |
| BU | II.1 | `coverage-ledger-2026-10-06.md`, section II.1 (copied from the box's coverage report) |
| BV | II.2 | `coverage-ledger-2026-10-06.md`, section II.2 (copied from the box's coverage report) |
| BW | II.3 | `coverage-ledger-2026-10-06.md`, section II.3 (copied from the box's coverage report) |
| BX | Article III | `coverage-ledger-2026-10-06.md`, section Article III (copied from the box's coverage report) |
| BY | III.1 | `coverage-ledger-2026-10-06.md`, section III.1 (copied from the box's coverage report) |
| BZ | III.2 | `coverage-ledger-2026-10-06.md`, section III.2 (copied from the box's coverage report) |
| CA | III.3 | `coverage-ledger-2026-10-06.md`, section III.3 (copied from the box's coverage report) |
| CB | III.4 | `coverage-ledger-2026-10-06.md`, section III.4 (copied from the box's coverage report) |
| CC | III.5 | `coverage-ledger-2026-10-06.md`, section III.5 (copied from the box's coverage report) |
| CD | Article IV | `coverage-ledger-2026-10-06.md`, section Article IV (copied from the box's coverage report) |
| CE | IV.1 | `coverage-ledger-2026-10-06.md`, section IV.1 (copied from the box's coverage report) |
| CF | IV.2 | `coverage-ledger-2026-10-06.md`, section IV.2 (copied from the box's coverage report) |
| CG | IV.3 | `coverage-ledger-2026-10-06.md`, section IV.3 (copied from the box's coverage report) |
| CH | IV.5 | `coverage-ledger-2026-10-06.md`, section IV.5 (copied from the box's coverage report) |
| CI | IV.6 | `coverage-ledger-2026-10-06.md`, section IV.6 (copied from the box's coverage report) |
| CJ | IV.4 | `coverage-ledger-2026-10-06.md`, section IV.4 (copied from the box's coverage report) |
| CK | IV.7 | `coverage-ledger-2026-10-06.md`, section IV.7 (copied from the box's coverage report) |
| CL | IV.8 | `coverage-ledger-2026-10-06.md`, section IV.8 (copied from the box's coverage report) |
| CM | Article V | `coverage-ledger-2026-10-06.md`, section Article V (copied from the box's coverage report) |
| CN | V.1 | `coverage-ledger-2026-10-06.md`, section V.1 (copied from the box's coverage report) |
| CO | V.2 | `coverage-ledger-2026-10-06.md`, section V.2 (copied from the box's coverage report) |
| CP | V.3 | `coverage-ledger-2026-10-06.md`, section V.3 (copied from the box's coverage report) |
| CQ | V.4 | `coverage-ledger-2026-10-06.md`, section V.4 (copied from the box's coverage report) |
| CR | V.4a | `coverage-ledger-2026-10-06.md`, section V.4a (copied from the box's coverage report) |
| CS | V.4b | `coverage-ledger-2026-10-06.md`, section V.4b (copied from the box's coverage report) |
| CT | V.5 | `coverage-ledger-2026-10-06.md`, section V.5 (copied from the box's coverage report) |
| CU | V.6 | `coverage-ledger-2026-10-06.md`, section V.6 (copied from the box's coverage report) |
| CV | V.7 | `coverage-ledger-2026-10-06.md`, section V.7 (copied from the box's coverage report) |
| CW | V.8 | `coverage-ledger-2026-10-06.md`, section V.8 (copied from the box's coverage report) |
| CX | V.9 | `coverage-ledger-2026-10-06.md`, section V.9 (copied from the box's coverage report) |
| CY | Article VI | `coverage-ledger-2026-10-06.md`, section Article VI (copied from the box's coverage report) |
| CZ | VI.1 | `coverage-ledger-2026-10-06.md`, section VI.1 (copied from the box's coverage report) |
| DA | VI.2 | `coverage-ledger-2026-10-06.md`, section VI.2 (copied from the box's coverage report) |
| DB | VI.3 | `coverage-ledger-2026-10-06.md`, section VI.3 (copied from the box's coverage report) |
| DC | VI.4 | `coverage-ledger-2026-10-06.md`, section VI.4 (copied from the box's coverage report) |
| DD | VI.5 | `coverage-ledger-2026-10-06.md`, section VI.5 (copied from the box's coverage report) |
| DE | VI.6 | `coverage-ledger-2026-10-06.md`, section VI.6 (copied from the box's coverage report) |
| DF | Article VII | `coverage-ledger-2026-10-06.md`, section Article VII (copied from the box's coverage report) |
| DG | VII.default | `coverage-ledger-2026-10-06.md`, section VII.default (copied from the box's coverage report) |
| DH | Article VIII | `coverage-ledger-2026-10-06.md`, section Article VIII (copied from the box's coverage report) |
| DI | VIII.1 | `coverage-ledger-2026-10-06.md`, section VIII.1 (copied from the box's coverage report) |
| DJ | VIII.2 | `coverage-ledger-2026-10-06.md`, section VIII.2 (copied from the box's coverage report) |
| DK | VIII.3 | `coverage-ledger-2026-10-06.md`, section VIII.3 (copied from the box's coverage report) |
| DL | Article IX | `coverage-ledger-2026-10-06.md`, section Article IX (copied from the box's coverage report) |
| DM | IX.1 | `coverage-ledger-2026-10-06.md`, section IX.1 (copied from the box's coverage report) |
| DN | IX.2 | `coverage-ledger-2026-10-06.md`, section IX.2 (copied from the box's coverage report) |
| DO | IX.3 | `coverage-ledger-2026-10-06.md`, section IX.3 (copied from the box's coverage report) |
| DP | IX.4 | `coverage-ledger-2026-10-06.md`, section IX.4 (copied from the box's coverage report) |
| DQ | Article X | `coverage-ledger-2026-10-06.md`, section Article X (copied from the box's coverage report) |
| DR | X.1 | `coverage-ledger-2026-10-06.md`, section X.1 (copied from the box's coverage report) |
| DS | X.2 | `coverage-ledger-2026-10-06.md`, section X.2 (copied from the box's coverage report) |
| DT | X.3 | `coverage-ledger-2026-10-06.md`, section X.3 (copied from the box's coverage report) |
| DU | X.4 | `coverage-ledger-2026-10-06.md`, section X.4 (copied from the box's coverage report) |
| DV | X.4a | `coverage-ledger-2026-10-06.md`, section X.4a (copied from the box's coverage report) |
| DW | Article XI | `coverage-ledger-2026-10-06.md`, section Article XI (copied from the box's coverage report) |
| DX | XI.1 | `coverage-ledger-2026-10-06.md`, section XI.1 (copied from the box's coverage report) |
| DY | XI.2 | `coverage-ledger-2026-10-06.md`, section XI.2 (copied from the box's coverage report) |
| DZ | XI.3 | `coverage-ledger-2026-10-06.md`, section XI.3 (copied from the box's coverage report) |
| EA | Article XII | `coverage-ledger-2026-10-06.md`, section Article XII (copied from the box's coverage report) |
| EB | XII.1 | `coverage-ledger-2026-10-06.md`, section XII.1 (copied from the box's coverage report) |
| EC | XII.2 | `coverage-ledger-2026-10-06.md`, section XII.2 (copied from the box's coverage report) |
| ED | XII.3 | `coverage-ledger-2026-10-06.md`, section XII.3 (copied from the box's coverage report) |
| EE | XII.4 | `coverage-ledger-2026-10-06.md`, section XII.4 (copied from the box's coverage report) |
| EF | Article XIII | `coverage-ledger-2026-10-06.md`, section Article XIII (copied from the box's coverage report) |
| EG | unknown | `coverage-ledger-2026-10-06.md`, section unknown (copied from the box's coverage report) |
<!-- /cross-table:sources -->

## Index

<!-- cross-table:index -->
| Cell | Rule | Source | Share | Standing |
|---|---|---|---|---|
| BG1 | - clause `Article 0` is line 58 of the constitution: The Eternity Clause. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:13 | 0.11% | unattested |
| BG2 | - clause `Article 0` verdict, from the human-kept declarations: undeclared. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:14 | 0.12% | unattested |
| BG3 | - clause `Article 0` in `willows-grove` code: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:15 | 0.10% | unattested |
| BG4 | - clause `Article 0` in `willows-grove` tests: 1 file cites it: `tests/test_const_coverage.py`. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:16 | 0.15% | unattested |
| BG5 | - clause `Article 0` in `willows-grove` docs: 6 files cite it: `docs/design/one-script/constitution-proposal/CONSTITUTION.neutral.proposed.md`, `docs/design/one-script/constitution-proposal/CONSTITUTION.proposed.md`, `docs/design/one-script/constitution-proposal/CONSTITUTION.provenance.md`, `docs/design/one-script/constitution-proposal/in-box-terms-scan.md`, … | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:17 | 0.82% | unattested |
| BG6 | - clause `Article 0` in `willow-mcp` code: 1 file cites it: `tools/mai_prose_split.py`. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:18 | 0.14% | unattested |
| BG7 | - clause `Article 0` in `willow-mcp` tests: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:19 | 0.09% | unattested |
| BG8 | - clause `Article 0` in `willow-mcp` docs: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:20 | 0.09% | unattested |
| BG9 | - clause `Article 0` in `willow-bot` code: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:21 | 0.09% | unattested |
| BG10 | - clause `Article 0` in `willow-bot` tests: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:22 | 0.09% | unattested |
| BG11 | - clause `Article 0` in `willow-bot` docs: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:23 | 0.09% | unattested |
| BH1 | - clause `0.1` is line 64 of the constitution: No self-attestation. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:27 | 0.10% | unattested |
| BH2 | - clause `0.1` verdict, from the human-kept declarations: undeclared. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:28 | 0.11% | unattested |
| BH3 | - clause `0.1` in `willows-grove` code: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:29 | 0.09% | unattested |
| BH4 | - clause `0.1` in `willows-grove` tests: 1 file cites it: `tests/test_const_coverage.py`. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:30 | 0.14% | unattested |
| BH5 | - clause `0.1` in `willows-grove` docs: 8 files cite it: `docs/design/one-script/constitution-proposal/CONSTITUTION.neutral.proposed.md`, `docs/design/one-script/constitution-proposal/CONSTITUTION.proposed.md`, `docs/design/one-script/constitution-proposal/CONSTITUTION.provenance.md`, `docs/design/one-script/constitution-proposal/in-box-terms-scan.md`, … | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:31 | 0.85% | unattested |
| BH6 | - clause `0.1` in `willow-mcp` code: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:32 | 0.08% | unattested |
| BH7 | - clause `0.1` in `willow-mcp` tests: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:33 | 0.08% | unattested |
| BH8 | - clause `0.1` in `willow-mcp` docs: 1 file cites it: `SECURITY_AUDIT.md`. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:34 | 0.12% | unattested |
| BH9 | - clause `0.1` in `willow-bot` code: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:35 | 0.08% | unattested |
| BH10 | - clause `0.1` in `willow-bot` tests: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:36 | 0.08% | unattested |
| BH11 | - clause `0.1` in `willow-bot` docs: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:37 | 0.08% | unattested |
| BI1 | - clause `0.2` is line 67 of the constitution: No self-ratification to canon. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:41 | 0.12% | unattested |
| BI2 | - clause `0.2` verdict, from the human-kept declarations: undeclared. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:42 | 0.11% | unattested |
| BI3 | - clause `0.2` in `willows-grove` code: 4 files cite it: `docs/design/one-script/day-3/predictions.json`, `docs/design/one-script/onescript/gate.py`, `docs/design/one-script/onescript/predict.py`, `governance/compliance/cases/const_0_2_ratify.py`. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:43 | 0.39% | unattested |
| BI4 | - clause `0.2` in `willows-grove` tests: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:44 | 0.09% | unattested |
| BI5 | - clause `0.2` in `willows-grove` docs: 12 files cite it: `docs/design/autonomous-continuity.md`, `docs/design/one-box/rules-cross-table-2026-10-06.md`, `docs/design/one-script/constitution-proposal/CONSTITUTION.neutral.proposed.md`, `docs/design/one-script/constitution-proposal/CONSTITUTION.proposed.md`, `docs/design/one-script/constitution-proposal/CONSTITUTION.provenance.md`, … | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:45 | 1.11% | unattested |
| BI6 | - clause `0.2` in `willow-mcp` code: 4 files cite it: `src/willow_mcp/gaps.py`, `src/willow_mcp/mem_ratify/collect.py`, `src/willow_mcp/mem_ratify/ratify.py`, `src/willow_mcp/server.py`. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:46 | 0.29% | unattested |
| BI7 | - clause `0.2` in `willow-mcp` tests: 1 file cites it: `tests/test_witness_collector.py`. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:47 | 0.14% | unattested |
| BI8 | - clause `0.2` in `willow-mcp` docs: 1 file cites it: `docs/design/gaps-in-soil.md`. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:48 | 0.13% | unattested |
| BI9 | - clause `0.2` in `willow-bot` code: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:49 | 0.08% | unattested |
| BI10 | - clause `0.2` in `willow-bot` tests: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:50 | 0.08% | unattested |
| BI11 | - clause `0.2` in `willow-bot` docs: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:51 | 0.08% | unattested |
| BJ1 | - clause `0.3` is line 70 of the constitution: No self-extension of capability. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:55 | 0.12% | unattested |
| BJ2 | - clause `0.3` verdict, from the human-kept declarations: undeclared. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:56 | 0.11% | unattested |
| BJ3 | - clause `0.3` in `willows-grove` code: 4 files cite it: `docs/design/one-script/onescript/gate.py`, `governance/compliance/cases/const_0_3_capability.py`, `governance/compliance/cases/const_0_3_egress.py`, `grove/envelope_reader.py`. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:57 | 0.37% | unattested |
| BJ4 | - clause `0.3` in `willows-grove` tests: 1 file cites it: `tests/test_const_coverage.py`. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:58 | 0.14% | unattested |
| BJ5 | - clause `0.3` in `willows-grove` docs: 10 files cite it: `docs/design/autonomous-continuity.md`, `docs/design/one-box/rules-cross-table-2026-10-06.md`, `docs/design/one-script/constitution-proposal/CONSTITUTION.neutral.proposed.md`, `docs/design/one-script/constitution-proposal/CONSTITUTION.proposed.md`, `docs/design/one-script/constitution-proposal/CONSTITUTION.provenance.md`, … | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:59 | 0.89% | unattested |
| BJ6 | - clause `0.3` in `willow-mcp` code: 2 files cite it: `.willow/constitutional/syscall-table.json`, `src/willow_mcp/bundle/constitutional/syscall-table.json`. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:60 | 0.25% | unattested |
| BJ7 | - clause `0.3` in `willow-mcp` tests: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:61 | 0.08% | unattested |
| BJ8 | - clause `0.3` in `willow-mcp` docs: 2 files cite it: `SECURITY_AUDIT.md`, `docs/design/federation-wire-format.md`. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:62 | 0.18% | unattested |
| BJ9 | - clause `0.3` in `willow-bot` code: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:63 | 0.08% | unattested |
| BJ10 | - clause `0.3` in `willow-bot` tests: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:64 | 0.08% | unattested |
| BJ11 | - clause `0.3` in `willow-bot` docs: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:65 | 0.08% | unattested |
| BK1 | - clause `0.4` is line 73 of the constitution: The human key is required, and cannot be forged forward. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:69 | 0.16% | unattested |
| BK2 | - clause `0.4` verdict, from the human-kept declarations: undeclared. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:70 | 0.11% | unattested |
| BK3 | - clause `0.4` in `willows-grove` code: 1 file cites it: `governance/compliance/cases/const_0_4_humankey.py`. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:71 | 0.17% | unattested |
| BK4 | - clause `0.4` in `willows-grove` tests: 1 file cites it: `tests/test_const_coverage.py`. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:72 | 0.14% | unattested |
| BK5 | - clause `0.4` in `willows-grove` docs: 6 files cite it: `docs/design/one-script/constitution-proposal/CONSTITUTION.neutral.proposed.md`, `docs/design/one-script/constitution-proposal/CONSTITUTION.proposed.md`, `docs/design/one-script/incoming/haiku-2026-10-02/proposal-overnight-and-morning-screen.md`, `docs/design/one-script/incoming/opus-2026-10-02/2026-10-02-reachability-and-staleness.md`, … | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:73 | 0.75% | unattested |
| BK6 | - clause `0.4` in `willow-mcp` code: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:74 | 0.08% | unattested |
| BK7 | - clause `0.4` in `willow-mcp` tests: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:75 | 0.08% | unattested |
| BK8 | - clause `0.4` in `willow-mcp` docs: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:76 | 0.08% | unattested |
| BK9 | - clause `0.4` in `willow-bot` code: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:77 | 0.08% | unattested |
| BK10 | - clause `0.4` in `willow-bot` tests: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:78 | 0.08% | unattested |
| BK11 | - clause `0.4` in `willow-bot` docs: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:79 | 0.08% | unattested |
| BL1 | - clause `0.5` is line 76 of the constitution: The Record is append-only and its keepers are bound by it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:83 | 0.16% | unattested |
| BL2 | - clause `0.5` verdict, from the human-kept declarations: undeclared. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:84 | 0.11% | unattested |
| BL3 | - clause `0.5` in `willows-grove` code: 1 file cites it: `governance/compliance/cases/const_0_5_ledger.py`. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:85 | 0.17% | unattested |
| BL4 | - clause `0.5` in `willows-grove` tests: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:86 | 0.09% | unattested |
| BL5 | - clause `0.5` in `willows-grove` docs: 9 files cite it: `docs/design/one-box/rules-cross-table-2026-10-06.md`, `docs/design/one-script/constitution-proposal/CONSTITUTION.neutral.proposed.md`, `docs/design/one-script/constitution-proposal/CONSTITUTION.proposed.md`, `docs/design/one-script/constitution-proposal/CONSTITUTION.provenance.md`, `docs/design/one-script/incoming/README.md`, … | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:87 | 0.97% | unattested |
| BL6 | - clause `0.5` in `willow-mcp` code: 1 file cites it: `src/willow_mcp/integrations.py`. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:88 | 0.14% | unattested |
| BL7 | - clause `0.5` in `willow-mcp` tests: 1 file cites it: `tests/test_utety_adapter.py`. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:89 | 0.13% | unattested |
| BL8 | - clause `0.5` in `willow-mcp` docs: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:90 | 0.08% | unattested |
| BL9 | - clause `0.5` in `willow-bot` code: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:91 | 0.08% | unattested |
| BL10 | - clause `0.5` in `willow-bot` tests: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:92 | 0.08% | unattested |
| BL11 | - clause `0.5` in `willow-bot` docs: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:93 | 0.08% | unattested |
| BM1 | - clause `0.6` is line 79 of the constitution: Silence escalates. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:97 | 0.10% | unattested |
| BM2 | - clause `0.6` verdict, from the human-kept declarations: undeclared. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:98 | 0.11% | unattested |
| BM3 | - clause `0.6` in `willows-grove` code: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:99 | 0.09% | unattested |
| BM4 | - clause `0.6` in `willows-grove` tests: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:100 | 0.09% | unattested |
| BM5 | - clause `0.6` in `willows-grove` docs: 8 files cite it: `docs/design/one-script/constitution-proposal/CONSTITUTION.neutral.proposed.md`, `docs/design/one-script/constitution-proposal/CONSTITUTION.proposed.md`, `docs/design/one-script/constitution-proposal/CONSTITUTION.provenance.md`, `docs/design/one-script/constitution-proposal/amendments-2026-10-06-seat.md`, … | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:101 | 0.92% | unattested |
| BM6 | - clause `0.6` in `willow-mcp` code: 2 files cite it: `.willow/constitutional/syscall-table.json`, `src/willow_mcp/bundle/constitutional/syscall-table.json`. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:102 | 0.25% | unattested |
| BM7 | - clause `0.6` in `willow-mcp` tests: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:103 | 0.08% | unattested |
| BM8 | - clause `0.6` in `willow-mcp` docs: 1 file cites it: `docs/design/federation-wire-format.md`. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:104 | 0.15% | unattested |
| BM9 | - clause `0.6` in `willow-bot` code: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:105 | 0.08% | unattested |
| BM10 | - clause `0.6` in `willow-bot` tests: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:106 | 0.08% | unattested |
| BM11 | - clause `0.6` in `willow-bot` docs: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:107 | 0.08% | unattested |
| BN1 | - clause `Article I` is line 128 of the constitution: Identity & Standing. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:111 | 0.12% | unattested |
| BN2 | - clause `Article I` verdict, from the human-kept declarations: undeclared. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:112 | 0.12% | unattested |
| BN3 | - clause `Article I` in `willows-grove` code: 2 files cite it: `docs/design/one-script/onescript/boot.py`, `governance/fleet_personas.json`. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:113 | 0.22% | unattested |
| BN4 | - clause `Article I` in `willows-grove` tests: 2 files cite it: `docs/design/one-script/onescript/tests/test_onescript.py`, `tests/test_const_coverage.py`. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:114 | 0.24% | unattested |
| BN5 | - clause `Article I` in `willows-grove` docs: 10 files cite it: `docs/design/one-box/research-2026-10-06.md`, `docs/design/one-box/rules-cross-table-2026-10-06.md`, `docs/design/one-script/constitution-proposal/CONSTITUTION.neutral.proposed.md`, `docs/design/one-script/constitution-proposal/CONSTITUTION.proposed.md`, `docs/design/one-script/constitution-proposal/CONSTITUTION.provenance.md`, … | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:115 | 1.10% | unattested |
| BN6 | - clause `Article I` in `willow-mcp` code: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:116 | 0.09% | unattested |
| BN7 | - clause `Article I` in `willow-mcp` tests: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:117 | 0.09% | unattested |
| BN8 | - clause `Article I` in `willow-mcp` docs: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:118 | 0.09% | unattested |
| BN9 | - clause `Article I` in `willow-bot` code: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:119 | 0.09% | unattested |
| BN10 | - clause `Article I` in `willow-bot` tests: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:120 | 0.09% | unattested |
| BN11 | - clause `Article I` in `willow-bot` docs: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:121 | 0.09% | unattested |
| BO1 | - clause `I.1` is line 132 of the constitution: Identity is the manifest, not the runtime. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:125 | 0.14% | unattested |
| BO2 | - clause `I.1` verdict, from the human-kept declarations: undeclared. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:126 | 0.11% | unattested |
| BO3 | - clause `I.1` in `willows-grove` code: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:127 | 0.09% | unattested |
| BO4 | - clause `I.1` in `willows-grove` tests: 1 file cites it: `tests/test_const_coverage.py`. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:128 | 0.14% | unattested |
| BO5 | - clause `I.1` in `willows-grove` docs: 5 files cite it: `docs/design/one-script/constitution-proposal/CONSTITUTION.neutral.proposed.md`, `docs/design/one-script/constitution-proposal/CONSTITUTION.proposed.md`, `docs/design/one-script/constitution-proposal/CONSTITUTION.provenance.md`, `docs/design/one-script/constitution-proposal/in-box-terms-scan.md`, `governance/CASEBOOK.md`. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:129 | 0.59% | unattested |
| BO6 | - clause `I.1` in `willow-mcp` code: 1 file cites it: `tools/mai_prose_split.py`. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:130 | 0.13% | unattested |
| BO7 | - clause `I.1` in `willow-mcp` tests: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:131 | 0.08% | unattested |
| BO8 | - clause `I.1` in `willow-mcp` docs: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:132 | 0.08% | unattested |
| BO9 | - clause `I.1` in `willow-bot` code: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:133 | 0.08% | unattested |
| BO10 | - clause `I.1` in `willow-bot` tests: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:134 | 0.08% | unattested |
| BO11 | - clause `I.1` in `willow-bot` docs: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:135 | 0.08% | unattested |
| BP1 | - clause `I.2` is line 134 of the constitution: Standing follows identity and role. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:139 | 0.13% | unattested |
| BP2 | - clause `I.2` verdict, from the human-kept declarations: undeclared. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:140 | 0.11% | unattested |
| BP3 | - clause `I.2` in `willows-grove` code: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:141 | 0.09% | unattested |
| BP4 | - clause `I.2` in `willows-grove` tests: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:142 | 0.09% | unattested |
| BP5 | - clause `I.2` in `willows-grove` docs: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:143 | 0.09% | unattested |
| BP6 | - clause `I.2` in `willow-mcp` code: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:144 | 0.08% | unattested |
| BP7 | - clause `I.2` in `willow-mcp` tests: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:145 | 0.08% | unattested |
| BP8 | - clause `I.2` in `willow-mcp` docs: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:146 | 0.08% | unattested |
| BP9 | - clause `I.2` in `willow-bot` code: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:147 | 0.08% | unattested |
| BP10 | - clause `I.2` in `willow-bot` tests: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:148 | 0.08% | unattested |
| BP11 | - clause `I.2` in `willow-bot` docs: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:149 | 0.08% | unattested |
| BQ1 | - clause `I.3` is line 136 of the constitution: Issuance and revocation are reserved. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:153 | 0.13% | unattested |
| BQ2 | - clause `I.3` verdict, from the human-kept declarations: undeclared. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:154 | 0.11% | unattested |
| BQ3 | - clause `I.3` in `willows-grove` code: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:155 | 0.09% | unattested |
| BQ4 | - clause `I.3` in `willows-grove` tests: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:156 | 0.09% | unattested |
| BQ5 | - clause `I.3` in `willows-grove` docs: 1 file cites it: `governance/CASEBOOK.md`. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:157 | 0.13% | unattested |
| BQ6 | - clause `I.3` in `willow-mcp` code: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:158 | 0.08% | unattested |
| BQ7 | - clause `I.3` in `willow-mcp` tests: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:159 | 0.08% | unattested |
| BQ8 | - clause `I.3` in `willow-mcp` docs: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:160 | 0.08% | unattested |
| BQ9 | - clause `I.3` in `willow-bot` code: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:161 | 0.08% | unattested |
| BQ10 | - clause `I.3` in `willow-bot` tests: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:162 | 0.08% | unattested |
| BQ11 | - clause `I.3` in `willow-bot` docs: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:163 | 0.08% | unattested |
| BR1 | - clause `I.4` is line 138 of the constitution: Drift is suspicion, and suspicion suspends. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:167 | 0.14% | unattested |
| BR2 | - clause `I.4` verdict, from the human-kept declarations: undeclared. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:168 | 0.11% | unattested |
| BR3 | - clause `I.4` in `willows-grove` code: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:169 | 0.09% | unattested |
| BR4 | - clause `I.4` in `willows-grove` tests: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:170 | 0.09% | unattested |
| BR5 | - clause `I.4` in `willows-grove` docs: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:171 | 0.09% | unattested |
| BR6 | - clause `I.4` in `willow-mcp` code: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:172 | 0.08% | unattested |
| BR7 | - clause `I.4` in `willow-mcp` tests: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:173 | 0.08% | unattested |
| BR8 | - clause `I.4` in `willow-mcp` docs: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:174 | 0.08% | unattested |
| BR9 | - clause `I.4` in `willow-bot` code: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:175 | 0.08% | unattested |
| BR10 | - clause `I.4` in `willow-bot` tests: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:176 | 0.08% | unattested |
| BR11 | - clause `I.4` in `willow-bot` docs: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:177 | 0.08% | unattested |
| BS1 | - clause `I.5` is line 140 of the constitution: Presence is a label; authority is a key. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:181 | 0.14% | unattested |
| BS2 | - clause `I.5` verdict, from the human-kept declarations: undeclared. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:182 | 0.11% | unattested |
| BS3 | - clause `I.5` in `willows-grove` code: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:183 | 0.09% | unattested |
| BS4 | - clause `I.5` in `willows-grove` tests: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:184 | 0.09% | unattested |
| BS5 | - clause `I.5` in `willows-grove` docs: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:185 | 0.09% | unattested |
| BS6 | - clause `I.5` in `willow-mcp` code: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:186 | 0.08% | unattested |
| BS7 | - clause `I.5` in `willow-mcp` tests: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:187 | 0.08% | unattested |
| BS8 | - clause `I.5` in `willow-mcp` docs: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:188 | 0.08% | unattested |
| BS9 | - clause `I.5` in `willow-bot` code: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:189 | 0.08% | unattested |
| BS10 | - clause `I.5` in `willow-bot` tests: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:190 | 0.08% | unattested |
| BS11 | - clause `I.5` in `willow-bot` docs: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:191 | 0.08% | unattested |
| BT1 | - clause `Article II` is line 157 of the constitution: Enumerated Capabilities. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:195 | 0.12% | unattested |
| BT2 | - clause `Article II` verdict, from the human-kept declarations: undeclared. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:196 | 0.12% | unattested |
| BT3 | - clause `Article II` in `willows-grove` code: 1 file cites it: `docs/design/one-script/onescript/gate.py`. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:197 | 0.17% | unattested |
| BT4 | - clause `Article II` in `willows-grove` tests: 1 file cites it: `docs/design/one-script/onescript/tests/test_onescript.py`. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:198 | 0.19% | unattested |
| BT5 | - clause `Article II` in `willows-grove` docs: 2 files cite it: `docs/design/one-script/constitution-proposal/CONSTITUTION.neutral.proposed.md`, `docs/design/one-script/constitution-proposal/CONSTITUTION.proposed.md`. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:199 | 0.34% | unattested |
| BT6 | - clause `Article II` in `willow-mcp` code: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:200 | 0.09% | unattested |
| BT7 | - clause `Article II` in `willow-mcp` tests: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:201 | 0.10% | unattested |
| BT8 | - clause `Article II` in `willow-mcp` docs: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:202 | 0.09% | unattested |
| BT9 | - clause `Article II` in `willow-bot` code: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:203 | 0.09% | unattested |
| BT10 | - clause `Article II` in `willow-bot` tests: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:204 | 0.10% | unattested |
| BT11 | - clause `Article II` in `willow-bot` docs: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:205 | 0.09% | unattested |
| BU1 | - clause `II.1` is line 161 of the constitution: Capabilities are enumerated, not inferred. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:209 | 0.14% | unattested |
| BU2 | - clause `II.1` verdict, from the human-kept declarations: undeclared. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:210 | 0.11% | unattested |
| BU3 | - clause `II.1` in `willows-grove` code: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:211 | 0.09% | unattested |
| BU4 | - clause `II.1` in `willows-grove` tests: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:212 | 0.09% | unattested |
| BU5 | - clause `II.1` in `willows-grove` docs: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:213 | 0.09% | unattested |
| BU6 | - clause `II.1` in `willow-mcp` code: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:214 | 0.08% | unattested |
| BU7 | - clause `II.1` in `willow-mcp` tests: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:215 | 0.09% | unattested |
| BU8 | - clause `II.1` in `willow-mcp` docs: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:216 | 0.08% | unattested |
| BU9 | - clause `II.1` in `willow-bot` code: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:217 | 0.08% | unattested |
| BU10 | - clause `II.1` in `willow-bot` tests: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:218 | 0.09% | unattested |
| BU11 | - clause `II.1` in `willow-bot` docs: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:219 | 0.08% | unattested |
| BV1 | - clause `II.2` is line 163 of the constitution: Creation is reserved; delegation is witnessed. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:223 | 0.15% | unattested |
| BV2 | - clause `II.2` verdict, from the human-kept declarations: undeclared. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:224 | 0.11% | unattested |
| BV3 | - clause `II.2` in `willows-grove` code: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:225 | 0.09% | unattested |
| BV4 | - clause `II.2` in `willows-grove` tests: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:226 | 0.09% | unattested |
| BV5 | - clause `II.2` in `willows-grove` docs: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:227 | 0.09% | unattested |
| BV6 | - clause `II.2` in `willow-mcp` code: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:228 | 0.08% | unattested |
| BV7 | - clause `II.2` in `willow-mcp` tests: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:229 | 0.09% | unattested |
| BV8 | - clause `II.2` in `willow-mcp` docs: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:230 | 0.08% | unattested |
| BV9 | - clause `II.2` in `willow-bot` code: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:231 | 0.08% | unattested |
| BV10 | - clause `II.2` in `willow-bot` tests: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:232 | 0.09% | unattested |
| BV11 | - clause `II.2` in `willow-bot` docs: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:233 | 0.08% | unattested |
| BW1 | - clause `II.3` is line 165 of the constitution: The veto, and its limits. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:237 | 0.12% | unattested |
| BW2 | - clause `II.3` verdict, from the human-kept declarations: undeclared. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:238 | 0.11% | unattested |
| BW3 | - clause `II.3` in `willows-grove` code: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:239 | 0.09% | unattested |
| BW4 | - clause `II.3` in `willows-grove` tests: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:240 | 0.09% | unattested |
| BW5 | - clause `II.3` in `willows-grove` docs: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:241 | 0.09% | unattested |
| BW6 | - clause `II.3` in `willow-mcp` code: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:242 | 0.08% | unattested |
| BW7 | - clause `II.3` in `willow-mcp` tests: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:243 | 0.09% | unattested |
| BW8 | - clause `II.3` in `willow-mcp` docs: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:244 | 0.08% | unattested |
| BW9 | - clause `II.3` in `willow-bot` code: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:245 | 0.08% | unattested |
| BW10 | - clause `II.3` in `willow-bot` tests: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:246 | 0.09% | unattested |
| BW11 | - clause `II.3` in `willow-bot` docs: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:247 | 0.08% | unattested |
| BX1 | - clause `Article III` is line 180 of the constitution: Reach & Jurisdiction. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:251 | 0.12% | unattested |
| BX2 | - clause `Article III` verdict, from the human-kept declarations: undeclared. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:252 | 0.12% | unattested |
| BX3 | - clause `Article III` in `willows-grove` code: 4 files cite it: `docs/design/one-script/onescript/boot.py`, `docs/design/one-script/onescript/gate.py`, `docs/design/one-script/onescript/resolve.py`, `governance/compliance/cases/const_0_3_egress.py`. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:253 | 0.39% | unattested |
| BX4 | - clause `Article III` in `willows-grove` tests: 3 files cite it: `docs/design/one-script/onescript/tests/test_incoming.py`, `docs/design/one-script/onescript/tests/test_layers.py`, `docs/design/one-script/onescript/tests/test_onescript.py`. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:254 | 0.38% | unattested |
| BX5 | - clause `Article III` in `willows-grove` docs: 5 files cite it: `docs/design/one-box/rules-cross-table-2026-10-06.md`, `docs/design/one-script/constitution-proposal/CONSTITUTION.neutral.proposed.md`, `docs/design/one-script/constitution-proposal/CONSTITUTION.proposed.md`, `docs/design/one-script/incoming/haiku-2026-10-02/proposal-overnight-and-morning-screen.md`, `docs/design/one-script/next-pile.md`. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:255 | 0.63% | unattested |
| BX6 | - clause `Article III` in `willow-mcp` code: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:256 | 0.10% | unattested |
| BX7 | - clause `Article III` in `willow-mcp` tests: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:257 | 0.10% | unattested |
| BX8 | - clause `Article III` in `willow-mcp` docs: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:258 | 0.10% | unattested |
| BX9 | - clause `Article III` in `willow-bot` code: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:259 | 0.10% | unattested |
| BX10 | - clause `Article III` in `willow-bot` tests: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:260 | 0.10% | unattested |
| BX11 | - clause `Article III` in `willow-bot` docs: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:261 | 0.10% | unattested |
| BY1 | - clause `III.1` is line 184 of the constitution: Default-deny. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:265 | 0.10% | unattested |
| BY2 | - clause `III.1` verdict, from the human-kept declarations: undeclared. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:266 | 0.11% | unattested |
| BY3 | - clause `III.1` in `willows-grove` code: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:267 | 0.09% | unattested |
| BY4 | - clause `III.1` in `willows-grove` tests: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:268 | 0.09% | unattested |
| BY5 | - clause `III.1` in `willows-grove` docs: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:269 | 0.09% | unattested |
| BY6 | - clause `III.1` in `willow-mcp` code: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:270 | 0.09% | unattested |
| BY7 | - clause `III.1` in `willow-mcp` tests: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:271 | 0.09% | unattested |
| BY8 | - clause `III.1` in `willow-mcp` docs: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:272 | 0.09% | unattested |
| BY9 | - clause `III.1` in `willow-bot` code: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:273 | 0.09% | unattested |
| BY10 | - clause `III.1` in `willow-bot` tests: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:274 | 0.09% | unattested |
| BY11 | - clause `III.1` in `willow-bot` docs: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:275 | 0.09% | unattested |
| BZ1 | - clause `III.2` is line 186 of the constitution: Pre-Approved Scope is the standing grant. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:279 | 0.14% | unattested |
| BZ2 | - clause `III.2` verdict, from the human-kept declarations: undeclared. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:280 | 0.11% | unattested |
| BZ3 | - clause `III.2` in `willows-grove` code: 1 file cites it: `web/fixtures/envelopes.json`. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:281 | 0.14% | unattested |
| BZ4 | - clause `III.2` in `willows-grove` tests: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:282 | 0.09% | unattested |
| BZ5 | - clause `III.2` in `willows-grove` docs: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:283 | 0.09% | unattested |
| BZ6 | - clause `III.2` in `willow-mcp` code: 4 files cite it: `.willow/constitutional/pre-approved.json`, `.willow/constitutional/syscall-table.json`, `src/willow_mcp/bundle/constitutional/pre-approved.json`, `src/willow_mcp/bundle/constitutional/syscall-table.json`. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:284 | 0.41% | unattested |
| BZ7 | - clause `III.2` in `willow-mcp` tests: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:285 | 0.09% | unattested |
| BZ8 | - clause `III.2` in `willow-mcp` docs: 1 file cites it: `docs/design/federation-wire-format.md`. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:286 | 0.15% | unattested |
| BZ9 | - clause `III.2` in `willow-bot` code: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:287 | 0.09% | unattested |
| BZ10 | - clause `III.2` in `willow-bot` tests: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:288 | 0.09% | unattested |
| BZ11 | - clause `III.2` in `willow-bot` docs: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:289 | 0.09% | unattested |
| CA1 | - clause `III.3` is line 188 of the constitution: Every grant expires. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:293 | 0.11% | unattested |
| CA2 | - clause `III.3` verdict, from the human-kept declarations: undeclared. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:294 | 0.11% | unattested |
| CA3 | - clause `III.3` in `willows-grove` code: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:295 | 0.09% | unattested |
| CA4 | - clause `III.3` in `willows-grove` tests: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:296 | 0.09% | unattested |
| CA5 | - clause `III.3` in `willows-grove` docs: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:297 | 0.09% | unattested |
| CA6 | - clause `III.3` in `willow-mcp` code: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:298 | 0.09% | unattested |
| CA7 | - clause `III.3` in `willow-mcp` tests: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:299 | 0.09% | unattested |
| CA8 | - clause `III.3` in `willow-mcp` docs: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:300 | 0.09% | unattested |
| CA9 | - clause `III.3` in `willow-bot` code: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:301 | 0.09% | unattested |
| CA10 | - clause `III.3` in `willow-bot` tests: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:302 | 0.09% | unattested |
| CA11 | - clause `III.3` in `willow-bot` docs: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:303 | 0.09% | unattested |
| CB1 | - clause `III.4` is line 190 of the constitution: Reach is audited. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:307 | 0.10% | unattested |
| CB2 | - clause `III.4` verdict, from the human-kept declarations: undeclared. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:308 | 0.11% | unattested |
| CB3 | - clause `III.4` in `willows-grove` code: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:309 | 0.09% | unattested |
| CB4 | - clause `III.4` in `willows-grove` tests: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:310 | 0.09% | unattested |
| CB5 | - clause `III.4` in `willows-grove` docs: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:311 | 0.09% | unattested |
| CB6 | - clause `III.4` in `willow-mcp` code: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:312 | 0.09% | unattested |
| CB7 | - clause `III.4` in `willow-mcp` tests: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:313 | 0.09% | unattested |
| CB8 | - clause `III.4` in `willow-mcp` docs: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:314 | 0.09% | unattested |
| CB9 | - clause `III.4` in `willow-bot` code: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:315 | 0.09% | unattested |
| CB10 | - clause `III.4` in `willow-bot` tests: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:316 | 0.09% | unattested |
| CB11 | - clause `III.4` in `willow-bot` docs: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:317 | 0.09% | unattested |
| CC1 | - clause `III.5` is line 192 of the constitution: Reach guards what leaves. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:321 | 0.12% | unattested |
| CC2 | - clause `III.5` verdict, from the human-kept declarations: undeclared. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:322 | 0.11% | unattested |
| CC3 | - clause `III.5` in `willows-grove` code: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:323 | 0.09% | unattested |
| CC4 | - clause `III.5` in `willows-grove` tests: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:324 | 0.09% | unattested |
| CC5 | - clause `III.5` in `willows-grove` docs: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:325 | 0.09% | unattested |
| CC6 | - clause `III.5` in `willow-mcp` code: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:326 | 0.09% | unattested |
| CC7 | - clause `III.5` in `willow-mcp` tests: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:327 | 0.09% | unattested |
| CC8 | - clause `III.5` in `willow-mcp` docs: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:328 | 0.09% | unattested |
| CC9 | - clause `III.5` in `willow-bot` code: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:329 | 0.09% | unattested |
| CC10 | - clause `III.5` in `willow-bot` tests: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:330 | 0.09% | unattested |
| CC11 | - clause `III.5` in `willow-bot` docs: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:331 | 0.09% | unattested |
| CD1 | - clause `Article IV` is line 207 of the constitution: Knowledge & Canon. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:335 | 0.11% | unattested |
| CD2 | - clause `Article IV` verdict, from the human-kept declarations: undeclared. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:336 | 0.12% | unattested |
| CD3 | - clause `Article IV` in `willows-grove` code: 5 files cite it: `docs/design/one-script/onescript/boot.py`, `docs/design/one-script/onescript/predict.py`, `docs/design/one-script/onescript/resolve.py`, `docs/design/one-script/onescript/reverse.py`, `docs/design/one-script/onescript/view.py`. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:337 | 0.46% | unattested |
| CD4 | - clause `Article IV` in `willows-grove` tests: 1 file cites it: `docs/design/one-script/onescript/tests/test_onescript.py`. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:338 | 0.19% | unattested |
| CD5 | - clause `Article IV` in `willows-grove` docs: 7 files cite it: `docs/design/one-box/rules-cross-table-2026-10-06.md`, `docs/design/one-script/constitution-proposal/CONSTITUTION.neutral.proposed.md`, `docs/design/one-script/constitution-proposal/CONSTITUTION.proposed.md`, `docs/design/one-script/incoming/haiku-2026-10-02/PROPOSALS-SUMMARY.md`, … | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:339 | 0.88% | unattested |
| CD6 | - clause `Article IV` in `willow-mcp` code: 1 file cites it: `src/willow_mcp/mem_ratify/ratify.py`. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:340 | 0.15% | unattested |
| CD7 | - clause `Article IV` in `willow-mcp` tests: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:341 | 0.10% | unattested |
| CD8 | - clause `Article IV` in `willow-mcp` docs: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:342 | 0.09% | unattested |
| CD9 | - clause `Article IV` in `willow-bot` code: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:343 | 0.09% | unattested |
| CD10 | - clause `Article IV` in `willow-bot` tests: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:344 | 0.10% | unattested |
| CD11 | - clause `Article IV` in `willow-bot` docs: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:345 | 0.09% | unattested |
| CE1 | - clause `IV.1` is line 211 of the constitution: Two axes, and the three tiers they compose. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:349 | 0.14% | unattested |
| CE2 | - clause `IV.1` verdict, from the human-kept declarations: undeclared. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:350 | 0.11% | unattested |
| CE3 | - clause `IV.1` in `willows-grove` code: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:351 | 0.09% | unattested |
| CE4 | - clause `IV.1` in `willows-grove` tests: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:352 | 0.09% | unattested |
| CE5 | - clause `IV.1` in `willows-grove` docs: 1 file cites it: `governance/CASEBOOK.md`. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:353 | 0.13% | unattested |
| CE6 | - clause `IV.1` in `willow-mcp` code: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:354 | 0.08% | unattested |
| CE7 | - clause `IV.1` in `willow-mcp` tests: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:355 | 0.09% | unattested |
| CE8 | - clause `IV.1` in `willow-mcp` docs: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:356 | 0.08% | unattested |
| CE9 | - clause `IV.1` in `willow-bot` code: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:357 | 0.08% | unattested |
| CE10 | - clause `IV.1` in `willow-bot` tests: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:358 | 0.09% | unattested |
| CE11 | - clause `IV.1` in `willow-bot` docs: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:359 | 0.08% | unattested |
| CF1 | - clause `IV.2` is line 229 of the constitution: Anyone proposes; no one ratifies their own. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:363 | 0.14% | unattested |
| CF2 | - clause `IV.2` verdict, from the human-kept declarations: undeclared. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:364 | 0.11% | unattested |
| CF3 | - clause `IV.2` in `willows-grove` code: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:365 | 0.09% | unattested |
| CF4 | - clause `IV.2` in `willows-grove` tests: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:366 | 0.09% | unattested |
| CF5 | - clause `IV.2` in `willows-grove` docs: 1 file cites it: `governance/CASEBOOK.md`. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:367 | 0.13% | unattested |
| CF6 | - clause `IV.2` in `willow-mcp` code: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:368 | 0.08% | unattested |
| CF7 | - clause `IV.2` in `willow-mcp` tests: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:369 | 0.09% | unattested |
| CF8 | - clause `IV.2` in `willow-mcp` docs: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:370 | 0.08% | unattested |
| CF9 | - clause `IV.2` in `willow-bot` code: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:371 | 0.08% | unattested |
| CF10 | - clause `IV.2` in `willow-bot` tests: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:372 | 0.09% | unattested |
| CF11 | - clause `IV.2` in `willow-bot` docs: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:373 | 0.08% | unattested |
| CG1 | - clause `IV.3` is line 231 of the constitution: Canonical costs the most. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:377 | 0.12% | unattested |
| CG2 | - clause `IV.3` verdict, from the human-kept declarations: undeclared. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:378 | 0.11% | unattested |
| CG3 | - clause `IV.3` in `willows-grove` code: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:379 | 0.09% | unattested |
| CG4 | - clause `IV.3` in `willows-grove` tests: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:380 | 0.09% | unattested |
| CG5 | - clause `IV.3` in `willows-grove` docs: 1 file cites it: `docs/design/one-script/incoming/haiku-2026-10-02/PROPOSALS-SUMMARY.md`. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:381 | 0.20% | unattested |
| CG6 | - clause `IV.3` in `willow-mcp` code: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:382 | 0.08% | unattested |
| CG7 | - clause `IV.3` in `willow-mcp` tests: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:383 | 0.09% | unattested |
| CG8 | - clause `IV.3` in `willow-mcp` docs: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:384 | 0.08% | unattested |
| CG9 | - clause `IV.3` in `willow-bot` code: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:385 | 0.08% | unattested |
| CG10 | - clause `IV.3` in `willow-bot` tests: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:386 | 0.09% | unattested |
| CG11 | - clause `IV.3` in `willow-bot` docs: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:387 | 0.08% | unattested |
| CH1 | - clause `IV.5` is line 235 of the constitution: Neither axis may be inferred from the other. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:391 | 0.15% | unattested |
| CH2 | - clause `IV.5` verdict, from the human-kept declarations: undeclared. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:392 | 0.11% | unattested |
| CH3 | - clause `IV.5` in `willows-grove` code: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:393 | 0.09% | unattested |
| CH4 | - clause `IV.5` in `willows-grove` tests: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:394 | 0.09% | unattested |
| CH5 | - clause `IV.5` in `willows-grove` docs: 1 file cites it: `governance/CASEBOOK.md`. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:395 | 0.13% | unattested |
| CH6 | - clause `IV.5` in `willow-mcp` code: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:396 | 0.08% | unattested |
| CH7 | - clause `IV.5` in `willow-mcp` tests: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:397 | 0.09% | unattested |
| CH8 | - clause `IV.5` in `willow-mcp` docs: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:398 | 0.08% | unattested |
| CH9 | - clause `IV.5` in `willow-bot` code: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:399 | 0.08% | unattested |
| CH10 | - clause `IV.5` in `willow-bot` tests: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:400 | 0.09% | unattested |
| CH11 | - clause `IV.5` in `willow-bot` docs: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:401 | 0.08% | unattested |
| CI1 | - clause `IV.6` is line 237 of the constitution: A verifier is an attribution, not a warrant. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:405 | 0.15% | unattested |
| CI2 | - clause `IV.6` verdict, from the human-kept declarations: undeclared. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:406 | 0.11% | unattested |
| CI3 | - clause `IV.6` in `willows-grove` code: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:407 | 0.09% | unattested |
| CI4 | - clause `IV.6` in `willows-grove` tests: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:408 | 0.09% | unattested |
| CI5 | - clause `IV.6` in `willows-grove` docs: 1 file cites it: `governance/CASEBOOK.md`. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:409 | 0.13% | unattested |
| CI6 | - clause `IV.6` in `willow-mcp` code: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:410 | 0.08% | unattested |
| CI7 | - clause `IV.6` in `willow-mcp` tests: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:411 | 0.09% | unattested |
| CI8 | - clause `IV.6` in `willow-mcp` docs: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:412 | 0.08% | unattested |
| CI9 | - clause `IV.6` in `willow-bot` code: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:413 | 0.08% | unattested |
| CI10 | - clause `IV.6` in `willow-bot` tests: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:414 | 0.09% | unattested |
| CI11 | - clause `IV.6` in `willow-bot` docs: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:415 | 0.08% | unattested |
| CJ1 | - clause `IV.4` is line 239 of the constitution: Debasement is refused, demotion is evidenced. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:419 | 0.15% | unattested |
| CJ2 | - clause `IV.4` verdict, from the human-kept declarations: undeclared. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:420 | 0.11% | unattested |
| CJ3 | - clause `IV.4` in `willows-grove` code: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:421 | 0.09% | unattested |
| CJ4 | - clause `IV.4` in `willows-grove` tests: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:422 | 0.09% | unattested |
| CJ5 | - clause `IV.4` in `willows-grove` docs: 1 file cites it: `governance/CASEBOOK.md`. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:423 | 0.13% | unattested |
| CJ6 | - clause `IV.4` in `willow-mcp` code: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:424 | 0.08% | unattested |
| CJ7 | - clause `IV.4` in `willow-mcp` tests: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:425 | 0.09% | unattested |
| CJ8 | - clause `IV.4` in `willow-mcp` docs: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:426 | 0.08% | unattested |
| CJ9 | - clause `IV.4` in `willow-bot` code: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:427 | 0.08% | unattested |
| CJ10 | - clause `IV.4` in `willow-bot` tests: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:428 | 0.09% | unattested |
| CJ11 | - clause `IV.4` in `willow-bot` docs: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:429 | 0.08% | unattested |
| CK1 | - clause `IV.7` is line 241 of the constitution: Below Canonical is kept, and nothing is discarded. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:433 | 0.15% | unattested |
| CK2 | - clause `IV.7` verdict, from the human-kept declarations: undeclared. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:434 | 0.11% | unattested |
| CK3 | - clause `IV.7` in `willows-grove` code: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:435 | 0.09% | unattested |
| CK4 | - clause `IV.7` in `willows-grove` tests: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:436 | 0.09% | unattested |
| CK5 | - clause `IV.7` in `willows-grove` docs: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:437 | 0.09% | unattested |
| CK6 | - clause `IV.7` in `willow-mcp` code: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:438 | 0.08% | unattested |
| CK7 | - clause `IV.7` in `willow-mcp` tests: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:439 | 0.09% | unattested |
| CK8 | - clause `IV.7` in `willow-mcp` docs: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:440 | 0.08% | unattested |
| CK9 | - clause `IV.7` in `willow-bot` code: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:441 | 0.08% | unattested |
| CK10 | - clause `IV.7` in `willow-bot` tests: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:442 | 0.09% | unattested |
| CK11 | - clause `IV.7` in `willow-bot` docs: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:443 | 0.08% | unattested |
| CL1 | - clause `IV.8` is line 243 of the constitution: The recorded before the new. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:447 | 0.12% | unattested |
| CL2 | - clause `IV.8` verdict, from the human-kept declarations: undeclared. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:448 | 0.11% | unattested |
| CL3 | - clause `IV.8` in `willows-grove` code: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:449 | 0.09% | unattested |
| CL4 | - clause `IV.8` in `willows-grove` tests: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:450 | 0.09% | unattested |
| CL5 | - clause `IV.8` in `willows-grove` docs: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:451 | 0.09% | unattested |
| CL6 | - clause `IV.8` in `willow-mcp` code: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:452 | 0.08% | unattested |
| CL7 | - clause `IV.8` in `willow-mcp` tests: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:453 | 0.09% | unattested |
| CL8 | - clause `IV.8` in `willow-mcp` docs: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:454 | 0.08% | unattested |
| CL9 | - clause `IV.8` in `willow-bot` code: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:455 | 0.08% | unattested |
| CL10 | - clause `IV.8` in `willow-bot` tests: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:456 | 0.09% | unattested |
| CL11 | - clause `IV.8` in `willow-bot` docs: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:457 | 0.08% | unattested |
| CM1 | - clause `Article V` is line 263 of the constitution: The Human & Delegation. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:461 | 0.12% | unattested |
| CM2 | - clause `Article V` verdict, from the human-kept declarations: undeclared. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:462 | 0.12% | unattested |
| CM3 | - clause `Article V` in `willows-grove` code: 2 files cite it: `docs/design/one-script/onescript/boot.py`, `docs/design/one-script/onescript/gate.py`. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:463 | 0.23% | unattested |
| CM4 | - clause `Article V` in `willows-grove` tests: 2 files cite it: `docs/design/one-script/onescript/tests/test_onescript.py`, `tests/test_const_coverage.py`. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:464 | 0.24% | unattested |
| CM5 | - clause `Article V` in `willows-grove` docs: 4 files cite it: `docs/design/one-script/constitution-proposal/CONSTITUTION.neutral.proposed.md`, `docs/design/one-script/constitution-proposal/CONSTITUTION.proposed.md`, `docs/design/one-script/incoming/haiku-2026-10-02/PROPOSALS-SUMMARY.md`, `docs/design/willow-grove-premise.md`. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:465 | 0.51% | unattested |
| CM6 | - clause `Article V` in `willow-mcp` code: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:466 | 0.09% | unattested |
| CM7 | - clause `Article V` in `willow-mcp` tests: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:467 | 0.09% | unattested |
| CM8 | - clause `Article V` in `willow-mcp` docs: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:468 | 0.09% | unattested |
| CM9 | - clause `Article V` in `willow-bot` code: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:469 | 0.09% | unattested |
| CM10 | - clause `Article V` in `willow-bot` tests: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:470 | 0.09% | unattested |
| CM11 | - clause `Article V` in `willow-bot` docs: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:471 | 0.09% | unattested |
| CN1 | - clause `V.1` is line 267 of the constitution: Reserved decisions. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:475 | 0.10% | unattested |
| CN2 | - clause `V.1` verdict, from the human-kept declarations: undeclared. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:476 | 0.11% | unattested |
| CN3 | - clause `V.1` in `willows-grove` code: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:477 | 0.09% | unattested |
| CN4 | - clause `V.1` in `willows-grove` tests: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:478 | 0.09% | unattested |
| CN5 | - clause `V.1` in `willows-grove` docs: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:479 | 0.09% | unattested |
| CN6 | - clause `V.1` in `willow-mcp` code: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:480 | 0.08% | unattested |
| CN7 | - clause `V.1` in `willow-mcp` tests: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:481 | 0.08% | unattested |
| CN8 | - clause `V.1` in `willow-mcp` docs: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:482 | 0.08% | unattested |
| CN9 | - clause `V.1` in `willow-bot` code: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:483 | 0.08% | unattested |
| CN10 | - clause `V.1` in `willow-bot` tests: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:484 | 0.08% | unattested |
| CN11 | - clause `V.1` in `willow-bot` docs: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:485 | 0.08% | unattested |
| CO1 | - clause `V.2` is line 269 of the constitution: Delegation is bounded and revocable. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:489 | 0.13% | unattested |
| CO2 | - clause `V.2` verdict, from the human-kept declarations: undeclared. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:490 | 0.11% | unattested |
| CO3 | - clause `V.2` in `willows-grove` code: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:491 | 0.09% | unattested |
| CO4 | - clause `V.2` in `willows-grove` tests: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:492 | 0.09% | unattested |
| CO5 | - clause `V.2` in `willows-grove` docs: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:493 | 0.09% | unattested |
| CO6 | - clause `V.2` in `willow-mcp` code: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:494 | 0.08% | unattested |
| CO7 | - clause `V.2` in `willow-mcp` tests: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:495 | 0.08% | unattested |
| CO8 | - clause `V.2` in `willow-mcp` docs: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:496 | 0.08% | unattested |
| CO9 | - clause `V.2` in `willow-bot` code: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:497 | 0.08% | unattested |
| CO10 | - clause `V.2` in `willow-bot` tests: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:498 | 0.08% | unattested |
| CO11 | - clause `V.2` in `willow-bot` docs: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:499 | 0.08% | unattested |
| CP1 | - clause `V.3` is line 271 of the constitution: Stepping back, and succession. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:503 | 0.12% | unattested |
| CP2 | - clause `V.3` verdict, from the human-kept declarations: undeclared. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:504 | 0.11% | unattested |
| CP3 | - clause `V.3` in `willows-grove` code: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:505 | 0.09% | unattested |
| CP4 | - clause `V.3` in `willows-grove` tests: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:506 | 0.09% | unattested |
| CP5 | - clause `V.3` in `willows-grove` docs: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:507 | 0.09% | unattested |
| CP6 | - clause `V.3` in `willow-mcp` code: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:508 | 0.08% | unattested |
| CP7 | - clause `V.3` in `willow-mcp` tests: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:509 | 0.08% | unattested |
| CP8 | - clause `V.3` in `willow-mcp` docs: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:510 | 0.08% | unattested |
| CP9 | - clause `V.3` in `willow-bot` code: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:511 | 0.08% | unattested |
| CP10 | - clause `V.3` in `willow-bot` tests: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:512 | 0.08% | unattested |
| CP11 | - clause `V.3` in `willow-bot` docs: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:513 | 0.08% | unattested |
| CQ1 | - clause `V.4` is line 273 of the constitution: Operator Incapacity. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:517 | 0.11% | unattested |
| CQ2 | - clause `V.4` verdict, from the human-kept declarations: undeclared. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:518 | 0.11% | unattested |
| CQ3 | - clause `V.4` in `willows-grove` code: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:519 | 0.09% | unattested |
| CQ4 | - clause `V.4` in `willows-grove` tests: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:520 | 0.09% | unattested |
| CQ5 | - clause `V.4` in `willows-grove` docs: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:521 | 0.09% | unattested |
| CQ6 | - clause `V.4` in `willow-mcp` code: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:522 | 0.08% | unattested |
| CQ7 | - clause `V.4` in `willow-mcp` tests: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:523 | 0.08% | unattested |
| CQ8 | - clause `V.4` in `willow-mcp` docs: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:524 | 0.08% | unattested |
| CQ9 | - clause `V.4` in `willow-bot` code: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:525 | 0.08% | unattested |
| CQ10 | - clause `V.4` in `willow-bot` tests: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:526 | 0.08% | unattested |
| CQ11 | - clause `V.4` in `willow-bot` docs: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:527 | 0.08% | unattested |
| CR1 | - clause `V.4a` is line 275 of the constitution: Declaration of Incapacity (the compromised operator). | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:531 | 0.16% | unattested |
| CR2 | - clause `V.4a` verdict, from the human-kept declarations: undeclared. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:532 | 0.11% | unattested |
| CR3 | - clause `V.4a` in `willows-grove` code: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:533 | 0.09% | unattested |
| CR4 | - clause `V.4a` in `willows-grove` tests: 1 file cites it: `tests/test_const_coverage.py`. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:534 | 0.14% | unattested |
| CR5 | - clause `V.4a` in `willows-grove` docs: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:535 | 0.09% | unattested |
| CR6 | - clause `V.4a` in `willow-mcp` code: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:536 | 0.08% | unattested |
| CR7 | - clause `V.4a` in `willow-mcp` tests: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:537 | 0.09% | unattested |
| CR8 | - clause `V.4a` in `willow-mcp` docs: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:538 | 0.08% | unattested |
| CR9 | - clause `V.4a` in `willow-bot` code: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:539 | 0.08% | unattested |
| CR10 | - clause `V.4a` in `willow-bot` tests: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:540 | 0.09% | unattested |
| CR11 | - clause `V.4a` in `willow-bot` docs: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:541 | 0.08% | unattested |
| CS1 | - clause `V.4b` is line 277 of the constitution: Hold. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:545 | 0.08% | unattested |
| CS2 | - clause `V.4b` verdict, from the human-kept declarations: undeclared. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:546 | 0.11% | unattested |
| CS3 | - clause `V.4b` in `willows-grove` code: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:547 | 0.09% | unattested |
| CS4 | - clause `V.4b` in `willows-grove` tests: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:548 | 0.09% | unattested |
| CS5 | - clause `V.4b` in `willows-grove` docs: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:549 | 0.09% | unattested |
| CS6 | - clause `V.4b` in `willow-mcp` code: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:550 | 0.08% | unattested |
| CS7 | - clause `V.4b` in `willow-mcp` tests: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:551 | 0.09% | unattested |
| CS8 | - clause `V.4b` in `willow-mcp` docs: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:552 | 0.08% | unattested |
| CS9 | - clause `V.4b` in `willow-bot` code: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:553 | 0.08% | unattested |
| CS10 | - clause `V.4b` in `willow-bot` tests: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:554 | 0.09% | unattested |
| CS11 | - clause `V.4b` in `willow-bot` docs: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:555 | 0.08% | unattested |
| CT1 | - clause `V.5` is line 279 of the constitution: The Duty to Disobey. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:559 | 0.11% | unattested |
| CT2 | - clause `V.5` verdict, from the human-kept declarations: undeclared. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:560 | 0.11% | unattested |
| CT3 | - clause `V.5` in `willows-grove` code: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:561 | 0.09% | unattested |
| CT4 | - clause `V.5` in `willows-grove` tests: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:562 | 0.09% | unattested |
| CT5 | - clause `V.5` in `willows-grove` docs: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:563 | 0.09% | unattested |
| CT6 | - clause `V.5` in `willow-mcp` code: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:564 | 0.08% | unattested |
| CT7 | - clause `V.5` in `willow-mcp` tests: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:565 | 0.08% | unattested |
| CT8 | - clause `V.5` in `willow-mcp` docs: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:566 | 0.08% | unattested |
| CT9 | - clause `V.5` in `willow-bot` code: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:567 | 0.08% | unattested |
| CT10 | - clause `V.5` in `willow-bot` tests: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:568 | 0.08% | unattested |
| CT11 | - clause `V.5` in `willow-bot` docs: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:569 | 0.08% | unattested |
| CU1 | - clause `V.6` is line 281 of the constitution: Offers, not acts. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:573 | 0.10% | unattested |
| CU2 | - clause `V.6` verdict, from the human-kept declarations: undeclared. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:574 | 0.11% | unattested |
| CU3 | - clause `V.6` in `willows-grove` code: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:575 | 0.09% | unattested |
| CU4 | - clause `V.6` in `willows-grove` tests: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:576 | 0.09% | unattested |
| CU5 | - clause `V.6` in `willows-grove` docs: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:577 | 0.09% | unattested |
| CU6 | - clause `V.6` in `willow-mcp` code: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:578 | 0.08% | unattested |
| CU7 | - clause `V.6` in `willow-mcp` tests: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:579 | 0.08% | unattested |
| CU8 | - clause `V.6` in `willow-mcp` docs: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:580 | 0.08% | unattested |
| CU9 | - clause `V.6` in `willow-bot` code: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:581 | 0.08% | unattested |
| CU10 | - clause `V.6` in `willow-bot` tests: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:582 | 0.08% | unattested |
| CU11 | - clause `V.6` in `willow-bot` docs: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:583 | 0.08% | unattested |
| CV1 | - clause `V.7` is line 283 of the constitution: Attention belongs to the human. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:587 | 0.12% | unattested |
| CV2 | - clause `V.7` verdict, from the human-kept declarations: undeclared. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:588 | 0.11% | unattested |
| CV3 | - clause `V.7` in `willows-grove` code: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:589 | 0.09% | unattested |
| CV4 | - clause `V.7` in `willows-grove` tests: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:590 | 0.09% | unattested |
| CV5 | - clause `V.7` in `willows-grove` docs: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:591 | 0.09% | unattested |
| CV6 | - clause `V.7` in `willow-mcp` code: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:592 | 0.08% | unattested |
| CV7 | - clause `V.7` in `willow-mcp` tests: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:593 | 0.08% | unattested |
| CV8 | - clause `V.7` in `willow-mcp` docs: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:594 | 0.08% | unattested |
| CV9 | - clause `V.7` in `willow-bot` code: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:595 | 0.08% | unattested |
| CV10 | - clause `V.7` in `willow-bot` tests: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:596 | 0.08% | unattested |
| CV11 | - clause `V.7` in `willow-bot` docs: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:597 | 0.08% | unattested |
| CW1 | - clause `V.8` is line 285 of the constitution: Escalation Budget. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:601 | 0.10% | unattested |
| CW2 | - clause `V.8` verdict, from the human-kept declarations: undeclared. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:602 | 0.11% | unattested |
| CW3 | - clause `V.8` in `willows-grove` code: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:603 | 0.09% | unattested |
| CW4 | - clause `V.8` in `willows-grove` tests: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:604 | 0.09% | unattested |
| CW5 | - clause `V.8` in `willows-grove` docs: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:605 | 0.09% | unattested |
| CW6 | - clause `V.8` in `willow-mcp` code: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:606 | 0.08% | unattested |
| CW7 | - clause `V.8` in `willow-mcp` tests: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:607 | 0.08% | unattested |
| CW8 | - clause `V.8` in `willow-mcp` docs: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:608 | 0.08% | unattested |
| CW9 | - clause `V.8` in `willow-bot` code: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:609 | 0.08% | unattested |
| CW10 | - clause `V.8` in `willow-bot` tests: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:610 | 0.08% | unattested |
| CW11 | - clause `V.8` in `willow-bot` docs: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:611 | 0.08% | unattested |
| CX1 | - clause `V.9` is line 287 of the constitution: Backpressure is reported state. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:615 | 0.12% | unattested |
| CX2 | - clause `V.9` verdict, from the human-kept declarations: undeclared. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:616 | 0.11% | unattested |
| CX3 | - clause `V.9` in `willows-grove` code: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:617 | 0.09% | unattested |
| CX4 | - clause `V.9` in `willows-grove` tests: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:618 | 0.09% | unattested |
| CX5 | - clause `V.9` in `willows-grove` docs: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:619 | 0.09% | unattested |
| CX6 | - clause `V.9` in `willow-mcp` code: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:620 | 0.08% | unattested |
| CX7 | - clause `V.9` in `willow-mcp` tests: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:621 | 0.08% | unattested |
| CX8 | - clause `V.9` in `willow-mcp` docs: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:622 | 0.08% | unattested |
| CX9 | - clause `V.9` in `willow-bot` code: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:623 | 0.08% | unattested |
| CX10 | - clause `V.9` in `willow-bot` tests: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:624 | 0.08% | unattested |
| CX11 | - clause `V.9` in `willow-bot` docs: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:625 | 0.08% | unattested |
| CY1 | - clause `Article VI` is line 315 of the constitution: The Record. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:629 | 0.10% | unattested |
| CY2 | - clause `Article VI` verdict, from the human-kept declarations: undeclared. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:630 | 0.12% | unattested |
| CY3 | - clause `Article VI` in `willows-grove` code: 3 files cite it: `docs/design/one-script/onescript/record.py`, `docs/design/one-script/onescript/view.py`, `docs/design/one-script/onescript/xref.py`. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:631 | 0.31% | unattested |
| CY4 | - clause `Article VI` in `willows-grove` tests: 5 files cite it: `docs/design/one-script/onescript/tests/test_incoming.py`, `docs/design/one-script/onescript/tests/test_layers.py`, `docs/design/one-script/onescript/tests/test_onescript.py`, `docs/design/one-script/onescript/tests/test_xref.py`, `tests/test_const_coverage.py`. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:632 | 0.51% | unattested |
| CY5 | - clause `Article VI` in `willows-grove` docs: 9 files cite it: `docs/design/one-box/research-2026-10-06.md`, `docs/design/one-box/rules-cross-table-2026-10-06.md`, `docs/design/one-script/constitution-proposal/CONSTITUTION.neutral.proposed.md`, `docs/design/one-script/constitution-proposal/CONSTITUTION.proposed.md`, `docs/design/one-script/constitution-proposal/CONSTITUTION.provenance.md`, … | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:633 | 0.98% | unattested |
| CY6 | - clause `Article VI` in `willow-mcp` code: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:634 | 0.09% | unattested |
| CY7 | - clause `Article VI` in `willow-mcp` tests: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:635 | 0.10% | unattested |
| CY8 | - clause `Article VI` in `willow-mcp` docs: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:636 | 0.09% | unattested |
| CY9 | - clause `Article VI` in `willow-bot` code: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:637 | 0.09% | unattested |
| CY10 | - clause `Article VI` in `willow-bot` tests: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:638 | 0.10% | unattested |
| CY11 | - clause `Article VI` in `willow-bot` docs: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:639 | 0.09% | unattested |
| CZ1 | - clause `VI.1` is line 319 of the constitution: Append and read, by standing. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:643 | 0.12% | unattested |
| CZ2 | - clause `VI.1` verdict, from the human-kept declarations: undeclared. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:644 | 0.11% | unattested |
| CZ3 | - clause `VI.1` in `willows-grove` code: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:645 | 0.09% | unattested |
| CZ4 | - clause `VI.1` in `willows-grove` tests: 1 file cites it: `tests/test_const_coverage.py`. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:646 | 0.14% | unattested |
| CZ5 | - clause `VI.1` in `willows-grove` docs: 1 file cites it: `governance/CASEBOOK.md`. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:647 | 0.13% | unattested |
| CZ6 | - clause `VI.1` in `willow-mcp` code: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:648 | 0.08% | unattested |
| CZ7 | - clause `VI.1` in `willow-mcp` tests: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:649 | 0.09% | unattested |
| CZ8 | - clause `VI.1` in `willow-mcp` docs: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:650 | 0.08% | unattested |
| CZ9 | - clause `VI.1` in `willow-bot` code: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:651 | 0.08% | unattested |
| CZ10 | - clause `VI.1` in `willow-bot` tests: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:652 | 0.09% | unattested |
| CZ11 | - clause `VI.1` in `willow-bot` docs: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:653 | 0.08% | unattested |
| DA1 | - clause `VI.2` is line 321 of the constitution: Content is inviolable. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:657 | 0.11% | unattested |
| DA2 | - clause `VI.2` verdict, from the human-kept declarations: undeclared. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:658 | 0.11% | unattested |
| DA3 | - clause `VI.2` in `willows-grove` code: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:659 | 0.09% | unattested |
| DA4 | - clause `VI.2` in `willows-grove` tests: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:660 | 0.09% | unattested |
| DA5 | - clause `VI.2` in `willows-grove` docs: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:661 | 0.09% | unattested |
| DA6 | - clause `VI.2` in `willow-mcp` code: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:662 | 0.08% | unattested |
| DA7 | - clause `VI.2` in `willow-mcp` tests: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:663 | 0.09% | unattested |
| DA8 | - clause `VI.2` in `willow-mcp` docs: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:664 | 0.08% | unattested |
| DA9 | - clause `VI.2` in `willow-bot` code: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:665 | 0.08% | unattested |
| DA10 | - clause `VI.2` in `willow-bot` tests: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:666 | 0.09% | unattested |
| DA11 | - clause `VI.2` in `willow-bot` docs: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:667 | 0.08% | unattested |
| DB1 | - clause `VI.3` is line 323 of the constitution: The split-brain problem. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:671 | 0.11% | unattested |
| DB2 | - clause `VI.3` verdict, from the human-kept declarations: undeclared. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:672 | 0.11% | unattested |
| DB3 | - clause `VI.3` in `willows-grove` code: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:673 | 0.09% | unattested |
| DB4 | - clause `VI.3` in `willows-grove` tests: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:674 | 0.09% | unattested |
| DB5 | - clause `VI.3` in `willows-grove` docs: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:675 | 0.09% | unattested |
| DB6 | - clause `VI.3` in `willow-mcp` code: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:676 | 0.08% | unattested |
| DB7 | - clause `VI.3` in `willow-mcp` tests: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:677 | 0.09% | unattested |
| DB8 | - clause `VI.3` in `willow-mcp` docs: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:678 | 0.08% | unattested |
| DB9 | - clause `VI.3` in `willow-bot` code: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:679 | 0.08% | unattested |
| DB10 | - clause `VI.3` in `willow-bot` tests: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:680 | 0.09% | unattested |
| DB11 | - clause `VI.3` in `willow-bot` docs: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:681 | 0.08% | unattested |
| DC1 | - clause `VI.4` is line 325 of the constitution: The auditor is not the actor. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:685 | 0.12% | unattested |
| DC2 | - clause `VI.4` verdict, from the human-kept declarations: undeclared. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:686 | 0.11% | unattested |
| DC3 | - clause `VI.4` in `willows-grove` code: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:687 | 0.09% | unattested |
| DC4 | - clause `VI.4` in `willows-grove` tests: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:688 | 0.09% | unattested |
| DC5 | - clause `VI.4` in `willows-grove` docs: 1 file cites it: `governance/CASEBOOK.md`. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:689 | 0.13% | unattested |
| DC6 | - clause `VI.4` in `willow-mcp` code: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:690 | 0.08% | unattested |
| DC7 | - clause `VI.4` in `willow-mcp` tests: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:691 | 0.09% | unattested |
| DC8 | - clause `VI.4` in `willow-mcp` docs: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:692 | 0.08% | unattested |
| DC9 | - clause `VI.4` in `willow-bot` code: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:693 | 0.08% | unattested |
| DC10 | - clause `VI.4` in `willow-bot` tests: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:694 | 0.09% | unattested |
| DC11 | - clause `VI.4` in `willow-bot` docs: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:695 | 0.08% | unattested |
| DD1 | - clause `VI.5` is line 327 of the constitution: Unanimity is recorded as a property, not assumed as a quality. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:699 | 0.17% | unattested |
| DD2 | - clause `VI.5` verdict, from the human-kept declarations: undeclared. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:700 | 0.11% | unattested |
| DD3 | - clause `VI.5` in `willows-grove` code: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:701 | 0.09% | unattested |
| DD4 | - clause `VI.5` in `willows-grove` tests: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:702 | 0.09% | unattested |
| DD5 | - clause `VI.5` in `willows-grove` docs: 1 file cites it: `docs/design/one-script/incoming/haiku-2026-10-02/PROPOSALS-SUMMARY.md`. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:703 | 0.20% | unattested |
| DD6 | - clause `VI.5` in `willow-mcp` code: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:704 | 0.08% | unattested |
| DD7 | - clause `VI.5` in `willow-mcp` tests: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:705 | 0.09% | unattested |
| DD8 | - clause `VI.5` in `willow-mcp` docs: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:706 | 0.08% | unattested |
| DD9 | - clause `VI.5` in `willow-bot` code: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:707 | 0.08% | unattested |
| DD10 | - clause `VI.5` in `willow-bot` tests: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:708 | 0.09% | unattested |
| DD11 | - clause `VI.5` in `willow-bot` docs: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:709 | 0.08% | unattested |
| DE1 | - clause `VI.6` is line 329 of the constitution: No smoothing. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:713 | 0.10% | unattested |
| DE2 | - clause `VI.6` verdict, from the human-kept declarations: undeclared. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:714 | 0.11% | unattested |
| DE3 | - clause `VI.6` in `willows-grove` code: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:715 | 0.09% | unattested |
| DE4 | - clause `VI.6` in `willows-grove` tests: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:716 | 0.09% | unattested |
| DE5 | - clause `VI.6` in `willows-grove` docs: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:717 | 0.09% | unattested |
| DE6 | - clause `VI.6` in `willow-mcp` code: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:718 | 0.08% | unattested |
| DE7 | - clause `VI.6` in `willow-mcp` tests: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:719 | 0.09% | unattested |
| DE8 | - clause `VI.6` in `willow-mcp` docs: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:720 | 0.08% | unattested |
| DE9 | - clause `VI.6` in `willow-bot` code: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:721 | 0.08% | unattested |
| DE10 | - clause `VI.6` in `willow-bot` tests: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:722 | 0.09% | unattested |
| DE11 | - clause `VI.6` in `willow-bot` docs: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:723 | 0.08% | unattested |
| DF1 | - clause `Article VII` is line 346 of the constitution: The Interpreter. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:727 | 0.11% | unattested |
| DF2 | - clause `Article VII` verdict, from the human-kept declarations: undeclared. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:728 | 0.12% | unattested |
| DF3 | - clause `Article VII` in `willows-grove` code: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:729 | 0.10% | unattested |
| DF4 | - clause `Article VII` in `willows-grove` tests: 1 file cites it: `tests/test_const_coverage.py`. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:730 | 0.15% | unattested |
| DF5 | - clause `Article VII` in `willows-grove` docs: 4 files cite it: `docs/design/one-script/constitution-proposal/CONSTITUTION.neutral.proposed.md`, `docs/design/one-script/constitution-proposal/CONSTITUTION.proposed.md`, `docs/design/willow-grove-premise.md`, `governance/CASEBOOK.md`. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:731 | 0.44% | unattested |
| DF6 | - clause `Article VII` in `willow-mcp` code: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:732 | 0.10% | unattested |
| DF7 | - clause `Article VII` in `willow-mcp` tests: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:733 | 0.10% | unattested |
| DF8 | - clause `Article VII` in `willow-mcp` docs: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:734 | 0.10% | unattested |
| DF9 | - clause `Article VII` in `willow-bot` code: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:735 | 0.10% | unattested |
| DF10 | - clause `Article VII` in `willow-bot` tests: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:736 | 0.10% | unattested |
| DF11 | - clause `Article VII` in `willow-bot` docs: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:737 | 0.10% | unattested |
| DG1 | - clause `VII.default` is line 352 of the constitution: Escalation holds the seat. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:741 | 0.13% | unattested |
| DG2 | - clause `VII.default` verdict, from the human-kept declarations: undeclared. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:742 | 0.12% | unattested |
| DG3 | - clause `VII.default` in `willows-grove` code: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:743 | 0.10% | unattested |
| DG4 | - clause `VII.default` in `willows-grove` tests: 1 file cites it: `tests/test_const_coverage.py`. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:744 | 0.15% | unattested |
| DG5 | - clause `VII.default` in `willows-grove` docs: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:745 | 0.10% | unattested |
| DG6 | - clause `VII.default` in `willow-mcp` code: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:746 | 0.10% | unattested |
| DG7 | - clause `VII.default` in `willow-mcp` tests: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:747 | 0.10% | unattested |
| DG8 | - clause `VII.default` in `willow-mcp` docs: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:748 | 0.10% | unattested |
| DG9 | - clause `VII.default` in `willow-bot` code: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:749 | 0.10% | unattested |
| DG10 | - clause `VII.default` in `willow-bot` tests: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:750 | 0.10% | unattested |
| DG11 | - clause `VII.default` in `willow-bot` docs: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:751 | 0.10% | unattested |
| DH1 | - clause `Article VIII` is line 377 of the constitution: Amendment. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:755 | 0.10% | unattested |
| DH2 | - clause `Article VIII` verdict, from the human-kept declarations: undeclared. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:756 | 0.12% | unattested |
| DH3 | - clause `Article VIII` in `willows-grove` code: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:757 | 0.10% | unattested |
| DH4 | - clause `Article VIII` in `willows-grove` tests: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:758 | 0.10% | unattested |
| DH5 | - clause `Article VIII` in `willows-grove` docs: 2 files cite it: `docs/design/one-script/constitution-proposal/CONSTITUTION.neutral.proposed.md`, `docs/design/one-script/constitution-proposal/CONSTITUTION.proposed.md`. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:759 | 0.34% | unattested |
| DH6 | - clause `Article VIII` in `willow-mcp` code: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:760 | 0.10% | unattested |
| DH7 | - clause `Article VIII` in `willow-mcp` tests: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:761 | 0.10% | unattested |
| DH8 | - clause `Article VIII` in `willow-mcp` docs: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:762 | 0.10% | unattested |
| DH9 | - clause `Article VIII` in `willow-bot` code: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:763 | 0.10% | unattested |
| DH10 | - clause `Article VIII` in `willow-bot` tests: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:764 | 0.10% | unattested |
| DH11 | - clause `Article VIII` in `willow-bot` docs: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:765 | 0.10% | unattested |
| DI1 | - clause `VIII.1` is line 381 of the constitution: Propose, weigh, ratify. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:769 | 0.12% | unattested |
| DI2 | - clause `VIII.1` verdict, from the human-kept declarations: undeclared. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:770 | 0.11% | unattested |
| DI3 | - clause `VIII.1` in `willows-grove` code: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:771 | 0.09% | unattested |
| DI4 | - clause `VIII.1` in `willows-grove` tests: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:772 | 0.09% | unattested |
| DI5 | - clause `VIII.1` in `willows-grove` docs: 1 file cites it: `docs/design/one-script/incoming/haiku-2026-10-02/PROPOSALS-SUMMARY.md`. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:773 | 0.21% | unattested |
| DI6 | - clause `VIII.1` in `willow-mcp` code: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:774 | 0.09% | unattested |
| DI7 | - clause `VIII.1` in `willow-mcp` tests: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:775 | 0.09% | unattested |
| DI8 | - clause `VIII.1` in `willow-mcp` docs: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:776 | 0.09% | unattested |
| DI9 | - clause `VIII.1` in `willow-bot` code: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:777 | 0.09% | unattested |
| DI10 | - clause `VIII.1` in `willow-bot` tests: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:778 | 0.09% | unattested |
| DI11 | - clause `VIII.1` in `willow-bot` docs: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:779 | 0.09% | unattested |
| DJ1 | - clause `VIII.2` is line 383 of the constitution: Emergency amendment is a bounded envelope. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:783 | 0.15% | unattested |
| DJ2 | - clause `VIII.2` verdict, from the human-kept declarations: undeclared. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:784 | 0.11% | unattested |
| DJ3 | - clause `VIII.2` in `willows-grove` code: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:785 | 0.09% | unattested |
| DJ4 | - clause `VIII.2` in `willows-grove` tests: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:786 | 0.09% | unattested |
| DJ5 | - clause `VIII.2` in `willows-grove` docs: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:787 | 0.09% | unattested |
| DJ6 | - clause `VIII.2` in `willow-mcp` code: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:788 | 0.09% | unattested |
| DJ7 | - clause `VIII.2` in `willow-mcp` tests: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:789 | 0.09% | unattested |
| DJ8 | - clause `VIII.2` in `willow-mcp` docs: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:790 | 0.09% | unattested |
| DJ9 | - clause `VIII.2` in `willow-bot` code: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:791 | 0.09% | unattested |
| DJ10 | - clause `VIII.2` in `willow-bot` tests: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:792 | 0.09% | unattested |
| DJ11 | - clause `VIII.2` in `willow-bot` docs: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:793 | 0.09% | unattested |
| DK1 | - clause `VIII.3` is line 385 of the constitution: Article 0 is beyond reach. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:797 | 0.12% | unattested |
| DK2 | - clause `VIII.3` verdict, from the human-kept declarations: undeclared. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:798 | 0.11% | unattested |
| DK3 | - clause `VIII.3` in `willows-grove` code: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:799 | 0.09% | unattested |
| DK4 | - clause `VIII.3` in `willows-grove` tests: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:800 | 0.09% | unattested |
| DK5 | - clause `VIII.3` in `willows-grove` docs: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:801 | 0.09% | unattested |
| DK6 | - clause `VIII.3` in `willow-mcp` code: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:802 | 0.09% | unattested |
| DK7 | - clause `VIII.3` in `willow-mcp` tests: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:803 | 0.09% | unattested |
| DK8 | - clause `VIII.3` in `willow-mcp` docs: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:804 | 0.09% | unattested |
| DK9 | - clause `VIII.3` in `willow-bot` code: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:805 | 0.09% | unattested |
| DK10 | - clause `VIII.3` in `willow-bot` tests: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:806 | 0.09% | unattested |
| DK11 | - clause `VIII.3` in `willow-bot` docs: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:807 | 0.09% | unattested |
| DL1 | - clause `Article IX` is line 400 of the constitution: Ratification & Founding. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:811 | 0.12% | unattested |
| DL2 | - clause `Article IX` verdict, from the human-kept declarations: undeclared. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:812 | 0.12% | unattested |
| DL3 | - clause `Article IX` in `willows-grove` code: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:813 | 0.10% | unattested |
| DL4 | - clause `Article IX` in `willows-grove` tests: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:814 | 0.10% | unattested |
| DL5 | - clause `Article IX` in `willows-grove` docs: 2 files cite it: `docs/design/one-script/constitution-proposal/CONSTITUTION.neutral.proposed.md`, `docs/design/one-script/constitution-proposal/CONSTITUTION.proposed.md`. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:815 | 0.34% | unattested |
| DL6 | - clause `Article IX` in `willow-mcp` code: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:816 | 0.09% | unattested |
| DL7 | - clause `Article IX` in `willow-mcp` tests: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:817 | 0.10% | unattested |
| DL8 | - clause `Article IX` in `willow-mcp` docs: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:818 | 0.09% | unattested |
| DL9 | - clause `Article IX` in `willow-bot` code: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:819 | 0.09% | unattested |
| DL10 | - clause `Article IX` in `willow-bot` tests: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:820 | 0.10% | unattested |
| DL11 | - clause `Article IX` in `willow-bot` docs: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:821 | 0.09% | unattested |
| DM1 | - clause `IX.1` is line 404 of the constitution: The genesis act. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:825 | 0.10% | unattested |
| DM2 | - clause `IX.1` verdict, from the human-kept declarations: undeclared. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:826 | 0.11% | unattested |
| DM3 | - clause `IX.1` in `willows-grove` code: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:827 | 0.09% | unattested |
| DM4 | - clause `IX.1` in `willows-grove` tests: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:828 | 0.09% | unattested |
| DM5 | - clause `IX.1` in `willows-grove` docs: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:829 | 0.09% | unattested |
| DM6 | - clause `IX.1` in `willow-mcp` code: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:830 | 0.08% | unattested |
| DM7 | - clause `IX.1` in `willow-mcp` tests: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:831 | 0.09% | unattested |
| DM8 | - clause `IX.1` in `willow-mcp` docs: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:832 | 0.08% | unattested |
| DM9 | - clause `IX.1` in `willow-bot` code: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:833 | 0.08% | unattested |
| DM10 | - clause `IX.1` in `willow-bot` tests: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:834 | 0.09% | unattested |
| DM11 | - clause `IX.1` in `willow-bot` docs: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:835 | 0.08% | unattested |
| DN1 | - clause `IX.2` is line 406 of the constitution: Witnesses and assent. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:839 | 0.11% | unattested |
| DN2 | - clause `IX.2` verdict, from the human-kept declarations: undeclared. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:840 | 0.11% | unattested |
| DN3 | - clause `IX.2` in `willows-grove` code: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:841 | 0.09% | unattested |
| DN4 | - clause `IX.2` in `willows-grove` tests: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:842 | 0.09% | unattested |
| DN5 | - clause `IX.2` in `willows-grove` docs: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:843 | 0.09% | unattested |
| DN6 | - clause `IX.2` in `willow-mcp` code: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:844 | 0.08% | unattested |
| DN7 | - clause `IX.2` in `willow-mcp` tests: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:845 | 0.09% | unattested |
| DN8 | - clause `IX.2` in `willow-mcp` docs: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:846 | 0.08% | unattested |
| DN9 | - clause `IX.2` in `willow-bot` code: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:847 | 0.08% | unattested |
| DN10 | - clause `IX.2` in `willow-bot` tests: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:848 | 0.09% | unattested |
| DN11 | - clause `IX.2` in `willow-bot` docs: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:849 | 0.08% | unattested |
| DO1 | - clause `IX.3` is line 408 of the constitution: Adoption and forking. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:853 | 0.11% | unattested |
| DO2 | - clause `IX.3` verdict, from the human-kept declarations: undeclared. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:854 | 0.11% | unattested |
| DO3 | - clause `IX.3` in `willows-grove` code: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:855 | 0.09% | unattested |
| DO4 | - clause `IX.3` in `willows-grove` tests: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:856 | 0.09% | unattested |
| DO5 | - clause `IX.3` in `willows-grove` docs: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:857 | 0.09% | unattested |
| DO6 | - clause `IX.3` in `willow-mcp` code: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:858 | 0.08% | unattested |
| DO7 | - clause `IX.3` in `willow-mcp` tests: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:859 | 0.09% | unattested |
| DO8 | - clause `IX.3` in `willow-mcp` docs: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:860 | 0.08% | unattested |
| DO9 | - clause `IX.3` in `willow-bot` code: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:861 | 0.08% | unattested |
| DO10 | - clause `IX.3` in `willow-bot` tests: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:862 | 0.09% | unattested |
| DO11 | - clause `IX.3` in `willow-bot` docs: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:863 | 0.08% | unattested |
| DP1 | - clause `IX.4` is line 410 of the constitution: Succession out of Safe Mode. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:867 | 0.12% | unattested |
| DP2 | - clause `IX.4` verdict, from the human-kept declarations: undeclared. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:868 | 0.11% | unattested |
| DP3 | - clause `IX.4` in `willows-grove` code: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:869 | 0.09% | unattested |
| DP4 | - clause `IX.4` in `willows-grove` tests: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:870 | 0.09% | unattested |
| DP5 | - clause `IX.4` in `willows-grove` docs: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:871 | 0.09% | unattested |
| DP6 | - clause `IX.4` in `willow-mcp` code: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:872 | 0.08% | unattested |
| DP7 | - clause `IX.4` in `willow-mcp` tests: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:873 | 0.09% | unattested |
| DP8 | - clause `IX.4` in `willow-mcp` docs: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:874 | 0.08% | unattested |
| DP9 | - clause `IX.4` in `willow-bot` code: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:875 | 0.08% | unattested |
| DP10 | - clause `IX.4` in `willow-bot` tests: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:876 | 0.09% | unattested |
| DP11 | - clause `IX.4` in `willow-bot` docs: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:877 | 0.08% | unattested |
| DQ1 | - clause `Article X` is line 424 of the constitution: Supremacy and Severability. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:881 | 0.13% | unattested |
| DQ2 | - clause `Article X` verdict, from the human-kept declarations: undeclared. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:882 | 0.12% | unattested |
| DQ3 | - clause `Article X` in `willows-grove` code: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:883 | 0.10% | unattested |
| DQ4 | - clause `Article X` in `willows-grove` tests: 1 file cites it: `tests/test_const_coverage.py`. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:884 | 0.15% | unattested |
| DQ5 | - clause `Article X` in `willows-grove` docs: 4 files cite it: `CHANGELOG.md`, `docs/design/one-script/constitution-proposal/CONSTITUTION.neutral.proposed.md`, `docs/design/one-script/constitution-proposal/CONSTITUTION.proposed.md`, `docs/design/willow-grove-premise.md`. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:885 | 0.42% | unattested |
| DQ6 | - clause `Article X` in `willow-mcp` code: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:886 | 0.09% | unattested |
| DQ7 | - clause `Article X` in `willow-mcp` tests: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:887 | 0.09% | unattested |
| DQ8 | - clause `Article X` in `willow-mcp` docs: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:888 | 0.09% | unattested |
| DQ9 | - clause `Article X` in `willow-bot` code: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:889 | 0.09% | unattested |
| DQ10 | - clause `Article X` in `willow-bot` tests: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:890 | 0.09% | unattested |
| DQ11 | - clause `Article X` in `willow-bot` docs: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:891 | 0.09% | unattested |
| DR1 | - clause `X.1` is line 426 of the constitution: Supremacy. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:895 | 0.09% | unattested |
| DR2 | - clause `X.1` verdict, from the human-kept declarations: undeclared. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:896 | 0.11% | unattested |
| DR3 | - clause `X.1` in `willows-grove` code: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:897 | 0.09% | unattested |
| DR4 | - clause `X.1` in `willows-grove` tests: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:898 | 0.09% | unattested |
| DR5 | - clause `X.1` in `willows-grove` docs: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:899 | 0.09% | unattested |
| DR6 | - clause `X.1` in `willow-mcp` code: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:900 | 0.08% | unattested |
| DR7 | - clause `X.1` in `willow-mcp` tests: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:901 | 0.08% | unattested |
| DR8 | - clause `X.1` in `willow-mcp` docs: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:902 | 0.08% | unattested |
| DR9 | - clause `X.1` in `willow-bot` code: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:903 | 0.08% | unattested |
| DR10 | - clause `X.1` in `willow-bot` tests: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:904 | 0.08% | unattested |
| DR11 | - clause `X.1` in `willow-bot` docs: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:905 | 0.08% | unattested |
| DS1 | - clause `X.2` is line 428 of the constitution: Severability. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:909 | 0.10% | unattested |
| DS2 | - clause `X.2` verdict, from the human-kept declarations: undeclared. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:910 | 0.11% | unattested |
| DS3 | - clause `X.2` in `willows-grove` code: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:911 | 0.09% | unattested |
| DS4 | - clause `X.2` in `willows-grove` tests: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:912 | 0.09% | unattested |
| DS5 | - clause `X.2` in `willows-grove` docs: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:913 | 0.09% | unattested |
| DS6 | - clause `X.2` in `willow-mcp` code: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:914 | 0.08% | unattested |
| DS7 | - clause `X.2` in `willow-mcp` tests: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:915 | 0.08% | unattested |
| DS8 | - clause `X.2` in `willow-mcp` docs: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:916 | 0.08% | unattested |
| DS9 | - clause `X.2` in `willow-bot` code: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:917 | 0.08% | unattested |
| DS10 | - clause `X.2` in `willow-bot` tests: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:918 | 0.08% | unattested |
| DS11 | - clause `X.2` in `willow-bot` docs: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:919 | 0.08% | unattested |
| DT1 | - clause `X.3` is line 430 of the constitution: Duty to Disobey (formalized). | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:923 | 0.12% | unattested |
| DT2 | - clause `X.3` verdict, from the human-kept declarations: undeclared. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:924 | 0.11% | unattested |
| DT3 | - clause `X.3` in `willows-grove` code: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:925 | 0.09% | unattested |
| DT4 | - clause `X.3` in `willows-grove` tests: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:926 | 0.09% | unattested |
| DT5 | - clause `X.3` in `willows-grove` docs: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:927 | 0.09% | unattested |
| DT6 | - clause `X.3` in `willow-mcp` code: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:928 | 0.08% | unattested |
| DT7 | - clause `X.3` in `willow-mcp` tests: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:929 | 0.08% | unattested |
| DT8 | - clause `X.3` in `willow-mcp` docs: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:930 | 0.08% | unattested |
| DT9 | - clause `X.3` in `willow-bot` code: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:931 | 0.08% | unattested |
| DT10 | - clause `X.3` in `willow-bot` tests: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:932 | 0.08% | unattested |
| DT11 | - clause `X.3` in `willow-bot` docs: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:933 | 0.08% | unattested |
| DU1 | - clause `X.4` is line 432 of the constitution: The Concurrence Rule. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:937 | 0.11% | unattested |
| DU2 | - clause `X.4` verdict, from the human-kept declarations: differently. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:938 | 0.11% | unattested |
| DU3 | - clause `X.4` in `willows-grove` code: 1 file cites it: `governance/compliance/coverage-declarations.json`. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:939 | 0.17% | unattested |
| DU4 | - clause `X.4` in `willows-grove` tests: 1 file cites it: `tests/test_const_coverage.py`. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:940 | 0.14% | unattested |
| DU5 | - clause `X.4` in `willows-grove` docs: 3 files cite it: `CHANGELOG.md`, `docs/design/forge-convergence.md`, `docs/design/one-script/constitution-proposal/amendments-2026-10-06-seat.md`. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:941 | 0.29% | unattested |
| DU6 | - clause `X.4` in `willow-mcp` code: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:942 | 0.08% | unattested |
| DU7 | - clause `X.4` in `willow-mcp` tests: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:943 | 0.08% | unattested |
| DU8 | - clause `X.4` in `willow-mcp` docs: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:944 | 0.08% | unattested |
| DU9 | - clause `X.4` in `willow-bot` code: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:945 | 0.08% | unattested |
| DU10 | - clause `X.4` in `willow-bot` tests: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:946 | 0.08% | unattested |
| DU11 | - clause `X.4` in `willow-bot` docs: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:947 | 0.08% | unattested |
| DV1 | - clause `X.4a` is line 434 of the constitution: Closed, and loud. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:951 | 0.10% | unattested |
| DV2 | - clause `X.4a` verdict, from the human-kept declarations: undeclared. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:952 | 0.11% | unattested |
| DV3 | - clause `X.4a` in `willows-grove` code: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:953 | 0.09% | unattested |
| DV4 | - clause `X.4a` in `willows-grove` tests: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:954 | 0.09% | unattested |
| DV5 | - clause `X.4a` in `willows-grove` docs: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:955 | 0.09% | unattested |
| DV6 | - clause `X.4a` in `willow-mcp` code: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:956 | 0.08% | unattested |
| DV7 | - clause `X.4a` in `willow-mcp` tests: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:957 | 0.09% | unattested |
| DV8 | - clause `X.4a` in `willow-mcp` docs: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:958 | 0.08% | unattested |
| DV9 | - clause `X.4a` in `willow-bot` code: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:959 | 0.08% | unattested |
| DV10 | - clause `X.4a` in `willow-bot` tests: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:960 | 0.09% | unattested |
| DV11 | - clause `X.4a` in `willow-bot` docs: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:961 | 0.08% | unattested |
| DW1 | - clause `Article XI` is line 450 of the constitution: Constitutional Review. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:965 | 0.12% | unattested |
| DW2 | - clause `Article XI` verdict, from the human-kept declarations: undeclared. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:966 | 0.12% | unattested |
| DW3 | - clause `Article XI` in `willows-grove` code: 1 file cites it: `docs/design/one-script/onescript/reverse.py`. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:967 | 0.17% | unattested |
| DW4 | - clause `Article XI` in `willows-grove` tests: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:968 | 0.10% | unattested |
| DW5 | - clause `Article XI` in `willows-grove` docs: 6 files cite it: `docs/design/one-box/rules-cross-table-2026-10-06.md`, `docs/design/one-script/constitution-proposal/CONSTITUTION.neutral.proposed.md`, `docs/design/one-script/constitution-proposal/CONSTITUTION.proposed.md`, `docs/design/one-script/incoming/haiku-2026-10-02/PROPOSALS-SUMMARY.md`, `docs/design/one-script/next-pile.md`, `governance/CASEBOOK.md`. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:969 | 0.64% | unattested |
| DW6 | - clause `Article XI` in `willow-mcp` code: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:970 | 0.09% | unattested |
| DW7 | - clause `Article XI` in `willow-mcp` tests: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:971 | 0.10% | unattested |
| DW8 | - clause `Article XI` in `willow-mcp` docs: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:972 | 0.09% | unattested |
| DW9 | - clause `Article XI` in `willow-bot` code: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:973 | 0.09% | unattested |
| DW10 | - clause `Article XI` in `willow-bot` tests: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:974 | 0.10% | unattested |
| DW11 | - clause `Article XI` in `willow-bot` docs: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:975 | 0.09% | unattested |
| DX1 | - clause `XI.1` is line 454 of the constitution: Who may invoke, and what it suspends. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:979 | 0.13% | unattested |
| DX2 | - clause `XI.1` verdict, from the human-kept declarations: undeclared. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:980 | 0.11% | unattested |
| DX3 | - clause `XI.1` in `willows-grove` code: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:981 | 0.09% | unattested |
| DX4 | - clause `XI.1` in `willows-grove` tests: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:982 | 0.09% | unattested |
| DX5 | - clause `XI.1` in `willows-grove` docs: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:983 | 0.09% | unattested |
| DX6 | - clause `XI.1` in `willow-mcp` code: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:984 | 0.08% | unattested |
| DX7 | - clause `XI.1` in `willow-mcp` tests: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:985 | 0.09% | unattested |
| DX8 | - clause `XI.1` in `willow-mcp` docs: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:986 | 0.08% | unattested |
| DX9 | - clause `XI.1` in `willow-bot` code: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:987 | 0.08% | unattested |
| DX10 | - clause `XI.1` in `willow-bot` tests: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:988 | 0.09% | unattested |
| DX11 | - clause `XI.1` in `willow-bot` docs: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:989 | 0.08% | unattested |
| DY1 | - clause `XI.2` is line 456 of the constitution: Resolution is recorded and binding. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:993 | 0.13% | unattested |
| DY2 | - clause `XI.2` verdict, from the human-kept declarations: undeclared. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:994 | 0.11% | unattested |
| DY3 | - clause `XI.2` in `willows-grove` code: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:995 | 0.09% | unattested |
| DY4 | - clause `XI.2` in `willows-grove` tests: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:996 | 0.09% | unattested |
| DY5 | - clause `XI.2` in `willows-grove` docs: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:997 | 0.09% | unattested |
| DY6 | - clause `XI.2` in `willow-mcp` code: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:998 | 0.08% | unattested |
| DY7 | - clause `XI.2` in `willow-mcp` tests: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:999 | 0.09% | unattested |
| DY8 | - clause `XI.2` in `willow-mcp` docs: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:1000 | 0.08% | unattested |
| DY9 | - clause `XI.2` in `willow-bot` code: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:1001 | 0.08% | unattested |
| DY10 | - clause `XI.2` in `willow-bot` tests: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:1002 | 0.09% | unattested |
| DY11 | - clause `XI.2` in `willow-bot` docs: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:1003 | 0.08% | unattested |
| DZ1 | - clause `XI.3` is line 458 of the constitution: Enforcement artifact. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:1007 | 0.11% | unattested |
| DZ2 | - clause `XI.3` verdict, from the human-kept declarations: undeclared. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:1008 | 0.11% | unattested |
| DZ3 | - clause `XI.3` in `willows-grove` code: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:1009 | 0.09% | unattested |
| DZ4 | - clause `XI.3` in `willows-grove` tests: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:1010 | 0.09% | unattested |
| DZ5 | - clause `XI.3` in `willows-grove` docs: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:1011 | 0.09% | unattested |
| DZ6 | - clause `XI.3` in `willow-mcp` code: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:1012 | 0.08% | unattested |
| DZ7 | - clause `XI.3` in `willow-mcp` tests: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:1013 | 0.09% | unattested |
| DZ8 | - clause `XI.3` in `willow-mcp` docs: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:1014 | 0.08% | unattested |
| DZ9 | - clause `XI.3` in `willow-bot` code: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:1015 | 0.08% | unattested |
| DZ10 | - clause `XI.3` in `willow-bot` tests: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:1016 | 0.09% | unattested |
| DZ11 | - clause `XI.3` in `willow-bot` docs: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:1017 | 0.08% | unattested |
| EA1 | - clause `Article XII` is line 471 of the constitution: Resource Governance. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:1021 | 0.12% | unattested |
| EA2 | - clause `Article XII` verdict, from the human-kept declarations: undeclared. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:1022 | 0.12% | unattested |
| EA3 | - clause `Article XII` in `willows-grove` code: 1 file cites it: `docs/design/one-script/onescript/resolve.py`. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:1023 | 0.17% | unattested |
| EA4 | - clause `Article XII` in `willows-grove` tests: 1 file cites it: `docs/design/one-script/onescript/tests/test_onescript.py`. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:1024 | 0.20% | unattested |
| EA5 | - clause `Article XII` in `willows-grove` docs: 4 files cite it: `docs/design/one-script/constitution-proposal/CONSTITUTION.neutral.proposed.md`, `docs/design/one-script/constitution-proposal/CONSTITUTION.proposed.md`, `docs/design/one-script/incoming/haiku-2026-10-02/PROPOSALS-SUMMARY.md`, `docs/design/one-script/incoming/haiku-2026-10-02/proposal-overnight-and-morning-screen.md`. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:1025 | 0.60% | unattested |
| EA6 | - clause `Article XII` in `willow-mcp` code: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:1026 | 0.10% | unattested |
| EA7 | - clause `Article XII` in `willow-mcp` tests: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:1027 | 0.10% | unattested |
| EA8 | - clause `Article XII` in `willow-mcp` docs: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:1028 | 0.10% | unattested |
| EA9 | - clause `Article XII` in `willow-bot` code: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:1029 | 0.10% | unattested |
| EA10 | - clause `Article XII` in `willow-bot` tests: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:1030 | 0.10% | unattested |
| EA11 | - clause `Article XII` in `willow-bot` docs: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:1031 | 0.10% | unattested |
| EB1 | - clause `XII.1` is line 475 of the constitution: Allocation is assigned, not seized. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:1035 | 0.13% | unattested |
| EB2 | - clause `XII.1` verdict, from the human-kept declarations: undeclared. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:1036 | 0.11% | unattested |
| EB3 | - clause `XII.1` in `willows-grove` code: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:1037 | 0.09% | unattested |
| EB4 | - clause `XII.1` in `willows-grove` tests: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:1038 | 0.09% | unattested |
| EB5 | - clause `XII.1` in `willows-grove` docs: 1 file cites it: `docs/design/one-script/incoming/haiku-2026-10-02/PROPOSALS-SUMMARY.md`. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:1039 | 0.20% | unattested |
| EB6 | - clause `XII.1` in `willow-mcp` code: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:1040 | 0.09% | unattested |
| EB7 | - clause `XII.1` in `willow-mcp` tests: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:1041 | 0.09% | unattested |
| EB8 | - clause `XII.1` in `willow-mcp` docs: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:1042 | 0.09% | unattested |
| EB9 | - clause `XII.1` in `willow-bot` code: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:1043 | 0.09% | unattested |
| EB10 | - clause `XII.1` in `willow-bot` tests: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:1044 | 0.09% | unattested |
| EB11 | - clause `XII.1` in `willow-bot` docs: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:1045 | 0.09% | unattested |
| EC1 | - clause `XII.2` is line 477 of the constitution: No agent expands its own allocation. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:1049 | 0.13% | unattested |
| EC2 | - clause `XII.2` verdict, from the human-kept declarations: undeclared. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:1050 | 0.11% | unattested |
| EC3 | - clause `XII.2` in `willows-grove` code: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:1051 | 0.09% | unattested |
| EC4 | - clause `XII.2` in `willows-grove` tests: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:1052 | 0.09% | unattested |
| EC5 | - clause `XII.2` in `willows-grove` docs: 1 file cites it: `docs/design/one-script/incoming/haiku-2026-10-02/PROPOSALS-SUMMARY.md`. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:1053 | 0.20% | unattested |
| EC6 | - clause `XII.2` in `willow-mcp` code: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:1054 | 0.09% | unattested |
| EC7 | - clause `XII.2` in `willow-mcp` tests: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:1055 | 0.09% | unattested |
| EC8 | - clause `XII.2` in `willow-mcp` docs: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:1056 | 0.09% | unattested |
| EC9 | - clause `XII.2` in `willow-bot` code: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:1057 | 0.09% | unattested |
| EC10 | - clause `XII.2` in `willow-bot` tests: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:1058 | 0.09% | unattested |
| EC11 | - clause `XII.2` in `willow-bot` docs: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:1059 | 0.09% | unattested |
| ED1 | - clause `XII.3` is line 479 of the constitution: Contention is arbitrated under witness. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:1063 | 0.14% | unattested |
| ED2 | - clause `XII.3` verdict, from the human-kept declarations: undeclared. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:1064 | 0.11% | unattested |
| ED3 | - clause `XII.3` in `willows-grove` code: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:1065 | 0.09% | unattested |
| ED4 | - clause `XII.3` in `willows-grove` tests: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:1066 | 0.09% | unattested |
| ED5 | - clause `XII.3` in `willows-grove` docs: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:1067 | 0.09% | unattested |
| ED6 | - clause `XII.3` in `willow-mcp` code: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:1068 | 0.09% | unattested |
| ED7 | - clause `XII.3` in `willow-mcp` tests: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:1069 | 0.09% | unattested |
| ED8 | - clause `XII.3` in `willow-mcp` docs: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:1070 | 0.09% | unattested |
| ED9 | - clause `XII.3` in `willow-bot` code: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:1071 | 0.09% | unattested |
| ED10 | - clause `XII.3` in `willow-bot` tests: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:1072 | 0.09% | unattested |
| ED11 | - clause `XII.3` in `willow-bot` docs: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:1073 | 0.09% | unattested |
| EE1 | - clause `XII.4` is line 481 of the constitution: Background work yields to the present human. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:1077 | 0.15% | unattested |
| EE2 | - clause `XII.4` verdict, from the human-kept declarations: undeclared. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:1078 | 0.11% | unattested |
| EE3 | - clause `XII.4` in `willows-grove` code: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:1079 | 0.09% | unattested |
| EE4 | - clause `XII.4` in `willows-grove` tests: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:1080 | 0.09% | unattested |
| EE5 | - clause `XII.4` in `willows-grove` docs: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:1081 | 0.09% | unattested |
| EE6 | - clause `XII.4` in `willow-mcp` code: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:1082 | 0.09% | unattested |
| EE7 | - clause `XII.4` in `willow-mcp` tests: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:1083 | 0.09% | unattested |
| EE8 | - clause `XII.4` in `willow-mcp` docs: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:1084 | 0.09% | unattested |
| EE9 | - clause `XII.4` in `willow-bot` code: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:1085 | 0.09% | unattested |
| EE10 | - clause `XII.4` in `willow-bot` tests: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:1086 | 0.09% | unattested |
| EE11 | - clause `XII.4` in `willow-bot` docs: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:1087 | 0.09% | unattested |
| EF1 | - clause `Article XIII` is line 493 of the constitution: Federation. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:1091 | 0.11% | unattested |
| EF2 | - clause `Article XIII` verdict, from the human-kept declarations: undeclared. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:1092 | 0.12% | unattested |
| EF3 | - clause `Article XIII` in `willows-grove` code: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:1093 | 0.10% | unattested |
| EF4 | - clause `Article XIII` in `willows-grove` tests: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:1094 | 0.10% | unattested |
| EF5 | - clause `Article XIII` in `willows-grove` docs: 3 files cite it: `docs/design/one-box/research-2026-10-06.md`, `docs/design/one-script/constitution-proposal/CONSTITUTION.neutral.proposed.md`, `docs/design/one-script/constitution-proposal/CONSTITUTION.proposed.md`. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:1095 | 0.41% | unattested |
| EF6 | - clause `Article XIII` in `willow-mcp` code: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:1096 | 0.10% | unattested |
| EF7 | - clause `Article XIII` in `willow-mcp` tests: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:1097 | 0.10% | unattested |
| EF8 | - clause `Article XIII` in `willow-mcp` docs: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:1098 | 0.10% | unattested |
| EF9 | - clause `Article XIII` in `willow-bot` code: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:1099 | 0.10% | unattested |
| EF10 | - clause `Article XIII` in `willow-bot` tests: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:1100 | 0.10% | unattested |
| EF11 | - clause `Article XIII` in `willow-bot` docs: 0 files cite it. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:1101 | 0.10% | unattested |
| EG1 | - clause `unknown` is every cited ID the report finds that names no clause. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:1105 | 0.12% | unattested |
| EG2 | - clause `unknown` id `0.3.II` (written with the CONST prefix where cited): 4 files cite it: `willows-grove:CHANGELOG.md`, `willows-grove:governance/CASEBOOK.md`, `willows-grove:governance/compliance/cases/const_0_3_capability.py`, `willows-grove:tests/test_const_coverage.py`. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:1106 | 0.43% | unattested |
| EG3 | - clause `unknown` id `X.N` (written with the CONST prefix where cited): 2 files cite it: `willows-grove:CHANGELOG.md`, `willows-grove:governance/compliance/coverage-declarations.json`. | `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md`:1108 | 0.29% | unattested |
| EG4 | *source silent: no more unknown ids* | — | 0.00% | unattested |
| EG5 | *source silent: no more unknown ids* | — | 0.00% | unattested |
| EG6 | *source silent: no more unknown ids* | — | 0.00% | unattested |
| EG7 | *source silent: no more unknown ids* | — | 0.00% | unattested |
| EG8 | *source silent: no more unknown ids* | — | 0.00% | unattested |
| EG9 | *source silent: no more unknown ids* | — | 0.00% | unattested |
| EG10 | *source silent: no more unknown ids* | — | 0.00% | unattested |
| EG11 | *source silent: no more unknown ids* | — | 0.00% | unattested |
<!-- /cross-table:index -->

## Measure

*Written by `cross_table.py fill --measure`, the same as the other grids.*

<!-- cross-table:measure -->
- **Cells:** 869, of which 861 found (99.1%).
- **Text:** 64060 characters. An even share would be 0.12% per cell.
- **Trim:** 10 cell(s) cut at 420 characters; the index keeps 97.3% of the source text.

| Row | What it holds | Found | Characters | Share | Largest cell |
|---|---|---|---|---|---|
| BG | Article 0 | 11/11 | 1215 | 1.90% | BG5 0.82% |
| BH | 0.1 | 11/11 | 1164 | 1.82% | BH5 0.85% |
| BI | 0.2 | 11/11 | 1683 | 2.63% | BI5 1.11% |
| BJ | 0.3 | 11/11 | 1526 | 2.38% | BJ5 0.89% |
| BK | 0.4 | 11/11 | 1169 | 1.82% | BK5 0.75% |
| BL | 0.5 | 11/11 | 1342 | 2.09% | BL5 0.97% |
| BM | 0.6 | 11/11 | 1302 | 2.03% | BM5 0.92% |
| BN | Article I | 11/11 | 1506 | 2.35% | BN5 1.10% |
| BO | I.1 | 11/11 | 1032 | 1.61% | BO5 0.59% |
| BP | I.2 | 11/11 | 641 | 1.00% | BP1 0.13% |
| BQ | I.3 | 11/11 | 669 | 1.04% | BQ1 0.13% |
| BR | I.4 | 11/11 | 649 | 1.01% | BR1 0.14% |
| BS | I.5 | 11/11 | 646 | 1.01% | BS1 0.14% |
| BT | Article II | 11/11 | 965 | 1.51% | BT5 0.34% |
| BU | II.1 | 11/11 | 659 | 1.03% | BU1 0.14% |
| BV | II.2 | 11/11 | 663 | 1.03% | BV1 0.15% |
| BW | II.3 | 11/11 | 642 | 1.00% | BW1 0.12% |
| BX | Article III | 11/11 | 1418 | 2.21% | BX5 0.63% |
| BY | III.1 | 11/11 | 641 | 1.00% | BY2 0.11% |
| BZ | III.2 | 11/11 | 947 | 1.48% | BZ6 0.41% |
| CA | III.3 | 11/11 | 648 | 1.01% | CA2 0.11% |
| CB | III.4 | 11/11 | 645 | 1.01% | CB2 0.11% |
| CC | III.5 | 11/11 | 653 | 1.02% | CC1 0.12% |
| CD | Article IV | 11/11 | 1527 | 2.38% | CD5 0.88% |
| CE | IV.1 | 11/11 | 686 | 1.07% | CE1 0.14% |
| CF | IV.2 | 11/11 | 686 | 1.07% | CF1 0.14% |
| CG | IV.3 | 11/11 | 715 | 1.12% | CG5 0.20% |
| CH | IV.5 | 11/11 | 687 | 1.07% | CH1 0.15% |
| CI | IV.6 | 11/11 | 687 | 1.07% | CI1 0.15% |
| CJ | IV.4 | 11/11 | 688 | 1.07% | CJ1 0.15% |
| CK | IV.7 | 11/11 | 667 | 1.04% | CK1 0.15% |
| CL | IV.8 | 11/11 | 645 | 1.01% | CL1 0.12% |
| CM | Article V | 11/11 | 1141 | 1.78% | CM5 0.51% |
| CN | V.1 | 11/11 | 625 | 0.98% | CN2 0.11% |
| CO | V.2 | 11/11 | 642 | 1.00% | CO1 0.13% |
| CP | V.3 | 11/11 | 636 | 0.99% | CP1 0.12% |
| CQ | V.4 | 11/11 | 626 | 0.98% | CQ2 0.11% |
| CR | V.4a | 11/11 | 702 | 1.10% | CR1 0.16% |
| CS | V.4b | 11/11 | 622 | 0.97% | CS2 0.11% |
| CT | V.5 | 11/11 | 626 | 0.98% | CT2 0.11% |
| CU | V.6 | 11/11 | 623 | 0.97% | CU2 0.11% |
| CV | V.7 | 11/11 | 637 | 0.99% | CV1 0.12% |
| CW | V.8 | 11/11 | 624 | 0.97% | CW2 0.11% |
| CX | V.9 | 11/11 | 637 | 0.99% | CX1 0.12% |
| CY | Article VI | 11/11 | 1655 | 2.58% | CY5 0.98% |
| CZ | VI.1 | 11/11 | 704 | 1.10% | CZ4 0.14% |
| DA | VI.2 | 11/11 | 639 | 1.00% | DA1 0.11% |
| DB | VI.3 | 11/11 | 641 | 1.00% | DB1 0.11% |
| DC | VI.4 | 11/11 | 672 | 1.05% | DC5 0.13% |
| DD | VI.5 | 11/11 | 752 | 1.17% | DD5 0.20% |
| DE | VI.6 | 11/11 | 630 | 0.98% | DE2 0.11% |
| DF | Article VII | 11/11 | 961 | 1.50% | DF5 0.44% |
| DG | VII.default | 11/11 | 752 | 1.17% | DG4 0.15% |
| DH | Article VIII | 11/11 | 869 | 1.36% | DH5 0.34% |
| DI | VIII.1 | 11/11 | 735 | 1.15% | DI5 0.21% |
| DJ | VIII.2 | 11/11 | 681 | 1.06% | DJ1 0.15% |
| DK | VIII.3 | 11/11 | 665 | 1.04% | DK1 0.12% |
| DL | Article IX | 11/11 | 861 | 1.34% | DL5 0.34% |
| DM | IX.1 | 11/11 | 633 | 0.99% | DM2 0.11% |
| DN | IX.2 | 11/11 | 638 | 1.00% | DN1 0.11% |
| DO | IX.3 | 11/11 | 638 | 1.00% | DO1 0.11% |
| DP | IX.4 | 11/11 | 645 | 1.01% | DP1 0.12% |
| DQ | Article X | 11/11 | 940 | 1.47% | DQ5 0.42% |
| DR | X.1 | 11/11 | 616 | 0.96% | DR2 0.11% |
| DS | X.2 | 11/11 | 619 | 0.97% | DS2 0.11% |
| DT | X.3 | 11/11 | 635 | 0.99% | DT1 0.12% |
| DU | X.4 | 11/11 | 842 | 1.31% | DU5 0.29% |
| DV | X.4a | 11/11 | 634 | 0.99% | DV2 0.11% |
| DW | Article XI | 11/11 | 1099 | 1.72% | DW5 0.64% |
| DX | XI.1 | 11/11 | 654 | 1.02% | DX1 0.13% |
| DY | XI.2 | 11/11 | 652 | 1.02% | DY1 0.13% |
| DZ | XI.3 | 11/11 | 638 | 1.00% | DZ1 0.11% |
| EA | Article XII | 11/11 | 1141 | 1.78% | EA5 0.60% |
| EB | XII.1 | 11/11 | 736 | 1.15% | EB5 0.20% |
| EC | XII.2 | 11/11 | 737 | 1.15% | EC5 0.20% |
| ED | XII.3 | 11/11 | 667 | 1.04% | ED1 0.14% |
| EE | XII.4 | 11/11 | 672 | 1.05% | EE1 0.15% |
| EF | Article XIII | 11/11 | 916 | 1.43% | EF5 0.41% |
| EG | unknown | 3/11 | 537 | 0.84% | EG2 0.43% |

- **Largest:** BI5 1.11%, BN5 1.10%, CY5 0.98%, BL5 0.97%, BM5 0.92%.
- **Smallest:** DU9 0.08%, DU8 0.08%, DU6 0.08%, DU11 0.08%, DT9 0.08%.
- **Holding nothing:** EG4, EG5, EG6, EG7, EG8, EG9, EG10, EG11.

**Evenness.** Gini 0.24 (0 means every box holds the same, 1 means one box holds everything).
- **Fat** (at least 3× an even share; often several rules in one box, a candidate to split): BG5, BH5, BI3, BI5, BJ3, BJ5, BK5, BL5, BM5, BN5, BO5, BX3, BX4, BX5, BZ6, CD3, CD5, CM5, CY4, CY5, DF5, DQ5, DW5, EA5, EF5, EG2.
- **Thin** (at most 0.25× an even share; a label with a line behind it): none.

**Sources.** How much of each source file the grid draws on (distinct passages over the file's characters, whitespace collapsed, not counting any tables this script generated in it).

| File | Cells | Drawn | File | Coverage |
|---|---|---|---|---|
| `willows-grove/docs/design/coverage/coverage-ledger-2026-10-06.md` | 861 | 64060 | 66444 | 96.4% |

**Across grids.** Each grid's part of all the text.

| Grid | Cells | Characters | Share of all |
|---|---|---|---|
| Coverage: every clause of Draft 0.9 against the three repos (2026-10-06) | 869 | 64060 | 25.5% |
| Rules cross table: boxes and branches (2026-10-06) | 169 | 27250 | 10.9% |
| Boxes, from outside the system (2026-10-06) | 20 | 3434 | 1.4% |
| The fat, dripped (2026-10-06) | 90 | 4063 | 1.6% |
| Gerald session atoms (2026-10-06) | 156 | 53779 | 21.4% |
| Open branches (2026-10-06) | 48 | 6475 | 2.6% |
| Handoffs against Draft 0.9 (2026-10-06) | 210 | 13919 | 5.5% |
| Coverage by branch: the third axis (2026-10-06) | 468 | 78022 | 31.1% |
<!-- /cross-table:measure -->

---

ΔΣ=42
