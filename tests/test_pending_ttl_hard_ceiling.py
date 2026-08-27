# tests/test_pending_ttl_hard_ceiling.py — grove/mcp_auth.py: stash_pending must
# not reset the 5-minute pending-approval clock on re-stash.
#
# INVARIANTS.md §7: "Pending approvals expire in 5 minutes. The one-shot key
# becomes unusable and no code can be issued against it." The grove_approve
# GET branch (grove/mcp_local.py) re-stashes the same pending key so a
# subsequent POST from the same page load can still find it. That re-stash
# must not push expires_at out again — otherwise a browser tab left open on
# the approval page (or any repeated GET) keeps the one-shot key alive past
# the 5-minute ceiling the invariant promises.
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from grove import mcp_auth  # noqa: E402
from mcp.server.auth.provider import AuthorizationParams  # noqa: E402
from mcp.shared.auth import OAuthClientInformationFull  # noqa: E402

BASE_URL = "https://grove.example.test"


def _client() -> OAuthClientInformationFull:
    return OAuthClientInformationFull(
        client_id="client-1",
        client_name="Test Client",
        redirect_uris=["https://claude.ai/api/mcp/auth_callback"],
        grant_types=["authorization_code", "refresh_token"],
        scope="grove",
    )


def _params() -> AuthorizationParams:
    return AuthorizationParams(
        state="opaque-state",
        scopes=["grove"],
        code_challenge="E9Melhoa2OwvFrEMTJguCHaoeK1t8URWbuGJSstw-cM",
        redirect_uri="https://claude.ai/api/mcp/auth_callback",
        redirect_uri_provided_explicitly=True,
    )


def _provider(tmp_path: Path) -> mcp_auth.GroveOAuthProvider:
    return mcp_auth.GroveOAuthProvider(
        token_path=tmp_path / "grove_mcp_token",
        base_url=BASE_URL,
    )


def test_restash_preserves_original_expiry_not_a_rolling_window(tmp_path, monkeypatch):
    """Re-stashing an existing pending key must keep the ORIGINAL expires_at.

    t0: stash. t0+3min: re-stash (the grove_approve GET path, called again
    e.g. by a second GET on the same link). The effective expiry must still
    be t0+5min — not (t0+3min)+5min = t0+8min.

    On the unfixed code, stash_pending unconditionally recomputes
    expires_at = now + _PENDING_TTL on every call, so the re-stash pushes
    the ceiling out and the key is still usable at t0+5min+1s, which this
    test asserts must NOT be the case.
    """
    provider = _provider(tmp_path)
    client = _client()
    params = _params()
    key = "pending-key-0123456789abcdef"

    t0 = 1_700_000_000.0
    monkeypatch.setattr(mcp_auth.time, "time", lambda: t0)
    provider.stash_pending(key, client, params)

    # Re-stash 3 minutes later, well inside the original 5-minute window —
    # this mirrors grove_approve's GET branch calling stash_pending again
    # after popping the entry to inspect it.
    t_restash = t0 + 180
    monkeypatch.setattr(mcp_auth.time, "time", lambda: t_restash)
    provider.stash_pending(key, client, params)

    # Sanity: still alive just under the ORIGINAL deadline (t0 + 300).
    monkeypatch.setattr(mcp_auth.time, "time", lambda: t0 + mcp_auth._PENDING_TTL - 1)
    assert provider.pop_pending(key) is not None, (
        "key should still be usable just under the original 5-minute ceiling"
    )

    # Rebuild the same sequence (pop_pending above consumed the entry) to
    # check the hard ceiling itself.
    monkeypatch.setattr(mcp_auth.time, "time", lambda: t0)
    provider.stash_pending(key, client, params)
    monkeypatch.setattr(mcp_auth.time, "time", lambda: t_restash)
    provider.stash_pending(key, client, params)

    # Just past the ORIGINAL deadline (t0 + 300) — but still well inside what
    # a reset-on-restash implementation would compute as
    # (t_restash + 300) = t0 + 480. The hard ceiling must win: the key must
    # be dead here regardless of the intervening re-stash.
    monkeypatch.setattr(mcp_auth.time, "time", lambda: t0 + mcp_auth._PENDING_TTL + 1)
    assert provider.pop_pending(key) is None, (
        "pending key must expire at the ORIGINAL t0+5min; re-stash must not "
        "extend it to t_restash+5min"
    )
