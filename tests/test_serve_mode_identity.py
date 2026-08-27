# tests/test_serve_mode_identity.py — serve-mode operator identity resolution
# b17: TSMI  ΔΣ=42
#
# CODE_REVIEW.md P1 ("willow-mcp — serve mode ... has zero tests") noted that
# _SERVE_MODE was computed from sys.argv at module import, so the highest-value
# branch in the auth gate could not be exercised. PR 6 makes _SERVE_MODE
# injectable via `_detect_serve_mode(argv=...)` and introduces
# `_resolve_serve_identity(token)` and `_gate(serve_mode, token)` — the seam
# through which serve mode refuses a call with no verified identity. Per
# INVARIANTS.md §7, that refusal must be real, not decorative.
from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

mcp_local = pytest.importorskip("grove.mcp_local")


class _Tok:
    """Minimal stand-in for an mcp.server.auth.provider.AccessToken.

    Duck-typed against _resolve_serve_identity's actual reads — client_id and
    scopes. Not a Pydantic model, so tests don't drag in the SDK's model
    lifecycle just to check identity resolution.
    """

    def __init__(self, client_id: str | None, scopes):
        self.client_id = client_id
        self.scopes = scopes


# ── _detect_serve_mode / _SERVE_MODE injectability ───────────────────────────


def test_detect_serve_mode_uses_argv_by_default(monkeypatch):
    """The default path — the module inspects sys.argv."""
    monkeypatch.setattr(sys, "argv", ["mcp_local", "--serve"])
    assert mcp_local._detect_serve_mode() is True

    monkeypatch.setattr(sys, "argv", ["mcp_local"])
    assert mcp_local._detect_serve_mode() is False


def test_detect_serve_mode_accepts_explicit_argv():
    """The injection point CODE_REVIEW.md P1 asked for.

    Before PR 6, `_SERVE_MODE = "--serve" in sys.argv` at module import time
    meant a test could not toggle the branch without a subprocess. Passing
    argv here is what makes the branch reachable.
    """
    assert mcp_local._detect_serve_mode(["mcp_local", "--serve"]) is True
    assert mcp_local._detect_serve_mode(["mcp_local"]) is False
    assert mcp_local._detect_serve_mode([]) is False
    assert mcp_local._detect_serve_mode(["mcp_local", "--other"]) is False


# ── _resolve_serve_identity — the L-AUTH-02-shaped seam ──────────────────────


def test_resolve_identity_returns_operator_for_a_verified_token():
    """A token carrying at least one recognised Grove scope IS the operator."""
    tok = _Tok(client_id="claude-ai", scopes=["grove:read", "grove:write"])
    assert mcp_local._resolve_serve_identity(tok) == "grove-operator"


def test_resolve_identity_accepts_the_superscope():
    """`grove` on its own is the back-compat full-access scope; it counts."""
    tok = _Tok(client_id="legacy", scopes=["grove"])
    assert mcp_local._resolve_serve_identity(tok) == "grove-operator"


def test_resolve_identity_missing_binding_returns_none():
    """No token at all is the "missing binding" case. Fail-closed.

    INVARIANTS.md §7 — the gate refuses when no identity is verified.
    """
    assert mcp_local._resolve_serve_identity(None) is None


def test_resolve_identity_malformed_returns_none_and_logs_once(capsys, monkeypatch):
    """A structurally broken token (no client_id, wrong scopes shape) is
    denied AND logged once — never allowed under an ambient assumption."""
    monkeypatch.setattr(mcp_local, "_identity_malformed_logged", False)

    # No client_id — malformed.
    assert mcp_local._resolve_serve_identity(_Tok(client_id=None, scopes=["grove"])) is None
    err = capsys.readouterr().err
    assert "WARNING" in err and "malformed" in err

    # A second malformed token does NOT log again (log-once).
    assert mcp_local._resolve_serve_identity(_Tok(client_id="", scopes=["grove"])) is None
    err_again = capsys.readouterr().err
    assert "WARNING" not in err_again


