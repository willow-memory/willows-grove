# tests/test_grove_approval_page.py — the /grove-approve behaviors added in PR 6
# b17: TGAP  ΔΣ=42
#
# Pins the PR-6 tightenings to the OAuth consent flow that CODE_REVIEW.md called
# out (safe-app-willow-grove §"Needs improvement" P0 — "the OAuth consent page
# is dead code"). test_mcp_serve_oauth_flow.py already pinned the base flow
# (approval page reachable, /authorize doesn't auto-issue, replay-protection,
# escape). This file pins the new invariants — INVARIANTS.md §7:
#
#   - `authorize()` redirects to /grove-approve?req_id=… and does NOT issue a code
#   - the approval page renders the requesting client + scope + redirect_uri
#   - Submit-Allow from 127.0.0.1 completes the request and issues the code
#   - Submit from a non-loopback origin is refused
#   - Pending requests expire after 5 min; no code is issuable after
#   - DNS-rebinding protection: an inbound request naming a public DNS Host is refused
from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path
from urllib.parse import parse_qs, urlparse

import pytest

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

BASE_URL = "https://grove.example.test"

_saved_argv = list(sys.argv)
_saved_env = {
    k: os.environ.get(k)
    for k in (
        "GROVE_MCP_URL",
        "HOME",
        "GROVE_MCP_AUTO_APPROVE",
        "GROVE_MCP_ALLOW_DYNAMIC_REGISTRATION",
        "WILLOW_MCP_TUNNEL_ACKNOWLEDGED",
    )
}
_tmp_home = tempfile.mkdtemp(prefix="grove-approve-test-home-")

sys.argv = ["mcp_local", "--serve"]
os.environ["GROVE_MCP_URL"] = BASE_URL
os.environ["HOME"] = _tmp_home
os.environ.pop("GROVE_MCP_AUTO_APPROVE", None)
os.environ["GROVE_MCP_ALLOW_DYNAMIC_REGISTRATION"] = "1"
os.environ["WILLOW_MCP_TUNNEL_ACKNOWLEDGED"] = "1"

try:
    sys.modules.pop("grove.mcp_local", None)
    import grove.mcp_local as mcp_local
finally:
    sys.argv = _saved_argv
    for key, value in _saved_env.items():
        if value is None:
            os.environ.pop(key, None)
        else:
            os.environ[key] = value

starlette_testclient = pytest.importorskip("starlette.testclient")
TestClient = starlette_testclient.TestClient

CALLBACK = "https://claude.ai/api/mcp/auth_callback"
VERIFIER = "dBjftJeZ4CVP-mB92K27uhbUJU1p1r_wW1gFWFOEjXk"
CHALLENGE = "E9Melhoa2OwvFrEMTJguCHaoeK1t8URWbuGJSstw-cM"


@pytest.fixture(scope="module")
def loopback_http():
    """One client per module, its ASGI client tuple set to 127.0.0.1 so the
    approval POST passes the loopback check (INVARIANTS.md §7)."""
    with TestClient(
        mcp_local.mcp.streamable_http_app(),
        follow_redirects=False,
        client=("127.0.0.1", 12345),
    ) as c:
        yield c


@pytest.fixture(scope="module")
def public_http():
    """Same app, but the ASGI client tuple is a public-looking address —
    used to prove the loopback check refuses a POST from off-box."""
    with TestClient(
        mcp_local.mcp.streamable_http_app(),
        follow_redirects=False,
        client=("203.0.113.10", 54321),
    ) as c:
        yield c


@pytest.fixture
def _reset_provider(monkeypatch):
    provider = mcp_local._auth_provider
    monkeypatch.setattr(provider, "_state", {"clients": {}, "access_tokens": {}, "refresh_tokens": {}})
    monkeypatch.setattr(provider, "_pending", {})
    monkeypatch.setattr(provider, "_codes", {})
    return provider


def _register(client) -> str:
    r = client.post(
        "/register",
        json={
            "client_name": "Test Connector",
            "redirect_uris": [CALLBACK],
            "grant_types": ["authorization_code", "refresh_token"],
            "response_types": ["code"],
            "scope": "grove",
            "token_endpoint_auth_method": "client_secret_post",
        },
    )
    assert r.status_code in (200, 201), r.text
    return r.json()["client_id"]


