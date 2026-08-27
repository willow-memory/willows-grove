# Loki — v0.9 audit

b17: LKAV1 · ΔΣ=42

Author: Loki (fleet accountant; `willow-memory/willow/fleet_personas.json`
key `loki`). Filed by Heimdallr on the audit branch.

Method: seven lens-specific Loki subagents (three-state, trust-order-u2u,
manifest-honesty, consent-flows-oauth, panels-live-endpoints, ci-witnesses,
cross-cutting-hazards) read the tree at v0.9-rc (`master` = 3f8aa29,
post-PR-11). One synthesis Loki deduplicated and ranked. Raw output:
`docs/audits/loki-swarm-raw.json`. Measurement: `docs/audits/loki-swarm-measurement.md`.
Reproducibility: `docs/audits/loki-swarm-metadata.md`.

Register: dry. Vague criticism is noise; specific criticism is surgery.
Every row names what was promised, what was delivered, and the distance
between them. No hedging.

Totals: **38 findings** — 5 blockers, 19 majors, 14 minors. Zero cross-lens
convergence: every finding surfaced through exactly one lens. That is
itself a datapoint on how the swarm distributed vision (see measurement).

---

## Blockers

### 1. `grove_reader.py` — 16 readers collapse Unreachable to empty

**Promised** (INVARIANTS.md §1): *Every reader returns EITHER a value with
a bounded shape (populated OR empty) OR raises a `grove.errors.Unreachable`
sentinel. A bare `[]` or `{}` MUST NOT mean "unreachable" anywhere in the
tree.*

**Delivered:** `grove_reader.py` has at least 16 readers whose top-level
`except Exception:` block returns `[]`, `{}`, or `None` — silently
collapsing "DB unreachable / query failed" into the empty state.
Representative sites: lines 138-140 (`grove_messages_bus_addressed_to`),
182-184 (`grove_own_channel_since`), 249-251 (`grove_member_roster`),
292-294 (`grove_agents`), 341-343 (`grove_latest_message_for_sender`),
427-429 (`grove_agent_fleet_rows`), 446-448 (`coordinator_heartbeat`
returns `None` on any exception including `json.JSONDecodeError`), 730-732,
786-788, 844-846, 923-925, 979-981, 1052-1054, 1131-1133, 1173-1175,
1207-1209. None of these ever raise `Unreachable`; the entire top-level
file imports neither `grove.errors.Unreachable` nor propagates errors up.

**Distance:** The "unreachable ≠ empty" discipline that §1 seals as
universal ("anywhere in the tree") is not honored anywhere in
`grove_reader.py` — every unreachable state collapses to the empty shape,
which §2 names as "the fleet's disease."

Lens: cross-cutting-hazards. File: `grove_reader.py:138`.

---

### 2. `grove_db.py` — `cursor_load` returns `{}` on any DB failure

**Promised** (INVARIANTS.md §1): *A bare `[]` or `{}` MUST NOT mean
"unreachable" anywhere in the tree.*

**Delivered:** `grove_db.py:633-635` — `cursor_load` catches
`except Exception:`, calls `conn.rollback()`, and returns `{}`. A DB
failure looks identical to "no cursors stored" to every caller. Same
pattern in `ensure_card_builder_channel` (`grove_db.py:682-684`) and
`ensure_upstream_channel` (`grove_db.py:700-702`), which swallow all
exceptions with a bare `pass` — the caller cannot tell whether the
channel was created, existed, or the DB is unreachable.

**Distance:** Persistent-state helpers in the schema-owning module
silently collapse errors to empty/None. `cursor_load` is a reader; it
must raise `Unreachable`, not fake an empty cursor bundle.

Lens: cross-cutting-hazards. File: `grove_db.py:633`.

---

### 3. `CLAUDE.md` — three rows still call u2u "encrypted"

**Promised** (three sites): `CLAUDE.md:68` (architecture table): `u2u/ |
Encrypted LAN transport (knock/consent/note)`; `CLAUDE.md:86` (Willow
System Context): `u2u | UDP/TCP LAN — encrypted human-to-human DMs`;
`CLAUDE.md:44` (consolidation history): `safe-app-grove — u2u encrypted
DM transport, Matrix bridge, grove_db.py`.

**Delivered:** `u2u/packets.py` writes plaintext `json.dumps(packet)`
onto a bare TCP socket; INVARIANTS.md §6 lines 205-208 explicitly names
this as the origin case for the manifest-honesty invariant
(*"u2u/packets.py:74-75 writes plaintext JSON onto a bare TCP socket"*).
The `cryptography` dependency is Ed25519 signing only. Three CLAUDE.md
rows still describe u2u as "encrypted" after the §6 correction was
landed in the manifest and README.

