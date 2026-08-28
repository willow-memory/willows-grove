# b17: WGRV1 ΔΣ=42
"""tests/test_panel_wiring.py — INVARIANTS.md §8 pin for panel↔endpoint wiring.

Every Web Component consumes its live `/api/*` endpoint by default (§8),
and every endpoint answers with the three-state contract (§1). This
module boots the real Starlette + uvicorn app on an ephemeral loopback
port and asserts every endpoint the panels consume returns
``state=populated|empty|unreachable`` in the right cases.

The JS side (event names, DOM behavior) is not tested here — that is
PR 9's Playwright job. This file pins only the wire shape the panels
receive.

Endpoints exercised:
  * ``GET  /api/envelopes``        — populated | empty | unreachable via WILLOW_HOME
  * ``GET  /api/personas``         — populated | empty | unreachable via WILLOW_HOME
  * ``POST /api/nestor/decide``    — populated (sealed | refused | pending) via mock
  * ``GET  /api/dispatch``         — populated | empty via mocked kart_reader
                                     (unreachable case pinned by kart_reader tests)
  * ``POST /api/journal``          — populated | unreachable via mocked journal_writer
                                     (a successful write is always populated per §1)
  * ``GET  /api/journal/recent``   — populated | empty | unreachable via mocked reader

Stdlib only. Same harness shape as ``tests/test_grove_serve_envelopes.py`` and
``tests/test_grove_serve_nestor.py``.
"""
from __future__ import annotations

import contextlib
import json
import os
import socket
import sys
import tempfile
import threading
import time
import unittest
import urllib.error
import urllib.request
from pathlib import Path
from unittest import mock


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)


def _free_port() -> int:
    with contextlib.closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def _wait_until_up(url: str, timeout: float = 5.0) -> None:
    deadline = time.monotonic() + timeout
    last_err: Exception | None = None
    while time.monotonic() < deadline:
        try:
            with urllib.request.urlopen(url, timeout=0.5) as resp:
                if resp.status == 200:
                    return
        except (urllib.error.URLError, ConnectionError, OSError) as e:
            last_err = e
            time.sleep(0.05)
    raise RuntimeError(f"grove_serve did not come up at {url}: {last_err!r}")


class _ServerHarness:
    """Runs uvicorn in a background thread; shuts it down on exit."""

    def __init__(self) -> None:
        self.port = _free_port()
        self.host = "127.0.0.1"
        self._server = None
        self._thread: threading.Thread | None = None

    def __enter__(self) -> "_ServerHarness":
        import uvicorn
        import grove_serve

        config = uvicorn.Config(
            grove_serve.build_app(),
            host=self.host,
            port=self.port,
            log_level="error",
            access_log=False,
        )
        self._server = uvicorn.Server(config)
        self._thread = threading.Thread(target=self._server.run, daemon=True)
        self._thread.start()
        _wait_until_up(f"http://{self.host}:{self.port}/health")
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        if self._server is not None:
            self._server.should_exit = True
        if self._thread is not None:
            self._thread.join(timeout=3.0)

    def url(self, path: str) -> str:
        return f"http://{self.host}:{self.port}{path}"