def _authorize(client, client_id: str):
    return client.get(
        "/authorize",
        params={
            "client_id": client_id,
            "redirect_uri": CALLBACK,
            "response_type": "code",
            "code_challenge": CHALLENGE,
            "code_challenge_method": "S256",
            "state": "opaque-state",
            "scope": "grove",
        },
    )


# ── /authorize redirects to the approval page, never a code ──────────────────


def test_authorize_redirects_to_approval_page_never_a_code(loopback_http, _reset_provider):
    """The regression guard for CODE_REVIEW.md's P0. INVARIANTS.md §7."""
    client_id = _register(loopback_http)
    r = _authorize(loopback_http, client_id)

    assert r.status_code in (302, 303, 307)
    location = r.headers["location"]
    assert location.startswith(f"{BASE_URL}/grove-approve?pending="), location
    assert "code=" not in location
    assert "claude.ai" not in location
    assert _reset_provider._codes == {}
    assert _reset_provider._state["access_tokens"] == {}


# ── The rendered page shows client, scope, redirect_uri ──────────────────────


def test_approval_page_renders_client_scope_redirect(loopback_http, _reset_provider):
    """Per the PR-6 spec: the approval page presents the requesting client +
    scope + expiry to the operator."""
    client_id = _register(loopback_http)
    approve_url = _authorize(loopback_http, client_id).headers["location"]
    path_and_query = approve_url[len(BASE_URL):]

    page = loopback_http.get(path_and_query)
    assert page.status_code == 200

    body = page.text
    assert "Test Connector" in body        # client name
    assert "grove" in body                 # scope
    assert CALLBACK in body                # redirect target the code goes to
    assert "Allow" in body and "Deny" in body


# ── Submit-Allow from 127.0.0.1 completes the flow ──────────────────────────


def test_loopback_submit_allow_issues_the_code(loopback_http, _reset_provider):
    client_id = _register(loopback_http)
    approve_url = _authorize(loopback_http, client_id).headers["location"]
    path_and_query = approve_url[len(BASE_URL):]

    loopback_http.get(path_and_query)                      # render
    posted = loopback_http.post(path_and_query, data={"action": "allow"})

    assert posted.status_code == 302
    redirect = posted.headers["location"]
    assert redirect.startswith(CALLBACK)
    q = parse_qs(urlparse(redirect).query)
    assert q["state"] == ["opaque-state"]
    assert q["code"][0] in _reset_provider._codes


# ── Submit from a non-loopback origin is refused ────────────────────────────


def test_non_loopback_submit_is_refused(public_http, loopback_http, _reset_provider):
    """The loopback check added in PR 6 (INVARIANTS.md §7): the POST that
    completes the grant must originate from 127.0.0.1 / ::1 / localhost. A
    tunnel that forwards a public IP as the peer is refused, and no code is
    issued.
    """
    # Register + park via the loopback client (so the pending key exists).
    client_id = _register(loopback_http)
    approve_url = _authorize(loopback_http, client_id).headers["location"]
    path_and_query = approve_url[len(BASE_URL):]
    loopback_http.get(path_and_query)  # re-stash pending

    # Now POST from a public-looking peer.
    posted = public_http.post(path_and_query, data={"action": "allow"})
    assert posted.status_code == 403
    assert "local host" in posted.text.lower() or "loopback" in posted.text.lower()

    # And no code was minted.
    assert _reset_provider._codes == {}
    assert _reset_provider._state["access_tokens"] == {}


# ── Timeout: pending requests expire after 5 min ────────────────────────────


