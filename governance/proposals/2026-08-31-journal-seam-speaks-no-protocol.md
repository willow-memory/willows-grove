# Proposal — the C11 journal seam speaks a protocol willow-mcp has never served

**Status:** proposal · drafted by heimdallr 2026-08-31 · **awaiting root's ratification**
**Amends (with a corrected premise):** gap `GAP-007` · issue #16
**Target:** `grove/journal_writer.py`, `grove/journal_reader.py`, `tests/e2e_willow_mcp/`, `.willow/mcp_apps/`
**Companions:** [`2026-08-22-governed-path-write-gate.md`](2026-08-22-governed-path-write-gate.md)

---

## The gap as recorded, and what is actually true

`GAP-007` says the **read** half of the C11 seam depends on `kb_journal_read`,
which does not exist upstream. That is true, carefully found, and enumerated so
it retires itself — `_PENDING_UPSTREAM` fails in both directions, which is the
right shape for an allowance.

It then draws a line:

> *"The write half is genuinely wired: `kb_journal` exists and Grove's writer
> was driven through it to a live Postgres row."*

**That sentence is true of one path and is read as true of the seam.** It
describes path (a), the in-process import. It does not describe path (b), the
HTTP fallback — and path (b) is the path CI exercises, the path the CHANGELOG
names, and the only path a deployed Grove can take.

The read half is missing a **verb**. Both halves are missing the **transport**.

## willow-mcp serves one HTTP endpoint, and it is not this one

`grove/journal_writer.py:120` builds `POST {WILLOW_MCP_URL}/tools/kb_journal`.
`grove/journal_reader.py:225` builds `GET {WILLOW_MCP_URL}/tools/kb_journal_read?…`.

willow-mcp's entire serve-mode HTTP surface is one line — `server.py:8474`:

```python
mcp.run(transport="streamable-http", host=_HOST, port=_PORT)
```

MCP Streamable HTTP is a **single JSON-RPC 2.0 endpoint**, mounted by the SDK at
`streamable_http_path: str = "/mcp"` (`mcp/server/mcpserver/server.py:1060`,
SDK 2.0.0). It has no per-tool REST routes and cannot grow them — a tool is
reached by a `tools/call` method in the request body, not by a path segment.

The only custom HTTP routes willow-mcp declares anywhere are five OAuth
callbacks (`oauth.py:531-631`) and `gates_serve.py`, which is a different app on
a different port.

So `/tools/kb_journal` is not a fallback waiting on Gate 5. **It 404s on the
first byte and always has.** `_try_http_write` catches `HTTPError`, returns
`None`, and the caller raises `Unreachable` — the dead route fails into a state
indistinguishable from an honest D7 degradation, which is why nothing ever
reported it.

## Three independent failures, stacked

The write half — the half recorded as wired — has no working path in any
supported configuration:

| # | layer | what happens | evidence |
|---|---|---|---|
| 1 | **transport** | path (b) targets a route that does not exist | `server.py:8474`; no `/tools/*` route in willow-mcp |
| 2 | **packaging** | path (a) needs `import willow_mcp`; Grove's venv raises `ModuleNotFoundError` | not in `requirements.txt`, not in `pyproject.toml` dependencies |
| 3 | **seat** | both modules write as `_APP_ID = "willow-grove"`; `kb_journal` is `@_guarded`, and `gate.permitted()` is fail-closed | `journal_writer.py:42`; `gate.py:840-842`; no `willow-grove` in `.willow/mcp_apps/` |

Any one of these is sufficient. All three hold today.

The third has a sharp edge worth naming: **`kb_journal` is in heimdallr's own
`deny_tools`.** Grove does not hit that denial only because it writes as an
`app_id` that is well-formed and unmanifested, which `gate.py` denies for a
different reason. "Which seat writes the journal" is currently answered by
nothing.

## The belief is written down, which is why it survived

`requirements.txt:17-18`, justifying the `mcp` floor:

