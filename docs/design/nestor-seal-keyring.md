@markdownai v1.0

# Nestor seal keyring: which key signs, which file each reader uses

Written by Ada for packet 0B46D2DF, 2026-10-07. This is the third keyring split in three weeks. This page records the cause and gives a one-step check. Names, paths and the first 8 hex of each public key appear here. No key material does.

Contents: §1 The signer · §2 Who reads what · §3 Why the desk fails · §4 The fix · §5 One-step check · §6 Export source · §7 How this keeps recurring

## §1 The signer

| Fact | Value | Evidence |
|---|---|---|
| Verifier name | `sean campbell` | ledger `nestor.db.ledger.jsonl`, every seal row since 2026-09-14 |
| Signing keyring | `$WILLOW_HOME/verifiers.json` (box root) | `$WILLOW_HOME/env` line `NESTOR_KEYRING=` → nestor-ui reads it through `EnvironmentFile=` (`~/.config/systemd/user/nestor-ui.service:67`) |
| Signing key (ed25519 public, first 8 hex) | `f8c34c93` | `$WILLOW_HOME/verifiers.json`, entry created 2026-09-14T18:42 ("operator rotate 2026-09-14") |
| Same key, public-only copy | `/etc/willow-mcp/verifiers.public.json`, `f8c34c93` | net-signer unit `WILLOW_NET_SIGNER_RING` (`/etc/systemd/system/willow-mcp-net-signer.service:21`); exported 2026-09-20 |

Every seal nestor-ui writes is either signed server-side with that entry's private half (`signing.sign_seal` → `keyring.signing_entry`) or arrives client-signed and is verified against that entry before the write (`ui._seal_draft` → `memory.add_pair(seal_sig=...)`). In both cases, a seal row that exists verified under `f8c34c93` when it was written.

`constitutional/trust.env` (`970B50E7…`) is the PGP fingerprint for willow's constitutional signing. It plays no part in Nestor seals.

## §2 Who reads what

| Reader | Keyring it verifies seals against | Key | DB |
|---|---|---|---|
| nestor-ui (:8765, the signer) | `$WILLOW_HOME/verifiers.json` via `$WILLOW_HOME/env` | `f8c34c93` | `$WILLOW_HOME/nestor.db` |
| net-signer (system unit) | `/etc/willow-mcp/verifiers.public.json` | `f8c34c93` | `$WILLOW_HOME/nestor.db` (via willow-mcp `net_authority.read_sealed_pair`) |
| desk `nestor` MCP (willows-grove `.mcp.json:47`) | `$WILLOW_HOME/config/verifiers.json` | **`c3d1a7fc`** | `$WILLOW_HOME/nestor.db` |
| willow-mcp (seat; `reloader._load_verify_ring`, `seed_loader.load_sealed_corrections`, grant / amendment checks) | `WILLOW_KEYRING` = `$WILLOW_HOME/config/verifiers.json` (`.mcp.json:16`, `env:65`) | **`c3d1a7fc`** | `$WILLOW_HOME/nestor.db` |

All four readers open the same DB. Two keys are in play.

## §3 Why the desk fails

| Seals | Cause | Evidence |
|---|---|---|
| New ones (2026-09-14 onward, including 440d91ee, 2eddbc61, 261b3572, 6236a815) | The desk verifies against `config/verifiers.json`, whose `sean campbell` entry is a **different keypair** (`c3d1a7fc`, created 2026-10-01T11:47:18). It was regenerated during the 2026-10-01 public-only incident and its "rotate back". `KEYRING-PARTITION.md` (2026-09-14) says the two files share key material, and they no longer do. | `config/verifiers.json` `created_at`. `nestor_provenance 440d91ee-…` reports `key_type: ed25519` (the c3d1a7fc entry holds a private half) and `signed_by: none` |
| Old ones (before 2026-09-14, e.g. b24a97da 2026-09-03) | They were signed by the retired `d65d64…` key, whose private half was lost. No live keyring carries it, so they fail under **every** reader, nestor-ui included. This is expected and permanent until a human re-seals them. | `$WILLOW_HOME/KEYRING-PARTITION.md` epoch table |

The DB is not a cause: all four readers open the same `nestor.db`. Kart's copy is a stale snapshot (last row 2026-10-02), so it cannot be used to verify anything current.

## §4 The fix

Point every reader that only **verifies** at the public-only ring `/etc/willow-mcp/verifiers.public.json`. That file is root-owned, holds no private half and can't sign. It is already the net-signer's anchor, and only a root action changes it. `$WILLOW_HOME/verifiers.json` stays the one signing keyring, used only by nestor-ui.

Table 1: `.mcp.json` §nestor (willows-grove)

```diff
-        "NESTOR_KEYRING": "/home/sean-campbell/sean-data-vault/willow-operator-box/config/verifiers.json",
+        "NESTOR_KEYRING": "/etc/willow-mcp/verifiers.public.json",
```

After this is committed, run `/mcp` reconnect for `nestor`. `nestor.keyring.load` accepts a public-only ring at any mode (`keyring.py:429-441`).

willow-mcp's `WILLOW_KEYRING` does two jobs: session attestation (sign-session needs a private half) and Nestor seal verification. Those jobs must not share a file. Until willow-mcp verifies Nestor seals against the public ring (a code change), there are two ways to make willow-mcp's seal checks pass again:

- (a) The operator restores `config/verifiers.json`'s `sean campbell` entry to the `f8c34c93` keypair from `$WILLOW_HOME/verifiers.json`, as `KEYRING-PARTITION.md` intends. Keep mode 600, then run sign-session again. Session sidecars signed under `c3d1a7fc` since 2026-10-01 stop verifying.
- (b) A willow-mcp change: Nestor-seal verification reads the net-signer ring instead of `WILLOW_KEYRING`.

Both change the operator's own key or code, so neither was done by Ada.

## §5 One-step check

Run `nestor_provenance <full pair id>` from the desk on any seal made after 2026-09-14. It should return `signature_valid: true`, `servable: true` and `signed_by: verifier`. If it returns `signed_by: none` with `key_status: active`, the reader's keyring holds a different `sean campbell` key from the signer's. Compare the first 8 hex of `key` for `sean campbell` in the reader's `NESTOR_KEYRING` / `WILLOW_KEYRING` file with `f8c34c93`.

## §6 Export source

For the one-script public-only export (`onescript keys export`, willow-bot packet 56F80C2D), the correct `--from` is `$WILLOW_HOME/verifiers.json`, the signer's keyring. Its public projection is identical to `/etc/willow-mcp/verifiers.public.json`, except that it also carries the revoked `willow` entry, which verifies nothing. **Never** use `config/verifiers.json` (`c3d1a7fc`, not the seal signer).

## §7 How this keeps recurring

Three files each hold a `sean campbell` entry: `verifiers.json`, `config/verifiers.json` and `/etc/willow-mcp/verifiers.public.json`. A rotate or regeneration of one of them silently splits the others. The 2026-10-01 incident regenerated `config/verifiers.json`, and nothing compared it to the signer. The rule:

- Exactly one file signs Nestor seals: `$WILLOW_HOME/verifiers.json`.
- Every Nestor verifier reads the public ring exported from it.
- Any edit to any keyring is followed by the §5 check on one fresh seal.
