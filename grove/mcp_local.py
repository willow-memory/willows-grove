# grove/mcp_local.py — Grove MCP for Claude Code.
# b17: GRMLC  ΔΣ=42
"""
Modes:
  stdio (default):   python3 -m grove.mcp_local
                     .mcp.json: {"command": "python3", "args": ["-m", "grove.mcp_local"]}

  serve (push):      python3 -m grove.mcp_local --serve  [--port 8767] [--watch]
                     Runs as a persistent streamable-HTTP server with OAuth.
                     Set GROVE_MCP_URL to the public base URL (e.g. ngrok tunnel).
                     .mcp.json: {"url": "https://<tunnel>/mcp"}
                     Postgres LISTEN/NOTIFY → send_resource_updated pushed to all subscribers.
                     --watch: supervise a **child** serve process; restart it when
                     `grove/*.py` changes (parent polls mtimes — works because `mcp.run` blocks).

Auth in serve mode: OAuth 2.0 + PKCE. Per INVARIANTS.md §7, /authorize
                    always redirects to the /grove-approve page — no code is
                    ever issued without a human loopback click. Dynamic client
                    registration is DISABLED by default (an operator opts in
                    via GROVE_MCP_ALLOW_DYNAMIC_REGISTRATION=1); otherwise
                    only pre-enrolled clients can authorize. Access tokens
                    last 24 hours (mcp_auth._ACCESS_TTL).
Auth in stdio mode: implicit (local process, trusted user) — no OAuth.

Tunnel deployment (production): setting GROVE_MCP_URL to a non-loopback
address without also setting WILLOW_MCP_TUNNEL_ACKNOWLEDGED=1 logs a
prominent WARNING at startup — the operator has to say out loud that the
listener is intentionally reachable. DNS-rebinding protection is ON in
every configuration (see _transport_security); the ngrok-era https carve-out
is gone. INVARIANTS.md §7.

Reverse-proxy loopback: a same-box reverse proxy (Pangolin, nginx,
cloudflared, tailscale) forwards traffic to 127.0.0.1:<port>, so the raw
TCP peer of the /grove-approve POST is loopback for every off-box POST
that reaches the app that way. The operator opts in to X-Forwarded-For
consultation via GROVE_MCP_TRUSTED_PROXIES=<comma,ips>; default-closed
(unset → prior behavior). INVARIANTS.md §7.
"""
import functools
import os
import select
import socket
import sys
import threading
import asyncio
from contextlib import asynccontextmanager
from pathlib import Path
from typing import AsyncIterator
from urllib.parse import urlparse

# Ensure the grove repo root (parent of this file's package) is on sys.path
# so that `import u2u` resolves regardless of how the server is launched.
_GROVE_ROOT = Path(__file__).parent.parent
if str(_GROVE_ROOT) not in sys.path:
    sys.path.insert(0, str(_GROVE_ROOT))

from mcp.server.auth.middleware.auth_context import get_access_token
from mcp.server.mcpserver import MCPServer
from mcp.server.mcpserver.exceptions import ToolError
from mcp.server.subscriptions import InMemorySubscriptionBus
from mcp.shared.subscriptions import ResourceUpdated

import grove_db as db
import grove_reader as _grove_reader

# ── Notification state ─────────────────────────────────────────────
# SEP-2575 removed the standing GET stream and `subscribe_resource`. A client
# now opts in with `subscriptions/listen`, whose RESPONSE is the stream, and
# MCPServer registers the handler for it automatically. Fan-out is the bus's
# job, so the per-session queue registry this used to keep — a dict of
# asyncio.Queues keyed by channel id, plus a lock, plus a watcher task per
# subscription — is deleted rather than ported. We publish; the SDK delivers.
_bus = InMemorySubscriptionBus()
_main_loop: asyncio.AbstractEventLoop | None = None


def _pg_notify_thread() -> None:
    """Dedicated Postgres LISTEN thread. Broadcasts to subscriber queues on NOTIFY."""
    import psycopg2

    dsn = os.getenv("WILLOW_DB_URL", "")
    if not dsn:
        pg_db   = os.getenv("WILLOW_PG_DB", "willow_20")
        pg_user = os.getenv("WILLOW_PG_USER", os.environ.get("USER", ""))
        dsn = f"dbname={pg_db} user={pg_user}"

    while True:
        try:
            conn = psycopg2.connect(dsn)
            conn.autocommit = True
            cur = conn.cursor()
            cur.execute("SET search_path = grove, public")
            cur.execute("LISTEN grove_channel")

            while True:
                ready = select.select([conn], [], [], 5.0)
                if not ready[0]:
                    continue
                conn.poll()
                while conn.notifies:
                    n = conn.notifies.pop(0)
                    try:
                        channel_id = int(n.payload)
                    except ValueError:
                        continue
                    # `SubscriptionBus.publish` is a COROUTINE, and this is a
                    # plain thread — calling it here would build a coroutine
                    # nobody awaits, which does nothing and says nothing. It has
                    # to be marshalled onto the loop, same as the queue puts it
                    # replaced. No loop yet means no listener yet, so dropping
                    # the event is correct rather than merely tolerable.
                    name = _channel_name_for_id(channel_id)
                    if name and _main_loop:
                        asyncio.run_coroutine_threadsafe(
                            _bus.publish(ResourceUpdated(uri=f"grove://channel/{name}")),
                            _main_loop,
                        )
        except Exception:
            import time
            time.sleep(3)


@asynccontextmanager
async def _lifespan(server: MCPServer) -> AsyncIterator[None]:
    global _main_loop
    _main_loop = asyncio.get_running_loop()
    t = threading.Thread(target=_pg_notify_thread, daemon=True)
    t.start()
    yield


# 8767, not 8765: willow-mcp --serve also defaults to 8765 (its server.py),
# so the two MCP servers collided and only one could bind — a tunnel stood up
# in front of "the MCP port" fronted whichever won the race. The fleet port
# map is now explicit: 8765 willow-mcp MCP, 8766 the Grove desk page
# (loopback ONLY, never fronted — D4), 8767 Grove MCP.
_PORT = int(os.getenv("GROVE_MCP_PORT", "8767"))


