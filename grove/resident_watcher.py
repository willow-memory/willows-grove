# b17: WGRV1 ΔΣ=42
"""Willow's Grove resident watcher — Gate 5 v1, L1-capped.

*Companion runtime to* `docs/design/autonomous-continuity.md` *C4-C5, C7-C8,
C9, C11.* The autonomous-continuity doc pins the authority; this module is
the resident actor at rest for Grove's seat. It reads (Postgres LISTEN/NOTIFY
on ``grove.messages``, the fleet-presence roster, the envelope registry,
Nestor's ``decision_check``) and writes to exactly one place — ``kb_journal``
via ``grove.journal_writer.write_operator_turn`` — always with
``sender="resident-watcher"`` and a domain-tag classification.

This is the **L1 ceiling made concrete**:

* **Reads.** Anything the roster grants read on: journal, roster, envelopes,
  Nestor decision-check. Reads leave no trace of intent (§5 L0).
* **Writes.** ``kb_journal`` (``domain: "journal"``) only. Nothing else. No
  Kart drafts in v1 (deferred — task's C7-C8 seam). No Nestor pair proposals
  (L2 — deferred). No writes to ``grove.channels`` (that would be speaking as
  a persona; V5-adjacent — see the three-question lock below).
* **Never.** L3 and L4 are empty. This module contains no code path that
  reaches either.

Three-question locks (Gate 5 handoff, sealed 2026-08-27):

* **Q1 — model.** Read from SOIL at ``~/.willow/store/active_model``. Do not
  hard-code. Log-once and fall back to ``"llama3.2:3b"`` when SOIL is unset.
* **Q2 — classification scope.** Domain tag on the journal atom only. No
  persona routing, no writes to ``grove.channels`` in v1.
* **Q3 — sender.** ``"resident-watcher"`` on every journal write. Never
  speak as ``"willow"`` or as any persona.

D7 discipline everywhere: Postgres down, Ollama slow, Nestor absent — each
degrades to a legible state and a single log line, never a crash. The
watcher's job is to be at the post; a crashed watcher is a missed handoff.

Sync + threaded — matches ``grove/journal_writer.py``'s style. One LISTEN
thread, one worker thread that drains the classification queue, one
heartbeat thread. Ollama I/O never happens in the LISTEN callback: notifies
enqueue and return so Postgres is never blocked by a slow model.
"""
from __future__ import annotations

import json
import logging
import os
import queue
import select
import signal
import threading
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Optional

from grove import envelope_reader, fleet_presence, journal_writer
from grove.errors import Unreachable
from grove.nestor_client import NestorClient

log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants — the surface the watcher is willing to sign its name to.
# ---------------------------------------------------------------------------

SENDER = "resident-watcher"
"""Every kb_journal write from this watcher carries this sender (Q3 lock)."""

DOMAINS = ("chat", "governance", "pm", "pa", "unknown")
"""Closed vocabulary of domain tags (Q2 lock). ``unknown`` is the D7 fallback."""

DEFAULT_MODEL = "llama3.2:3b"
"""Fallback when SOIL's ``active_model`` file is absent (Q1 lock)."""

DEFAULT_OLLAMA_URL = "http://localhost:11434"
"""Local Ollama endpoint. Loopback-only by design (C5, workshop metaphor)."""

DEFAULT_HEARTBEAT_SECONDS = 30

_ENVELOPE_REATTEST_WINDOW_SECONDS = 48 * 3600
"""48h envelope re-attestation warning window (P1 discipline)."""

_OLLAMA_TIMEOUT_SECONDS = 2.0
"""Aggressive per-call Ollama timeout. Never crash the watcher on a hiccup (D7)."""

_CLASSIFY_PROMPT = (
    "You are a resident local classifier for Willow's Grove. Read the message "
    "and reply with EXACTLY one of these tokens, lowercase, no punctuation, no "
    "explanation: chat, governance, pm, pa, unknown. "
    "chat = casual conversation; governance = decisions/policy/authority; "
    "pm = project management, planning, tasks; pa = personal-assistant "
    "requests (reminders, scheduling). If truly unclear, answer unknown."
)


# ---------------------------------------------------------------------------
# SOIL — the operator's active-model file.
# ---------------------------------------------------------------------------

def _soil_active_model_path() -> Path:
    """Where SOIL stores the operator's current active-model choice.

    ``~/.willow/store/active_model``. A single line of text. Absent → fallback
    to ``DEFAULT_MODEL`` and log once.
    """
    return Path.home() / ".willow" / "store" / "active_model"


