# Grove — operator runbook (v0.9)

b17: WGROB · ΔΣ=42

Operator-facing reference for running, checking, and recovering
Willow's Grove at v0.9. Cites `docs/INVARIANTS.md` §-anchors, not
line numbers — line numbers rot, anchors don't (§3).

Trust root: the human at the seat. Willow (`willow-memory/willow/fleet_personas.json`
key `willow`, `trust: OPERATOR`) holds the seat where the human's
authorization is recorded. No fleet persona has unilateral authority
to commit, PR, merge, patch, or wire the fleet — §12 seals this.

---

## What Grove is

A loopback-only served page on `127.0.0.1:8766` (Starlette + uvicorn),
hosting the Grove Web Components. Reads live state from Postgres
(`willow_20` schema), from a local Nestor store, and from the
willow-mcp `kb_journal` seam. No public HTTP surface. The MCP server
(`./run_mcp.sh`) is a separate process for remote (claude.ai) tool
access — that one is auth-gated and lives on its own port when running
in `--serve` mode.

Every reader in the tree honors the three-state contract (§1):

- **populated** — the source was reached and returned a bounded value.
- **empty** — the source was reached and had nothing.
- **unreachable** — the source could not be reached; raises
  `grove.errors.Unreachable`. Never collapses into empty.

Every `/api/*` endpoint mirrors that shape (200/populated, 200/empty,
503/unreachable).

---

## Entry points

| Command | Purpose |
|---|---|
| `python3 grove_serve.py` | Loopback-only served-page host on `127.0.0.1:8766`. Reads env `GROVE_SERVE_PORT` (numeric; refuses on bad value with `sys.exit(2)`) and `GROVE_SERVE_HOST`. |
| `python3 app.py` | Textual dashboard — main operator TUI. |
| `python3 -m grove` | Lightweight curses TUI (SSH / narrow terminal). |
| `./run_mcp.sh` | Grove MCP server — stdio mode. Claude Code / Cursor spawns this to talk to Grove locally. |
| `./run_mcp.sh --serve` | Grove MCP over HTTP+OAuth on `:8765`. For remote clients (claude.ai) fronted by a tunnel. |
| `scripts/grove-serve {install\|on\|off\|status}` | Toggle the `--serve` systemd unit and the local `.mcp.json` entry together. |

---

## Boot preconditions (§ mandate: run `/startup` before anything else)

1. **Postgres must be up.** If Postgres is down, surface it and stop —
   do not build on a broken foundation. `grove_db.py` now sets a
   `connect_timeout` (env `GROVE_PG_CONNECT_TIMEOUT`, default 5s) and a
   `statement_timeout` (env `GROVE_PG_STATEMENT_TIMEOUT_MS`, default
   30000) so a stuck-but-reachable Postgres surfaces the failure
   quickly rather than hanging on the OS default socket timeout.
2. **`WILLOW_DB_URL`** is the single DSN used by `grove_db.py`,
   `grove_serve.py`, and the ledger writer. Overrides the legacy
   `WILLOW_PG_DB` + `WILLOW_PG_USER` pair.
3. **`OLLAMA_HOST`** points at the local Ollama instance for classify
   paths (resident watcher). Absent → the watcher fixture skips
   locally, fails loud in CI (`$GITHUB_ACTIONS=true`).
4. **`WILLOW_HOME`** roots the operator's per-node state (Nestor
   store, persona registry, seed canon fallback path).

---

## Health checks

**Endpoint level.**

Every `/api/*` endpoint returns one of the three §1 shapes. A quick
sweep from the operator's box:

```bash
for ep in personas envelopes dispatch journal/recent; do
  curl -s -o /dev/null -w "%{http_code} $ep\n" \
    http://127.0.0.1:8766/api/$ep
done
```

Expected: `200` (populated or empty) or `503` (unreachable). No
`500` — a bare exception on a §1 endpoint is drift the pinning tests
would have caught.

**Reader level.**

If an endpoint returns `503`, the reader raised `Unreachable`. The
reason string is in the JSON body's `reason` field. Common shapes:

| Reader | `reason` starts with | Likely cause |
|---|---|---|
| `grove/persona_roster.py` | `personas file` | Drifted or missing personas.json; check `WILLOW_HOME/personas/personas.json`. |
| `grove/journal_reader.py` | `willow-mcp error` | willow-mcp responded with an `{error}` dict; check the mcp process logs. |
| `grove/nestor_client.py` | `nestor not on PATH` | `nestor` binary not resolvable; check `$PATH` or set `NESTOR_STORE`. |
| `grove/fleet_presence.py` | `fleet_presence not importable` | The add-on module is missing; safe to ignore for local dev. |
| `grove_reader.py` (16 sites) | any psycopg2 error | Redacted per §6 privacy — check server logs for the full exception. |

**CI level.**

`.github/workflows/tests.yml` runs on every PR and push. Steps that
prove the invariants:

- `Security grep` (`scripts/ci-security-grep.sh`) — §10.
- `Docs-drift check` (`scripts/check_docs_drift.py`) — §3 + §10.
- `Ratification check` (`scripts/check_ratification.py`) — §10 + §12.
- `Persona-provenance check` (`scripts/check_persona_provenance.py`) —
  §10 + §11.
