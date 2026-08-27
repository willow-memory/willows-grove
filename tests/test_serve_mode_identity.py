# tests/test_serve_mode_identity.py — serve-mode module surface (PR 6, PR 12)
# b17: TSMI  ΔΣ=42
#
# PR 6 introduced `_detect_serve_mode(argv=...)` as an injectable seam so the
# serve branch of the module could be exercised without a subprocess. It also
# added `_resolve_serve_identity` + `_gate` as an "identity gate" seam — with
# zero call sites, since actual per-request refusal in serve mode is enforced
# by `AuthSettings(required_scopes=REQUIRED_SCOPES)` + `_require_scope`. Loki
# v0.9 audit finding #14 (PR 12) deleted those pretenders; the file is left
# to pin what remains real: the injectable serve-mode detection, and the
# tunnel-warning behavior tied to WILLOW_MCP_TUNNEL_ACKNOWLEDGED. INVARIANTS.md §7.
from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

mcp_local = pytest.importorskip("grove.mcp_local")


# ── _detect_serve_mode / _SERVE_MODE injectability ─────────────────────────


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


# ── The public-tunnel warning ────────────────────────────────────────


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