def test_resolve_identity_wrong_scopes_type_returns_none(monkeypatch):
    """scopes must be an iterable of strings; a plain string is malformed."""
    monkeypatch.setattr(mcp_local, "_identity_malformed_logged", False)
    tok = _Tok(client_id="x", scopes="grove")  # not a list
    assert mcp_local._resolve_serve_identity(tok) is None


def test_resolve_identity_unknown_scopes_returns_none():
    """A token whose scopes are all foreign to Grove is not the operator.

    Refresh, revoke, and other OAuth-shaped surfaces don't grant tool access.
    """
    tok = _Tok(client_id="x", scopes=["some:other:scope"])
    assert mcp_local._resolve_serve_identity(tok) is None


def test_resolve_identity_empty_scopes_returns_none():
    """An empty scope set is not a grant. INVARIANTS.md §7."""
    assert mcp_local._resolve_serve_identity(_Tok(client_id="x", scopes=[])) is None


# ── _gate — the serve branch that consults _resolve_serve_identity ──────────


def test_gate_stdio_is_implicit_trust():
    """Stdio mode has no request context — the local process is the operator.

    The gate here is a no-op precisely because there is no request boundary
    to enforce against; it stays True to preserve local Claude Code behavior.
    """
    assert mcp_local._gate(serve_mode=False, token=None) is True
    assert mcp_local._gate(serve_mode=False, token=_Tok("x", ["grove"])) is True


def test_gate_serve_denies_when_identity_is_none():
    """The core assertion CODE_REVIEW.md P1 wanted to see pinned: the serve
    branch of `_gate` denies when `_resolve_serve_identity` returns None."""
    assert mcp_local._gate(serve_mode=True, token=None) is False


def test_gate_serve_denies_a_malformed_token(monkeypatch):
    monkeypatch.setattr(mcp_local, "_identity_malformed_logged", False)
    assert mcp_local._gate(serve_mode=True, token=_Tok(None, ["grove"])) is False


def test_gate_serve_allows_a_verified_token():
    tok = _Tok(client_id="claude-ai", scopes=["grove:read"])
    assert mcp_local._gate(serve_mode=True, token=tok) is True


# ── The public-tunnel warning ─────────────────────────────────────────────────


def test_public_tunnel_warning_fires_without_acknowledgement(monkeypatch, capsys):
    """A non-loopback base URL logs a WARNING unless the operator
    acknowledged the tunnel via WILLOW_MCP_TUNNEL_ACKNOWLEDGED=1.

    Per the task: do NOT add a runtime flag; the security note is what
    matters. This is that note.
    """
    monkeypatch.delenv("WILLOW_MCP_TUNNEL_ACKNOWLEDGED", raising=False)
    fired = mcp_local._warn_public_tunnel_if_unacknowledged("https://grove.example.com")
    assert fired is True
    err = capsys.readouterr().err
    assert "WARNING" in err
    assert "non-loopback" in err
    assert "WILLOW_MCP_TUNNEL_ACKNOWLEDGED" in err


def test_public_tunnel_warning_silent_when_acknowledged(monkeypatch, capsys):
    monkeypatch.setenv("WILLOW_MCP_TUNNEL_ACKNOWLEDGED", "1")
    fired = mcp_local._warn_public_tunnel_if_unacknowledged("https://grove.example.com")
    assert fired is False
    assert "WARNING" not in capsys.readouterr().err


def test_public_tunnel_warning_silent_on_loopback(monkeypatch, capsys):
    monkeypatch.delenv("WILLOW_MCP_TUNNEL_ACKNOWLEDGED", raising=False)
    assert mcp_local._warn_public_tunnel_if_unacknowledged("http://127.0.0.1:8765") is False
    assert mcp_local._warn_public_tunnel_if_unacknowledged("http://localhost:8765") is False
    assert capsys.readouterr().err == ""
