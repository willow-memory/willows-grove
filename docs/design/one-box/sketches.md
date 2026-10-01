# One-box sketches: code that runs, and configs that don't yet

These are the working sketches behind [`README.md`](README.md). They aren't a
package and aren't wired into anything. They exist so the next session starts
from code that has been shown to behave, not from prose.

**Two kinds of sketch:**
- **§1 and §2 were tested.** They passed on 2026-10-01 under Python 3.11.15
  with msgspec 0.22.0 and pytest: **10 passed**.
- **§3 onward are untested configs.** Each is marked with what has to be
  checked on the operator's box.

**To run §1 and §2:** copy the two blocks to `onebox.py` and
`test_onebox.py` in an empty directory, outside any git tree, then run
`pip install msgspec pytest` and `python -m pytest -q`.

**What the tests pin, all on Linux:**
- **Socket permissions and peers.** The socket is mode 0660. The kernel's
  `SO_PEERCRED` uid is checked on every accept, and a peer whose uid isn't
  allowed is **refused by name**.
- **Bad requests.** An unknown op, and a request over the cap, each come back
  as `bad_request`.
- **The gate fails closed and loud.** With Rat down (`unreachable`) or slow
  (`timeout`), the gate's answer is `block` with `loud=True`, never allow.
- **The first D0 class works through the real socket.** A done-claim with no
  tool call is blocked; the same claim with tool calls passes.
- **One result renders per front end.** The same `DoorResult` comes out as
  Claude Code / Codex / Qwen `decision:block`, Gemini `deny`, Cursor
  `followup_message`, and `unenforced` for a front end with no blocking OUT
  door.
- **The grant challenge binds the exact bytes leaving.** It doesn't depend on
  key order, and any byte change, or a new nonce, changes it.
- **The Nestor walk.** It follows edges in both directions, reports each
  pair's own state, stops at cycles (`UNION`), and never pulls in an
  unlinked pair.

**Known simplifications, to fix in the real build:**
- `serve()` is threaded and synchronous. The real Rat should use `asyncio`.
- `DONE_WORDS` is a placeholder for the D0 rule set.
- The real neighborhood query must also filter `superseded_by = ''`, and
  return each edge's `edge_sig` (sealed vs proposed) and `kind`. The columns
  match Nestor's `sqlite_store.py` (`tm_pairs`, `decision_edges`).
- An adapter's `parse_*` half can be replaced by polyhook (MIT); see
  `research-2026-10-01.md` §1.

---

## 1. `onebox.py`: socket standard, door contract, adapters, D0, grant challenge, neighborhood

