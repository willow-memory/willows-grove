"""tests/test_mcp_remote_tools.py — the fleet-awareness / channel-management
tools added to the remote (serve-mode) MCP surface.

Each tool is a thin wrapper over a grove_reader function that owns its own DB
connection, so these tests patch the reader and assert two things the wrapper is
responsible for: argument handling (clamping, @-stripping, defaults) and that
the result is JSON-safe (datetimes coerced to ISO strings — the MCP result must
serialize).
"""
from __future__ import annotations

from datetime import datetime, timezone

import pytest

mcp_local = pytest.importorskip("grove.mcp_local")


_DT = datetime(2026, 8, 17, 12, 0, tzinfo=timezone.utc)
_ISO = _DT.isoformat()


def test_jsonify_coerces_nested_datetimes():
    out = mcp_local._jsonify({"a": _DT, "b": [1, {"c": _DT}], "d": "x"})
    assert out == {"a": _ISO, "b": [1, {"c": _ISO}], "d": "x"}


def test_jsonify_coerces_decimal_and_set():
    from decimal import Decimal

    # Decimal is what psycopg2 hands back for NUMERIC columns; it is not
    # JSON-serializable and must become a float.
    assert mcp_local._jsonify(Decimal("1.5")) == 1.5
    assert mcp_local._jsonify({"n": Decimal("2")}) == {"n": 2.0}
    assert sorted(mcp_local._jsonify({1, 2, 3})) == [1, 2, 3]


def test_grove_agents_serializes_last_seen(monkeypatch):
    monkeypatch.setattr(
        mcp_local._grove_reader, "grove_agents",
        lambda: [{"sender": "loki", "last_seen_at": _DT, "age_secs": 5}],
    )
    out = mcp_local.grove_agents()
    assert out == [{"sender": "loki", "last_seen_at": _ISO, "age_secs": 5}]


def test_grove_fleet_status_clamps_limit(monkeypatch):
    seen = {}

    def fake(limit):
        seen["limit"] = limit
        return [{"sender": "auto", "last_seen_at": _DT}]

    monkeypatch.setattr(mcp_local._grove_reader, "grove_agent_fleet_rows", fake)
    out = mcp_local.grove_fleet_status(limit=9999)
    assert seen["limit"] == 100          # clamped to the ceiling
    assert out[0]["last_seen_at"] == _ISO


def test_grove_fleet_status_floor(monkeypatch):
    seen = {}
    monkeypatch.setattr(
        mcp_local._grove_reader, "grove_agent_fleet_rows",
        lambda limit: seen.setdefault("limit", limit) or [],
    )
    mcp_local.grove_fleet_status(limit=0)
    assert seen["limit"] == 1            # clamped to the floor


def test_grove_mentions_strips_at_and_clamps(monkeypatch):
    seen = {}

    def fake(name, limit):
        seen["name"] = name
        seen["limit"] = limit
        return [{"id": 1, "created_at": _DT, "content": "hi @auto"}]

    monkeypatch.setattr(mcp_local._grove_reader, "grove_mentions", fake)
    out = mcp_local.grove_mentions("@Auto", limit=999)
    assert seen["name"] == "Auto"
    assert seen["limit"] == 50           # clamped
    assert out[0]["created_at"] == _ISO


def test_grove_mentions_empty_handle_returns_empty(monkeypatch):
    called = {"n": 0}
    monkeypatch.setattr(
        mcp_local._grove_reader, "grove_mentions",
        lambda *a, **k: called.__setitem__("n", called["n"] + 1) or [],
    )
    assert mcp_local.grove_mentions("   @  ") == []
    assert called["n"] == 0              # never reached the reader


def test_grove_human_required_passes_flags(monkeypatch):
    seen = {}

    def fake(limit, open_only):
        seen["limit"] = limit
        seen["open_only"] = open_only
        return [{"id": 3, "title": "consent", "created_at": _DT}]

    monkeypatch.setattr(mcp_local._grove_reader, "human_required_queue", fake)
    out = mcp_local.grove_human_required(limit=5, open_only=False)
    assert seen == {"limit": 5, "open_only": False}
    assert out[0]["created_at"] == _ISO


def test_grove_create_channel_delegates(monkeypatch):
    seen = {}

    def fake(name, description):
        seen["name"] = name
        seen["description"] = description
        return {"ok": True, "channel": {"id": 7, "name": name}}

    monkeypatch.setattr(mcp_local._grove_reader, "grove_create_text_channel", fake)
    out = mcp_local.grove_create_channel("Ops Room", description="planning")
    assert seen == {"name": "Ops Room", "description": "planning"}
    assert out["ok"] is True
