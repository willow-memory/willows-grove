# Proposal — `manifest.grant` carries federated tool grants

**Status:** ruled **A** by the operator 2026-09-26 ("A") · **built** in willow-mcp (the `mcp:<server_id>:<tool>` grammar in `src/willow_mcp/manifest_grant_executor.py` and `manifest_admin.validate_permission`, on master `15ae7b2`; corrected 2026-09-30, the line used to say "not built")
**Gap:** `133e17b1291f` (recurrence of `6ff907987c41`)
**Repo touched:** `willow-memory/willow-mcp` (one module, one syscall-table row)
**Trigger:** node9 was ratified as federated server `56c491dfe39d` (pair `37cca612`) and still cannot be called, because no path on this box can grant `mcp:56c491dfe39d:<tool>` to any seat.

---

## The problem, measured

A federated server is useless until a manifest grants its tools one at a time
(`gate.py:702`, `mcp:<server_id>:<tool>`; `federated-mcp-gating.md` Decision 1).
Today there are two grant paths, and neither one works for these names:

| Path | Why it fails |
|---|---|
| `willow-mcp allow-permission <app> mcp:<id>:<tool>` (operator CLI) | Signs the candidate manifest **as the invoking human** (`manifest_admin.publish_via_trust_owner` docstring: "Signing has already happened as the invoking human, with that human's gpg-agent"). Since the 2026-09-23 one-key move, the only trusted secret key (`970B50E7…`, `constitutional/trust.env`) lives in the trust owner's `GNUPGHOME` (`/var/lib/willow-mcp/manifest-grant/gnupg`, unit file lines 26-29, 69). Observed 2026-09-26: five calls, each `gpg: no default secret key`, refused before mutation. |
| `manifest.grant` (sealed pair → trust-owner apply) | The sealed-text grammar cannot express the name. `_RULING_RE` (`manifest_grant_executor.py:217-220`) allows groups matching `[A-Za-z0-9_,\-]+`, so the colons in `mcp:56c491dfe39d:node9_explain` never parse. |

The write side is already there. `manifest_admin.validate_permission`
(`manifest_admin.py:52-77`) accepts `mcp:<server_id>:<tool>` and checks the
server id against the ratified registry, and the apply half publishes through
the same `set_permission` path. Only the grammar in front of it refuses.

## The change

1. **Grammar.** Widen the `groups=` token of `willow-manifest-grant-v1`, and
   only there, to accept one extra exact shape beside today's bare names:

   ```
   mcp:[0-9a-f]{12}:[A-Za-z0-9_.\-]{1,64}
   ```

   A 12-hex server id, then a tool name. The existing test pair `d23a3726` still
   parses unchanged. `ruling_text()` needs no change: it already refuses only
   commas and spaces.

2. **Registry check at request AND apply.** Every `mcp:` group goes through
   `manifest_admin.validate_permission` at request time (a refusal names the
   unratified id) and again at apply, the same "re-verify fresh" rule the seal
   and pre-state already follow. A grant naming a server that was revoked
   between request and apply fails `edrift`.

3. **Nothing new becomes grantable.** `mcp_federation` stays on
   `ESCALATION_GROUPS`, so a seat must already hold the capability to spawn
   servers at all. This verb only adds the per-tool names beneath it. The
   envelope's `groups` bound (`list[group-name]`) names the exact `mcp:` strings,
   so an envelope for node9's five read-only tools cannot carry a sixth.

4. **Syscall row 18 text** is updated to name the new shape and the registry
   check.

## The decision that is the operator's

Row 18's `bounds.apps` text says *"the broker's own app_id is never a grantable
member."* That rule is prose only. The row is `"enforcement": "soft",
"enforced_by": null`, and the executor has no such check. Its seat check runs
the other way: the **caller** must be the orchestrator seat
(`manifest_grant_executor.py:102-105`).

The first real use of this change is to grant the orchestrator seat (`willow`)
node9's tools. So the rule needs a ruling, not a quiet skip:

- **A. Allow federated-tool groups for the orchestrator seat, and only those
  groups.** The confirming act is the operator's seal, not the seat's. The
  server was ratified by a separate earlier seal. Every group is a single
  read or act on one tool, `mcp_federation` itself stays ungrantable, and the
  PreToolUse guard's own self-grant refusal (`hooks/pre_tool_use.py:928-940`)
  is unchanged. Enforce it in code: orchestrator seat plus a non-`mcp:` group
  → `EPERM`.
- **B. Keep it absolute.** Enforce "never the orchestrator seat" in code, and
  fix the CLI instead so the trust owner signs (a `sudo -u willow-operator`
  publish that carries its own `GNUPGHOME`). Federated grants to `willow` stay
  a keyboard act.

**Ruling: A** (operator, 2026-09-26). The recommendation stands as written: It turns the last keyboard-only grant into the same
seal → apply shape every other grant already uses. It covers jeles-corpus and
every future server, not only node9. Either way, the soft rule becomes a hard
one.

## Tests (the build's acceptance)

- `mcp:<12 hex>:<tool>` parses; a 11- or 13-char id, uppercase hex, or an empty
  tool name is `EINVAL`.
- An unratified id refuses at request; a server revoked after request refuses
  `edrift` at apply.
- `mcp_federation` inside a pair is still `EPERM` (escalation set unchanged).
- Under A: orchestrator seat plus `grove_write` → `EPERM`; orchestrator seat
  plus `mcp:<ratified>:<tool>` → granted. Under B: orchestrator seat plus
  anything → `EPERM`.
- `d23a3726`'s sealed text still parses to the same seats and groups
  (regression).
- End to end in a throwaway `WILLOW_HOME`: ratify a stub stdio server, then
  seal, request and apply a grant, then check `permitted()` is true for exactly
  the granted tools.

## Out of scope

- `node9 init` hooks, and any gating of tool calls by node9 verdicts.
  Federation stays on-demand.
- The CLI signing mismatch under option A. It stays logged on `6ff907987c41`
  as its own fix.
- Tool-name validation against what a server advertises (it would require
  spawning the server at request time).

## Next, once ruled

Builder packet to willow-mcp (Sonnet builds, Opus audits). Push, open the PR,
watch CI, operator merge, `git_pull_execute`, restart the apply unit. Then the
node9 grant pair:
`willow-manifest-grant-v1 seats=willow groups=mcp:56c491dfe39d:node9_explain,mcp:56c491dfe39d:node9_posture,mcp:56c491dfe39d:node9_policy_get,mcp:56c491dfe39d:node9_egress_status,mcp:56c491dfe39d:node9_status`.

*ΔΣ=42*
