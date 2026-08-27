# grove/mcp_auth.py — Grove OAuth 2.0 PKCE provider (single-user)
# b17: GRMOAUTH  ΔΣ=42
"""
Single-user OAuth 2.0 provider for `grove.mcp_local --serve`.

Authorization is never automatic. Per INVARIANTS.md §7 (consent flows are
real, not automatic), /authorize parks the request in memory and redirects
the browser to <base_url>/grove-approve?pending=<key>. The human at that
browser clicks Allow (or Deny) — an authorization code exists only after a
human clicked. The client then exchanges the code (with its PKCE verifier)
for access + refresh tokens.

There is no unattended-approve path. The prior GROVE_MCP_AUTO_APPROVE env
opt-in was removed in PR 6: an auto-approve escape hatch on a listener the
serve mode encourages to be tunnelled is the same open dispenser it used to
be at /authorize itself, just with an env-var next to it. If a specific
deployment needs unattended auth, it goes through a different mechanism —
not a knob on this provider.

PKCE (S256) is enforced by the MCP SDK's token handler, not by this module.
PKCE binds a code to the client that requested it; it does not decide
*whether* a requester should be authorized. The approval click is what
does that.

Access tokens live for 24 hours — bounded for the operator seat, not the
30 days a shared account might carry. Refresh tokens keep their longer
horizon (a client that reconnects the next day should not have to walk the
consent page again for a benign session gap), but the access token itself
is the credential that gets replayed, so it is the one that has to expire.
See INVARIANTS.md §7.

Pending approvals and issued codes are in-memory (lost on restart, which
just means the client re-auths). Tokens are persisted to token_path so
reconnects work; that file is created 0600 and replaced atomically, and a
corrupt one is a hard error rather than a silent reset — see _load_state.
"""
import json
import os
import secrets
import time
from pathlib import Path
from typing import Any

from mcp.server.auth.provider import (
    AccessToken,
    AuthorizationCode,
    AuthorizationParams,
    RefreshToken,
    construct_redirect_uri,
)
from mcp.shared.auth import OAuthClientInformationFull, OAuthToken

# Access tokens are bounded for the operator seat per INVARIANTS.md §7 —
# not the 30 days the pre-PR-6 value carried. A tunnelled listener replays
# these; a bounded lifetime is what turns "reachable" back into "needs
# consent again". Refresh keeps the multi-day horizon so a benign
# reconnect the next day does not walk the consent page again.
_ACCESS_TTL  = 24 * 3600   # 24 hours — INVARIANTS.md §7
_CODE_TTL    = 300         # 5 minutes
_REFRESH_TTL = 30 * 86400  # 30 days (client reconnect horizon; still user-revocable)
_PENDING_TTL = 300         # 5 minutes for a human to click Allow — INVARIANTS.md §7

# Scope vocabulary — mirrors grove/mcp_local.py's AuthSettings. Duplicated
# rather than imported: mcp_local imports GroveOAuthProvider from this module
# only in serve mode, so importing back from here would risk a cycle for no
# real gain (three string constants).
SCOPE_READ  = "grove:read"
SCOPE_WRITE = "grove:write"
SCOPE_FULL  = "grove"  # back-compat superscope: implies both read and write
DEFAULT_SCOPES = [SCOPE_READ, SCOPE_WRITE]


def _expand_scopes(scopes: list[str] | None) -> list[str]:
    """Widen the `grove` superscope to its granular equivalents.

    The MCP SDK's `RequireAuthMiddleware` checks `required_scope not in
    token.scopes` — exact string membership, no notion of implication. A
    token minted before per-tool scopes existed carries literally
    `["grove"]`; without this it would fail a `required_scopes=["grove:read"]`
    gate even though "grove" was always meant to be full access. Called at
    the token-verification boundary (`load_access_token`) so both the
    transport-level gate and the per-tool checks in grove/mcp_local.py see
    the same widened set — old tokens keep working, nothing needs migrating.
    """
    out = list(dict.fromkeys(scopes or []))
    if SCOPE_FULL in out:
        for s in (SCOPE_READ, SCOPE_WRITE):
            if s not in out:
                out.append(s)
    return out


