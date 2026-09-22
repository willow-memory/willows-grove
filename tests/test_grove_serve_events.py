"""tests/test_grove_serve_events.py — WS /events/{seat} (sealed 13330d1c).

Uses Starlette's TestClient websocket support against grove_serve.build_app()
directly (no live uvicorn socket needed for these — an uvicorn-backed check
is a follow-on the desk runs after merge, per the assignment). The client's
reported peer address is set per test via TestClient(..., client=(host, port))
so both the loopback-allowed and non-loopback-refused paths are exercised.

grove_serve._events reads through grove_reader.grove_events_since — patched
per test to a fake paged reader, except the F1 tests below, which exercise
the REAL reader with only grove_db.get_connection patched to fail, per
Loki FA0EFB5F's instruction to prove the fix against the actual connection
path rather than a mock that already assumes it away.
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
from starlette.websockets import WebSocketDisconnect  # noqa: E402

import grove_db  # noqa: E402
import grove_serve  # noqa: E402
from grove.errors import Unreachable  # noqa: E402


_LOOPBACK_CLIENT = ("127.0.0.1", 51000)
_REMOTE_CLIENT = ("203.0.113.5", 51000)


def _client(peer=_LOOPBACK_CLIENT) -> TestClient:
    return TestClient(grove_serve.build_app(), client=peer)


def _fake_paged_reader(all_rows):
    """A stand-in for grove_reader.grove_events_since: ascending,
    since_id-bounded, limit-bounded — the same contract the real function
    promises, over an in-memory list instead of Postgres."""

    def _reader(_seat, *, since_id=0, limit=200):
        page = sorted(
            (r for r in all_rows if int(r["id"]) > since_id), key=lambda r: r["id"]
        )
        return page[:limit]

    return _reader


class EventsRouteRegistrationTests(unittest.TestCase):
    def test_route_registered_on_served_app(self) -> None:
        app = grove_serve.build_app()
        paths = [getattr(r, "path", None) for r in app.routes]
        self.assertIn("/events/{seat}", paths)


class EventsNonLoopbackTests(unittest.TestCase):
    def test_non_loopback_client_refused(self) -> None:
        with _client(_REMOTE_CLIENT) as c:
            with self.assertRaises(WebSocketDisconnect):
                with c.websocket_connect("/events/hanuman"):
                    pass


class EventsEmptyStateTests(unittest.TestCase):
    def test_fake_reader_empty_sends_empty_state_frame(self) -> None:
        with (
            patch.object(
                grove_serve.grove_reader, "grove_events_since", lambda *a, **kw: []
            ),
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
                grove_serve.grove_reader, "grove_events_since", _fake_paged_reader(rows)
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
                grove_serve.grove_reader, "grove_events_since", _fake_paged_reader(rows)
            ),
            _client() as c,
        ):
            with c.websocket_connect("/events/hanuman?since_id=1") as ws:
                state = ws.receive_json()
                frame = ws.receive_json()
        self.assertEqual(state, {"state": "populated", "reason": ""})
        self.assertEqual(frame["id"], 2)
        self.assertEqual(frame["content"], "new")


class EventsPagingTests(unittest.TestCase):
    """Loki FA0EFB5F F2: grove_inbox_bundle kept only the newest 35 by id,
    so a bigger backlog silently lost its oldest rows under state
    'populated'. grove_events_since pages ascending instead; these tests
    pin that 60 unread rows all arrive, in order, and that a disconnect
    mid-backlog followed by a reconnect at the last delivered id sees
    neither a gap nor a duplicate."""

    def test_60_unread_rows_deliver_1_through_60_in_order(self) -> None:
        rows = [
            {"id": i, "channel": "hanuman", "sender": "willow", "content": f"m{i}"}
            for i in range(1, 61)
        ]
        with (
            patch.object(
                grove_serve.grove_reader, "grove_events_since", _fake_paged_reader(rows)
            ),
            patch.object(grove_serve, "_EVENTS_PAGE_SIZE", 10),
            _client() as c,
        ):
            with c.websocket_connect("/events/hanuman") as ws:
                state = ws.receive_json()
                received = [ws.receive_json()["id"] for _ in range(60)]
        self.assertEqual(state, {"state": "populated", "reason": ""})
        self.assertEqual(received, list(range(1, 61)))

    def test_disconnect_and_reconnect_at_last_id_has_no_gap_or_duplicate(self) -> None:
        rows = [
            {"id": i, "channel": "hanuman", "sender": "willow", "content": f"m{i}"}
            for i in range(1, 61)
        ]
        reader = _fake_paged_reader(rows)
        with (
            patch.object(grove_serve.grove_reader, "grove_events_since", reader),
            patch.object(grove_serve, "_EVENTS_PAGE_SIZE", 10),
            _client() as c,
        ):
            with c.websocket_connect("/events/hanuman") as ws:
                ws.receive_json()  # state frame
                first_batch = [ws.receive_json()["id"] for _ in range(25)]
            # `with` exit above closes the client side — a mid-backlog
            # disconnect. Reconnect at the last id this connection actually
            # received (not the id the server may have queued to send next).
            last_id = first_batch[-1]
            with c.websocket_connect(f"/events/hanuman?since_id={last_id}") as ws2:
                state2 = ws2.receive_json()
                second_batch = [ws2.receive_json()["id"] for _ in range(35)]
        self.assertEqual(first_batch, list(range(1, 26)))
        self.assertEqual(state2, {"state": "populated", "reason": ""})
        self.assertEqual(second_batch, list(range(26, 61)))
        # No gap (26 immediately follows 25) and no duplicate (25 not resent).
        self.assertNotIn(25, second_batch)


class EventsUnreachableTests(unittest.TestCase):
    def test_reader_raising_unreachable_sends_unreachable_frame_and_stays_open(
        self,
    ) -> None:
        def _boom(*_a, **_kw):
            raise Unreachable("test — DSN gone")

        with (
            patch.object(grove_serve.grove_reader, "grove_events_since", _boom),
            patch.object(grove_serve, "_EVENTS_POLL_INTERVAL_S", 0.05),
            _client() as c,
        ):
            with c.websocket_connect("/events/hanuman") as ws:
                frame = ws.receive_json()
                # Socket stays open and re-probes: a second unreachable
                # frame arrives rather than the connection closing.
                second = ws.receive_json()
        # Redacted (Loki FA0EFB5F F1): reason is type-based, not the raw
        # Unreachable.reason text (which a real reader's psycopg2 message
        # could ride inside of).
        self.assertEqual(frame, {"state": "unreachable", "reason": "database error"})
        self.assertEqual(second, {"state": "unreachable", "reason": "database error"})


class EventsF1RealReaderConnectFailureTests(unittest.TestCase):
    """Loki FA0EFB5F F1: grove_reader.grove_inbox_bundle used to acquire its
    pooled connection OUTSIDE its own try, so a down Postgres raised
    psycopg2.OperationalError straight through the ASGI app — no frame, an
    abrupt close. Exercised here against the REAL reader
    (grove_serve.grove_reader.grove_events_since, unpatched) with only
    grove_db.get_connection made to fail, matching the measured bug
    exactly rather than a mock that assumes the fix already works."""

    def test_get_connection_operational_error_sends_redacted_unreachable_frame(
        self,
    ) -> None:
        import psycopg2

        def _boom(*_a, **_kw):
            raise psycopg2.OperationalError(
                "could not connect to server: Connection refused\n"
                '\tIs the server running on host "10.0.0.5" and accepting\n'
                "\tTCP/IP connections on port 5432?"
            )

        with (
            patch.object(grove_db, "get_connection", _boom),
            patch.object(grove_serve, "_EVENTS_POLL_INTERVAL_S", 0.05),
            _client() as c,
        ):
            with c.websocket_connect("/events/hanuman") as ws:
                frame = ws.receive_json()
                # Stays open and re-probes rather than closing in silence.
                second = ws.receive_json()
        self.assertEqual(frame["state"], "unreachable")
        self.assertEqual(frame["reason"], "database unreachable")
        self.assertNotIn("10.0.0.5", frame["reason"])
        self.assertNotIn("5432", frame["reason"])
        self.assertEqual(second["state"], "unreachable")


class EventsSinceIdBoundsTests(unittest.TestCase):
    """Loki FA0EFB5F Q2: since_id was parsed but unbounded — an oversized
    value would reach SQL and hand psycopg2's own error text back on the
    wire. Both cases below are refused with a state frame naming the
    field, before any reader is called (grove_events_since is left
    unpatched — these must never reach it)."""

    def test_since_id_out_of_int64_range_is_refused(self) -> None:
        with _client() as c:
            with c.websocket_connect(
                "/events/hanuman?since_id=99999999999999999999999999"
            ) as ws:
                frame = ws.receive_json()
                self.assertEqual(frame["state"], "unreachable")
                self.assertIn("since_id", frame["reason"])
                with self.assertRaises(WebSocketDisconnect):
                    ws.receive_json()

    def test_since_id_negative_is_refused(self) -> None:
        with _client() as c:
            with c.websocket_connect("/events/hanuman?since_id=-1") as ws:
                frame = ws.receive_json()
                self.assertEqual(frame["state"], "unreachable")
                self.assertIn("since_id", frame["reason"])

    def test_since_id_non_numeric_is_refused(self) -> None:
        with _client() as c:
            with c.websocket_connect("/events/hanuman?since_id=not-a-number") as ws:
                frame = ws.receive_json()
                self.assertEqual(frame["state"], "unreachable")
                self.assertIn("since_id", frame["reason"])


class EventsInboundIgnoredTests(unittest.TestCase):
    def test_inbound_text_frame_is_ignored_not_acted_on(self) -> None:
        with (
            patch.object(
                grove_serve.grove_reader, "grove_events_since", lambda *a, **kw: []
            ),
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