> *"Grove and willow-mcp speak the same protocol to each other, so they should
> not be able to drift apart."*

They do not speak the same protocol to each other. Grove speaks REST-over-HTTP
at a path of its own invention; willow-mcp speaks MCP. The pin defends against a
drift between two implementations of one protocol, in a seam that has two
protocols and one implementation.

And `mock_willow_mcp.py:12` states its routes *"mirror willow-mcp's tool
routes."* There are no tool routes to mirror. That is INVARIANTS §6 — *the
manifest describes code, not aspirations* — inside a test double, where it is
hardest to see and does the most damage: the suite proves Grove correctly speaks
a protocol nothing serves, in **both** directions.

## The client already exists. Twice.

Nothing needs inventing, and no dependency needs adding:

- **`grove/nestor_client.py`** — Grove's own MCP-over-stdio client. Long-lived
  child process, mutex-serialized, in production against `nestor serve`, and
  already carrying the three-state discipline. It does this exact job for a
  different server.
- **`willow-mcp/src/willow_mcp/mcp_federation_client.py:41`** — the SDK client:
  `stdio_client` and `streamable_http_client`, with `HTTP_TRANSPORTS` at
  `mcp_federation.py:172`. willow-mcp already knows how to be an MCP client to
  another MCP server, over both transports.

Which reframes what this seam is. **Grove writing to willow-mcp is federation** —
and there is already a `_federation` seat sitting in `.willow/mcp_apps/`.

## Proposed change

Four items, in dependency order. Only the first changes behaviour.

**1. Delete paths (a) and (b); speak MCP.** One client — stdio, or
streamable-http against `/mcp` — modeled on `nestor_client.py` or lifted from
`mcp_federation_client.py`. Three degradation branches collapse into one real
one, and `Unreachable` starts meaning *unreachable* instead of *misaddressed*.

**2. Materialize a seat.** Either a `willow-grove` manifest permitting
`kb_journal`, or a decision that Grove writes as an existing seat — which
requires amending heimdallr's `deny_tools`, and is therefore a governance act,
not a config edit. Right now the answer is neither, and the fail-closed gate is
the only thing that has been correct about this seam.

**3. Correct the record.** `GAP-007`, the CHANGELOG entry, the conftest
docstring, and `requirements.txt:17-18` all state the write half is wired.
`_PENDING_UPSTREAM` should pin the **transport**, not only the missing verb, so
it retires on the thing that is actually blocking.

**4. Then `kb_journal_read` upstream.** This is the only part that was ever
genuinely blocked on Gate 5.

## What this does not fix, and what it does not claim

**It does not claim the write half never worked.** `kb_journal` exists
(`server.py:2663`) and someone plainly drove Grove's writer through it into a
live Postgres row. In a process where `willow_mcp` was importable — a developer
box with both trees on `PYTHONPATH` — path (a) works, and that is what was
witnessed. The defect is that **no supported install produces that process**,
and the fallback built for every other process was never real.

**It does not change the three-state contract**, and it does not widen a bind.
This is entirely inside the seam; `:8766` stays on loopback and D4 stays sealed.

**It does not resolve Gate 5.** After all four items, the read half still has no
verb upstream. What changes is that its absence becomes the *only* thing
missing, instead of the only thing visible.

**Left undecided:** whether the resident watcher, when it lands, writes through
this same client or in-process as a willow-mcp component. That choice decides
whether Grove is a federation peer or a co-resident, and it should be made
deliberately rather than inherited from whichever lands first.

---

*Measured, not recalled: the serve-mode transport by reading `server.py:8474`
and the SDK's `streamable_http_path` default; the absent routes by enumerating
every `custom_route` and `Route` in `willow-mcp/src`; the import failure by
running `./.venv/bin/python3 -c "import willow_mcp"` in this repo; the missing
seat by `ls .willow/mcp_apps/`; the gate's fail-closed default by reading
`gate.py:825-842`. `kb_journal_read` appears zero times in `willow-mcp/src`,
confirming GAP-007's finding unchanged.*
