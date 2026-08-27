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

## §5 — Trust order

Every u2u packet has its signature verified before consent is consulted;
consent decisions never render on unverified data. The order is
**signature → consent → dispatch**, in exactly that sequence.

Concretely, in `u2u/listener.py._process`:

1. Parse and shape-check the header.
2. Verify the Ed25519 signature against the *correct* verification key —
   the stored key for a known contact, or the KNOCK's own payload key for
   an unknown peer's KNOCK (the only self-verifying admission).
3. **Only then** consult `ConsentGate.check` with the (now-authenticated)
   sender address, packet type, and thread_id.
4. Dispatch on ALLOW; refuse-with-signal on DENY; refuse-with-approval-hook
   on PENDING.

Anything derived from an unauthenticated header — including a `_denied`
notification, a `_pending` operator prompt, or a bridge admission — is a
dispatch, and MUST NOT happen before step 2 succeeds.

Two related contact-store rules protect the state that decision depends on:

- `ContactStore.add()` is the ONLY path to create a new contact and refuses
  an address it already knows. Reconstructing the dataclass silently reset
  `blocked` and every `consent_*` flag — that was the "silent trust reset"
  half of the P0.
- `ContactStore.update_key()` is the ONLY path to rotate an existing
  contact's key. It mutates the pubkey and preserves `blocked`, every
  `consent_*` flag, `name`, `added` and `resources`. It defaults closed —
  the caller must explicitly pass `require_confirmation=False` to attest
  that a human authorised the rotation.

Anchor witnesses: `tests/test_u2u_consent_order.py` (this invariant by
name) and `tests/test_u2u_trust.py` (the wider matrix). Every code comment
on the modified lines cites this section by anchor, not by line number.

## §6 — Manifests describe code, not aspirations

Every capability described in `safe-app-manifest.json` reflects a property the
code demonstrably has. Aspirational descriptions belong in design docs, not in
a manifest that claims trust from consumers. Tests enforce this.

The origin case: `dm_conversations` was previously described as *"End-to-end
encrypted, local-only"* while `u2u/packets.py:74-75` writes plaintext JSON
onto a bare TCP socket (the `cryptography` dependency is imported only for
Ed25519 signing). See `CODE_REVIEW.md` P0 — *"the manifest claims u2u is
encrypted; it is not"*. The correction is in the manifest; the aspiration
(Gate 6 confidentiality) lives in `docs/design/u2u-security-limits.md`.

### Enforcement

- `tests/test_manifest_honesty.py` pins the `dm_conversations` description —
  it must contain `NOT encrypted` and must not contain `End-to-end encrypted`,
  and any capability description that mentions `Encrypted` must sit next to a
  disclaimer (`NOT encrypted`, `cleartext`, or `Gate 6`) in the same
  purpose+description blob.
- `tests/test_readme_honesty.py` pins the README's u2u row — the withdrawn
  phrasings `Encrypted LAN transport` and `encrypted transport` may not
  reappear, and the corrected substrings must be present.
- New capability rows added to `safe-app-manifest.json` MUST be describable
  in code-demonstrable terms. If the description names a property that a
  reader can't verify by reading the tree, the row is wrong.

## §7 — Consent flows are real, not automatic

OAuth authorization never auto-issues a code. The operator approves via a
loopback-only page. Access tokens have a bounded TTL suitable for the
operator seat, not 30 days. DNS-rebinding protection is on regardless of
scheme; a public tunnel deployment requires an explicit operator
acknowledgement flag.

Concretely, for `grove.mcp_local --serve` (see `grove/mcp_auth.py`,
`grove/mcp_local.py`):

- **`/authorize` never issues a code.** It parks the request under a
  256-bit one-shot key and redirects the browser to
  `/grove-approve?pending=<key>`. The pre-PR-6 `GROVE_MCP_AUTO_APPROVE`
  env-var escape hatch is gone — there is no auto-approve path.
- **The approval page runs on the box.** Rendering (GET) is available to
  any peer that has the one-shot key, so an operator can inspect it over
  a tunnel; the POST that completes the grant is refused unless the peer
  is on 127.0.0.1 / ::1 / localhost. The operator has to be on the box
  (SSH port-forward, local browser) to complete the click.
- **Pending approvals expire in 5 minutes.** The one-shot key becomes
  unusable and no code can be issued against it.
- **Access tokens live for 24 hours.** Refresh tokens keep their longer
  reconnect horizon; the access token itself is what gets replayed on
  every call, so it is what has to expire.
- **Dynamic client registration is off by default.** An operator opts in
  explicitly via `GROVE_MCP_ALLOW_DYNAMIC_REGISTRATION=1`. Otherwise
  only pre-enrolled clients can authorize — the pre-PR-6 open dispenser
  is closed.
- **DNS-rebinding protection is on in every configuration.** The prior
  `_transport_security()` carve-out that disabled it "behind ngrok" for
  `https://` base URLs is removed. Loopback plus the operator-configured
  tunnel host stay allowlisted; nothing widens to `*`.
- **A non-loopback base URL logs a WARNING** unless the operator sets
  `WILLOW_MCP_TUNNEL_ACKNOWLEDGED=1`. The listener refuses no request on
  the strength of that flag alone (the transport allowlist is what
  gates access); the flag is the operator saying out loud that the
  tunnel is intended. There is no `--allow-tunnel` CLI flag — the
  warning IS the security note.

Every code change to `grove/mcp_auth.py` or the OAuth surface of
`grove/mcp_local.py` cites `INVARIANTS.md §7` in the docstring or
comment that motivates it. Pinning tests: `tests/test_mcp_auth.py`,
`tests/test_mcp_serve_oauth_flow.py`, `tests/test_serve_mode_identity.py`,
`tests/test_grove_approval_page.py`, `tests/test_transport_security.py`.

## §8 — Panels consume live endpoints by default

Every Web Component consumes its live `/api/*` endpoint by default.
Fixture-based rendering is opt-in (harness use only). The served page
renders live state, not curated data.

Concretely:

- Every Web Component's `data-source` (or equivalent) default resolves
  to the matching endpoint from the §4 coverage table — never a JSON
  fixture path.
- The harness page `web/harness.html` MAY carry an explicit
  `data-source="./fixtures/..."` override so a design pass can inspect
  the populated shape without a running server. That is the only
  legitimate use of an explicit fixture path.
- The served page (`grove_html.py`) MUST NOT carry an explicit
  fixture-path `data-source` on any component. Every panel there
  renders whatever the reader currently returns — populated, empty, or
  unreachable per §1.
- New Web Components state their live-endpoint default (and the
  harness carve-out) in the JSDoc header, alongside their §1 three-state
  posture.

Pinning tests: `tests/test_panel_wiring.py` (endpoint side of the
default source; three-state shape end-to-end) and
`tests/test_refusal_summon_shape.py` (the refusal-summon boot module's
POST target and event contract).
