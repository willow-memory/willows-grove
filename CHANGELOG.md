# Changelog

All notable changes to Willow Grove are documented here.

## [Unreleased]

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