def effective_scopes(
    client: OAuthClientInformationFull,
    params: AuthorizationParams,
) -> list[str]:
    """The scopes actually in play for one authorization request.

    Prefers what `/authorize` explicitly asked for (`params.scopes`). Falls
    back to the client's own registered scope, which itself defaults to
    `AuthSettings.default_scopes` at registration time when the client asked
    for nothing specific (see the MCP SDK's `register.py`) — so an ordinary
    dynamic-client-registration connect that never sends `scope=` still shows
    and grants the granular scope names rather than a hardcoded guess. Only
    a client record from before any of this existed (no `.scope` at all)
    falls all the way back to the full-access superscope.
    """
    if params.scopes:
        return list(params.scopes)
    if client.scope:
        return client.scope.split(" ")
    return [SCOPE_FULL]


_STATE_KEYS = ("clients", "access_tokens", "refresh_tokens")


class TokenStateError(RuntimeError):
    """The persisted token file exists but could not be read as valid state.

    Raised instead of silently falling back to an empty state: an empty state
    deregisters every client, and the next _save_state() would write that loss
    to disk permanently.
    """


def _empty_state() -> dict[str, Any]:
    return {key: {} for key in _STATE_KEYS}


def _tok() -> str:
    return secrets.token_urlsafe(32)