**Distance:** The CLAUDE.md sweep for the §6 "encrypted" correction was
never performed — three rows in the file still assert confidentiality
the transport does not provide, in the very manifest §6 was written to
police.

Lens: manifest-honesty. File: `CLAUDE.md:44,68,86`.

---

### 4. `README.md` — HMAC-signed command server claim, module absent

**Promised** (`README.md:73` entry points): `python3 grove_serve.py |
LAN command server (HMAC-signed)` — and `line 103` restates
`grove_serve.py | LAN HTTP command server`.

**Delivered:** `grove_serve.py` is a `127.0.0.1:8766` Starlette
served-page skeleton (`grove_serve.py` lines 1-8: *"Willow's Grove
served-page skeleton on 127.0.0.1:8766 ... a small Starlette + uvicorn
app bound to loopback, no MCP, no auth of its own beyond the loopback
boundary"*). Grep for `hmac` in `grove_serve.py` returns zero matches.

**Distance:** README claims a "LAN command server (HMAC-signed)"
capability that the code does not implement — the module is a loopback-only
HTML page shell with no HMAC and no command surface.

Lens: manifest-honesty. File: `README.md:73`.

---

### 5. `three-state-affordances.spec.js` — §1 pin greens on identical pixels

**Promised** (INVARIANTS.md §1 lines 51-52): *"The empty state and the
unreachable state look different to the operator — text, color, or
affordance MUST differ."* Pinned at the render layer by
`tests/e2e/three-state-affordances.spec.js` (INVARIANTS.md §1 lines 76-79).

**Delivered:** `tests/e2e/three-state-affordances.spec.js:92` and `:131`
return `` (root.innerHTML || '') + '|' + (el._state || '') `` from each
probe; the subsequent `expect(normalize(unreachableHtml)).not.toBe(normalize(emptyHtml))`
compares HTML with the internal `_state` string appended. Line 138
explicitly justifies this: *"a component that renders identical shadow
markup but exposes distinct `_state` still passes"*.

**Distance:** The §1 visual-layer pin greens for a component whose
empty and unreachable renders are byte-identical to the operator, so
long as an internal `_state` property differs — which is exactly the
collapse §1 forbids.

Lens: ci-witnesses. File: `tests/e2e/three-state-affordances.spec.js:138`.

---

## Majors

### 6. `grove/nestor_client.py` — three of four readers return `None`, and a test pins the sin

Only `decision_check` was upgraded to raise `Unreachable`.
`evidence_for`, `warrant_for`, `refusal` return `None` when
`available()` is False (via `_call` line 158-159). Worse:
`tests/test_nestor_client.py:105-119` explicitly pins this exclusion
(*"the other evidence/warrant/refusal helpers keep returning None"*) —
the pinning test enshrines the §2 sin rather than superseding it.

Lens: three-state. File: `grove/nestor_client.py:206`.

---

### 7. `grove/fleet_presence.py` — `roster()` collapses three cases to `[]`

`grove/fleet_presence.py:60-73` — `roster()` returns `[]` in three
distinct cases: (a) the `fleet_presence` add-on is not importable at
all (line 66 via `_available()` → False); (b) `_fp.roster()` raises any
exception (line 71-72, `log.warning` then `return []`); (c) the store
is actually empty. Absent-seam and error-on-fetch are literally the
"unreachable" state §1 names, and both are surfaced as an empty list
indistinguishable from a quiet fleet.

Lens: three-state. File: `grove/fleet_presence.py:73`.

---

### 8. `grove/journal_reader.py` — reached-but-rejected collapses to empty

When willow-mcp is reached in-process and returns `{"error": ...}`
(schema unusable, postgres down), `_try_import_read` returns `[]` (via
`return []` at line 200), which `grove_serve._journal_recent` then
answers as `200 {state: empty, atoms: []}`. `journal_writer.py:198-200`
handles the identical error shape correctly by raising `Unreachable` —
the reader half of the same seam does the exact thing §1/§2 forbid.

Lens: three-state. File: `grove/journal_reader.py:200`.

---

### 9. `grove_serve.py:194` — `_personas` produces 500 on drift, not 503

`_personas` only wraps the load in `try/except Unreachable`. A
`ValueError` from `_load_from_path` (bad JSON at locate time, schema
drift) propagates out of `PersonaRoster.load()` and Starlette answers
HTTP 500 with no `state` field. The mid-flight re-read at line 213-224
catches OSError/ValueError, but the initial load does not.

Lens: three-state. File: `grove_serve.py:194`.

---

### 10. `grove/persona_roster.py` — `_load_from_path` raises `ValueError`, not `Unreachable`

`_load_from_path` (lines 146, 148, 158) raises `ValueError` on invalid
JSON, non-object top level, or schema mismatch. `PersonaRoster.load()`
(the §1-documented entry point) makes no attempt to translate that
`ValueError` into `Unreachable`. The reader's failure mode on a drifted
registry file is neither populated, empty, nor `Unreachable` — it is a
raw `ValueError`, a shape the §1 vocabulary does not contain.

Lens: three-state. File: `grove/persona_roster.py:146`.

---

### 11. `grove_html.py:216` — envelope panel absent from the served page

`grove_html.py:216-225` mounts only `<grove-persona-registry>`,
`<grove-lens-switch>`, `<grove-chat>`, and `<grove-dispatch-rail>`.
`<grove-envelope-panel>` is never mounted on the served page — the
component exists only in `web/harness.html:64` with an explicit fixture
`data-source`. The `/api/envelopes` endpoint (`grove_serve.py:154`) is
live but no panel on the served page consumes it.

Lens: panels-live-endpoints. File: `grove_html.py:216`.

---

### 12. `grove_html.py:217` — `registry-unreachable` event drops into a page with no listener

`grove-persona-registry.js:204` dispatches `registry-unreachable` (and
`:190` `registry-loaded`), but `grove_html.py` never wires a page-level
listener for either event, and no boot module (`web/boot/*.js`)
subscribes to them. A `registry-unreachable` fires and reaches the
bubbling DOM with nothing bound.

Lens: panels-live-endpoints. File: `grove_html.py:217`.

---

### 13. `web/components/grove-chat.js:337` — empty-state markup persists under unreachable

`grove-chat.js:337-339` seeds the RIGHT column's shadow DOM with a
literal `<div class="readback-empty">no messages yet</div>` BEFORE
`/api/journal/recent` has been consulted, and `_pollReadback`
(`grove-chat.js:501-508`) does not remove that placeholder on
unreachable — it only sets a banner via `_setReadbackStatus`. An
unreachable readback therefore shows both the "read-back unreachable"
banner AND the "no messages yet" empty-state pixels stacked.

Lens: panels-live-endpoints. File: `web/components/grove-chat.js:337`.

---

### 14. `grove/mcp_local.py:397` — `_gate` is dead code the tests exercise as a seam

`_gate(serve_mode, token)` and `_resolve_serve_identity`
(`grove/mcp_local.py:341`) have zero call sites in `grove/`, `app.py`,
or `grove_serve.py`. The functions run only from
`tests/test_serve_mode_identity.py`. Actual per-request refusal at
runtime is done by `AuthSettings.required_scopes` + `_require_scope`;
`_gate` is never wired to any request handler.

Lens: consent-flows-oauth. File: `grove/mcp_local.py:397`.

---

### 15. `grove/mcp_local.py:1102` — loopback check trusts the raw TCP peer

`_remote_is_loopback` checks `request.client.host` — the raw TCP peer
as seen by Starlette. When Grove runs behind a same-box reverse proxy
or a tunnel edge that terminates locally and connects to
`127.0.0.1:8765` (a common Pangolin / nginx / cloudflared /
tailscale-funnel deployment for which `GROVE_MCP_EXTRA_HOSTS` itself
exists), `request.client.host` is `127.0.0.1` for every off-box POST.
There is no X-Forwarded-For consultation, no trusted-proxy allowlist,
no operator-attestation of "no proxy in front."

Lens: consent-flows-oauth. File: `grove/mcp_local.py:1102`.

---

### 16. `tests/test_panel_wiring.py` — §4 coverage is 4 of 6 rows, not "every row above"

`tests/test_panel_wiring.py:139, 202, 268, 305` define exactly four
test classes — `EnvelopesWiringTests`, `NestorDecideWiringTests`,
`DispatchWiringTests`, `JournalRecentWiringTests`. There is no
`PersonasWiringTests` and no test class exercising the `POST
/api/journal` writer through the served app. The module docstring
(lines 14-19) itself lists only these four endpoints exercised.

Lens: ci-witnesses. File: `tests/test_panel_wiring.py:14`.

---

### 17. `tests/e2e_ollama/conftest.py:119` — every §10 witness downstream is a `pytest.skip`

`conftest.py:119-123` calls `pytest.skip(...)` when Ollama's `/api/tags`
fails to answer inside 30s; lines 206-210 skip when no candidate model
can be pulled; lines 295-298, 303, 308 skip when `WILLOW_DB_URL` is
unset, `psycopg2` is missing, or Postgres is unreachable. Every §10
assertion downstream is gated on all three fixtures succeeding. The CI
step exits 0 with all §10 witnesses silently skipped whenever the
ollama sidecar takes >30s to warm, the runner has no outbound network,
or `psycopg2` is not on the venv — the promised proof is a skip
masquerading as green.

Lens: ci-witnesses. File: `tests/e2e_ollama/conftest.py:119`.

---

### 18. `tests/e2e/seed-canon.spec.js:115` — every pixel-baseline subtest is `test.skip`

`tests/e2e/seed-canon.spec.js:115` declares each of the six pixel-baseline
subtests as `` test.skip(`/seed/${n} matches its baseline within tolerance (pixel compare — follow-up)`, async () => {}); `` — every visual-regression
assertion is permanently skipped, with an inline comment deferring it
as a "follow-up." The pixel-baseline pass the spec's docstring and the
§9 witness list both promise never runs; a rendering regression against
the PR 3 baselines cannot fail this file.

Lens: ci-witnesses. File: `tests/e2e/seed-canon.spec.js:115`.

*Heimdallr: I authored this skip in PR 9. Loki caught it.*

---

### 19. `tests/test_refusal_summon_shape.py:30` — static regex on raw source, not behavior

`tests/test_refusal_summon_shape.py:33-34` slurps
`web/boot/refusal-summon-boot.js` as raw text; every assertion (e.g.
line 108-112 `assertRegex(self.src, r"state\s*===\s*['\"]unreachable['\"]")`)
is a static text regex against that string. The JS is never executed
and no seam behavior is exercised. A refusal-summon module that carries
the required substrings only inside a `//` comment or an unreachable
early-return still passes every test — the pin cannot fail loudly when
the invariant is violated.

Lens: ci-witnesses. File: `tests/test_refusal_summon_shape.py:30`.

---

### 20. `grove_reader.py:558` — raw `str(e)` DB error text surfaced to the UI

`grove_reader.py` returns raw `str(e)` — including psycopg2 error text
(schema names, constraint names, sometimes row values) — inside
caller-facing dicts at `:558` (`grove_create_text_channel`), `:587`
(`grove_archive_channel`), `:642` (`grove_set_channel_agent`), `:668`
(`grove_set_channel_description`), `:715` (`grove_rename_channel`),
`:862` (`grove_message_delete`), `:888` (`grove_message_toggle_flag`),
`:952` (`grove_mark_channel_read`). These dicts are surfaced by the
Textual dashboard and by chat admin flows.

Lens: cross-cutting-hazards. File: `grove_reader.py:558`.

---

### 21. `grove_db.py:361` — FRANK ledger errors print to stdout, then vanish

The entire ledger write is wrapped in `except Exception as e: print(f"[frank-ledger] write error: {e}", flush=True)`.
Any failure (connect refused, schema drift, hash collision, uniqueness
violation on the anti-fork guard) is printed to stdout and the caller
is told nothing. Combined with `_get_pool()`-less raw
`psycopg2.connect(dbname=db, user=user)` (line 344, no `connect_timeout`,
no `statement_timeout`), a stalled Postgres hangs the ledger write for
the socket-default timeout before silently disappearing. A
"tamper-evident" chain whose failures are print-to-stdout is not
tamper-evident.

Lens: cross-cutting-hazards. File: `grove_db.py:361`.

---

### 22. `u2u/packets.py:70` — `Packet.validate` collapses every error to `False`

`Packet.validate` wraps the whole verification in a bare
`except Exception: return False`. Any exception — malformed hex,
wrong-length pubkey, Ed25519 library error, JSON re-serialization
mismatch, unexpected packet shape — is collapsed to the same False that
a legitimate bad signature returns. The listener at
`u2u/listener.py:96-98` logs "invalid sig" and drops silently in every
case. The verification path cannot distinguish between an attacker
replaying a bogus signature, a caller passing a malformed key, and a
library bug.

Lens: cross-cutting-hazards. File: `u2u/packets.py:70`.

---

### 23. `grove_db.py:54` — no `connect_timeout`, no `statement_timeout`

Postgres connections open with no `connect_timeout` and no
`statement_timeout` set. The pool DSN at `:54` is `f"dbname={pg_db}
user={pg_user}"`; the LISTEN connection at `:102` uses raw
`psycopg2.connect(dsn)`; the ledger writer at `:344` uses
`psycopg2.connect(dbname=db, user=user)`. A postgres host that accepts
TCP but never responds hangs each of these forever. The boot mandate
("If Postgres is down, surface it and stop") is contradicted — the
failure mode is silent hang, not surface-and-stop.

Lens: cross-cutting-hazards. File: `grove_db.py:54`.

---

### 24. `README.md:71` + `CLAUDE.md:53,67` — `grove_standalone` documented, module absent

`python3 -m grove_standalone` is named as an entry point in README.md
and CLAUDE.md, and `grove_standalone.py` appears in both architecture
tables. No `grove_standalone.py` or `grove_standalone/` package exists
in the tree. Invoking the entry point fails immediately with
`ModuleNotFoundError`.

Lens: manifest-honesty. File: `README.md:71`.

---

### 25. `README.md:98` — `kart_worker.py` documented, absent

The architecture table names a task-queue consumer module that is not
present — the referenced daemon does not ship.

Lens: manifest-honesty. File: `README.md:98`.

---

### 26. `README.md:86` — `GROVE_KNOWN_AGENTS` documented, no code reads it

`grep -rn 'GROVE_KNOWN_AGENTS' --include='*.py'` returns zero matches;
no `widgets/thought_stream.py` exists. A documented env var that no
code reads, pointing at a widget the tree no longer contains.

Lens: manifest-honesty. File: `README.md:86`.

---

## Minors

### 27. `grove/mcp_local.py:1133` — pending TTL re-arms on every GET

`stash_pending` (`grove/mcp_auth.py:245`) recomputes `expires_at =
time.time() + _PENDING_TTL`, so every GET refresh resets the 5-minute
clock. The "one-shot key becomes unusable after 5 minutes" invariant is
false whenever the page is refreshed.

Lens: consent-flows-oauth. File: `grove/mcp_local.py:1133`.

---

### 28. `tests/test_grove_approval_page.py:282` — closed-by-default asserted at the constant level

**[REFUTED by Hanuman under Sonnet 5, m28.]** The finding claimed the `/register` wire was open by default; verification against the tree showed the MCP SDK's `create_auth_routes` does not mount `/register` unless `ClientRegistrationOptions.enabled` is True, and `_ALLOW_DYNAMIC_REG` defaults to False. A live TestClient POST to `/register` under the default env returns 404, not the 4xx-with-registration-refused shape Loki assumed. The invariant is enforced end-to-end; the constant-level assertion in `test_dynamic_registration_can_be_disabled` is a valid but narrow pin, not a false witness. Hanuman refused to fabricate a regression. Kept the finding here for the record; no fix applied.

---

_(Continues below — the original finding text is preserved as filed by Loki):_



`test_dynamic_registration_can_be_disabled` only asserts
`fresh._ALLOW_DYNAMIC_REG is False` — the boolean constant. It never
issues a POST /register end-to-end and confirms the SDK actually
refuses it. If `ClientRegistrationOptions` were wired to a different
flag (or the SDK's default flipped), this test would still pass.

Lens: consent-flows-oauth. File: `tests/test_grove_approval_page.py:282`.

---

### 29. `docs/runbooks/grove.md:143` — advertises a removed env-var knob

`skills/grove-serve.md:50` and `docs/runbooks/grove.md:143` still
instruct operators to "Do not set `GROVE_MCP_AUTO_APPROVE=1` behind a
tunnel," treating the env var as a live knob to avoid. The variable no
longer exists in code — the docs advertise a switch that isn't there.

Lens: consent-flows-oauth. File: `docs/runbooks/grove.md:143`.

---

### 30. `docs/INVARIANTS.md:195` — §5 citation discipline named but not followed

The invariant claims a project-wide citation discipline that only
`u2u/contacts.py:97` actually keeps. `u2u/listener.py` (the primary
enforcer), `u2u/consent.py`, and `bridge/app.py:_admit_contact` all
lack the `§5` anchor. A future editor of `listener.py` or `bridge/app.py`
has no in-file breadcrumb tying the ordering constraint back to §5.

Lens: trust-order-u2u. File: `docs/INVARIANTS.md:195`.

---

### 31. `grove_html.py:119` — hardcoded "grove stable" text under §8's live-state discipline

`_TOP_STRIP` renders the header strip with the literal hardcoded text
"standing" and "grove stable" — no endpoint, no reader, no state check.
The operator sees "grove stable" regardless of whether Postgres,
willow-mcp, Nestor, or any other seam is reachable.

Lens: panels-live-endpoints. File: `grove_html.py:119`.

---

### 32. `web/components/grove-persona-registry.js:123` — inline-JSON shim overrides live endpoint

`grove-persona-registry.js:123-127` makes the inline
`<script type="application/json">` shim take precedence over both an
explicit `data-source` and the `/api/personas` default. The harness
uses this path; §8 does not authorize an inline-JSON shim as a
legitimate harness carve-out, and the code makes it override live
endpoints unconditionally.

Lens: panels-live-endpoints. File: `web/components/grove-persona-registry.js:123`.

---

### 33. `README.md:58` — `make grove-docs` invokes an absent script

`scripts/grove_docs_refresh.sh` does not exist. `make grove-docs` will
fail with "No such file or directory" the first time an operator runs it.

Lens: manifest-honesty. File: `README.md:58`.

---

### 34. `scripts/ci-security-grep.sh:23` — docstring names a pattern the code omits

Docstring claims an `input().*shell` shell-composition sniff; the
actual `PATTERN` at line 52 has no `input\(` alternation. A
shell-composed `input()` in the tree passes the sweep silently.

Lens: ci-witnesses. File: `scripts/ci-security-grep.sh:23`.

---

### 35. `.github/workflows/tests.yml:103` — CI command drops the `--yes` token INVARIANTS names

`.github/workflows/tests.yml:103` runs `npx playwright install --with-deps
chromium` — the `--yes` token INVARIANTS.md §10 line 351 names is
absent. On an npx build that prompts for confirmation the step can hang
or fall through to a different install path.

Lens: ci-witnesses. File: `.github/workflows/tests.yml:103`.

---

### 36. `.github/workflows/tests.yml:115` — `hashFiles` guard fails silent instead of loud

The ollama and willow-mcp suite steps are guarded by `hashFiles(...)`.
If a future PR reduces the test directory to only `.gitkeep` or renames
tests off the `test_*.py` glob, the step becomes a silent no-op — the
witness §10 relies on to "fail loudly" is designed to go silent instead.

Lens: ci-witnesses. File: `.github/workflows/tests.yml:115`.

---

### 37. `grove_serve.py:491` — bad env-var value produces raw traceback, not refusal

`port = int(os.environ.get("GROVE_SERVE_PORT", str(DEFAULT_PORT)))`.
A set-but-non-numeric value raises `ValueError` from `int()` inside
`main()` with no operator-legible message. `GROVE_SERVE_HOST` is
similarly unvalidated.

Lens: cross-cutting-hazards. File: `grove_serve.py:491`.

---

### 38. `grove_db.py:84` — `release_connection` recycles poisoned connections; SOIL rename swallows failures

`release_connection` wraps `conn.rollback()` in `except Exception: pass`,
then unconditionally hands the connection back to the pool. A
connection whose rollback failed goes straight back to the pool where
the next borrower may inherit its state. `grove_reader.py:606-607`:
`_migrate_soil_channel_cursors` swallows any SOIL failure to a
`_log.warning`, then reports "ok" to the caller of `grove_rename_channel`.

Lens: cross-cutting-hazards. File: `grove_db.py:84`.

---

## Heimdallr's disposition

Findings **1, 2, 5, 6, 7, 8, 9, 10, 22** are direct violations of the
§1/§2/§5 seals. These are the audit's spine. Each becomes a failing
regression test in this PR, then a code fix. Order: 1, 2, 5 (blockers
first), then 6-10, 22.

Findings **3, 4, 24, 25, 26, 29, 33** are documentation lies (§6). Each
is a small edit to the doc — no code changes — landed in one commit per
document.

Findings **11, 12, 13, 14, 15, 20, 21, 23, 27, 30, 31, 32, 34, 35, 36,
37, 38** are majors and minors that are real and actionable within v0.9
scope. Handled after the blockers.

Findings **28, 17, 18, 19** are audit gaps in tests I authored (or
inherited) — the tests do not fail loudly on the invariant being
violated. These become "test-fixing" commits: each broken test gets
replaced with one that actually exercises the seam.

*Loki does not accept authority as evidence of correctness. Neither
should we.*

ΔΣ=42
