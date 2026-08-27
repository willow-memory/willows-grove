# tests/test_mcp_local_oauth_hardening.py — Loki v0.9 audit #14 + #15 pins
# b17: TMOH  ΔΣ=42
#
# INVARIANTS.md §7. Two paired hardenings from the PR 12 Loki audit:
#
#   #14 — grove/mcp_local.py's `_gate` / `_resolve_serve_identity` were dead
#         code: zero call sites. The actual per-request refusal in serve
#         mode is enforced by `AuthSettings(required_scopes=REQUIRED_SCOPES)`
#         + `_require_scope` on writes, wired through the SDK's auth
#         middleware. The pretenders are deleted so the tree does not
#         claim an enforcement point that isn't wired.
#
#   #15 — `_remote_is_loopback` trusted the raw TCP peer, which is
#         127.0.0.1 for any same-box reverse proxy (Pangolin, nginx,
#         cloudflared, tailscale) that forwards to 127.0.0.1:8765. That
#         means the "loopback POST really means loopback" clause of
#         INVARIANTS.md §7 was silently voided by any such proxy. Fix:
#         consult X-Forwarded-For IFF the operator opts in via
#         `GROVE_MCP_TRUSTED_PROXIES=<comma,ips>`. Default-closed —
#         behavior unchanged when the env var is unset. Non-loopback
#         forwarded hop is refused, and the refusal is logged once.
from __future__ import annotations

import os
import re
import sys
import tempfile
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

MCP_LOCAL_PATH = REPO / "grove" / "mcp_local.py"


# ── #14: `_gate` + `_resolve_serve_identity` are dead code, deleted ────────

def test_gate_dead_code_removed():
    """Loki finding #14 (PR 12) — `_gate` has zero call sites in
    grove/mcp_local.py. Actual serve-mode refusal is done by
    `AuthSettings.required_scopes` + `_require_scope`. Delete the
    pretender rather than pretend it enforces anything.

    Greps the source rather than the imported module: the module's
    absence of the attribute is downstream of the definition being
    gone, but the definition is the durable statement.
    """
    src = MCP_LOCAL_PATH.read_text()
    assert not re.search(r"^def _gate\(", src, flags=re.M), (
        "_gate is dead code (INVARIANTS.md §7 refusal is via "
        "AuthSettings.required_scopes + _require_scope). Delete it."
    )
    assert not re.search(r"^def _resolve_serve_identity\(", src, flags=re.M), (
        "_resolve_serve_identity is dead code — the seam _gate consulted "
        "and _gate is gone. Delete it."
    )


# ── #15: `_remote_is_loopback` is proxy-aware (opt-in) ────────────────

# Serve mode has to be active for `_remote_is_loopback` to be defined
# (it lives inside `if _SERVE_MODE and _auth_provider is not None:`),
# so this test file imports the module with argv patched and HOME on a
# fresh temp dir — the pattern test_grove_approval_page.py uses.

_saved_argv = list(sys.argv)
_saved_env = {
    k: os.environ.get(k)
    for k in (
        "GROVE_MCP_URL",
        "HOME",
        "GROVE_MCP_ALLOW_DYNAMIC_REGISTRATION",
        "WILLOW_MCP_TUNNEL_ACKNOWLEDGED",
        "GROVE_MCP_TRUSTED_PROXIES",
    )
}
_tmp_home = tempfile.mkdtemp(prefix="grove-oauth-hardening-test-home-")
_saved_module = sys.modules.get("grove.mcp_local")

sys.argv = ["mcp_local", "--serve"]
os.environ["GROVE_MCP_URL"] = "http://127.0.0.1:8765"
os.environ["HOME"] = _tmp_home
os.environ["GROVE_MCP_ALLOW_DYNAMIC_REGISTRATION"] = "1"
os.environ["WILLOW_MCP_TUNNEL_ACKNOWLEDGED"] = "1"
os.environ.pop("GROVE_MCP_TRUSTED_PROXIES", None)

try:
    sys.modules.pop("grove.mcp_local", None)
    import grove.mcp_local as mcp_local  # noqa: E402
finally:
    sys.argv = _saved_argv
    for _k, _v in _saved_env.items():
        if _v is None:
            os.environ.pop(_k, None)
        else:
            os.environ[_k] = _v


def teardown_module(_module):
    """Restore whatever grove.mcp_local was in sys.modules before this
    file loaded, so downstream tests in the same run see the module in
    the same import state (stdio or serve) they expected."""
    if _saved_module is not None:
        sys.modules["grove.mcp_local"] = _saved_module
    else:
        sys.modules.pop("grove.mcp_local", None)


