# tests/test_mcp_auth.py — grove/mcp_auth.py: token-state durability and the
# authorization decision.
#
# There were no tests over this module. The two things pinned here are the two
# that fail silently: a corrupt token file that reads back as "no clients at
# all", and an /authorize that hands out tokens without asking anyone.
import asyncio
import json
import os
import stat
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from grove.mcp_auth import (  # noqa: E402
    GroveOAuthProvider,
    TokenStateError,
)
from mcp.server.auth.provider import AuthorizationParams  # noqa: E402
from mcp.shared.auth import OAuthClientInformationFull  # noqa: E402

BASE_URL = "https://grove.example.test"


def _client(client_id: str = "client-1") -> OAuthClientInformationFull:
    return OAuthClientInformationFull(
        client_id=client_id,
        client_name="Test Client",
        redirect_uris=["https://claude.ai/api/mcp/auth_callback"],
        grant_types=["authorization_code", "refresh_token"],
        scope="grove",
    )


def _params(state: str | None = "opaque-state") -> AuthorizationParams:
    return AuthorizationParams(
        state=state,
        scopes=["grove"],
        code_challenge="E9Melhoa2OwvFrEMTJguCHaoeK1t8URWbuGJSstw-cM",
        redirect_uri="https://claude.ai/api/mcp/auth_callback",
        redirect_uri_provided_explicitly=True,
    )


def _provider(tmp_path: Path) -> GroveOAuthProvider:
    return GroveOAuthProvider(
        token_path=tmp_path / "grove_mcp_token",
        base_url=BASE_URL,
    )


def _mode(path: Path) -> int:
    return stat.S_IMODE(path.stat().st_mode)


# ── Corrupt token state must be loud ─────────────────────────────────────────


@pytest.mark.parametrize(
    "body",
    [
        pytest.param('{"clients": {"a": {}}, "access_tok', id="truncated-mid-write"),
        pytest.param("", id="empty-file"),
        pytest.param("not json at all", id="garbage"),
        pytest.param("[]", id="json-but-not-an-object"),
        pytest.param('{"clients": {}}', id="missing-sections"),
        pytest.param('{"clients": [], "access_tokens": {}, "refresh_tokens": {}}', id="section-wrong-type"),
    ],
)
def test_corrupt_token_file_raises_instead_of_yielding_empty_state(tmp_path, body):
    """A corrupt token file must not read back as 'no clients registered'.

    That is the silent-deregistration path: every client disappears, and the
    very next _save_state() writes the loss to disk permanently.
    """
    token_path = tmp_path / "grove_mcp_token"
    token_path.write_text(body)

    with pytest.raises(TokenStateError) as excinfo:
        GroveOAuthProvider(token_path=token_path, base_url=BASE_URL)

    # The operator has to be able to act on it: name the file, say what to do.
    message = str(excinfo.value)
    assert str(token_path) in message
    assert "aside" in message or "delete" in message

    # And the corrupt bytes must still be on disk — not silently replaced.
    assert token_path.read_text() == body


def test_missing_token_file_is_not_an_error(tmp_path):
    """Absent is different from corrupt: a first run starts empty, quietly."""
    provider = _provider(tmp_path)
    assert provider._state == {"clients": {}, "access_tokens": {}, "refresh_tokens": {}}


def test_valid_token_file_round_trips(tmp_path):
    provider = _provider(tmp_path)
    asyncio.run(provider.register_client(_client()))

    reloaded = _provider(tmp_path)
    assert "client-1" in reloaded._state["clients"]
    assert asyncio.run(reloaded.get_client("client-1")) is not None


# ── Token file permissions ───────────────────────────────────────────────────


def test_token_file_is_0600_on_fresh_create(tmp_path):
    """The file holds live bearer tokens; it must never be group/world readable."""
    token_path = tmp_path / "nested" / "grove_mcp_token"
    provider = GroveOAuthProvider(token_path=token_path, base_url=BASE_URL)
    asyncio.run(provider.register_client(_client()))

    assert token_path.exists()
    assert _mode(token_path) == 0o600, f"expected 0600, got {_mode(token_path):#o}"


