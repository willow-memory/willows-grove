# ADR — the dispatch packet gets a closed lifecycle

**Status:** proposed · drafted by willow 2026-09-02 · **willow-mcp code change, root ratifies**
**Build order:** 3 of 6 — see [`2026-09-02-build-order.md`](2026-09-02-build-order.md)
**Design source:** [`willow-mcp/docs/design/complete-system-packet-2026-07-08.md`](../../../willow-mcp/docs/design/complete-system-packet-2026-07-08.md) — the operator's north star. This ADR builds what that packet specified and the July slices left out.
**Prior art:** [`willow-mcp/docs/PRIOR_ART.md`](../../../willow-mcp/docs/PRIOR_ART.md) §1 (staged approval: **Adapt**, Netflix Conductor), §5 (workflow engines), §13 (human-in-the-loop: **Compose**). Nestor covenant lineage (draft / sealed / rejected-with-reopen), already ported once in [`envelope-accrual.md`](../../../willow-mcp/docs/design/envelope-accrual.md).
**Companion:** [`2026-09-02-governed-path-write-gate-v2.md`](2026-09-02-governed-path-write-gate-v2.md) — the packet this ADR could not retire is the motivating case.

---

## Context

The dispatch lifecycle shipped in July as slices S1 through S5 of
`session-lifecycle.md`. Measured 2026-09-02 against `willow-mcp` at `120dead`:

| Transition | Verb | Check |
|---|---|---|
| new → pending | `dispatch_send` | signs meta, hashes assignment |
| pending or cleared → working | `dispatch_accept` | recipient matches |
| any → complete | `handoff_write_v4` | recipient matches |
| complete → verified | `verify_handoff` | two booleans the specialist set; each finding has text |
| complete or verified → cleared | `agent_clear` | none |
| → closed, → failed | *no verb* | |

`VALID_STATUSES` (`roles.py:11`) admits seven states. Five are reachable.
There is no withdraw, no fail, no return, no expiry, no archive. A specialist
who cannot do the work has no honest exit. An orchestrator who rejects a
handoff has no way to say so in the record. A pending packet lives forever,
and the specialist's next `session_enter` auto-accepts the oldest one.

The packet carries no authorization. `meta.json` names from, to, role,
phase, priority, and reply-to. It does not name the envelope the work rides
on, the repository, or the paths. The syscall table (`verbs[10]`, dispatch)
says *"a dispatched task carries the citing envelope with it."* It does not.
`E8FD5CC1` cited its envelope in prose; the envelope was not in the enforced
registry; nothing noticed for eleven days.

Verification is declaration-checking. `verify_handoff` (`handoff.py:150`)
confirms `checklist_resolved` and `envelope_clean`, both of which the
specialist supplied and both of which default to true. Evidence references
are not opened. The north star's ORIENT.md asked for four checks: checklist
done, evidence attached, ledger anchors present, envelope clean. Two are
implemented, and those two are self-reports.

Three packets have ever existed. Two from 2026-08-11 reached `verified`,
were never cleared, predate signing, and are now filed as `legacy_unsigned`
outside the main list. The third is pending and cannot be retired.

The survey that names this gap is three weeks old. The north star that
specifies the fix is eight weeks old. Nestor took the intervening time, and
Nestor is the reason the fix is now small: the state discipline it produced
is exactly what the packet lacks.

## Decision

Adopt a closed state model on the existing filesystem packet. Do not adopt
an engine. Conductor supplies the terminal set and the human-task semantics;
Nestor supplies the rejection-with-reopen shape and the rule that a yes
cannot be self-issued. The packet stays a directory of JSON and Markdown
under `$WILLOW_HOME/dispatch/`, signed as today.

### States

| State | Meaning | Terminal |
|---|---|---|
| `pending` | cut, not yet accepted | |
| `working` | accepted, specialist executing | |
| `complete` | handoff written, awaiting verify | |
| `verified` | orchestrator verified | |
| `returned` | orchestrator rejected the handoff with a reason and a reopen condition | |
| `failed` | specialist handed the work back with a reason | |
| `cleared` | specialist released; packet awaiting archive | |
| `withdrawn` | orchestrator retired it before acceptance | yes |
| `expired` | pending past `expires_at` | yes |
| `closed` | archived after clear | yes |