def _detect_serve_mode(argv: list[str] | None = None) -> bool:
    """Whether the module was launched in serve mode.

    Separated from the module-level import so tests can substitute their own
    argv (or set `_SERVE_MODE` outright before importing derived surfaces).
    The current CLI convention — `--serve` in argv — is preserved. See
    tests/test_serve_mode_identity.py and INVARIANTS.md §7.
    """
    src = sys.argv if argv is None else argv
    return "--serve" in src


_SERVE_MODE = _detect_serve_mode()
_BASE_URL = os.getenv("GROVE_MCP_URL", f"http://127.0.0.1:{_PORT}")

_TRUTHY = {"1", "true", "yes", "on"}


def _env_flag(name: str, env: dict[str, str] | None = None) -> bool:
    """A truthy env var, defensively normalised. True on "1"/"true"/"yes"/"on"."""
    src = os.environ if env is None else env
    return src.get(name, "").strip().lower() in _TRUTHY


def _is_loopback_base_url(base_url: str) -> bool:
    """`base_url`'s host is one of the loopback names — 127.0.0.1, localhost, ::1.

    Used only for the tunnel-warning heuristic; the transport allowlist still
    does the authoritative check per request. See INVARIANTS.md §7.
    """
    try:
        host = urlparse(base_url).hostname
    except (ValueError, AttributeError):
        return False
    return host in ("127.0.0.1", "localhost", "::1")


def _csv_env(name: str) -> list[str]:
    """A comma-separated env var as a clean list (empty and blanks dropped)."""
    return [v.strip() for v in os.getenv(name, "").split(",") if v.strip()]


# Extra Host/Origin values to allowlist beyond loopback and the GROVE_MCP_URL
# netloc. Escape hatch for tunnels whose edge forwards a Host header that is
# neither loopback nor the exact public host in GROVE_MCP_URL — e.g. a Pangolin
# resource host, a reverse proxy's upstream name, or a second public alias. This
# is additive and explicit: an operator sets it deliberately, an attacker does
# not, so it never widens protection into the "off" state the DNS-rebinding
# guard exists to prevent. Format: comma-separated Host values (host or
# host:port) in GROVE_MCP_EXTRA_HOSTS, comma-separated scheme://host origins in
# GROVE_MCP_EXTRA_ORIGINS.
_EXTRA_HOSTS = _csv_env("GROVE_MCP_EXTRA_HOSTS")
_EXTRA_ORIGINS = _csv_env("GROVE_MCP_EXTRA_ORIGINS")


def _transport_security():
    """Host/Origin allowlist for the Streamable HTTP transport (G-REBIND-01).

    DNS-rebinding protection is ON in every deployment. It used to be turned OFF
    whenever `GROVE_MCP_URL` was https:// — i.e. exactly the tunnelled
    deployment this server is meant to run in — so the only thing gating access
    was knowledge of the tunnel URL, and a page in the operator's browser could
    reach the server cross-origin through a rebound name.

    The reason it was disabled is real: behind a tunnel the edge may forward
    `Host: 127.0.0.1:8767` (the origin address) OR the public hostname,
    depending on the tunnel. That is an argument for allowlisting BOTH, not for
    checking neither. Loopback stays on the list for the forwarded case; the
    tunnel host comes from the configured base URL, which the operator sets and
    an attacker does not.

    A malformed or hostless GROVE_MCP_URL adds nothing rather than falling back
    to permissive — an address that cannot be parsed is not a grant.
    """
    from mcp.server.transport_security import TransportSecuritySettings

    # The forwarded-origin case, and plain local runs.
    hosts = ["127.0.0.1:*", "localhost:*", "[::1]:*"]
    origins = ["http://127.0.0.1:*", "http://localhost:*", "http://[::1]:*"]

    parsed = urlparse(_BASE_URL)
    if parsed.scheme in ("http", "https") and parsed.netloc:
        # netloc keeps any explicit port, which is what the Host header carries.
        if parsed.netloc not in hosts:
            hosts.append(parsed.netloc)
        origin = f"{parsed.scheme}://{parsed.netloc}"
        if origin not in origins:
            origins.append(origin)

    # Operator-supplied extras for tunnels that forward some other Host/Origin
    # (Pangolin resource hosts, reverse-proxy upstream names, public aliases).
    for h in _EXTRA_HOSTS:
        if h not in hosts:
            hosts.append(h)
    for o in _EXTRA_ORIGINS:
        if o not in origins:
            origins.append(o)

    return TransportSecuritySettings(
        enable_dns_rebinding_protection=True,
        allowed_hosts=hosts,
        allowed_origins=origins,
    )


def _public_mcp_url() -> str:
    """RFC 9728 resource URL — must match the connector URL (…/mcp)."""
    base = _BASE_URL.rstrip("/")
    return base if base.endswith("/mcp") else f"{base}/mcp"


# ── Per-tool OAuth scopes (serve mode) ──────────────────────────────────
# Two granular scopes, plus `grove` kept as a back-compat superscope that
# implies both — so a 30-day token minted before this existed, or a client
# that still asks for plain `grove`, keeps full access rather than breaking.
# Defined at module level (not inside `if _SERVE_MODE:`) so both the stdio and
# serve import paths see the same constants — decorators below are applied to
# tool functions unconditionally, and just no-op under stdio.
SCOPE_READ  = "grove:read"
SCOPE_WRITE = "grove:write"
SCOPE_FULL  = "grove"

VALID_SCOPES   = [SCOPE_FULL, SCOPE_READ, SCOPE_WRITE]
DEFAULT_SCOPES = [SCOPE_READ, SCOPE_WRITE]   # a normal connect still gets full access
REQUIRED_SCOPES = [SCOPE_READ]               # the floor every token must clear


