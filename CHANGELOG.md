# Changelog

All notable changes land here per INVARIANTS.md §3. Format follows Keep a Changelog v1.1.0.

## [Unreleased]

### Changed
- Three-state discipline landed for every /api/* endpoint and every Web Component (INVARIANTS.md §1). Supersedes D7's implicit read of "absence is a state" (INVARIANTS.md §2).
- `<grove-envelope-panel>` default `data-source` moved to `/api/envelopes` — the served page now consumes the live envelope registry, not the fixture harness's JSON. Fixture-based rendering is opt-in via an explicit `data-source` attribute (harness use only). INVARIANTS.md §8.

### Added
- INVARIANTS.md — single source of truth for Grove discipline.
- INVARIANTS.md §5 "Trust order" — signature → consent → dispatch, in exactly that sequence, with the contact-store rules that protect the state consent depends on.
- INVARIANTS.md §6 — "Manifests describe code, not aspirations" (Grove v0.9 PR 7). Tests enforce.
- INVARIANTS.md §7 — "Consent flows are real, not automatic" (Grove v0.9 PR 6). Names the /grove-approve loopback POST discipline, the 5-min pending TTL, the 24-hour access TTL, and the tunnel-acknowledgement flag.
- INVARIANTS.md §8 — "Panels consume live endpoints by default" (Grove v0.9 PR 2). Every Web Component consumes its matching `/api/*` endpoint by default; fixture-based rendering is opt-in (harness use only); the served page renders live state, not curated data.
- `window.groveNestorAsk(claim)` now handles the `state="unreachable"` branch distinctly — summons a subdued `<grove-refusal-chip>` in a new `mode: "unreachable"` variant so the operator sees when the L4 Nestor seam is down instead of the 503 being swallowed silently. INVARIANTS.md §1 + §8.
- `<grove-refusal-chip>` gains a `mode` field: `"refusal"` (default, verbatim Nestor speech act) or `"unreachable"` (dashed border + subdued render, distinct from a real refusal). V5 discipline is unchanged for the `refusal` mode.
- `tests/test_panel_wiring.py` — pins the three-state shape end-to-end for every endpoint the panels consume: `/api/envelopes`, `/api/nestor/decide`, `/api/dispatch`, `/api/journal/recent`. INVARIANTS.md §1 + §8.
- `tests/test_refusal_summon_shape.py` — pins the refusal-summon boot module's contract with the chip: POSTs to `/api/nestor/decide`, dispatches `nestor-refusal` on `refused`, dispatches the same event with `mode: "unreachable"` on 503/state=unreachable.
- CHANGELOG.md — reorganized under Keep a Changelog v1.1.0; earlier per-branch entries preserved below as historical work.
- docs/design/u2u-security-limits.md — new doc naming what u2u guarantees (authenticity, integrity, non-repudiation within signing-key boundary) and what it does not (confidentiality). Cites `u2u/packets.py:74-75`. Encryption planned for Gate 6.
- tests/test_manifest_honesty.py — pins INVARIANTS.md §6 for `safe-app-manifest.json`.
- tests/test_readme_honesty.py — pins INVARIANTS.md §6 for the README's u2u row.
- `tests/test_serve_mode_identity.py` — pins `_detect_serve_mode` injectability, `_resolve_serve_identity` (verified / missing / malformed / unknown-scopes cases with log-once), and the serve branch of `_gate` denying when identity resolves to None. Fills the CODE_REVIEW.md P1 gap ("serve mode ... has zero tests").
- `tests/test_grove_approval_page.py` — pins `/authorize` never issuing a code, the approval page rendering the client + scope + redirect, loopback-only completion, non-loopback POST refused (403), 5-min pending expiry, and DNS-rebinding-protection invariants on the transport allowlist.

### Fixed
- safe-app-manifest.json: dm_conversations no longer claims encryption; u2u is signed-not-encrypted (CODE_REVIEW.md P0 corrected).
- README.md: u2u description corrected to match code.
- docs/design/u2u-security-limits.md: new doc naming what u2u guarantees and what it does not.
- u2u: verify signature before consulting consent for every packet type (was: PENDING KNOCKs dispatched unverified — CODE_REVIEW.md P0). The invariant is now anchored at INVARIANTS.md §5 and pinned by name in `tests/test_u2u_consent_order.py`.
- u2u: `contacts.update_key()` preserves blocked and consent flags on rotation; `bridge/app.py` no longer resets state via `contacts.add()`. Rotation now defaults closed — the caller MUST pass `require_confirmation=False` to attest that a human authorised the key change, and the refusal is logged.
- u2u: REPLY packets require a correlated outstanding thread_id — the `ALLOW`-unconditional path is gone, and a REPLY without a live `open_thread` entry is DENY, per INVARIANTS.md §5.
- `grove/mcp_auth.py`: `authorize()` no longer auto-issues codes; wired to the /grove-approve page (CODE_REVIEW.md P0). The `GROVE_MCP_AUTO_APPROVE` env-var escape hatch and the `auto_approve` constructor arg are removed — there is no unattended-approve path. INVARIANTS.md §7.
- `grove/mcp_local.py`: DNS-rebinding protection stays on regardless of scheme; ngrok carve-out removed (CODE_REVIEW.md P0). The `/grove-approve` POST that completes a grant is refused unless the peer is on 127.0.0.1/::1/localhost — the operator has to be on the box. A non-loopback `GROVE_MCP_URL` without `WILLOW_MCP_TUNNEL_ACKNOWLEDGED=1` logs a WARNING at startup. INVARIANTS.md §7.
- `client_registration.enabled` disabled by default; explicit enrollment required via `GROVE_MCP_ALLOW_DYNAMIC_REGISTRATION=1`. Closes CODE_REVIEW.md P0 ("unvalidated register_client"). INVARIANTS.md §7.
- `_ACCESS_TTL` reduced from 30 days to 24 hours; `_PENDING_TTL` from 10 minutes to 5 minutes. Bounded for the operator seat per INVARIANTS.md §7.
- `_SERVE_MODE` now derives from an injectable `_detect_serve_mode(argv=…)`; the OAuth provider is built via `_build_serve_provider(base_url)`. Makes the serve branch of the gate testable (CODE_REVIEW.md P1). New `_resolve_serve_identity(token)` and `_gate(serve_mode, token)` seams — fail-closed on missing / malformed identity.
- `SECURITY_AUDIT.md`: G-OAUTH-01 residual risk updated to reflect the removed auto-approve path; G-REG-01 closed (dynamic registration off by default). INVARIANTS.md §7.

### Previous work (pre-v0.9)

### feat/grove-per-tool-oauth-scopes
Serve-mode OAuth scopes are now granular instead of one flat `grove` scope that let any remote token call every tool including writes.

- **Two scopes**: `grove:read` and `grove:write`. `grove` remains a back-compat superscope implying both, so a 30-day token minted before this change (or any client that still asks for plain `grove`) keeps full access — nothing needs re-authorizing. `AuthSettings` (`grove/mcp_local.py`): `valid_scopes=["grove", "grove:read", "grove:write"]`, `default_scopes=["grove:read", "grove:write"]` (an ordinary connect still gets full access), `required_scopes=["grove:read"]` (the floor every token must clear).
- **Enforcement point:** `_require_scope()` reads the *current request's* token via the MCP SDK's own auth-context contextvar (`mcp.server.auth.middleware.auth_context.get_access_token()`) — not an ambient flag. It is a no-op whenever that contextvar is empty, which is always true under stdio (no HTTP request ever runs through the SDK's auth middleware there), preserving local Claude Code's implicit trust unchanged.
- **`@writes` decorator** applied to the 9 write tools (`grove_send_message`, `grove_reply`, `grove_flag`, `grove_unflag`, `grove_bus_send`, `grove_bus_delete`, `grove_ack`, `grove_heartbeat`, `grove_create_channel`); it composes cleanly under `@mcp.tool()` because `functools.wraps` preserves `__wrapped__`, which `inspect.signature(..., eval_str=True)` follows by default — the advertised JSON schema and docstring are unaffected (verified in tests, not assumed). Read tools carry no decorator; the server-wide `required_scopes=["grove:read"]` already covers them.
- **`grove/mcp_auth.py`:** `GroveOAuthProvider.load_access_token` now widens a stored `grove`-scoped token to also carry `grove:read`/`grove:write` literally before handing it back — the SDK's transport-level scope gate does exact string membership with no notion of implication, so an old `["grove"]` token would otherwise fail a `required_scopes=["grove:read"]` check. New `effective_scopes()` picks what `/authorize` explicitly requested, else the client's own registered scope (which defaults to `default_scopes` at DCR time), else the superscope — used by `issue_code`, the auto-approve warning, and the `/grove-approve` consent page so the scopes shown there are the granular ones.
- **Tests:** new `tests/test_tool_scopes.py` (22 cases) — the gate's read/refused-write/full-access/no-context matrix, all 9 write tools individually confirmed gated, schema/docstring survival through `@writes`, `_expand_scopes`/`effective_scopes` unit coverage, and a collection-time probe pinning the actual `AuthSettings` wiring in serve mode. Full suite: 362 passing.
- **Docs:** `docs/runbooks/grove.md` remote section documents the two scopes and how a client requests read-only.

### feat/grove-adaptor-remote-restore
Restored the remote-Grove (claude.ai) MCP adaptor and made it tunnel-agnostic so it can be fronted by **Pangolin** (Newt or reverse-proxy) as readily as ngrok/cloudflared/Tailscale Funnel. The serve/OAuth code was healthy but undeployed and unwired; this closes the plumbing gaps.

- **`run_mcp.sh`** no longer defaults to a stale absolute venv path (`/home/sean-campbell/...willow-2.0/.venv-dev`) that silently fell back to bare `python3`. It now prefers `$GROVE_VENV`, then a repo-local `./.venv`, then PATH, and warns loudly when the resolved interpreter cannot import the MCP SDK.
- **Tunnel escape hatch:** `_transport_security()` (`grove/mcp_local.py`) now honours `GROVE_MCP_EXTRA_HOSTS` / `GROVE_MCP_EXTRA_ORIGINS` (comma-separated) so a tunnel that forwards a Host other than loopback or the `GROVE_MCP_URL` netloc can be allowlisted **without disabling DNS-rebinding protection** (which stays on in every deployment).
- **`scripts/grove-serve`** + `deploy/grove-mcp-serve.service.template` + `scripts/mcp_entry_toggle.py`: one-command on/off/status for serve mode, managing the systemd `--user` unit and the local `.mcp.json` entry together (parity with willow-mcp's `willow-serve`). Skill: `skills/grove-serve.md`.
- **New remote tools** (serve-mode MCP surface): `grove_agents` (fleet presence), `grove_fleet_status` (AGENTS-region rows), `grove_mentions`, `grove_human_required` (operator queue), `grove_create_channel` — each wrapping an existing `grove_reader` function, with datetimes coerced to ISO via `_jsonify`.
- **Docs:** `docs/runbooks/grove.md` remote section rewritten for tunnel-agnostic + Pangolin (Newt and reverse-proxy) fronting, the extra-hosts allowlist, and the `/grove-approve` OAuth flow; stale `grove_serve.py` entry-point references fixed in `CLAUDE.md`.
- **Tests:** escape-hatch cases added to `test_transport_security.py`; new `test_mcp_remote_tools.py` covers the five new tools (argument clamping, `@`-stripping, JSON-safety incl. Decimal/set). `test_mcp_serve_oauth_flow.py` now force-reloads the module in serve mode instead of relying on collection order (an earlier plain import elsewhere could otherwise leave it in stdio mode and silently error the OAuth-consent tests). Full suite: 340 passing.
- `_jsonify` also coerces `Decimal` (psycopg2's NUMERIC type) to float and sets to lists, not just datetimes. `SECURITY_AUDIT.md` scope table + G-REBIND-01/G-PATH-01 notes updated for the new files and surface.

### fix/u2u-verify-before-consent
P0 security fix in the u2u trust layer. **Authentication now precedes authorisation.** The listener verified a packet's signature only on the ALLOW path, so consent was decided from an attacker-chosen `from` address and the PENDING branch handed an entirely unverified KNOCK to registered handlers — one unauthenticated TCP packet was enough to install an attacker's public key as trusted. Signatures are now checked for every packet type before consent is consulted; a KNOCK from an unknown peer must be self-verifying against the key in its own payload, and a KNOCK from a known peer is verified against the STORED key, so wire-driven key rotation is impossible.

Consent is now enforced rather than advisory: the unconditional KNOCK/REPLY allow is gone, a REPLY must correlate to an outstanding `thread_id` (which is consumed, so replays fail), and new contacts start with every `consent_*` flag **False** instead of note/ask/share defaulting True. `ContactStore.add()` refuses an address it already knows — re-running the `Contact(...)` constructor silently reset `blocked` and every consent flag — and the new `ContactStore.update_key()` mutates only the key. The bridge's "update key silently" re-KNOCK branch now refuses a mismatched key and logs it.

Docs corrected: u2u was described as "end-to-end encrypted" in `safe-app-manifest.json` and "Encrypted LAN transport" in `README.md`. It is signed, not encrypted — packet bodies are plaintext JSON on the wire. Adding confidentiality remains an open decision. First tests for `u2u/` and `bridge/`: 75 new cases (suite 177 → 252).

**Operator note:** contacts already in `grove_contacts.json` keep their stored flags — only newly admitted contacts start closed. A new contact now delivers nothing until granted, via `ContactStore.set_consent(addr, consent_note=True, ...)`. There is still no TUI surface for granting consent; that gap predates this change.

### feat/routing-feed-panel (PR#3)
Added routing feed panel to dashboard right sidebar. Displays routing decisions from `willow.routing_decisions` table in real-time, showing which agents are receiving work and why. Helps visualize fleet dispatch patterns and troubleshoot routing issues. Replaces static monitoring with live decision feed.

### feat/mention-index (PR#4)
Implemented mention index schema and query layer for Grove. Tracks @-mentions across all channels and correlates them with agent assignments. Enables fast lookup of who mentioned whom and when, supporting mention notifications and mention-based task routing.

### feat/todos-projects (PR#5)
Added Todos and Projects cards to dashboard home grid. Cards render task lists and project status from SOIL local store, with filtering by project and completion status. Integrates with Kart task queue for live task updates. Provides quick-glance project health on home pane.

### feat/binder-dashboard (PR#9)
Launched BinderPane for dashboard. Surfaces SOIL binder state (proposed edges, filed JSONLs, extracted atoms) in a browsable tree. Allows users to inspect and ratify binder output before it lands in KB. Critical for understanding what the fleet extracted and what it decided to keep.

### feat/knowledge-cards-shell (PR#10)
Added KnowledgeRailPreview to dashboard right panel. Clicking an atom now shows its preview (title, summary, domain, depth) alongside the full KB view. Supports quick context lookup without leaving the dashboard. Sets stage for integrated KB search and discovery.

### docs/grove-docs-pass (PR#11)
Documentation refresh for Willow Grove. Added INDEX.md (entry points and architecture overview), KNOWN_GAPS.md (documentation gaps and coverage status), and updated TESTER_ONBOARDING.md. Clarified portless dashboard design, Grove schema, and Postgres entry points. Serves as canonical reference for onboarding and architecture questions.

### audit/2026-05-05 (PR#6)
Security and reliability fixes across auth, UI, and Grove layers. Extended MCP access token TTL from 1 hour to 30 days (eliminates overnight session drops). Fixed unread count relay from ChatPane to ChannelList at App level (CursorAdvanced now bubbles correctly). Added Run Ledger pane for willow.runs observability. Includes markup escaping fix and worker threading improvements.

### fleet-gaps (PR#8)
Hardened FleetManager reliability. Fixed circuit breaker state tracking, added log lock to prevent concurrent writes, and improved stderr capture for fleet health monitoring. Addresses known gaps in fleet process monitoring that were causing race conditions and lost status messages.

### audit/2026-05-06-grove (PR#7)
Level 2 security audit for safe-app-willow-grove. Covers dashboard code, Grove schema, and MCP tool exposure. No P0 findings. P1: dashboard tools expose KB operations without rate limiting (local-only, acceptable). Audit tracking doc for compliance and future hardening.
