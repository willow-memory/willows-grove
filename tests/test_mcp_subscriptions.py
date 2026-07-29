"""Resource-update fan-out after the SEP-2575 subscription rewrite.

SDK 1.x: the client opened a standing GET stream, `subscribe_resource` ran per
session, and Grove kept its own registry — a dict of `asyncio.Queue` keyed by
channel id, a lock, and one watcher task per subscription — pushing
`send_resource_updated` down each session's own stream.

SDK 2.0 (SEP-2575) removed both the standing stream and `subscribe_resource`.
A client opts in with `subscriptions/listen`, whose *response* is the stream,
and `MCPServer` registers that handler itself. Fan-out belongs to the bus, so
the registry is deleted rather than ported: Grove publishes a typed
`ResourceUpdated`, the SDK delivers it.

That moved one thing. The registry keyed queues by channel **id**, resolved at
subscribe time; the bus carries a **URI**, which is built from the channel
name. So the id→name lookup moved to publish time, and that is what
`_channel_name_for_id` is. These tests cover it, because it is the one piece of
new logic in the rewrite and it sits on a database call that can fail.

NOT covered here: end-to-end delivery to a subscribed client. That needs a real
MCP client speaking `subscriptions/listen` against a live Postgres emitting
NOTIFY, which this suite has no harness for. Stated rather than implied — see
the PR.
"""
from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

mcp_local = pytest.importorskip("grove.mcp_local")


def test_resolves_a_known_channel_id_to_its_name():
    conn = MagicMock()
    with patch.object(mcp_local.db, "get_connection", return_value=conn), \
         patch.object(mcp_local.db, "release_connection") as rel, \
         patch.object(mcp_local.db, "list_channels",
                      return_value=[{"id": 1, "name": "general"},
                                    {"id": 2, "name": "dispatch"}]):
        assert mcp_local._channel_name_for_id(2) == "dispatch"
    rel.assert_called_once_with(conn)


def test_unknown_channel_id_resolves_to_none():
    """A NOTIFY for a channel that no longer exists must not raise into the
    LISTEN thread, which would kill the reconnect loop."""
    with patch.object(mcp_local.db, "get_connection", return_value=MagicMock()), \
         patch.object(mcp_local.db, "release_connection"), \
         patch.object(mcp_local.db, "list_channels", return_value=[{"id": 1, "name": "general"}]):
        assert mcp_local._channel_name_for_id(99) is None


def test_a_database_failure_resolves_to_none_and_releases():
    """Publishing a wrong URI is worse than publishing nothing: a subscriber
    told the wrong channel changed will refetch the wrong channel and believe
    the right one is unchanged. So the failure path returns None — and must
    still hand the connection back, or the pool leaks one per failed NOTIFY."""
    conn = MagicMock()
    with patch.object(mcp_local.db, "get_connection", return_value=conn), \
         patch.object(mcp_local.db, "release_connection") as rel, \
         patch.object(mcp_local.db, "list_channels", side_effect=RuntimeError("db down")):
        assert mcp_local._channel_name_for_id(1) is None
    rel.assert_called_once_with(conn)


def test_a_connection_failure_does_not_try_to_release_nothing():
    with patch.object(mcp_local.db, "get_connection", side_effect=RuntimeError("no pool")), \
         patch.object(mcp_local.db, "release_connection") as rel:
        assert mcp_local._channel_name_for_id(1) is None
    rel.assert_not_called()


def test_the_bus_is_wired_onto_the_server():
    """Grove must publish onto the bus the SDK is fanning out from. If these are
    two different objects the publish succeeds and nothing is ever delivered —
    silent, and indistinguishable from a quiet channel."""
    from mcp.server.subscriptions import InMemorySubscriptionBus

    assert isinstance(mcp_local._bus, InMemorySubscriptionBus)


def test_published_resource_updates_reach_a_listener():
    """The publish path, end to end through the real bus.

    `publish` is a COROUTINE. The first cut of this rewrite called it straight
    from the Postgres LISTEN thread, which built a coroutine nobody awaited —
    silently delivering nothing. This test is why that was caught, so it awaits
    deliberately rather than through a sync helper that would hide the same
    mistake again.
    """
    import asyncio

    from mcp.shared.subscriptions import ResourceUpdated

    seen = []
    unsubscribe = mcp_local._bus.subscribe(seen.append)
    try:
        asyncio.run(mcp_local._bus.publish(ResourceUpdated(uri="grove://channel/general")))
    finally:
        unsubscribe()

    assert [e.uri for e in seen] == ["grove://channel/general"]


def test_the_old_per_session_registry_is_gone():
    """Regression fence. The queue registry and its lock were deleted, not left
    beside the bus — two fan-out mechanisms where one is fed and the other is
    read is how a subscription silently stops delivering."""
    assert not hasattr(mcp_local, "_subscriptions")
    assert not hasattr(mcp_local, "_subscriptions_lock")