def _require_scope(required_scope: str) -> None:
    """Per-tool scope gate, enforced against the CURRENT request's token.

    Stdio mode never runs a Starlette request through the SDK's auth
    middleware, so `get_access_token()` is always None there — this is a
    no-op, preserving the existing implicit-trust posture for local Claude
    Code usage. In serve mode, `required_scopes=["grove:read"]` on the whole
    server already refuses an unauthenticated or scope-less request before it
    reaches any tool, so a live tool call always has a token in context;
    reaching this function with `token is None` would mean that gate was
    bypassed, and is treated as fail-closed rather than assumed benign.

    `GroveOAuthProvider.load_access_token` widens a `grove`-scoped token to
    also carry `grove:read`/`grove:write` literally (see mcp_auth._expand_scopes),
    so the plain `in` checks below already account for the superscope; the
    explicit `SCOPE_FULL in scopes` check is defense-in-depth, not the only path.
    """
    token = get_access_token()
    if token is None:
        return
    scopes = set(token.scopes or [])
    if required_scope in scopes or SCOPE_FULL in scopes:
        return
    raise ToolError(
        f"insufficient scope: '{required_scope}' required "
        f"(token scopes: {sorted(scopes) or ['(none)']})"
    )


def writes(fn):
    """Tool decorator: require `grove:write` before the wrapped tool runs.

    Place it directly on the function, under `@mcp.tool()`:

        @mcp.tool()
        @writes
        def grove_send_message(...): ...

    `functools.wraps` sets `__wrapped__`, and `Tool.from_function` builds the
    JSON schema via `inspect.signature(fn, eval_str=True)`, which follows
    `__wrapped__` by default — so `@mcp.tool()` still sees the original
    parameters and docstring, not `(*args, **kwargs)`. Verified in
    tests/test_tool_scopes.py rather than assumed.
    """
    @functools.wraps(fn)
    def _scope_checked(*args, **kwargs):
        _require_scope(SCOPE_WRITE)
        return fn(*args, **kwargs)

    return _scope_checked


_common_kwargs = dict(
    instructions=(
        "Grove sovereign workspace messaging. "
        "Send and read messages, search conversations, list channels."
    ),
    lifespan=_lifespan,
    subscriptions=_bus,
)

# Dynamic client registration is DISABLED by default (INVARIANTS.md §7).
# The pre-PR-6 posture was ClientRegistrationOptions(enabled=True) — the SDK
# would persist any `/register` payload as a legitimate client, so a stranger
# could register-and-then-authorize themselves the moment a person clicked
# Allow on that stranger's approval page. Off by default closes the
# "unvalidated register_client" hole from CODE_REVIEW.md §"safe-app-willow-grove"
# P0. An operator who genuinely wants dynamic registration (e.g. for
# claude.ai's connector discovery) opts in explicitly:
#     GROVE_MCP_ALLOW_DYNAMIC_REGISTRATION=1
# and takes on the responsibility of the approval click filtering strangers.
_ALLOW_DYNAMIC_REG = _env_flag("GROVE_MCP_ALLOW_DYNAMIC_REGISTRATION")


def _build_serve_provider(base_url: str):
    """Construct the OAuth provider for serve mode. Extracted so tests can
    substitute _SERVE_MODE and rebuild the provider without re-importing the
    module. See tests/test_serve_mode_identity.py.
    """
    from grove.mcp_auth import GroveOAuthProvider  # local import: serve-only dep
    return GroveOAuthProvider(
        token_path=Path.home() / ".willow" / "grove_mcp_token",
        base_url=base_url,
    )


# NOTE — Loki v0.9 audit finding #14 (PR 12): `_gate` and
# `_resolve_serve_identity` used to live here as a "serve-mode identity gate"
# seam. They had zero call sites — the actual per-request refusal in serve
# mode is done by `AuthSettings(required_scopes=REQUIRED_SCOPES)` in
# combination with `_require_scope` on every write tool, both wired through
# the SDK's auth middleware. Deleting the pretenders so the tree does not
# claim an enforcement point that isn't wired. INVARIANTS.md §7.


# ── Forwarded-refusal log-once (approval POST behind a trusted proxy) ────────
# Set by `_remote_is_loopback` when GROVE_MCP_TRUSTED_PROXIES is configured
# and an off-box X-Forwarded-For hop is refused. Log-once so a busy attacker
# does not flood stderr, but the operator still sees a signal the first time.
_forwarded_refusal_logged = False


def _log_forwarded_refusal_once(effective_host: str) -> None:
    global _forwarded_refusal_logged
    if _forwarded_refusal_logged:
        return
    _forwarded_refusal_logged = True
    print(
        f"[grove-mcp] WARNING: /grove-approve POST refused — X-Forwarded-For "
        f"reports non-loopback client ({effective_host}) through a trusted "
        "proxy (GROVE_MCP_TRUSTED_PROXIES). See INVARIANTS.md §7.",
        file=sys.stderr, flush=True,
    )


def _warn_public_tunnel_if_unacknowledged(base_url: str) -> bool:
    """Log a WARNING when the base URL is not loopback and the operator has
    not acknowledged the tunnel via WILLOW_MCP_TUNNEL_ACKNOWLEDGED=1.

    Returns True when a warning was emitted (used by tests). No `--allow-tunnel`
    flag exists — the warning is the security note. INVARIANTS.md §7.
    """
    if _is_loopback_base_url(base_url):
        return False
    if _env_flag("WILLOW_MCP_TUNNEL_ACKNOWLEDGED"):
        return False
    print(
        f"[grove-mcp] WARNING: GROVE_MCP_URL is a non-loopback address "
        f"({base_url}) — this listener is reachable off-box. DNS-rebinding "
        "protection stays on regardless, but the operator should set "
        "WILLOW_MCP_TUNNEL_ACKNOWLEDGED=1 to acknowledge that the tunnel is "
        "intended. See INVARIANTS.md §7.",
        file=sys.stderr, flush=True,
    )
    return True


if _SERVE_MODE:
    from grove.mcp_auth import effective_scopes
    from mcp.server.auth.settings import AuthSettings, ClientRegistrationOptions

    _auth_provider = _build_serve_provider(_BASE_URL)
    _warn_public_tunnel_if_unacknowledged(_BASE_URL)

    mcp = MCPServer(
        "grove",
        **_common_kwargs,
        auth_server_provider=_auth_provider,
        auth=AuthSettings(
            issuer_url=_BASE_URL.rstrip("/") + "/",
            resource_server_url=_public_mcp_url(),
            client_registration_options=ClientRegistrationOptions(
                enabled=_ALLOW_DYNAMIC_REG,
                valid_scopes=VALID_SCOPES,
                default_scopes=DEFAULT_SCOPES,
            ),
            required_scopes=REQUIRED_SCOPES,
        ),
    )
