# Retire-with-record — user units from the willow-2.0 generation

**Status:** proposed · drafted by willow 2026-09-02 · **operator's act; nothing here is disabled by the seat**
**Build order:** 1 of 6 — see [`2026-09-02-build-order.md`](2026-09-02-build-order.md)
**Gap:** `abaf0d0d9c75` (fleet-units) · related `8ef0e691b6c2` (trust-root hardening)
**Measured:** unit files by Kart `TK758QVB`; targets on disk by Kart `HXTWWZHF`; live state by the operator's own `systemctl --user list-units --all` at 17:38 MDT.

---

## Live state, 2026-09-02 17:38

| Unit | State | Generation | Verdict |
|---|---|---|---|
| willow-mcp-serve | active running | current | keep |
| willow-mcp-worker-fast | active running | current | keep |
| willow-mcp-worker-batch | active running | current | keep |
| willow-gpg-unlock | active exited (login one-shot) | current | keep |
| downloads-watcher | active running | current (Nest front door, writes to `$WILLOW_HOME/nest/inbox`) | keep |
| openclaw-gateway | active running | not fleet | operator's call, out of scope |
| sentinel-watchdog.timer | active running, every 15 min | **old** | retire |
| sentinel-watchdog.service | **activating (start)**, stuck | **old** | retire |
| kb-snapshot-refresh.timer | active waiting, daily 05:30 | **old** | retire |
| kb-snapshot-refresh.service | **failed** | **old** | retire |
| repo-fleet-sweep.timer | not-found, wanted at boot | **old** | remove dangling link |
| journal-watcher.service | not-found, wanted at boot | **old** | remove dangling link |

Everything else in `~/.config/systemd/user` from the old generation is a
unit file that is neither loaded nor enabled. Their ExecStart targets are
gone from disk, so none can start:

| Unit file | Pointed at | On disk |
|---|---|---|
| drop-server, drop-ngrok | `~/github/willow-2.0/.venv-dev`, `tools/drop_server.py` | missing |
| grove-mcp (old), grove-ngrok, newt-willow | `~/github/willow-2.0/.venv-dev`, `~/github/safe-app-willow-grove` | missing |
| nest-watcher, orin-worker | `~/github/willow-2.0` | missing |
| willow-grove-listen, stuck-loop-watch (+timer), hook-wiring-audit (+timer) | `~/github/willow-2.0` | missing |
| willow-metabolic, willow-upstream-desk, willow-w8-census, willow-wce (+3 timers) | `~/github/willow-2.0/willow.sh` | missing |
| kart-worker, kart-worker-batch (old pair) | `~/SAFE/.venv`, working dir `~/sean-data-vault` | missing |
| gitsync (+timer) | `~/.local/share/gitsync` | not fleet; not in live list, so not enabled |

## What each retiring unit last did

- **sentinel-watchdog.** Runs `~/.willow/fleet-dispatch/sentinel_watchdog.py`
  every fifteen minutes. The script and its directory date from 2026-08-10.
  It appends to `dispatch-log.jsonl`, last written 17:22 today, now 769 KB.
  The service sits in `activating (start)`: the script is waiting on
  something the 2.0 fleet used to provide. Nothing in the current
  generation reads that log. Registered as a "lane 4 tenant" in the
  archived willow-2.0 watchmen (Grove #253, 2026-07-05).
- **kb-snapshot-refresh.** Daily at 05:30, runs an export script under
  `~/github/.willow/claude-science`, the decoy home the registry proposal
  §D flagged. The directory no longer exists. The unit has failed every
  morning since the home moved. Its output fed the claude-science lane,
  which the July handoffs already marked blocked.
- **repo-fleet-sweep.timer, journal-watcher.service.** Wanted at boot;
  unit files absent. Systemd logs a not-found on every boot.

## The act

Operator's terminal, in this order. Stop first so nothing writes during
the disable; disable removes the wants links; the `rm` lines clear unit
files that can never start. `daemon-reload` last.

```
systemctl --user stop sentinel-watchdog.timer sentinel-watchdog.service kb-snapshot-refresh.timer
systemctl --user disable sentinel-watchdog.timer kb-snapshot-refresh.timer
systemctl --user disable repo-fleet-sweep.timer journal-watcher.service 2>/dev/null
rm -f ~/.config/systemd/user/timers.target.wants/repo-fleet-sweep.timer ~/.config/systemd/user/default.target.wants/journal-watcher.service
cd ~/.config/systemd/user && mkdir -p retired-2026-09-02 && mv drop-server.service drop-ngrok.service grove-mcp.service grove-ngrok.service newt-willow.service nest-watcher.service orin-worker.service willow-grove-listen.service stuck-loop-watch.service stuck-loop-watch.timer hook-wiring-audit.service hook-wiring-audit.timer willow-metabolic.service willow-upstream-desk.service willow-upstream-desk.timer willow-w8-census.service willow-w8-census.timer willow-wce.service willow-wce.timer kart-worker.service kart-worker-batch.service sentinel-watchdog.service sentinel-watchdog.timer kb-snapshot-refresh.service kb-snapshot-refresh.timer retired-2026-09-02/
systemctl --user daemon-reload
systemctl --user list-units --type=service,timer --all --no-pager | grep -E 'willow|kart|grove|nest|sentinel|kb-snap|repo-fleet|journal'
```

Moving rather than deleting keeps the record on disk. `~/.willow/fleet-dispatch/`
and its log are left in place; archiving that directory is a separate
decision once the log has been read for anything worth keeping.

## Nestor

No unit runs Nestor and nothing Nestor-shaped writes on a timer. Two
servers are spawned on demand by the IDE: the fleet Nestor over the sealed
decision store, and this repo's `nestor-grove-session` running offline and
read-only against `nestor/grove-session.db`. Not part of this cull. The
open question it leaves for the local-inference proposal: which of the two
carries the Ollama engine, and whether the grove-session one should exist
at all now that the seat's memory marks it as a different server.

## After

The current generation's unit set becomes the manifest: serve, two workers,
gpg-unlock, downloads-watcher. `doctor` should compare the live unit list
against that manifest and report any fleet-shaped unit outside it. That is
the check gap `abaf0d0d9c75` asks for, and it is what would have caught the
two old timers before they ran for three weeks against missing trees.

*ΔΣ=42*
