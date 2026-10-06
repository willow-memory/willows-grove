# Coverage by branch: the third axis (2026-10-06)

*Desk session, 2026-10-06. After the coverage grid, the operator: "And we
could probably easily expand this into a third", then "Fix first, then
build". The fix taught the coverage report every spelling of a citation; this
is the build. Agent-reported; not ratified.*

## How it's built

- **One instrument, six layers.** This branch's coverage script, with the
  fix, was run at every branch head against **that branch's own**
  constitution and declarations, over its tree plus willow-mcp and willow-bot.
  The same instrument means differences between layers are differences in
  the branches, not in the measuring.
- **The source** is [`coverage-layers-ledger-2026-10-06.md`](coverage-layers-ledger-2026-10-06.md):
  one line per clause per branch, giving the files citing it, the spellings
  they use, the verdict, and the clause's title on that branch's law. Clauses
  are matched by ID, and the title is carried so an ID that meant something
  else on another law would show it. None does. The ledger is written without
  Trace IDs or section signs, so it cites nothing. A second run gave the same
  bytes.
- **Rows EH–HG,** one per clause of Draft 0.9, after the coverage grid's EG.
  **Columns 1–6** are the branches, in the ledger's order. All 468 boxes were
  checked to be exactly their own line.

## What the third axis shows

- **Two laws.** Five branches carry Draft 0.9. The 10-04 branch carries
  **Draft 0.8** (65 clauses). On its layer, **13 clauses are absent, not
  uncited:** I.5, III.5, IV.7, IV.8, V.4b, V.6–V.9, VI.5, VI.6, X.4a and
  XII.4. These are the October amendments that 0.9 brought in. Its other
  differences are fewer citing files, because it is 38 commits behind.
- **The fix shows up where it should.** Before it, the ccr branches'
  rewritten `CLAUDE.md` added nothing. Now both ccr branches cite **9
  articles by heading anchor** (Article 0, I, III–VII, X, XII), and those
  rows gain a file on each.
- **This branch's own citations.** This branch adds files to the six eternity
  clauses (four to six more each) and to Articles I and III. They are this
  session's documents that cite the clauses: the amendment proposals, the
  rules grid that copies passages containing them, and the coverage test.
  Copying a citation counts as citing. The report reads text, not intent.
- **No layer changes the law's gaps.** Every Draft 0.9 layer has the same 38
  cited rows and the same 40 clauses cited nowhere, and one verdict declared.
  Branches move which files cite a clause, not which clauses are covered.

## The grid

<!-- cross-table:grid -->
| | 1 | 2 | 3 | 4 | 5 | 6 |
|---|---|---|---|---|---|---|
| **EH** Article 0 | master | ccr-392b8b73-v809qu | ccr-542b5884-0deee5 | ccr-8a588c96-jf76ei | claude/agent-instruction-files | claude/ai-model-smoothing-gentrification-alc5dm |
| **EI** 0.1 | master | ccr-392b8b73-v809qu | ccr-542b5884-0deee5 | ccr-8a588c96-jf76ei | claude/agent-instruction-files | claude/ai-model-smoothing-gentrification-alc5dm |
| **EJ** 0.2 | master | ccr-392b8b73-v809qu | ccr-542b5884-0deee5 | ccr-8a588c96-jf76ei | claude/agent-instruction-files | claude/ai-model-smoothing-gentrification-alc5dm |
| **EK** 0.3 | master | ccr-392b8b73-v809qu | ccr-542b5884-0deee5 | ccr-8a588c96-jf76ei | claude/agent-instruction-files | claude/ai-model-smoothing-gentrification-alc5dm |
| **EL** 0.4 | master | ccr-392b8b73-v809qu | ccr-542b5884-0deee5 | ccr-8a588c96-jf76ei | claude/agent-instruction-files | claude/ai-model-smoothing-gentrification-alc5dm |
| **EM** 0.5 | master | ccr-392b8b73-v809qu | ccr-542b5884-0deee5 | ccr-8a588c96-jf76ei | claude/agent-instruction-files | claude/ai-model-smoothing-gentrification-alc5dm |
| **EN** 0.6 | master | ccr-392b8b73-v809qu | ccr-542b5884-0deee5 | ccr-8a588c96-jf76ei | claude/agent-instruction-files | claude/ai-model-smoothing-gentrification-alc5dm |
| **EO** Article I | master | ccr-392b8b73-v809qu | ccr-542b5884-0deee5 | ccr-8a588c96-jf76ei | claude/agent-instruction-files | claude/ai-model-smoothing-gentrification-alc5dm |
| **EP** I.1 | master | ccr-392b8b73-v809qu | ccr-542b5884-0deee5 | ccr-8a588c96-jf76ei | claude/agent-instruction-files | claude/ai-model-smoothing-gentrification-alc5dm |
| **EQ** I.2 | master | ccr-392b8b73-v809qu | ccr-542b5884-0deee5 | ccr-8a588c96-jf76ei | claude/agent-instruction-files | claude/ai-model-smoothing-gentrification-alc5dm |
| **ER** I.3 | master | ccr-392b8b73-v809qu | ccr-542b5884-0deee5 | ccr-8a588c96-jf76ei | claude/agent-instruction-files | claude/ai-model-smoothing-gentrification-alc5dm |
| **ES** I.4 | master | ccr-392b8b73-v809qu | ccr-542b5884-0deee5 | ccr-8a588c96-jf76ei | claude/agent-instruction-files | claude/ai-model-smoothing-gentrification-alc5dm |
| **ET** I.5 | master | ccr-392b8b73-v809qu | ccr-542b5884-0deee5 | ccr-8a588c96-jf76ei | claude/agent-instruction-files | claude/ai-model-smoothing-gentrification-alc5dm |
| **EU** Article II | master | ccr-392b8b73-v809qu | ccr-542b5884-0deee5 | ccr-8a588c96-jf76ei | claude/agent-instruction-files | claude/ai-model-smoothing-gentrification-alc5dm |
| **EV** II.1 | master | ccr-392b8b73-v809qu | ccr-542b5884-0deee5 | ccr-8a588c96-jf76ei | claude/agent-instruction-files | claude/ai-model-smoothing-gentrification-alc5dm |
| **EW** II.2 | master | ccr-392b8b73-v809qu | ccr-542b5884-0deee5 | ccr-8a588c96-jf76ei | claude/agent-instruction-files | claude/ai-model-smoothing-gentrification-alc5dm |
| **EX** II.3 | master | ccr-392b8b73-v809qu | ccr-542b5884-0deee5 | ccr-8a588c96-jf76ei | claude/agent-instruction-files | claude/ai-model-smoothing-gentrification-alc5dm |
| **EY** Article III | master | ccr-392b8b73-v809qu | ccr-542b5884-0deee5 | ccr-8a588c96-jf76ei | claude/agent-instruction-files | claude/ai-model-smoothing-gentrification-alc5dm |
| **EZ** III.1 | master | ccr-392b8b73-v809qu | ccr-542b5884-0deee5 | ccr-8a588c96-jf76ei | claude/agent-instruction-files | claude/ai-model-smoothing-gentrification-alc5dm |
| **FA** III.2 | master | ccr-392b8b73-v809qu | ccr-542b5884-0deee5 | ccr-8a588c96-jf76ei | claude/agent-instruction-files | claude/ai-model-smoothing-gentrification-alc5dm |
| **FB** III.3 | master | ccr-392b8b73-v809qu | ccr-542b5884-0deee5 | ccr-8a588c96-jf76ei | claude/agent-instruction-files | claude/ai-model-smoothing-gentrification-alc5dm |
| **FC** III.4 | master | ccr-392b8b73-v809qu | ccr-542b5884-0deee5 | ccr-8a588c96-jf76ei | claude/agent-instruction-files | claude/ai-model-smoothing-gentrification-alc5dm |
| **FD** III.5 | master | ccr-392b8b73-v809qu | ccr-542b5884-0deee5 | ccr-8a588c96-jf76ei | claude/agent-instruction-files | claude/ai-model-smoothing-gentrification-alc5dm |
| **FE** Article IV | master | ccr-392b8b73-v809qu | ccr-542b5884-0deee5 | ccr-8a588c96-jf76ei | claude/agent-instruction-files | claude/ai-model-smoothing-gentrification-alc5dm |
| **FF** IV.1 | master | ccr-392b8b73-v809qu | ccr-542b5884-0deee5 | ccr-8a588c96-jf76ei | claude/agent-instruction-files | claude/ai-model-smoothing-gentrification-alc5dm |
| **FG** IV.2 | master | ccr-392b8b73-v809qu | ccr-542b5884-0deee5 | ccr-8a588c96-jf76ei | claude/agent-instruction-files | claude/ai-model-smoothing-gentrification-alc5dm |
| **FH** IV.3 | master | ccr-392b8b73-v809qu | ccr-542b5884-0deee5 | ccr-8a588c96-jf76ei | claude/agent-instruction-files | claude/ai-model-smoothing-gentrification-alc5dm |
| **FI** IV.5 | master | ccr-392b8b73-v809qu | ccr-542b5884-0deee5 | ccr-8a588c96-jf76ei | claude/agent-instruction-files | claude/ai-model-smoothing-gentrification-alc5dm |
| **FJ** IV.6 | master | ccr-392b8b73-v809qu | ccr-542b5884-0deee5 | ccr-8a588c96-jf76ei | claude/agent-instruction-files | claude/ai-model-smoothing-gentrification-alc5dm |
| **FK** IV.4 | master | ccr-392b8b73-v809qu | ccr-542b5884-0deee5 | ccr-8a588c96-jf76ei | claude/agent-instruction-files | claude/ai-model-smoothing-gentrification-alc5dm |
| **FL** IV.7 | master | ccr-392b8b73-v809qu | ccr-542b5884-0deee5 | ccr-8a588c96-jf76ei | claude/agent-instruction-files | claude/ai-model-smoothing-gentrification-alc5dm |
| **FM** IV.8 | master | ccr-392b8b73-v809qu | ccr-542b5884-0deee5 | ccr-8a588c96-jf76ei | claude/agent-instruction-files | claude/ai-model-smoothing-gentrification-alc5dm |
| **FN** Article V | master | ccr-392b8b73-v809qu | ccr-542b5884-0deee5 | ccr-8a588c96-jf76ei | claude/agent-instruction-files | claude/ai-model-smoothing-gentrification-alc5dm |
| **FO** V.1 | master | ccr-392b8b73-v809qu | ccr-542b5884-0deee5 | ccr-8a588c96-jf76ei | claude/agent-instruction-files | claude/ai-model-smoothing-gentrification-alc5dm |
| **FP** V.2 | master | ccr-392b8b73-v809qu | ccr-542b5884-0deee5 | ccr-8a588c96-jf76ei | claude/agent-instruction-files | claude/ai-model-smoothing-gentrification-alc5dm |
| **FQ** V.3 | master | ccr-392b8b73-v809qu | ccr-542b5884-0deee5 | ccr-8a588c96-jf76ei | claude/agent-instruction-files | claude/ai-model-smoothing-gentrification-alc5dm |
| **FR** V.4 | master | ccr-392b8b73-v809qu | ccr-542b5884-0deee5 | ccr-8a588c96-jf76ei | claude/agent-instruction-files | claude/ai-model-smoothing-gentrification-alc5dm |
| **FS** V.4a | master | ccr-392b8b73-v809qu | ccr-542b5884-0deee5 | ccr-8a588c96-jf76ei | claude/agent-instruction-files | claude/ai-model-smoothing-gentrification-alc5dm |
| **FT** V.4b | master | ccr-392b8b73-v809qu | ccr-542b5884-0deee5 | ccr-8a588c96-jf76ei | claude/agent-instruction-files | claude/ai-model-smoothing-gentrification-alc5dm |
| **FU** V.5 | master | ccr-392b8b73-v809qu | ccr-542b5884-0deee5 | ccr-8a588c96-jf76ei | claude/agent-instruction-files | claude/ai-model-smoothing-gentrification-alc5dm |
| **FV** V.6 | master | ccr-392b8b73-v809qu | ccr-542b5884-0deee5 | ccr-8a588c96-jf76ei | claude/agent-instruction-files | claude/ai-model-smoothing-gentrification-alc5dm |
| **FW** V.7 | master | ccr-392b8b73-v809qu | ccr-542b5884-0deee5 | ccr-8a588c96-jf76ei | claude/agent-instruction-files | claude/ai-model-smoothing-gentrification-alc5dm |
| **FX** V.8 | master | ccr-392b8b73-v809qu | ccr-542b5884-0deee5 | ccr-8a588c96-jf76ei | claude/agent-instruction-files | claude/ai-model-smoothing-gentrification-alc5dm |
| **FY** V.9 | master | ccr-392b8b73-v809qu | ccr-542b5884-0deee5 | ccr-8a588c96-jf76ei | claude/agent-instruction-files | claude/ai-model-smoothing-gentrification-alc5dm |
| **FZ** Article VI | master | ccr-392b8b73-v809qu | ccr-542b5884-0deee5 | ccr-8a588c96-jf76ei | claude/agent-instruction-files | claude/ai-model-smoothing-gentrification-alc5dm |
| **GA** VI.1 | master | ccr-392b8b73-v809qu | ccr-542b5884-0deee5 | ccr-8a588c96-jf76ei | claude/agent-instruction-files | claude/ai-model-smoothing-gentrification-alc5dm |
| **GB** VI.2 | master | ccr-392b8b73-v809qu | ccr-542b5884-0deee5 | ccr-8a588c96-jf76ei | claude/agent-instruction-files | claude/ai-model-smoothing-gentrification-alc5dm |
| **GC** VI.3 | master | ccr-392b8b73-v809qu | ccr-542b5884-0deee5 | ccr-8a588c96-jf76ei | claude/agent-instruction-files | claude/ai-model-smoothing-gentrification-alc5dm |
| **GD** VI.4 | master | ccr-392b8b73-v809qu | ccr-542b5884-0deee5 | ccr-8a588c96-jf76ei | claude/agent-instruction-files | claude/ai-model-smoothing-gentrification-alc5dm |
| **GE** VI.5 | master | ccr-392b8b73-v809qu | ccr-542b5884-0deee5 | ccr-8a588c96-jf76ei | claude/agent-instruction-files | claude/ai-model-smoothing-gentrification-alc5dm |
| **GF** VI.6 | master | ccr-392b8b73-v809qu | ccr-542b5884-0deee5 | ccr-8a588c96-jf76ei | claude/agent-instruction-files | claude/ai-model-smoothing-gentrification-alc5dm |
| **GG** Article VII | master | ccr-392b8b73-v809qu | ccr-542b5884-0deee5 | ccr-8a588c96-jf76ei | claude/agent-instruction-files | claude/ai-model-smoothing-gentrification-alc5dm |
| **GH** VII.default | master | ccr-392b8b73-v809qu | ccr-542b5884-0deee5 | ccr-8a588c96-jf76ei | claude/agent-instruction-files | claude/ai-model-smoothing-gentrification-alc5dm |
| **GI** Article VIII | master | ccr-392b8b73-v809qu | ccr-542b5884-0deee5 | ccr-8a588c96-jf76ei | claude/agent-instruction-files | claude/ai-model-smoothing-gentrification-alc5dm |
| **GJ** VIII.1 | master | ccr-392b8b73-v809qu | ccr-542b5884-0deee5 | ccr-8a588c96-jf76ei | claude/agent-instruction-files | claude/ai-model-smoothing-gentrification-alc5dm |
| **GK** VIII.2 | master | ccr-392b8b73-v809qu | ccr-542b5884-0deee5 | ccr-8a588c96-jf76ei | claude/agent-instruction-files | claude/ai-model-smoothing-gentrification-alc5dm |
| **GL** VIII.3 | master | ccr-392b8b73-v809qu | ccr-542b5884-0deee5 | ccr-8a588c96-jf76ei | claude/agent-instruction-files | claude/ai-model-smoothing-gentrification-alc5dm |
| **GM** Article IX | master | ccr-392b8b73-v809qu | ccr-542b5884-0deee5 | ccr-8a588c96-jf76ei | claude/agent-instruction-files | claude/ai-model-smoothing-gentrification-alc5dm |
| **GN** IX.1 | master | ccr-392b8b73-v809qu | ccr-542b5884-0deee5 | ccr-8a588c96-jf76ei | claude/agent-instruction-files | claude/ai-model-smoothing-gentrification-alc5dm |
| **GO** IX.2 | master | ccr-392b8b73-v809qu | ccr-542b5884-0deee5 | ccr-8a588c96-jf76ei | claude/agent-instruction-files | claude/ai-model-smoothing-gentrification-alc5dm |
| **GP** IX.3 | master | ccr-392b8b73-v809qu | ccr-542b5884-0deee5 | ccr-8a588c96-jf76ei | claude/agent-instruction-files | claude/ai-model-smoothing-gentrification-alc5dm |
| **GQ** IX.4 | master | ccr-392b8b73-v809qu | ccr-542b5884-0deee5 | ccr-8a588c96-jf76ei | claude/agent-instruction-files | claude/ai-model-smoothing-gentrification-alc5dm |
| **GR** Article X | master | ccr-392b8b73-v809qu | ccr-542b5884-0deee5 | ccr-8a588c96-jf76ei | claude/agent-instruction-files | claude/ai-model-smoothing-gentrification-alc5dm |
| **GS** X.1 | master | ccr-392b8b73-v809qu | ccr-542b5884-0deee5 | ccr-8a588c96-jf76ei | claude/agent-instruction-files | claude/ai-model-smoothing-gentrification-alc5dm |
| **GT** X.2 | master | ccr-392b8b73-v809qu | ccr-542b5884-0deee5 | ccr-8a588c96-jf76ei | claude/agent-instruction-files | claude/ai-model-smoothing-gentrification-alc5dm |
| **GU** X.3 | master | ccr-392b8b73-v809qu | ccr-542b5884-0deee5 | ccr-8a588c96-jf76ei | claude/agent-instruction-files | claude/ai-model-smoothing-gentrification-alc5dm |
| **GV** X.4 | master | ccr-392b8b73-v809qu | ccr-542b5884-0deee5 | ccr-8a588c96-jf76ei | claude/agent-instruction-files | claude/ai-model-smoothing-gentrification-alc5dm |
| **GW** X.4a | master | ccr-392b8b73-v809qu | ccr-542b5884-0deee5 | ccr-8a588c96-jf76ei | claude/agent-instruction-files | claude/ai-model-smoothing-gentrification-alc5dm |
| **GX** Article XI | master | ccr-392b8b73-v809qu | ccr-542b5884-0deee5 | ccr-8a588c96-jf76ei | claude/agent-instruction-files | claude/ai-model-smoothing-gentrification-alc5dm |
| **GY** XI.1 | master | ccr-392b8b73-v809qu | ccr-542b5884-0deee5 | ccr-8a588c96-jf76ei | claude/agent-instruction-files | claude/ai-model-smoothing-gentrification-alc5dm |
| **GZ** XI.2 | master | ccr-392b8b73-v809qu | ccr-542b5884-0deee5 | ccr-8a588c96-jf76ei | claude/agent-instruction-files | claude/ai-model-smoothing-gentrification-alc5dm |
| **HA** XI.3 | master | ccr-392b8b73-v809qu | ccr-542b5884-0deee5 | ccr-8a588c96-jf76ei | claude/agent-instruction-files | claude/ai-model-smoothing-gentrification-alc5dm |
| **HB** Article XII | master | ccr-392b8b73-v809qu | ccr-542b5884-0deee5 | ccr-8a588c96-jf76ei | claude/agent-instruction-files | claude/ai-model-smoothing-gentrification-alc5dm |
| **HC** XII.1 | master | ccr-392b8b73-v809qu | ccr-542b5884-0deee5 | ccr-8a588c96-jf76ei | claude/agent-instruction-files | claude/ai-model-smoothing-gentrification-alc5dm |
| **HD** XII.2 | master | ccr-392b8b73-v809qu | ccr-542b5884-0deee5 | ccr-8a588c96-jf76ei | claude/agent-instruction-files | claude/ai-model-smoothing-gentrification-alc5dm |
| **HE** XII.3 | master | ccr-392b8b73-v809qu | ccr-542b5884-0deee5 | ccr-8a588c96-jf76ei | claude/agent-instruction-files | claude/ai-model-smoothing-gentrification-alc5dm |
| **HF** XII.4 | master | ccr-392b8b73-v809qu | ccr-542b5884-0deee5 | ccr-8a588c96-jf76ei | claude/agent-instruction-files | claude/ai-model-smoothing-gentrification-alc5dm |
| **HG** Article XIII | master | ccr-392b8b73-v809qu | ccr-542b5884-0deee5 | ccr-8a588c96-jf76ei | claude/agent-instruction-files | claude/ai-model-smoothing-gentrification-alc5dm |
<!-- /cross-table:grid -->

