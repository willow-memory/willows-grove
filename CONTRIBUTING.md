# Contributing

This repo (willow-memory/willows-grove) shares one working method with the
rest of the fleet, whether the contributor is a person or an agent. The
binding rules live in [`CLAUDE.md`](CLAUDE.md) and
[`docs/INVARIANTS.md`](docs/INVARIANTS.md); this file names the commands and
conventions a contributor needs in hand.

## The method

- **One bite at a time.** A PR delivers one outcome.
- **Receipts, not claims.** The PR body carries Evidence — check only what
  you actually ran, and state the result, counts included.
- **Propose before acting — for new work.** The human trust root ratifies
  the start of new work; every PR body ends with a `Ratified-by:` line
  (INVARIANTS.md §12) and every code-changing commit carries a `Persona:`
  trailer naming a key from `governance/fleet_personas.json`
  (INVARIANTS.md §11).
- **A scan that has never fired has not been shown to check anything.**
  Every scan-shaped test helper plants its own violation
  (`tests/test_scans_fire.py` holds the suite to it).

## Build and test

```sh
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
psql -c "CREATE DATABASE willow_20;" && psql -d willow_20 -f schema.sql
python3 -m pytest -x -q --ignore=tests/e2e --ignore=tests/e2e_ollama --ignore=tests/e2e_willow_mcp
```

Requires Python 3.11+. CI (`.github/workflows/tests.yml`) runs that command
with `--tb=short`, plus the `tests/e2e_ollama/` and `tests/e2e_willow_mcp/`
legs and the Playwright suite under `tests/e2e/`, and the four checkers under
`scripts/check_*.py` and `scripts/ci-security-grep.sh`. The full onboarding
walk-through is [`docs/TESTER_ONBOARDING.md`](docs/TESTER_ONBOARDING.md).

## The idea pile

Open work is recorded in [`docs/ideas.md`](docs/ideas.md), a numbered pile in
the shape willow-reconciler reads. Numbers there are permanent join keys:
never renumber, never let markdown auto-number, retire a number and leave the
gap.

## The Idea-Id commit-trailer convention

A commit that lands an idea recorded in docs/ideas.md carries an
`Idea-Id: <corpus>-ideas-<num>` git trailer (add `Idea-Status: partial` when a
commit only partly lands it). It is the durable join key willow-reconciler
reads; a wrong id is worse than no id, so never type one by hand:

    reconciler id --repo ./ --doc docs/ideas.md --grep "words from the item"
    reconciler install-hook --repo ./       # derives it from a branch named idea-NN

`.github/workflows/trailers.yml` runs `reconciler verify` on every PR and fails
on a trailer that names an item the doc does not contain.

(`--repo ./`, with the slash: willow-reconciler 0.6.0 reads a bare `.` as a
repo *name* to look up beside your checkout, not as a path.)

## Fleet conventions

`tests/test_fleet_conventions.py` holds this repo's wiring to the fleet's
convention set — which commit types a release hides, which workflows must
exist once a release workflow arms auto-merge or a numbered pile exists, that
this file names the test command above. The rules are not restated there:
`reconciler conventions --json` publishes them, and the test reads the copy
vendored at `tests/fleet_conventions.json`, pinned by hash.