class GroveOAuthProvider:
    """
    Minimal single-user OAuth provider. Clients register dynamically.

    An authorization code is only ever issued by issue_code(), which is
    called from the /grove-approve route after a human clicks Allow.
    /authorize itself always redirects to that approval page. There is no
    unattended-approve path. See INVARIANTS.md §7.
    """

    def __init__(
        self,
        token_path: Path,
        base_url: str,
    ) -> None:
        self._token_path = Path(token_path)
        self._base_url   = base_url.rstrip("/")

        # In-memory: pending approvals {key: (client, params, expires_at)}
        self._pending: dict[str, tuple[OAuthClientInformationFull, AuthorizationParams, float]] = {}
        # In-memory: issued auth codes {code: AuthorizationCode}
        self._codes:   dict[str, AuthorizationCode] = {}

        # Persisted state
        self._state: dict[str, Any] = self._load_state()

    # ── Persistence ───────────────────────────────────────────────────────────

    def _load_state(self) -> dict:
        """Read persisted state. Raise TokenStateError on anything unreadable.

        A corrupt or truncated token file must never degrade into an empty
        state: that silently deregisters every client, and the next save makes
        the loss permanent. Refuse to start instead, and say what to do.
        """
        if not self._token_path.exists():
            return _empty_state()

        try:
            raw = self._token_path.read_text()
        except OSError as e:
            raise TokenStateError(f"cannot read token state {self._token_path}: {e}") from e

        hint = (
            f" Move {self._token_path} aside (or delete it) to start from an "
            "empty state and re-authorize; do not let it be overwritten silently."
        )
        try:
            data = json.loads(raw)
        except json.JSONDecodeError as e:
            raise TokenStateError(
                f"token state {self._token_path} is not valid JSON ({e})."
                f" It is corrupt or truncated.{hint}"
            ) from e

        if not isinstance(data, dict):
            raise TokenStateError(
                f"token state {self._token_path} is a {type(data).__name__}, expected a JSON object.{hint}"
            )
        for key in _STATE_KEYS:
            if key not in data:
                raise TokenStateError(
                    f"token state {self._token_path} is missing the {key!r} section.{hint}"
                )
            if not isinstance(data[key], dict):
                raise TokenStateError(
                    f"token state {self._token_path} has a non-object {key!r} section.{hint}"
                )
        return data

    def _save_state(self) -> None:
        """Write state atomically, 0600, never widening an existing file's mode.

        The file holds live bearer tokens. Writing it in place at the default
        umask left it world-readable and left a half-written file behind on a
        crash mid-write. Create a fresh 0600 temp file, fsync, then rename over
        the target — os.replace is atomic and carries the temp file's mode, so
        the result is 0600 whether or not the target already existed.
        """
        self._token_path.parent.mkdir(parents=True, exist_ok=True)
        tmp = self._token_path.with_name(f"{self._token_path.name}.{os.getpid()}.{secrets.token_hex(6)}.tmp")
        try:
            # O_EXCL: never write through a pre-existing (possibly planted, possibly
            # world-readable) path. Mode 0600 at create time, so there is no window
            # in which the tokens are on disk under a wider mode.
            fd = os.open(str(tmp), os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
            with os.fdopen(fd, "w") as f:
                f.write(json.dumps(self._state, indent=2))
                f.flush()
                os.fsync(f.fileno())
            # Defensive: umask can only narrow the mode above, but a restrictive
            # umask plus an inherited default should still land exactly on 0600.
            os.chmod(tmp, 0o600)
            os.replace(tmp, self._token_path)
        except BaseException:
            try:
                tmp.unlink()
            except OSError:
                pass
            raise

    # ── Pending approval helpers (called by grove_approve route) ──────────────

    def stash_pending(
        self,
        key: str,
        client: OAuthClientInformationFull,
        params: AuthorizationParams,
    ) -> None:
        """Park an authorization request until a human decides on it.

        If `key` already has a live entry, its ORIGINAL expires_at is kept —
        re-stashing (e.g. grove_approve's GET branch re-parking the request
        after popping it) must not push the 5-minute ceiling out again. Per
        INVARIANTS.md §7 the one-shot key has a hard 5-minute lifetime; a
        caller that genuinely needs the clock reset should use
        stash_pending_or_refresh instead.
        """
        existing = self._pending.get(key)
        expires_at = existing[2] if existing is not None else time.time() + _PENDING_TTL
        self._pending[key] = (client, params, expires_at)

    def stash_pending_or_refresh(
        self,
        key: str,
        client: OAuthClientInformationFull,
        params: AuthorizationParams,
    ) -> None:
        """Park an authorization request, resetting the TTL even if `key` is
        already pending. Distinct from stash_pending, which preserves the
        original expiry on re-stash — see INVARIANTS.md §7.
        """
        self._pending[key] = (client, params, time.time() + _PENDING_TTL)

    def pop_pending(self, key: str):
        """Take a parked request, or None if it is unknown or expired."""
        self._prune_pending()
        entry = self._pending.pop(key, None)
        if entry is None:
            return None
        client, params, expires_at = entry
        if expires_at < time.time():
            return None
        return client, params

    def _prune_pending(self) -> None:
        now = time.time()
        for key in [k for k, (_, _, exp) in self._pending.items() if exp < now]:
            del self._pending[key]

    def issue_code(
        self,
        client: OAuthClientInformationFull,
        params: AuthorizationParams,
    ) -> str:
        code_str = _tok()
        self._codes[code_str] = AuthorizationCode(
            code=code_str,
            scopes=effective_scopes(client, params),
            expires_at=time.time() + _CODE_TTL,
            client_id=client.client_id,
            code_challenge=params.code_challenge,
            redirect_uri=params.redirect_uri,
            redirect_uri_provided_explicitly=params.redirect_uri_provided_explicitly,
        )
        return code_str

    # ── OAuthAuthorizationServerProvider protocol ─────────────────────────────

    async def get_client(self, client_id: str) -> OAuthClientInformationFull | None:
        data = self._state["clients"].get(client_id)
        if data is None:
            return None
        return OAuthClientInformationFull(**data)

    async def register_client(self, client_info: OAuthClientInformationFull) -> None:
        self._state["clients"][client_info.client_id] = client_info.model_dump(mode="json")
        self._save_state()

    async def authorize(
        self,
        client: OAuthClientInformationFull,
        params: AuthorizationParams,
    ) -> str:
        """Return the URL the browser should be redirected to next.

        Always the /grove-approve consent page, with the request parked under
        a one-shot key. No authorization code exists yet — the page issues one
        only if a human clicks Allow, and only when that click arrives from
        the loopback interface (see /grove-approve in mcp_local.py). There is
        no auto-approve branch — see INVARIANTS.md §7.
        """
        key = _tok()
        self.stash_pending(key, client, params)
        return f"{self._base_url}/grove-approve?pending={key}"

    async def load_authorization_code(
        self,
        client: OAuthClientInformationFull,
        authorization_code: str,
    ) -> AuthorizationCode | None:
        code = self._codes.get(authorization_code)
        if code is None:
            return None
        if code.client_id != client.client_id:
            return None
        if code.expires_at < time.time():
            del self._codes[authorization_code]
            return None
        return code

    async def exchange_authorization_code(
        self,
        client: OAuthClientInformationFull,
        authorization_code: AuthorizationCode,
    ) -> OAuthToken:
        # Consume the code
        self._codes.pop(authorization_code.code, None)

        access_tok  = _tok()
        refresh_tok = _tok()
        now         = int(time.time())

        self._state["access_tokens"][access_tok] = {
            "token":     access_tok,
            "client_id": client.client_id,
            "scopes":    authorization_code.scopes,
            "expires_at": now + _ACCESS_TTL,
        }
        self._state["refresh_tokens"][refresh_tok] = {
            "token":     refresh_tok,
            "client_id": client.client_id,
            "scopes":    authorization_code.scopes,
            "expires_at": now + _REFRESH_TTL,
        }
        self._save_state()

        return OAuthToken(
            access_token=access_tok,
            token_type="bearer",
            expires_in=_ACCESS_TTL,
            refresh_token=refresh_tok,
            scope=" ".join(authorization_code.scopes),
        )

    async def load_refresh_token(
        self,
        client: OAuthClientInformationFull,
        refresh_token: str,
    ) -> RefreshToken | None:
        data = self._state["refresh_tokens"].get(refresh_token)
        if data is None:
            return None
        if data["client_id"] != client.client_id:
            return None
        exp = data.get("expires_at")
        if exp and exp < time.time():
            del self._state["refresh_tokens"][refresh_token]
            self._save_state()
            return None
        return RefreshToken(**data)

    async def exchange_refresh_token(
        self,
        client: OAuthClientInformationFull,
        refresh_token: RefreshToken,
        scopes: list[str],
    ) -> OAuthToken:
        # Rotate both tokens
        self._state["refresh_tokens"].pop(refresh_token.token, None)

        effective_scopes = scopes or refresh_token.scopes
        access_tok  = _tok()
        new_refresh = _tok()
        now         = int(time.time())

        self._state["access_tokens"][access_tok] = {
            "token":     access_tok,
            "client_id": client.client_id,
            "scopes":    effective_scopes,
            "expires_at": now + _ACCESS_TTL,
        }
        self._state["refresh_tokens"][new_refresh] = {
            "token":     new_refresh,
            "client_id": client.client_id,
            "scopes":    effective_scopes,
            "expires_at": now + _REFRESH_TTL,
        }
        self._save_state()

        return OAuthToken(
            access_token=access_tok,
            token_type="bearer",
            expires_in=_ACCESS_TTL,
            refresh_token=new_refresh,
            scope=" ".join(effective_scopes),
        )

    async def load_access_token(self, token: str) -> AccessToken | None:
        data = self._state["access_tokens"].get(token)
        if data is None:
            return None
        exp = data.get("expires_at")
        if exp and exp < time.time():
            del self._state["access_tokens"][token]
            self._save_state()
            return None
        # Widen `grove` to its granular equivalents here, not in storage — the
        # persisted grant stays exactly what was authorized, but every reader
        # (the transport's required_scopes gate, per-tool checks) sees the
        # implied full access. See _expand_scopes.
        data = {**data, "scopes": _expand_scopes(data.get("scopes"))}
        return AccessToken(**data)

    async def revoke_token(self, token: AccessToken | RefreshToken) -> None:
        if isinstance(token, AccessToken):
            self._state["access_tokens"].pop(token.token, None)
        else:
            self._state["refresh_tokens"].pop(token.token, None)
        self._save_state()
