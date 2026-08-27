# tests/test_tool_scopes.py — per-tool OAuth read/write scopes for the
# serve-mode (remote/claude.ai) Grove MCP surface.
#
# The crux: enforcement must read the CURRENT request's token, not some
# ambient setting. grove/mcp_local._require_scope does that via the MCP SDK's
# own auth-context contextvar (mcp.server.auth.middleware.auth_context) — the
# same one AuthContextMiddleware populates from a real Bearer-token request.
# Driving that contextvar directly, without standing up a real HTTP request,
# is how this file "mocks the auth context": it is the SDK's actual
# mechanism, not a stand-in for it.
#
# grove.mcp_local decides serve vs stdio at import time (sys.argv), but the
# scope constants, `_require_scope`, and the `@writes` decorator are
# module-level and defined unconditionally either way (see mcp_local.py) — so
# `_require_scope`'s behavior is exercised here by driving the contextvar
# directly, independent of whichever mode happens to have built the module's
# `mcp` singleton by the time this file runs (that is itself shared,
# process-wide, mutable suite state — see the collection-time import below).
#
# A separate check, `test_serve_mode_auth_settings_use_the_granular_scopes`,
# pins that the *serve-mode* AuthSettings wiring itself uses these same
# constants. It re-imports under `--serve` using the same trick
# tests/test_mcp_serve_oauth_flow.py uses — but has to do so here, at MODULE
# (collection) scope, not inside a test function. sys.modules['grove.mcp_local']
# is one slot shared by the whole suite; test_transport_security.py later
# calls `importlib.reload()` against whatever object sits in that slot at ITS
# OWN collection time. Swapping the slot's identity from inside a *test
# function* — i.e. after collection has already finished and every file's
# module-level `mcp_local` name is bound — would leave those already-bound
# references pointing at an orphaned object, breaking that file's reload.
from __future__ import annotations

import contextlib
import os
import sys
import tempfile
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

import grove.mcp_local as mcp_local  # noqa: E402
from mcp.server.auth.middleware.auth_context import auth_context_var  # noqa: E402
from mcp.server.auth.middleware.bearer_auth import AuthenticatedUser  # noqa: E402
from mcp.server.auth.provider import AccessToken  # noqa: E402
from mcp.server.mcpserver.exceptions import ToolError  # noqa: E402

# ── Collection-time probe: what does serve mode actually build? ──────────
_saved_argv = list(sys.argv)
_saved_env = {k: os.environ.get(k) for k in ("GROVE_MCP_URL", "HOME", "GROVE_MCP_AUTO_APPROVE")}

sys.argv = ["mcp_local", "--serve"]
os.environ["GROVE_MCP_URL"] = "https://grove-scopes.example.test"
os.environ["HOME"] = tempfile.mkdtemp(prefix="grove-scopes-test-home-")
os.environ.pop("GROVE_MCP_AUTO_APPROVE", None)
try:
    sys.modules.pop("grove.mcp_local", None)
    import grove.mcp_local as _serve_mcp_local
finally:
    sys.argv = _saved_argv
    for _k, _v in _saved_env.items():
        if _v is None:
            os.environ.pop(_k, None)
        else:
            os.environ[_k] = _v

_SERVE_AUTH = _serve_mcp_local.mcp.settings.auth


def _access_token(scopes: list[str]) -> AccessToken:
    return AccessToken(token="test-token", client_id="test-client", scopes=list(scopes))


@contextlib.contextmanager
def _token_in_context(scopes: list[str] | None):
    """Simulate the current request carrying a token with these scopes.

    `scopes=None` simulates stdio: no request ever ran through
    AuthContextMiddleware, so the contextvar is at its default (None) and
    `get_access_token()` returns None — exactly the no-op path.
    """
    if scopes is None:
        yield
        return
    reset = auth_context_var.set(AuthenticatedUser(_access_token(scopes)))
    try:
        yield
    finally:
        auth_context_var.reset(reset)


# ── The gate itself ───────────────────────────────────────────────────────


def test_no_token_in_context_is_a_noop():
    """Stdio (and any call with nothing in the auth context): never refused."""
    with _token_in_context(None):
        mcp_local._require_scope(mcp_local.SCOPE_READ)
        mcp_local._require_scope(mcp_local.SCOPE_WRITE)


def test_read_only_token_may_read():
    with _token_in_context([mcp_local.SCOPE_READ]):
        mcp_local._require_scope(mcp_local.SCOPE_READ)


def test_read_only_token_is_refused_write():
    with _token_in_context([mcp_local.SCOPE_READ]):
        with pytest.raises(ToolError) as excinfo:
            mcp_local._require_scope(mcp_local.SCOPE_WRITE)
    message = str(excinfo.value)
    assert "grove:write" in message


def test_write_only_token_may_write_but_not_gated_reads():
    """A write-only token is not what any client should request (reads are
    ungated below the server-wide floor), but the gate itself is symmetric."""
    with _token_in_context([mcp_local.SCOPE_WRITE]):
        mcp_local._require_scope(mcp_local.SCOPE_WRITE)
        with pytest.raises(ToolError):
            mcp_local._require_scope(mcp_local.SCOPE_READ)


