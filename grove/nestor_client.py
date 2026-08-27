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

log = logging.getLogger(__name__)

_DEFAULT_STORE_ENVS = ("NESTOR_STORE", "NESTOR_STORE_PATH")


def _default_store_path() -> Optional[Path]:
    """Return a reasonable Nestor store path, or ``None`` if unresolvable.

    Prefer explicit env; then ``$WILLOW_HOME/nestor``; then
    ``~/.willow/nestor``. Returns ``None`` only when *no* candidate
    directory exists — Grove degrades to no-op in that case (D7).
    """
    for name in _DEFAULT_STORE_ENVS:
        val = os.environ.get(name)
        if val:
            return Path(val).expanduser()
    home = os.environ.get("WILLOW_HOME")
    if home:
        cand = Path(home).expanduser() / "nestor"
        if cand.exists():
            return cand
    fallback = Path.home() / ".willow" / "nestor"
    return fallback if fallback.exists() else None


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
            env["NESTOR_STORE"] = str(self._store_path)
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
    def _call(self, method: str, params: dict[str, Any]) -> Optional[dict[str, Any]]:
        """One JSON-RPC round trip. Returns ``None`` on no-op / failure."""
        if not self.available():
            return None
        with self._lock:
            if self._proc is None or self._proc.poll() is not None:
                self._start()
            proc = self._proc
            if proc is None or proc.stdin is None or proc.stdout is None:
                return None
            self._next_id += 1
            req = {"jsonrpc": "2.0", "id": self._next_id, "method": method, "params": params}
            try:
                proc.stdin.write(json.dumps(req) + "\n")
                proc.stdin.flush()
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

    # ---- public surface ----
    def decision_check(self, question: str) -> Optional[dict[str, Any]]:
        """Ask Nestor: has this decision been sealed?  Returns the raw response."""
        return self._call("nestor/decision_check", {"question": question})

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
