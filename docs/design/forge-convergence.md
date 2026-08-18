# Forge checkpoint decisions in the Grove dashboard

b17: WGRV1 ΔΣ=42
Status: **PROPOSED** — Heimdallr proposes, USER ratifies (CLAUDE.md rule 5). No code changed by this note.

## The convergence

Two systems independently grew the same shape: *work that must pause
automation until a human acts.*

- **Forge** (`forge/checkpoint_governance.py` → `forge/human_loop.py` →
  `forge/soil_store.py`): a model reaches a decision with no human present,
  calls `park_decision()`, which `enqueue()`s a `human_required` row
  (`kind=attestation`) plus a structured `parked_decisions` sidecar, into a
  **per-builder JSON file** (`<root>/<builder_id>.soil.json`). Filesystem
  only. A human later calls `resume_checkpoint`, which reads the parked
  decision and seals+attests it (`attested_by` bound to the caller's
  identity, never free text — anti-forgery is structural, D-HL-3).
- **Grove**: `grove_reader.human_required_queue()` reads
  `public.human_required_queue` in Postgres, priority-first then newest.
  `panes/human.py` renders it as the dashboard's Human pane. willow-mcp's
  `grove_human_required` tool (`grove_tools.py:491`) exposes the same read
  to agents.

Same vocabulary (`kind`, `priority`, `source_agent`, `source_ref`, `status:
open/resolved/dismissed/acknowledged`), same intent, **zero connection**. A
checkpoint parked by the Forge today is invisible to Grove and to the human
at the dashboard — visible only via `checkpoint_governance.py queue
<builder_id>` on the Forge side.

## Current state: two stores, same shape, no bridge

```
Forge  → park_decision() → human_loop.enqueue() → SOIL (*.soil.json, per builder, filesystem)
Grove  ← human_required_queue() ← public.human_required_queue (Postgres, fleet-wide)
```

No process reads one and writes the other. Convergence means: a Forge-parked
item shows up as a row in `panes/human.py`, and a human resolving it in the
dashboard (or via `grove_human_required`) is legible back to the Forge as
`resolve_item()`.

## Constraints

1. **Forge is dependency-free by design.** It cannot gain a hard Postgres
   dependency — that's why `human_loop` was vendored over an injected SOIL
   store instead of importing willow-mcp's Postgres-backed original (see
   `forge/human_loop.py` vendor note). Any bridge lives outside Forge.
2. **Grove reads, it doesn't decide.** `grove_reader.py` is read-only by
   repo rule (Rule 3); it must not resolve a Forge checkpoint itself.
   Resolution has to round-trip back through Forge's own `resolve_item()`
   so the attestation stays keyed to the Forge's `builder_id` / `pair_id`.
3. **The attestation must stay non-forgeable.** `attested_by` is bound to
   the calling identity inside `forge/human_loop.py`, never free text
   (D-HL-3). A bridge must not let a sync process "attest on behalf of" a
   human — it may only *surface* parked items and *carry back* a
   resolution a human actually performed.
4. **`apps/the-forge/` never imports the governance layer.** Whatever does
   the syncing runs with the Forge's own trust, not a sandboxed build's.

## Proposed path: one-way sync, SOIL → Postgres, Grove stays read-only

The simplest convergence that respects all four constraints:

- **Direction:** SOIL → Postgres only, for the *park* half. Forge keeps
  writing to its own filesystem store exactly as today — no new Forge
  dependency. A small, separately-owned sync process (not inside
  `forge/`, not inside `apps/the-forge/`) periodically reads each
  builder's `human_required` collection via `checkpoint_governance.open_items()`
  and upserts rows into `public.human_required_queue`, tagged
  `source_agent="the-forge"`, `source_ref` carrying the Forge's
  `builder_id:item_id` so the row is traceable back to its origin file.
- **Resolution direction:** Postgres → SOIL, also one-way, also outside
  Forge. When a human resolves the synced row in Grove (dashboard action
  or `grove_human_required` write path, once one exists), the same sync
  process calls `checkpoint_governance.resolve_item(builder_id, item_id,
  resolved_by=<human>, ...)` against the Forge's SOIL file — never Grove
  or Postgres writing the attestation directly.
- **Grove stays exactly as it is** (`grove_reader.py` read-only,
  `panes/human.py` renders whatever's in `public.human_required_queue`) —
  it does not know or care that some rows originated in SOIL.
- **Dedup / idempotency:** the sync's upsert key is `(source_agent,
  source_ref)`, mirroring the dedup `route_nudge()` already does inside
  Forge — a re-synced item never piles up as a second open row.

Rejected: *Forge writing directly to `grove.human_required_queue`* — a
hard Postgres dependency inside the dependency-free core (constraint 1).

Rejected: *a shared reader interface Grove calls into Forge's SOIL files
directly* — works for read-only display but breaks constraint 2 the
moment anyone resolves from the dashboard; a write path back into SOIL is
needed regardless, so a reader-only interface just defers the harder half.

## Open question for USER ratification

Where does the sync process live — a script under `stores/` in
safe-app-store (closest to Forge), a Grove-side poller, or a third,
neutral location? This note takes no position; it fixes only the
direction (SOIL → Postgres for parks, Postgres → SOIL for resolutions)
and the non-negotiables above.
