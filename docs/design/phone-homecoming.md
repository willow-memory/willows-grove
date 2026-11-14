<!-- b17: WGRV1  ΔΣ=42 -->
# Phone seat — homecoming

Written 2026-09-06 as "tier 0 homecoming"; rewritten 2026-11-13, when the
operator settled that the carrier and the destination are the person's
choice, and dropped the tier name. This replaces the missing mobile-vault
design note (`docs/design/phone-surface-context.md` §12, re-searched
2026-09-03, still unfound). It is not a second sync protocol.

Stack context: [seat-stack.md](seat-stack.md).

## What is fixed, for every person

**The payload.** The session-end **deposit** is what comes home. On the box
that is already the grove-hooks deposit (`kb_journal` + project Nestor pairs
+ stack snapshot). On the phone seat it is the same motion:

- If Nestor is installed on the device: `nestor export` on the project store,
  then `nestor import --apply` at home once the file has arrived.
- If only the Willow Capacitor memory store ran: the in-app **Copy homecoming
  deposit** action writes a `phone-seat-deposit` JSON (see
  `safe-app-store-public/apps/jarvis/src/homecoming.js`). That file is a
  deposit, not a vault replica. Review it; do not treat it as sealed.
- If a Willow kernel box ran on the phone: its `record.jsonl` and
  `kernel.json`, never its key. Home runs `kernel.py verify` on them.

Ratatosk sessions on the phone should end with the same deposit motion when
the operator closes a seat — the session runtime carries facts; homecoming
lands them at home.

**The check at home.** Nothing that arrives is trusted until home has
checked it (the chain, and each seal against a key home already holds). That
check is why the carrier does not matter: a deposit changed on the way is
refused at home, whatever carried it.

## What is the person's choice

- **The carrier.** USB/`adb`, Bluetooth, Wi-Fi, a thumb drive, a file sent
  to oneself: however the person wants to move it. Willow names none as the
  way.
- **Where it lands.** The person names the place — a box, a vault slice,
  both, somewhere else. Willow does not pick one and does not hide a default,
  the same way the kernel is told its pile and its box.

## What this is not

- Not a copy of a live vault snapshot, by any carrier.
- Not a network pull of `:8766`.
- Not a new ciphertext format. Vault secrets stay Fernet under `vault.key`,
  which stays home. The phone carries facts the operator chose to store in
  the seat, which is plaintext-on-device and is why that choice is still an
  open governance item.

## On this machine

The operator's own box, recorded so it is not read as the design: USB/`adb`,
the same wire playgate installs use in the other direction. The first run,
2026-11-13, carried a kernel box's record from Termux to the laptop over
`adb pull` and verified it there (chain held, 4 rows, 0 sealed). Where it
lands here is the operator's to name; the layout of this box's vault is in
[vault-home-store.md](vault-home-store.md).