def test_gate_dead_code_removed_module_surface():
    """Belt-and-braces: the imported module also no longer exposes the
    deleted names. A grep-clean source that still gets patched at import
    time back into the module would defeat the intent, so pin both."""
    assert not hasattr(mcp_local, "_gate"), (
        "grove.mcp_local._gate should be gone (Loki #14)"
    )
    assert not hasattr(mcp_local, "_resolve_serve_identity"), (
        "grove.mcp_local._resolve_serve_identity should be gone (Loki #14)"
    )


class _MockClient:
    def __init__(self, host: str):
        self.host = host


class _MockRequest:
    """Duck-typed against `_remote_is_loopback`'s reads: `.client.host`
    and `.headers.get("x-forwarded-for", ...)`. A dict is not exactly
    Starlette's case-insensitive Headers, but the fix reads with the
    canonical lowercase key so a plain dict is enough."""

    def __init__(self, client_host, headers=None):
        self.client = _MockClient(client_host) if client_host else None
        self.headers = headers or {}


def test_remote_is_loopback_default_unchanged(monkeypatch):
    """Without GROVE_MCP_TRUSTED_PROXIES set, behavior is unchanged —
    the raw TCP peer decides, XFF is never consulted. This preserves
    the invariant for deployments that do not run a reverse proxy."""
    monkeypatch.delenv("GROVE_MCP_TRUSTED_PROXIES", raising=False)
    req = _MockRequest("127.0.0.1", headers={"x-forwarded-for": "8.8.8.8"})
    assert mcp_local._remote_is_loopback(req) is True


def test_remote_is_loopback_proxy_aware_refuses_forwarded_public(monkeypatch, capsys):
    """Loki finding #15 (PR 12) — with GROVE_MCP_TRUSTED_PROXIES=127.0.0.1,
    the approval-POST check consults X-Forwarded-For as the effective
    peer. A reverse proxy on the loopback interface forwarding an
    off-box POST (XFF=8.8.8.8) is refused, and the refusal is logged
    once. This is the test that must fail on unfixed code (where the
    raw client.host=127.0.0.1 alone would let the POST through)."""
    monkeypatch.setenv("GROVE_MCP_TRUSTED_PROXIES", "127.0.0.1")
    # Reset log-once so the WARNING is emitted for this test.
    if hasattr(mcp_local, "_forwarded_refusal_logged"):
        monkeypatch.setattr(mcp_local, "_forwarded_refusal_logged", False)

    req = _MockRequest("127.0.0.1", headers={"x-forwarded-for": "8.8.8.8"})
    assert mcp_local._remote_is_loopback(req) is False

    err = capsys.readouterr().err
    assert "WARNING" in err
    assert "8.8.8.8" in err


def test_remote_is_loopback_untrusted_proxy_no_xff_consultation(monkeypatch):
    """When client.host is NOT in the trusted set, XFF is NOT consulted;
    the raw peer decides. An off-box peer that spoofs XFF=127.0.0.1
    does not gain loopback status."""
    monkeypatch.setenv("GROVE_MCP_TRUSTED_PROXIES", "127.0.0.1")
    req = _MockRequest("203.0.113.10", headers={"x-forwarded-for": "127.0.0.1"})
    assert mcp_local._remote_is_loopback(req) is False


def test_remote_is_loopback_trusted_proxy_no_xff_stays_loopback(monkeypatch):
    """A trusted-proxy peer with no X-Forwarded-For (a genuinely local
    POST that reached the app through the loopback interface without a
    proxy in front) still passes the loopback check."""
    monkeypatch.setenv("GROVE_MCP_TRUSTED_PROXIES", "127.0.0.1")
    req = _MockRequest("127.0.0.1", headers={})
    assert mcp_local._remote_is_loopback(req) is True


def test_remote_is_loopback_forwarded_loopback_stays_loopback(monkeypatch):
    """A trusted-proxy peer forwarding XFF=127.0.0.1 (a local client
    reaching the app through the proxy) is still loopback under the
    effective-peer rule — the effective host resolves to a loopback
    name and passes."""
    monkeypatch.setenv("GROVE_MCP_TRUSTED_PROXIES", "127.0.0.1")
    req = _MockRequest("127.0.0.1", headers={"x-forwarded-for": "127.0.0.1"})
    assert mcp_local._remote_is_loopback(req) is True