else:
    _auth_provider = None
    mcp = MCPServer("grove", **_common_kwargs)


@mcp.tool()
def grove_list_channels() -> list[dict]:
    """List all active Grove channels (name, type, description)."""
    conn = db.get_connection()
    try:
        rows = db.list_channels(conn)
        return [
            {"id": r["id"], "name": r["name"], "type": r["channel_type"],
             "description": r.get("description")}
            for r in rows
        ]
    finally:
        db.release_connection(conn)


@mcp.tool()
def grove_get_history(channel_name: str, limit: int = 50, since_id: int = 0) -> list[dict]:
    """
    Get message history from a Grove channel.

    Args:
        channel_name: Exact channel name (use grove_list_channels to find names).
        limit: Number of messages to return (max 200, default 50).
        since_id: If > 0, return only messages with id greater than this value,
                  oldest first. Use the last returned message's id as your next
                  since_id to poll for new messages without re-fetching history.
    """
    conn = db.get_connection()
    try:
        channels = db.list_channels(conn)
        ch = db.find_channel_in(channels, channel_name)
        if not ch:
            return []
        if since_id > 0:
            msgs = db.get_history(conn, ch["id"], limit=min(limit, 200), since_id=since_id)
        else:
            msgs = db.get_history(conn, ch["id"], limit=min(limit, 200))
            msgs = list(reversed(msgs))
        return [
            {
                "id": m["id"],
                "sender": m["sender"],
                "content": m["content"],
                "created_at": m["created_at"].isoformat() if m.get("created_at") else None,
            }
            for m in msgs
        ]
    finally:
        db.release_connection(conn)


@mcp.tool()
@writes
def grove_send_message(channel_name: str, content: str, sender: str = "Auto") -> dict:
    """
    Send a message to a Grove channel. Creates the channel if it doesn't exist.

    Args:
        channel_name: Target channel name.
        content: Message body.
        sender: Display name for the sender (default: Auto — matches public.agents / dashboard).
    """
    conn = db.get_connection()
    try:
        channels = db.list_channels(conn)
        ch = db.find_channel_in(channels, channel_name)
        if not ch:
            ch = db.create_channel(conn, name=channel_name, channel_type="group")
        msg = db.send_message(conn, channel_id=ch["id"], sender=sender, content=content)
        return {"id": msg["id"], "channel": ch["name"], "sent": True}
    finally:
        db.release_connection(conn)


@mcp.tool()
def grove_search(query: str, channel_name: str = "") -> list[dict]:
    """
    Search Grove messages by content.

    Args:
        query: Search term (case-insensitive substring match).
        channel_name: Optional channel to restrict search to.
    """
    conn = db.get_connection()
    try:
        channel_id = None
        if channel_name:
            channels = db.list_channels(conn)
            ch = db.find_channel_in(channels, channel_name)
            channel_id = ch["id"] if ch else None
        msgs = db.search_messages(conn, query, channel_id=channel_id)
        return [
            {
                "sender": m["sender"],
                "content": m["content"],
                "created_at": m["created_at"].isoformat() if m.get("created_at") else None,
            }
            for m in msgs[:50]
        ]
    finally:
        db.release_connection(conn)


@mcp.tool()
def grove_get_identity() -> dict:
    """Get this Grove node's u2u address and public key."""
    from u2u.identity import Identity
    identity_path = Path.home() / ".willow" / "grove_identity.json"
    identity = Identity.load_or_generate(identity_path)
    name = os.getenv("GROVE_NAME", os.getenv("USER", "me"))
    port = int(os.getenv("GROVE_PORT", "8550"))
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            host = s.getsockname()[0]
    except OSError:
        host = "localhost"
    return {
        "address": f"{name}@{host}:{port}",
        "public_key": identity.public_key_hex,
    }


def _msgs_to_dicts(msgs: list) -> list[dict]:
    return [
        {
            "id": m["id"],
            "sender": m["sender"],
            "content": m["content"],
            "reply_to_id": m.get("reply_to_id"),
            "to_agent": m.get("to_agent", db.BUS_BROADCAST),
            "bus_type": m.get("bus_type", "EVENT"),
            "priority": m.get("priority", 3),
            "correlation_id": m.get("correlation_id"),
            "created_at": m["created_at"].isoformat() if m.get("created_at") else None,
        }
        for m in msgs
    ]


# ── Resources (serve mode) ────────────────────────────────────────────

@mcp.resource("grove://channel/{channel_name}")
def grove_channel_resource(channel_name: str) -> str:
    """
    Grove channel as an MCP resource. Read to get recent messages.
    Subscribe to receive push notifications when new messages arrive.
    """
    conn = db.get_connection()
    try:
        channels = db.list_channels(conn)
        ch = db.find_channel_in(channels, channel_name)
        if not ch:
            return f"Channel '{channel_name}' not found."
        msgs = db.get_history(conn, ch["id"], limit=20)
        msgs = list(reversed(msgs))
        lines = [f"[{m['sender']}] {m['content']}" for m in msgs]
        return "\n".join(lines) if lines else "(empty)"
    finally:
        db.release_connection(conn)


def _channel_name_for_id(channel_id: int) -> str | None:
    """Resolve a NOTIFY payload (a channel id) to the name its resource URI uses.

    The old path did this lookup at SUBSCRIBE time and keyed queues by id; the
    bus carries a URI, so the resolution moves to publish time. Returns None on
    any failure — a channel we cannot name is one we cannot address, and
    publishing a wrong URI would be worse than publishing nothing.
    """
    conn = None
    try:
        conn = db.get_connection()
        ch = next((c for c in db.list_channels(conn) if c["id"] == channel_id), None)
        return ch["name"] if ch else None
    except Exception:
        return None
    finally:
        if conn is not None:
            db.release_connection(conn)


