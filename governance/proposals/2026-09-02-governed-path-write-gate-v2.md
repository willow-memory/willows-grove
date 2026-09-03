# Proposal — governed-path write gate, put to root directly

**Status:** proposal · drafted by willow 2026-09-02 · **root's decision, then a willow-mcp code change**
**Build order:** 4 of 6 — see [`2026-09-02-build-order.md`](2026-09-02-build-order.md)
**Supersedes:** [`2026-08-22-governed-path-write-gate.md`](2026-08-22-governed-path-write-gate.md) — same finding, same three edits; only the authorization route changes.
**Retires:** dispatch `E8FD5CC1` (willow → hanuman, 2026-08-22, never accepted).
**Companion:** [`2026-08-21-registry-path-repoint.md`](2026-08-21-registry-path-repoint.md) §F, still open.
**Target:** `willow-mcp/src/willow_mcp/bundle/hooks/pre_tool_use.py` (mirrored at `willow-mcp/hooks/pre_tool_use.py`; `test_hook_parity.py` pins the two together)

---

## Why this is back on root's desk

The 2026-08-22 proposal routed the fix through `env-fs.write-willow-mcp`,
grantees `hanuman` and `kart`. Dispatch `E8FD5CC1` was cut against that
envelope the same night. It sat eleven days unaccepted, and on 2026-09-02 the
seat checked the envelope before re-issuing it:

| registry | entries | `env-fs.write-willow-mcp` |
|---|---|---|
| enforced — `$WILLOW_HOME/constitutional/pre-approved.json` | **1** (`env-envelope.apply-planting`, tranche 0) | **absent** |
| charter — `envelopes/pre-approved.json` in this repo | 15 | present, `paths[]` pre-move, `expires_at: null` |

So the grant the brief cited exists only in the charter copy. The enforcing
registry has never carried it since the 2026-08-11 restore. **No agent holds
an active fs.write over willow-mcp today.** `E8FD5CC1` could not be accepted
under any envelope, and re-issuing it would reproduce the same dead end.

The companion proposal's §F asks root to decide the fate of that envelope
(expiry, two grantees, repoint). That decision has not been recorded. This
proposal does not wait on it: it asks root for one narrow grant, or for root's
own hand, and nothing else.

## The finding, re-verified 2026-09-02

Checked against the local `willow-mcp` tree at `120dead`, through the code
graph rather than by running the hook. The 2026-08-22 finding stands
unchanged:

- No `_GOVERNED_LAW_RE`, no `_GOVERNED_LAW_REASON`, no rule naming
  `pre-approved.json` or `syscall-table.json` anywhere in the hook.
- `check_trust_root_write` (lines 735–756) gates leases, the keystore, and
  manifest escalation. Nothing else.
- `check_bash_self_grant` (lines 684–715) is the only consumer of
  `_WRITE_VERB_RE` (line 596). Same three surfaces.
- `_ROUTE_FS_MUTATE_RE` (line 172) is still `warn` tier and still omits
  `sed -i` and redirection.
- The orchestrator lift is still exactly `_GIT_GH_ROUTING` (line 210), with
  the explanatory comment at lines 124–130.

The hook file was touched by recent commits, not for this. One caveat the
seat cannot close from here: the graph indexes the local checkout, and this
box has not been reconciled against origin after the operator's recent remote
sessions. If the gate landed remotely and was never pulled, the index would
not show it. Root should confirm against `origin/master` before acting.

## A wording defect in the table, noticed on the way

`syscall-table.json` says two different things about who edits it:

- `invariants[2]`: *"Editing this table is itself verb 11 (envelope.issue)"*
- `verbs[11]` (id 12, `envelope.issue`): *"Create, widen, renew, or revoke an
  envelope; edit this table."*

Verb 11 is `dispatch`. The invariant line predates the id 4 insertion noted
in `lineage` and was never renumbered. It changes no enforcement (the table's
`enforcement` for id 12 is hard and root-only either way), but the gate this
proposal adds will cite verb 12 in its reason string, and the table should
agree with itself when someone follows the citation. **Fixing that line is
verb 12 and is root's; noted here, not proposed as a rider.**

---

## The change — unchanged from 2026-08-22, restated with what the brief added

Three edits. Reuse `_WRITE_VERB_RE`; do not add a third write vocabulary.

### 1. Name the governed paths