Ten states. `VALID_STATUSES` grows by three (`returned`, `withdrawn`,
`expired`). Every state has at least one verb that reaches it and one that
leaves it, or is terminal.

### Transitions and verbs

| From | To | Verb | Seat | Ledger |
|---|---|---|---|---|
| new | pending | `dispatch_send` | orchestrator | `dispatch_sent` (exists) |
| pending, cleared, returned | working | `dispatch_accept` | specialist | — |
| working | complete | `handoff_write_v4` | specialist | — |
| working | failed | `handoff_write_v4(outcome="failed", reason=…)` | specialist | — |
| complete | verified | `verify_handoff` | orchestrator | `dispatch_verified` |
| complete | returned | `dispatch_return(reason, reopen_when)` | orchestrator | `dispatch_returned` |
| verified, failed | cleared | `agent_clear` | orchestrator | — |
| pending, returned | withdrawn | `dispatch_withdraw(reason)` | orchestrator | `dispatch_withdrawn` |
| pending | expired | lazy, on read, when `now > meta.expires_at` | system | `dispatch_expired` on first observation |
| cleared, withdrawn, expired | closed | `dispatch_close` | orchestrator | — |

Three new verbs: `dispatch_return`, `dispatch_withdraw`, `dispatch_close`.
One extended verb: `handoff_write_v4` gains `outcome` (`complete` |
`failed`) and `reason`. All four join `ORCHESTRATOR_WRITE_TOOLS` where the
seat is the orchestrator, so they sit behind the same attestation gate as
`agent_clear`. `dispatch_accept` also admits `returned`, so a corrected
packet does not need to be re-cut.

`agent_clear` drops `complete` from its admitted set. Clearing an unverified
handoff was the one path that let the orchestrator skip verify; the north
star has no such path.

`_pending_for_app` excludes `expired` and `withdrawn`. The auto-accept on
`session_enter` therefore cannot bind a specialist to a retired packet.

### The packet carries its authorization

`meta.json` gains two signed fields:

```json
"envelope_ids": ["env-fs.write-willow-mcp-2026-09"],
"target": {"repo": "willow-memory/willow-mcp", "paths": ["src/willow_mcp/bundle/hooks/pre_tool_use.py"]},
"expires_at": "2026-10-02T00:00:00Z"
```

- `dispatch_send` refuses to cut a packet whose `envelope_ids` are not all
  present in `active[]` of the **enforced** registry
  (`$WILLOW_HOME/constitutional/pre-approved.json`), returning the syscall
  table's `ENOENT`. An empty list is allowed only when `role` is one whose
  work needs no envelope (audit, research); the registry's role table says
  which. This is the check that would have refused `E8FD5CC1` on 2026-08-22.
- `dispatch_accept` re-checks the same list. An envelope that expired between
  send and accept returns `EEXPIRED`, and the packet moves to `expired`.
- `target` is informational to the gate today and is what a later slice
  binds the specialist's `fs.write` to. It goes in now so the packet is
  truthful even before it is enforced.
- `expires_at` defaults to thirty days from `created_at`. The ceiling is the
  shortest `expires_at` among the cited envelopes; a packet may not outlive
  its grant.

### Verify means verify

`verify_handoff` checks all four of the north star's conditions:

1. Checklist: every `- [ ]` in `assignment.md` has a matching `- [x]` in
   `closeout.md`, or the handoff names it in `unresolved[]` with a reason.
   The specialist's `checklist_resolved` boolean is retained as a
   declaration and compared against the parse; disagreement fails verify.
2. Evidence: every finding carries at least one `evidence` reference, and
   each reference resolves to a file that exists in `target.repo` at the
   named path. Line ranges are not checked. Absent `target`, existence is
   checked against the workspace.
3. Ledger anchors: when FRANK is present, `handoff.json` carries
   `frank_anchor`, the id of the last FRANK entry the specialist wrote or
   observed, and it resolves. Absent FRANK, this check is skipped and the
   result says so.