```python
"""One-box sketches: socket standard, door contract, adapters, fail-closed gate,
grant challenge, Nestor neighborhood. Sketch code, tested in isolation; not a
package. Stdlib only, plus msgspec for the typed contract."""

from __future__ import annotations

import hashlib
import json
import os
import socket
import sqlite3
import struct
import threading
from typing import Callable, Literal, Optional

import msgspec

# ---------------------------------------------------------------- socket standard

MAX_LINE = 64 * 1024  # request and reply cap, in bytes


class SockError(Exception):
    """Client-side failure, named by state. Never an empty reply."""

    def __init__(self, state: str, reason: str):
        super().__init__(f"{state}: {reason}")
        self.state = state  # unreachable | refused | timeout | bad_reply
        self.reason = reason


def peer_cred(conn: socket.socket) -> tuple[int, int, int]:
    """(pid, uid, gid) of the connected peer, from the kernel (Linux)."""
    raw = conn.getsockopt(socket.SOL_SOCKET, socket.SO_PEERCRED, struct.calcsize("3i"))
    return struct.unpack("3i", raw)


def listen_fds() -> list[socket.socket]:
    """systemd socket activation (sd_listen_fds(3)), without libsystemd."""
    if os.environ.get("LISTEN_PID") != str(os.getpid()):
        return []
    n = int(os.environ.get("LISTEN_FDS", "0"))
    return [socket.socket(fileno=3 + i) for i in range(n)]


Op = Callable[[dict, tuple[int, int, int]], dict]


def serve(path: str, ops: dict[str, Op], allowed_uids: set[int],
          stop: Optional[threading.Event] = None) -> None:
    """One JSON line in, one JSON line out, one request per connection.
    The peer's uid is checked on every accept; a disallowed peer is refused
    by name, never served."""
    activated = listen_fds()
    if activated:
        srv = activated[0]
    else:
        if os.path.exists(path):
            os.unlink(path)
        srv = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        srv.bind(path)
        os.chmod(path, 0o660)
        srv.listen(16)
    srv.settimeout(0.2)
    while not (stop and stop.is_set()):
        try:
            conn, _ = srv.accept()
        except socket.timeout:
            continue
        threading.Thread(target=_handle, args=(conn, ops, allowed_uids), daemon=True).start()
    srv.close()


def _reply(conn: socket.socket, obj: dict) -> None:
    conn.sendall(json.dumps(obj).encode() + b"\n")


def _handle(conn: socket.socket, ops: dict[str, Op], allowed_uids: set[int]) -> None:
    with conn:
        cred = peer_cred(conn)
        if cred[1] not in allowed_uids:
            _reply(conn, {"ok": False, "state": "refused", "reason": f"peer uid {cred[1]} not allowed"})
            return
        buf = b""
        while b"\n" not in buf:
            chunk = conn.recv(4096)
            if not chunk:
                break
            buf += chunk
            if len(buf) > MAX_LINE:
                _reply(conn, {"ok": False, "state": "bad_request", "reason": "request over cap"})
                return
        try:
            req = json.loads(buf.split(b"\n", 1)[0])
            op = ops[req["op"]]
        except (ValueError, KeyError, TypeError) as exc:
            _reply(conn, {"ok": False, "state": "bad_request", "reason": type(exc).__name__})
            return
        try:
            _reply(conn, {"ok": True, **op(req, cred)})
        except Exception as exc:  # an op failure is a named state, not a crash
            _reply(conn, {"ok": False, "state": "op_failed", "reason": f"{type(exc).__name__}: {exc}"})


def call(path: str, req: dict, timeout_s: float = 8.0) -> dict:
    """The ~15-line client a shim vendors. Raises SockError by state."""
    try:
        s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        s.settimeout(timeout_s)
        s.connect(path)
    except (FileNotFoundError, ConnectionRefusedError) as exc:
        raise SockError("unreachable", type(exc).__name__)
    with s:
        try:
            s.sendall(json.dumps(req).encode() + b"\n")
            buf = b""
            while b"\n" not in buf:
                chunk = s.recv(4096)
                if not chunk:
                    break
                buf += chunk
                if len(buf) > MAX_LINE:
                    raise SockError("bad_reply", "reply over cap")
        except socket.timeout:
            raise SockError("timeout", f">{timeout_s}s")
    try:
        reply = json.loads(buf.split(b"\n", 1)[0])
    except ValueError:
        raise SockError("bad_reply", "not JSON")
    if not reply.get("ok"):
        raise SockError(reply.get("state", "refused"), reply.get("reason", ""))
    return reply


# ---------------------------------------------------------------- door contract

Door = Literal["in", "out", "end"]


class DoorRequest(msgspec.Struct, kw_only=True):
    """Vendor-free. Rat never sees a vendor's hook payload."""
    v: int = 1
    door: Door
    front_end: str                 # "claude-code" | "codex" | "gemini-cli" | "ratatosk-repl" | ...
    session_id: str
    human_present: bool            # the willow seat is wherever the human is
    prompt: str = ""               # IN
    last_turn: str = ""            # OUT
    tool_calls_this_turn: int = 0  # OUT evidence
    transcript_ref: str = ""       # END


class DoorResult(msgspec.Struct, kw_only=True):
    v: int = 1
    decision: Literal["allow", "block"]
    reason: str = ""
    inject: str = ""
    status: str = ""               # resolved | escalate | needs_egress | refused | unreachable | ...
    loud: bool = False             # true: also raise to the willow seat / #alerts


def gate(path: str, req: DoorRequest, timeout_s: float = 8.0) -> DoorResult:
    """Every gate fails closed, and loud. If Rat cannot answer, the answer is
    block, with the failure named."""
    try:
        reply = call(path, {"op": req.door, "req": msgspec.to_builtins(req)}, timeout_s)
        return msgspec.convert(reply["result"], DoorResult)
    except SockError as exc:
        return DoorResult(decision="block", status=exc.state, loud=True,
                          reason=f"Rat {exc.state}: {exc.reason} (gate fails closed)")
    except (KeyError, msgspec.ValidationError) as exc:
        return DoorResult(decision="block", status="bad_reply", loud=True,
                          reason=f"Rat bad reply: {exc} (gate fails closed)")


# ---------------------------------------------------------------- adapters
# An adapter translates; it holds no logic. One per front end. polyhook
# (MIT) can replace the parse half; ACP-speaking editors go through a proxy.

def parse_stop(front_end: str, payload: dict, human_present: bool) -> DoorRequest:
    return DoorRequest(
        door="out", front_end=front_end, human_present=human_present,
        session_id=str(payload.get("session_id") or payload.get("conversation_id") or ""),
        last_turn=str(payload.get("last_assistant_message") or payload.get("prompt_response") or ""),
        tool_calls_this_turn=int(payload.get("tool_calls_this_turn", 0)),
    )


def render_stop(front_end: str, result: DoorResult) -> tuple[str, int]:
    """(stdout, exit code) in the front end's dialect. One document, one channel."""
    if result.decision == "allow":
        return "", 0
    if front_end in ("claude-code", "codex", "qwen-code"):
        return json.dumps({"decision": "block", "reason": result.reason}), 0
    if front_end == "gemini-cli":  # AfterAgent: deny forces a retry with the reason
        return json.dumps({"decision": "deny", "reason": result.reason}), 0
    if front_end == "cursor":      # stop: followup_message becomes the next user turn
        return json.dumps({"followup_message": result.reason}), 0
    # A front end with no blocking OUT door: unenforced, still loud.
    return json.dumps({"unenforced": True, "reason": result.reason}), 0


# ---------------------------------------------------------------- D0: claim vs evidence

DONE_WORDS = ("done", "fixed", "pushed", "merged", "all tests pass", "handoff written", "complete")


def d0_out(req: DoorRequest) -> DoorResult:
    """The first D0 class for the OUT door: a turn that claims done with no
    tool call behind it is blocked once. Everything else is allowed."""
    claims = any(w in req.last_turn.lower() for w in DONE_WORDS)
    if claims and req.tool_calls_this_turn == 0:
        return DoorResult(decision="block", status="claim_without_evidence",
                          reason="This turn claims completion with no tool call behind it. Show the evidence or withdraw the claim.")
    return DoorResult(decision="allow", status="resolved")


# ---------------------------------------------------------------- egress grant challenge

def grant_challenge(grant: dict, nonce: bytes) -> bytes:
    """WebAuthn challenge = SHA-256(canonical outbound grant + nonce). The
    passkey assertion then covers exactly these bytes leaving the box."""
    canonical = json.dumps(grant, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(canonical + nonce).digest()


# ---------------------------------------------------------------- Nestor neighborhood

NEIGHBORHOOD_SQL = """
WITH RECURSIVE walk(id, depth) AS (
  SELECT :start, 0
  UNION
  SELECT CASE WHEN e.src_id = w.id THEN e.dst_id ELSE e.src_id END, w.depth + 1
  FROM walk w JOIN decision_edges e ON e.src_id = w.id OR e.dst_id = w.id
  WHERE w.depth < :hops
)
SELECT p.id, p.status, MIN(w.depth) AS depth
FROM walk w JOIN tm_pairs p ON p.id = w.id
GROUP BY p.id ORDER BY depth, p.id
"""


def neighborhood(db: sqlite3.Connection, start: str, hops: int = 2) -> list[tuple]:
    """Pair, edges, and linked pairs with their own state: by edge only,
    never by similarity. UNION (not UNION ALL) stops cycles."""
    return db.execute(NEIGHBORHOOD_SQL, {"start": start, "hops": hops}).fetchall()
```

