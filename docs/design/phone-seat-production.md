<!-- b17: WGRV1  ΔΣ=42 -->
# Phone seat — production name and serve URL

2026-09-06. Inspiration in historical docs may still say Jarvis. **The
product name is Willow.** The Capacitor tree remains at
`safe-app-store-public/apps/jarvis/` until a later store rename.

See also: [seat-stack.md](seat-stack.md) (how Ratatosk, MCP, and Grove fit
together), [phone-tier0-sync.md](phone-tier0-sync.md) (homecoming deposit).

## Production ids

| Surface | Value |
|---|---|
| Launcher / document title | Willow |
| Android `applicationId` / namespace | `dev.willowmemory.willow` |
| Capacitor `appId` | `dev.willowmemory.willow` |
| OAuth `client_name` / MCP `clientInfo.name` | `willow` |

`dev.quickstupids.jarvis` must not ship.

## Port truth (gap `d8b0bea7e205`)

Two older sentences disagreed:

- KB 2026B306 / an older runbook row: Pangolin terminates at **8765**, and
  that port was `willow-mcp --serve`.
- Operator 2026-09-02: signing outranks serve. **8765** is Nestor UI / keep
  store / origin-bound verifier key. **`willow-mcp --serve` is 8768** on this
  box (`WILLOW_MCP_PORT` or `--port 8768`; set by the systemd drop-in
  `willow-mcp-serve.service.d/port-8768.conf`, which overrides the unit's own
  `--port 8765`). The package default in source is still **8765**
  (`server.py:489`) and that is correct for a fresh deployment elsewhere — the
  operator table governs this box, not the product.

**Resolution for the phone seat:** sign in to `willow-mcp --serve`, never to
the Grove desk, never to Nestor UI by mistake.

- Local default on this box: `http://127.0.0.1:8768`
- Remote: Pangolin fronts **that same --serve process** (8768 on the box),
  not 8765. ~~Re-ratify the 2026B306 “terminates at 8765” sentence against this
  table~~ — **done 2026-09-09**, operator: *“serve is on 8768, update the map.”*
  2026B306's port is superseded; tier 2 terminates at **8768**. The phone's
  ratified URL is 8768, no longer provisionally.
- **8766** stays loopback (D4). This app refuses a serve URL whose port is
  8766.
- **8767** is Grove MCP (`grove/mcp_local.py --serve`) — OAuth, not the phone
  Capacitor sign-in target.

The browser-key origin gap remains a Nestor UI problem on 8765. It is not
the phone’s sign-in port.

## First APK (2026-09-06)

Built on the host, not in Kart: `apps/jarvis/android` →
`app/build/outputs/apk/debug/app-debug.apk`, package
`dev.willowmemory.willow`. Installed on Waydroid `192.168.240.112:5555`.
`--serve` was already listening on 8768; `adb reverse tcp:8768 tcp:8768`
makes that URL reachable from the device. PKCE popup not completed in this
session.

## The phone only proposes (2026-10-08)

The operator, 2026-10-08: *"Phone only proposes, seal in Nestor on the box."*
Recorded here only, for now: *"Just in the grove for now."*

The phone holds no seal key. Every seal, of a scope or of a proposal, is
made in Nestor on the box. Serve hands out only a sealed scope, so a phone
turn starts and ends on the box:

| Step | Where |
|---|---|
| `checkin`, `scope`, seal the scope in Nestor, `serve` | box |
| `served.json` to the phone | USB (tier 0) |
| Rat `--onescript` reads it, writes `proposals.jsonl` | phone, offline |
| `proposals.jsonl` back to the box | USB (tier 0) |
| `take_proposals`, seal each in Nestor, write, `checkout` | box |

What follows from it:

- No `cryptography`, keyring or seal key on the phone. A lost phone holds
  served data and drafts, not authority.
- The one script's record and its gates stay on the box, where the gates can
  always run; the phone never runs with `--phone`.
- The APK's seal screen is not needed; the UI is choose the served task, run,
  review proposals, wait for the box.

Still open, not decided by this line:

- An in-process local rung for Rat, so the APK can drop `INTERNET` (a
  loopback server on a phone is open to every app on it).
- The box sizes `serve --max-chars`, so it must know the phone model's
  context window.
- Served text is plaintext on a device that leaves the house, bounded by the
  sealed scope.
- The USB handoff (steps 2 and 4) and the hash recorded at each end: the sync
  stage, still undesigned.
- Whether a 1–3B model calls `propose` reliably: unmeasured.