def read_active_model() -> tuple[str, bool]:
    """Return ``(model_name, from_soil)``.

    ``from_soil`` is ``True`` when the SOIL file existed and yielded a non-empty
    line, ``False`` when the fallback was used. The watcher log-once's the
    fallback the first time it fires.
    """
    path = _soil_active_model_path()
    try:
        text = path.read_text(encoding="utf-8").strip()
    except FileNotFoundError:
        return DEFAULT_MODEL, False
    except OSError:
        return DEFAULT_MODEL, False
    if not text:
        return DEFAULT_MODEL, False
    return text.splitlines()[0].strip() or DEFAULT_MODEL, bool(text)


# ---------------------------------------------------------------------------
# The watcher.
# ---------------------------------------------------------------------------

class ResidentWatcher:
    """Willow's Grove resident watcher — Gate 5 v1, L1-capped.

    Reads: Postgres LISTEN/NOTIFY on ``grove.messages``, roster, personas,
    envelopes, and Nestor ``decision_check`` before acting. Writes:
    ``kb_journal`` only, sender ``"resident-watcher"``, with a domain-tag
    classification.

    Threading model:

    * one LISTEN thread — psycopg2 autocommit connection; on each notification
      it fetches the row and enqueues it, never doing Ollama I/O inline
    * one worker thread — drains the classification queue; calls Ollama,
      then Nestor, then the journal writer
    * one heartbeat thread — every ``heartbeat_seconds`` refreshes the
      fleet-presence roster and checks the envelope re-attestation window

    Instantiating does not start any threads; call :meth:`start`. Call
    :meth:`stop` to shut down cleanly.
    """

    # In-memory dedupe for envelope re-attestation notes.
    # Resets on watcher restart — this is deliberate: a restart is when the
    # operator is looking, and a re-notification then is helpful.

    def __init__(
        self,
        *,
        db_url: str | None = None,
        model_name: str | None = None,
        ollama_url: str = DEFAULT_OLLAMA_URL,
        heartbeat_seconds: int = DEFAULT_HEARTBEAT_SECONDS,
    ) -> None:
        self._db_url = db_url if db_url is not None else os.environ.get("WILLOW_DB_URL", "").strip() or None
        if model_name:
            self._model = model_name
            self._model_from_soil = True
        else:
            model, from_soil = read_active_model()
            self._model = model
            self._model_from_soil = from_soil
        self._ollama_url = ollama_url.rstrip("/")
        self._heartbeat_seconds = max(1, int(heartbeat_seconds))

        self._abort = threading.Event()
        self._work_queue: "queue.Queue[dict[str, Any] | None]" = queue.Queue()
        self._threads: list[threading.Thread] = []
        self._envelope_noted: set[str] = set()

        # Log-once latches.
        self._logged_model_fallback = False
        self._logged_ollama_error = False
        self._logged_db_absent = False
        self._logged_listen_error = False
        self._logged_nestor_refused = False

        # Nestor client — created lazily so tests can inject.
        self._nestor: Optional[NestorClient] = None

        # For tests / observability.
        self._in_flight = threading.Semaphore(0)
        self._prev_signal_handlers: dict[int, Any] = {}

    # ---- lifecycle ----
    def start(self) -> None:
        """Spawn the LISTEN thread + worker + heartbeat + shutdown handler."""
        if not self._model_from_soil and not self._logged_model_fallback:
            log.info(
                "resident_watcher: SOIL active_model absent — using fallback %r (Q1).",
                self._model,
            )
            self._logged_model_fallback = True

        self._abort.clear()

        listen_t = threading.Thread(target=self._listen_loop, name="grove-watcher-listen", daemon=True)
        worker_t = threading.Thread(target=self._worker_loop, name="grove-watcher-worker", daemon=True)
        heartbeat_t = threading.Thread(target=self._heartbeat_loop, name="grove-watcher-heartbeat", daemon=True)
        self._threads = [listen_t, worker_t, heartbeat_t]
        for t in self._threads:
            t.start()

        # Install signal handlers ONLY on the main thread; tests spawn the
        # watcher from a worker thread and would hit ValueError otherwise.
        if threading.current_thread() is threading.main_thread():
            for sig in (signal.SIGTERM, signal.SIGINT):
                try:
                    self._prev_signal_handlers[sig] = signal.signal(sig, self._on_signal)
                except (ValueError, OSError):
                    pass

    def _on_signal(self, signum, frame):  # pragma: no cover — exercised in prod, not unit tests
        log.info("resident_watcher: received signal %d — shutting down.", signum)
        self.stop()

    def stop(self, timeout: float = 5.0) -> None:
        """Signal shutdown, drain in-flight classifications, join threads."""
        self._abort.set()
        # Wake the worker if it is blocked on the queue.
        try:
            self._work_queue.put_nowait(None)
        except Exception:  # noqa: BLE001
            pass
        deadline = time.monotonic() + max(0.0, timeout)
        for t in self._threads:
            remaining = max(0.0, deadline - time.monotonic())
            t.join(timeout=remaining)
        # Best-effort Nestor close.
        if self._nestor is not None:
            try:
                self._nestor.close()
            except Exception:  # noqa: BLE001
                pass
        # Restore previous signal handlers where installed.
        for sig, prev in self._prev_signal_handlers.items():
            try:
                signal.signal(sig, prev)
            except (ValueError, OSError):
                pass
        self._prev_signal_handlers.clear()

    # ---- classification ----
    def _classify_message(self, text: str, sender: str) -> str:
        """Return one of ``DOMAINS``. Ollama-backed, log-once on error.

        Never raises — a hiccup on Ollama surfaces as ``"unknown"`` and a
        single log line per process (D7 anti-noise).
        """
        if not text or not isinstance(text, str):
            return "unknown"
        payload = {
            "model": self._model,
            "prompt": f"{_CLASSIFY_PROMPT}\n\nSender: {sender}\nMessage: {text}\n\nAnswer:",
            "stream": False,
        }
        body = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(  # noqa: S310 — loopback local model
            self._ollama_url + "/api/generate",
            data=body,
            method="POST",
            headers={"content-type": "application/json"},
        )
        try:
            with urllib.request.urlopen(req, timeout=_OLLAMA_TIMEOUT_SECONDS) as resp:  # noqa: S310
                raw = resp.read().decode("utf-8", errors="replace")
        except (urllib.error.URLError, urllib.error.HTTPError, OSError, TimeoutError) as err:
            if not self._logged_ollama_error:
                log.warning("resident_watcher: Ollama unreachable/slow (%s) — domains fall back to 'unknown'.", err)
                self._logged_ollama_error = True
            return "unknown"
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            if not self._logged_ollama_error:
                log.warning("resident_watcher: Ollama returned unparseable body — domains fall back to 'unknown'.")
                self._logged_ollama_error = True
            return "unknown"
        answer = ""
        if isinstance(data, dict):
            answer = str(data.get("response", "")).strip().lower()
        # Take first token — model may pad with punctuation or a sentence.
        token = answer.split()[0].rstrip(".,:;!?") if answer else ""
        if token in DOMAINS:
            return token
        return "unknown"

    # ---- Postgres LISTEN/NOTIFY ----
    def _listen_loop(self) -> None:
        """Open a LISTEN connection and drain notifications until abort.

        On any Postgres unavailability (missing DSN, missing schema, import
        failure) we log-once and return — the heartbeat thread continues to
        run (D7 heartbeat-only mode).
        """
        if not self._db_url:
            if not self._logged_db_absent:
                log.info(
                    "resident_watcher: WILLOW_DB_URL unset — running heartbeat-only "
                    "(no LISTEN/NOTIFY on grove.messages) (D7)."
                )
                self._logged_db_absent = True
            return
        try:
            import psycopg2  # type: ignore
        except Exception as err:  # noqa: BLE001
            if not self._logged_db_absent:
                log.warning("resident_watcher: psycopg2 unavailable (%s) — heartbeat-only.", err)
                self._logged_db_absent = True
            return

        conn = None
        try:
            conn = psycopg2.connect(self._db_url)
            conn.autocommit = True
            cur = conn.cursor()
            cur.execute("LISTEN grove_channel")
        except Exception as err:  # noqa: BLE001
            if not self._logged_listen_error:
                log.warning("resident_watcher: LISTEN setup failed (%s) — heartbeat-only.", err)
                self._logged_listen_error = True
            try:
                if conn is not None:
                    conn.close()
            except Exception:  # noqa: BLE001
                pass
            return

        try:
            while not self._abort.is_set():
                try:
                    ready = select.select([conn], [], [], 1.0)
                except (OSError, ValueError):
                    break
                if ready == ([], [], []):
                    continue
                try:
                    conn.poll()
                except Exception as err:  # noqa: BLE001
                    if not self._logged_listen_error:
                        log.warning("resident_watcher: LISTEN poll failed (%s).", err)
                        self._logged_listen_error = True
                    break
                while getattr(conn, "notifies", None):
                    notif = conn.notifies.pop(0)
                    self._on_notify(conn, notif)
        finally:
            try:
                conn.close()
            except Exception:  # noqa: BLE001
                pass

    def _on_notify(self, conn: Any, notif: Any) -> None:
        """Fetch the newest row for the notified channel and enqueue it.

        Never runs Ollama I/O here — the LISTEN thread must stay responsive
        so Postgres does not stall.
        """
        try:
            channel_id = int(getattr(notif, "payload", "0") or "0")
        except (TypeError, ValueError):
            return
        try:
            cur = conn.cursor()
            cur.execute(
                "SELECT id, sender, content FROM grove.messages "
                "WHERE channel_id = %s ORDER BY id DESC LIMIT 1",
                (channel_id,),
            )
            row = cur.fetchone()
        except Exception as err:  # noqa: BLE001
            if not self._logged_listen_error:
                log.warning("resident_watcher: fetch after NOTIFY failed (%s).", err)
                self._logged_listen_error = True
            return
        if not row:
            return
        msg = {
            "id": row[0],
            "sender": row[1] or "",
            "content": row[2] or "",
            "channel_id": channel_id,
        }
        self._enqueue_message(msg)

    def _enqueue_message(self, row: dict[str, Any]) -> None:
        """Test-visible seam — package a message row for the worker queue.

        Refuses new work once shutdown has started (graceful-drain discipline).
        """
        if self._abort.is_set():
            return
        self._work_queue.put(row)

    def _on_message(self, row: dict[str, Any]) -> None:
        """Called by the worker when a NOTIFY-fetched row is due for classification.

        Classifies + Nestor-checks + writes to journal, in that order.
        """
        text = str(row.get("content", ""))
        sender = str(row.get("sender", "")) or "unknown"
        if not text.strip():
            return
        domain = self._classify_message(text, sender)
        if not self._nestor_permits(domain):
            return
        summary = f"[{domain}] {sender}: {text}"
        self._write_journal(summary, domain=domain)

    def _worker_loop(self) -> None:
        """Drain the classification queue until the shutdown sentinel arrives."""
        while True:
            try:
                item = self._work_queue.get(timeout=0.5)
            except queue.Empty:
                if self._abort.is_set():
                    return
                continue
            if item is None:  # shutdown sentinel
                return
            # Mark in-flight so tests can observe the drain-in-flight discipline.
            self._in_flight.release()
            try:
                self._on_message(item)
            except Exception as err:  # noqa: BLE001 — worker must not die
                log.warning("resident_watcher: worker error on row: %s", err)
            finally:
                # Consume our own semaphore permit — non-blocking.
                self._in_flight.acquire(blocking=False)

    # ---- Nestor gate ----
    def _get_nestor(self) -> NestorClient:
        if self._nestor is None:
            self._nestor = NestorClient()
        return self._nestor

    def _nestor_permits(self, domain: str) -> bool:
        """Ask Nestor whether we may write this classification.

        * ``refused`` → False (skip the journal write, log-once).
        * ``sealed`` / ``pending`` / anything else → True (proceed).
        * Nestor unreachable (``None``) → True (D7: proceed rather than block).
        """
        try:
            resp = self._get_nestor().decision_check(
                f"resident-watcher tags this as {domain}",
            )
        except Unreachable as err:
            # Nestor absent — heartbeat-only proceed (INVARIANTS.md §1).
            log.debug("resident_watcher: Nestor unreachable (%s) — proceeding.", err.reason)
            return True
        except Exception as err:  # noqa: BLE001
            log.debug("resident_watcher: Nestor call raised (%s) — proceeding.", err)
            return True
        if resp is None:
            # Nestor reached but no sealed pair — proceed.
            return True
        status = _extract_nestor_status(resp)
        if status == "refused":
            if not self._logged_nestor_refused:
                log.info("resident_watcher: Nestor refused a classification — skipping journal write.")
                self._logged_nestor_refused = True
            return False
        return True

    # ---- journal write ----
    def _write_journal(self, text: str, *, domain: str) -> None:
        """Delegate to ``journal_writer.write_operator_turn``.

        This is the ONLY write path in v1 (L1 ceiling). Sender is always
        ``resident-watcher``; the domain classification is carried as a tag
        on the atom.
        """
        try:
            journal_writer.write_operator_turn(text, sender=SENDER, domain=domain)
        except ValueError:
            # Empty text guard in the writer — nothing to do.
            return
        except Unreachable as err:
            # willow-mcp not reachable — degrade to heartbeat-only for this
            # atom (INVARIANTS.md §1). One log line, not per-atom noise.
            log.debug("resident_watcher: journal_writer unreachable (%s) — dropping atom.", err.reason)
        except Exception as err:  # noqa: BLE001
            log.warning("resident_watcher: journal_writer raised (%s) — dropping atom.", err)

    # ---- heartbeat ----
    def _heartbeat(self) -> None:
        """One tick: announce presence + check envelope re-attestation windows."""
        try:
            fleet_presence.announce_grove("resident-watcher at post", {"model": 1})
        except Exception as err:  # noqa: BLE001
            log.debug("resident_watcher: announce_grove failed (%s).", err)

        try:
            envelopes = envelope_reader.read_all().get("envelopes", [])
        except Unreachable as err:
            # No envelope directory in the probe path — heartbeat-only
            # for this tick, matching the earlier D7 degradation.
            log.debug("resident_watcher: envelope_reader unreachable (%s).", err.reason)
            return
        except Exception as err:  # noqa: BLE001
            log.debug("resident_watcher: envelope_reader failed (%s).", err)
            return

        now = time.time()
        for env in envelopes:
            if not isinstance(env, dict):
                continue
            env_id = env.get("id")
            if not isinstance(env_id, str) or not env_id:
                continue
            expires_at = _parse_expires_at(env.get("expires_at"))
            if expires_at is None:
                continue
            seconds_remaining = expires_at - now
            if seconds_remaining < 0 or seconds_remaining > _ENVELOPE_REATTEST_WINDOW_SECONDS:
                continue
            if env_id in self._envelope_noted:
                continue
            self._envelope_noted.add(env_id)
            hours = max(0, int(seconds_remaining // 3600))
            self._write_journal(
                f"envelope {env_id} re-attestation due within ~{hours}h",
                domain="governance",
            )

    def _heartbeat_loop(self) -> None:
        """Tick the heartbeat every ``heartbeat_seconds`` until abort."""
        while not self._abort.is_set():
            try:
                self._heartbeat()
            except Exception as err:  # noqa: BLE001
                log.warning("resident_watcher: heartbeat error (%s).", err)
            self._abort.wait(self._heartbeat_seconds)


# ---------------------------------------------------------------------------
# Small helpers.
# ---------------------------------------------------------------------------

def _extract_nestor_status(resp: Any) -> str:
    """Best-effort status extraction from a decision_check response.

    Nestor's stdio JSON-RPC shape is ``{"jsonrpc":"2.0","id":N,"result":{...}}``;
    the result carries a ``status`` field. Unknown shapes read as an empty
    string, which the caller treats as "not refused → proceed".
    """
    if isinstance(resp, dict):
        result = resp.get("result", resp)
        if isinstance(result, dict):
            status = result.get("status")
            if isinstance(status, str):
                return status.strip().lower()
    return ""


def _parse_expires_at(value: Any) -> Optional[float]:
    """Convert an envelope's ``expires_at`` to a unix timestamp.

    Accepts an int/float unix time or an ISO 8601 string; returns ``None`` for
    anything we cannot parse.
    """
    if isinstance(value, (int, float)):
        return float(value)
    if not isinstance(value, str) or not value:
        return None
    import datetime as _dt

    text = value.strip()
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    try:
        return _dt.datetime.fromisoformat(text).timestamp()
    except ValueError:
        return None


# ---------------------------------------------------------------------------
# Entry point — ``python3 -m grove.resident_watcher``.
# ---------------------------------------------------------------------------

def main() -> None:  # pragma: no cover — foreground process entry
    logging.basicConfig(
        level=os.environ.get("GROVE_WATCHER_LOGLEVEL", "INFO"),
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    watcher = ResidentWatcher()
    watcher.start()
    log.info(
        "resident_watcher: at post — model=%s ollama=%s heartbeat=%ss",
        watcher._model, watcher._ollama_url, watcher._heartbeat_seconds,
    )
    try:
        while not watcher._abort.is_set():
            time.sleep(1.0)
    except KeyboardInterrupt:
        pass
    finally:
        watcher.stop()


if __name__ == "__main__":  # pragma: no cover
    main()


__all__ = [
    "DEFAULT_MODEL",
    "DEFAULT_OLLAMA_URL",
    "DEFAULT_HEARTBEAT_SECONDS",
    "DOMAINS",
    "SENDER",
    "ResidentWatcher",
    "read_active_model",
]