## 2. `test_onebox.py`

```python
import json
import os
import socket
import sqlite3
import tempfile
import threading
import time

import onebox as ob


def _start(ops, allowed):
    d = tempfile.mkdtemp()
    path = os.path.join(d, "rat.sock")
    stop = threading.Event()
    t = threading.Thread(target=ob.serve, args=(path, ops, allowed, stop), daemon=True)
    t.start()
    for _ in range(50):
        if os.path.exists(path):
            break
        time.sleep(0.02)
    return path, stop


def _rat_ops():
    def out(req, cred):
        r = ob.d0_out(ob.msgspec.convert(req["req"], ob.DoorRequest))
        return {"result": ob.msgspec.to_builtins(r)}
    return {"out": out, "health": lambda req, cred: {"peer_uid": cred[1]}}


def test_socket_mode_and_peer_uid():
    path, stop = _start(_rat_ops(), {os.getuid()})
    assert oct(os.stat(path).st_mode & 0o777) == "0o660"
    assert ob.call(path, {"op": "health"})["peer_uid"] == os.getuid()
    stop.set()


def test_disallowed_peer_is_refused_by_name():
    path, stop = _start(_rat_ops(), {os.getuid() + 12345})
    try:
        ob.call(path, {"op": "health"})
        assert False
    except ob.SockError as e:
        assert e.state == "refused" and "not allowed" in e.reason
    stop.set()


def test_unknown_op_and_oversize_are_bad_request():
    path, stop = _start(_rat_ops(), {os.getuid()})
    for req in ({"op": "nope"}, {"op": "health", "pad": "x" * (ob.MAX_LINE + 10)}):
        try:
            ob.call(path, req)
            assert False
        except ob.SockError as e:
            assert e.state == "bad_request"
    stop.set()


def test_gate_fails_closed_and_loud_when_rat_is_down():
    req = ob.DoorRequest(door="out", front_end="codex", session_id="s", human_present=True,
                         last_turn="All done.")
    r = ob.gate("/nonexistent/rat.sock", req)
    assert r.decision == "block" and r.loud and r.status == "unreachable"


def test_gate_fails_closed_on_timeout():
    d = tempfile.mkdtemp()
    path = os.path.join(d, "slow.sock")
    srv = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    srv.bind(path)
    srv.listen(1)  # accepts, never replies
    req = ob.DoorRequest(door="out", front_end="claude-code", session_id="s", human_present=True)
    r = ob.gate(path, req, timeout_s=0.3)
    assert r.decision == "block" and r.status == "timeout" and r.loud
    srv.close()


def test_claim_without_evidence_blocks_through_the_real_socket():
    path, stop = _start(_rat_ops(), {os.getuid()})
    claim = ob.DoorRequest(door="out", front_end="gemini-cli", session_id="s", human_present=True,
                           last_turn="Fixed and pushed.", tool_calls_this_turn=0)
    honest = ob.DoorRequest(door="out", front_end="gemini-cli", session_id="s", human_present=True,
                            last_turn="Fixed and pushed.", tool_calls_this_turn=3)
    assert ob.gate(path, claim).decision == "block"
    assert ob.gate(path, honest).decision == "allow"
    stop.set()


def test_same_result_renders_per_front_end():
    r = ob.DoorResult(decision="block", reason="why")
    assert json.loads(ob.render_stop("claude-code", r)[0]) == {"decision": "block", "reason": "why"}
    assert json.loads(ob.render_stop("gemini-cli", r)[0])["decision"] == "deny"
    assert json.loads(ob.render_stop("cursor", r)[0]) == {"followup_message": "why"}
    assert json.loads(ob.render_stop("windsurf", r)[0])["unenforced"] is True
    assert ob.render_stop("codex", ob.DoorResult(decision="allow")) == ("", 0)


def test_parse_is_vendor_tolerant():
    a = ob.parse_stop("claude-code", {"session_id": "x", "last_assistant_message": "hi"}, True)
    b = ob.parse_stop("cursor", {"conversation_id": "x"}, False)
    assert a.session_id == b.session_id == "x" and a.human_present and not b.human_present


def test_grant_challenge_binds_exact_outbound_bytes():
    g = {"host": "search.example", "payload": "q=apple crate", "scope": "once"}
    n = b"\x01" * 16
    assert ob.grant_challenge(g, n) == ob.grant_challenge(dict(reversed(list(g.items()))), n)
    assert ob.grant_challenge(g, n) != ob.grant_challenge({**g, "payload": "q=apple crates"}, n)
    assert ob.grant_challenge(g, n) != ob.grant_challenge(g, b"\x02" * 16)


def test_neighborhood_walks_edges_with_states_and_stops_cycles():
    db = sqlite3.connect(":memory:")
    db.executescript("""
      CREATE TABLE tm_pairs(id TEXT PRIMARY KEY, status TEXT);
      CREATE TABLE decision_edges(src_id TEXT, dst_id TEXT, kind TEXT);
      INSERT INTO tm_pairs VALUES ('a','sealed'),('b','draft'),('c','sealed'),('d','draft'),('z','sealed');
      INSERT INTO decision_edges VALUES ('a','b','refines'),('b','c','depends_on'),
                                        ('c','a','contradicts'),('c','d','supersedes');
    """)
    got = ob.neighborhood(db, "a", hops=2)
    assert got == [("a", "sealed", 0), ("b", "draft", 1), ("c", "sealed", 1), ("d", "draft", 2)]
    assert ("z", "sealed", 1) not in got  # unlinked: never pulled in by similarity
```