def _get(url: str) -> tuple[int, dict]:
    req = urllib.request.Request(url, method="GET", headers={"accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=2.0) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        raw = e.read().decode("utf-8")
        try:
            return e.code, json.loads(raw)
        except json.JSONDecodeError:
            return e.code, {"raw": raw}


def _post_json(url: str, payload: dict) -> tuple[int, dict]:
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        method="POST",
        headers={"content-type": "application/json", "accept": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=3.0) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        raw = e.read().decode("utf-8")
        try:
            return e.code, json.loads(raw)
        except json.JSONDecodeError:
            return e.code, {"raw": raw}


# ---------------------------------------------------------------------------
# /api/envelopes — populated | empty | unreachable via WILLOW_HOME shape
# ---------------------------------------------------------------------------


class EnvelopesWiringTests(unittest.TestCase):
    """INVARIANTS.md §1 + §8 — the envelope panel's live endpoint."""

    def setUp(self) -> None:
        from grove import envelope_reader as er
        er._logged_missing_dirs = False
        er._logged_missing_files = False
        er._logged_malformed = set()
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.fake_home = Path(self.tmp.name) / "no-home"
        self.fake_home.mkdir()

    def _env(self, willow_home: Path):
        return mock.patch.dict(
            os.environ,
            {"HOME": str(self.fake_home), "WILLOW_HOME": str(willow_home)},
            clear=False,
        )

    def test_envelopes_unreachable_when_no_dir(self) -> None:
        willow_home = Path(self.tmp.name) / "no_envelopes_dir"
        willow_home.mkdir()
        with self._env(willow_home):
            with _ServerHarness() as srv:
                status, body = _get(srv.url("/api/envelopes"))
        self.assertEqual(status, 503)
        self.assertEqual(body.get("state"), "unreachable")

    def test_envelopes_empty_when_dir_present_but_no_files(self) -> None:
        willow_home = Path(self.tmp.name) / "empty_env_dir"
        (willow_home / "constitutional").mkdir(parents=True)
        with self._env(willow_home):
            with _ServerHarness() as srv:
                status, body = _get(srv.url("/api/envelopes"))
        self.assertEqual(status, 200)
        self.assertEqual(body.get("state"), "empty")
        self.assertEqual(body.get("envelopes"), [])

    def test_envelopes_populated_when_files_present(self) -> None:
        willow_home = Path(self.tmp.name) / "populated"
        env_dir = willow_home / "constitutional"
        env_dir.mkdir(parents=True)
        (env_dir / "a.json").write_text(
            json.dumps({
                "schema": "envelope-registry/v1.1",
                "envelopes": [{"id": "env-a", "grantee": "kart", "attestation": "attested"}],
            }),
            encoding="utf-8",
        )
        with self._env(willow_home):
            with _ServerHarness() as srv:
                status, body = _get(srv.url("/api/envelopes"))
        self.assertEqual(status, 200)
        self.assertEqual(body.get("state"), "populated")
        self.assertEqual(len(body.get("envelopes", [])), 1)


# ---------------------------------------------------------------------------
# /api/personas — populated | empty | unreachable via WILLOW_HOME shape
# ---------------------------------------------------------------------------


class PersonasWiringTests(unittest.TestCase):
    """INVARIANTS.md §1 + §4 + §8 — the persona registry panel's live endpoint.

    Mirrors ``EnvelopesWiringTests`` — tempdir + ``WILLOW_HOME`` override so the
    real ``persona_roster.locate_personas_file()`` probe path selects the shape,
    not a monkeypatched reader. That way the wire test also witnesses that the
    reader honors §1 (raises ``Unreachable`` on absence, returns an empty roster
    on a schema-valid file with no rows, returns a populated roster otherwise).
    """

    def setUp(self) -> None:
        from grove import persona_roster as pr
        pr._logged_missing = False
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.fake_home = Path(self.tmp.name) / "no-home"
        self.fake_home.mkdir()

    def _env(self, willow_home: Path):
        return mock.patch.dict(
            os.environ,
            {"HOME": str(self.fake_home), "WILLOW_HOME": str(willow_home)},
            clear=False,
        )

    def _write_registry(self, willow_home: Path, doc: dict) -> Path:
        target = willow_home / "willow-memory" / "willow" / "fleet_personas.json"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(doc), encoding="utf-8")
        return target

    def test_personas_unreachable_when_no_registry_file(self) -> None:
        """No fleet_personas.json anywhere in the probe path → 503 + unreachable.

        INVARIANTS.md §2 supersedes the pre-§1 read where absence collapsed to
        an empty-personas envelope: the reader now raises ``Unreachable`` and
        the endpoint answers 503.
        """
        willow_home = Path(self.tmp.name) / "no_registry"
        willow_home.mkdir()
        with self._env(willow_home):
            with _ServerHarness() as srv:
                status, body = _get(srv.url("/api/personas"))
        self.assertEqual(status, 503)
        self.assertEqual(body.get("state"), "unreachable")
        self.assertIn("fleet_personas.json", body.get("reason", ""))

    def test_personas_empty_when_registry_has_no_agents(self) -> None:
        """File present with ``agents: []`` → 200 + state=empty."""
        willow_home = Path(self.tmp.name) / "empty_registry"
        willow_home.mkdir()
        self._write_registry(
            willow_home, {"schema": "fleet-personas/v1", "agents": []}
        )
        with self._env(willow_home):
            with _ServerHarness() as srv:
                status, body = _get(srv.url("/api/personas"))
        self.assertEqual(status, 200)
        self.assertEqual(body.get("state"), "empty")
        self.assertEqual(body.get("schema"), "fleet-personas/v1")

    def test_personas_populated_when_registry_has_agents(self) -> None:
        """File present with one or more rows → 200 + state=populated. The
        endpoint round-trips the file's bytes under the ``state`` wrapper so
        the panel receives the schema and the row list verbatim."""
        willow_home = Path(self.tmp.name) / "populated_registry"
        willow_home.mkdir()
        self._write_registry(
            willow_home,
            {
                "schema": "fleet-personas/v1",
                "agents": [
                    {
                        "agent": "willow",
                        "role": "primary",
                        "trust": "flagship",
                        "voice": {"register": "warm"},
                        "visual": {"color": "#8FBC8F", "sigil": "\U0001F333"},
                    },
                ],
            },
        )
        with self._env(willow_home):
            with _ServerHarness() as srv:
                status, body = _get(srv.url("/api/personas"))
        self.assertEqual(status, 200)
        self.assertEqual(body.get("state"), "populated")
        self.assertEqual(body.get("schema"), "fleet-personas/v1")
        agents = body.get("agents")
        self.assertIsInstance(agents, list)
        self.assertEqual(len(agents), 1)
        self.assertEqual(agents[0]["agent"], "willow")


# ---------------------------------------------------------------------------
# /api/nestor/decide — populated (sealed | refused | pending) via mocked client
# ---------------------------------------------------------------------------


class NestorDecideWiringTests(unittest.TestCase):
    """INVARIANTS.md §1 + §8 — the refusal-summon boot's live endpoint."""

    def setUp(self) -> None:
        import grove_serve
        grove_serve._NESTOR_CLIENT = None

    def test_decide_populated_sealed(self) -> None:
        import grove_serve

        pair = {"id": "PAIR-1", "question": "q", "answer": "a"}

        def _sealed(_self, _q):
            return {"verdict": "sealed", "pair": pair}

        with _ServerHarness() as srv, \
                mock.patch.object(grove_serve.NestorClient, "available", return_value=True), \
                mock.patch.object(grove_serve.NestorClient, "decision_check", _sealed):
            status, body = _post_json(srv.url("/api/nestor/decide"), {"claim": "q"})
        self.assertEqual(status, 200)
        self.assertEqual(body.get("state"), "populated")
        self.assertEqual(body.get("verdict"), "sealed")
        self.assertEqual(body.get("pair"), pair)

    def test_decide_populated_refused(self) -> None:
        import grove_serve

        refusal = {
            "persona": "nestor",
            "act": "durable_rejection",
            "body": "no — this pair is not sealed.",
        }

        def _refused(_self, _q):
            return {"verdict": "refused", "refusal": refusal}

        with _ServerHarness() as srv, \
                mock.patch.object(grove_serve.NestorClient, "available", return_value=True), \
                mock.patch.object(grove_serve.NestorClient, "decision_check", _refused):
            status, body = _post_json(srv.url("/api/nestor/decide"), {"claim": "q"})
        self.assertEqual(status, 200)
        self.assertEqual(body.get("state"), "populated")
        self.assertEqual(body.get("verdict"), "refused")
        # V5 verbatim: the refusal object survives byte-for-byte.
        self.assertEqual(body.get("refusal"), refusal)

    def test_decide_populated_pending(self) -> None:
        import grove_serve

        def _no_match(_self, _q):
            return None

        with _ServerHarness() as srv, \
                mock.patch.object(grove_serve.NestorClient, "available", return_value=True), \
                mock.patch.object(grove_serve.NestorClient, "decision_check", _no_match):
            status, body = _post_json(srv.url("/api/nestor/decide"), {"claim": "novel"})
        self.assertEqual(status, 200)
        self.assertEqual(body.get("state"), "populated")
        self.assertEqual(body.get("verdict"), "pending")


# ---------------------------------------------------------------------------
# /api/dispatch — populated | empty via mocked kart_reader
# ---------------------------------------------------------------------------


class DispatchWiringTests(unittest.TestCase):
    """INVARIANTS.md §1 + §8 — the dispatch rail's live endpoint.

    The unreachable case is exercised directly by the kart_reader tests
    (see `tests/test_kart_reader.py` — Unreachable raised on missing DSN
    / missing table / connect failure). Here we pin the two 200 shapes."""

    def test_dispatch_empty_when_no_rows(self) -> None:
        from grove import kart_reader

        with _ServerHarness() as srv, \
                mock.patch.object(kart_reader, "read_queue", return_value=[]):
            status, body = _get(srv.url("/api/dispatch"))
        self.assertEqual(status, 200)
        self.assertEqual(body.get("state"), "empty")
        self.assertEqual(body.get("tasks"), [])

    def test_dispatch_populated_when_rows_present(self) -> None:
        from grove import kart_reader
        rows = [
            {"id": 1, "origin": "kart", "proposed_action": "seal PR-42",
             "authority_needed": "L2", "urgency": "operator-visible"},
        ]
        with _ServerHarness() as srv, \
                mock.patch.object(kart_reader, "read_queue", return_value=rows):
            status, body = _get(srv.url("/api/dispatch"))
        self.assertEqual(status, 200)
        self.assertEqual(body.get("state"), "populated")
        self.assertEqual(len(body.get("tasks", [])), 1)
        self.assertEqual(body["tasks"][0]["origin"], "kart")


# ---------------------------------------------------------------------------
# POST /api/journal — populated | unreachable via mocked journal_writer
# ---------------------------------------------------------------------------


class JournalWriterWiringTests(unittest.TestCase):
    """INVARIANTS.md §1 + §4 + §8 — the chat LEFT-side POST endpoint.

    A successful write is always ``state=populated`` per §1 (writes have no
    distinct empty case). The writer's ``Unreachable`` becomes 503 + state=
    unreachable, distinct from the 400 bad-input codepath (which is not a
    §1 state — it's the pre-existing validation surface).
    """

    def test_journal_write_populated_on_success(self) -> None:
        """Atom accepted → 200 + state=populated + writer's id/ts round-tripped."""
        import grove_serve

        captured: dict = {}

        def _fake_write(text, *, sender="operator"):
            captured["text"] = text
            captured["sender"] = sender
            return {"ok": True, "id": "ATOM-1", "ts": "2026-08-27T00:00:00Z"}

        with _ServerHarness() as srv, mock.patch.object(
            grove_serve.journal_writer, "write_operator_turn", _fake_write
        ):
            status, body = _post_json(
                srv.url("/api/journal"),
                {"text": "hello willow", "sender": "operator"},
            )
        self.assertEqual(status, 200)
        self.assertEqual(body.get("state"), "populated")
        self.assertTrue(body.get("ok"))
        self.assertEqual(body.get("id"), "ATOM-1")
        self.assertEqual(body.get("ts"), "2026-08-27T00:00:00Z")
        # The atom bytes propagate to the writer verbatim (V5 discipline).
        self.assertEqual(captured.get("text"), "hello willow")
        self.assertEqual(captured.get("sender"), "operator")

    def test_journal_write_unreachable_when_writer_raises(self) -> None:
        """Writer raises ``Unreachable`` → 503 + state=unreachable + reason."""
        import grove_serve
        from grove.errors import Unreachable

        def _boom(_text, *, sender="operator"):  # noqa: ARG001
            raise Unreachable("willow-mcp not reachable")

        with _ServerHarness() as srv, mock.patch.object(
            grove_serve.journal_writer, "write_operator_turn", _boom
        ):
            status, body = _post_json(
                srv.url("/api/journal"),
                {"text": "hi", "sender": "operator"},
            )
        self.assertEqual(status, 503)
        self.assertEqual(body.get("state"), "unreachable")
        self.assertFalse(body.get("ok"))
        self.assertIn("willow-mcp", body.get("reason", ""))


# ---------------------------------------------------------------------------
# /api/journal/recent — populated | empty | unreachable via mocked reader
# ---------------------------------------------------------------------------


class JournalRecentWiringTests(unittest.TestCase):
    """INVARIANTS.md §1 + §8 — the chat RIGHT-side read-back's live endpoint."""

    def test_journal_recent_populated(self) -> None:
        from grove import journal_reader
        atoms = [
            {"id": "a1", "text": "first", "sender": "operator", "ts": "2026-08-27T00:00:00Z"},
            {"id": "a2", "text": "second", "sender": "watcher", "ts": "2026-08-27T00:00:01Z"},
        ]
        with _ServerHarness() as srv, \
                mock.patch.object(journal_reader, "read_recent", return_value=atoms):
            status, body = _get(srv.url("/api/journal/recent"))
        self.assertEqual(status, 200)
        self.assertEqual(body.get("state"), "populated")
        self.assertEqual(body.get("atoms"), atoms)

    def test_journal_recent_empty(self) -> None:
        from grove import journal_reader
        with _ServerHarness() as srv, \
                mock.patch.object(journal_reader, "read_recent", return_value=[]):
            status, body = _get(srv.url("/api/journal/recent"))
        self.assertEqual(status, 200)
        self.assertEqual(body.get("state"), "empty")
        self.assertEqual(body.get("atoms"), [])

    def test_journal_recent_unreachable(self) -> None:
        from grove import journal_reader
        from grove.errors import Unreachable

        def _boom(*_a, **_kw):
            raise Unreachable("willow-mcp not reachable")

        with _ServerHarness() as srv, \
                mock.patch.object(journal_reader, "read_recent", side_effect=_boom):
            status, body = _get(srv.url("/api/journal/recent"))
        self.assertEqual(status, 503)
        self.assertEqual(body.get("state"), "unreachable")
        self.assertIn("willow-mcp", body.get("reason", ""))


if __name__ == "__main__":
    unittest.main()