@mcp.tool()
def grove_watch(channel_name: str, since_id: int) -> list[dict]:
    """
    Return any new messages in a channel since since_id. Non-blocking.

    Returns immediately — empty list means nothing new yet. Call again to poll.
    Use grove_get_history with since_id for the same effect with more control.

    Args:
        channel_name: Channel to check.
        since_id: Return messages with id greater than this value.
    """
    conn = db.get_connection()
    try:
        channels = db.list_channels(conn)
        ch = db.find_channel_in(channels, channel_name)
        if not ch:
            return []
        msgs = db.get_history(conn, ch["id"], limit=50, since_id=since_id)
        return _msgs_to_dicts(msgs)
    finally:
        db.release_connection(conn)


@mcp.tool()
def grove_watch_all(cursors: dict) -> dict:
    """
    Check multiple channels at once for new messages. Non-blocking.

    Returns immediately. Empty dict means nothing new in any channel.

    Args:
        cursors: Dict mapping channel_name → since_id, e.g. {"general": 6, "github": 10}

    Returns a dict mapping channel_name → list of new messages.
    Only channels with new messages appear in the result.
    Use the highest id in each channel's result as your updated cursor.
    """
    conn = db.get_connection()
    try:
        all_channels = db.list_channels(conn)
        results = {}
        for ch in all_channels:
            name = ch["name"]
            if name not in cursors:
                continue
            msgs = db.get_history(conn, ch["id"], limit=50, since_id=cursors[name])
            if msgs:
                results[name] = _msgs_to_dicts(msgs)
        return results
    finally:
        db.release_connection(conn)


@mcp.tool()
@writes
def grove_reply(channel_name: str, content: str, sender: str, reply_to_id: int) -> dict:
    """
    Reply to a message in a thread.

    Args:
        channel_name: Channel containing the parent message.
        content: Reply body.
        sender: Display name for the sender.
        reply_to_id: ID of the message being replied to.
    """
    conn = db.get_connection()
    try:
        channels = db.list_channels(conn)
        ch = db.find_channel_in(channels, channel_name)
        if not ch:
            return {"error": f"channel '{channel_name}' not found"}
        msg = db.send_message(conn, channel_id=ch["id"], sender=sender,
                              content=content, reply_to_id=reply_to_id)
        db.clear_flag(conn, message_id=reply_to_id, sender="__system__", flag="needs-reply")
        return {"id": msg["id"], "channel": channel_name, "reply_to_id": reply_to_id, "sent": True}
    finally:
        db.release_connection(conn)


@mcp.tool()
def grove_get_thread(message_id: int) -> dict:
    """
    Get a message and all its replies.

    Args:
        message_id: ID of the parent message.
    """
    conn = db.get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM messages WHERE id = %s AND is_deleted = 0", (message_id,))
        row = cur.fetchone()
        if not row:
            return {"error": "message not found"}
        cols = [d[0] for d in cur.description]
        parent = dict(zip(cols, row))
        replies = db.get_thread(conn, message_id)
        flags = db.get_flags(conn, message_id)
        return {
            "parent": _msgs_to_dicts([parent])[0],
            "flags": flags,
            "replies": _msgs_to_dicts(replies),
        }
    finally:
        db.release_connection(conn)


@mcp.tool()
@writes
def grove_flag(message_id: int, flag: str, sender: str) -> dict:
    """
    Set a flag on a message.

    Args:
        message_id: ID of the message to flag.
        flag: One of: needs-reply, starred, read, urgent, resolved.
        sender: Who is setting the flag.
    """
    conn = db.get_connection()
    try:
        db.set_flag(conn, message_id=message_id, sender=sender, flag=flag)
        return {"message_id": message_id, "flag": flag, "set": True}
    except ValueError as e:
        return {"error": str(e)}
    finally:
        db.release_connection(conn)


@mcp.tool()
@writes
def grove_unflag(message_id: int, flag: str, sender: str) -> dict:
    """
    Clear a flag from a message.

    Args:
        message_id: ID of the message to unflag.
        flag: Flag to clear.
        sender: Who is clearing the flag.
    """
    conn = db.get_connection()
    try:
        cleared = db.clear_flag(conn, message_id=message_id, sender=sender, flag=flag)
        return {"message_id": message_id, "flag": flag, "cleared": cleared}
    finally:
        db.release_connection(conn)


@mcp.tool()
@writes
def grove_bus_send(channel_name: str, sender: str, content: str,
                   to_agent: str = "__all__", bus_type: str = "EVENT",
                   priority: int = 3, correlation_id: str = "",
                   ttl: int = 0) -> dict:
    """
    Send a structured bus message — addressed, typed, and prioritized.

    Args:
        channel_name: Channel to post to.
        sender: Sending agent name.
        content: Message body.
        to_agent: Recipient agent name, or '__all__' for broadcast.
        bus_type: COMMAND, RESPONSE, EVENT, INTERRUPT, HEARTBEAT, ACK, DATA, SYNC.
        priority: 0=INTERRUPT, 3=NORMAL, 6=HEARTBEAT, 7=DEBUG.
        correlation_id: Pair requests with responses. Leave empty for new messages.
        ttl: Seconds until message expires. 0 = never.
    """
    conn = db.get_connection()
    try:
        channels = db.list_channels(conn)
        ch = db.find_channel_in(channels, channel_name)
        if not ch:
            ch = db.create_channel(conn, name=channel_name, channel_type="group")
        msg = db.bus_send(
            conn, channel_id=ch["id"], sender=sender, content=content,
            to_agent=to_agent or db.BUS_BROADCAST,
            bus_type=bus_type, priority=priority,
            correlation_id=correlation_id or None,
            ttl=ttl or None,
        )
        if bus_type in ("COMMAND", "INTERRUPT"):
            db.set_flag(conn, message_id=msg["id"], sender="__system__", flag="needs-reply")
        return {
            "id": msg["id"], "channel": ch["name"], "to_agent": to_agent,
            "bus_type": bus_type, "priority": priority,
            "correlation_id": correlation_id or None, "sent": True,
        }
    finally:
        db.release_connection(conn)


