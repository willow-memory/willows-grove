# Grove persona seal worksheet (Slice A)

Status as of 2026-10-01: **already sealed in Nestor and bridged to Jeles human rung.**
Intake file `grove-persona-partition-seals.json` was the candidate packet; ceremony completed 2026-09-02.

Operator doctrine reminder: sealing is the machine-servable receipt for human work already done — not inventing verification from draft status.

| # | Question | Answer (abbrev) | Nestor pair id | Jeles nugget id | verified_by | corpus_ask |
|---|----------|-----------------|----------------|-----------------|-------------|------------|
| 1 | Who owns Willow's Grove desk? | Willow — operator seat… | `0e434a0b-2acd-4f9d-86ec-d64ca6828a4a` | `i271765f53f` | sean campbell | found:true human |
| 2 | Who owns the Grove watch post? | Heimdallr — watchman… | `564bc2dd-9ab4-4501-8c64-aaebbe38dc69` | `i5344f636b7` | sean campbell | found:true human |
| 3 | Is Willow's Grove a mode switch for Governance / PM / PA? | No. One Jarvis seat… | `1d67f1d2-49a9-4841-a13f-6ac6ff03d272` | `i1033c7358a` | sean campbell | found:true human |

Sources (all three): `willows-grove/docs/design/grove-persona-partition.md` (+ premise / CLAUDE / autonomous-continuity / grove-served-page as tagged in intake).

## Re-prove commands

```bash
# Federated Jeles (works today)
willow-seat.sh jeles corpus_ask '{"app_id":"jeles-corpus","question":"Who owns Willow'\''s Grove desk?"}'

# After Cursor reloads Nestor MCP with fixed mcp.json:
# nestor_ask → text: same questions; expect state sealed, cite pair ids above.
```

## If seals need re-mint (only if signatures stop verifying)

1. Confirm `NESTOR_KEYRING` → `$VAULT/config/verifiers.json` (not `$VAULT/verifiers.json`).
2. `nestor ui --db $VAULT/nestor.db` and seal/re-seal the three pairs as verifier `sean campbell`.
3. Bridge with `nestor-seal-v1` evidence into `corpus.put_nugget(..., verification_kind="human")` or operator-session `corpus_put` + `JELES_CORPUS_TRUST_TOOL_WRITES=1`.

## Slice B (not this worksheet)

Other `jeles-intake/*.json` novel packets remain backlog: human-checked ≠ sealed until ceremony. Seed 968 stays asserted-by-design.
