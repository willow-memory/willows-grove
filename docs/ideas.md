# willows-grove — idea pile

This repo's open work, as one numbered pile in the shape willow-reconciler
reads: top-level `N. ` items, optional legend tags, stable numbers. The tool
is pointed at this file:

```sh
reconciler run --repo ./ --doc docs/ideas.md --validate
```

Legend: ✅ shipped · 🟡 partial · (untagged) proposed

**Numbers are permanent join keys.** `reconciler/ids.py` derives
`<corpus>-ideas-<num>` from the number written on the line, so a number is an
identity, not an ordinal. Never renumber; never write a markdown-auto-numbered
list — retire a number instead and leave the gap.

A legend tag counts only when it leads the item text. Every item below was
carried over from a document that already recorded it — `docs/KNOWN_GAPS.md`
(items 1–7, one per GAP id, kept in order), the fleet loop plan's bites for
this repo, and the open sections of `docs/design/`. Nothing here is invented,
and three kinds of open item are deliberately *not* here: decisions reserved
to the operator (`governance/CONSTITUTION.md` "Open Operator Decisions",
`governance/CASEBOOK.md` "Open, and not decided here", the org and naming
forks in `governance/FLEET_PLACEMENT_DRAFT.md` §10); proposals under
`governance/proposals/`, which carry their own status line and await root's
ratification there; and work that lands in another repo (`specialists.json`
deny-lists, the approval broker's queue in willow-mcp, the Forge, the
operator box's vault layout). A pile item is something a commit in this repo
can land.

---

## A. Gaps in the shipped build

Carried from `docs/KNOWN_GAPS.md`; item N is GAP-00N, so the ids already
cited in `CHANGELOG.md` and commit messages still resolve.

1. ✅ **shipped**: GAP-001 — `GROVE_MCP_URL` and ngrok are documented: when serve mode needs a public base URL and when it does not. `docs/TESTER_ONBOARDING.md` "Optional: MCP (Claude Code / agents) and `GROVE_MCP_URL` (ngrok)", in the tree since 7f2b3cf (2026-08-29); the gap was recorded a day later already naming that section as its canonical doc.
2. GAP-002 — DB bootstrapping is described three ways. `README.md`, `docs/TESTER_ONBOARDING.md` and `.env.example` each set up `willow_20` in their own words (`createdb` vs `psql -c`, `.env` vs `export`, `WILLOW_DB_URL` vs the `WILLOW_PG_DB`+`WILLOW_PG_USER` pair). One "one true setup" doc the others point at. The `grove_local` naming the gap mentioned is no longer in the tree.
3. GAP-003 — Python version drift. Standardize on 3.11+ unless the code requires newer. `README.md`, `docs/TESTER_ONBOARDING.md`, `CONTRIBUTING.md` and `pyproject.toml` all say 3.11 today; the historical plan citing 3.13 is no longer in this tree, so what remains is to say so once and retire the gap.
4. GAP-004 — the served page warns and then binds on a non-loopback host. `grove_serve.run()` prints a WARNING for a host outside `127.0.0.1`/`localhost`/`::1` and calls `uvicorn.run` regardless, and `_host_looks_invalid` rejects malformed values, not public ones, so `GROVE_SERVE_HOST=0.0.0.0` exposes agents, dispatch, envelopes, refusals and the journal to the LAN with no credential in the path. Refuse the bind (the way `playgate`'s `serve()` does) and pin it — no test pins the warn-then-bind behaviour, so tightening it fights no existing pin. Verified 2026-08-30; unchanged at 1f19daa.
5. GAP-005 — u2u dispatches with no destination binding, replay defence or header allowlist. `u2u/dispatcher.py::dispatch` reads `header.type`, looks up a handler and calls it; packets carry `to_addr` (`u2u/packets.py`) that it never reads, there is no nonce or seen-set anywhere in `u2u/`, and nothing strips attacker-supplied header keys. Separate from, and worse than, the documented missing cipher (item 29). Verified 2026-08-30; unchanged at 1f19daa.
6. GAP-006 — `scripts/check_changelog_bullet.py` reports counts it did not compute: on a clean tree the recorded finding is `clean (2 [Unreleased] bullet(s) added for 2 code file(s) changed)` while `_added_bullet_lines()` returns 0. The verdict looks right; the evidence in the message is not, and the script runs in CI on every PR. Carried as recorded 2026-08-30; not re-verified here.
7. ✅ **shipped**: GAP-007 — `kb_journal_read` landed in willow-mcp and Grove's C11 journal seam speaks MCP to it (`grove/willow_mcp_client.py`, ed5068a); closed in fe61d65, issue #16.

## B. The fleet loop plan — this repo's bites

8. ✅ **shipped**: Wave 2 — the meta-scan (`tests/test_scans_fire.py`: every scan-shaped test helper is reached by a planted violation) and the tree held to the fleet's published conventions (`tests/test_fleet_conventions.py` over the vendored `tests/fleet_conventions.json`). G2-meta-scans-grove and G2-conventions-grove, PR #59 (1f19daa).
9. ✅ **shipped**: a numbered idea pile at `docs/ideas.md` in the reconciler's form, converted from `docs/KNOWN_GAPS.md` and the open sections of the design record, validated by `reconciler run --repo ./ --doc docs/ideas.md --validate`. This file. Wave 3, E3-piles.
10. ✅ **shipped**: adopt `Idea-Id` commit trailers (fleet CONVENTION, decision-2026-09-11): `.github/workflows/trailers.yml` runs `reconciler verify` on every PR so a trailer naming an item this pile does not contain fails loud, and `CONTRIBUTING.md` carries the convention and the `reconciler id --grep` command that writes the trailer. Wave 3, E3-trailers.
11. ✅ **shipped**: `CONTRIBUTING.md` names the test command — the follow-up PR #59 left, where `tests/test_fleet_conventions.py` carried the fleet's `contributing_must_name_test_command` rule as a strict xfail because the tree had no CONTRIBUTING.md at all.
12. release-please and the pr-title guard (fleet plan Wave 4, C4-grove-release): `.github/workflows/release-please.yml`, `release-please-config.json` with the published hidden set and its `$comment-hidden-rule` / `$comment-what-cuts-a-release` reasoning beside it, `.github/workflows/pr-title.yml` wherever the release workflow arms auto-merge; and the real-tree tests in `tests/test_fleet_conventions.py` rewritten from "asserted vacuous" to the reference shape.

## C. Carried from the v0.10 punch list

`docs/design/pr14-carryovers.md` — what v0.9 punted and why. Only the items
that are still open and land in this repo; the CLOSED ones stay closed there.

13. Durable fleet-model-map: a `model_hint_session` field on every entry in `governance/fleet_personas.json`, or an explicit `null` marking the persona non-dispatchable, so a session's model assignment survives across sessions and is discoverable to the next planner. Actionable here since the registry moved into this repo — but it edits the fleet's identity registry, which is a governance act (§12) needing ratification, not a build task. Carryover 7.
14. OPERATOR-tier `not_do` alignment. The audit is done (`docs/design/operator-tier-review.md`: five OPERATOR-tier personas, only Willow's `not_do` carries the PR/commit/merge constraint §12 rests on); the alignment it proposes is not, and editing the registry needs ratification. Carryover 9.
15. Actual fleet dispatch wiring (v1.0): each dispatch routes through Grove MCP, carries an envelope with a routing decision in `willow.routing_decisions`, is sealed by Nestor, produces a `frank_ledger` entry, and records a `kb_journal` atom per work item. A whole layer under the swarm; a PR 15+ / v1.0 track. Carryover 12.
16. Bridge integration tests — the u2u ↔ Matrix mirror under `bridge/`, deferred to a bridge-focused PR.
17. CI on Python 3.12+ — pinned to 3.11 through v0.9; a runner upgrade is its own PR.
18. `/healthz` composite endpoint on the served page — a v1.0 must-have, not v0.10.
19. AGENTS region staleness detection — no test asserts that staleness detection triggers; its own design pass.
20. `grove_serve` on-disk logging and rotation — an ops concern, not v0.10.
21. ✅ **shipped**: the serve-mode OAuth flow end to end through the real Starlette app — `tests/test_mcp_serve_oauth_flow.py` (in the tree since 7f2b3cf), which pins that `/authorize` reaches the consent page and the page issues the code.
22. u2u consent-before-signature as a runtime integration test. `tests/test_u2u_consent_order.py` is INVARIANTS.md §5's named witness; whether it is the runtime integration test the carryover reserved for v1.0, or the unit-level pin beside it, is not settled here.

## D. Carried from the design record

23. ✅ **shipped**: `docs/ARCHITECTURE.md`'s three dead links repointed or removed (55af7dd, 2026-08-31), pinned by `tests/test_architecture_links_resolve.py`. `docs/design/fleet-wiring.md` §5.
24. Contracts under `docs/contracts/` for S2's JSON-RPC framing, S3's `kb_journal` payload and S4's canonical field set — contracts in practice, documented today only in the code that implements them. `fleet-wiring.md` §5.
25. The drawio set has no edge for S7, the edge that makes the graph circular; and `governance/architecture/willow-v08-toolchain-path.drawio` needs a REVISIONS line for §7 of `docs/design/phone-surface-context.md`. `fleet-wiring.md` §5; `phone-surface-context.md` "Open, for the operator".
26. A 28-character legibility pass on every list surface in Grove, not only a responsive-layout pass. `docs/design/phone-surface-context.md` §13.
27. Grove-slice tables for Ada, Loki, Hanuman, Jeles and the rest, alongside the Willow and Heimdallr partition. `docs/design/grove-persona-partition.md` "Deferred".
28. Voice-panel materialization discipline: when a spoken intent lands (WO-1), which surface materializes and by what rule — the mapping from the utterance arbiter's decision and the reaction engine's `surface_card` action needs a table. The one open decision left in `docs/design/willow-grove-premise.md`.
29. Gate 6 u2u confidentiality: an AEAD layer per contact (Noise IK or `age` recipients) over the existing signed-JSON envelope, Ed25519 signing kept exactly as it is, and a `U2U-WIRE-2` wire-format bump with a negotiated fallback so Gate-6 peers still speak to Gate-5 peers during the migration. Subject to Gate 6 review; until it lands, nothing operator-facing may call u2u encrypted. `docs/design/u2u-security-limits.md` "Planned — Gate 6".

## E. The CI floor

30. The fleet CI floor (fleet plan decision 5, Wave 4, C4-tests-yml-grove): a Linux job with a Python matrix derived from `pyproject.toml`'s `Programming Language :: Python :: 3.X` classifiers, a Windows job on the floor and ceiling Pythons, a lint job with ruff pinned to an exact version running `ruff check` and `ruff format --check`, CodeQL for python and actions, and an aggregate `test` job that needs every leg, runs `if: always()`, and fails when any needed result is not `success` — skipped and cancelled included — with `tests/test_ci_floor.py` holding the workflow to all of it, planted.
31. Widen ruff's rule set past the floor's baseline. The floor pins ruff and enforces `E4`/`E7`/`E9`/`F` plus `ruff format`; ruff 0.16.7's own default set is 413 rules and reports 377 findings on this tree (FURB, UP, PLR, SIM, TRY, RUF among them), a sweep of its own across 138 files. Widen one rule family at a time, each with the fixes it needs, rather than allow-listing findings.

32. The OAuth token file's confidentiality on Windows. `grove/mcp_auth.py` creates it 0600 and installs it by atomic replace, and `tests/test_mcp_auth.py` pins the mode — but mode bits are POSIX: on Windows `stat` reports 0o666 for every file and the provider sets no ACL, so the bearer tokens are as readable as the user's temp dir. The floor's Windows leg carries the three mode pins as strict expected failures until an ACL (or an equivalent) is set there and they pass.