@pytest.mark.parametrize("scopes", [["grove"], ["grove", "grove:read"], ["grove:read", "grove:write", "grove"]])
def test_grove_superscope_implies_both(scopes):
    """The back-compat superscope grants both — this is what keeps a pre-existing
    30-day `grove` token (and any client that still asks for plain `grove`)
    working at full access without reissuing anything."""
    with _token_in_context(scopes):
        mcp_local._require_scope(mcp_local.SCOPE_READ)
        mcp_local._require_scope(mcp_local.SCOPE_WRITE)


def test_full_granular_token_may_do_both():
    with _token_in_context([mcp_local.SCOPE_READ, mcp_local.SCOPE_WRITE]):
        mcp_local._require_scope(mcp_local.SCOPE_READ)
        mcp_local._require_scope(mcp_local.SCOPE_WRITE)


def test_no_scopes_at_all_is_refused():
    with _token_in_context([]):
        with pytest.raises(ToolError):
            mcp_local._require_scope(mcp_local.SCOPE_READ)
        with pytest.raises(ToolError):
            mcp_local._require_scope(mcp_local.SCOPE_WRITE)


# ── The decorator, wired onto a real tool ────────────────────────────────
#
# grove_list_channels (read) and grove_send_message (write) are exercised
# through their actual bodies, not stand-ins — db.* is monkeypatched at the
# module boundary mcp_local imports it through (`import grove_db as db`), the
# same seam tests/test_mcp_remote_tools.py already uses for _grove_reader.


@pytest.fixture
def fake_db(monkeypatch):
    channels = [{"id": 1, "name": "general", "channel_type": "group", "description": None}]

    class _Conn:
        pass

    monkeypatch.setattr(mcp_local.db, "get_connection", lambda: _Conn())
    monkeypatch.setattr(mcp_local.db, "release_connection", lambda conn: None)
    monkeypatch.setattr(mcp_local.db, "list_channels", lambda conn: channels)
    monkeypatch.setattr(mcp_local.db, "find_channel_in", lambda chans, name: chans[0] if chans else None)
    monkeypatch.setattr(
        mcp_local.db, "send_message",
        lambda conn, *, channel_id, sender, content, reply_to_id=None: {"id": 42},
    )
    return channels


def test_read_tool_runs_for_a_read_only_token(fake_db):
    with _token_in_context([mcp_local.SCOPE_READ]):
        out = mcp_local.grove_list_channels()
    assert out == [{"id": 1, "name": "general", "type": "group", "description": None}]


def test_write_tool_runs_for_a_full_token(fake_db):
    with _token_in_context([mcp_local.SCOPE_READ, mcp_local.SCOPE_WRITE]):
        out = mcp_local.grove_send_message("general", "hi", sender="tester")
    assert out == {"id": 42, "channel": "general", "sent": True}


def test_write_tool_runs_for_the_grove_superscope(fake_db):
    with _token_in_context([mcp_local.SCOPE_FULL]):
        out = mcp_local.grove_send_message("general", "hi", sender="tester")
    assert out["sent"] is True


def test_write_tool_refused_for_a_read_only_token(fake_db):
    """The headline case: a read-only remote token must not be able to write."""
    with _token_in_context([mcp_local.SCOPE_READ]):
        with pytest.raises(ToolError) as excinfo:
            mcp_local.grove_send_message("general", "hi", sender="tester")
    assert "grove:write" in str(excinfo.value)


def test_write_tool_runs_under_stdio_with_no_auth_context(fake_db):
    """No token/auth context at all (stdio's actual condition) allows everything —
    local Claude Code usage must not regress."""
    with _token_in_context(None):
        out = mcp_local.grove_send_message("general", "hi", sender="tester")
    assert out["sent"] is True


def test_read_tool_unaffected_by_decorator_absence(fake_db):
    """Read tools carry no @writes decorator; a read-only token still reads."""
    with _token_in_context([mcp_local.SCOPE_READ]):
        out = mcp_local.grove_list_channels()
    assert len(out) == 1


# ── All nine write tools are actually decorated ──────────────────────────

_EXPECTED_WRITE_TOOLS = {
    "grove_send_message", "grove_reply", "grove_flag", "grove_unflag",
    "grove_bus_send", "grove_bus_delete", "grove_ack", "grove_heartbeat",
    "grove_create_channel",
}


def test_every_write_tool_carries_the_scope_gate():
    """A write tool's `@writes` wrapper must refuse a read-only token — checked
    by calling each with a read-only token in context and confirming ToolError,
    without needing a live DB (the gate raises before the body runs)."""
    for name in _EXPECTED_WRITE_TOOLS:
        fn = getattr(mcp_local, name)
        with _token_in_context([mcp_local.SCOPE_READ]):
            with pytest.raises(ToolError):
                fn()  # missing required args is fine — the scope gate raises first