---

## 3. A front-end shim: what each CLI's hook command runs (untested)

The same file serves every front end; only `FRONT_END` differs, and the
adapter is the only vendor-aware part. Verify each front end's payload
fields against `research-2026-10-01.md` §1 before trusting the parse.

```python
#!/usr/bin/env python3
"""Thin OUT-door shim: one call, one rendered reply. No logic lives here."""
import json, os, sys
from onebox import gate, parse_stop, render_stop   # vendored client + adapter

FRONT_END = os.environ.get("ONEBOX_FRONT_END", "claude-code")
SOCK = os.environ.get("RAT_SOCK", f"/run/user/{os.getuid()}/ratatosk/rat.sock")
# Seat by presence: an interactive session with a person in it is willow;
# headless / woken / dispatched runs are not.
HUMAN = os.environ.get("ONEBOX_HEADLESS") != "1"   # placeholder; see below

payload = json.load(sys.stdin) if not sys.stdin.isatty() else {}
result = gate(SOCK, parse_stop(FRONT_END, payload, HUMAN))   # fails closed, loud
out, rc = render_stop(FRONT_END, result)
if out:
    print(out)
if result.loud:
    print(f"onebox: {result.reason}", file=sys.stderr)   # also raised to #alerts by Rat
sys.exit(rc)
```

