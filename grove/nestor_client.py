# b17: WGRV1 ΔΣ=42
"""Thin Grove-side wrapper over ``nestor serve`` (MCP-over-stdio), per D11.

The Nestor CLI ships a ``serve`` subcommand that speaks MCP over
stdio. Grove's backend keeps one long-lived child process and calls
into it for decision-checks, evidence lookups, warrant lookups, and to
render Nestor's persona refusal speech act *verbatim* (V5 negation
guard — the refusal must never be paraphrased on our side).

Discipline (D7): if the ``nestor`` executable is not installed on the
operator's machine, every method returns ``None`` and the wrapper is a
silent no-op — Grove renders "no Nestor add-on present" state rather
than crashing. The probe-once + cache pattern follows
``hornbook-knowledge/oakenscrolls-office/almanac_seam.py``.

The stdio JSON-RPC framing here is the minimal MCP-lines subset used
by the reference client wrappers in the fleet (one JSON object per
line, matching request ids). Style is synchronous to keep the surface
small; Grove's Starlette layer (mirroring willow-mcp's ``gates_serve``)
runs client calls in a threadpool.
"""
from __future__ import annotations

import json
import logging
import os
import shutil
import subprocess
import threading
from pathlib import Path
from typing import Any, Optional

from grove.errors import Unreachable

log = logging.getLogger(__name__)

_DEFAULT_STORE_ENVS = ("NESTOR_DB", "NESTOR_HOME", "NESTOR_STORE", "NESTOR_STORE_PATH")


def _default_store_path() -> Optional[Path]:
    """Return a reasonable Nestor store path, or ``None`` if unresolvable.

    Probe order (first existing wins):

    1. ``$NESTOR_DB`` / ``$NESTOR_HOME`` — Nestor's own pins.
    2. ``$NESTOR_STORE`` / ``$NESTOR_STORE_PATH`` — legacy env override.
    2. ``~/.nestor/keep/nestor.db`` — household canonical store when present.
    3. ``$WILLOW_HOME/nestor`` — per-node Grove-adjacent store.
    3. ``~/.willow/nestor`` — local user overlay under the Willow prefix.
    4. ``~/.nestor`` — the operator's household Nestor store (the actual
       location on our operator's box; without this probe Grove falls
       through to Nestor's own CLI default of ``./data/nestor.db``, which
       drops a scratch DB into the repo cwd on every run).
    5. ``None`` — no candidate present, Grove degrades to no-op (D7).
    """
    for name in _DEFAULT_STORE_ENVS:
        val = os.environ.get(name)
        if val:
            return Path(val).expanduser()
    household_db = Path.home() / ".nestor" / "keep" / "nestor.db"
    if household_db.is_file():
        return household_db
    home = os.environ.get("WILLOW_HOME")
    if home:
        cand = Path(home).expanduser() / "nestor"
        if cand.exists():
            return cand
    willow_fallback = Path.home() / ".willow" / "nestor"
    if willow_fallback.exists():
        return willow_fallback
    household = Path.home() / ".nestor"
    if household.exists():
        return household
    return None


def _apply_nestor_store_env(env: dict[str, str], store_path: Path) -> None:
    """Pin the child ``nestor serve`` to the operator's household store.

    Nestor reads ``NESTOR_HOME`` / ``NESTOR_DB``, not the legacy
    ``NESTOR_STORE`` name this module used to set — without that pin the child
    falls back to ``data/nestor.db`` in the Grove cwd (empty) while the
    operator's sealed corpus sits in ``~/.nestor/keep/``.
    """
    p = store_path.expanduser()
    if p.is_dir():
        env["NESTOR_HOME"] = str(p)
        keyring = p / "keep" / "verifiers.json"
        ledger = p / "keep" / "ledger.jsonl"
    else:
        env["NESTOR_DB"] = str(p)
        keyring = p.parent / "verifiers.json"
        ledger = p.parent / "ledger.jsonl"
    if keyring.is_file():
        env["NESTOR_KEYRING"] = str(keyring)
        env.setdefault("NESTOR_REQUIRE_SEAL_KEY", "1")
    if ledger.is_file():
        env["NESTOR_LEDGER"] = str(ledger)