- `Run test suite` — the pytest layer.
- `Playwright e2e suite` — the browser-driven layer for §1 + §8 + §9.
- `Ollama-backed watcher e2e` + `willow-mcp mock e2e` — §10 witnesses
  for the C11 seam. Fail-loud on CI, skip-loud locally.

---

## Recovering common failures

### The dashboard shows `grove stable` but a seam is actually down

**As of v0.9, PR 12 fix m31, the top strip renders `reading standing…`
as a loading placeholder.** The static `grove stable` claim was
removed. If you see `grove stable` in the render, you are on a
pre-v0.9 checkout; upgrade.

### One panel shows empty when Postgres is actually down

Every reader raises `Unreachable` on §1 discipline. If a panel is
showing empty instead of the unreachable affordance, either (a) the
seam it reads is genuinely empty (not down), or (b) a §1 regression
slipped in. Check the endpoint directly (see health checks above). If
the endpoint returns 200/empty when the source is actually down, file
a regression against §1 — the pinning tests should have caught it.

### The read-back column shows both a banner AND `no messages yet`

**As of v0.9, PR 12 fix M11, this cannot happen.** The empty-state
placeholder is now removed on the unreachable branch; only the
banner shows. If you see both, upgrade.

### A PR CI complains about `ratification: FAIL`

Per §12, the PR body's first non-blank line must match
`Ratified-by: <identifier> — "<verbatim quote>"`. Add the line with
the human's verbatim word that authorized the PR open. Em-dash,
en-dash, or ASCII `" - "` all accepted; straight or curly quotes.

### A commit fails `persona-provenance` CI

Per §11, every commit changing tracked code (`.py`, `.js`, `.sh`,
`.md`, `.yml`, `.yaml`, `.sql`, `.json`, `.html`) needs a `Persona:`
trailer naming a fleet-persona key from
`willow-memory/willow/fleet_personas.json`. Multi-persona commits
carry two trailers. Merge commits are exempt. Amend the commit
message locally with the trailer and force-with-lease on your own
branch. Never rewrite history on someone else's branch.

### The FRANK ledger write fails silently

**As of v0.9, PR 12 fix M18, ledger write failures raise
`grove.errors.LedgerWriteFailed` with a full traceback via
`log.exception`.** The failure is no longer print-to-stdout-and-vanish.
If you see stray `[frank-ledger] write error:` lines in stdout, you
are on a pre-v0.9 checkout; upgrade.

---

## The audit record

`docs/audits/loki-v0.9-audit.md` — Loki's v0.9 audit in his voice
(dry, exact, three-column: promised / delivered / distance). 38
ranked findings, all resolved in PR 12 or refuted with reason.

`docs/audits/loki-swarm-raw.json` — raw workflow output verbatim.

`docs/audits/loki-swarm-measurement.md` — persona-discipline scored on
seven dimensions. The evidence for the pitch: register hold 0/41
florid, deny-list hold 0/41 build proposals, three-column
completeness 41/41, softening 1/41 (2.4%), authority-as-correctness
0/41, signal-density spread 10×, near-zero cross-lens convergence.

`docs/audits/loki-swarm-metadata.md` — reproducibility layer:
persona strings verbatim, per-lens prompts verbatim, per-agent
runtime metrics, to-reproduce recipes for same-code/same-persona,
same-code/different-persona, and same-persona/different-code.

---

## Where discipline is sealed

- `docs/INVARIANTS.md` — 12 §-sections. Every invariant has at least
  one CI witness (§10 enforces).
- `scripts/check_docs_drift.py` — grep + parse, enforces §3.
- `scripts/check_persona_provenance.py` — git log walk, enforces §11.
- `scripts/check_ratification.py` — PR body / merge commit grep,
  enforces §12.
- `.github/workflows/tests.yml` — runs all three checks on every push.

Every seal is `hard` from its landing commit forward. Grandfathered
commits carry no provenance and no ratification records; those are
logged in `docs/design/pr14-carryovers.md` for the record and are not
backfillable.

---

## Known carryovers to v0.10

See `docs/design/pr14-carryovers.md` — the durable list of what
v0.9 punt to v0.10 or later. Key items:

- Pixel-baseline regression re-enable on `/seed/{1..6}` (deferred in
  PR 9).
- CI schema completeness so §1 populated branch is exercised, not just
  §1 unreachable branch (v0.9 CI logs show `public.human_required_queue`
  and `public.routing_decisions` do not exist in the bootstrap
  schema).
- Sibling panels' `_state` vocabulary audit (dispatch-rail was on the
  pre-§1 vocabulary; PR 9 fixed it; every other panel is a candidate).
- Durable fleet-model-map (`model_hint_session` field on every entry
  in `willow-memory/willow/fleet_personas.json` — Sonnet 5 for
  Hanuman, Opus for Loki + Heimdallr, Haiku 4.5 for WORKER tier,
  Fable reserved).
- `specialists.json` deny-lists for every ENGINEER+ persona (only Loki
  has one today).
- OPERATOR-tier `not_do` audit (Ada, Steve, Skirnir).
- Actual fleet dispatch wiring (Grove MCP + willow-mcp + Nestor +
  `willow.routing_decisions` + `frank_ledger`) — v1.0 shape.
- Character continuity across compactions.

---

ΔΣ=42
