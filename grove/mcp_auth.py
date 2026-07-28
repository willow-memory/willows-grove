# grove/mcp_auth.py — Grove OAuth 2.0 PKCE provider (single-user)
# b17: GRMOAUTH  ΔΣ=42
"""
Single-user OAuth 2.0 provider for `grove.mcp_local --serve`.

There are two authorization postures. The default is the first one.

Interactive approval (default — `GROVE_MCP_AUTO_APPROVE` unset or falsey):
  1. A client hits /authorize. This provider parks the request in memory and
     redirects the browser to <base_url>/grove-approve?pending=<key>.
  2. The human at that browser clicks Allow (or Deny). The /grove-approve
     route in grove/mcp_local.py is what calls issue_code() — an
     authorization code exists only after a human clicked.
  3. The client exchanges the code (with its PKCE verifier) for access +
     refresh tokens.
  4. Tokens are persisted to token_path; access tokens expire in 30 days.

Unattended auto-approve (`GROVE_MCP_AUTO_APPROVE=1` — operator opt-in):
  /authorize issues a code immediately and redirects straight back to the
  client's callback. No human is in the loop. Because dynamic client
  registration is open (see register_client) and register+authorize needs no
  credential, *anyone who can reach /authorize* gets a 30-day full-scope
  `grove` token. That is only acceptable when you are certain nobody else can
  reach the listener — and note that grove/mcp_local.py disables DNS-rebinding
  protection when GROVE_MCP_URL is https://, i.e. exactly the tunnelled setup
  where "only I can reach it" is least true. The provider prints a warning to
  stderr at construction and on every grant while this mode is on.

PKCE (S256) is enforced by the MCP SDK's token handler, not by this module.
PKCE binds a code to the client that requested it; it does not decide *whether*
a requester should be authorized. The approval click is what does that.

Pending approvals and issued codes are in-memory (lost on restart, which just
means the client re-auths). Tokens are persisted to token_path so reconnects
work; that file is created 0600 and replaced atomically, and a corrupt one is
a hard error rather than a silent reset — see _load_state.
"""
import json
import os
import secrets
import sys
import time
from pathlib import Path
from typing import Any

from mcp.server.auth.provider import (
    AccessToken,
    AuthorizationCode,
    AuthorizationParams,
    AuthorizeError,
    RefreshToken,
    TokenError,
    construct_redirect_uri,
)
from mcp.shared.auth import OAuthClientInformationFull, OAuthToken

_ACCESS_TTL  = 30 * 86400  # 30 days (single-user local; claude.ai doesn't auto-refresh)
_CODE_TTL    = 300         # 5 minutes
_REFRESH_TTL = 30 * 86400  # 30 days
_PENDING_TTL = 600         # 10 minutes for a human to click Allow

AUTO_APPROVE_ENV = "GROVE_MCP_AUTO_APPROVE"
_TRUTHY = {"1", "true", "yes", "on"}

_STATE_KEYS = ("clients", "access_tokens", "refresh_tokens")


class TokenStateError(RuntimeError):
    """The persisted token file exists but could not be read as valid state.

    Raised instead of silently falling back to an empty state: an empty state
    deregisters every client, and the next _save_state() would write that loss
    to disk permanently.
    """


def auto_approve_enabled(env: dict[str, str] | None = None) -> bool:
    """True when the operator has explicitly opted into unattended approval."""
    src = os.environ if env is None else env
    return src.get(AUTO_APPROVE_ENV, "").strip().lower() in _TRUTHY


def _empty_state() -> dict[str, Any]:
    return {key: {} for key in _STATE_KEYS}


def _tok() -> str:
    return secrets.token_urlsafe(32)


class GroveOAuthProvider:
    """
    Minimal single-user OAuth provider. Clients register dynamically.

    By default an authorization code is issued only by issue_code(), which is
    called from the /grove-approve route after a human clicks Allow. Pass
    auto_approve=True (operator opt-in, see module docstring) to skip that and
    have authorize() issue codes unattended.
    """

    def __init__(
        self,
        token_path: Path,
        base_url: str,
        auto_approve: bool = False,
    ) -> None:
        self._token_path = Path(token_path)
        self._base_url   = base_url.rstrip("/")
        self._auto_approve = bool(auto_approve)

        # In-memory: pending approvals {key: (client, params, expires_at)}
        self._pending: dict[str, tuple[OAuthClientInformationFull, AuthorizationParams, float]] = {}
        # In-memory: issued auth codes {code: AuthorizationCode}
        self._codes:   dict[str, AuthorizationCode] = {}

        # Persisted state
        self._state: dict[str, Any] = self._load_state()

        if self._auto_approve:
            self._warn(
                f"{AUTO_APPROVE_ENV} is set: /authorize will hand out 30-day "
                "full-scope 'grove' tokens to any caller that can reach it, "
                "with no human approval and no client vetting. Unset it to "
                "restore the /grove-approve click."
            )

    @property
    def auto_approve(self) -> bool:
        return self._auto_approve

    @staticmethod
    def _warn(msg: str) -> None:
        print(f"[grove-oauth] WARNING: {msg}", file=sys.stderr, flush=True)

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
        """Park an authorization request until a human decides on it."""
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
            scopes=params.scopes or ["grove"],
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

        Default: the /grove-approve consent page, with the request parked
        under a one-shot key. No authorization code exists yet — the page
        issues one only if a human clicks Allow.

        With auto_approve on (opt-in, see module docstring): the client's own
        callback, carrying a code, with nobody consulted.
        """
        if self._auto_approve:
            self._warn(
                f"auto-approved OAuth grant for client_id={client.client_id!r} "
                f"(scopes={params.scopes or ['grove']}) with no human approval — "
                f"{AUTO_APPROVE_ENV} is set."
            )
            return construct_redirect_uri(
                str(params.redirect_uri),
                code=self.issue_code(client, params),
                state=params.state,
            )

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
        return AccessToken(**data)

    async def revoke_token(self, token: AccessToken | RefreshToken) -> None:
        if isinstance(token, AccessToken):
            self._state["access_tokens"].pop(token.token, None)
        else:
            self._state["refresh_tokens"].pop(token.token, None)
        self._save_state()