def test_pending_expires_after_5_min_no_code_issuable(loopback_http, _reset_provider, monkeypatch):
    """PR 6 dropped _PENDING_TTL to 5 minutes and _ACCESS_TTL to 24 hours
    (INVARIANTS.md §7). After the pending window closes, the parked entry is
    gone and no code can be issued for it — replaying the approval URL yields
    "Invalid or expired"."""
    import grove.mcp_auth as mcp_auth
    assert mcp_auth._PENDING_TTL == 300  # the boundary this test relies on

    client_id = _register(loopback_http)
    approve_url = _authorize(loopback_http, client_id).headers["location"]
    path_and_query = approve_url[len(BASE_URL):]

    # Jump the provider's clock past the pending TTL.
    real_time = mcp_auth.time.time
    monkeypatch.setattr(mcp_auth.time, "time", lambda: real_time() + mcp_auth._PENDING_TTL + 1)

    # GET now falls through the "invalid or expired" branch.
    page = loopback_http.get(path_and_query)
    assert page.status_code == 400
    assert "Invalid or expired" in page.text

    # And POST still refuses; nothing was issued.
    posted = loopback_http.post(path_and_query, data={"action": "allow"})
    assert posted.status_code == 200
    assert "denied" in posted.text.lower()
    assert _reset_provider._codes == {}


# ── DNS-rebinding protection: Host header naming a public DNS name refused ──


def test_dns_rebinding_public_host_header_refused(loopback_http, _reset_provider):
    """PR 6 removed the ngrok carve-out (CODE_REVIEW.md P0 — "_transport_security()
    disables DNS-rebinding protection for https:// base URLs"). Even with a
    grove.example.test tunnel configured, an inbound Host header naming a
    third-party public DNS is not on the transport allowlist — the transport
    layer would refuse it before /grove-approve ran.

    We assert the allowlist itself: an attacker-supplied Host is not present,
    and DNS-rebinding protection is unconditionally enabled.
    """
    from mcp.server.transport_security import TransportSecuritySettings

    settings = mcp_local._transport_security()
    assert isinstance(settings, TransportSecuritySettings)
    assert settings.enable_dns_rebinding_protection is True

    # The allowlist covers loopback and the operator-configured tunnel host.
    hosts = settings.allowed_hosts
    assert any(h.startswith("127.0.0.1") for h in hosts)
    # And it does NOT open on any-Host — a random public DNS name is absent.
    assert "attacker.example.org" not in hosts
    assert "*" not in hosts

    # Origins likewise never widen to "*".
    origins = settings.allowed_origins
    assert "*" not in origins
    assert "http://attacker.example.org" not in origins
    assert "https://attacker.example.org" not in origins


# ── Dynamic client registration gated behind the operator opt-in ─────────────


def test_dynamic_registration_can_be_disabled(monkeypatch, tmp_path):
    """PR 6: client_registration.enabled defaults to False; enabling requires
    GROVE_MCP_ALLOW_DYNAMIC_REGISTRATION=1. This test rebuilds the module
    without the opt-in and asserts the SDK's ClientRegistrationOptions was
    constructed with enabled=False.
    """
    # Capture the exact module object currently registered — other test files
    # (test_transport_security.py) hold a reference to it and call
    # `importlib.reload(mcp_local)`, which requires the module in sys.modules
    # to be that same object. Restore it verbatim after this test.
    saved_module = sys.modules.get("grove.mcp_local")
    saved_argv = list(sys.argv)
    saved_env = {k: os.environ.get(k) for k in ("GROVE_MCP_ALLOW_DYNAMIC_REGISTRATION", "HOME", "GROVE_MCP_URL")}
    try:
        sys.argv = ["mcp_local", "--serve"]
        os.environ.pop("GROVE_MCP_ALLOW_DYNAMIC_REGISTRATION", None)
        os.environ["HOME"] = str(tmp_path)
        os.environ["GROVE_MCP_URL"] = "http://127.0.0.1:8765"
        sys.modules.pop("grove.mcp_local", None)
        import grove.mcp_local as fresh
        assert fresh._ALLOW_DYNAMIC_REG is False
    finally:
        sys.argv = saved_argv
        for k, v in saved_env.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v
        # Put the ORIGINAL module back into sys.modules so cross-file
        # `importlib.reload` calls still see the same object they captured.
        if saved_module is not None:
            sys.modules["grove.mcp_local"] = saved_module
        else:
            sys.modules.pop("grove.mcp_local", None)
