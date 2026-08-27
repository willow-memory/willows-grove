# Resident watcher — end-to-end test notes (Grove v0.9 PR 8)

b17: WGRV1 ΔΣ=42

*Companion to `INVARIANTS.md` §10 (CI proves the invariants) and
`autonomous-continuity.md` C11 (the chat card's LEFT side is a
`kb_journal` write via the resident local watcher). This doc names
what the `tests/e2e_ollama/` suite pins and — deliberately — what it
does not.*

## What the suite verifies

The C11 LEFT-side write path, end-to-end:

    grove.messages INSERT
      → pg_notify('grove_channel', channel_id::text)   ← trigger fires
      → ResidentWatcher LISTEN thread pops the notify
      → worker thread calls Ollama /api/generate       ← real model
      → journal_writer.write_operator_turn(text, sender, domain=<tag>)
      → willow_mcp.server.kb_journal(...)              ← stubbed in-test

The assertion surface is exactly the Gate 5 three-question lock plus
V5 verbatim discipline:

* **Q3.** Every capture carries `source="resident-watcher"`.
* **Q2.** Every capture carries exactly one `domain:<value>` tag; the
  value lives in the closed `DOMAINS` set (`chat`, `governance`, `pm`,
  `pa`, `unknown`).
* **V5.** The operator's utterance appears verbatim inside the
  captured content — `journal_writer` never paraphrases.

The base tag surface from `journal_writer._build_tags` (`journal`,
`sender:*`, `ts:*`) is pinned in the same assertion block.

## Why the resident watcher does not RUN inside CI

The watcher is an operational service (a foreground process at the
operator's seat, `python3 -m grove.resident_watcher`), not a unit. CI
does not install a systemd unit and does not run a `-serve` process.
What CI runs is a `pytest` that starts `ResidentWatcher()` in-process,
sends three messages, waits for the journal writes, then calls
`.stop()`. That is the test — not "does the watcher come up as a
service on the box" but "does the watcher's LEFT-side write path do
what it says on the tin when handed a real Postgres and a real Ollama."

## What "green" means for this suite

* **Green in CI** — the `ollama` service container came up, the tiny
  model pulled, Postgres accepted the INSERT, and three
  `kb_journal(...)` captures arrived within the 60s deadline. The
  invariants named above held on every capture.
* **Green locally** — same, provided the operator has `OLLAMA_HOST`
  reachable and `WILLOW_DB_URL` pointing at a Postgres with the
  `grove` schema (the fixture is idempotent — it re-issues the DDL).
* **Skip, not fail** — if Ollama is unreachable, if the pull fails,
  or if Postgres refuses the DSN, every test in the suite `pytest.skip`s
  with a reason line that says which service was missing. A skip is
  not a fail; the operator-only build is entitled to skip Ollama
  without CI going red on the operator's behalf. CI, where the
  services are provisioned by the workflow, treats a skip as a signal
  that the invariant is not being exercised — see
  `test_watcher_ollama_readiness.py`, the canary that names the gap.

## Cost caveat

The first run in a fresh CI container pulls the model (`qwen2.5:0.5b`
by preference, `tinyllama:latest` and `smollm:135m` as fallbacks). The
pull is dominated by the download and takes ~30-60s on a warm network,
longer cold. The `pulled_model` fixture is session-scoped and caches
the winner, so the readiness canary and the watcher e2e share one
pull; a suite with two tests pays that cost once.

Steady-state `/api/generate` on the smallest model takes ~1-3s per
call. The test widens `_OLLAMA_TIMEOUT_SECONDS` via `monkeypatch` for
the duration of the classify path — production defaults stay at the
aggressive 2.0s (D7: never block the seat on a slow model).