@mcp.tool()
def grove_bus_receive(agent: str, channel_name: str = "", since_id: int = 0) -> list[dict]:
    """
    Fetch bus messages addressed to this agent (or broadcast), ordered by priority.

    Args:
        agent: Your agent name — receives messages addressed to you or '__all__'.
        channel_name: Optional — restrict to one channel.
        since_id: Only return messages with id greater than this cursor.
    """
    conn = db.get_connection()
    try:
        if channel_name:
            channels = db.list_channels(conn)
            ch = db.find_channel_in(channels, channel_name)
            if not ch:
                return []
            msgs = db.bus_receive(conn, agent=agent, since_id=since_id)
            msgs = [m for m in msgs if m.get("channel_id") == ch["id"]]
        else:
            msgs = db.bus_receive(conn, agent=agent, since_id=since_id)
        return _msgs_to_dicts(msgs)
    finally:
        db.release_connection(conn)


@mcp.tool()
@writes
def grove_bus_delete(channel_name: str, sender: str, message_id: int) -> dict:
    """
    Soft-delete a bus message — retracted, invisible to grove_bus_receive.

    Args:
        channel_name: Channel the message was sent to (used for context only).
        sender: Your agent name — must match the original message sender.
        message_id: ID of the message to retract.
    """
    conn = db.get_connection()
    try:
        return db.bus_delete(conn, message_id=message_id, sender=sender)
    except (ValueError, PermissionError) as exc:
        return {"deleted": False, "error": str(exc)}
    finally:
        db.release_connection(conn)


@mcp.tool()
@writes
def grove_ack(channel_name: str, sender: str, correlation_id: str,
              original_id: int) -> dict:
    """
    Acknowledge a received message. Clears needs-reply flag on the original.

    Args:
        channel_name: Channel of the original message.
        sender: Your agent name.
        correlation_id: The correlation_id from the message you're acking.
        original_id: The id of the message being acknowledged.
    """
    conn = db.get_connection()
    try:
        channels = db.list_channels(conn)
        ch = db.find_channel_in(channels, channel_name)
        if not ch:
            return {"error": f"channel '{channel_name}' not found"}
        msg = db.bus_send(
            conn, channel_id=ch["id"], sender=sender,
            content=f"ACK {correlation_id}",
            bus_type="ACK", priority=2,
            correlation_id=correlation_id,
        )
        db.clear_flag(conn, message_id=original_id, sender="__system__", flag="needs-reply")
        db.set_flag(conn, message_id=original_id, sender=sender, flag="read")
        return {"id": msg["id"], "acked": original_id, "correlation_id": correlation_id}
    finally:
        db.release_connection(conn)


@mcp.tool()
@writes
def grove_heartbeat(sender: str) -> dict:
    """
    Broadcast a heartbeat — I am alive and on the bus.

    Args:
        sender: Your agent name.
    """
    conn = db.get_connection()
    try:
        channels = db.list_channels(conn)
        ch = next((c for c in channels if c["name"] == "general"), None)
        if not ch:
            ch = db.create_channel(conn, name="general", channel_type="group")
        msg = db.bus_send(
            conn, channel_id=ch["id"], sender=sender,
            content=f"{sender} online",
            bus_type="HEARTBEAT", priority=6,
            to_agent=db.BUS_BROADCAST,
        )
        return {"id": msg["id"], "sender": sender, "bus_type": "HEARTBEAT"}
    finally:
        db.release_connection(conn)


@mcp.tool()
def grove_inbox(agent: str = "", since_id: int = 0, limit: int = 35) -> list[dict]:
    """
    Fleet inbox for Cursor: @mentions (@Auto / @all / GROVE_DESK_MENTIONS) plus messages
    bus-addressed directly to Auto (to_agent matches) even when the body has no @.

    Poll this when coordinating from the IDE— nothing is pushed into chat automatically.

    Args:
        agent: Recipient identity as stored on to_agent; default follows
               GROVE_SENDER/GROVE_NAME/dashboard default (Auto).
        since_id: Only messages with id greater than this (cursor for polling).
        limit: Merge cap after dedupe-by-id newest-first.
    """
    who = agent.strip() if agent.strip() else None
    cap = max(5, min(int(limit), 80))
    return _grove_reader.grove_inbox_bundle(who, since_id=max(0, int(since_id)), merge_limit=cap)


@mcp.tool()
def grove_flagged(flag: str, channel_name: str = "") -> list[dict]:
    """
    List messages carrying a given flag across all channels (or one channel).

    Args:
        flag: One of: needs-reply, starred, read, urgent, resolved.
        channel_name: Optional — restrict to one channel.
    """
    conn = db.get_connection()
    try:
        channel_id = None
        if channel_name:
            channels = db.list_channels(conn)
            ch = db.find_channel_in(channels, channel_name)
            channel_id = ch["id"] if ch else None
        msgs = db.get_flagged(conn, flag=flag, channel_id=channel_id)
        return _msgs_to_dicts(msgs)
    finally:
        db.release_connection(conn)


# ── Fleet awareness & channel management ─────────────────────────────────
# These expose read/write surfaces that already existed for the local dashboard
# (grove_reader) to remote MCP clients (claude.ai). Each wraps a reader function
# that owns its own connection, so there is no pool handling here. Datetimes are
# coerced to ISO strings by _jsonify because the MCP result must be JSON.
from datetime import date, datetime  # noqa: E402
from decimal import Decimal  # noqa: E402


def _jsonify(value):
    """Recursively coerce non-JSON DB types to JSON-safe ones for MCP results.

    datetime/date -> ISO string; Decimal (psycopg2 returns NUMERIC as Decimal)
    -> float; set/frozenset -> list. Dicts and sequences recurse.
    """
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if isinstance(value, Decimal):
        return float(value)
    if isinstance(value, dict):
        return {k: _jsonify(v) for k, v in value.items()}
    if isinstance(value, (list, tuple, set, frozenset)):
        return [_jsonify(v) for v in value]
    return value


