# tests/test_resident_watcher.py — Gate 5 v1 resident watcher, L1-capped.
#
# Sync stdlib unittest, no live DB / no Ollama needed. Mocks:
#   * psycopg2 flow via _on_notify + _on_message seams (see the module)
#   * Ollama HTTP via urllib.request.urlopen
#   * journal_writer.write_operator_turn — assert sender + domain tag
#
# Coverage matches the Gate 5 test-plan checklist:
#   * classification → journal write with the classified domain tag
#   * Ollama timeout → domain="unknown" + log-once (3 timeouts, 1 log)
#   * WILLOW_DB_URL unset → heartbeat-only mode
#   * envelope 48h window → one write per envelope-id per cycle; second cycle
#     same envelope → no duplicate write
#   * SIGTERM → graceful drain: in-flight classification finishes, no new work
#   * Nestor `refused` → skip journal write
#   * Nestor unreachable → proceed anyway (D7)
#   * every write carries sender="resident-watcher" (V5-adjacent)
from __future__ import annotations

import io
import os
import queue
import sys
import threading
import time
import unittest
import urllib.error
from unittest.mock import MagicMock, patch


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from grove import resident_watcher  # noqa: E402
from grove.resident_watcher import ResidentWatcher, SENDER, DOMAINS  # noqa: E402


class _FakeResp:
    def __init__(self, body: bytes) -> None:
        self._body = body

    def read(self) -> bytes:
        return self._body

    def __enter__(self) -> "_FakeResp":
        return self

    def __exit__(self, *exc) -> None:
        return None


def _ollama_response(text: str) -> bytes:
    import json
    return json.dumps({"response": text}).encode("utf-8")


class _CapturingWriter:
    """Stand-in for ``journal_writer.write_operator_turn`` that records calls."""

    def __init__(self) -> None:
        self.calls: list[dict] = []
        self.lock = threading.Lock()

    def __call__(self, text: str, *, sender: str = "operator", domain=None):
        with self.lock:
            self.calls.append({"text": text, "sender": sender, "domain": domain})
        return {"ok": True, "id": "atom-1", "ts": "2026-08-27T00:00:00Z"}


class _NestorStub:
    """Minimal NestorClient replacement — configurable ``decision_check`` result."""

    def __init__(self, response=None) -> None:
        self._response = response
        self.calls: list[str] = []

    def decision_check(self, question):
        self.calls.append(question)
        return self._response

    def close(self) -> None:
        pass


def _make_watcher(*, db_url=None, nestor=None, model="testmodel:1b") -> ResidentWatcher:
    w = ResidentWatcher(db_url=db_url, model_name=model, heartbeat_seconds=3600)
    if nestor is not None:
        w._nestor = nestor
    return w


class ClassificationTests(unittest.TestCase):
    def test_domain_tag_and_sender_on_journal_write(self) -> None:
        writer = _CapturingWriter()
        w = _make_watcher(nestor=_NestorStub(response=None))
        row = {"id": 1, "sender": "operator", "content": "please schedule my dentist"}

        with patch("grove.resident_watcher.urllib.request.urlopen",
                   lambda *_a, **_k: _FakeResp(_ollama_response("pa"))), \
             patch("grove.resident_watcher.journal_writer.write_operator_turn", writer):
            w._on_message(row)

        self.assertEqual(len(writer.calls), 1)
        call = writer.calls[0]
        self.assertEqual(call["sender"], SENDER)
        self.assertEqual(call["domain"], "pa")
        # Text is preserved verbatim (V5-adjacent).
        self.assertIn("please schedule my dentist", call["text"])

    def test_every_domain_token_round_trips(self) -> None:
        """The classifier accepts every token in DOMAINS and rejects garbage."""
        w = _make_watcher(nestor=_NestorStub(response=None))
        for token in ("chat", "governance", "pm", "pa", "unknown"):
            with patch("grove.resident_watcher.urllib.request.urlopen",
                       lambda *_a, _t=token, **_k: _FakeResp(_ollama_response(_t))):
                self.assertEqual(w._classify_message("m", "u"), token)
        # Garbage token → unknown.
        with patch("grove.resident_watcher.urllib.request.urlopen",
                   lambda *_a, **_k: _FakeResp(_ollama_response("banana"))):
            self.assertEqual(w._classify_message("m", "u"), "unknown")


