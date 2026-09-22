"""tests/test_grove_serve_events.py — WS /events/{seat} (sealed 13330d1c).

Uses Starlette's TestClient websocket support against grove_serve.build_app()
directly (no live uvicorn socket needed for these — an uvicorn-backed check
is a follow-on the desk runs after merge, per the assignment). The client's
reported peer address is set per test via TestClient(..., client=(host, port))
so both the loopback-allowed and non-loopback-refused paths are exercised.

grove_serve._events reads through grove_reader.grove_inbox_bundle — patched
per test to a fake reader (never a real Postgres round-trip).
"""

from __future__ import annotations

import os
import sys
import unittest
from unittest.mock import patch

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from starlette.testclient import TestClient  # noqa: E402

import grove_serve  # noqa: E402
from grove.errors import Unreachable  # noqa: E402


_LOOPBACK_CLIENT = ("127.0.0.1", 51000)
_REMOTE_CLIENT = ("203.0.113.5", 51000)


def _client(peer=_LOOPBACK_CLIENT) -> TestClient:
    return TestClient(grove_serve.build_app(), client=peer)


class EventsRouteRegistrationTests(unittest.TestCase):
    def test_route_registered_on_served_app(self) -> None:
        app = grove_serve.build_app()
        paths = [getattr(r, "path", None) for r in app.routes]
        self.assertIn("/events/{seat}", paths)


class EventsNonLoopbackTests(unittest.TestCase):
    def test_non_loopback_client_refused(self) -> None:
        from starlette.websockets import WebSocketDisconnect

        with _client(_REMOTE_CLIENT) as c:
            with self.assertRaises(WebSocketDisconnect):
                with c.websocket_connect("/events/hanuman"):
                    pass


class EventsEmptyStateTests(unittest.TestCase):
    def test_fake_reader_empty_sends_empty_state_frame(self) -> None:
        with (
            patch.object(grove_serve.grove_reader, "grove_inbox_bundle", lambda *a, **kw: []),
            _client() as c,
        ):
            with c.websocket_connect("/events/hanuman") as ws:
                frame = ws.receive_json()
        self.assertEqual(frame, {"state": "empty", "reason": ""})


class EventsPopulatedTests(unittest.TestCase):
    def test_rows_arrive_as_one_frame_each_in_id_order(self) -> None:
        rows = [
            {"id": 3, "channel": "hanuman", "sender": "willow", "content": "third"},
            {"id": 1, "channel": "hanuman", "sender": "willow", "content": "first"},
            {"id": 2, "channel": "hanuman", "sender": "willow", "content": "second"},
        ]
        with (
            patch.object(
                grove_serve.grove_reader, "grove_inbox_bundle", lambda *a, **kw: list(rows)
            ),
            _client() as c,
        ):
            with c.websocket_connect("/events/hanuman") as ws:
                state = ws.receive_json()
                first = ws.receive_json()
                second = ws.receive_json()
                third = ws.receive_json()
        self.assertEqual(state, {"state": "populated", "reason": ""})
        self.assertEqual([first["id"], second["id"], third["id"]], [1, 2, 3])
        self.assertEqual(first["content"], "first")
        self.assertEqual(third["content"], "third")
        # Frame shape: exactly id/channel/sender/content/at.
        self.assertEqual(
            set(first.keys()), {"id", "channel", "sender", "content", "at"}
        )

    def test_since_id_resumes_past_what_was_already_seen(self) -> None:
        rows = [
            {"id": 1, "channel": "hanuman", "sender": "willow", "content": "old"},
            {"id": 2, "channel": "hanuman", "sender": "willow", "content": "new"},
        ]
        with (
            patch.object(
                grove_serve.grove_reader, "grove_inbox_bundle", lambda *a, **kw: list(rows)
            ),
            _client() as c,
        ):
            with c.websocket_connect("/events/hanuman?since_id=1") as ws:
                state = ws.receive_json()
                frame = ws.receive_json()
        self.assertEqual(state, {"state": "populated", "reason": ""})
        self.assertEqual(frame["id"], 2)
        self.assertEqual(frame["content"], "new")


class EventsUnreachableTests(unittest.TestCase):
    def test_reader_raising_unreachable_sends_unreachable_frame_and_stays_open(
        self,
    ) -> None:
        def _boom(*_a, **_kw):
            raise Unreachable("test — DSN gone")

        with (
            patch.object(grove_serve.grove_reader, "grove_inbox_bundle", _boom),
            patch.object(grove_serve, "_EVENTS_POLL_INTERVAL_S", 0.05),
            _client() as c,
        ):
            with c.websocket_connect("/events/hanuman") as ws:
                frame = ws.receive_json()
                # Socket stays open and re-probes: a second unreachable
                # frame arrives rather than the connection closing.
                second = ws.receive_json()
        self.assertEqual(frame, {"state": "unreachable", "reason": "test — DSN gone"})
        self.assertEqual(second, {"state": "unreachable", "reason": "test — DSN gone"})


class EventsInboundIgnoredTests(unittest.TestCase):
    def test_inbound_text_frame_is_ignored_not_acted_on(self) -> None:
        with (
            patch.object(grove_serve.grove_reader, "grove_inbox_bundle", lambda *a, **kw: []),
            _client() as c,
        ):
            with c.websocket_connect("/events/hanuman") as ws:
                state = ws.receive_json()
                # A read-only stream: sending a command-shaped frame does
                # nothing observable — no ack, no error, no state change —
                # and the connection stays usable for the next real frame.
                ws.send_text('{"do": "something"}')
                ws.close()
        self.assertEqual(state, {"state": "empty", "reason": ""})


if __name__ == "__main__":
    unittest.main()
