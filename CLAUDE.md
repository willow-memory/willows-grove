<!-- b17: WGRV1 -->
# Willow's Grove

b17: WGRV1  ΔΣ=42

## Whose seat this is

This file describes the repo. It does not assign an identity.

The seat comes from `session_enter(app_id=...)`, which returns the persona from
the willow-mcp bundle — the same mechanism every other seat uses. Two seats work
in this repo:

| Lens | Seat | `app_id` | Opened from |
|------|------|----------|-------------|
| **Desk** | Willow | `willow` | repo root |
| **Watch** | Heimdallr | `heimdallr` | `seat/heimdallr/` |

If `session_enter` has not run, you do not yet know which seat you are. Run it
before acting. No prose in this file assigns an identity: the seat is carried by
the `WILLOW_APP_ID` in the `.mcp.json` of the directory you opened, and
`session_enter` reads it back from the persona bundle, which stays the single
source of truth. The Desk is the default because this repo is Willow's Grove;
the Watch is a lens you open on purpose.

## Grove is

A loopback-only served page on `127.0.0.1:8766` (Starlette + uvicorn) that
hosts the Grove Web Components. Reads live state from Postgres, the local
Nestor store, and the willow-mcp `kb_journal` seam. The MCP server
(`./run_mcp.sh`) runs as its own process; in `--serve` mode it exposes
Grove tools to remote (claude.ai) clients over HTTP+OAuth on `:8767`.

Every reader honors the three-state contract (INVARIANTS.md §1): populated /
empty / unreachable — never collapsed. Every panel renders each state
distinctly.

## Watch vs Desk

This repo is **Willow's Grove** (possessive). Inside it:

| Lens | Owner | Owns |
|------|--------|------|
| **Desk** | Willow | The repo root — this is Willow's Grove, so the Desk is what you get by opening it; desk content (seat scripts, `jeles-intake/`) stays under `seat/willow/`; what the desk is *for* — one Jarvis composition (priority bubbles underneath; not a Governance/PM/PA mode switch) |
| **Watch** | Heimdallr | Served page honesty, resident watcher, Gjallarhorn / `#alerts`, serve-mode auth |

Rule of thumb: Willow decides what the desk is for; Heimdallr decides whether
the surface is telling the truth. The desk is **not** a mode switch. Full table:
[`docs/design/grove-persona-partition.md`](docs/design/grove-persona-partition.md).

Heimdallr does **not** maintain `seat/willow/` and does **not** invent desk
posture for the operator. Willow does **not** own watcher classification or
serve-mode OAuth.

> The desk composes priority for one principal across heterogeneous concerns
> rather than offering a mode switch — the "Operator Jarvis seat," sealed as D1
> and argued in [`docs/design/willow-grove-premise.md`](docs/design/willow-grove-premise.md).
> That doc also draws the line the metaphor stops at: Iron Man's workshop as
> metaphor, not copy; J.A.R.V.I.S. iconography stays theirs.

## Architecture

| File/Dir | Responsibility |
|---|---|
| `grove_serve.py` | The served-page host on 127.0.0.1:8766 |
| `grove_html.py` | The served page's HTML shell |
| `grove_db.py` | Postgres reader; `connect_timeout` + `statement_timeout` bounded |
| `grove_reader.py` | Reader helpers (channels, messages, agents, routing) |
| `grove/` | Grove Python package (readers + endpoints + serve-mode auth) |
| `web/components/*.js` | Web Components (persona-registry, envelope-panel, dispatch-rail, chat, refusal-chip, cast-chip, lens-switch, card, dispatch-rail, envelope-panel) |
| `web/boot/*.js` | Page-level boot modules (refusal-summon, layout-memory, standing) |
| `u2u/` | LAN transport for knock/consent/note messages — signed (Ed25519), plaintext on the wire; see `docs/design/u2u-security-limits.md` for what u2u guarantees and what it does not. Confidentiality planned for Gate 6. |
| `bridge/` | Matrix bridge |
| `grove/mcp_local.py` | Grove MCP server — stdio (local) or `--serve` (HTTP+OAuth on :8767) |
| `grove/mcp_auth.py` | `GroveOAuthProvider` — OAuth 2.0/PKCE authorization server for serve mode |
| `run_mcp.sh` | Launch wrapper (resolves venv, sets env) |
| `deploy/grove-mcp-serve.service.template` | systemd `--user` unit template |
| `scripts/grove-serve` | Toggle serve unit + `.mcp.json` entry together |

## Rules

These bind whoever is sitting here, in either lens.

1. **No web ports for the dashboard.** Portless means portless.
2. **grove_db.py owns the schema.** Don't duplicate schema definitions elsewhere.
3. **grove_reader.py is read-only.** Writes go through grove_db.py.
4. **Propose before acting — for new work.** The human trust root ratifies
   the start of new work. Neither party acts alone on new scope. But an
   authorized running task continues to completion without re-ratification
   at each sub-item. "Propose before acting" governs starting, not
   continuing. The only valid mid-task stops are genuine blockers.
5. **Willow's own not_do binds every fleet persona.** Commit, PR, merge,
   patch, or wire the fleet without a recorded authorization — do not do.
   INVARIANTS.md §12.
6. **Persona provenance and ratification are enforced, not aspirational.**
   Every commit that changes tracked code — including `.md`, which is tracked
   code under §3 — carries a `Persona:` trailer whose value is a key from
   `governance/fleet_personas.json`, verbatim and lowercase. Merge commits are
   exempt; nothing else is, and there is no grace period. Every PR body ends
   with `Ratified-by: <id> — "<the operator's verbatim words>"`.
   INVARIANTS.md §11 and §12; `scripts/check_persona_provenance.py` in CI.

---

ΔΣ=42