class OllamaTimeoutTests(unittest.TestCase):
    def test_timeout_returns_unknown_and_log_once(self) -> None:
        w = _make_watcher()

        def _boom(*_a, **_k):
            raise urllib.error.URLError("timed out")

        with patch("grove.resident_watcher.urllib.request.urlopen", _boom):
            with self.assertLogs(resident_watcher.log, level="WARNING") as cap:
                first = w._classify_message("a", "u")
                second = w._classify_message("b", "u")
                third = w._classify_message("c", "u")

        self.assertEqual(first, "unknown")
        self.assertEqual(second, "unknown")
        self.assertEqual(third, "unknown")
        # One log line across three failures.
        ollama_lines = [r for r in cap.records if "Ollama" in r.getMessage()]
        self.assertEqual(len(ollama_lines), 1, cap.output)


class HeartbeatOnlyModeTests(unittest.TestCase):
    def test_missing_db_url_runs_heartbeat_only(self) -> None:
        """No WILLOW_DB_URL → LISTEN loop logs-once and returns; heartbeat still runs."""
        saved = os.environ.pop("WILLOW_DB_URL", None)
        try:
            w = _make_watcher(db_url=None)
            with self.assertLogs(resident_watcher.log, level="INFO") as cap:
                w._listen_loop()
            self.assertTrue(
                any("WILLOW_DB_URL unset" in r.getMessage() for r in cap.records),
                cap.output,
            )
            # Second call is silent (log-once).
            with self.assertLogs(resident_watcher.log, level="INFO") as cap2:
                # Prime an INFO so assertLogs never fails on empty; then check ours is absent.
                resident_watcher.log.info("marker")
                w._listen_loop()
            db_lines = [r for r in cap2.records if "WILLOW_DB_URL unset" in r.getMessage()]
            self.assertEqual(len(db_lines), 0, cap2.output)
        finally:
            if saved is not None:
                os.environ["WILLOW_DB_URL"] = saved


class EnvelopeReattestationTests(unittest.TestCase):
    def test_one_write_per_envelope_per_cycle_and_no_duplicate_next_cycle(self) -> None:
        writer = _CapturingWriter()
        w = _make_watcher()

        # Two envelopes: one due within 48h, one due far in the future.
        soon = time.time() + 12 * 3600
        far = time.time() + 30 * 24 * 3600
        envs = {
            "schema": "envelope-registry/v1.1",
            "envelopes": [
                {"id": "env-soon", "expires_at": soon},
                {"id": "env-far", "expires_at": far},
            ],
        }
        with patch("grove.resident_watcher.envelope_reader.read_all", return_value=envs), \
             patch("grove.resident_watcher.fleet_presence.announce_grove", return_value=True), \
             patch("grove.resident_watcher.journal_writer.write_operator_turn", writer):
            # Watcher's Nestor gate must return True to reach the writer.
            w._nestor = _NestorStub(response=None)
            w._heartbeat()
            first_calls = list(writer.calls)
            w._heartbeat()

        # Only one write, for env-soon, tagged governance.
        self.assertEqual(len(first_calls), 1)
        self.assertEqual(first_calls[0]["sender"], SENDER)
        self.assertEqual(first_calls[0]["domain"], "governance")
        self.assertIn("env-soon", first_calls[0]["text"])
        # Second cycle → no duplicate.
        self.assertEqual(len(writer.calls), 1)


class GracefulShutdownTests(unittest.TestCase):
    def test_stop_drains_in_flight_and_refuses_new_work(self) -> None:
        w = _make_watcher(nestor=_NestorStub(response=None))
        writer = _CapturingWriter()

        started = threading.Event()
        may_finish = threading.Event()

        def _slow_urlopen(*_a, **_k):
            started.set()
            # Simulate a slow classification — but bail if the test explicitly frees us.
            may_finish.wait(timeout=2.0)
            return _FakeResp(_ollama_response("chat"))

        with patch("grove.resident_watcher.urllib.request.urlopen", _slow_urlopen), \
             patch("grove.resident_watcher.journal_writer.write_operator_turn", writer):
            w.start()
            try:
                # Enqueue one item — worker starts classifying.
                w._enqueue_message({"id": 1, "sender": "op", "content": "hello"})
                self.assertTrue(started.wait(timeout=2.0), "worker never started classifying")

                # Start shutdown while classification is in-flight (in a bg thread
                # because .stop() blocks). Then free the classifier — the in-flight
                # write must land.
                stopper = threading.Thread(target=lambda: w.stop(timeout=5.0), daemon=True)
                stopper.start()

                # New enqueue after abort must be dropped.
                w._enqueue_message({"id": 2, "sender": "op", "content": "should-be-dropped"})

                may_finish.set()
                stopper.join(timeout=5.0)
            finally:
                w._abort.set()
                may_finish.set()

        # Exactly one write landed — the in-flight one.
        self.assertEqual(len(writer.calls), 1, writer.calls)
        self.assertEqual(writer.calls[0]["sender"], SENDER)
        self.assertNotIn("should-be-dropped", writer.calls[0]["text"])