4. Envelope clean: the specialist's declaration, retained, plus a check
   that no auto-proposed envelope from this session is still pending in
   `proposals[]` for this grantee. A pending proposal means the specialist
   hit a gate miss and the work may have routed around it.

A verify that fails does not silently leave the packet at `complete`. The
result carries `failed_checks[]`, and the orchestrator's next move is
`dispatch_return` with that list as the reason, or `agent_clear` is refused.

### Legacy packets

`C17010F0` and `3647BA07` predate signing. A one-time operator CLI,
`willow-mcp dispatch resign <id>`, signs the existing meta under the current
key and records `dispatch_resigned` in FRANK with the operator's attestation.
No MCP tool does this. After re-signing, both can be cleared and closed
through the normal verbs.

### What stays out

- **DAG, `dag_next`, `status_report`.** The north star specifies them.
  They remain earn-first per the slice backlog. This ADR closes the loop on
  one packet; walking a graph of packets is the next decision, and it is
  cheaper once packets have terminal states.
- **Binding `target.paths` in the sandbox.** The field lands; the bwrap bind
  from it is the fs.write enforcement slice.
- **Kart-inside-bwrap specialists.** Still no MCP client, still no path
  back. Unchanged.
- **Postgres mirror schema.** `dispatch_tasks` gains the three statuses and
  the two fields as nullable columns. Best-effort, as today.

## Consequences

**Gains.** Every packet ends. Every end is recorded. A specialist can
refuse. An orchestrator can reject. A retired packet cannot be
auto-accepted. A packet cannot be cut against an envelope that does not
exist, and cannot outlive one that does. Verify opens the evidence.

**Costs.** Three verbs, one extended verb, two signed fields, a CLI, and a
verify that reads files. Roughly the size of the envelope-accrual PR5. The
ORCHESTRATOR_WRITE_TOOLS set grows from ten to thirteen, and the two
design docs that count it need the number changed.

**Risks.** Evidence checking against `target.repo` reads the filesystem
from the server process. That is a read under `paths.trusted_read`
discipline, same as the registry. It is not a write and creates no new
authority.

## Verification

`tests/test_dispatch_lifecycle_closed.py`, replayed through `server.*`:

1. `dispatch_send` with an `envelope_ids` entry absent from the enforced
   registry → `ENOENT`, no packet directory created.
2. `dispatch_withdraw` on pending → `withdrawn`; `_pending_for_app` no longer
   returns it; `session_enter` for the grantee binds idle.
3. `handoff_write_v4(outcome="failed")` → `failed`; `agent_clear` admits it;
   `verify_handoff` refuses it.
4. `dispatch_return` on complete → `returned`; `dispatch_accept` admits it;
   the reason and `reopen_when` are in `status.json` and FRANK.
5. A pending packet with `expires_at` in the past reads as `expired` and is
   excluded from auto-accept.
6. `agent_clear` on `complete` → refused.
7. `verify_handoff` with a finding whose evidence path does not exist →
   `verified: false`, `failed_checks: ["evidence"]`.
8. Existing `test_at_m2_dispatch_lifecycle.py` and
   `test_dispatch_stack.py` pass unchanged, except where they assert the
   old `agent_clear` on `complete`.

## Ratification

This ADR changes willow-mcp code and the FRANK event vocabulary. It changes
no envelope and no syscall table row. The authorizing envelope for the build
is the same question the companion proposal puts to root: a narrow
`fs.write` over the dispatch, handoff, roles, and human_session modules
plus their tests, one grantee, thirty days. One grant can cover both builds
if root prefers; the paths differ and are listed in each.

## Provenance

Every claim about current behaviour was produced 2026-09-02 by reading the
indexed tree at `120dead` through the code graph: `dispatch.py` (send,
accept, set_status, agent_clear, `_pending_for_app`), `handoff.py`
(write_v4, verify), `roles.py` (`VALID_STATUSES`). The dispatch history is
from `dispatch_list` against the live home. The north star and the survey
were read in full. The retirement attempt that motivated this is FRANK
`1ebb1680` and gap `afa515539c0a`.

*ΔΣ=42*