class NestorClient:
    """MCP-over-stdio client for a local ``nestor serve`` child process.

    Use as a context manager to keep the child alive across many calls::

        with NestorClient() as nc:
            check = nc.decision_check("may we merge?")

    All methods return ``None`` when the ``nestor`` executable is
    missing (D7). Every method is thread-safe via a single mutex; the
    stdio protocol is inherently serial per child.
    """

    def __init__(
        self,
        store_path: Optional[str | os.PathLike] = None,
        executable: str = "nestor",
    ) -> None:
        self._exe = executable
        self._store_path = Path(store_path).expanduser() if store_path else _default_store_path()
        self._proc: Optional[subprocess.Popen[str]] = None
        self._lock = threading.Lock()
        self._next_id = 0
        self._session_ready = False
        self._available: Optional[bool] = None  # tri-state: None=unprobed, True/False cached

    # ---- lifecycle ----
    def __enter__(self) -> "NestorClient":
        self._start()
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()

    def available(self) -> bool:
        """Cheap probe: is the ``nestor`` binary on PATH?  Cached."""
        if self._available is None:
            self._available = shutil.which(self._exe) is not None
        return self._available

    def _start(self) -> None:
        if not self.available():
            log.info("nestor_client: %r not on PATH — running as no-op (D7).", self._exe)
            return
        if self._proc is not None and self._proc.poll() is None:
            return
        env = os.environ.copy()
        if self._store_path is not None:
            _apply_nestor_store_env(env, self._store_path)
        try:
            self._proc = subprocess.Popen(  # noqa: S603 — trusted local exec
                [self._exe, "serve"],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                env=env,
            )
        except (FileNotFoundError, OSError) as err:
            log.warning("nestor_client: failed to spawn %r: %s — no-op mode.", self._exe, err)
            self._proc = None
            self._available = False

    def close(self) -> None:
        with self._lock:
            proc = self._proc
            self._proc = None
            self._session_ready = False
        if proc is None:
            return
        try:
            if proc.stdin and not proc.stdin.closed:
                proc.stdin.close()
        except Exception:  # noqa: BLE001
            pass
        try:
            proc.terminate()
            proc.wait(timeout=2)
        except Exception:  # noqa: BLE001
            try:
                proc.kill()
            except Exception:  # noqa: BLE001
                pass

    # ---- MCP call ----
    def _rpc(self, method: str, params: dict[str, Any], *, notify: bool = False) -> Optional[dict[str, Any]]:
        """One JSON-RPC request/response round trip (no response for notifications)."""
        if not self.available():
            return None
        with self._lock:
            if self._proc is None or self._proc.poll() is not None:
                self._start()
            proc = self._proc
            if proc is None or proc.stdin is None or proc.stdout is None:
                return None
            req: dict[str, Any] = {"jsonrpc": "2.0", "method": method, "params": params}
            if not notify:
                self._next_id += 1
                req["id"] = self._next_id
            try:
                proc.stdin.write(json.dumps(req) + "\n")
                proc.stdin.flush()
                if notify:
                    return {}
                line = proc.stdout.readline()
            except (BrokenPipeError, OSError) as err:
                log.warning("nestor_client: transport error on %s: %s", method, err)
                return None
            if not line:
                return None
            try:
                return json.loads(line)
            except json.JSONDecodeError as err:
                log.warning("nestor_client: bad response for %s: %s", method, err)
                return None

    def _ensure_session(self) -> bool:
        if self._session_ready:
            return True
        init = self._rpc(
            "initialize",
            {
                "protocolVersion": "2025-06-18",
                "capabilities": {},
                "clientInfo": {"name": "grove-nestor-client", "version": "1.0"},
            },
        )
        if not init or init.get("error"):
            return False
        self._rpc("notifications/initialized", {}, notify=True)
        self._session_ready = True
        return True

    def _tool(self, name: str, arguments: dict[str, Any]) -> Optional[Any]:
        """Call one Nestor MCP tool; return the decoded JSON payload."""
        if not self._ensure_session():
            return None
        resp = self._rpc("tools/call", {"name": name, "arguments": arguments})
        if not resp or resp.get("error"):
            return None
        result = resp.get("result") or {}
        content = result.get("content") or []
        if not content:
            return None
        text = content[0].get("text") if isinstance(content[0], dict) else None
        if not isinstance(text, str) or not text.strip():
            return None
        try:
            return json.loads(text)
        except json.JSONDecodeError as err:
            log.warning("nestor_client: tool %s returned non-JSON: %s", name, err)
            return None

    def _call(self, method: str, params: dict[str, Any]) -> Optional[dict[str, Any]]:
        """Legacy wire shim for tests that still patch the old method names."""
        if method == "nestor/decision_check":
            return self.decision_check(str(params.get("question") or ""))
        return self._rpc(method, params)

    # ---- public surface ----
    def decision_check(self, question: str) -> Optional[dict[str, Any]]:
        """Ask Nestor: has this decision been sealed?

        Three-state contract (INVARIANTS.md §1):

        * populated → returns the raw JSON-RPC response dict with a
          ``result`` payload (sealed / refused / pending — all real
          Nestor states).
        * empty → returns ``None`` when Nestor is reachable but has no
          matching sealed pair for this claim (the "pending" case at the
          endpoint layer).
        * unreachable → raises ``Unreachable`` when ``available()`` is
          False (nestor binary not on PATH). Callers used to see
          ``None`` in both the "reachable but no match" and "binary
          absent" cases; the endpoint used to disambiguate by calling
          ``available()`` first, and it still does — but a caller that
          skips the probe now gets a distinct sentinel.
        """
        if not self.available():
            raise Unreachable("nestor binary not on PATH")
        payload = self._tool(
            "nestor_ask",
            {"text": question, "source_lang": "decision", "target_lang": "decision"},
        )
        if not payload:
            return None
        passage = payload.get("passage") if isinstance(payload, dict) else None
        if not isinstance(passage, dict):
            return None
        state = passage.get("state")
        meta = passage.get("meta") if isinstance(passage.get("meta"), dict) else {}
        if state == "sealed":
            return {
                "verdict": "sealed",
                "pair": {
                    "pair_id": meta.get("pair_id"),
                    "source": passage.get("source"),
                    "target": passage.get("target"),
                    "verifier": meta.get("verifier"),
                },
            }
        return None

    def evidence_for(self, pair_id: str) -> Optional[dict[str, Any]]:
        """Fetch evidence attached to a sealed pair, by id."""
        return self._call("nestor/evidence_for", {"pair_id": pair_id})

    def warrant_for(self, pair_id: str) -> Optional[dict[str, Any]]:
        """Fetch the warrant (citation or construction) for a sealed pair."""
        return self._call("nestor/warrant_for", {"pair_id": pair_id})

    def refusal(self, act: str, **facts: Any) -> Optional[str]:
        """Render Nestor's persona refusal speech act, VERBATIM (V5).

        The value returned is Nestor's own text — negation preserved,
        no paraphrasing done here. Grove displays it inside its own
        chip vocabulary but the string content stays untouched.
        """
        resp = self._call("nestor/refusal", {"act": act, "facts": facts})
        if not resp:
            return None
        result = resp.get("result") if isinstance(resp, dict) else None
        if isinstance(result, dict):
            text = result.get("text") or result.get("speech_act") or result.get("utterance")
            if isinstance(text, str):
                return text
        if isinstance(result, str):
            return result
        return None


__all__ = ["NestorClient"]