```python
# The law itself: the envelope registries and the syscall table. A write here
# is verb 12 (envelope.issue — root-only, non-grantable) or verb 13 (scribe
# under citation, via envelope_apply). Neither is a file edit, in any tool.
_GOVERNED_LAW_RE = re.compile(
    r"(?:^|/)(?:envelopes/pre-approved\.json"
    r"|constitutional/(?:pre-approved|syscall-table)\.json)$|"
    r"constitutional/(?:pre-approved|syscall-table)\.json\b"
)
```

This is the sketch, not tested code. The implementer validates it against
both real paths — the charter copy and the enforced copy — and reports the
regex actually shipped. Filenames, not directories.

### 2. Shell gate — beside `check_bash_self_grant`, before routing

```python
if _WRITE_VERB_RE.search(command) and _GOVERNED_LAW_RE.search(command):
    return _GOVERNED_LAW_REASON
```

### 3. Write/Edit gate — inside `check_trust_root_write`

```python
if _GOVERNED_LAW_RE.search(path):
    return _GOVERNED_LAW_REASON
```

Both `block`, both through the existing dispatch in `main()` (lines 769–809).
No new tier.

**Reason string** — must name the legitimate path:

> This file is the envelope registry / syscall table. Editing it is **verb 12**
> — root-only and non-grantable — and recording an act against it is **verb 13**,
> `envelope_apply`, which scribes under citation. Neither is a file write. Draft
> the change as a proposal under `governance/proposals/` and put it to root.

### Constraints

- **Reading stays open.** `cat`, `jq`, `Read`. Only `_WRITE_VERB_RE` matches
  trip the shell gate, exactly as the keystore rule works.
- **`governance/proposals/` stays writable.** This document is the proof.
- **Not lifted for the orchestrator seat.** `check_bash_routing` lifts exactly
  `_GIT_GH_ROUTING` for willow; this gate is the opposite case. Extend the
  comment at line 124 to say so.
- **`warn` is not an option.** Warn decisions do not reach the model. Block
  or nothing.

### Verification — five cases

1. `sed -i` on `envelopes/pre-approved.json` → `block`
2. `>>` onto `$WILLOW_HOME/constitutional/pre-approved.json` → `block`
3. `Edit` on either → `block`
4. `cat` / `jq` on either → not blocked
5. `Write` to `governance/proposals/anything.md` → not blocked

Plus `test_hook_parity.py` and `test_hook_wiring_sync.py`, which cover the
bundle/source mirror.

---

## What root is asked to decide

One of two, recorded before anyone opens the file:

**(a) Grant.** Issue a fresh envelope, verb 1 `fs.write`, one grantee,
`paths[]` naming only the hook file, its mirror, and
`tests/test_pre_tool_use_hook.py`, with an expiry — thirty days is enough.
Willow scribes it under `env-envelope.apply-planting` (verb 13, live) and
re-cuts the dispatch against it. The 2026-08-22 brief serves as the
assignment body unchanged; only the envelope id differs.

**(b) Own hand.** Root makes the three edits directly. No envelope needed;
root is not an agent. Willow records the act in FRANK after the fact from
the commit.

The seat recommends **(a)**. The change is small, but the review that a
dispatch-and-handoff produces is the point: a gate on the law should not be
written by the same hand that holds the law, even when that hand is root's.

## What this does not decide

- The fate of the fifteen charter-copy envelopes (companion §F). Separate.
- Whether the rest of `_BASH_ROUTING` moves to `block`. Gap `c2fffe6af8f2`.
- The verb 13 relative-path bounds signature. Gap `006e0144da95`,
  [`2026-08-22-syscall-table-verb13-bounds.md`](2026-08-22-syscall-table-verb13-bounds.md).

## Provenance

Every claim above was produced 2026-09-02 from live reads, not from the
2026-08-22 documents: the active registry by `envelope_list`, the hook by
`code_graph_search` and `get_code_snippet` over the indexed tree at
`120dead`, the syscall table by reading
`$WILLOW_HOME/constitutional/syscall-table.json`, the dispatch by
`dispatch_read`. Nestor holds no sealed pair on the gate or on verb 12; the
knowledge base returns nothing for the proposal name. The argument lives in
these files and nowhere else.

The retirement of `E8FD5CC1` is authorized by the operator in-session
2026-09-02 and is pending session attestation before it can be scribed to
FRANK and cleared.

*ΔΣ=42*
