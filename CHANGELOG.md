# Changelog

All notable changes to Willow Grove are documented here.

## [Unreleased]

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