@mcp.tool()
def grove_agents() -> list[dict]:
    """
    List fleet agents by most-recent HEARTBEAT, newest first.

    Each entry: {sender, last_seen_at (ISO), age_secs}. Use this to see who is
    currently alive in the fleet before addressing or coordinating with them.
    """
    return _jsonify(_grove_reader.grove_agents())


@mcp.tool()
def grove_fleet_status(limit: int = 50) -> list[dict]:
    """
    Rich fleet status rows — presence plus what each agent is doing.

    Each row: {sender, last_seen_at (ISO), age_secs, ui_state, peek, blocked,
    reply_to_message_id, correlation_id}. This is the AGENTS-region view the
    dashboard shows, made available remotely.

    Args:
        limit: Max agents to return (clamped 1..100).
    """
    cap = max(1, min(int(limit), 100))
    return _jsonify(_grove_reader.grove_agent_fleet_rows(limit=cap))


@mcp.tool()
def grove_mentions(handle: str, limit: int = 20) -> list[dict]:
    """
    Recent messages that @-mention a handle, across all channels, newest first.

    Args:
        handle: The mention handle to search for (with or without a leading @).
        limit: Max messages to return (clamped 1..50).
    """
    name = handle.strip().lstrip("@")
    if not name:
        return []
    cap = max(1, min(int(limit), 50))
    return _jsonify(_grove_reader.grove_mentions(name, limit=cap))


@mcp.tool()
def grove_human_required(limit: int = 30, open_only: bool = True) -> list[dict]:
    """
    The human-required queue — work that pauses automation until a person acts
    (consent, attestation, review, onboarding). Priority-first, then newest.

    Poll this from a remote session to see what needs the operator before the
    fleet can proceed.

    Args:
        limit: Max items to return (clamped 1..100).
        open_only: When true (default) only items with status='open'.
    """
    cap = max(1, min(int(limit), 100))
    return _jsonify(_grove_reader.human_required_queue(limit=cap, open_only=bool(open_only)))


@mcp.tool()
@writes
def grove_create_channel(name: str, description: str = "") -> dict:
    """
    Create a new group text channel (or revive an archived one of the same name).

    Args:
        name: Desired channel name; normalized to Grove's channel-name rules.
        description: Optional description; defaults to "#<name>".

    Returns {ok: bool, channel?: {...}, error?: str}.
    """
    return _jsonify(_grove_reader.grove_create_text_channel(name, description))


# ── OAuth approval route (serve mode only) ───────────────────────────────

if _SERVE_MODE and _auth_provider is not None:
    from html import escape as html_escape

    from mcp.server.auth.provider import construct_redirect_uri
    from starlette.requests import Request
    from starlette.responses import HTMLResponse, RedirectResponse

    @mcp.custom_route("/", methods=["GET", "POST", "DELETE", "PUT"])
    async def root_redirect(request: Request) -> RedirectResponse:
        """Redirect bare-root MCP calls to /mcp for clients that drop the path."""
        url = str(request.url).replace(str(request.base_url).rstrip("/"), "", 1)
        target = "/mcp" + (url if url and url != "/" else "")
        return RedirectResponse(target, status_code=307)

    # Loopback source addresses accepted for the approval POST. Per
    # INVARIANTS.md §7, "the operator approves via a loopback-only page":
    # this list is the enforcement of that clause. A public tunnel deployment
    # that forwards its client's public IP to the app will not match; the
    # operator has to reach /grove-approve from the box itself (SSH port-
    # forward, `xdg-open http://127.0.0.1:8767/grove-approve?pending=…`).
    _LOOPBACK_HOSTS = {"127.0.0.1", "::1", "localhost"}

    def _remote_is_loopback(request: Request) -> bool:
        """The approval POST's peer must be loopback — INVARIANTS.md §7.

        A same-box reverse proxy (Pangolin, nginx, cloudflared, tailscale)
        forwards traffic to 127.0.0.1:<port>, so `request.client.host` is
        loopback for every off-box POST that reaches the app that way. To
        keep the loopback promise real behind such a proxy, the operator
        opts in via `GROVE_MCP_TRUSTED_PROXIES=<comma,ips>`: when set, AND
        the raw TCP peer is in that trusted set, the leftmost hop of
        `X-Forwarded-For` becomes the effective peer for the loopback
        check. Unset (default) keeps prior behavior — no XFF trust, no
        widening. Loki v0.9 audit finding #15.
        """
        client = request.client
        if client is None or not client.host:
            return False

        effective_host = client.host
        trusted = set(_csv_env("GROVE_MCP_TRUSTED_PROXIES"))
        if trusted and client.host in trusted:
            headers = getattr(request, "headers", None)
            xff = headers.get("x-forwarded-for", "") if headers is not None else ""
            if xff:
                first_hop = xff.split(",")[0].strip()
                if first_hop:
                    effective_host = first_hop

        if effective_host in _LOOPBACK_HOSTS:
            return True

        # Refused. Log once when the refusal is specifically because a
        # trusted proxy forwarded an off-box hop — that is the operational
        # signal the operator wants to see.
        if trusted and client.host in trusted and effective_host != client.host:
            _log_forwarded_refusal_once(effective_host)
        return False

    @mcp.custom_route("/grove-approve", methods=["GET", "POST"])
    async def grove_approve(request: Request) -> HTMLResponse | RedirectResponse:
        """Single-user OAuth approval page — the authorization decision itself.

        /authorize parks a request here and redirects the browser to this page.
        No authorization code exists until the POST below runs, so declining or
        simply closing the tab denies the grant. `pending` is a 256-bit
        one-shot key, which is also what stops a third party from POSTing an
        approval they were never shown.

        Per INVARIANTS.md §7, the POST that completes the grant is refused
        unless the request originates from a loopback address — the operator
        has to be on the box. GET renders normally so the operator can inspect
        the page over a tunnel if they want, but the grant itself never crosses
        the network.
        """
        pending_key = request.query_params.get("pending", "")
        entry = _auth_provider.pop_pending(pending_key)

        if request.method == "GET":
            if not entry:
                return HTMLResponse("<h2>Grove OAuth</h2><p>Invalid or expired approval link.</p>", status_code=400)
            client, params = entry
            # Re-stash so POST can use it
            _auth_provider.stash_pending(pending_key, client, params)
            # client_name and redirect_uri are supplied by whoever registered the
            # client, so they are escaped: this page must not be a way to inject
            # markup into the operator's browser.
            name = html_escape(client.client_name or client.client_id)
            target = html_escape(str(params.redirect_uri))
            scopes = html_escape(" ".join(effective_scopes(client, params)))
            page = f"""<!DOCTYPE html>
<html><head><title>Grove Access Request</title>
<style>body{{font-family:sans-serif;max-width:480px;margin:80px auto;padding:20px}}
button{{padding:12px 24px;font-size:16px;cursor:pointer;margin:8px}}
code{{word-break:break-all}}
.allow{{background:#2563eb;color:#fff;border:none;border-radius:6px}}
.deny{{background:#e5e7eb;color:#111;border:none;border-radius:6px}}</style>
</head><body>
<h2>Allow Grove access?</h2>
<p><strong>{name}</strong> is requesting access to read and send Grove messages.</p>
<p>Scopes: <code>{scopes}</code><br>
Codes will be sent to: <code>{target}</code></p>
<p>This approval only completes when submitted from the local box (127.0.0.1).
If you did not just start this from your own client, click Deny.</p>
<form method="post" action="/grove-approve?pending={pending_key}">
  <button class="allow" type="submit" name="action" value="allow">Allow</button>
  <button class="deny" type="submit" name="action" value="deny">Deny</button>
</form>
</body></html>"""
            return HTMLResponse(page)

        # POST — issue code or deny (entry already popped at top of function).
        # Loopback check first: a non-loopback origin is refused before the
        # action is even inspected. INVARIANTS.md §7.
        if not _remote_is_loopback(request):
            return HTMLResponse(
                "<h2>Access denied.</h2>"
                "<p>Approval must be submitted from the local host (127.0.0.1). "
                "See INVARIANTS.md §7.</p>",
                status_code=403,
            )

        form = await request.form()
        action = form.get("action", "deny")
        if not entry or action != "allow":
            return HTMLResponse("<h2>Access denied.</h2>", status_code=200)

        client, params = entry
        code = _auth_provider.issue_code(client, params)
        redirect_url = construct_redirect_uri(
            str(params.redirect_uri),
            code=code,
            state=params.state,
        )
        return RedirectResponse(redirect_url, status_code=302)


