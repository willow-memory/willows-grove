# tests/test_mcp_serve_oauth_flow.py — the serve-mode OAuth flow, end to end,
# through the real Starlette app.
#
# The unit tests in test_mcp_auth.py pin GroveOAuthProvider.authorize(). This
# file pins the thing that was actually broken: that /authorize routes to the
# consent page and that the consent page is reachable and issues the code. The
# ~55 lines of approval UI in grove/mcp_local.py were unreachable — no test
# would have noticed, because nothing exercised the assembled app.
import os
import sys
import tempfile
from pathlib import Path
from urllib.parse import parse_qs, urlparse

import pytest

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

BASE_URL = "https://grove.example.test"

# grove.mcp_local decides serve mode at import time from sys.argv and the
# environment, so both have to be in place before the import.
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
_tmp_home = tempfile.mkdtemp(prefix="grove-oauth-test-home-")

sys.argv = ["mcp_local", "--serve"]
os.environ["GROVE_MCP_URL"] = BASE_URL
os.environ["HOME"] = _tmp_home
os.environ.pop("GROVE_MCP_AUTO_APPROVE", None)
# PR 6 (INVARIANTS.md §5): dynamic client registration is off by default.
# This test exercises the full OAuth flow, so enable it here explicitly.
os.environ["GROVE_MCP_ALLOW_DYNAMIC_REGISTRATION"] = "1"
# Silence the tunnel-warning that would otherwise fire for a non-loopback
# BASE_URL — the tests don't care about it, only that the code runs cleanly.
os.environ["WILLOW_MCP_TUNNEL_ACKNOWLEDGED"] = "1"
try:
    # Serve mode is decided at import time, so this file must re-execute the
    # module under --serve rather than accept a copy another test file already
    # imported in stdio mode (which leaves _auth_provider = None). Dropping the
    # cached entry forces a fresh load regardless of collection order.
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
# S256 of the verifier below.
VERIFIER = "dBjftJeZ4CVP-mB92K27uhbUJU1p1r_wW1gFWFOEjXk"
CHALLENGE = "E9Melhoa2OwvFrEMTJguCHaoeK1t8URWbuGJSstw-cM"


@pytest.fixture(scope="module")
def http():
    """One client for the module.

    FastMCP's StreamableHTTPSessionManager refuses to start twice, and the app
    is a module-level singleton, so the app is built and entered once. Per-test
    isolation comes from resetting the provider's state instead.
    """
    # client=("127.0.0.1", ...) so the /grove-approve POST passes the loopback
    # check introduced by PR 6 (INVARIANTS.md §5). Default TestClient host is
    # "testclient", which is deliberately NOT loopback.
    with TestClient(
        mcp_local.mcp.streamable_http_app(),
        follow_redirects=False,
        client=("127.0.0.1", 12345),
    ) as c:
        yield c


@pytest.fixture
def client(http, tmp_path, monkeypatch):
    provider = mcp_local._auth_provider
    monkeypatch.setattr(provider, "_token_path", tmp_path / "grove_mcp_token")
    monkeypatch.setattr(provider, "_state", {"clients": {}, "access_tokens": {}, "refresh_tokens": {}})
    monkeypatch.setattr(provider, "_pending", {})
    monkeypatch.setattr(provider, "_codes", {})
    # `_auto_approve` no longer exists as of PR 6 — the escape hatch is gone
    # (INVARIANTS.md §5). Nothing to reset; approval is always required.
    return http


_secrets: dict[str, str | None] = {}


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
    body = r.json()
    _secrets[body["client_id"]] = body.get("client_secret")
    return body["client_id"]


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


def test_the_approval_page_is_reachable(client):
    """It was dead code. If it stops being routed to, this fails."""
    client_id = _register(client)
    r = _authorize(client, client_id)
    assert r.status_code in (302, 303, 307)

    page = client.get(r.headers["location"])
    assert page.status_code == 200
    assert "Allow Grove access?" in page.text


