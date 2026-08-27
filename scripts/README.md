# scripts/

Operator-run helpers around Grove. Not application code — nothing else in the
repo imports from here; each script is invoked by a human (or a systemd unit
they wrote) and does one thing.

## `grove-serve`

Toggle the `grove-mcp-serve` systemd `--user` unit (`--serve` mode of the
Grove MCP server) and the matching entry in this repo's `.mcp.json`. See the
header of the script for the subcommand list. Loopback-only by default.

## `grove-serve-run`

Foreground launcher for the Grove *served-page* skeleton (`grove_serve.py`
on `127.0.0.1:8766`). Sets `WILLOW_HUMAN_ORCHESTRATOR=1` and echoes the URL.
Used interactively during development; the persistent variant is
`deploy/grove-serve.service.template`.

## `mcp_entry_toggle.py`

Backend used by `grove-serve` to edit `.mcp.json` in place.

## `nestor_reseed.py` — re-emit sealed design decisions into a persistent Nestor store

Copies every sealed pair (plus its evidence and warrant rows) from the
design conversation's scratch Nestor store into a Grove-owned persistent
store at `$WILLOW_HOME/nestor/willows-grove.db` (default
`~/.willow/nestor/willows-grove.db`). Preserves every field — `source_text`,
`source_norm`, `target_text`, `verifier`, `weight`, `origin`, `seal_sig`,
and every attached evidence + warrant row. Idempotent: pairs whose
`source_norm` already exists at the destination (under the same lang pair)
are skipped whole, so a re-run after a partial pass converges cleanly.

This is the runtime cash-out of the **Discipline** section of
`docs/design/willow-grove-premise.md` — *"point memory infra inward: Grove's
design decisions live in a Nestor store … a Grove-owned Nestor store on
`$WILLOW_HOME/nestor/willows-grove.db` holds every design decision as an
evidence-backed sealed pair."* With the persistent store in place, future
Grove sessions can run `nestor decision check "<question>"` before proposing
any new design, and the seed's boot injection has a stable home to read
from.

Usage:

```bash
pip install nestor-meaning       # provides nestor.sqlite_store.SqliteStore
python3 scripts/nestor_reseed.py
# Overrides:
python3 scripts/nestor_reseed.py --src /path/to/source.db --dst /path/to/dst.db
WILLOW_HOME=/opt/willow python3 scripts/nestor_reseed.py
python3 scripts/nestor_reseed.py --dry-run
```