def _snapshot_grove_mtimes(grove_dir: Path) -> dict[Path, float]:
    return {p: p.stat().st_mtime for p in grove_dir.glob("*.py")}


def _watch_serve_supervisor() -> None:
    """Reload dev mode: run `--serve` in a subprocess and restart on `grove/*.py` changes.

    Calling `mcp.run()` in-process blocks forever, so an outer poll loop cannot run.
    Supervising a child fixes that without requiring uvicorn reload internals.
    """
    import subprocess
    import time

    grove_dir = Path(__file__).parent
    mtimes = _snapshot_grove_mtimes(grove_dir)

    def child_argv() -> list[str]:
        args = [sys.executable, "-m", "grove.mcp_local"]
        for a in sys.argv[1:]:
            if a == "--watch":
                continue
            args.append(a)
        return args

    proc: subprocess.Popen | None = None
    print(f"[grove-mcp] watch: supervising child; grove dir={grove_dir}", flush=True)
    try:
        while True:
            cmd = child_argv()
            print(f"[grove-mcp] watch: spawn: {' '.join(cmd)}", flush=True)
            proc = subprocess.Popen(cmd)
            reload_requested = False
            while proc.poll() is None:
                time.sleep(0.5)
                for p in grove_dir.glob("*.py"):
                    try:
                        cur = p.stat().st_mtime
                    except OSError:
                        continue
                    old = mtimes.get(p)
                    if old is None or cur != old:
                        reload_requested = True
                        break
                if reload_requested:
                    print("[grove-mcp] watch: source changed — restarting child", flush=True)
                    proc.terminate()
                    try:
                        proc.wait(timeout=15)
                    except subprocess.TimeoutExpired:
                        proc.kill()
                    mtimes = _snapshot_grove_mtimes(grove_dir)
                    break
            else:
                rc = proc.returncode if proc is not None else -1
                if rc == 0:
                    print("[grove-mcp] watch: child exited cleanly — supervisor done", flush=True)
                    return
                print(f"[grove-mcp] watch: child exited {rc}; retry in 2s", flush=True)
                time.sleep(2)
                mtimes = _snapshot_grove_mtimes(grove_dir)
    except KeyboardInterrupt:
        print("[grove-mcp] watch: interrupted", flush=True)
        if proc is not None and proc.poll() is None:
            proc.terminate()
            try:
                proc.wait(timeout=10)
            except subprocess.TimeoutExpired:
                proc.kill()


def main():
    if "--serve" in sys.argv:
        # Approval is always required per INVARIANTS.md §7 — the pre-PR-6
        # auto-approve escape hatch is gone. Every /authorize walks through
        # /grove-approve and needs a loopback click.
        reg_hint = "dynamic-reg=ON" if _ALLOW_DYNAMIC_REG else "dynamic-reg=OFF (opt-in via GROVE_MCP_ALLOW_DYNAMIC_REGISTRATION=1)"
        gate = f"OAuth: enabled, approval required at /grove-approve, {reg_hint}"
        print(f"[grove-mcp] serving on http://127.0.0.1:{_PORT}/mcp  ({gate})", flush=True)
        # SDK 2.x: host/port/transport_security/path all belong to the
        # transport now, not the server object — the stateless core making
        # "where and how this instance listens" a property of the run.
        # `mount_path` was renamed `streamable_http_path`.
        mcp.run(
            transport="streamable-http",
            host="127.0.0.1",
            port=_PORT,
            streamable_http_path="/",
            transport_security=_transport_security(),
        )
    else:
        mcp.run(transport="stdio")


if __name__ == "__main__":
    if "--watch" in sys.argv:
        if "--serve" not in sys.argv:
            print("[grove-mcp] error: --watch requires --serve", file=sys.stderr)
            sys.exit(2)
        _watch_serve_supervisor()
    else:
        main()