def test_token_file_is_0600_after_overwriting_a_wide_open_file(tmp_path):
    """Overwriting must narrow an existing wide mode, not inherit it.

    An in-place write to a pre-existing 0644 file leaves it 0644 forever.
    """
    token_path = tmp_path / "grove_mcp_token"
    token_path.write_text(json.dumps({"clients": {}, "access_tokens": {}, "refresh_tokens": {}}))
    os.chmod(token_path, 0o644)
    assert _mode(token_path) == 0o644

    provider = GroveOAuthProvider(token_path=token_path, base_url=BASE_URL)
    asyncio.run(provider.register_client(_client()))

    assert _mode(token_path) == 0o600, f"expected 0600, got {_mode(token_path):#o}"


def test_token_file_is_0600_under_a_permissive_umask(tmp_path):
    """0600 must come from the create mode, not from luck about the umask."""
    token_path = tmp_path / "grove_mcp_token"
    old = os.umask(0o000)
    try:
        provider = GroveOAuthProvider(token_path=token_path, base_url=BASE_URL)
        asyncio.run(provider.register_client(_client()))
    finally:
        os.umask(old)

    assert _mode(token_path) == 0o600, f"expected 0600, got {_mode(token_path):#o}"


def test_save_replaces_the_file_rather_than_writing_through_it(tmp_path):
    """Atomicity, stated as something observable without crashing mid-write.

    An in-place `write_text` truncates the existing file and writes into the
    same inode, so a reader holding it — or a crash — sees a half file. A
    tmp-then-`os.replace` install puts a *new* inode in place, and anything
    already holding the old one still sees the complete previous state.
    """
    token_path = tmp_path / "grove_mcp_token"
    provider = _provider(tmp_path)
    asyncio.run(provider.register_client(_client()))

    first_inode = token_path.stat().st_ino
    with token_path.open() as held:
        asyncio.run(provider.register_client(_client("client-2")))

        assert token_path.stat().st_ino != first_inode, (
            "token file was written through in place — a crash mid-write "
            "truncates it and _load_state has nothing to recover"
        )
        # The old inode is still whole and still parses.
        previous = json.loads(held.read())
        assert set(previous["clients"]) == {"client-1"}

    # And the installed file is the new state, with no temp files left over.
    assert set(json.loads(token_path.read_text())["clients"]) == {"client-1", "client-2"}
    assert [p.name for p in tmp_path.iterdir()] == ["grove_mcp_token"]


def test_failed_save_leaves_the_previous_state_installed(tmp_path):
    """A save that cannot complete must not destroy what was already there."""
    token_path = tmp_path / "grove_mcp_token"
    provider = _provider(tmp_path)
    asyncio.run(provider.register_client(_client()))
    good = token_path.read_text()

    provider._state["clients"]["bad"] = {"unserializable": object()}
    with pytest.raises(TypeError):
        provider._save_state()

    assert token_path.read_text() == good
    assert [p.name for p in tmp_path.iterdir()] == ["grove_mcp_token"]


# ── The authorization decision ───────────────────────────────────────────────


def test_authorize_does_not_issue_a_code_by_default(tmp_path):
    """The pin against silently reverting to unconditional auto-approve.

    Default posture: /authorize must send the browser to the local approval
    page and must NOT mint an authorization code or redirect to the client's
    callback. If this ever goes back to auto-approve, this fails.
    """
    provider = _provider(tmp_path)
    client, params = _client(), _params()

    redirect = asyncio.run(provider.authorize(client, params))

    assert redirect.startswith(f"{BASE_URL}/grove-approve?pending=")
    # Nothing that looks like a grant went back to the client.
    assert "claude.ai" not in redirect
    assert "code=" not in redirect
    # And no code exists yet — a human has not decided.
    assert provider._codes == {}


def test_authorize_is_independent_of_ambient_env(tmp_path, monkeypatch):
    """No env var toggles the authorize() path anymore — PR 6 removed the
    GROVE_MCP_AUTO_APPROVE escape hatch entirely. Setting it must not
    resurrect the behavior. Per INVARIANTS.md §5."""
    monkeypatch.setenv("GROVE_MCP_AUTO_APPROVE", "1")
    provider = _provider(tmp_path)

    redirect = asyncio.run(provider.authorize(_client(), _params()))
    assert "/grove-approve?pending=" in redirect
    assert provider._codes == {}