`HUMAN` above is a placeholder. Each front end signals interactivity
differently, so presence detection belongs in the capability table, not in
code.

## 4. Capability table: one row per front end (data, untested)

```json
{
  "claude-code":   {"in": "block+inject", "out": "block", "end": "notify:1.5s", "egress": "vendor (ungated)"},
  "codex":         {"in": "block+inject", "out": "block", "end": "notify:1-3s", "egress": "vendor (ungated)"},
  "gemini-cli":    {"in": "block+inject", "out": "deny-retry", "end": "notify", "egress": "vendor (ungated)"},
  "qwen-code":     {"in": "block+inject", "out": "block (cap 8)", "end": "notify", "egress": "vendor (ungated)"},
  "cursor":        {"in": "block", "out": "followup_message", "end": "?", "egress": "vendor (ungated)"},
  "windsurf":      {"in": "block", "out": "unenforced", "end": "?", "egress": "vendor (ungated)"},
  "ratatosk-repl": {"in": "to build", "out": "to build", "end": "notify", "egress": "none on local models"}
}
```

## 5. systemd: socket-activated Rat (untested)

```ini
# ~/.config/systemd/user/ratatosk.socket
[Socket]
ListenStream=%t/ratatosk/rat.sock
SocketMode=0660
DirectoryMode=0750

[Install]
WantedBy=sockets.target

# ~/.config/systemd/user/ratatosk.service
[Service]
ExecStart=%h/.local/bin/ratatosk serve
# listen_fds() in onebox.py picks up the passed socket (fd 3)
```

## 6. The browser front door: Caddy to UDS backends (untested)

There is one loopback listener, and it is the only browser-facing port. It
binds `localhost`, because WebAuthn refuses an IP as the RP ID. Every mutation
behind it is passkey-signed, so the port itself carries no authority.

```caddyfile
http://localhost:8766 {
    handle_path /grove/*  { reverse_proxy unix//run/user/1000/grove/page.sock }
    handle_path /nestor/* { reverse_proxy unix//run/user/1000/nestor/ui.sock }
    handle_path /grants/* { reverse_proxy unix//run/user/1000/ratatosk/grants.sock }
}
```

Verify the Host header each backend expects. The MCP SDK checks
`allowed_hosts`.

## 7. Opt-in remote ingress: frp to a UDS (untested, D10)

frp runs only when the operator opens the remote door. The server is one the
operator rents and controls. There is no tunnel by default, and willow-bot
polls GitHub.

```toml
# frpc.toml on the box
serverAddr = "frp.example.org"     # the operator's own server
serverPort = 7000

[[proxies]]
name = "grove-mcp"
type = "https"
customDomains = ["mcp.example.org"]
[proxies.plugin]
type = "unix_domain_socket"
unixPath = "/run/user/1000/grove/mcp.sock"
```

## 8. The grant click: WebAuthn flow (untested)

1. Rat queues a `needs_egress` card in `forge.human_loop`. The card holds the
   host, the literal outbound payload, its size, and the precedent Yeses and
   Nos.
2. The page computes nothing. The server sends
   `challenge = grant_challenge(card, nonce)` (§1) and the one stored
   credential id.
3. The browser calls `navigator.credentials.get({publicKey: {challenge,
   allowCredentials, userVerification: "required"}})`. That needs a touch or
   PIN on the operator's authenticator.
4. The server verifies with `webauthn.verify_authentication_response(...,
   expected_challenge=challenge, require_user_verification=True)`, then hands
   the grant to the signer process (`net_authority`, a separate uid). The
   signer writes the lease, and FRANK records it.
5. Any failure at any step means **no grant**: closed, and loud.

ΔΣ=42
