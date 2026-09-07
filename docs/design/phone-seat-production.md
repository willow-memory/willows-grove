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
  box (`WILLOW_MCP_PORT` or `--port 8768`). The package default in source is
  still **8765** until that is re-ratified in code.

**Resolution for the phone seat:** sign in to `willow-mcp --serve`, never to
the Grove desk, never to Nestor UI by mistake.

- Local default on this box: `http://127.0.0.1:8768`
- Remote: Pangolin fronts **that same --serve process** (8768 on the box),
  not 8765. Re-ratify the 2026B306 “terminates at 8765” sentence against this
  table, or move `--serve` back to 8765 only after the origin-bound key on
  8765 is fixed. Until then the phone’s ratified URL is 8768.
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