## Where each row comes from

<!-- cross-table:sources -->
| Row | What it holds | Source |
|---|---|---|
| EH | Article 0 | `coverage-layers-ledger-2026-10-06.md`, section Article 0 |
| EI | 0.1 | `coverage-layers-ledger-2026-10-06.md`, section 0.1 |
| EJ | 0.2 | `coverage-layers-ledger-2026-10-06.md`, section 0.2 |
| EK | 0.3 | `coverage-layers-ledger-2026-10-06.md`, section 0.3 |
| EL | 0.4 | `coverage-layers-ledger-2026-10-06.md`, section 0.4 |
| EM | 0.5 | `coverage-layers-ledger-2026-10-06.md`, section 0.5 |
| EN | 0.6 | `coverage-layers-ledger-2026-10-06.md`, section 0.6 |
| EO | Article I | `coverage-layers-ledger-2026-10-06.md`, section Article I |
| EP | I.1 | `coverage-layers-ledger-2026-10-06.md`, section I.1 |
| EQ | I.2 | `coverage-layers-ledger-2026-10-06.md`, section I.2 |
| ER | I.3 | `coverage-layers-ledger-2026-10-06.md`, section I.3 |
| ES | I.4 | `coverage-layers-ledger-2026-10-06.md`, section I.4 |
| ET | I.5 | `coverage-layers-ledger-2026-10-06.md`, section I.5 |
| EU | Article II | `coverage-layers-ledger-2026-10-06.md`, section Article II |
| EV | II.1 | `coverage-layers-ledger-2026-10-06.md`, section II.1 |
| EW | II.2 | `coverage-layers-ledger-2026-10-06.md`, section II.2 |
| EX | II.3 | `coverage-layers-ledger-2026-10-06.md`, section II.3 |
| EY | Article III | `coverage-layers-ledger-2026-10-06.md`, section Article III |
| EZ | III.1 | `coverage-layers-ledger-2026-10-06.md`, section III.1 |
| FA | III.2 | `coverage-layers-ledger-2026-10-06.md`, section III.2 |
| FB | III.3 | `coverage-layers-ledger-2026-10-06.md`, section III.3 |
| FC | III.4 | `coverage-layers-ledger-2026-10-06.md`, section III.4 |
| FD | III.5 | `coverage-layers-ledger-2026-10-06.md`, section III.5 |
| FE | Article IV | `coverage-layers-ledger-2026-10-06.md`, section Article IV |
| FF | IV.1 | `coverage-layers-ledger-2026-10-06.md`, section IV.1 |
| FG | IV.2 | `coverage-layers-ledger-2026-10-06.md`, section IV.2 |
| FH | IV.3 | `coverage-layers-ledger-2026-10-06.md`, section IV.3 |
| FI | IV.5 | `coverage-layers-ledger-2026-10-06.md`, section IV.5 |
| FJ | IV.6 | `coverage-layers-ledger-2026-10-06.md`, section IV.6 |
| FK | IV.4 | `coverage-layers-ledger-2026-10-06.md`, section IV.4 |
| FL | IV.7 | `coverage-layers-ledger-2026-10-06.md`, section IV.7 |
| FM | IV.8 | `coverage-layers-ledger-2026-10-06.md`, section IV.8 |
| FN | Article V | `coverage-layers-ledger-2026-10-06.md`, section Article V |
| FO | V.1 | `coverage-layers-ledger-2026-10-06.md`, section V.1 |
| FP | V.2 | `coverage-layers-ledger-2026-10-06.md`, section V.2 |
| FQ | V.3 | `coverage-layers-ledger-2026-10-06.md`, section V.3 |
| FR | V.4 | `coverage-layers-ledger-2026-10-06.md`, section V.4 |
| FS | V.4a | `coverage-layers-ledger-2026-10-06.md`, section V.4a |
| FT | V.4b | `coverage-layers-ledger-2026-10-06.md`, section V.4b |
| FU | V.5 | `coverage-layers-ledger-2026-10-06.md`, section V.5 |
| FV | V.6 | `coverage-layers-ledger-2026-10-06.md`, section V.6 |
| FW | V.7 | `coverage-layers-ledger-2026-10-06.md`, section V.7 |
| FX | V.8 | `coverage-layers-ledger-2026-10-06.md`, section V.8 |
| FY | V.9 | `coverage-layers-ledger-2026-10-06.md`, section V.9 |
| FZ | Article VI | `coverage-layers-ledger-2026-10-06.md`, section Article VI |
| GA | VI.1 | `coverage-layers-ledger-2026-10-06.md`, section VI.1 |
| GB | VI.2 | `coverage-layers-ledger-2026-10-06.md`, section VI.2 |
| GC | VI.3 | `coverage-layers-ledger-2026-10-06.md`, section VI.3 |
| GD | VI.4 | `coverage-layers-ledger-2026-10-06.md`, section VI.4 |
| GE | VI.5 | `coverage-layers-ledger-2026-10-06.md`, section VI.5 |
| GF | VI.6 | `coverage-layers-ledger-2026-10-06.md`, section VI.6 |
| GG | Article VII | `coverage-layers-ledger-2026-10-06.md`, section Article VII |
| GH | VII.default | `coverage-layers-ledger-2026-10-06.md`, section VII.default |
| GI | Article VIII | `coverage-layers-ledger-2026-10-06.md`, section Article VIII |
| GJ | VIII.1 | `coverage-layers-ledger-2026-10-06.md`, section VIII.1 |
| GK | VIII.2 | `coverage-layers-ledger-2026-10-06.md`, section VIII.2 |
| GL | VIII.3 | `coverage-layers-ledger-2026-10-06.md`, section VIII.3 |
| GM | Article IX | `coverage-layers-ledger-2026-10-06.md`, section Article IX |
| GN | IX.1 | `coverage-layers-ledger-2026-10-06.md`, section IX.1 |
| GO | IX.2 | `coverage-layers-ledger-2026-10-06.md`, section IX.2 |
| GP | IX.3 | `coverage-layers-ledger-2026-10-06.md`, section IX.3 |
| GQ | IX.4 | `coverage-layers-ledger-2026-10-06.md`, section IX.4 |
| GR | Article X | `coverage-layers-ledger-2026-10-06.md`, section Article X |
| GS | X.1 | `coverage-layers-ledger-2026-10-06.md`, section X.1 |
| GT | X.2 | `coverage-layers-ledger-2026-10-06.md`, section X.2 |
| GU | X.3 | `coverage-layers-ledger-2026-10-06.md`, section X.3 |
| GV | X.4 | `coverage-layers-ledger-2026-10-06.md`, section X.4 |
| GW | X.4a | `coverage-layers-ledger-2026-10-06.md`, section X.4a |
| GX | Article XI | `coverage-layers-ledger-2026-10-06.md`, section Article XI |
| GY | XI.1 | `coverage-layers-ledger-2026-10-06.md`, section XI.1 |
| GZ | XI.2 | `coverage-layers-ledger-2026-10-06.md`, section XI.2 |
| HA | XI.3 | `coverage-layers-ledger-2026-10-06.md`, section XI.3 |
| HB | Article XII | `coverage-layers-ledger-2026-10-06.md`, section Article XII |
| HC | XII.1 | `coverage-layers-ledger-2026-10-06.md`, section XII.1 |
| HD | XII.2 | `coverage-layers-ledger-2026-10-06.md`, section XII.2 |
| HE | XII.3 | `coverage-layers-ledger-2026-10-06.md`, section XII.3 |
| HF | XII.4 | `coverage-layers-ledger-2026-10-06.md`, section XII.4 |
| HG | Article XIII | `coverage-layers-ledger-2026-10-06.md`, section Article XIII |
<!-- /cross-table:sources -->

## Index