class NestorGateTests(unittest.TestCase):
    def test_nestor_refused_skips_journal_write(self) -> None:
        writer = _CapturingWriter()
        w = _make_watcher(nestor=_NestorStub(response={"result": {"status": "refused"}}))

        with patch("grove.resident_watcher.urllib.request.urlopen",
                   lambda *_a, **_k: _FakeResp(_ollama_response("chat"))), \
             patch("grove.resident_watcher.journal_writer.write_operator_turn", writer):
            w._on_message({"id": 1, "sender": "op", "content": "hi"})

        self.assertEqual(writer.calls, [])

    def test_nestor_unreachable_proceeds(self) -> None:
        writer = _CapturingWriter()
        # decision_check returns None when Nestor is absent (D7).
        w = _make_watcher(nestor=_NestorStub(response=None))

        with patch("grove.resident_watcher.urllib.request.urlopen",
                   lambda *_a, **_k: _FakeResp(_ollama_response("chat"))), \
             patch("grove.resident_watcher.journal_writer.write_operator_turn", writer):
            w._on_message({"id": 1, "sender": "op", "content": "hi"})

        self.assertEqual(len(writer.calls), 1)
        self.assertEqual(writer.calls[0]["sender"], SENDER)
        self.assertEqual(writer.calls[0]["domain"], "chat")

    def test_nestor_sealed_and_pending_both_proceed(self) -> None:
        writer = _CapturingWriter()
        for status in ("sealed", "pending"):
            writer.calls.clear()
            w = _make_watcher(nestor=_NestorStub(response={"result": {"status": status}}))
            with patch("grove.resident_watcher.urllib.request.urlopen",
                       lambda *_a, **_k: _FakeResp(_ollama_response("pm"))), \
                 patch("grove.resident_watcher.journal_writer.write_operator_turn", writer):
                w._on_message({"id": 1, "sender": "op", "content": "sync"})
            self.assertEqual(len(writer.calls), 1, f"status={status}")


class SenderIsResidentWatcherTests(unittest.TestCase):
    def test_v5_adjacent_never_speak_as_willow_or_operator(self) -> None:
        """Every journal write from this watcher must carry sender='resident-watcher'."""
        writer = _CapturingWriter()
        w = _make_watcher(nestor=_NestorStub(response=None))

        with patch("grove.resident_watcher.urllib.request.urlopen",
                   lambda *_a, **_k: _FakeResp(_ollama_response("chat"))), \
             patch("grove.resident_watcher.journal_writer.write_operator_turn", writer):
            # Chat classification path.
            w._on_message({"id": 1, "sender": "someone", "content": "hey"})
            # Envelope re-attestation path.
            envs = {"envelopes": [{"id": "env-x", "expires_at": time.time() + 3600}]}
            with patch("grove.resident_watcher.envelope_reader.read_all", return_value=envs), \
                 patch("grove.resident_watcher.fleet_presence.announce_grove", return_value=True):
                w._heartbeat()

        self.assertGreaterEqual(len(writer.calls), 2)
        for call in writer.calls:
            self.assertEqual(call["sender"], SENDER,
                             f"never allowed to speak as anything but {SENDER!r}, got {call!r}")


class ModelResolutionTests(unittest.TestCase):
    def test_explicit_model_wins_and_marks_from_soil_true(self) -> None:
        w = ResidentWatcher(db_url=None, model_name="explicit:9b", heartbeat_seconds=3600)
        self.assertEqual(w._model, "explicit:9b")
        self.assertTrue(w._model_from_soil)  # explicit is authoritative

    def test_missing_soil_file_falls_back_and_reports_it(self) -> None:
        # Point _soil_active_model_path at a nonexistent path.
        import pathlib
        fake = pathlib.Path("/nonexistent/willow/store/active_model")
        with patch("grove.resident_watcher._soil_active_model_path", return_value=fake):
            model, from_soil = resident_watcher.read_active_model()
        self.assertEqual(model, resident_watcher.DEFAULT_MODEL)
        self.assertFalse(from_soil)


if __name__ == "__main__":
    unittest.main()
