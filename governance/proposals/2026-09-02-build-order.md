
## Progress — 2026-09-03, recorded by the willow seat

Read against the rows above, from the record (handoff `2026-09-03-df72e542`, FRANK 80609939 / 93e041a1 / 4db66d5b, #handoffs 375).

| Step | Moved | Still open |
|---|---|---|
| 0 | Operator sealed 99 pairs in `nestor.ui` on 8765, 67 of them Forge-origin; the Forge project store now holds them verified against the fleet keyring. | The design-intent atom is unchanged. |
| 1 | **Done.** ada retired 22 fossil units under envelope `env-shell.exec-b31eee38a08f`, packet 276C7A34 verified and cleared; after-state matches the retirement record. | The two ngrok units (binary still present) left for the operator. |
| 2 | The house can now hear: `willow-mcp grove-listen --app-id <seat>` (willow-mcp #421, merged) is 2.0's LISTEN/NOTIFY monitor rebuilt on the gate; the session-start skill names it for every seat. Session-end deposit done by hand this once: handoff file plus a pointer in #handoffs. | Tracked hooks, reinject, stop gate, Grove in the corpus — untouched. jeles and loki still hold no `grove_read`. Presence reads six hours stale (naive local timestamps read as UTC, gap a2ea88cc006b). |
| 3 | First full lifecycles on record: six packets sent under a ratified `dispatch` envelope, accepted, handed off, verified against the artifact, cleared (D83F9739, A47DD0CB, 276C7A34, 5ED80CC1, A09139D2, C01EA727). E8FD5CC1 parked by hand (`status.json` closed, meta untouched). | No withdraw verb still (afa515539c0a). `verify_handoff` demands a `text` key per finding that `handoff_write_v4` never asks for (5805dba0ad47). Witness and architect seats needed operator grants to close at all (2f20111ea877). |
| 4 | The enforced register was used as law for the first time since the planting: eight envelopes proposed and ratified under a keyring-attributed session; `dispatch_send` refused a role outside the envelope's task class (EAMBIG) and was right. | The register writer leaves `pre-approved.json` group-writable after every write, so `trusted_read` refuses the next read until the operator chmods (6b4b7737c535). Attestation and attribution are two locks under two key systems (bcd8b6d918da). Forge pushes had no envelope of their own; recorded on FRANK instead. |
| 5 | Nothing. The five packets were reviewed for fit against the seam proposal's own rule and none was safe for a local model; Sonnet seats ran them. | As drafted. |
| 6 | Nothing. | As drafted. |

Landed elsewhere the same night, feeding row 3: Forge #5 (PR-time deposit, propose-only as a type after loki's review), #6 (bundle cut/check, witnessed by skirnir), #8 (store diff, both loki notes fixed on-branch); v0.2.0 tagged; willow-bot #10 (bridge keys check runs on the check id, carries head_sha); store #219 (record-gate pointer).
