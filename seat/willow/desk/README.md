# The box desk

What the desk asks of the piles it works from, with nothing running but a
Willow checkout: no MCP server, no database, no model. It is the desk's
other way in, beside `willow-seat.sh desk`, for a machine (or a session)
that has neither the willow-mcp venv nor a sign-in.

    bash seat/willow/scripts/box-desk.sh piles
    bash seat/willow/scripts/box-desk.sh headlines
    bash seat/willow/scripts/box-desk.sh github DIR
    bash seat/willow/scripts/box-desk.sh ask github "what is in the merge queue"

## What is here

| File | What it is |
|---|---|
| [stack.md](stack.md) | The desk's stack for Willow's `stack` add-on: what each pile tells an agent, what the code owes, secrets in plain files, the same questions asked of every pile, what the box needs |
| [words.txt](words.txt) | The desk's words list (`failed = failure`, `queue = queued`, …); the script copies it beside each box with mode 600, as the kernel asks |

## The two boxes

- **piles**: one box over the folder holding the piles (`DESK_PILES`; on a
  cloud container, the folder holding Willow, the Provider, Die-Namic and
  this Grove), and the stack run over it. `headlines` prints each step's
  first line.
- **github**: what `gh ... --json` printed, or what GitHub's API or an MCP
  server over it answered, saved as JSON in DIR, mirrored by Willow's
  `gh-json` (0.2.0 reads the API's shape and says a merge queue's run as
  the pull request it holds) and made a box to ask.

## What it keeps to

- **Runs live under `$WILLOW_HOME/desk`, never in this tree.** A box over the
  piles that held its own write-ups would answer from them (Willow's
  `demo/kept` found it first).
- **No bytecode in the piles.** The add-ons run from inside one, so the
  script sets `PYTHONDONTWRITEBYTECODE`; otherwise `box-health` counts the
  stack's own `.pyc` files as unreadable.
- **Each box has a scratch key of its own.** Nothing here seals, nothing
  reads the person's key, and nothing is proposed.

## What its first run found (2026-11-20)

Recorded in Willow's issues: #383 (37 add-ons crash on a box made with
`--from`, which is why this box is one folder, not four sources) and #91's
fix (hook-guard's `seal` rule). The Grove's own CLAUDE.md names two files
that are not in this tree: `onescript/reach_bootstrap.py` and
`onescript/states.py` (they are willow-bot's, reached through
`grove/onescript_reach.py`).
