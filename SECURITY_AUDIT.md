---
b17: WGRV2
title: Security Audit — safe-app-willow-grove
date: 2026-05-06
revised: 2026-07-28
auditor: Hanuman (Claude Code, Sonnet 4.6)
reviser: Claude Opus 5 — re-scoped against the actual file tree
baseline: 27e123a
status: open (tracking doc)
---

# Security Audit — safe-app-willow-grove

Part of the Level 2 full-fleet security audit. Tracking doc: findings are
recorded here, patches land in their own PRs.

## About the 2026-07-28 revision

The 2026-05-06 revision certified things that are not true of this repository.
It reported line-specific findings in `grove_serve.py` and `kart_worker.py`,
neither of which exists here (they live in `willow-2.0`; `grove_db.py:333` still
carries the comment "Re-homed from the cut grove_serve"). It rated the MCP
server's OAuth a PASS and its serve mode "localhost-only by design" while the
code in the same tree auto-approved every authorization request and switched off
the host check for the tunnelled deployment. And it never mentioned `u2u/` or
`bridge/` — the only modules in the repo that make cryptographic trust
decisions.

Everything below is stated against commit `27e123a` and was re-derived from the
tree, not carried forward. Withdrawn claims are listed under
[Corrections](#corrections-to-the-2026-05-06-revision) rather than deleted, so
that anyone who acted on the old document can see what changed.

---

## Scope and method

Coverage levels mean exactly this:

| Level | Meaning |
|---|---|
| **Reviewed** | Read end to end for this revision. |
| **Scanned** | Included in the rubric pattern sweep below; any hit was then opened and read. Not read end to end. |
| **Out of scope — …** | Deliberately excluded, with the reason on the row. |

The sweep behind **Scanned** is `rg` across every tracked `*.py` and `*.sh` for:
`os.system` / `shell=True` / `subprocess.*` / `eval(` / `exec(`; `execute(f"`
and other dynamic SQL; `write_text` / `os.open` / `open(…, "w")` / `chmod`;
`/tmp` and `tempfile`; `except Exception`; `/home/sean-campbell`; and
`innerHTML`. Every hit is accounted for in the rubric table or in a finding.

**The scope table below is enforced by a test.**
`tests/test_security_audit_scope.py` asserts it is exactly the set of tracked
`*.py` and `*.sh` files: a new source file that nobody classified fails the
suite, and a row naming a file that does not exist fails the suite. That is the
mechanism that would have caught the `grove_serve.py` / `kart_worker.py` rows.

Not covered by the table, and deliberately so: `docs/`, `*.md`, `schema.sql`,
`requirements.txt`, `pyproject.toml`, `.mcp.json`, `safe-app-manifest.json` and
`.env.example`. Those are configuration and prose, not executable source; where
one of them carries a finding (`.mcp.json` in G-PATH-01, `requirements.txt` in
G-DEP-01) it is named in the finding.

---

## Scope

| Path | Purpose | Coverage |
|---|---|---|
| `.cursor/hooks/grove_followup.py` | stop hook helper — enqueue new Grove inbox as followup_message for Cursor Auto | Reviewed |
| `.cursor/hooks/run_grove_followup.sh` | keep PYTHONPATH stable | Reviewed |
| `app.py` | Willow Grove dashboard (fresh start) | Scanned |
| `bridge/__init__.py` | Grove ↔ Matrix Application Service bridge | Scanned |
| `bridge/__main__.py` | Grove ↔ Matrix bridge | Scanned |
| `bridge/app.py` | Flow summary | Scanned |
| `bridge/matrix.py` | Matrix CS API client + Application Service HTTP server | Scanned |
| `bridge/store.py` | SQLite mapping: grove addr ↔ Matrix room ↔ Matrix user | Scanned |
| `dev.sh` | alias for run_dev.sh (fresh-start worktree) | Reviewed |
| `grove/__init__.py` | Grove dashboard package — theme and vitals for Textual shell | Scanned |
| `grove/apps/__init__.py` | Grove dashboard apps — vitals strip, MCP registry, pane helpers | Scanned |
| `grove/apps/card_builder/__init__.py` | scripted card builder (v1) | Scanned |
| `grove/apps/card_builder/discovery.py` | list data sources and nav targets | Scanned |
| `grove/apps/card_builder/templates.py` | scripted card-def builders (v1) | Scanned |
| `grove/apps/card_builder/values.py` | resolve live card subtitles from value_source | Scanned |
| `grove/apps/card_builder/wizard.py` | scripted card builder steps (v1, no LLM) | Scanned |
| `grove/apps/hero_format.py` | Rich/plain formatters for hero band regions | Scanned |
| `grove/apps/hero_stats.py` | Live Grove + host stats for the hero band | Scanned |
| `grove/apps/mcp_catalog.py` | Annotated MCP registry + live-server drift | Scanned |
| `grove/apps/mcp_client.py` | stdio MCP sessions for list/call from the dashboard | Scanned |
| `grove/apps/mcp_process.py` | manage grove.mcp_local --serve from the dashboard | Scanned |
| `grove/apps/mcp_registry.py` | Read ~/.mcp.json and probe serve-mode health | Scanned |
| `grove/apps/think_map/__init__.py` | Think Map SOIL store + validation (P0) | Scanned |
| `grove/apps/think_map/outline.py` | outline rows for Think Map pane | Scanned |
| `grove/apps/think_map/store.py` | SOIL CRUD for Think Map drafts | Scanned |
| `grove/apps/think_map/validate.py` | confirm gate rules (brainstorming skill) | Scanned |
| `grove/apps/upstream_steward.py` | read-only consumer for Upstream Steward (2.0 writes) | Scanned |
| `grove/apps/user_board.py` | aggregate user desk items from SOIL + Grove + Kart | Scanned |
| `grove/apps/vitals.py` | System vitals strip for NavBar | Scanned |
| `grove/envelope_reader.py` | Read helper for the fleet envelope registry (schema `envelope-registry/v1.1`, P1); probes `$WILLOW_HOME/envelopes` / `~/willow-memory/Willow/envelopes` / `~/.willow/envelopes` and returns the union under the `envelopes` key, later dirs overriding earlier on `id` collision; on absent dirs or malformed files logs once and returns an empty list (D7). Offline, read-only. | Reviewed |
| `grove/fleet_presence.py` | `announce_grove` / `roster` / `withdraw` wrappers over the `fleet_presence` seam; log-once no-op when the seam is absent (D7). | Reviewed |
| `grove/journal_reader.py` | Thin reader over willow-mcp's `kb_journal` atoms — the chat card's RIGHT-side (C11) sync reader that Grove ships pre-Gate-5. Tries (a) `willow_mcp.server.kb_journal_read` in-process when present, then (b) HTTP GET to `$WILLOW_MCP_URL/tools/kb_journal_read`, then (c) log-once no-op returning `[]` (D7 degradation — absence is a legible state, not an error). Atom text is surfaced verbatim (V5-adjacent discipline); `limit` is clamped to `[1, 200]`; `since_id` filters to strictly-newer atoms with a stale-cursor tolerance. Read-only. | Reviewed |
| `grove/journal_writer.py` | Thin wrapper over willow-mcp's `kb_journal` write path — the chat card's LEFT-side (C11) sync writer. Tries (a) `willow_mcp.server.kb_journal` in-process, then (b) HTTP POST to `$WILLOW_MCP_URL/tools/kb_journal`, then (c) log-once no-op returning `{"ok": False, ...}` (D7 degradation). Operator text is passed through verbatim (V5 discipline). | Reviewed |
| `grove/kart_reader.py` | Read-only helper over `public.tasks` — the Kart escalation seam (autonomous-continuity C6-C8, C12). Probes `information_schema.columns` and drops missing predicates + omits missing select expressions (D7); log-once on absent DSN, missing table, or shape drift; returns `[]` cleanly in every failure mode. Read-only — no INSERT / UPDATE / DELETE (L0 in the promotion-authority ladder). | Reviewed |
| `grove/mcp_auth.py` | Single-user OAuth 2.0 provider for `grove.mcp_local --serve` | Reviewed |
| `grove/mcp_local.py` | Modes: | Reviewed |
| `grove/nestor_client.py` | `NestorClient` wrapper around a long-lived `nestor serve` subprocess (MCP-over-stdio, D11); returns `None` cleanly when the binary is absent (D7); `refusal()` returns Nestor's speech act verbatim (V5). | Reviewed |
| `grove/paths.py` | Resolve Willow repo root and CLI for dashboard subprocesses | Scanned |
| `grove/persona_roster.py` | Read helper for `willow-memory/willow/fleet_personas.json` (schema `fleet-personas/v1`, D10); probes `$WILLOW_HOME` / `~/willow-memory` / `~/.willow`, returns `None` cleanly with a single log when absent (D7); rejects unknown schema versions with ValueError. Offline, read-only. | Reviewed |
| `grove/theme.py` | 256-color palette, borders, draw helpers | Scanned |
| `grove/theme_textual.py` | Textual/Rich colors from grove/theme.py palette | Scanned |
| `grove_channel_audit.py` | find and heal shadow channels | Scanned |
| `grove_client.py` | Send a signed command to a remote Willow Grove server | Scanned |
| `grove_db.py` | Grove workspace messaging database | Scanned |
| `grove_html.py` | Static placeholder HTML for the Grove served-page skeleton (`grove_serve.py`) — no user input, no template rendering, no JS; string constants concatenated in `render_page()` | Reviewed |
| `grove_reader.py` | Direct Postgres reader for Grove and routing data | Scanned |
| `grove_serve.py` | Willow's Grove served-page skeleton on 127.0.0.1:8766 — Starlette + uvicorn, three routes (`/`, `/health`, `POST /api/journal` — the C11 chat card LEFT-side write into willow-mcp `kb_journal` via `grove.journal_writer`), loopback-only by default and warns on wider bind. NOT the cut `willow-2.0` grove_serve — the 2026-05-06 revision's line citations are still withdrawn under corrections. | Reviewed |
| `hero_test.py` | Standalone hero scene test harness | Scanned |
| `panes/__init__.py` | Grove dashboard panes — fresh-start rebuild | Scanned |
| `panes/agents.py` | Fleet agent view from Grove heartbeats | Scanned |
| `panes/chat.py` | Discord social layout: server · channels · transcript · members + DMs | Scanned |
| `panes/chat_admin.py` | channel create/archive helpers (pure + thin DB) | Scanned |
| `panes/chat_commands.py` | Wave B `:` mod command parser + dispatch | Scanned |
| `panes/chat_format.py` | pure formatters for Discord-style Grove chat | Scanned |
| `panes/chat_message_mod.py` | message mod helpers (flags display + toggles) | Scanned |
| `panes/chat_modals.py` | in-context modals for chat admin | Scanned |
| `panes/chat_persona.py` | persona channel helpers (bind, reply routing, dispatch) | Scanned |
| `panes/git.py` | Git status for the Grove repo | Scanned |
| `panes/help.py` | Keyboard reference for fresh-start shell | Scanned |
| `panes/home.py` | DeskPane + dense HomeGrid (wave 2) | Scanned |
| `panes/human.py` | Human-required queue: consent, attestation, review, onboarding | Scanned |
| `panes/knowledge.py` | KB search + atom detail from Postgres | Scanned |
| `panes/mcp.py` | interactive MCP control: serve lifecycle, tools, calls | Scanned |
| `panes/projects.py` | Personal projects from SOIL | Scanned |
| `panes/providers.py` | Provider health from Ollama, env keys, SOIL | Scanned |
| `panes/prs.py` | Open pull requests via gh CLI | Scanned |
| `panes/routing.py` | Live routing decision feed | Scanned |
| `panes/settings.py` | Consent toggles + subsystem vitals | Scanned |
| `panes/stubs.py` | placeholder panes until wave 3+ | Scanned |
| `panes/tasks.py` | Kart task queue from Postgres | Scanned |
| `panes/think_map.py` | Think Map outline pane (P1: draft edit + save) | Scanned |
| `panes/upstream.py` | Upstream Steward inbox (read-only; 2.0 writes SOIL) | Scanned |
| `panes/user_todos.py` | My Desk: user todos, projects, deadlines, atoms | Scanned |
| `run_dev.sh` | launch Grove dashboard (fresh-start worktree) | Reviewed |
| `run_mcp.sh` | Grove MCP server (stdio or serve) | Reviewed |
| `scripts/mcp_entry_toggle.py` | idempotent add/remove of one http entry in an .mcp.json (used by grove-serve) | Reviewed |
| `scripts/nestor_reseed.py` | One-shot operator script — copies sealed pairs from the design's scratch Nestor store into `$WILLOW_HOME/nestor/willows-grove.db` via `nestor.sqlite_store.SqliteStore`. Idempotent (skips existing `source_norm`). Reads `$WILLOW_HOME` and CLI paths — no other external input. | Reviewed |
| `soil.py` | thin sqlite3 wrapper for SOIL collections used by the dashboard | Scanned |
| `tests/__init__.py` | Empty package marker (0 bytes) | Out of scope — test code; not shipped and not reachable at runtime |
| `tests/test_card_builder.py` | scripted wizard + templates | Out of scope — test code; not shipped and not reachable at runtime |
| `tests/test_card_store.py` | tests/test_card_store.py | Out of scope — test code; not shipped and not reachable at runtime |
| `tests/test_channel_normalize.py` | tests/test_channel_normalize.py | Out of scope — test code; not shipped and not reachable at runtime |
| `tests/test_chat.py` | tests/test_chat.py | Out of scope — test code; not shipped and not reachable at runtime |
| `tests/test_chat_admin.py` | channel name rules + archive guards | Out of scope — test code; not shipped and not reachable at runtime |
| `tests/test_chat_commands.py` | Wave B `:` mod command parser | Out of scope — test code; not shipped and not reachable at runtime |
| `tests/test_chat_composer.py` | composer colon → mod command | Out of scope — test code; not shipped and not reachable at runtime |
| `tests/test_chat_message_mod.py` | message mod helpers | Out of scope — test code; not shipped and not reachable at runtime |
| `tests/test_chat_persona.py` | Wave C persona routing + dispatch | Out of scope — test code; not shipped and not reachable at runtime |
| `tests/test_content_stack.py` | nav pane wiring | Out of scope — test code; not shipped and not reachable at runtime |
| `tests/test_envelope_reader.py` | `grove/envelope_reader.py` D7 tolerance — empty dirs, malformed-file skip + log-once, later-dir precedence on `id` collision, and the `pre_approved` charter-key shape | Out of scope — test code; not shipped and not reachable at runtime |
| `tests/test_grove_html_boot_wire.py` | `grove_html.render_page()` mounts `/web/boot/layout-memory-boot.js` last among module scripts in `<head>` so the boot walks the DOM after all sibling component scripts have registered their custom elements | Out of scope — test code; not shipped and not reachable at runtime |
| `tests/test_grove_lens_switch.py` | `<grove-lens-switch>` mount verification — asserts `grove_html.render_page()` references the tri-modal lens component + module, and that the JS file exists on disk | Out of scope — test code; not shipped and not reachable at runtime |
| `tests/test_grove_serve.py` | Grove served-page skeleton integration test (starts uvicorn on an ephemeral loopback port; asserts /health and /) | Out of scope — test code; not shipped and not reachable at runtime |
| `tests/test_grove_serve_dispatch.py` | integration test for grove_serve.py's /api/dispatch route + /web/ static mount | Out of scope — test code; not shipped and not reachable at runtime |
| `tests/test_grove_serve_envelopes.py` | integration test for grove_serve.py's /api/envelopes route — asserts the P1 shape (`schema` + `envelopes`) in both the degraded (no dir) and populated cases | Out of scope — test code; not shipped and not reachable at runtime |
| `tests/test_grove_serve_journal.py` | POST /api/journal integration test (C11 LEFT-side); asserts 400 on missing text, 200 on success, 503 on writer degradation | Out of scope — test code; not shipped and not reachable at runtime |
| `tests/test_grove_serve_journal_read.py` | GET /api/journal/recent integration test (C11 RIGHT-side); asserts 200 with reader-supplied list, empty-list D7 state, `limit` cap at 200, default fallback, invalid-int fallback, and `since` pass-through | Out of scope — test code; not shipped and not reachable at runtime |
| `tests/test_grove_serve_personas.py` | GET /api/personas integration test (D10 unified registry); asserts empty-envelope 200 when the sidecar file is absent (D7) and a verbatim body when `$WILLOW_HOME/willow-memory/willow/fleet_personas.json` is present | Out of scope — test code; not shipped and not reachable at runtime |
| `tests/test_hero_format.py` | hero band formatters | Out of scope — test code; not shipped and not reachable at runtime |
| `tests/test_fleet_presence.py` | `grove/fleet_presence.py` no-op path + announce/roster/withdraw behavior | Out of scope — test code; not shipped and not reachable at runtime |
| `tests/test_hero_stats.py` | hero stats bundle | Out of scope — test code; not shipped and not reachable at runtime |
| `tests/test_internal_panes.py` | Home card internal pane helpers | Out of scope — test code; not shipped and not reachable at runtime |
| `tests/test_journal_reader.py` | `grove/journal_reader.py` — degradation path, mocked HTTP read, `since_id` filter incl. stale-cursor tolerance, `limit` cap + default fallback, verbatim text preservation, direct-import path with a fake `willow_mcp.server.kb_journal_read` | Out of scope — test code; not shipped and not reachable at runtime |
| `tests/test_journal_writer.py` | `grove/journal_writer.py` — degradation path, mocked HTTP write, empty-text ValueError, log-once behavior | Out of scope — test code; not shipped and not reachable at runtime |
| `tests/test_kart_reader.py` | `grove/kart_reader.py` D7 shape tolerance + C12 lens filtering + log-once on missing DSN / table / column, against a real Postgres | Out of scope — test code; not shipped and not reachable at runtime |
| `tests/test_mcp_auth.py` | grove/mcp_auth.py: token-state durability and the authorization decision | Out of scope — test code; not shipped and not reachable at runtime |
| `tests/test_mcp_client.py` | MCP stdio client helpers | Out of scope — test code; not shipped and not reachable at runtime |
| `tests/test_mcp_process.py` | grove serve process control | Out of scope — test code; not shipped and not reachable at runtime |
| `tests/test_mcp_registry.py` | MCP config reader | Out of scope — test code; not shipped and not reachable at runtime |
| `tests/test_mcp_remote_tools.py` | fleet-awareness / channel-management serve-mode tools + _jsonify | Out of scope — test code; not shipped and not reachable at runtime |
| `tests/test_mcp_subscriptions.py` | SEP-2575 resource-update fan-out | Out of scope — test code; not shipped and not reachable at runtime |
| `tests/test_mcp_serve_oauth_flow.py` | The serve-mode OAuth flow, end to end, through the real Starlette app | Out of scope — test code; not shipped and not reachable at runtime |
| `tests/test_nav_bar.py` | wave 2 nav targets | Out of scope — test code; not shipped and not reachable at runtime |
| `tests/test_nestor_client.py` | `grove/nestor_client.py` subprocess wrapper, absent-binary graceful path, verbatim-refusal guard | Out of scope — test code; not shipped and not reachable at runtime |
| `tests/test_panes_home.py` | desk render + home grid cells | Out of scope — test code; not shipped and not reachable at runtime |
| `tests/test_panes_knowledge.py` | KB search helpers | Out of scope — test code; not shipped and not reachable at runtime |
| `tests/test_panes_knowledge_mount.py` | Knowledge pane search regression | Out of scope — test code; not shipped and not reachable at runtime |
| `tests/test_panes_mcp.py` | MCP pane messages + mount regression | Out of scope — test code; not shipped and not reachable at runtime |
| `tests/test_panes_projects.py` | projects SOIL helpers | Out of scope — test code; not shipped and not reachable at runtime |
| `tests/test_panes_providers.py` | provider registry read | Out of scope — test code; not shipped and not reachable at runtime |
| `tests/test_panes_settings.py` | consent I/O | Out of scope — test code; not shipped and not reachable at runtime |
| `tests/test_panes_user_todos.py` | My Desk markup regression | Out of scope — test code; not shipped and not reachable at runtime |
| `tests/test_persona_roster.py` | `grove/persona_roster.py` locate + load + get/all/by_role + schema-drift ValueError + log-once absent-file path | Out of scope — test code; not shipped and not reachable at runtime |
| `tests/test_security_audit_scope.py` | SECURITY_AUDIT.md's scope table must be a bijection with the tree it audits | Out of scope — test code; not shipped and not reachable at runtime |
| `tests/test_theme_textual.py` | grove palette → Textual CSS helpers | Out of scope — test code; not shipped and not reachable at runtime |
| `tests/test_think_map.py` | Think Map P0 store/validate + outline | Out of scope — test code; not shipped and not reachable at runtime |
| `tests/test_tool_scopes.py` | per-tool grove:read/grove:write OAuth scope enforcement | Out of scope — test code; not shipped and not reachable at runtime |
| `tests/test_transport_security.py` | G-REBIND-01 host/origin allowlist | Out of scope — test code; not shipped and not reachable at runtime |
| `tests/test_u2u_trust.py` | u2u verify-before-consent, consent matrix, key rotation | Out of scope — test code; not shipped and not reachable at runtime |
| `tests/test_upstream_steward.py` | Grove read-only upstream steward consumer | Out of scope — test code; not shipped and not reachable at runtime |
| `tests/test_user_board.py` | My Desk aggregation | Out of scope — test code; not shipped and not reachable at runtime |
| `tests/test_vitals.py` | Tests for vitals strip helpers | Out of scope — test code; not shipped and not reachable at runtime |
| `tests/test_widgets_hero.py` | tests/test_widgets_hero.py | Out of scope — test code; not shipped and not reachable at runtime |
| `tests/test_widgets_hero_scene.py` | tests/test_widgets_hero_scene.py | Out of scope — test code; not shipped and not reachable at runtime |
| `u2u/__init__.py` | Empty package marker (0 bytes) | Scanned |
| `u2u/consent.py` | U2U consent gate — allow/deny/pending logic | Reviewed |
| `u2u/contacts.py` | U2U contact store — ~/.willow/grove_contacts.json | Scanned |
| `u2u/dispatcher.py` | U2U inbound packet dispatcher — routes by type to registered handlers | Scanned |
| `u2u/identity.py` | u2u/identity.py | Reviewed |
| `u2u/listener.py` | U2U TCP listener — asyncio server, port 8550 by default | Reviewed |
| `u2u/packets.py` | U2U packet format — U2U-WIRE-1. Signed JSON, newline-delimited | Reviewed |
| `u2u/sender.py` | U2U outbound packet sender — sign and deliver over TCP | Scanned |
| `widgets/__init__.py` | Empty package marker (0 bytes) | Scanned |
| `widgets/_hero_state.py` | Shared runtime state between hero widgets | Scanned |
| `widgets/card_builder_modal.py` | scripted v1 card builder wizard | Scanned |
| `widgets/card_store.py` | SOIL-backed card definitions + built-in Home cards | Scanned |
| `widgets/content_stack.py` | center pane swapper for nav targets | Scanned |
| `widgets/context_panel.py` | left rail; DeskPane on Home only | Scanned |
| `widgets/hero.py` | Animated willow tree hero widget | Scanned |
| `widgets/hero_db.py` | SQLite state store for hero easter eggs | Scanned |
| `widgets/hero_scene.py` | HeroScene: willow tree + info panel + full-width meadow | Scanned |
| `widgets/nav_bar.py` | NavBar with 1–7 targets + vitals line | Scanned |

130 tracked source files: 14 Reviewed, 74 Scanned, 42 out of scope (`tests/`).

---

## Rubric Results

| # | Check | Status | Finding |
|---|---|---|---|
| R1 | SQL injection via f-string/identifier concat | ⚠️ P3 | `grove_db.py:75,110,111` interpolate `SCHEMA` into `SET search_path` / `CREATE SCHEMA`. `SCHEMA` is the module constant `"grove"` (`grove_db.py:17`), never request data, so there is no injection path today. All value binding elsewhere uses `%s`. Code smell only — see G-SQL-02. |
| R2 | Shell injection — `os.system`, `shell=True` | ✅ PASS | No `os.system`, no `shell=True`, no `bash -c` anywhere in the tree. The seven `subprocess` call sites (`panes/git.py:22`, `panes/prs.py:23`, `panes/providers.py:134,146`, `grove/apps/mcp_process.py:103`, `grove/mcp_local.py:801,807`) all pass argument lists. |
| R3 | Path traversal — file ops accepting `../` or absolute | ✅ PASS | File paths derive from `Path.home()`, `Path(__file__)`, or env vars set by the operator. No request- or message-derived path reaches a file operation. |
| R4 | Hardcoded credentials in VC | ✅ PASS | No secrets in source. OAuth tokens are generated with `secrets.token_urlsafe(32)` (`grove/mcp_auth.py`) and stored under `~/.willow/`. U2U keys are generated per host (`u2u/identity.py`). |
| R5 | CORS / network exposure of the MCP server | ✅ PASS (was ⚠️ P2) | **Corrected, then fixed.** Serve mode is *not* localhost-only by design, and `_transport_security` used to disable DNS-rebinding protection outright whenever `GROVE_MCP_URL` was `https://` — the intended tunnel deployment — leaving no Host or Origin check there. Now the tunnel host and origin are allowlisted alongside loopback and protection is on in every configuration. The approval click (G-OAUTH-01) remains the access control; this restores the transport check that was supposed to sit under it. See G-REBIND-01. |
| R6 | XSS — untrusted values rendered into HTML | ✅ PASS | The repo does have one HTML surface — the `/grove-approve` consent page in `grove/mcp_local.py`. It renders `client_name`, `redirect_uri` and scopes, all supplied by whoever registered the client, and escapes them with `html.escape`. `client_id` and the `pending` key are server-generated. (The 2026-05-06 "no web frontend" rating was wrong about the page's existence, though the page was unreachable at the time.) |
| R7 | Unsigned/unverified code execution | ✅ PASS | No task-executor in this repo. The `subprocess` sites in R2 run fixed binaries (`git`, `willow`, the configured MCP command, `python3 -m grove.mcp_local`). |
| R8 | Missing auth on MCP tools | ⚠️ P2 (was P0) | **Corrected.** PKCE was implemented and *is* enforced (S256, by the SDK token handler), but PKCE binds a code to the requester — it does not decide whether a requester should get one. Until this branch, `authorize()` issued a code unconditionally, so open dynamic client registration plus one `/authorize` call yielded a 30-day full-scope `grove` token to any caller. The consent page existed but nothing routed to it. Fixed: approval is now required by default, auto-approve is an explicit opt-in. See G-OAUTH-01. Residual P2: registration remains open and unbounded — G-REG-01. |
| R9 | Bare `except` swallowing security-critical errors | ⚠️ P2 | 140 `except Exception` handlers across 38 files. The security-relevant ones: `grove_db.py:86` (silent rollback failure on connection release — possible leak), `grove_db.py:633` (rollback failure returns `{}`, caller cannot distinguish from "no data"), `grove_db.py:682,701` (silent `pass` in channel seeding), `panes/settings.py:95` (a consent-toggle write that fails is silently not persisted), `u2u/packets.py:70` (`Packet.validate` returns `False` on any exception — fails closed, acceptable). See G-EXC-01. |
| R10 | Predictable temp paths, world-readable state | ✅ PASS (was FAIL) | **Corrected.** `~/.willow/grove_mcp_token` holds live bearer tokens and was written with `Path.write_text` at the default umask — mode 0644 on a normal box — and non-atomically. Fixed on this branch: created 0600 via `os.open(..., O_EXCL, 0o600)` and installed with `os.replace`. See G-TOK-01. `/tmp` is used only by `hero_test.py` (a developer harness, log file only) and by test fixtures. |
| R11 | Race conditions / missing locks | ✅ PASS | `grove_db.py` uses `ThreadedConnectionPool` behind a double-checked `threading.Lock`. `grove/mcp_local.py` guards `_subscriptions` with `_subscriptions_lock` and hands NOTIFY payloads to the event loop via `run_coroutine_threadsafe`. Token-file writes are now atomic (G-TOK-01). |
| R12 | `safe_integration.py` status() correctness | ✅ N/A | No `safe_integration.py`; the manifest declares `local: true`, so no SAFE gate is required. |
| R13 | Entry point in manifest is importable | ✅ PASS | `entry_point: "willow-grove:app"`; `app.py` imports clean. |
| R14 | `requirements.txt` with pinned deps | ✅ PASS (was P2) | **Corrected — resolved upstream.** Every dependency has had a floor and a ceiling since `3ab5691` (2026-07-27), including `cryptography>=42.0.0,<50` and `mcp>=1.28.1,<2.0.0`. G-DEP-01 is closed. |
| R15 | No hardcoded developer home paths | ❌ FAIL (was PASS) | **Corrected.** `run_mcp.sh:13` defaults the interpreter to `/home/sean-campbell/github/willow-2.0/.venv-dev/bin/python3`; `.cursor/hooks/run_grove_followup.sh` defaults `WILLOW_PG_USER` to `sean-campbell`; `.mcp.json` hardcodes six absolute paths under `/home/sean-campbell/`. Python source is clean — the old rating appears to have scanned `*.py` only. See G-PATH-01. |
| R16 | Signature verification on inbound U2U packets | ⚠️ P2 | New check. `u2u/listener.py` verifies Ed25519 signatures (`Packet.validate`) only on the ALLOW path. The DENY and PENDING paths dispatch attacker-supplied header content to `dispatcher.dispatch` *before* any signature check, so an unauthenticated peer can put a chosen `from` address in front of the user as a KNOCK. See G-U2U-01. |
| R17 | Untrusted content reaching an agent's instruction stream | ⚠️ P2 | New check. `.cursor/hooks/grove_followup.py` formats Grove message bodies into `followup_message`, which the editor feeds to an agent as a turn. Message bodies come from any Grove sender. See G-HOOK-01. |

---

## Findings

### G-OAUTH-01 — `/authorize` Issued Tokens With Nobody Asked (P0 — Fixed on this branch)

**File:** `grove/mcp_auth.py`, `grove/mcp_local.py`
**Status:** Fixed in `claude/oauth-approve-and-audit-honesty`

Before the fix, three things composed into an open token dispenser:

1. `register_client()` persisted any client presented to it, with no validation
   and no operator involvement, and `ClientRegistrationOptions(enabled=True)`
   exposed that over the network.
2. `authorize()` called `issue_code()` immediately and redirected to the
   client's own callback. The `/grove-approve` page — about 55 lines of working
   consent UI — was never linked to by anything and could not be reached.
3. The resulting access token carried the full `grove` scope for 30 days
   (`_ACCESS_TTL`).

So `POST /register` followed by `GET /authorize` yielded a 30-day token to any
caller who could reach the server, with no human in the loop. The module
docstring described a flow ("USER opens that URL in a browser, clicks Allow")
that the code did not perform, which is why this survived review.

The remaining control was the 127.0.0.1 bind — undercut by R5/G-REBIND-01 in
exactly the tunnelled configuration the serve mode exists for.

**Fix:** `authorize()` now parks the request and redirects to
`/grove-approve?pending=<key>`; only the human clicking Allow calls
`issue_code()`. Unattended approval survives as an explicit opt-in,
`GROVE_MCP_AUTO_APPROVE=1`, which is off by default and prints a warning at
startup and on every grant. Parked requests expire after 10 minutes and their
keys are one-shot. Docstrings in both files now describe what the code does.

**Residual risk:** an operator who sets `GROVE_MCP_AUTO_APPROVE=1` on a
tunnelled server is back to the original exposure. That is now a deliberate,
named, logged choice rather than the default.

---

### G-TOK-01 — Bearer-Token File Was World-Readable, Non-Atomic, and Failed Open (P1 — Fixed on this branch)

**File:** `grove/mcp_auth.py` — `_save_state`, `_load_state`
**Status:** Fixed in `claude/oauth-approve-and-audit-honesty`

`~/.willow/grove_mcp_token` holds live access and refresh tokens. Three defects:

1. **Mode.** `Path.write_text` creates at the default umask — 0644 on a typical
   box. Any local user could read the tokens. `u2u/identity.py:24` already had
   the correct pattern (`os.open(..., 0o600)`) in the same repo.
2. **Atomicity.** A single in-place `write_text` truncates first. A crash or a
   full disk mid-write leaves a truncated file.
3. **Failing open.** `_load_state` caught every exception and returned an empty
   state. Combined with (2): a truncated file read back as "no clients, no
   tokens", every client silently deregistered, and the next `_save_state`
   wrote that loss to disk permanently. The operator's only symptom was clients
   mysteriously needing to re-auth — with the evidence already overwritten.

**Fix:** writes go to a fresh `os.open(..., O_CREAT|O_EXCL, 0o600)` temp file,
are fsynced, and are installed with `os.replace`, which is atomic and carries
the temp file's mode — so the result is 0600 even when overwriting a
pre-existing 0644 file. `_load_state` distinguishes *absent* (start empty,
quietly) from *unreadable* (raise `TokenStateError`, naming the file and saying
to move it aside). Corrupt bytes are left on disk for inspection.

Covered by `tests/test_mcp_auth.py`.

---

### G-REBIND-01 — DNS-Rebinding Protection Disabled in the Deployment That Needs It (P2)

**File:** `grove/mcp_local.py` — `_transport_security`
**Status:** Fixed in `claude/g-rebind-01`

Was:

```python
if _BASE_URL.startswith("https://"):
    return TransportSecuritySettings(enable_dns_rebinding_protection=False)
```

The comment says the tunnel edge may forward `Host: 127.0.0.1:8765`, which is a
real problem. The fix chosen was to switch the check off entirely rather than to
allowlist the tunnel's hostname, so the https deployment has no Host or Origin
validation at all. A page in the operator's browser can therefore issue
cross-origin requests to the server, and any party who learns the tunnel URL
reaches it directly.

This was survivable only because it was paired with an approval click — which,
until G-OAUTH-01, was not there.

**Fixed** as recommended: the allowlist is derived from `GROVE_MCP_URL` — that
host and origin plus the loopback set — and `enable_dns_rebinding_protection` is
now `True` in every configuration. Loopback stays on the list precisely because
the edge may forward `Host: 127.0.0.1:8765`; that case wanted both entries
allowlisted, never the check removed. A malformed or hostless `GROVE_MCP_URL`
adds nothing rather than falling back to permissive — an address that cannot be
parsed is not a grant.

**Follow-up (`claude/grove-adaptor-remote-restore`):** the allowlist gained an
operator escape hatch for tunnels (Pangolin/Newt, reverse proxies) that forward
a Host other than loopback or the `GROVE_MCP_URL` netloc:
`GROVE_MCP_EXTRA_HOSTS` / `GROVE_MCP_EXTRA_ORIGINS` (comma-separated). These are
read once at import time from the environment only — never from a request or
header — so they are operator-set, not attacker-influenced. They are purely
additive: `enable_dns_rebinding_protection` stays `True`, and a bare `*` / `:*`
entry cannot match a real Host header, so the mechanism cannot reach an
allow-all state. Covered by `tests/test_transport_security.py`
(`test_extras_never_disable_protection`, `test_blank_and_empty_extras_add_nothing`).

Pinned by `tests/test_transport_security.py`, whose headline assertion is that
there is no configuration in which protection is off. It is parametrised over
the https, http, unset, and unparseable cases, and every https case fails
against the previous code.

---

### G-REG-01 — Dynamic Client Registration Is Open and Unbounded (P2)

**File:** `grove/mcp_auth.py` — `register_client`
**Status:** Open

```python
async def register_client(self, client_info):
    self._state["clients"][client_info.client_id] = client_info.model_dump(mode="json")
    self._save_state()
```

Any caller can register, with no cap, no expiry and no pruning; each
registration is written to disk. Registrations are never removed, so the token
file grows without bound and an operator reviewing it cannot tell a real client
from noise.

With G-OAUTH-01 fixed, registration alone grants nothing — a human still has to
approve. So this is a durability and reviewability problem rather than an access
one. It becomes access-relevant again under `GROVE_MCP_AUTO_APPROVE=1`.

**Recommended fix:** cap the client table, expire registrations that never
completed an authorization, and reject `redirect_uri`s outside an operator-set
allowlist.

---

### G-U2U-01 — Unverified Packets Reach the Dispatcher (P2)

**File:** `u2u/listener.py:62-84`
**Status:** Open — observed at `27e123a`; `u2u/` is under concurrent change on
another branch, so re-check before acting.

`Packet.validate` — the Ed25519 signature check — runs only after the consent
gate returns ALLOW:

```python
result = self._consent.check(sender_addr, ptype)
if result == ConsentResult.DENY:
    if ptype == PacketType.NOTE:
        dispatcher.dispatch({"header": {**packet["header"], "_denied": True}, ...})
    return
if result == ConsentResult.PENDING:
    dispatcher.dispatch({"header": {**packet["header"], "_pending": True}, ...})
    return

contact = self._consent.get_contact(sender_addr)
if not contact or not Packet.validate(packet, contact.public_key_hex):
    return
```

`sender_addr` is read straight out of the packet header. On the PENDING path
(an unknown sender's KNOCK, which is by definition unauthenticated) the header
*and payload* are dispatched into the UI. Anyone who can reach TCP 8550 can put
a chosen `from` address and payload in front of the user as an approval prompt,
which is the exact moment the user is deciding whom to trust.

There is no key to check a KNOCK against — that is what a KNOCK is for — so the
fix is not "verify it too".

**Recommended fix:** make the unauthenticated path visibly unauthenticated. The
KNOCK is self-signed; verify it against the key *carried in the packet* and show
the user that key's fingerprint, so the identity they approve is the identity
that later packets must match. Mark denied/pending dispatches as unverified all
the way through to the UI.

---

### G-HOOK-01 — Grove Message Bodies Enter an Agent's Turn (P2)

**File:** `.cursor/hooks/grove_followup.py:93-108`
**Status:** Open

The stop hook formats unread Grove messages into `followup_message`, which the
editor delivers to an agent as a new turn:

```python
snip = body[:80] + ("…" if len(body) > 80 else "")
lines.append(f"- #{ch} id={r['id']} | {r.get('sender', '?')}: {snip}")
...
_emit({"followup_message": msg})
```

`body` and `sender` are whatever a Grove sender wrote. Content is truncated and
newlines are stripped, which limits but does not prevent instruction-shaped text
reaching the agent — and the agent holds the developer's tool permissions.

**Risk:** low today (Grove senders are fleet-local), and it is the same trust
boundary the fleet already accepts for agent-to-agent messaging. Recorded
because it is the one place message content crosses from data into instructions.

**Recommended fix:** fence the block explicitly as untrusted quoted data in the
followup text, and drop the `sender` field's ability to impersonate the frame.

---

### G-EXC-01 — Silent Exception Swallowing (P2)

**File:** `grove_db.py:86,633,682,701`; `panes/settings.py:95`
**Status:** Open

Line numbers corrected — the 2026-05-06 revision cited `grove_db.py:87,499,548`,
which do not correspond to the handlers described.

```python
# grove_db.py:84-88 — rollback failure ignored; connection returned to the pool anyway
except Exception:
    pass

# grove_db.py:629-635 — rollback failure returns {}, indistinguishable from "no row"
except Exception:
    conn.rollback()
    return {}

# panes/settings.py:94-95 — a consent toggle that fails to persist reports success
except Exception:
    pass
```

The count is 140 `except Exception` handlers across 38 files (not 166). Most are
UI-refresh guards and are fine; the ones above hide connection leaks, data loss,
and a consent setting that silently did not take.

**Fix:** log before swallowing, and let `panes/settings.py` surface a write
failure to the user rather than returning as if the toggle stuck.

---

### G-SQL-02 — f-string Schema Identifier in DDL (P3)

**File:** `grove_db.py:75, 110, 111`
**Status:** Open (code smell)

```python
cur.execute(f"SET search_path = {SCHEMA}, public")
cur.execute(f"CREATE SCHEMA IF NOT EXISTS {SCHEMA}")
```

`SCHEMA` is the module-level constant `"grove"` (`grove_db.py:17`). Identifiers
cannot be parameterised with `%s`, so an f-string is the normal approach — but
if `SCHEMA` ever becomes configurable, these are the three lines that turn into
an injection. Supersedes G-SQL-01, which pointed at a file this repo does not
contain.

**Fix:** wrap with `psycopg2.sql.Identifier`, which quotes correctly and stays
correct if the constant becomes a setting.

---

### G-PATH-01 — Hardcoded Developer Home Paths (P3)

**Files:** `run_mcp.sh:13`, `.cursor/hooks/run_grove_followup.sh:8`, `.mcp.json`
**Status:** Partially fixed — `run_mcp.sh` done in `claude/grove-adaptor-remote-restore`
(the hardcoded `/home/sean-campbell/...` default is gone; it now resolves
`$GROVE_VENV` → repo `./.venv` → `PATH` and warns when the MCP SDK is absent).
`.cursor/hooks/run_grove_followup.sh` and `.mcp.json` remain open.

`run_mcp.sh` falls back to `command -v python3` when the hardcoded venv is
missing, so it degrades rather than breaking, and `.mcp.json` is developer-local
configuration. Not a vulnerability; a portability and provenance defect, and
directly contradicts the previous revision's R15 PASS.

**Fix:** `run_mcp.sh` should use the same `find_python` candidate search
`run_dev.sh` already has. `.cursor/hooks/run_grove_followup.sh` should default
`WILLOW_PG_USER` to `${USER}` as `run_dev.sh` does.

---

## Corrections to the 2026-05-06 revision

| Claim | Status |
|---|---|
| Scope row `grove_serve.py` — "Full" coverage | **Withdrawn.** File is not in this repo (cut to `willow-2.0`; see `grove_db.py:333`). |
| Scope row `kart_worker.py` — "Full" coverage | **Withdrawn.** File is not in this repo. |
| Scope "Total Python files ~45" | **Wrong.** 117 tracked `*.py` (81 excluding `tests/`), plus 4 `*.sh`. |
| `u2u/`, `bridge/` unmentioned | **Fixed.** Both in the scope table; new checks R16/R17 and finding G-U2U-01. |
| G-SHL-01 — `kart_worker.py:144` `bash -c` (P1) | **Withdrawn.** No `bash -c`, no `shell=True`, no `os.system` in this repo. |
| G-KART-01 — unsigned Kart tasks (P1) | **Withdrawn.** No Kart worker in this repo. `panes/tasks.py` reads the queue; it does not execute. |
| G-SQL-01 — `grove_serve.py:306` (P2) | **Withdrawn**, superseded by G-SQL-02 against a file that exists. |
| G-DEP-01 — unpinned deps (P2) | **Closed.** Resolved by `3ab5691`. |
| G-EXC-01 line numbers `87, 499, 548`; "166 `except Exception`" | **Corrected** to `86, 633, 682, 701` and 140. |
| R4 — "tokens generated with `secrets.token_hex(32)`" | **Corrected** to `secrets.token_urlsafe(32)`. |
| R5 — "Serve mode is localhost-only by design" | **Corrected to P2.** Host checking is disabled for the https deployment. See G-REBIND-01. |
| R6 — "No web frontend. Textual TUI only." | **Corrected to PASS-with-a-frontend.** `/grove-approve` is an HTML page; it renders registrant-supplied values and now escapes them. |
| R8 — "PASS — implements OAuth 2.0 PKCE (token-gated)" | **Corrected.** PKCE was real; authorization was not. Was P0, now P2 residual. See G-OAUTH-01. |
| R10 — "PASS — token files use `Path.home()/.willow`" | **Corrected.** Location was fine; mode (0644) and atomicity were not. See G-TOK-01. |
| R15 — "No `/home/sean-campbell/` in source" | **Corrected to FAIL.** Three files carry it. See G-PATH-01. |
| Summary — "P0 0 — OAuth PKCE on the MCP server is correctly implemented" | **Withdrawn.** Two P0/P1s existed at the time of writing (G-OAUTH-01, G-TOK-01), both in the file the sentence certified. |

---

## Summary

| Priority | Count | Items |
|---|---|---|
| P0 | 0 open (1 fixed) | G-OAUTH-01 — fixed on `claude/oauth-approve-and-audit-honesty` |
| P1 | 0 open (1 fixed) | G-TOK-01 — fixed on `claude/oauth-approve-and-audit-honesty` |
| P2 | 5 | G-REBIND-01 (host check disabled behind https), G-REG-01 (open unbounded registration), G-U2U-01 (unverified packets dispatched), G-HOOK-01 (message bodies into an agent turn), G-EXC-01 (silent exceptions) |
| P3 | 2 | G-SQL-02 (f-string schema identifier), G-PATH-01 (hardcoded home paths) |

The two serious findings were both in `grove/mcp_auth.py` — the file the
previous revision rated PASS. Both are fixed on this branch and pinned by
`tests/test_mcp_auth.py` and `tests/test_mcp_serve_oauth_flow.py`, which
exercise the assembled Starlette app — the consent page was unreachable for as
long as nothing did.

The highest-value open item is **G-REBIND-01**: the serve mode is designed to be
tunnelled, and in that configuration the transport has no host check. It is now
gated by a human approval click, so it is no longer an open dispenser, but the
listener is still reachable by anyone who learns the URL.

`u2u/` and `bridge/` (G-U2U-01) are **Scanned, not Reviewed**. They make the
repo's only cryptographic trust decisions and deserve a dedicated pass; treat
the coverage level in the scope table as the honest ceiling on what this
document establishes about them.

---

*ΔΣ=42*