def test_auto_approve_constructor_arg_no_longer_exists(tmp_path):
    """The `auto_approve` constructor arg was removed in PR 6. If someone
    re-adds it as a knob, this fails — INVARIANTS.md §5."""
    with pytest.raises(TypeError):
        GroveOAuthProvider(
            token_path=tmp_path / "grove_mcp_token",
            base_url=BASE_URL,
            auto_approve=True,  # type: ignore[call-arg]
        )


def test_access_ttl_is_bounded_for_operator_seat():
    """Access tokens live for the operator seat's horizon, not 30 days.
    INVARIANTS.md §5 (bounded TTL suitable for the operator seat)."""
    import grove.mcp_auth as mcp_auth
    # 24 hours — bounded, defensible. Not 30 days.
    assert mcp_auth._ACCESS_TTL == 24 * 3600
    assert mcp_auth._PENDING_TTL == 300  # 5 minutes for the approval click


def test_pending_request_is_parked_and_claimable_once(tmp_path):
    """The approval page's half of the flow: pop the parked request, issue a
    code, and make the one-shot key unusable afterwards."""
    provider = _provider(tmp_path)
    client, params = _client(), _params()

    redirect = asyncio.run(provider.authorize(client, params))
    key = redirect.split("pending=", 1)[1]

    entry = provider.pop_pending(key)
    assert entry is not None
    got_client, got_params = entry
    assert got_client.client_id == client.client_id
    assert str(got_params.redirect_uri) == str(params.redirect_uri)

    code = provider.issue_code(got_client, got_params)
    assert code in provider._codes

    # Replay of the same approval link gets nothing.
    assert provider.pop_pending(key) is None


def test_pending_key_is_unguessable_and_unique(tmp_path):
    provider = _provider(tmp_path)
    keys = {
        asyncio.run(provider.authorize(_client(), _params())).split("pending=", 1)[1]
        for _ in range(10)
    }
    assert len(keys) == 10
    assert all(len(k) >= 40 for k in keys)


def test_unknown_pending_key_yields_nothing(tmp_path):
    provider = _provider(tmp_path)
    assert provider.pop_pending("not-a-real-key") is None
    assert provider.pop_pending("") is None


def test_pending_requests_expire(tmp_path, monkeypatch):
    provider = _provider(tmp_path)
    redirect = asyncio.run(provider.authorize(_client(), _params()))
    key = redirect.split("pending=", 1)[1]

    import grove.mcp_auth as mcp_auth

    real_time = mcp_auth.time.time
    monkeypatch.setattr(mcp_auth.time, "time", lambda: real_time() + mcp_auth._PENDING_TTL + 1)
    assert provider.pop_pending(key) is None


# ── Code exchange still behaves ──────────────────────────────────────────────


def test_issued_code_exchanges_for_a_token_and_is_single_use(tmp_path):
    provider = _provider(tmp_path)
    client, params = _client(), _params()
    asyncio.run(provider.register_client(client))

    redirect = asyncio.run(provider.authorize(client, params))
    key = redirect.split("pending=", 1)[1]
    got_client, got_params = provider.pop_pending(key)
    code_str = provider.issue_code(got_client, got_params)

    auth_code = asyncio.run(provider.load_authorization_code(client, code_str))
    assert auth_code is not None

    token = asyncio.run(provider.exchange_authorization_code(client, auth_code))
    assert token.access_token
    assert asyncio.run(provider.load_access_token(token.access_token)) is not None

    # Code is consumed.
    assert asyncio.run(provider.load_authorization_code(client, code_str)) is None


def test_code_is_not_usable_by_a_different_client(tmp_path):
    provider = _provider(tmp_path)
    client, params = _client(), _params()
    code_str = provider.issue_code(client, params)
    assert asyncio.run(provider.load_authorization_code(_client("other"), code_str)) is None