<!-- cross-table:index -->
| Cell | Rule | Source | Share | Standing |
|---|---|---|---|---|
| EH1 | - layer `Article 0` on `master`: 8 files cite it (trace-id 8); verdict undeclared; titled "The Eternity Clause" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:18 | 0.19% | unattested |
| EH2 | - layer `Article 0` on `ccr-392b8b73-v809qu`: 8 files cite it (trace-id 8); verdict undeclared; titled "The Eternity Clause" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:19 | 0.21% | unattested |
| EH3 | - layer `Article 0` on `ccr-542b5884-0deee5`: 9 files cite it (trace-id 8, anchor 1); verdict undeclared; titled "The Eternity Clause" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:20 | 0.22% | unattested |
| EH4 | - layer `Article 0` on `ccr-8a588c96-jf76ei`: 9 files cite it (trace-id 8, anchor 1); verdict undeclared; titled "The Eternity Clause" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:21 | 0.22% | unattested |
| EH5 | - layer `Article 0` on `claude/agent-instruction-files`: 8 files cite it (trace-id 8); verdict undeclared; titled "The Eternity Clause" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:22 | 0.22% | unattested |
| EH6 | - layer `Article 0` on `claude/ai-model-smoothing-gentrification-alc5dm`: 8 files cite it (trace-id 8); verdict undeclared; titled "The Eternity Clause" on its law (Draft 0.8, blob `c6343c7`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:23 | 0.25% | unattested |
| EI1 | - layer `0.1` on `master`: 10 files cite it (trace-id 7, section-sign 9); verdict undeclared; titled "No self-attestation" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:27 | 0.21% | unattested |
| EI2 | - layer `0.1` on `ccr-392b8b73-v809qu`: 14 files cite it (trace-id 7, section-sign 13); verdict undeclared; titled "No self-attestation" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:28 | 0.23% | unattested |
| EI3 | - layer `0.1` on `ccr-542b5884-0deee5`: 13 files cite it (trace-id 7, section-sign 12); verdict undeclared; titled "No self-attestation" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:29 | 0.23% | unattested |
| EI4 | - layer `0.1` on `ccr-8a588c96-jf76ei`: 12 files cite it (trace-id 7, section-sign 11); verdict undeclared; titled "No self-attestation" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:30 | 0.23% | unattested |
| EI5 | - layer `0.1` on `claude/agent-instruction-files`: 10 files cite it (trace-id 7, section-sign 9); verdict undeclared; titled "No self-attestation" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:31 | 0.24% | unattested |
| EI6 | - layer `0.1` on `claude/ai-model-smoothing-gentrification-alc5dm`: 10 files cite it (trace-id 7, section-sign 9); verdict undeclared; titled "No self-attestation" on its law (Draft 0.8, blob `c6343c7`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:32 | 0.26% | unattested |
| EJ1 | - layer `0.2` on `master`: 20 files cite it (trace-id 5, section-sign 19); verdict undeclared; titled "No self-ratification to canon" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:36 | 0.22% | unattested |
| EJ2 | - layer `0.2` on `ccr-392b8b73-v809qu`: 26 files cite it (trace-id 5, section-sign 25); verdict undeclared; titled "No self-ratification to canon" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:37 | 0.24% | unattested |
| EJ3 | - layer `0.2` on `ccr-542b5884-0deee5`: 22 files cite it (trace-id 5, section-sign 21); verdict undeclared; titled "No self-ratification to canon" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:38 | 0.24% | unattested |
| EJ4 | - layer `0.2` on `ccr-8a588c96-jf76ei`: 21 files cite it (trace-id 5, section-sign 20); verdict undeclared; titled "No self-ratification to canon" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:39 | 0.24% | unattested |
| EJ5 | - layer `0.2` on `claude/agent-instruction-files`: 20 files cite it (trace-id 5, section-sign 19); verdict undeclared; titled "No self-ratification to canon" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:40 | 0.25% | unattested |
| EJ6 | - layer `0.2` on `claude/ai-model-smoothing-gentrification-alc5dm`: 18 files cite it (trace-id 5, section-sign 17); verdict undeclared; titled "No self-ratification to canon" on its law (Draft 0.8, blob `c6343c7`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:41 | 0.27% | unattested |
| EK1 | - layer `0.3` on `master`: 18 files cite it (trace-id 12, section-sign 10); verdict undeclared; titled "No self-extension of capability" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:45 | 0.23% | unattested |
| EK2 | - layer `0.3` on `ccr-392b8b73-v809qu`: 23 files cite it (trace-id 12, section-sign 15); verdict undeclared; titled "No self-extension of capability" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:46 | 0.24% | unattested |
| EK3 | - layer `0.3` on `ccr-542b5884-0deee5`: 20 files cite it (trace-id 12, section-sign 12); verdict undeclared; titled "No self-extension of capability" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:47 | 0.24% | unattested |
| EK4 | - layer `0.3` on `ccr-8a588c96-jf76ei`: 19 files cite it (trace-id 12, section-sign 11); verdict undeclared; titled "No self-extension of capability" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:48 | 0.24% | unattested |
| EK5 | - layer `0.3` on `claude/agent-instruction-files`: 18 files cite it (trace-id 12, section-sign 10); verdict undeclared; titled "No self-extension of capability" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:49 | 0.26% | unattested |
| EK6 | - layer `0.3` on `claude/ai-model-smoothing-gentrification-alc5dm`: 18 files cite it (trace-id 12, section-sign 10); verdict undeclared; titled "No self-extension of capability" on its law (Draft 0.8, blob `c6343c7`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:50 | 0.28% | unattested |
| EL1 | - layer `0.4` on `master`: 7 files cite it (trace-id 3, section-sign 6); verdict undeclared; titled "The human key is required, and cannot be forged forward" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:54 | 0.25% | unattested |
| EL2 | - layer `0.4` on `ccr-392b8b73-v809qu`: 12 files cite it (trace-id 4, section-sign 11); verdict undeclared; titled "The human key is required, and cannot be forged forward" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:55 | 0.27% | unattested |
| EL3 | - layer `0.4` on `ccr-542b5884-0deee5`: 8 files cite it (trace-id 3, section-sign 7); verdict undeclared; titled "The human key is required, and cannot be forged forward" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:56 | 0.27% | unattested |
| EL4 | - layer `0.4` on `ccr-8a588c96-jf76ei`: 8 files cite it (trace-id 3, section-sign 7); verdict undeclared; titled "The human key is required, and cannot be forged forward" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:57 | 0.27% | unattested |
| EL5 | - layer `0.4` on `claude/agent-instruction-files`: 7 files cite it (trace-id 3, section-sign 6); verdict undeclared; titled "The human key is required, and cannot be forged forward" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:58 | 0.28% | unattested |
| EL6 | - layer `0.4` on `claude/ai-model-smoothing-gentrification-alc5dm`: 7 files cite it (trace-id 3, section-sign 6); verdict undeclared; titled "The human key is required, and cannot be forged forward" on its law (Draft 0.8, blob `c6343c7`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:59 | 0.31% | unattested |
| EM1 | - layer `0.5` on `master`: 11 files cite it (trace-id 5, section-sign 9); verdict undeclared; titled "The Record is append-only and its keepers are bound by it" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:63 | 0.26% | unattested |
| EM2 | - layer `0.5` on `ccr-392b8b73-v809qu`: 16 files cite it (trace-id 5, section-sign 14); verdict undeclared; titled "The Record is append-only and its keepers are bound by it" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:64 | 0.27% | unattested |
| EM3 | - layer `0.5` on `ccr-542b5884-0deee5`: 13 files cite it (trace-id 5, section-sign 11); verdict undeclared; titled "The Record is append-only and its keepers are bound by it" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:65 | 0.27% | unattested |
| EM4 | - layer `0.5` on `ccr-8a588c96-jf76ei`: 13 files cite it (trace-id 5, section-sign 11); verdict undeclared; titled "The Record is append-only and its keepers are bound by it" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:66 | 0.27% | unattested |
| EM5 | - layer `0.5` on `claude/agent-instruction-files`: 11 files cite it (trace-id 5, section-sign 9); verdict undeclared; titled "The Record is append-only and its keepers are bound by it" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:67 | 0.29% | unattested |
| EM6 | - layer `0.5` on `claude/ai-model-smoothing-gentrification-alc5dm`: 11 files cite it (trace-id 5, section-sign 9); verdict undeclared; titled "The Record is append-only and its keepers are bound by it" on its law (Draft 0.8, blob `c6343c7`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:68 | 0.31% | unattested |
| EN1 | - layer `0.6` on `master`: 11 files cite it (trace-id 7, section-sign 6); verdict undeclared; titled "Silence escalates" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:72 | 0.21% | unattested |
| EN2 | - layer `0.6` on `ccr-392b8b73-v809qu`: 15 files cite it (trace-id 7, section-sign 10); verdict undeclared; titled "Silence escalates" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:73 | 0.22% | unattested |
| EN3 | - layer `0.6` on `ccr-542b5884-0deee5`: 13 files cite it (trace-id 7, section-sign 8); verdict undeclared; titled "Silence escalates" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:74 | 0.22% | unattested |
| EN4 | - layer `0.6` on `ccr-8a588c96-jf76ei`: 13 files cite it (trace-id 7, section-sign 8); verdict undeclared; titled "Silence escalates" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:75 | 0.22% | unattested |
| EN5 | - layer `0.6` on `claude/agent-instruction-files`: 11 files cite it (trace-id 7, section-sign 6); verdict undeclared; titled "Silence escalates" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:76 | 0.24% | unattested |
| EN6 | - layer `0.6` on `claude/ai-model-smoothing-gentrification-alc5dm`: 10 files cite it (trace-id 7, section-sign 5); verdict undeclared; titled "Silence escalates" on its law (Draft 0.8, blob `c6343c7`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:77 | 0.26% | unattested |
| EO1 | - layer `Article I` on `master`: 13 files cite it (trace-id 13); verdict undeclared; titled "Identity & Standing" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:81 | 0.20% | unattested |
| EO2 | - layer `Article I` on `ccr-392b8b73-v809qu`: 14 files cite it (trace-id 14); verdict undeclared; titled "Identity & Standing" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:82 | 0.21% | unattested |
| EO3 | - layer `Article I` on `ccr-542b5884-0deee5`: 14 files cite it (trace-id 13, anchor 1); verdict undeclared; titled "Identity & Standing" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:83 | 0.23% | unattested |
| EO4 | - layer `Article I` on `ccr-8a588c96-jf76ei`: 14 files cite it (trace-id 13, anchor 1); verdict undeclared; titled "Identity & Standing" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:84 | 0.23% | unattested |
| EO5 | - layer `Article I` on `claude/agent-instruction-files`: 13 files cite it (trace-id 13); verdict undeclared; titled "Identity & Standing" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:85 | 0.23% | unattested |
| EO6 | - layer `Article I` on `claude/ai-model-smoothing-gentrification-alc5dm`: 12 files cite it (trace-id 12); verdict undeclared; titled "Identity & Standing" on its law (Draft 0.8, blob `c6343c7`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:86 | 0.25% | unattested |
| EP1 | - layer `I.1` on `master`: 7 files cite it (trace-id 7); verdict undeclared; titled "Identity is the manifest, not the runtime" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:90 | 0.21% | unattested |
| EP2 | - layer `I.1` on `ccr-392b8b73-v809qu`: 7 files cite it (trace-id 7); verdict undeclared; titled "Identity is the manifest, not the runtime" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:91 | 0.23% | unattested |
| EP3 | - layer `I.1` on `ccr-542b5884-0deee5`: 7 files cite it (trace-id 7); verdict undeclared; titled "Identity is the manifest, not the runtime" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:92 | 0.23% | unattested |
| EP4 | - layer `I.1` on `ccr-8a588c96-jf76ei`: 7 files cite it (trace-id 7); verdict undeclared; titled "Identity is the manifest, not the runtime" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:93 | 0.23% | unattested |
| EP5 | - layer `I.1` on `claude/agent-instruction-files`: 7 files cite it (trace-id 7); verdict undeclared; titled "Identity is the manifest, not the runtime" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:94 | 0.24% | unattested |
| EP6 | - layer `I.1` on `claude/ai-model-smoothing-gentrification-alc5dm`: 7 files cite it (trace-id 7); verdict undeclared; titled "Identity is the manifest, not the runtime" on its law (Draft 0.8, blob `c6343c7`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:95 | 0.27% | unattested |
| EQ1 | - layer `I.2` on `master`: 0 files cite it; verdict undeclared; titled "Standing follows identity and role" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:99 | 0.19% | unattested |
| EQ2 | - layer `I.2` on `ccr-392b8b73-v809qu`: 0 files cite it; verdict undeclared; titled "Standing follows identity and role" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:100 | 0.21% | unattested |
| EQ3 | - layer `I.2` on `ccr-542b5884-0deee5`: 0 files cite it; verdict undeclared; titled "Standing follows identity and role" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:101 | 0.21% | unattested |
| EQ4 | - layer `I.2` on `ccr-8a588c96-jf76ei`: 0 files cite it; verdict undeclared; titled "Standing follows identity and role" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:102 | 0.21% | unattested |
| EQ5 | - layer `I.2` on `claude/agent-instruction-files`: 0 files cite it; verdict undeclared; titled "Standing follows identity and role" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:103 | 0.22% | unattested |
| EQ6 | - layer `I.2` on `claude/ai-model-smoothing-gentrification-alc5dm`: 0 files cite it; verdict undeclared; titled "Standing follows identity and role" on its law (Draft 0.8, blob `c6343c7`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:104 | 0.24% | unattested |
| ER1 | - layer `I.3` on `master`: 1 file cites it (trace-id 1); verdict undeclared; titled "Issuance and revocation are reserved" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:108 | 0.21% | unattested |
| ER2 | - layer `I.3` on `ccr-392b8b73-v809qu`: 1 file cites it (trace-id 1); verdict undeclared; titled "Issuance and revocation are reserved" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:109 | 0.22% | unattested |
| ER3 | - layer `I.3` on `ccr-542b5884-0deee5`: 1 file cites it (trace-id 1); verdict undeclared; titled "Issuance and revocation are reserved" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:110 | 0.22% | unattested |
| ER4 | - layer `I.3` on `ccr-8a588c96-jf76ei`: 1 file cites it (trace-id 1); verdict undeclared; titled "Issuance and revocation are reserved" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:111 | 0.22% | unattested |
| ER5 | - layer `I.3` on `claude/agent-instruction-files`: 1 file cites it (trace-id 1); verdict undeclared; titled "Issuance and revocation are reserved" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:112 | 0.24% | unattested |
| ER6 | - layer `I.3` on `claude/ai-model-smoothing-gentrification-alc5dm`: 1 file cites it (trace-id 1); verdict undeclared; titled "Issuance and revocation are reserved" on its law (Draft 0.8, blob `c6343c7`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:113 | 0.26% | unattested |
| ES1 | - layer `I.4` on `master`: 0 files cite it; verdict undeclared; titled "Drift is suspicion, and suspicion suspends" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:117 | 0.20% | unattested |
| ES2 | - layer `I.4` on `ccr-392b8b73-v809qu`: 0 files cite it; verdict undeclared; titled "Drift is suspicion, and suspicion suspends" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:118 | 0.22% | unattested |
| ES3 | - layer `I.4` on `ccr-542b5884-0deee5`: 0 files cite it; verdict undeclared; titled "Drift is suspicion, and suspicion suspends" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:119 | 0.22% | unattested |
| ES4 | - layer `I.4` on `ccr-8a588c96-jf76ei`: 0 files cite it; verdict undeclared; titled "Drift is suspicion, and suspicion suspends" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:120 | 0.22% | unattested |
| ES5 | - layer `I.4` on `claude/agent-instruction-files`: 0 files cite it; verdict undeclared; titled "Drift is suspicion, and suspicion suspends" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:121 | 0.23% | unattested |
| ES6 | - layer `I.4` on `claude/ai-model-smoothing-gentrification-alc5dm`: 0 files cite it; verdict undeclared; titled "Drift is suspicion, and suspicion suspends" on its law (Draft 0.8, blob `c6343c7`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:122 | 0.25% | unattested |
| ET1 | - layer `I.5` on `master`: 0 files cite it; verdict undeclared; titled "Presence is a label; authority is a key" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:126 | 0.19% | unattested |
| ET2 | - layer `I.5` on `ccr-392b8b73-v809qu`: 0 files cite it; verdict undeclared; titled "Presence is a label; authority is a key" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:127 | 0.21% | unattested |
| ET3 | - layer `I.5` on `ccr-542b5884-0deee5`: 0 files cite it; verdict undeclared; titled "Presence is a label; authority is a key" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:128 | 0.21% | unattested |
| ET4 | - layer `I.5` on `ccr-8a588c96-jf76ei`: 0 files cite it; verdict undeclared; titled "Presence is a label; authority is a key" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:129 | 0.21% | unattested |
| ET5 | - layer `I.5` on `claude/agent-instruction-files`: 0 files cite it; verdict undeclared; titled "Presence is a label; authority is a key" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:130 | 0.23% | unattested |
| ET6 | - layer `I.5` on `claude/ai-model-smoothing-gentrification-alc5dm`: not a clause of this branch's law (Draft 0.8, blob `c6343c7`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:131 | 0.17% | unattested |
| EU1 | - layer `Article II` on `master`: 4 files cite it (trace-id 4); verdict undeclared; titled "Enumerated Capabilities" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:135 | 0.20% | unattested |
| EU2 | - layer `Article II` on `ccr-392b8b73-v809qu`: 4 files cite it (trace-id 4); verdict undeclared; titled "Enumerated Capabilities" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:136 | 0.22% | unattested |
| EU3 | - layer `Article II` on `ccr-542b5884-0deee5`: 4 files cite it (trace-id 4); verdict undeclared; titled "Enumerated Capabilities" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:137 | 0.22% | unattested |
| EU4 | - layer `Article II` on `ccr-8a588c96-jf76ei`: 4 files cite it (trace-id 4); verdict undeclared; titled "Enumerated Capabilities" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:138 | 0.22% | unattested |
| EU5 | - layer `Article II` on `claude/agent-instruction-files`: 4 files cite it (trace-id 4); verdict undeclared; titled "Enumerated Capabilities" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:139 | 0.23% | unattested |
| EU6 | - layer `Article II` on `claude/ai-model-smoothing-gentrification-alc5dm`: 4 files cite it (trace-id 4); verdict undeclared; titled "Enumerated Capabilities" on its law (Draft 0.8, blob `c6343c7`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:140 | 0.25% | unattested |
| EV1 | - layer `II.1` on `master`: 0 files cite it; verdict undeclared; titled "Capabilities are enumerated, not inferred" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:144 | 0.20% | unattested |
| EV2 | - layer `II.1` on `ccr-392b8b73-v809qu`: 0 files cite it; verdict undeclared; titled "Capabilities are enumerated, not inferred" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:145 | 0.22% | unattested |
| EV3 | - layer `II.1` on `ccr-542b5884-0deee5`: 0 files cite it; verdict undeclared; titled "Capabilities are enumerated, not inferred" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:146 | 0.22% | unattested |
| EV4 | - layer `II.1` on `ccr-8a588c96-jf76ei`: 0 files cite it; verdict undeclared; titled "Capabilities are enumerated, not inferred" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:147 | 0.22% | unattested |
| EV5 | - layer `II.1` on `claude/agent-instruction-files`: 0 files cite it; verdict undeclared; titled "Capabilities are enumerated, not inferred" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:148 | 0.23% | unattested |
| EV6 | - layer `II.1` on `claude/ai-model-smoothing-gentrification-alc5dm`: 0 files cite it; verdict undeclared; titled "Capabilities are enumerated, not inferred" on its law (Draft 0.8, blob `c6343c7`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:149 | 0.25% | unattested |
| EW1 | - layer `II.2` on `master`: 0 files cite it; verdict undeclared; titled "Creation is reserved; delegation is witnessed" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:153 | 0.20% | unattested |
| EW2 | - layer `II.2` on `ccr-392b8b73-v809qu`: 0 files cite it; verdict undeclared; titled "Creation is reserved; delegation is witnessed" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:154 | 0.22% | unattested |
| EW3 | - layer `II.2` on `ccr-542b5884-0deee5`: 0 files cite it; verdict undeclared; titled "Creation is reserved; delegation is witnessed" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:155 | 0.22% | unattested |
| EW4 | - layer `II.2` on `ccr-8a588c96-jf76ei`: 0 files cite it; verdict undeclared; titled "Creation is reserved; delegation is witnessed" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:156 | 0.22% | unattested |
| EW5 | - layer `II.2` on `claude/agent-instruction-files`: 0 files cite it; verdict undeclared; titled "Creation is reserved; delegation is witnessed" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:157 | 0.23% | unattested |
| EW6 | - layer `II.2` on `claude/ai-model-smoothing-gentrification-alc5dm`: 0 files cite it; verdict undeclared; titled "Creation is reserved; delegation is witnessed" on its law (Draft 0.8, blob `c6343c7`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:158 | 0.26% | unattested |
| EX1 | - layer `II.3` on `master`: 0 files cite it; verdict undeclared; titled "The veto, and its limits" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:162 | 0.18% | unattested |
| EX2 | - layer `II.3` on `ccr-392b8b73-v809qu`: 0 files cite it; verdict undeclared; titled "The veto, and its limits" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:163 | 0.19% | unattested |
| EX3 | - layer `II.3` on `ccr-542b5884-0deee5`: 0 files cite it; verdict undeclared; titled "The veto, and its limits" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:164 | 0.19% | unattested |
| EX4 | - layer `II.3` on `ccr-8a588c96-jf76ei`: 0 files cite it; verdict undeclared; titled "The veto, and its limits" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:165 | 0.19% | unattested |
| EX5 | - layer `II.3` on `claude/agent-instruction-files`: 0 files cite it; verdict undeclared; titled "The veto, and its limits" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:166 | 0.21% | unattested |
| EX6 | - layer `II.3` on `claude/ai-model-smoothing-gentrification-alc5dm`: 0 files cite it; verdict undeclared; titled "The veto, and its limits" on its law (Draft 0.8, blob `c6343c7`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:167 | 0.23% | unattested |
| EY1 | - layer `Article III` on `master`: 11 files cite it (trace-id 11); verdict undeclared; titled "Reach & Jurisdiction" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:171 | 0.20% | unattested |
| EY2 | - layer `Article III` on `ccr-392b8b73-v809qu`: 12 files cite it (trace-id 12); verdict undeclared; titled "Reach & Jurisdiction" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:172 | 0.22% | unattested |
| EY3 | - layer `Article III` on `ccr-542b5884-0deee5`: 12 files cite it (trace-id 11, anchor 1); verdict undeclared; titled "Reach & Jurisdiction" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:173 | 0.23% | unattested |
| EY4 | - layer `Article III` on `ccr-8a588c96-jf76ei`: 12 files cite it (trace-id 11, anchor 1); verdict undeclared; titled "Reach & Jurisdiction" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:174 | 0.23% | unattested |
| EY5 | - layer `Article III` on `claude/agent-instruction-files`: 11 files cite it (trace-id 11); verdict undeclared; titled "Reach & Jurisdiction" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:175 | 0.23% | unattested |
| EY6 | - layer `Article III` on `claude/ai-model-smoothing-gentrification-alc5dm`: 11 files cite it (trace-id 11); verdict undeclared; titled "Reach & Jurisdiction" on its law (Draft 0.8, blob `c6343c7`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:176 | 0.25% | unattested |
| EZ1 | - layer `III.1` on `master`: 0 files cite it; verdict undeclared; titled "Default-deny" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:180 | 0.16% | unattested |
| EZ2 | - layer `III.1` on `ccr-392b8b73-v809qu`: 0 files cite it; verdict undeclared; titled "Default-deny" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:181 | 0.18% | unattested |
| EZ3 | - layer `III.1` on `ccr-542b5884-0deee5`: 0 files cite it; verdict undeclared; titled "Default-deny" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:182 | 0.18% | unattested |
| EZ4 | - layer `III.1` on `ccr-8a588c96-jf76ei`: 0 files cite it; verdict undeclared; titled "Default-deny" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:183 | 0.18% | unattested |
| EZ5 | - layer `III.1` on `claude/agent-instruction-files`: 0 files cite it; verdict undeclared; titled "Default-deny" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:184 | 0.19% | unattested |
| EZ6 | - layer `III.1` on `claude/ai-model-smoothing-gentrification-alc5dm`: 0 files cite it; verdict undeclared; titled "Default-deny" on its law (Draft 0.8, blob `c6343c7`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:185 | 0.22% | unattested |
| FA1 | - layer `III.2` on `master`: 6 files cite it (trace-id 6); verdict undeclared; titled "Pre-Approved Scope is the standing grant" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:189 | 0.22% | unattested |
| FA2 | - layer `III.2` on `ccr-392b8b73-v809qu`: 6 files cite it (trace-id 6); verdict undeclared; titled "Pre-Approved Scope is the standing grant" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:190 | 0.23% | unattested |
| FA3 | - layer `III.2` on `ccr-542b5884-0deee5`: 6 files cite it (trace-id 6); verdict undeclared; titled "Pre-Approved Scope is the standing grant" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:191 | 0.23% | unattested |
| FA4 | - layer `III.2` on `ccr-8a588c96-jf76ei`: 6 files cite it (trace-id 6); verdict undeclared; titled "Pre-Approved Scope is the standing grant" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:192 | 0.23% | unattested |
| FA5 | - layer `III.2` on `claude/agent-instruction-files`: 6 files cite it (trace-id 6); verdict undeclared; titled "Pre-Approved Scope is the standing grant" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:193 | 0.25% | unattested |
| FA6 | - layer `III.2` on `claude/ai-model-smoothing-gentrification-alc5dm`: 6 files cite it (trace-id 6); verdict undeclared; titled "Pre-Approved Scope is the standing grant" on its law (Draft 0.8, blob `c6343c7`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:194 | 0.27% | unattested |
| FB1 | - layer `III.3` on `master`: 0 files cite it; verdict undeclared; titled "Every grant expires" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:198 | 0.17% | unattested |
| FB2 | - layer `III.3` on `ccr-392b8b73-v809qu`: 0 files cite it; verdict undeclared; titled "Every grant expires" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:199 | 0.19% | unattested |
| FB3 | - layer `III.3` on `ccr-542b5884-0deee5`: 0 files cite it; verdict undeclared; titled "Every grant expires" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:200 | 0.19% | unattested |
| FB4 | - layer `III.3` on `ccr-8a588c96-jf76ei`: 0 files cite it; verdict undeclared; titled "Every grant expires" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:201 | 0.19% | unattested |
| FB5 | - layer `III.3` on `claude/agent-instruction-files`: 0 files cite it; verdict undeclared; titled "Every grant expires" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:202 | 0.20% | unattested |
| FB6 | - layer `III.3` on `claude/ai-model-smoothing-gentrification-alc5dm`: 0 files cite it; verdict undeclared; titled "Every grant expires" on its law (Draft 0.8, blob `c6343c7`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:203 | 0.22% | unattested |
| FC1 | - layer `III.4` on `master`: 0 files cite it; verdict undeclared; titled "Reach is audited" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:207 | 0.17% | unattested |
| FC2 | - layer `III.4` on `ccr-392b8b73-v809qu`: 0 files cite it; verdict undeclared; titled "Reach is audited" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:208 | 0.18% | unattested |
| FC3 | - layer `III.4` on `ccr-542b5884-0deee5`: 0 files cite it; verdict undeclared; titled "Reach is audited" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:209 | 0.18% | unattested |
| FC4 | - layer `III.4` on `ccr-8a588c96-jf76ei`: 0 files cite it; verdict undeclared; titled "Reach is audited" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:210 | 0.18% | unattested |
| FC5 | - layer `III.4` on `claude/agent-instruction-files`: 0 files cite it; verdict undeclared; titled "Reach is audited" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:211 | 0.20% | unattested |
| FC6 | - layer `III.4` on `claude/ai-model-smoothing-gentrification-alc5dm`: 0 files cite it; verdict undeclared; titled "Reach is audited" on its law (Draft 0.8, blob `c6343c7`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:212 | 0.22% | unattested |
| FD1 | - layer `III.5` on `master`: 0 files cite it; verdict undeclared; titled "Reach guards what leaves" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:216 | 0.18% | unattested |
| FD2 | - layer `III.5` on `ccr-392b8b73-v809qu`: 0 files cite it; verdict undeclared; titled "Reach guards what leaves" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:217 | 0.19% | unattested |
| FD3 | - layer `III.5` on `ccr-542b5884-0deee5`: 0 files cite it; verdict undeclared; titled "Reach guards what leaves" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:218 | 0.19% | unattested |
| FD4 | - layer `III.5` on `ccr-8a588c96-jf76ei`: 0 files cite it; verdict undeclared; titled "Reach guards what leaves" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:219 | 0.19% | unattested |
| FD5 | - layer `III.5` on `claude/agent-instruction-files`: 0 files cite it; verdict undeclared; titled "Reach guards what leaves" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:220 | 0.21% | unattested |
| FD6 | - layer `III.5` on `claude/ai-model-smoothing-gentrification-alc5dm`: not a clause of this branch's law (Draft 0.8, blob `c6343c7`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:221 | 0.17% | unattested |
| FE1 | - layer `Article IV` on `master`: 13 files cite it (trace-id 13); verdict undeclared; titled "Knowledge & Canon" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:225 | 0.19% | unattested |
| FE2 | - layer `Article IV` on `ccr-392b8b73-v809qu`: 14 files cite it (trace-id 14); verdict undeclared; titled "Knowledge & Canon" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:226 | 0.21% | unattested |
| FE3 | - layer `Article IV` on `ccr-542b5884-0deee5`: 14 files cite it (trace-id 13, anchor 1); verdict undeclared; titled "Knowledge & Canon" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:227 | 0.22% | unattested |
| FE4 | - layer `Article IV` on `ccr-8a588c96-jf76ei`: 14 files cite it (trace-id 13, anchor 1); verdict undeclared; titled "Knowledge & Canon" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:228 | 0.22% | unattested |
| FE5 | - layer `Article IV` on `claude/agent-instruction-files`: 13 files cite it (trace-id 13); verdict undeclared; titled "Knowledge & Canon" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:229 | 0.23% | unattested |
| FE6 | - layer `Article IV` on `claude/ai-model-smoothing-gentrification-alc5dm`: 13 files cite it (trace-id 13); verdict undeclared; titled "Knowledge & Canon" on its law (Draft 0.8, blob `c6343c7`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:230 | 0.25% | unattested |
| FF1 | - layer `IV.1` on `master`: 1 file cites it (trace-id 1); verdict undeclared; titled "Two axes, and the three tiers they compose" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:234 | 0.22% | unattested |
| FF2 | - layer `IV.1` on `ccr-392b8b73-v809qu`: 1 file cites it (trace-id 1); verdict undeclared; titled "Two axes, and the three tiers they compose" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:235 | 0.23% | unattested |
| FF3 | - layer `IV.1` on `ccr-542b5884-0deee5`: 1 file cites it (trace-id 1); verdict undeclared; titled "Two axes, and the three tiers they compose" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:236 | 0.23% | unattested |
| FF4 | - layer `IV.1` on `ccr-8a588c96-jf76ei`: 1 file cites it (trace-id 1); verdict undeclared; titled "Two axes, and the three tiers they compose" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:237 | 0.23% | unattested |
| FF5 | - layer `IV.1` on `claude/agent-instruction-files`: 1 file cites it (trace-id 1); verdict undeclared; titled "Two axes, and the three tiers they compose" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:238 | 0.25% | unattested |
| FF6 | - layer `IV.1` on `claude/ai-model-smoothing-gentrification-alc5dm`: 1 file cites it (trace-id 1); verdict undeclared; titled "Two axes, and the three tiers they compose" on its law (Draft 0.8, blob `c6343c7`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:239 | 0.27% | unattested |
| FG1 | - layer `IV.2` on `master`: 1 file cites it (trace-id 1); verdict undeclared; titled "Anyone proposes; no one ratifies their own" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:243 | 0.22% | unattested |
| FG2 | - layer `IV.2` on `ccr-392b8b73-v809qu`: 1 file cites it (trace-id 1); verdict undeclared; titled "Anyone proposes; no one ratifies their own" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:244 | 0.23% | unattested |
| FG3 | - layer `IV.2` on `ccr-542b5884-0deee5`: 1 file cites it (trace-id 1); verdict undeclared; titled "Anyone proposes; no one ratifies their own" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:245 | 0.23% | unattested |
| FG4 | - layer `IV.2` on `ccr-8a588c96-jf76ei`: 1 file cites it (trace-id 1); verdict undeclared; titled "Anyone proposes; no one ratifies their own" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:246 | 0.23% | unattested |
| FG5 | - layer `IV.2` on `claude/agent-instruction-files`: 1 file cites it (trace-id 1); verdict undeclared; titled "Anyone proposes; no one ratifies their own" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:247 | 0.25% | unattested |
| FG6 | - layer `IV.2` on `claude/ai-model-smoothing-gentrification-alc5dm`: 1 file cites it (trace-id 1); verdict undeclared; titled "Anyone proposes; no one ratifies their own" on its law (Draft 0.8, blob `c6343c7`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:248 | 0.27% | unattested |
| FH1 | - layer `IV.3` on `master`: 1 file cites it (trace-id 1); verdict undeclared; titled "Canonical costs the most" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:252 | 0.19% | unattested |
| FH2 | - layer `IV.3` on `ccr-392b8b73-v809qu`: 1 file cites it (trace-id 1); verdict undeclared; titled "Canonical costs the most" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:253 | 0.21% | unattested |
| FH3 | - layer `IV.3` on `ccr-542b5884-0deee5`: 1 file cites it (trace-id 1); verdict undeclared; titled "Canonical costs the most" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:254 | 0.21% | unattested |
| FH4 | - layer `IV.3` on `ccr-8a588c96-jf76ei`: 1 file cites it (trace-id 1); verdict undeclared; titled "Canonical costs the most" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:255 | 0.21% | unattested |
| FH5 | - layer `IV.3` on `claude/agent-instruction-files`: 1 file cites it (trace-id 1); verdict undeclared; titled "Canonical costs the most" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:256 | 0.22% | unattested |
| FH6 | - layer `IV.3` on `claude/ai-model-smoothing-gentrification-alc5dm`: 1 file cites it (trace-id 1); verdict undeclared; titled "Canonical costs the most" on its law (Draft 0.8, blob `c6343c7`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:257 | 0.25% | unattested |
| FI1 | - layer `IV.5` on `master`: 1 file cites it (trace-id 1); verdict undeclared; titled "Neither axis may be inferred from the other" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:261 | 0.22% | unattested |
| FI2 | - layer `IV.5` on `ccr-392b8b73-v809qu`: 1 file cites it (trace-id 1); verdict undeclared; titled "Neither axis may be inferred from the other" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:262 | 0.23% | unattested |
| FI3 | - layer `IV.5` on `ccr-542b5884-0deee5`: 1 file cites it (trace-id 1); verdict undeclared; titled "Neither axis may be inferred from the other" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:263 | 0.23% | unattested |
| FI4 | - layer `IV.5` on `ccr-8a588c96-jf76ei`: 1 file cites it (trace-id 1); verdict undeclared; titled "Neither axis may be inferred from the other" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:264 | 0.23% | unattested |
| FI5 | - layer `IV.5` on `claude/agent-instruction-files`: 1 file cites it (trace-id 1); verdict undeclared; titled "Neither axis may be inferred from the other" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:265 | 0.25% | unattested |
| FI6 | - layer `IV.5` on `claude/ai-model-smoothing-gentrification-alc5dm`: 1 file cites it (trace-id 1); verdict undeclared; titled "Neither axis may be inferred from the other" on its law (Draft 0.8, blob `c6343c7`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:266 | 0.27% | unattested |
| FJ1 | - layer `IV.6` on `master`: 1 file cites it (trace-id 1); verdict undeclared; titled "A verifier is an attribution, not a warrant" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:270 | 0.22% | unattested |
| FJ2 | - layer `IV.6` on `ccr-392b8b73-v809qu`: 1 file cites it (trace-id 1); verdict undeclared; titled "A verifier is an attribution, not a warrant" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:271 | 0.23% | unattested |
| FJ3 | - layer `IV.6` on `ccr-542b5884-0deee5`: 1 file cites it (trace-id 1); verdict undeclared; titled "A verifier is an attribution, not a warrant" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:272 | 0.23% | unattested |
| FJ4 | - layer `IV.6` on `ccr-8a588c96-jf76ei`: 1 file cites it (trace-id 1); verdict undeclared; titled "A verifier is an attribution, not a warrant" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:273 | 0.23% | unattested |
| FJ5 | - layer `IV.6` on `claude/agent-instruction-files`: 1 file cites it (trace-id 1); verdict undeclared; titled "A verifier is an attribution, not a warrant" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:274 | 0.25% | unattested |
| FJ6 | - layer `IV.6` on `claude/ai-model-smoothing-gentrification-alc5dm`: 1 file cites it (trace-id 1); verdict undeclared; titled "A verifier is an attribution, not a warrant" on its law (Draft 0.8, blob `c6343c7`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:275 | 0.27% | unattested |
| FK1 | - layer `IV.4` on `master`: 1 file cites it (trace-id 1); verdict undeclared; titled "Debasement is refused, demotion is evidenced" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:279 | 0.22% | unattested |
| FK2 | - layer `IV.4` on `ccr-392b8b73-v809qu`: 1 file cites it (trace-id 1); verdict undeclared; titled "Debasement is refused, demotion is evidenced" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:280 | 0.24% | unattested |
| FK3 | - layer `IV.4` on `ccr-542b5884-0deee5`: 1 file cites it (trace-id 1); verdict undeclared; titled "Debasement is refused, demotion is evidenced" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:281 | 0.24% | unattested |
| FK4 | - layer `IV.4` on `ccr-8a588c96-jf76ei`: 1 file cites it (trace-id 1); verdict undeclared; titled "Debasement is refused, demotion is evidenced" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:282 | 0.24% | unattested |
| FK5 | - layer `IV.4` on `claude/agent-instruction-files`: 1 file cites it (trace-id 1); verdict undeclared; titled "Debasement is refused, demotion is evidenced" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:283 | 0.25% | unattested |
| FK6 | - layer `IV.4` on `claude/ai-model-smoothing-gentrification-alc5dm`: 1 file cites it (trace-id 1); verdict undeclared; titled "Debasement is refused, demotion is evidenced" on its law (Draft 0.8, blob `c6343c7`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:284 | 0.27% | unattested |
| FL1 | - layer `IV.7` on `master`: 0 files cite it; verdict undeclared; titled "Below Canonical is kept, and nothing is discarded" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:288 | 0.21% | unattested |
| FL2 | - layer `IV.7` on `ccr-392b8b73-v809qu`: 0 files cite it; verdict undeclared; titled "Below Canonical is kept, and nothing is discarded" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:289 | 0.23% | unattested |
| FL3 | - layer `IV.7` on `ccr-542b5884-0deee5`: 0 files cite it; verdict undeclared; titled "Below Canonical is kept, and nothing is discarded" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:290 | 0.23% | unattested |
| FL4 | - layer `IV.7` on `ccr-8a588c96-jf76ei`: 0 files cite it; verdict undeclared; titled "Below Canonical is kept, and nothing is discarded" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:291 | 0.23% | unattested |
| FL5 | - layer `IV.7` on `claude/agent-instruction-files`: 0 files cite it; verdict undeclared; titled "Below Canonical is kept, and nothing is discarded" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:292 | 0.24% | unattested |
| FL6 | - layer `IV.7` on `claude/ai-model-smoothing-gentrification-alc5dm`: not a clause of this branch's law (Draft 0.8, blob `c6343c7`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:293 | 0.17% | unattested |
| FM1 | - layer `IV.8` on `master`: 0 files cite it; verdict undeclared; titled "The recorded before the new" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:297 | 0.18% | unattested |
| FM2 | - layer `IV.8` on `ccr-392b8b73-v809qu`: 0 files cite it; verdict undeclared; titled "The recorded before the new" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:298 | 0.20% | unattested |
| FM3 | - layer `IV.8` on `ccr-542b5884-0deee5`: 0 files cite it; verdict undeclared; titled "The recorded before the new" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:299 | 0.20% | unattested |
| FM4 | - layer `IV.8` on `ccr-8a588c96-jf76ei`: 0 files cite it; verdict undeclared; titled "The recorded before the new" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:300 | 0.20% | unattested |
| FM5 | - layer `IV.8` on `claude/agent-instruction-files`: 0 files cite it; verdict undeclared; titled "The recorded before the new" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:301 | 0.21% | unattested |
| FM6 | - layer `IV.8` on `claude/ai-model-smoothing-gentrification-alc5dm`: not a clause of this branch's law (Draft 0.8, blob `c6343c7`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:302 | 0.17% | unattested |
| FN1 | - layer `Article V` on `master`: 8 files cite it (trace-id 8); verdict undeclared; titled "The Human & Delegation" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:306 | 0.20% | unattested |
| FN2 | - layer `Article V` on `ccr-392b8b73-v809qu`: 8 files cite it (trace-id 8); verdict undeclared; titled "The Human & Delegation" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:307 | 0.21% | unattested |
| FN3 | - layer `Article V` on `ccr-542b5884-0deee5`: 9 files cite it (trace-id 8, anchor 1); verdict undeclared; titled "The Human & Delegation" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:308 | 0.23% | unattested |
| FN4 | - layer `Article V` on `ccr-8a588c96-jf76ei`: 9 files cite it (trace-id 8, anchor 1); verdict undeclared; titled "The Human & Delegation" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:309 | 0.23% | unattested |
| FN5 | - layer `Article V` on `claude/agent-instruction-files`: 8 files cite it (trace-id 8); verdict undeclared; titled "The Human & Delegation" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:310 | 0.23% | unattested |
| FN6 | - layer `Article V` on `claude/ai-model-smoothing-gentrification-alc5dm`: 8 files cite it (trace-id 8); verdict undeclared; titled "The Human & Delegation" on its law (Draft 0.8, blob `c6343c7`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:311 | 0.25% | unattested |
| FO1 | - layer `V.1` on `master`: 0 files cite it; verdict undeclared; titled "Reserved decisions" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:315 | 0.17% | unattested |
| FO2 | - layer `V.1` on `ccr-392b8b73-v809qu`: 0 files cite it; verdict undeclared; titled "Reserved decisions" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:316 | 0.18% | unattested |
| FO3 | - layer `V.1` on `ccr-542b5884-0deee5`: 0 files cite it; verdict undeclared; titled "Reserved decisions" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:317 | 0.18% | unattested |
| FO4 | - layer `V.1` on `ccr-8a588c96-jf76ei`: 0 files cite it; verdict undeclared; titled "Reserved decisions" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:318 | 0.18% | unattested |
| FO5 | - layer `V.1` on `claude/agent-instruction-files`: 0 files cite it; verdict undeclared; titled "Reserved decisions" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:319 | 0.20% | unattested |
| FO6 | - layer `V.1` on `claude/ai-model-smoothing-gentrification-alc5dm`: 0 files cite it; verdict undeclared; titled "Reserved decisions" on its law (Draft 0.8, blob `c6343c7`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:320 | 0.22% | unattested |
| FP1 | - layer `V.2` on `master`: 0 files cite it; verdict undeclared; titled "Delegation is bounded and revocable" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:324 | 0.19% | unattested |
| FP2 | - layer `V.2` on `ccr-392b8b73-v809qu`: 0 files cite it; verdict undeclared; titled "Delegation is bounded and revocable" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:325 | 0.21% | unattested |
| FP3 | - layer `V.2` on `ccr-542b5884-0deee5`: 0 files cite it; verdict undeclared; titled "Delegation is bounded and revocable" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:326 | 0.21% | unattested |
| FP4 | - layer `V.2` on `ccr-8a588c96-jf76ei`: 0 files cite it; verdict undeclared; titled "Delegation is bounded and revocable" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:327 | 0.21% | unattested |
| FP5 | - layer `V.2` on `claude/agent-instruction-files`: 0 files cite it; verdict undeclared; titled "Delegation is bounded and revocable" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:328 | 0.22% | unattested |
| FP6 | - layer `V.2` on `claude/ai-model-smoothing-gentrification-alc5dm`: 0 files cite it; verdict undeclared; titled "Delegation is bounded and revocable" on its law (Draft 0.8, blob `c6343c7`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:329 | 0.24% | unattested |
| FQ1 | - layer `V.3` on `master`: 0 files cite it; verdict undeclared; titled "Stepping back, and succession" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:333 | 0.18% | unattested |
| FQ2 | - layer `V.3` on `ccr-392b8b73-v809qu`: 0 files cite it; verdict undeclared; titled "Stepping back, and succession" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:334 | 0.20% | unattested |
| FQ3 | - layer `V.3` on `ccr-542b5884-0deee5`: 0 files cite it; verdict undeclared; titled "Stepping back, and succession" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:335 | 0.20% | unattested |
| FQ4 | - layer `V.3` on `ccr-8a588c96-jf76ei`: 0 files cite it; verdict undeclared; titled "Stepping back, and succession" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:336 | 0.20% | unattested |
| FQ5 | - layer `V.3` on `claude/agent-instruction-files`: 0 files cite it; verdict undeclared; titled "Stepping back, and succession" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:337 | 0.21% | unattested |
| FQ6 | - layer `V.3` on `claude/ai-model-smoothing-gentrification-alc5dm`: 0 files cite it; verdict undeclared; titled "Stepping back, and succession" on its law (Draft 0.8, blob `c6343c7`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:338 | 0.23% | unattested |
| FR1 | - layer `V.4` on `master`: 0 files cite it; verdict undeclared; titled "Operator Incapacity" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:342 | 0.17% | unattested |
| FR2 | - layer `V.4` on `ccr-392b8b73-v809qu`: 0 files cite it; verdict undeclared; titled "Operator Incapacity" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:343 | 0.19% | unattested |
| FR3 | - layer `V.4` on `ccr-542b5884-0deee5`: 0 files cite it; verdict undeclared; titled "Operator Incapacity" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:344 | 0.19% | unattested |
| FR4 | - layer `V.4` on `ccr-8a588c96-jf76ei`: 0 files cite it; verdict undeclared; titled "Operator Incapacity" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:345 | 0.19% | unattested |
| FR5 | - layer `V.4` on `claude/agent-instruction-files`: 0 files cite it; verdict undeclared; titled "Operator Incapacity" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:346 | 0.20% | unattested |
| FR6 | - layer `V.4` on `claude/ai-model-smoothing-gentrification-alc5dm`: 0 files cite it; verdict undeclared; titled "Operator Incapacity" on its law (Draft 0.8, blob `c6343c7`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:347 | 0.22% | unattested |
| FS1 | - layer `V.4a` on `master`: 1 file cites it (trace-id 1); verdict undeclared; titled "Declaration of Incapacity (the compromised operator)" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:351 | 0.23% | unattested |
| FS2 | - layer `V.4a` on `ccr-392b8b73-v809qu`: 1 file cites it (trace-id 1); verdict undeclared; titled "Declaration of Incapacity (the compromised operator)" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:352 | 0.25% | unattested |
| FS3 | - layer `V.4a` on `ccr-542b5884-0deee5`: 1 file cites it (trace-id 1); verdict undeclared; titled "Declaration of Incapacity (the compromised operator)" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:353 | 0.25% | unattested |
| FS4 | - layer `V.4a` on `ccr-8a588c96-jf76ei`: 1 file cites it (trace-id 1); verdict undeclared; titled "Declaration of Incapacity (the compromised operator)" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:354 | 0.25% | unattested |
| FS5 | - layer `V.4a` on `claude/agent-instruction-files`: 1 file cites it (trace-id 1); verdict undeclared; titled "Declaration of Incapacity (the compromised operator)" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:355 | 0.26% | unattested |
| FS6 | - layer `V.4a` on `claude/ai-model-smoothing-gentrification-alc5dm`: 1 file cites it (trace-id 1); verdict undeclared; titled "Declaration of Incapacity (the compromised operator)" on its law (Draft 0.8, blob `c6343c7`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:356 | 0.28% | unattested |
| FT1 | - layer `V.4b` on `master`: 0 files cite it; verdict undeclared; titled "Hold" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:360 | 0.15% | unattested |
| FT2 | - layer `V.4b` on `ccr-392b8b73-v809qu`: 0 files cite it; verdict undeclared; titled "Hold" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:361 | 0.17% | unattested |
| FT3 | - layer `V.4b` on `ccr-542b5884-0deee5`: 0 files cite it; verdict undeclared; titled "Hold" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:362 | 0.17% | unattested |
| FT4 | - layer `V.4b` on `ccr-8a588c96-jf76ei`: 0 files cite it; verdict undeclared; titled "Hold" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:363 | 0.17% | unattested |
| FT5 | - layer `V.4b` on `claude/agent-instruction-files`: 0 files cite it; verdict undeclared; titled "Hold" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:364 | 0.18% | unattested |
| FT6 | - layer `V.4b` on `claude/ai-model-smoothing-gentrification-alc5dm`: not a clause of this branch's law (Draft 0.8, blob `c6343c7`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:365 | 0.17% | unattested |
| FU1 | - layer `V.5` on `master`: 0 files cite it; verdict undeclared; titled "The Duty to Disobey" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:369 | 0.17% | unattested |
| FU2 | - layer `V.5` on `ccr-392b8b73-v809qu`: 0 files cite it; verdict undeclared; titled "The Duty to Disobey" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:370 | 0.19% | unattested |
| FU3 | - layer `V.5` on `ccr-542b5884-0deee5`: 0 files cite it; verdict undeclared; titled "The Duty to Disobey" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:371 | 0.19% | unattested |
| FU4 | - layer `V.5` on `ccr-8a588c96-jf76ei`: 0 files cite it; verdict undeclared; titled "The Duty to Disobey" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:372 | 0.19% | unattested |
| FU5 | - layer `V.5` on `claude/agent-instruction-files`: 0 files cite it; verdict undeclared; titled "The Duty to Disobey" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:373 | 0.20% | unattested |
| FU6 | - layer `V.5` on `claude/ai-model-smoothing-gentrification-alc5dm`: 0 files cite it; verdict undeclared; titled "The Duty to Disobey" on its law (Draft 0.8, blob `c6343c7`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:374 | 0.22% | unattested |
| FV1 | - layer `V.6` on `master`: 0 files cite it; verdict undeclared; titled "Offers, not acts" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:378 | 0.17% | unattested |
| FV2 | - layer `V.6` on `ccr-392b8b73-v809qu`: 0 files cite it; verdict undeclared; titled "Offers, not acts" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:379 | 0.18% | unattested |
| FV3 | - layer `V.6` on `ccr-542b5884-0deee5`: 0 files cite it; verdict undeclared; titled "Offers, not acts" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:380 | 0.18% | unattested |
| FV4 | - layer `V.6` on `ccr-8a588c96-jf76ei`: 0 files cite it; verdict undeclared; titled "Offers, not acts" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:381 | 0.18% | unattested |
| FV5 | - layer `V.6` on `claude/agent-instruction-files`: 0 files cite it; verdict undeclared; titled "Offers, not acts" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:382 | 0.20% | unattested |
| FV6 | - layer `V.6` on `claude/ai-model-smoothing-gentrification-alc5dm`: not a clause of this branch's law (Draft 0.8, blob `c6343c7`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:383 | 0.17% | unattested |
| FW1 | - layer `V.7` on `master`: 0 files cite it; verdict undeclared; titled "Attention belongs to the human" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:387 | 0.18% | unattested |
| FW2 | - layer `V.7` on `ccr-392b8b73-v809qu`: 0 files cite it; verdict undeclared; titled "Attention belongs to the human" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:388 | 0.20% | unattested |
| FW3 | - layer `V.7` on `ccr-542b5884-0deee5`: 0 files cite it; verdict undeclared; titled "Attention belongs to the human" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:389 | 0.20% | unattested |
| FW4 | - layer `V.7` on `ccr-8a588c96-jf76ei`: 0 files cite it; verdict undeclared; titled "Attention belongs to the human" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:390 | 0.20% | unattested |
| FW5 | - layer `V.7` on `claude/agent-instruction-files`: 0 files cite it; verdict undeclared; titled "Attention belongs to the human" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:391 | 0.21% | unattested |
| FW6 | - layer `V.7` on `claude/ai-model-smoothing-gentrification-alc5dm`: not a clause of this branch's law (Draft 0.8, blob `c6343c7`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:392 | 0.17% | unattested |
| FX1 | - layer `V.8` on `master`: 0 files cite it; verdict undeclared; titled "Escalation Budget" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:396 | 0.17% | unattested |
| FX2 | - layer `V.8` on `ccr-392b8b73-v809qu`: 0 files cite it; verdict undeclared; titled "Escalation Budget" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:397 | 0.18% | unattested |
| FX3 | - layer `V.8` on `ccr-542b5884-0deee5`: 0 files cite it; verdict undeclared; titled "Escalation Budget" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:398 | 0.18% | unattested |
| FX4 | - layer `V.8` on `ccr-8a588c96-jf76ei`: 0 files cite it; verdict undeclared; titled "Escalation Budget" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:399 | 0.18% | unattested |
| FX5 | - layer `V.8` on `claude/agent-instruction-files`: 0 files cite it; verdict undeclared; titled "Escalation Budget" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:400 | 0.20% | unattested |
| FX6 | - layer `V.8` on `claude/ai-model-smoothing-gentrification-alc5dm`: not a clause of this branch's law (Draft 0.8, blob `c6343c7`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:401 | 0.17% | unattested |
| FY1 | - layer `V.9` on `master`: 0 files cite it; verdict undeclared; titled "Backpressure is reported state" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:405 | 0.18% | unattested |
| FY2 | - layer `V.9` on `ccr-392b8b73-v809qu`: 0 files cite it; verdict undeclared; titled "Backpressure is reported state" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:406 | 0.20% | unattested |
| FY3 | - layer `V.9` on `ccr-542b5884-0deee5`: 0 files cite it; verdict undeclared; titled "Backpressure is reported state" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:407 | 0.20% | unattested |
| FY4 | - layer `V.9` on `ccr-8a588c96-jf76ei`: 0 files cite it; verdict undeclared; titled "Backpressure is reported state" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:408 | 0.20% | unattested |
| FY5 | - layer `V.9` on `claude/agent-instruction-files`: 0 files cite it; verdict undeclared; titled "Backpressure is reported state" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:409 | 0.21% | unattested |
| FY6 | - layer `V.9` on `claude/ai-model-smoothing-gentrification-alc5dm`: not a clause of this branch's law (Draft 0.8, blob `c6343c7`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:410 | 0.17% | unattested |
| FZ1 | - layer `Article VI` on `master`: 15 files cite it (trace-id 15); verdict undeclared; titled "The Record" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:414 | 0.19% | unattested |
| FZ2 | - layer `Article VI` on `ccr-392b8b73-v809qu`: 17 files cite it (trace-id 17, anchor 1); verdict undeclared; titled "The Record" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:415 | 0.22% | unattested |
| FZ3 | - layer `Article VI` on `ccr-542b5884-0deee5`: 16 files cite it (trace-id 15, anchor 1); verdict undeclared; titled "The Record" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:416 | 0.22% | unattested |
| FZ4 | - layer `Article VI` on `ccr-8a588c96-jf76ei`: 16 files cite it (trace-id 15, anchor 1); verdict undeclared; titled "The Record" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:417 | 0.22% | unattested |
| FZ5 | - layer `Article VI` on `claude/agent-instruction-files`: 15 files cite it (trace-id 15); verdict undeclared; titled "The Record" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:418 | 0.22% | unattested |
| FZ6 | - layer `Article VI` on `claude/ai-model-smoothing-gentrification-alc5dm`: 12 files cite it (trace-id 12); verdict undeclared; titled "The Record" on its law (Draft 0.8, blob `c6343c7`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:419 | 0.24% | unattested |
| GA1 | - layer `VI.1` on `master`: 1 file cites it (trace-id 1); verdict undeclared; titled "Append and read, by standing" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:423 | 0.20% | unattested |
| GA2 | - layer `VI.1` on `ccr-392b8b73-v809qu`: 2 files cite it (trace-id 2); verdict undeclared; titled "Append and read, by standing" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:424 | 0.22% | unattested |
| GA3 | - layer `VI.1` on `ccr-542b5884-0deee5`: 1 file cites it (trace-id 1); verdict undeclared; titled "Append and read, by standing" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:425 | 0.22% | unattested |
| GA4 | - layer `VI.1` on `ccr-8a588c96-jf76ei`: 1 file cites it (trace-id 1); verdict undeclared; titled "Append and read, by standing" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:426 | 0.22% | unattested |
| GA5 | - layer `VI.1` on `claude/agent-instruction-files`: 1 file cites it (trace-id 1); verdict undeclared; titled "Append and read, by standing" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:427 | 0.23% | unattested |
| GA6 | - layer `VI.1` on `claude/ai-model-smoothing-gentrification-alc5dm`: 1 file cites it (trace-id 1); verdict undeclared; titled "Append and read, by standing" on its law (Draft 0.8, blob `c6343c7`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:428 | 0.25% | unattested |
| GB1 | - layer `VI.2` on `master`: 0 files cite it; verdict undeclared; titled "Content is inviolable" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:432 | 0.17% | unattested |
| GB2 | - layer `VI.2` on `ccr-392b8b73-v809qu`: 0 files cite it; verdict undeclared; titled "Content is inviolable" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:433 | 0.19% | unattested |
| GB3 | - layer `VI.2` on `ccr-542b5884-0deee5`: 0 files cite it; verdict undeclared; titled "Content is inviolable" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:434 | 0.19% | unattested |
| GB4 | - layer `VI.2` on `ccr-8a588c96-jf76ei`: 0 files cite it; verdict undeclared; titled "Content is inviolable" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:435 | 0.19% | unattested |
| GB5 | - layer `VI.2` on `claude/agent-instruction-files`: 0 files cite it; verdict undeclared; titled "Content is inviolable" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:436 | 0.20% | unattested |
| GB6 | - layer `VI.2` on `claude/ai-model-smoothing-gentrification-alc5dm`: 0 files cite it; verdict undeclared; titled "Content is inviolable" on its law (Draft 0.8, blob `c6343c7`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:437 | 0.23% | unattested |
| GC1 | - layer `VI.3` on `master`: 0 files cite it; verdict undeclared; titled "The split-brain problem" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:441 | 0.18% | unattested |
| GC2 | - layer `VI.3` on `ccr-392b8b73-v809qu`: 0 files cite it; verdict undeclared; titled "The split-brain problem" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:442 | 0.19% | unattested |
| GC3 | - layer `VI.3` on `ccr-542b5884-0deee5`: 0 files cite it; verdict undeclared; titled "The split-brain problem" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:443 | 0.19% | unattested |
| GC4 | - layer `VI.3` on `ccr-8a588c96-jf76ei`: 0 files cite it; verdict undeclared; titled "The split-brain problem" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:444 | 0.19% | unattested |
| GC5 | - layer `VI.3` on `claude/agent-instruction-files`: 0 files cite it; verdict undeclared; titled "The split-brain problem" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:445 | 0.21% | unattested |
| GC6 | - layer `VI.3` on `claude/ai-model-smoothing-gentrification-alc5dm`: 0 files cite it; verdict undeclared; titled "The split-brain problem" on its law (Draft 0.8, blob `c6343c7`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:446 | 0.23% | unattested |
| GD1 | - layer `VI.4` on `master`: 1 file cites it (trace-id 1); verdict undeclared; titled "The auditor is not the actor" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:450 | 0.20% | unattested |
| GD2 | - layer `VI.4` on `ccr-392b8b73-v809qu`: 1 file cites it (trace-id 1); verdict undeclared; titled "The auditor is not the actor" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:451 | 0.22% | unattested |
| GD3 | - layer `VI.4` on `ccr-542b5884-0deee5`: 1 file cites it (trace-id 1); verdict undeclared; titled "The auditor is not the actor" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:452 | 0.22% | unattested |
| GD4 | - layer `VI.4` on `ccr-8a588c96-jf76ei`: 1 file cites it (trace-id 1); verdict undeclared; titled "The auditor is not the actor" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:453 | 0.22% | unattested |
| GD5 | - layer `VI.4` on `claude/agent-instruction-files`: 1 file cites it (trace-id 1); verdict undeclared; titled "The auditor is not the actor" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:454 | 0.23% | unattested |
| GD6 | - layer `VI.4` on `claude/ai-model-smoothing-gentrification-alc5dm`: 1 file cites it (trace-id 1); verdict undeclared; titled "The auditor is not the actor" on its law (Draft 0.8, blob `c6343c7`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:455 | 0.25% | unattested |
| GE1 | - layer `VI.5` on `master`: 1 file cites it (trace-id 1); verdict undeclared; titled "Unanimity is recorded as a property, not assumed as a quality" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:459 | 0.24% | unattested |
| GE2 | - layer `VI.5` on `ccr-392b8b73-v809qu`: 1 file cites it (trace-id 1); verdict undeclared; titled "Unanimity is recorded as a property, not assumed as a quality" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:460 | 0.26% | unattested |
| GE3 | - layer `VI.5` on `ccr-542b5884-0deee5`: 1 file cites it (trace-id 1); verdict undeclared; titled "Unanimity is recorded as a property, not assumed as a quality" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:461 | 0.26% | unattested |
| GE4 | - layer `VI.5` on `ccr-8a588c96-jf76ei`: 1 file cites it (trace-id 1); verdict undeclared; titled "Unanimity is recorded as a property, not assumed as a quality" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:462 | 0.26% | unattested |
| GE5 | - layer `VI.5` on `claude/agent-instruction-files`: 1 file cites it (trace-id 1); verdict undeclared; titled "Unanimity is recorded as a property, not assumed as a quality" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:463 | 0.27% | unattested |
| GE6 | - layer `VI.5` on `claude/ai-model-smoothing-gentrification-alc5dm`: not a clause of this branch's law (Draft 0.8, blob `c6343c7`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:464 | 0.17% | unattested |
| GF1 | - layer `VI.6` on `master`: 0 files cite it; verdict undeclared; titled "No smoothing" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:468 | 0.16% | unattested |
| GF2 | - layer `VI.6` on `ccr-392b8b73-v809qu`: 0 files cite it; verdict undeclared; titled "No smoothing" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:469 | 0.18% | unattested |
| GF3 | - layer `VI.6` on `ccr-542b5884-0deee5`: 0 files cite it; verdict undeclared; titled "No smoothing" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:470 | 0.18% | unattested |
| GF4 | - layer `VI.6` on `ccr-8a588c96-jf76ei`: 0 files cite it; verdict undeclared; titled "No smoothing" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:471 | 0.18% | unattested |
| GF5 | - layer `VI.6` on `claude/agent-instruction-files`: 0 files cite it; verdict undeclared; titled "No smoothing" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:472 | 0.19% | unattested |
| GF6 | - layer `VI.6` on `claude/ai-model-smoothing-gentrification-alc5dm`: not a clause of this branch's law (Draft 0.8, blob `c6343c7`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:473 | 0.17% | unattested |
| GG1 | - layer `Article VII` on `master`: 5 files cite it (trace-id 5); verdict undeclared; titled "The Interpreter" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:477 | 0.19% | unattested |
| GG2 | - layer `Article VII` on `ccr-392b8b73-v809qu`: 5 files cite it (trace-id 5); verdict undeclared; titled "The Interpreter" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:478 | 0.21% | unattested |
| GG3 | - layer `Article VII` on `ccr-542b5884-0deee5`: 7 files cite it (trace-id 5, anchor 2); verdict undeclared; titled "The Interpreter" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:479 | 0.22% | unattested |
| GG4 | - layer `Article VII` on `ccr-8a588c96-jf76ei`: 7 files cite it (trace-id 5, anchor 2); verdict undeclared; titled "The Interpreter" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:480 | 0.22% | unattested |
| GG5 | - layer `Article VII` on `claude/agent-instruction-files`: 5 files cite it (trace-id 5); verdict undeclared; titled "The Interpreter" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:481 | 0.22% | unattested |
| GG6 | - layer `Article VII` on `claude/ai-model-smoothing-gentrification-alc5dm`: 5 files cite it (trace-id 5); verdict undeclared; titled "The Interpreter" on its law (Draft 0.8, blob `c6343c7`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:482 | 0.24% | unattested |
| GH1 | - layer `VII.default` on `master`: 1 file cites it (trace-id 1); verdict undeclared; titled "Escalation holds the seat" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:486 | 0.20% | unattested |
| GH2 | - layer `VII.default` on `ccr-392b8b73-v809qu`: 1 file cites it (trace-id 1); verdict undeclared; titled "Escalation holds the seat" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:487 | 0.22% | unattested |
| GH3 | - layer `VII.default` on `ccr-542b5884-0deee5`: 1 file cites it (trace-id 1); verdict undeclared; titled "Escalation holds the seat" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:488 | 0.22% | unattested |
| GH4 | - layer `VII.default` on `ccr-8a588c96-jf76ei`: 1 file cites it (trace-id 1); verdict undeclared; titled "Escalation holds the seat" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:489 | 0.22% | unattested |
| GH5 | - layer `VII.default` on `claude/agent-instruction-files`: 1 file cites it (trace-id 1); verdict undeclared; titled "Escalation holds the seat" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:490 | 0.23% | unattested |
| GH6 | - layer `VII.default` on `claude/ai-model-smoothing-gentrification-alc5dm`: 1 file cites it (trace-id 1); verdict undeclared; titled "Escalation holds the seat" on its law (Draft 0.8, blob `c6343c7`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:491 | 0.26% | unattested |
| GI1 | - layer `Article VIII` on `master`: 2 files cite it (trace-id 2); verdict undeclared; titled "Amendment" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:495 | 0.18% | unattested |
| GI2 | - layer `Article VIII` on `ccr-392b8b73-v809qu`: 2 files cite it (trace-id 2); verdict undeclared; titled "Amendment" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:496 | 0.20% | unattested |
| GI3 | - layer `Article VIII` on `ccr-542b5884-0deee5`: 2 files cite it (trace-id 2); verdict undeclared; titled "Amendment" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:497 | 0.20% | unattested |
| GI4 | - layer `Article VIII` on `ccr-8a588c96-jf76ei`: 2 files cite it (trace-id 2); verdict undeclared; titled "Amendment" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:498 | 0.20% | unattested |
| GI5 | - layer `Article VIII` on `claude/agent-instruction-files`: 2 files cite it (trace-id 2); verdict undeclared; titled "Amendment" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:499 | 0.22% | unattested |
| GI6 | - layer `Article VIII` on `claude/ai-model-smoothing-gentrification-alc5dm`: 2 files cite it (trace-id 2); verdict undeclared; titled "Amendment" on its law (Draft 0.8, blob `c6343c7`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:500 | 0.24% | unattested |
| GJ1 | - layer `VIII.1` on `master`: 1 file cites it (trace-id 1); verdict undeclared; titled "Propose, weigh, ratify" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:504 | 0.19% | unattested |
| GJ2 | - layer `VIII.1` on `ccr-392b8b73-v809qu`: 1 file cites it (trace-id 1); verdict undeclared; titled "Propose, weigh, ratify" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:505 | 0.21% | unattested |
| GJ3 | - layer `VIII.1` on `ccr-542b5884-0deee5`: 1 file cites it (trace-id 1); verdict undeclared; titled "Propose, weigh, ratify" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:506 | 0.21% | unattested |
| GJ4 | - layer `VIII.1` on `ccr-8a588c96-jf76ei`: 1 file cites it (trace-id 1); verdict undeclared; titled "Propose, weigh, ratify" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:507 | 0.21% | unattested |
| GJ5 | - layer `VIII.1` on `claude/agent-instruction-files`: 1 file cites it (trace-id 1); verdict undeclared; titled "Propose, weigh, ratify" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:508 | 0.22% | unattested |
| GJ6 | - layer `VIII.1` on `claude/ai-model-smoothing-gentrification-alc5dm`: 1 file cites it (trace-id 1); verdict undeclared; titled "Propose, weigh, ratify" on its law (Draft 0.8, blob `c6343c7`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:509 | 0.25% | unattested |
| GK1 | - layer `VIII.2` on `master`: 0 files cite it; verdict undeclared; titled "Emergency amendment is a bounded envelope" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:513 | 0.20% | unattested |
| GK2 | - layer `VIII.2` on `ccr-392b8b73-v809qu`: 0 files cite it; verdict undeclared; titled "Emergency amendment is a bounded envelope" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:514 | 0.22% | unattested |
| GK3 | - layer `VIII.2` on `ccr-542b5884-0deee5`: 0 files cite it; verdict undeclared; titled "Emergency amendment is a bounded envelope" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:515 | 0.22% | unattested |
| GK4 | - layer `VIII.2` on `ccr-8a588c96-jf76ei`: 0 files cite it; verdict undeclared; titled "Emergency amendment is a bounded envelope" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:516 | 0.22% | unattested |
| GK5 | - layer `VIII.2` on `claude/agent-instruction-files`: 0 files cite it; verdict undeclared; titled "Emergency amendment is a bounded envelope" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:517 | 0.23% | unattested |
| GK6 | - layer `VIII.2` on `claude/ai-model-smoothing-gentrification-alc5dm`: 0 files cite it; verdict undeclared; titled "Emergency amendment is a bounded envelope" on its law (Draft 0.8, blob `c6343c7`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:518 | 0.25% | unattested |
| GL1 | - layer `VIII.3` on `master`: 0 files cite it; verdict undeclared; titled "Article 0 is beyond reach" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:522 | 0.18% | unattested |
| GL2 | - layer `VIII.3` on `ccr-392b8b73-v809qu`: 0 files cite it; verdict undeclared; titled "Article 0 is beyond reach" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:523 | 0.20% | unattested |
| GL3 | - layer `VIII.3` on `ccr-542b5884-0deee5`: 0 files cite it; verdict undeclared; titled "Article 0 is beyond reach" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:524 | 0.20% | unattested |
| GL4 | - layer `VIII.3` on `ccr-8a588c96-jf76ei`: 0 files cite it; verdict undeclared; titled "Article 0 is beyond reach" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:525 | 0.20% | unattested |
| GL5 | - layer `VIII.3` on `claude/agent-instruction-files`: 0 files cite it; verdict undeclared; titled "Article 0 is beyond reach" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:526 | 0.21% | unattested |
| GL6 | - layer `VIII.3` on `claude/ai-model-smoothing-gentrification-alc5dm`: 0 files cite it; verdict undeclared; titled "Article 0 is beyond reach" on its law (Draft 0.8, blob `c6343c7`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:527 | 0.23% | unattested |
| GM1 | - layer `Article IX` on `master`: 2 files cite it (trace-id 2); verdict undeclared; titled "Ratification & Founding" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:531 | 0.20% | unattested |
| GM2 | - layer `Article IX` on `ccr-392b8b73-v809qu`: 2 files cite it (trace-id 2); verdict undeclared; titled "Ratification & Founding" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:532 | 0.22% | unattested |
| GM3 | - layer `Article IX` on `ccr-542b5884-0deee5`: 2 files cite it (trace-id 2); verdict undeclared; titled "Ratification & Founding" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:533 | 0.22% | unattested |
| GM4 | - layer `Article IX` on `ccr-8a588c96-jf76ei`: 2 files cite it (trace-id 2); verdict undeclared; titled "Ratification & Founding" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:534 | 0.22% | unattested |
| GM5 | - layer `Article IX` on `claude/agent-instruction-files`: 2 files cite it (trace-id 2); verdict undeclared; titled "Ratification & Founding" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:535 | 0.23% | unattested |
| GM6 | - layer `Article IX` on `claude/ai-model-smoothing-gentrification-alc5dm`: 2 files cite it (trace-id 2); verdict undeclared; titled "Ratification & Founding" on its law (Draft 0.8, blob `c6343c7`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:536 | 0.25% | unattested |
| GN1 | - layer `IX.1` on `master`: 0 files cite it; verdict undeclared; titled "The genesis act" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:540 | 0.17% | unattested |
| GN2 | - layer `IX.1` on `ccr-392b8b73-v809qu`: 0 files cite it; verdict undeclared; titled "The genesis act" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:541 | 0.18% | unattested |
| GN3 | - layer `IX.1` on `ccr-542b5884-0deee5`: 0 files cite it; verdict undeclared; titled "The genesis act" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:542 | 0.18% | unattested |
| GN4 | - layer `IX.1` on `ccr-8a588c96-jf76ei`: 0 files cite it; verdict undeclared; titled "The genesis act" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:543 | 0.18% | unattested |
| GN5 | - layer `IX.1` on `claude/agent-instruction-files`: 0 files cite it; verdict undeclared; titled "The genesis act" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:544 | 0.20% | unattested |
| GN6 | - layer `IX.1` on `claude/ai-model-smoothing-gentrification-alc5dm`: 0 files cite it; verdict undeclared; titled "The genesis act" on its law (Draft 0.8, blob `c6343c7`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:545 | 0.22% | unattested |
| GO1 | - layer `IX.2` on `master`: 0 files cite it; verdict undeclared; titled "Witnesses and assent" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:549 | 0.17% | unattested |
| GO2 | - layer `IX.2` on `ccr-392b8b73-v809qu`: 0 files cite it; verdict undeclared; titled "Witnesses and assent" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:550 | 0.19% | unattested |
| GO3 | - layer `IX.2` on `ccr-542b5884-0deee5`: 0 files cite it; verdict undeclared; titled "Witnesses and assent" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:551 | 0.19% | unattested |
| GO4 | - layer `IX.2` on `ccr-8a588c96-jf76ei`: 0 files cite it; verdict undeclared; titled "Witnesses and assent" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:552 | 0.19% | unattested |
| GO5 | - layer `IX.2` on `claude/agent-instruction-files`: 0 files cite it; verdict undeclared; titled "Witnesses and assent" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:553 | 0.20% | unattested |
| GO6 | - layer `IX.2` on `claude/ai-model-smoothing-gentrification-alc5dm`: 0 files cite it; verdict undeclared; titled "Witnesses and assent" on its law (Draft 0.8, blob `c6343c7`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:554 | 0.22% | unattested |
| GP1 | - layer `IX.3` on `master`: 0 files cite it; verdict undeclared; titled "Adoption and forking" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:558 | 0.17% | unattested |
| GP2 | - layer `IX.3` on `ccr-392b8b73-v809qu`: 0 files cite it; verdict undeclared; titled "Adoption and forking" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:559 | 0.19% | unattested |
| GP3 | - layer `IX.3` on `ccr-542b5884-0deee5`: 0 files cite it; verdict undeclared; titled "Adoption and forking" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:560 | 0.19% | unattested |
| GP4 | - layer `IX.3` on `ccr-8a588c96-jf76ei`: 0 files cite it; verdict undeclared; titled "Adoption and forking" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:561 | 0.19% | unattested |
| GP5 | - layer `IX.3` on `claude/agent-instruction-files`: 0 files cite it; verdict undeclared; titled "Adoption and forking" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:562 | 0.20% | unattested |
| GP6 | - layer `IX.3` on `claude/ai-model-smoothing-gentrification-alc5dm`: 0 files cite it; verdict undeclared; titled "Adoption and forking" on its law (Draft 0.8, blob `c6343c7`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:563 | 0.22% | unattested |
| GQ1 | - layer `IX.4` on `master`: 0 files cite it; verdict undeclared; titled "Succession out of Safe Mode" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:567 | 0.18% | unattested |
| GQ2 | - layer `IX.4` on `ccr-392b8b73-v809qu`: 0 files cite it; verdict undeclared; titled "Succession out of Safe Mode" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:568 | 0.20% | unattested |
| GQ3 | - layer `IX.4` on `ccr-542b5884-0deee5`: 0 files cite it; verdict undeclared; titled "Succession out of Safe Mode" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:569 | 0.20% | unattested |
| GQ4 | - layer `IX.4` on `ccr-8a588c96-jf76ei`: 0 files cite it; verdict undeclared; titled "Succession out of Safe Mode" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:570 | 0.20% | unattested |
| GQ5 | - layer `IX.4` on `claude/agent-instruction-files`: 0 files cite it; verdict undeclared; titled "Succession out of Safe Mode" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:571 | 0.21% | unattested |
| GQ6 | - layer `IX.4` on `claude/ai-model-smoothing-gentrification-alc5dm`: 0 files cite it; verdict undeclared; titled "Succession out of Safe Mode" on its law (Draft 0.8, blob `c6343c7`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:572 | 0.23% | unattested |
| GR1 | - layer `Article X` on `master`: 5 files cite it (trace-id 5); verdict undeclared; titled "Supremacy and Severability" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:576 | 0.20% | unattested |
| GR2 | - layer `Article X` on `ccr-392b8b73-v809qu`: 5 files cite it (trace-id 5); verdict undeclared; titled "Supremacy and Severability" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:577 | 0.22% | unattested |
| GR3 | - layer `Article X` on `ccr-542b5884-0deee5`: 6 files cite it (trace-id 5, anchor 1); verdict undeclared; titled "Supremacy and Severability" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:578 | 0.23% | unattested |
| GR4 | - layer `Article X` on `ccr-8a588c96-jf76ei`: 6 files cite it (trace-id 5, anchor 1); verdict undeclared; titled "Supremacy and Severability" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:579 | 0.23% | unattested |
| GR5 | - layer `Article X` on `claude/agent-instruction-files`: 5 files cite it (trace-id 5); verdict undeclared; titled "Supremacy and Severability" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:580 | 0.23% | unattested |
| GR6 | - layer `Article X` on `claude/ai-model-smoothing-gentrification-alc5dm`: 5 files cite it (trace-id 5); verdict undeclared; titled "Supremacy and Severability" on its law (Draft 0.8, blob `c6343c7`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:581 | 0.26% | unattested |
| GS1 | - layer `X.1` on `master`: 0 files cite it; verdict undeclared; titled "Supremacy" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:585 | 0.16% | unattested |
| GS2 | - layer `X.1` on `ccr-392b8b73-v809qu`: 0 files cite it; verdict undeclared; titled "Supremacy" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:586 | 0.17% | unattested |
| GS3 | - layer `X.1` on `ccr-542b5884-0deee5`: 0 files cite it; verdict undeclared; titled "Supremacy" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:587 | 0.17% | unattested |
| GS4 | - layer `X.1` on `ccr-8a588c96-jf76ei`: 0 files cite it; verdict undeclared; titled "Supremacy" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:588 | 0.17% | unattested |
| GS5 | - layer `X.1` on `claude/agent-instruction-files`: 0 files cite it; verdict undeclared; titled "Supremacy" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:589 | 0.19% | unattested |
| GS6 | - layer `X.1` on `claude/ai-model-smoothing-gentrification-alc5dm`: 0 files cite it; verdict undeclared; titled "Supremacy" on its law (Draft 0.8, blob `c6343c7`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:590 | 0.21% | unattested |
| GT1 | - layer `X.2` on `master`: 0 files cite it; verdict undeclared; titled "Severability" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:594 | 0.16% | unattested |
| GT2 | - layer `X.2` on `ccr-392b8b73-v809qu`: 0 files cite it; verdict undeclared; titled "Severability" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:595 | 0.18% | unattested |
| GT3 | - layer `X.2` on `ccr-542b5884-0deee5`: 0 files cite it; verdict undeclared; titled "Severability" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:596 | 0.18% | unattested |
| GT4 | - layer `X.2` on `ccr-8a588c96-jf76ei`: 0 files cite it; verdict undeclared; titled "Severability" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:597 | 0.18% | unattested |
| GT5 | - layer `X.2` on `claude/agent-instruction-files`: 0 files cite it; verdict undeclared; titled "Severability" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:598 | 0.19% | unattested |
| GT6 | - layer `X.2` on `claude/ai-model-smoothing-gentrification-alc5dm`: 0 files cite it; verdict undeclared; titled "Severability" on its law (Draft 0.8, blob `c6343c7`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:599 | 0.21% | unattested |
| GU1 | - layer `X.3` on `master`: 0 files cite it; verdict undeclared; titled "Duty to Disobey (formalized)" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:603 | 0.18% | unattested |
| GU2 | - layer `X.3` on `ccr-392b8b73-v809qu`: 0 files cite it; verdict undeclared; titled "Duty to Disobey (formalized)" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:604 | 0.20% | unattested |
| GU3 | - layer `X.3` on `ccr-542b5884-0deee5`: 0 files cite it; verdict undeclared; titled "Duty to Disobey (formalized)" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:605 | 0.20% | unattested |
| GU4 | - layer `X.3` on `ccr-8a588c96-jf76ei`: 0 files cite it; verdict undeclared; titled "Duty to Disobey (formalized)" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:606 | 0.20% | unattested |
| GU5 | - layer `X.3` on `claude/agent-instruction-files`: 0 files cite it; verdict undeclared; titled "Duty to Disobey (formalized)" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:607 | 0.21% | unattested |
| GU6 | - layer `X.3` on `claude/ai-model-smoothing-gentrification-alc5dm`: 0 files cite it; verdict undeclared; titled "Duty to Disobey (formalized)" on its law (Draft 0.8, blob `c6343c7`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:608 | 0.23% | unattested |
| GV1 | - layer `X.4` on `master`: 5 files cite it (trace-id 5); verdict differently; titled "The Concurrence Rule" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:612 | 0.19% | unattested |
| GV2 | - layer `X.4` on `ccr-392b8b73-v809qu`: 5 files cite it (trace-id 5); verdict differently; titled "The Concurrence Rule" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:613 | 0.21% | unattested |
| GV3 | - layer `X.4` on `ccr-542b5884-0deee5`: 5 files cite it (trace-id 5); verdict differently; titled "The Concurrence Rule" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:614 | 0.21% | unattested |
| GV4 | - layer `X.4` on `ccr-8a588c96-jf76ei`: 5 files cite it (trace-id 5); verdict differently; titled "The Concurrence Rule" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:615 | 0.21% | unattested |
| GV5 | - layer `X.4` on `claude/agent-instruction-files`: 5 files cite it (trace-id 5); verdict differently; titled "The Concurrence Rule" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:616 | 0.22% | unattested |
| GV6 | - layer `X.4` on `claude/ai-model-smoothing-gentrification-alc5dm`: 4 files cite it (trace-id 4); verdict differently; titled "The Concurrence Rule" on its law (Draft 0.8, blob `c6343c7`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:617 | 0.24% | unattested |
| GW1 | - layer `X.4a` on `master`: 0 files cite it; verdict undeclared; titled "Closed, and loud" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:621 | 0.17% | unattested |
| GW2 | - layer `X.4a` on `ccr-392b8b73-v809qu`: 0 files cite it; verdict undeclared; titled "Closed, and loud" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:622 | 0.18% | unattested |
| GW3 | - layer `X.4a` on `ccr-542b5884-0deee5`: 0 files cite it; verdict undeclared; titled "Closed, and loud" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:623 | 0.18% | unattested |
| GW4 | - layer `X.4a` on `ccr-8a588c96-jf76ei`: 0 files cite it; verdict undeclared; titled "Closed, and loud" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:624 | 0.18% | unattested |
| GW5 | - layer `X.4a` on `claude/agent-instruction-files`: 0 files cite it; verdict undeclared; titled "Closed, and loud" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:625 | 0.20% | unattested |
| GW6 | - layer `X.4a` on `claude/ai-model-smoothing-gentrification-alc5dm`: not a clause of this branch's law (Draft 0.8, blob `c6343c7`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:626 | 0.17% | unattested |
| GX1 | - layer `Article XI` on `master`: 6 files cite it (trace-id 6); verdict undeclared; titled "Constitutional Review" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:630 | 0.20% | unattested |
| GX2 | - layer `Article XI` on `ccr-392b8b73-v809qu`: 7 files cite it (trace-id 7); verdict undeclared; titled "Constitutional Review" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:631 | 0.21% | unattested |
| GX3 | - layer `Article XI` on `ccr-542b5884-0deee5`: 6 files cite it (trace-id 6); verdict undeclared; titled "Constitutional Review" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:632 | 0.21% | unattested |
| GX4 | - layer `Article XI` on `ccr-8a588c96-jf76ei`: 6 files cite it (trace-id 6); verdict undeclared; titled "Constitutional Review" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:633 | 0.21% | unattested |
| GX5 | - layer `Article XI` on `claude/agent-instruction-files`: 6 files cite it (trace-id 6); verdict undeclared; titled "Constitutional Review" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:634 | 0.23% | unattested |
| GX6 | - layer `Article XI` on `claude/ai-model-smoothing-gentrification-alc5dm`: 6 files cite it (trace-id 6); verdict undeclared; titled "Constitutional Review" on its law (Draft 0.8, blob `c6343c7`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:635 | 0.25% | unattested |
| GY1 | - layer `XI.1` on `master`: 0 files cite it; verdict undeclared; titled "Who may invoke, and what it suspends" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:639 | 0.19% | unattested |
| GY2 | - layer `XI.1` on `ccr-392b8b73-v809qu`: 0 files cite it; verdict undeclared; titled "Who may invoke, and what it suspends" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:640 | 0.21% | unattested |
| GY3 | - layer `XI.1` on `ccr-542b5884-0deee5`: 0 files cite it; verdict undeclared; titled "Who may invoke, and what it suspends" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:641 | 0.21% | unattested |
| GY4 | - layer `XI.1` on `ccr-8a588c96-jf76ei`: 0 files cite it; verdict undeclared; titled "Who may invoke, and what it suspends" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:642 | 0.21% | unattested |
| GY5 | - layer `XI.1` on `claude/agent-instruction-files`: 0 files cite it; verdict undeclared; titled "Who may invoke, and what it suspends" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:643 | 0.22% | unattested |
| GY6 | - layer `XI.1` on `claude/ai-model-smoothing-gentrification-alc5dm`: 0 files cite it; verdict undeclared; titled "Who may invoke, and what it suspends" on its law (Draft 0.8, blob `c6343c7`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:644 | 0.24% | unattested |
| GZ1 | - layer `XI.2` on `master`: 0 files cite it; verdict undeclared; titled "Resolution is recorded and binding" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:648 | 0.19% | unattested |
| GZ2 | - layer `XI.2` on `ccr-392b8b73-v809qu`: 0 files cite it; verdict undeclared; titled "Resolution is recorded and binding" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:649 | 0.21% | unattested |
| GZ3 | - layer `XI.2` on `ccr-542b5884-0deee5`: 0 files cite it; verdict undeclared; titled "Resolution is recorded and binding" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:650 | 0.21% | unattested |
| GZ4 | - layer `XI.2` on `ccr-8a588c96-jf76ei`: 0 files cite it; verdict undeclared; titled "Resolution is recorded and binding" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:651 | 0.21% | unattested |
| GZ5 | - layer `XI.2` on `claude/agent-instruction-files`: 0 files cite it; verdict undeclared; titled "Resolution is recorded and binding" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:652 | 0.22% | unattested |
| GZ6 | - layer `XI.2` on `claude/ai-model-smoothing-gentrification-alc5dm`: 0 files cite it; verdict undeclared; titled "Resolution is recorded and binding" on its law (Draft 0.8, blob `c6343c7`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:653 | 0.24% | unattested |
| HA1 | - layer `XI.3` on `master`: 0 files cite it; verdict undeclared; titled "Enforcement artifact" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:657 | 0.17% | unattested |
| HA2 | - layer `XI.3` on `ccr-392b8b73-v809qu`: 0 files cite it; verdict undeclared; titled "Enforcement artifact" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:658 | 0.19% | unattested |
| HA3 | - layer `XI.3` on `ccr-542b5884-0deee5`: 0 files cite it; verdict undeclared; titled "Enforcement artifact" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:659 | 0.19% | unattested |
| HA4 | - layer `XI.3` on `ccr-8a588c96-jf76ei`: 0 files cite it; verdict undeclared; titled "Enforcement artifact" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:660 | 0.19% | unattested |
| HA5 | - layer `XI.3` on `claude/agent-instruction-files`: 0 files cite it; verdict undeclared; titled "Enforcement artifact" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:661 | 0.20% | unattested |
| HA6 | - layer `XI.3` on `claude/ai-model-smoothing-gentrification-alc5dm`: 0 files cite it; verdict undeclared; titled "Enforcement artifact" on its law (Draft 0.8, blob `c6343c7`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:662 | 0.22% | unattested |
| HB1 | - layer `Article XII` on `master`: 6 files cite it (trace-id 6); verdict undeclared; titled "Resource Governance" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:666 | 0.20% | unattested |
| HB2 | - layer `Article XII` on `ccr-392b8b73-v809qu`: 6 files cite it (trace-id 6); verdict undeclared; titled "Resource Governance" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:667 | 0.21% | unattested |
| HB3 | - layer `Article XII` on `ccr-542b5884-0deee5`: 7 files cite it (trace-id 6, anchor 1); verdict undeclared; titled "Resource Governance" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:668 | 0.23% | unattested |
| HB4 | - layer `Article XII` on `ccr-8a588c96-jf76ei`: 7 files cite it (trace-id 6, anchor 1); verdict undeclared; titled "Resource Governance" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:669 | 0.23% | unattested |
| HB5 | - layer `Article XII` on `claude/agent-instruction-files`: 6 files cite it (trace-id 6); verdict undeclared; titled "Resource Governance" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:670 | 0.23% | unattested |
| HB6 | - layer `Article XII` on `claude/ai-model-smoothing-gentrification-alc5dm`: 6 files cite it (trace-id 6); verdict undeclared; titled "Resource Governance" on its law (Draft 0.8, blob `c6343c7`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:671 | 0.25% | unattested |
| HC1 | - layer `XII.1` on `master`: 1 file cites it (trace-id 1); verdict undeclared; titled "Allocation is assigned, not seized" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:675 | 0.21% | unattested |
| HC2 | - layer `XII.1` on `ccr-392b8b73-v809qu`: 1 file cites it (trace-id 1); verdict undeclared; titled "Allocation is assigned, not seized" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:676 | 0.22% | unattested |
| HC3 | - layer `XII.1` on `ccr-542b5884-0deee5`: 1 file cites it (trace-id 1); verdict undeclared; titled "Allocation is assigned, not seized" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:677 | 0.22% | unattested |
| HC4 | - layer `XII.1` on `ccr-8a588c96-jf76ei`: 1 file cites it (trace-id 1); verdict undeclared; titled "Allocation is assigned, not seized" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:678 | 0.22% | unattested |
| HC5 | - layer `XII.1` on `claude/agent-instruction-files`: 1 file cites it (trace-id 1); verdict undeclared; titled "Allocation is assigned, not seized" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:679 | 0.24% | unattested |
| HC6 | - layer `XII.1` on `claude/ai-model-smoothing-gentrification-alc5dm`: 1 file cites it (trace-id 1); verdict undeclared; titled "Allocation is assigned, not seized" on its law (Draft 0.8, blob `c6343c7`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:680 | 0.26% | unattested |
| HD1 | - layer `XII.2` on `master`: 1 file cites it (trace-id 1); verdict undeclared; titled "No agent expands its own allocation" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:684 | 0.21% | unattested |
| HD2 | - layer `XII.2` on `ccr-392b8b73-v809qu`: 1 file cites it (trace-id 1); verdict undeclared; titled "No agent expands its own allocation" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:685 | 0.23% | unattested |
| HD3 | - layer `XII.2` on `ccr-542b5884-0deee5`: 1 file cites it (trace-id 1); verdict undeclared; titled "No agent expands its own allocation" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:686 | 0.23% | unattested |
| HD4 | - layer `XII.2` on `ccr-8a588c96-jf76ei`: 1 file cites it (trace-id 1); verdict undeclared; titled "No agent expands its own allocation" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:687 | 0.23% | unattested |
| HD5 | - layer `XII.2` on `claude/agent-instruction-files`: 1 file cites it (trace-id 1); verdict undeclared; titled "No agent expands its own allocation" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:688 | 0.24% | unattested |
| HD6 | - layer `XII.2` on `claude/ai-model-smoothing-gentrification-alc5dm`: 1 file cites it (trace-id 1); verdict undeclared; titled "No agent expands its own allocation" on its law (Draft 0.8, blob `c6343c7`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:689 | 0.26% | unattested |
| HE1 | - layer `XII.3` on `master`: 0 files cite it; verdict undeclared; titled "Contention is arbitrated under witness" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:693 | 0.20% | unattested |
| HE2 | - layer `XII.3` on `ccr-392b8b73-v809qu`: 0 files cite it; verdict undeclared; titled "Contention is arbitrated under witness" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:694 | 0.21% | unattested |
| HE3 | - layer `XII.3` on `ccr-542b5884-0deee5`: 0 files cite it; verdict undeclared; titled "Contention is arbitrated under witness" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:695 | 0.21% | unattested |
| HE4 | - layer `XII.3` on `ccr-8a588c96-jf76ei`: 0 files cite it; verdict undeclared; titled "Contention is arbitrated under witness" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:696 | 0.21% | unattested |
| HE5 | - layer `XII.3` on `claude/agent-instruction-files`: 0 files cite it; verdict undeclared; titled "Contention is arbitrated under witness" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:697 | 0.23% | unattested |
| HE6 | - layer `XII.3` on `claude/ai-model-smoothing-gentrification-alc5dm`: 0 files cite it; verdict undeclared; titled "Contention is arbitrated under witness" on its law (Draft 0.8, blob `c6343c7`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:698 | 0.25% | unattested |
| HF1 | - layer `XII.4` on `master`: 0 files cite it; verdict undeclared; titled "Background work yields to the present human" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:702 | 0.20% | unattested |
| HF2 | - layer `XII.4` on `ccr-392b8b73-v809qu`: 0 files cite it; verdict undeclared; titled "Background work yields to the present human" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:703 | 0.22% | unattested |
| HF3 | - layer `XII.4` on `ccr-542b5884-0deee5`: 0 files cite it; verdict undeclared; titled "Background work yields to the present human" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:704 | 0.22% | unattested |
| HF4 | - layer `XII.4` on `ccr-8a588c96-jf76ei`: 0 files cite it; verdict undeclared; titled "Background work yields to the present human" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:705 | 0.22% | unattested |
| HF5 | - layer `XII.4` on `claude/agent-instruction-files`: 0 files cite it; verdict undeclared; titled "Background work yields to the present human" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:706 | 0.23% | unattested |
| HF6 | - layer `XII.4` on `claude/ai-model-smoothing-gentrification-alc5dm`: not a clause of this branch's law (Draft 0.8, blob `c6343c7`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:707 | 0.17% | unattested |
| HG1 | - layer `Article XIII` on `master`: 3 files cite it (trace-id 3); verdict undeclared; titled "Federation" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:711 | 0.19% | unattested |
| HG2 | - layer `Article XIII` on `ccr-392b8b73-v809qu`: 3 files cite it (trace-id 3); verdict undeclared; titled "Federation" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:712 | 0.20% | unattested |
| HG3 | - layer `Article XIII` on `ccr-542b5884-0deee5`: 3 files cite it (trace-id 3); verdict undeclared; titled "Federation" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:713 | 0.20% | unattested |
| HG4 | - layer `Article XIII` on `ccr-8a588c96-jf76ei`: 3 files cite it (trace-id 3); verdict undeclared; titled "Federation" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:714 | 0.20% | unattested |
| HG5 | - layer `Article XIII` on `claude/agent-instruction-files`: 3 files cite it (trace-id 3); verdict undeclared; titled "Federation" on its law (Draft 0.9, blob `3f356da`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:715 | 0.22% | unattested |
| HG6 | - layer `Article XIII` on `claude/ai-model-smoothing-gentrification-alc5dm`: 2 files cite it (trace-id 2); verdict undeclared; titled "Federation" on its law (Draft 0.8, blob `c6343c7`). | `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md`:716 | 0.24% | unattested |
<!-- /cross-table:index -->

## Measure

*Written by `cross_table.py fill --measure`, the same as the other grids.*

<!-- cross-table:measure -->
- **Cells:** 468, of which 468 found (100.0%).
- **Text:** 78022 characters. An even share would be 0.21% per cell.
- **Trim:** 0 cell(s) cut at 420 characters; the index keeps 100.0% of the source text.

| Row | What it holds | Found | Characters | Share | Largest cell |
|---|---|---|---|---|---|
| EH | Article 0 | 6/6 | 1030 | 1.32% | EH6 0.25% |
| EI | 0.1 | 6/6 | 1079 | 1.38% | EI6 0.26% |
| EJ | 0.2 | 6/6 | 1142 | 1.46% | EJ6 0.27% |
| EK | 0.3 | 6/6 | 1160 | 1.49% | EK6 0.28% |
| EL | 0.4 | 6/6 | 1288 | 1.65% | EL6 0.31% |
| EM | 0.5 | 6/6 | 1307 | 1.68% | EM6 0.31% |
| EN | 0.6 | 6/6 | 1065 | 1.36% | EN6 0.26% |
| EO | Article I | 6/6 | 1042 | 1.34% | EO6 0.25% |
| EP | I.1 | 6/6 | 1106 | 1.42% | EP6 0.27% |
| EQ | I.2 | 6/6 | 986 | 1.26% | EQ6 0.24% |
| ER | I.3 | 6/6 | 1076 | 1.38% | ER6 0.26% |
| ES | I.4 | 6/6 | 1034 | 1.33% | ES6 0.25% |
| ET | I.5 | 6/6 | 953 | 1.22% | ET5 0.23% |
| EU | Article II | 6/6 | 1040 | 1.33% | EU6 0.25% |
| EV | II.1 | 6/6 | 1034 | 1.33% | EV6 0.25% |
| EW | II.2 | 6/6 | 1058 | 1.36% | EW6 0.26% |
| EX | II.3 | 6/6 | 932 | 1.19% | EX6 0.23% |
| EY | Article III | 6/6 | 1060 | 1.36% | EY6 0.25% |
| EZ | III.1 | 6/6 | 866 | 1.11% | EZ6 0.22% |
| FA | III.2 | 6/6 | 1112 | 1.43% | FA6 0.27% |
| FB | III.3 | 6/6 | 908 | 1.16% | FB6 0.22% |
| FC | III.4 | 6/6 | 890 | 1.14% | FC6 0.22% |
| FD | III.5 | 6/6 | 890 | 1.14% | FD5 0.21% |
| FE | Article IV | 6/6 | 1036 | 1.33% | FE6 0.25% |
| FF | IV.1 | 6/6 | 1118 | 1.43% | FF6 0.27% |
| FG | IV.2 | 6/6 | 1118 | 1.43% | FG6 0.27% |
| FH | IV.3 | 6/6 | 1010 | 1.29% | FH6 0.25% |
| FI | IV.5 | 6/6 | 1124 | 1.44% | FI6 0.27% |
| FJ | IV.6 | 6/6 | 1124 | 1.44% | FJ6 0.27% |
| FK | IV.4 | 6/6 | 1130 | 1.45% | FK6 0.27% |
| FL | IV.7 | 6/6 | 1009 | 1.29% | FL5 0.24% |
| FM | IV.8 | 6/6 | 899 | 1.15% | FM5 0.21% |
| FN | Article V | 6/6 | 1048 | 1.34% | FN6 0.25% |
| FO | V.1 | 6/6 | 890 | 1.14% | FO6 0.22% |
| FP | V.2 | 6/6 | 992 | 1.27% | FP6 0.24% |
| FQ | V.3 | 6/6 | 956 | 1.23% | FQ6 0.23% |
| FR | V.4 | 6/6 | 896 | 1.15% | FR6 0.22% |
| FS | V.4a | 6/6 | 1178 | 1.51% | FS6 0.28% |
| FT | V.4b | 6/6 | 784 | 1.00% | FT5 0.18% |
| FU | V.5 | 6/6 | 896 | 1.15% | FU6 0.22% |
| FV | V.6 | 6/6 | 838 | 1.07% | FV5 0.20% |
| FW | V.7 | 6/6 | 908 | 1.16% | FW5 0.21% |
| FX | V.8 | 6/6 | 843 | 1.08% | FX5 0.20% |
| FY | V.9 | 6/6 | 908 | 1.16% | FY5 0.21% |
| FZ | Article VI | 6/6 | 1004 | 1.29% | FZ6 0.24% |
| GA | VI.1 | 6/6 | 1034 | 1.33% | GA6 0.25% |
| GB | VI.2 | 6/6 | 914 | 1.17% | GB6 0.23% |
| GC | VI.3 | 6/6 | 926 | 1.19% | GC6 0.23% |
| GD | VI.4 | 6/6 | 1034 | 1.33% | GD6 0.25% |
| GE | VI.5 | 6/6 | 1134 | 1.45% | GE5 0.27% |
| GF | VI.6 | 6/6 | 824 | 1.06% | GF5 0.19% |
| GG | Article VII | 6/6 | 1018 | 1.30% | GG6 0.24% |
| GH | VII.default | 6/6 | 1058 | 1.36% | GH6 0.26% |
| GI | Article VIII | 6/6 | 968 | 1.24% | GI6 0.24% |
| GJ | VIII.1 | 6/6 | 1010 | 1.29% | GJ6 0.25% |
| GK | VIII.2 | 6/6 | 1046 | 1.34% | GK6 0.25% |
| GL | VIII.3 | 6/6 | 950 | 1.22% | GL6 0.23% |
| GM | Article IX | 6/6 | 1040 | 1.33% | GM6 0.25% |
| GN | IX.1 | 6/6 | 878 | 1.13% | GN6 0.22% |
| GO | IX.2 | 6/6 | 908 | 1.16% | GO6 0.22% |
| GP | IX.3 | 6/6 | 908 | 1.16% | GP6 0.22% |
| GQ | IX.4 | 6/6 | 950 | 1.22% | GQ6 0.23% |
| GR | Article X | 6/6 | 1072 | 1.37% | GR6 0.26% |
| GS | X.1 | 6/6 | 836 | 1.07% | GS6 0.21% |
| GT | X.2 | 6/6 | 854 | 1.09% | GT6 0.21% |
| GU | X.3 | 6/6 | 950 | 1.22% | GU6 0.23% |
| GV | X.4 | 6/6 | 986 | 1.26% | GV6 0.24% |
| GW | X.4a | 6/6 | 844 | 1.08% | GW5 0.20% |
| GX | Article XI | 6/6 | 1028 | 1.32% | GX6 0.25% |
| GY | XI.1 | 6/6 | 1004 | 1.29% | GY6 0.24% |
| GZ | XI.2 | 6/6 | 992 | 1.27% | GZ6 0.24% |
| HA | XI.3 | 6/6 | 908 | 1.16% | HA6 0.22% |
| HB | Article XII | 6/6 | 1042 | 1.34% | HB6 0.25% |
| HC | XII.1 | 6/6 | 1076 | 1.38% | HC6 0.26% |
| HD | XII.2 | 6/6 | 1082 | 1.39% | HD6 0.26% |
| HE | XII.3 | 6/6 | 1022 | 1.31% | HE6 0.25% |
| HF | XII.4 | 6/6 | 985 | 1.26% | HF5 0.23% |
| HG | Article XIII | 6/6 | 974 | 1.25% | HG6 0.24% |

- **Largest:** EM6 0.31%, EL6 0.31%, EM5 0.29%, EL5 0.28%, FS6 0.28%.
- **Smallest:** FT1 0.15%, GS1 0.16%, GT1 0.16%, GF1 0.16%, EZ1 0.16%.

**Evenness.** Gini 0.07 (0 means every box holds the same, 1 means one box holds everything).
- **Fat** (at least 3× an even share; often several rules in one box, a candidate to split): none.
- **Thin** (at most 0.25× an even share; a label with a line behind it): none.

**Sources.** How much of each source file the grid draws on (distinct passages over the file's characters, whitespace collapsed, not counting any tables this script generated in it).

| File | Cells | Drawn | File | Coverage |
|---|---|---|---|---|
| `willows-grove/docs/design/coverage/coverage-layers-ledger-2026-10-06.md` | 468 | 78022 | 80535 | 96.9% |

**Across grids.** Each grid's part of all the text.

| Grid | Cells | Characters | Share of all |
|---|---|---|---|
| Coverage by branch: the third axis (2026-10-06) | 468 | 78022 | 31.1% |
| Rules cross table: boxes and branches (2026-10-06) | 169 | 27250 | 10.9% |
| Boxes, from outside the system (2026-10-06) | 20 | 3434 | 1.4% |
| The fat, dripped (2026-10-06) | 90 | 4063 | 1.6% |
| Gerald session atoms (2026-10-06) | 156 | 53779 | 21.4% |
| Open branches (2026-10-06) | 48 | 6475 | 2.6% |
| Handoffs against Draft 0.9 (2026-10-06) | 210 | 13919 | 5.5% |
| Coverage: every clause of Draft 0.9 against the three repos (2026-10-06) | 869 | 64060 | 25.5% |
<!-- /cross-table:measure -->

---

ΔΣ=42
