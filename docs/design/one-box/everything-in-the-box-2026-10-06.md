# Everything in the box, in the grid (proposal, 2026-10-06)

*Desk session, 2026-10-06. The operator asked whether N+1 was in the grids yet,
then: "How hard would it be to get everything in the Box in that grid?", and
on the answer: "Write it up". A proposal. Nothing here is built, and nothing
is ratified. The figures were measured in this session from the three repos'
tracked files. Agent-reported.*

## 1. N+1, which is where this started

N+1 isn't a box in any grid yet. It is in the repos, in four design places,
and every time it has the same shape: **step N+1 checks or builds on step N**.

| Where | What N+1 does |
|---|---|
| [`../one-script/workflow.md`](../one-script/workflow.md) | "Gate *n+1* verifies gate *n*'s stamp but can't produce it." This is the ΔΣ=42 packet chain. |
| `../one-script/incoming/haiku-2026-10-02/proposal-packet-stamp-chain.md` | Gate N+1, the receiver, verifies the last stamp and checks the chain backward. |
| `../one-script/incoming/haiku-2026-10-02/proposal-heartbeat-and-loops.md` | The loop restarts on beat N+1. |
| willow-mcp `docs/mai-conversion-loop.md` | Bite N+1 starts from everything bites 1..N learned, so the gap list shrinks toward zero. |

The cross-table template does it mechanically. Its `next_row` starts every new
grid at the last grid's row plus one, which is how this session's grids ran
A–M, N–Q, R–Z, AA–AL, AM–AR, AS–BF, BG–EG, EH–HG and HH–HJ. Every drip
checked its clause against the parent's place, and every snapshot is checked
by the next run's `--against`. N+1 is the pattern under most of this
session's work. It just hasn't been named as a box.

A grid of everything would make that pattern the whole point: each run is
N+1 of the last, and the snapshot says exactly what changed.

## 2. How big "everything" is

Measured from `git ls-files` in each repo:

| | Files | Text | Can't read | Lines | Blocks* |
|---|---|---|---|---|---|
| willows-grove | 543 | 532 | 11 | 128,970 | 27,558 |
| willow-mcp | 872 | 869 | 3 | 241,534 | 48,141 |
| willow-bot | 148 | 148 | 0 | 32,206 | 5,461 |
| **Total** | **1,563** | 1,549 | 14 | 402,710 | **81,160** |

\* A block is the template's unit: a paragraph, list item, table row or
heading. 18.7 MB of text in all. The rows used so far run A–HJ, which is 218
rows.

## 3. Two grains, and what each costs

### One row per file: easy

- **1,563 rows,** starting at HK, the row after HJ. The 14 files that can't
  be read as text get a row that says so (the "can't tell" state).
- **Mechanically, this already exists.** The ledger generators in this
  session read every tracked file (the coverage ledger did it twice). A run
  takes about a minute and gives the same bytes every time.
- **Size:** a few MB of markdown, so one ledger and one grid per repo, not
  one document.

### One row per passage: hard, for three structural reasons

Effort isn't the hard part.

1. **It copies the box into itself.** About 81,000 copied passages is roughly
   another 18 MB. Once it's committed, the copy is part of the box, so the
   next run has to contain it, and the run after that contains both. That's
   the Library of Babel row in [`random-pull-2026-10-06.md`](random-pull-2026-10-06.md).
2. **It would cite everything.** A grid that copies every passage copies every
   clause citation, and the coverage report would count it as citing every
   clause. This session hit that twice, with one file at a time: a draft
   coverage ledger that wrote Trace IDs, and generated ledgers that wrote the
   eternity clauses' section sign
   ([`../coverage/coverage-table-2026-10-06.md`](../coverage/coverage-table-2026-10-06.md)).
3. **Markdown stops being the right container.** At 81,000 rows the ledger
   should be JSONL or a database table, with grids rendered for whatever slice
   someone is looking at. That's the stack's row 11, "the database builds
   itself" ([`../one-script/README.md`](../one-script/README.md)).

The answer to all three is the one the box's coverage script already uses:
**the grid excludes itself, and rows hold pointers and hashes, not copies.**
That's the stack's row 3: pointers, not prose. A row says where a passage is
and what its fingerprint is. Reading it means following the pointer.

## 4. What "everything" can't include from a session like this one

- **The vault.** No vault path is set in the cloud container, and the vault
  is the operator's key in any case. Nothing here reaches into it, and a
  grid of everything should never need to.
- **Untracked and ignored files** (`.willow/` and the like), which `git
  ls-files` doesn't list. They can be added deliberately, as a declared
  root, the way the coverage script takes `--root`.
- **The Willow repo,** which is empty in this checkout.
- **Anything on other machines,** and anything outside the three repos (the
  Gerald session's uploads, for example).

The grid should say what it left out, in its header, the same way the
coverage report says what it couldn't read.

## 5. The recommendation

Build it at file grain, with pointers and hashes:

- **One ledger per repo,** generated from `git ls-files`, one line per file,
  and every line naming its file, so each box's pattern finds exactly one line.
- **It excludes itself.** The ledgers, their grids and their snapshots are
  never rows in their own output.
- **It holds pointers and hashes, not copies,** so it cites nothing and can't
  grow by containing itself.
- **A snapshot on every run.** `measure --against` names exactly which files
  changed, appeared or went since the last run. That is N+1, made the point
  of the grid.
- **JSONL underneath once it passes markdown size,** with markdown grids
  rendered for slices (one repo, one directory, one kind).

**Building it is small:** a generator like the ones in this session, a map,
and a fill. Possibly one template change, so `fill` can read a JSONL ledger
directly. The size is no longer the question.

## 6. The decision only the operator can make: the columns

The script asks every question of every row. Choosing the questions is what
decides what the box is *for*, and it's the one part a script can't do
honestly. Some candidates, all of which can be generated deterministically:

| Column | Generated from |
|---|---|
| path, repo | `git ls-files` |
| kind (code, tests, docs) | the coverage ledger's rule |
| size, lines | the file |
| sha256 | the file |
| last commit, and its date | `git log -1` |
| clauses it cites, and by which spelling | the box's coverage report |
| grids that already copy from it | the maps' `file` fields |
| N+1 shape present | a pattern for the "N+1" form |
| standing | the human, never the script |

The last row is the same as in every grid: the script writes `unattested`,
and only a person moves it.

## 7. Open

- Which columns, from the table above or others. **(Operator.)**
- Whether untracked roots such as `.willow/` are declared in. **(Operator.)**
- Whether the per-file ledger lives in the repo or beside it. A few MB per
  run is fine to commit once. Committing a new one on every N+1 isn't, so
  snapshots may belong outside git. **(Operator.)**
- Whether passage grain is ever wanted. If it is, it's pointers and hashes
  in JSONL, never copies, and never in this repo's tree.

---

ΔΣ=42
