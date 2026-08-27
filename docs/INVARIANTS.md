# Grove Invariants

Single source of truth for the discipline Grove's readers, endpoints,
and Web Components share. Every code-changing PR that reads a source or
paints a state cites a section here by anchor, not by line number.

Load-bearing constraint (Constraint 1, DESIGN_CONSTRAINTS.md):

> Every surface has at least three states — populated, empty, and unknown.
> "I could not reach the source" must never collapse into "there is
> nothing there."

## §1 — The three-state contract

Every reader returns EITHER a value with a bounded shape (populated OR
empty) OR raises a `grove.errors.Unreachable` sentinel. **A bare `[]` or
`{}` MUST NOT mean "unreachable" anywhere in the tree.**

### Reader shape

| Case         | Return                                        |
|--------------|-----------------------------------------------|
| populated    | the value's real shape, non-empty             |
| empty        | the same shape with no data (`[]`, `{}`, `PersonaRoster` with no rows, `{"schema": "...", "envelopes": []}`) |
| unreachable  | `raise Unreachable(reason)` — never a value   |

### Endpoint shape

Every `/api/*` handler wraps its reader in a `try/except Unreachable` and
answers with one of:

| Status | Body                                                             | When |
|--------|------------------------------------------------------------------|------|
| `200`  | `{"state": "populated", <data-fields>}`                          | source reached, data present |
| `200`  | `{"state": "empty",     <same-shape-with-no-data>}`              | source reached, no data      |
| `503`  | `{"state": "unreachable", "reason": "<why>"}`                    | source could not be reached  |

Every other pre-existing status (400 on bad input, 405 on wrong method,
etc.) is preserved verbatim. `state` is the discipline; the other
non-2xx codes are the pre-existing surface. A successful write endpoint
has no `empty` case — a successful write is always `populated`.

Existing response fields (e.g. journal-writer's `ok`) may coexist with
`state` for backward compatibility — the `state` field is the one every
Web Component reads.

### Web Component shape

Every Web Component that consumes an `/api/*` endpoint renders a
distinct visual for `unreachable`. It is NEVER the same pixels as
`empty`. The empty state and the unreachable state look different to
the operator — text, color, or affordance MUST differ. The three-state
JSDoc header on every consuming component names this section.

Unreachable rendering guidance (not mandate):
- amber / muted-red banner or border for unreachable
- neutral / plant sigil (❦) for quiet-but-reached (empty)
- source-fetch failure fires a component `<name>-unreachable` event so
  a page-level listener can act; log-once to `console.info`, never
  `console.error`

### Where the sentinel lives

`grove.errors.Unreachable` — one class, one `reason` string. See
`grove/errors.py`. Every reader in `grove/*.py` and every endpoint in
`grove_serve.py` uses this vocabulary.

## §2 — Supersedes D7 (premise doc)

`docs/design/willow-grove-premise.md` D7 sealed the phrase *"absence is
a state, not a failure"*. That phrase was widely misread as
"empty-on-failure is fine" — the readers collapsed
"could-not-reach-the-source" into `[]` / `{}` / `None`, and the Web
Components rendered nothing (which reads to the operator as "there is
nothing there"), which IS the fleet's disease named in Constraint 1.

D7 remains sealed. Its correct reading is now three-state per §1 above:
the state (unreached) exists AND rendering it distinctly is required.
The premise-doc D7 section (`docs/design/willow-grove-premise.md`
around line 316) carries a supersede line pointing here.

## §3 — Doc discipline

- Every design-doc reference in code comments cites `INVARIANTS.md
  §<anchor>`, not line numbers in `DESIGN_CONSTRAINTS.md` (line numbers
  rot; anchors don't).
- Every code-changing PR appends a bullet to `CHANGELOG.md`'s
  `[Unreleased]` section under `### Changed`, `### Added`, `### Fixed`,
  or `### Removed`, per Keep a Changelog v1.1.0.
- New readers state their §1 posture in the module docstring.
- New endpoints state their §1 response shape in the handler docstring.
- New Web Components state their §1 rendering states in the JSDoc
  header.

## §4 — Reader/endpoint coverage (v0.9 PR 1 baseline)

Every reader listed below returns bounded-shape-or-`Unreachable`; every
endpoint answers 200/populated, 200/empty, or 503/unreachable.

| Reader                     | Endpoint                       |
|----------------------------|--------------------------------|
| `grove/persona_roster.py`  | `GET  /api/personas`           |
| `grove/envelope_reader.py` | `GET  /api/envelopes`          |
| `grove/kart_reader.py`     | `GET  /api/dispatch`           |
| `grove/journal_reader.py`  | `GET  /api/journal/recent`     |
| `grove/journal_writer.py`  | `POST /api/journal`            |
| `grove/nestor_client.py`   | `POST /api/nestor/decide`      |

Any future reader/endpoint added to Grove joins this table in the same PR.
