<!-- b17: WGRV1  ΔΣ=42 -->
# Phone seat — tier 0 homecoming

Written 2026-09-06. This replaces the missing mobile-vault design note
(`docs/design/phone-surface-context.md` §12, re-searched 2026-09-03, still
unfound). It is not a second sync protocol.

Stack context: [seat-stack.md](seat-stack.md).

## The payload

The session-end **deposit** is what comes home. On the box that is already
the grove-hooks deposit (`kb_journal` + project Nestor pairs + stack
snapshot). On the phone seat it is the same motion:

- If Nestor is installed on the device: `nestor export` on the project store,
  then `nestor import --apply` on the box after USB/`adb` lands the file.
- If only the Willow Capacitor memory store ran: the in-app **Copy homecoming
  deposit** action writes a `phone-seat-deposit` JSON (see
  `safe-app-store-public/apps/jarvis/src/homecoming.js`). That file is a
  deposit, not a vault replica. Review it; do not treat it as sealed.

Ratatosk sessions on the phone should end with the same deposit motion when
the operator closes a seat — the session runtime carries facts; homecoming
lands them on the box.

## What this is not

- Not `adb` of a live vault snapshot.
- Not a network pull of `:8766`.
- Not a new ciphertext format. Vault secrets stay Fernet under `vault.key`,
  which stays home. The phone carries facts the operator chose to store in
  the seat, which is plaintext-on-device and is why that choice is still an
  open governance item.

## Transport

USB/`adb` already moves bytes one way for playgate installs. Homecoming is
the other direction on the same wire. LAN u2u and Pangolin are other tiers;
they do not replace this deposit.