def test_authorize_does_not_redirect_to_the_client_with_a_code(client):
    """The regression guard: /authorize must not complete the grant itself.

    Pre-fix, the Location header here was the claude.ai callback carrying a
    usable authorization code, with nobody consulted.
    """
    client_id = _register(client)
    r = _authorize(client, client_id)

    location = r.headers["location"]
    assert location.startswith(f"{BASE_URL}/grove-approve?pending="), location
    assert "claude.ai" not in location
    assert "code=" not in location
    assert mcp_local._auth_provider._codes == {}


def test_registration_alone_grants_nothing(client):
    """Open dynamic registration must not by itself be a path to a token."""
    client_id = _register(client)
    _authorize(client, client_id)
    assert mcp_local._auth_provider._state["access_tokens"] == {}
    assert mcp_local._auth_provider._codes == {}


def test_allow_completes_the_flow_and_the_code_exchanges(client):
    client_id = _register(client)
    approve_url = _authorize(client, client_id).headers["location"]
    path_and_query = approve_url[len(BASE_URL):]

    client.get(path_and_query)  # render the page (re-stashes the pending entry)
    posted = client.post(path_and_query, data={"action": "allow"})

    assert posted.status_code == 302
    redirect = posted.headers["location"]
    assert redirect.startswith(CALLBACK)
    query = parse_qs(urlparse(redirect).query)
    assert query["state"] == ["opaque-state"]
    code = query["code"][0]

    form = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": CALLBACK,
        "client_id": client_id,
        "code_verifier": VERIFIER,
    }
    if _secrets.get(client_id):
        form["client_secret"] = _secrets[client_id]
    token = client.post("/token", data=form)
    assert token.status_code == 200, token.text
    body = token.json()
    assert body["token_type"].lower() == "bearer"
    assert body["access_token"]


def test_deny_issues_no_code(client):
    client_id = _register(client)
    approve_url = _authorize(client, client_id).headers["location"]
    path_and_query = approve_url[len(BASE_URL):]

    client.get(path_and_query)
    posted = client.post(path_and_query, data={"action": "deny"})

    assert posted.status_code == 200
    assert "denied" in posted.text.lower()
    assert mcp_local._auth_provider._codes == {}
    assert mcp_local._auth_provider._state["access_tokens"] == {}


def test_ignoring_the_page_issues_no_code(client):
    """Closing the tab is a denial. Nothing is granted by inaction."""
    client_id = _register(client)
    approve_url = _authorize(client, client_id).headers["location"]
    client.get(approve_url[len(BASE_URL):])
    assert mcp_local._auth_provider._codes == {}


def test_approval_link_is_not_replayable(client):
    client_id = _register(client)
    path_and_query = _authorize(client, client_id).headers["location"][len(BASE_URL):]

    client.get(path_and_query)
    first = client.post(path_and_query, data={"action": "allow"})
    assert first.status_code == 302

    second = client.post(path_and_query, data={"action": "allow"})
    assert second.status_code == 200
    assert "denied" in second.text.lower()


def test_unknown_pending_key_is_rejected(client):
    r = client.get("/grove-approve?pending=made-up")
    assert r.status_code == 400
    assert "Invalid or expired" in r.text


def test_mcp_endpoint_still_requires_a_token(client):
    r = client.post(
        "/mcp",
        json={"jsonrpc": "2.0", "id": 1, "method": "tools/list"},
        headers={"Accept": "application/json, text/event-stream"},
    )
    assert r.status_code == 401


def test_approval_page_escapes_registrant_supplied_values(client):
    """client_name and redirect_uri come from whoever registered. The consent
    page is the operator's browser — it must not be an injection surface."""
    r = client.post(
        "/register",
        json={
            "client_name": "<img src=x onerror=alert(1)>",
            "redirect_uris": [CALLBACK],
            "grant_types": ["authorization_code", "refresh_token"],
            "response_types": ["code"],
            "scope": "grove",
            "token_endpoint_auth_method": "client_secret_post",
        },
    )
    assert r.status_code in (200, 201), r.text
    client_id = r.json()["client_id"]

    approve_url = _authorize(client, client_id).headers["location"]
    page = client.get(approve_url[len(BASE_URL):])

    assert "<img src=x" not in page.text
    assert "&lt;img src=x" in page.text