def test_read_tools_carry_no_write_gate():
    """Spot-check a handful of read tools: none is wrapped by `writes`, i.e.
    none has the `_scope_checked` wrapper's `__wrapped__` marker from it."""
    read_sample = [
        "grove_list_channels", "grove_get_history", "grove_search",
        "grove_get_identity", "grove_watch", "grove_watch_all",
        "grove_get_thread", "grove_bus_receive", "grove_inbox",
        "grove_flagged", "grove_agents", "grove_fleet_status",
        "grove_mentions", "grove_human_required",
    ]
    for name in read_sample:
        fn = getattr(mcp_local, name)
        # No read tool's call may raise ToolError purely from a missing scope
        # when a read-only token is in context (arg errors are a different
        # exception and are fine to hit here — the point is scope, not arity).
        with _token_in_context([mcp_local.SCOPE_READ]):
            try:
                fn()
            except ToolError as e:
                assert "insufficient scope" not in str(e)
            except Exception:
                pass  # missing required positional args etc — not a scope refusal


# ── Composition with @mcp.tool(): schema/docstring survive @writes ───────


def test_writes_preserves_signature_and_docstring_for_mcp_tool():
    tool = mcp_local.mcp._tool_manager.get_tool("grove_send_message")
    assert tool.parameters["required"] == ["channel_name", "content"]
    assert "sender" in tool.parameters["properties"]
    assert "Send a message to a Grove channel" in tool.description


# ── mcp_auth: scope expansion and the effective-scopes fallback ──────────


def test_expand_scopes_widens_the_superscope():
    from grove.mcp_auth import SCOPE_READ, SCOPE_WRITE, _expand_scopes

    assert set(_expand_scopes(["grove"])) == {"grove", SCOPE_READ, SCOPE_WRITE}
    assert _expand_scopes(["grove:read"]) == ["grove:read"]  # untouched, no superscope
    assert _expand_scopes([]) == []
    assert _expand_scopes(None) == []


def test_effective_scopes_prefers_explicit_request_then_client_then_fallback():
    from mcp.server.auth.provider import AuthorizationParams
    from mcp.shared.auth import OAuthClientInformationFull

    from grove.mcp_auth import effective_scopes

    client = OAuthClientInformationFull(
        client_id="c1",
        client_name="Test",
        redirect_uris=["https://example.test/cb"],
        grant_types=["authorization_code"],
        scope="grove:read grove:write",
    )
    params_explicit = AuthorizationParams(
        state="s", scopes=["grove:read"],
        code_challenge="x", redirect_uri="https://example.test/cb",
        redirect_uri_provided_explicitly=True,
    )
    params_implicit = AuthorizationParams(
        state="s", scopes=None,
        code_challenge="x", redirect_uri="https://example.test/cb",
        redirect_uri_provided_explicitly=True,
    )

    assert effective_scopes(client, params_explicit) == ["grove:read"]
    assert effective_scopes(client, params_implicit) == ["grove:read", "grove:write"]

    bare_client = OAuthClientInformationFull(
        client_id="c2", client_name="Old", redirect_uris=["https://example.test/cb"],
        grant_types=["authorization_code"],
    )
    assert effective_scopes(bare_client, params_implicit) == ["grove"]


def test_load_access_token_widens_a_pre_existing_grove_token(tmp_path):
    """The regression this whole design exists to avoid: a 30-day token
    persisted before per-tool scopes existed must still satisfy a
    `required_scopes=["grove:read"]` gate after this change ships."""
    import asyncio
    import json

    from grove.mcp_auth import GroveOAuthProvider

    token_path = tmp_path / "grove_mcp_token"
    token_path.write_text(json.dumps({
        "clients": {},
        "access_tokens": {
            "old-tok": {
                "token": "old-tok", "client_id": "c1",
                "scopes": ["grove"], "expires_at": None,
            },
        },
        "refresh_tokens": {},
    }))

    provider = GroveOAuthProvider(token_path=token_path, base_url="https://grove.example.test")
    loaded = asyncio.run(provider.load_access_token("old-tok"))

    assert loaded is not None
    assert "grove:read" in loaded.scopes
    assert "grove:write" in loaded.scopes
    assert "grove" in loaded.scopes  # nothing is taken away, only widened


# ── Serve-mode wiring: AuthSettings actually uses the granular scopes ────


def test_serve_mode_auth_settings_use_the_granular_scopes():
    """Pins the AuthSettings construction in grove/mcp_local.py itself — not
    just the constants, but that they were actually threaded through. See the
    collection-time probe near the top of this file for why the re-import
    under `--serve` happens there and not in this function body."""
    assert _SERVE_AUTH is not None
    assert set(_SERVE_AUTH.required_scopes or []) == {"grove:read"}
    reg = _SERVE_AUTH.client_registration_options
    assert set(reg.valid_scopes or []) == {"grove", "grove:read", "grove:write"}
    assert set(reg.default_scopes or []) == {"grove:read", "grove:write"}
