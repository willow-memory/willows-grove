# b17: WGRV1 ΔΣ=42
"""tests/test_human_required_reader.py — the desk reads the queue the fleet files.

willow-mcp's human_required_list is stubbed: nothing here starts willow-mcp.
"""

from __future__ import annotations

import json
import sys
import textwrap
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from grove import human_required_reader as hrr  # noqa: E402
from grove import journal_reader  # noqa: E402
from grove import mcp_local  # noqa: E402
from grove import willow_mcp_client as wmc  # noqa: E402
from grove.errors import Unreachable  # noqa: E402

import grove_html  # noqa: E402


def _item(i, priority="normal", when="2026-10-30T10:00:00Z", status="open"):
    return {
        "id": f"id{i}",
        "kind": "review",
        "title": f"t{i}",
        "summary": "s",
        "priority": priority,
        "status": status,
        "source_agent": "willow-bot",
        "source_ref": f"r{i}",
        "created_at": when,
    }


def test_open_items_come_priority_first_then_newest(monkeypatch):
    items = [
        _item(1, "normal", "2026-10-29T00:00:00Z"),
        _item(2, "high", "2026-10-01T00:00:00Z"),
        _item(3, "normal", "2026-10-30T00:00:00Z"),
        _item(4, "urgent", "2026-09-23T00:00:00Z"),
        _item(5, "high", "2026-10-30T00:00:00Z"),
        _item(6, "normal", status="resolved"),
    ]
    monkeypatch.setattr(
        hrr._wmc, "call_tool", lambda name, args: {"items": items, "stats": {"open": 5}}
    )
    doc = hrr.read_open(limit=50)
    assert [i["id"] for i in doc["items"]] == ["id4", "id5", "id2", "id3", "id1"]
    assert doc["open"] == 5 and doc["stats"] == {"open": 5}


def test_the_whole_open_queue_is_sorted_before_the_page_is_cut(monkeypatch):
    """2026-10-31: 139 open, 100 asked for, newest first, so the oldest 39
    (two urgent among them) never reached the sort, and the page heading
    read the length of the page."""
    newest = [_item(i, "normal", f"2026-10-30T{i % 24:02d}:00:00Z") for i in range(138)]
    urgent = _item(999, "urgent", "2026-09-23T00:00:00Z")
    asked = {}

    def answer(name, args):
        asked.update(args)
        return {
            "items": (newest + [urgent])[: args["limit"]],
            "stats": {"open": 139, "resolved": 400},
        }

    monkeypatch.setattr(hrr._wmc, "call_tool", answer)
    doc = hrr.read_open(limit=50)
    assert asked["limit"] >= 139
    assert doc["items"][0]["id"] == "id999"
    assert doc["open"] == 139 and doc["shown"] == 50 and len(doc["items"]) == 50


def test_open_is_never_less_than_what_was_read(monkeypatch):
    items = [_item(i) for i in range(3)]
    monkeypatch.setattr(
        hrr._wmc, "call_tool", lambda name, args: {"items": items, "stats": {"open": 1}}
    )
    assert hrr.read_open()["open"] == 3
    monkeypatch.setattr(hrr._wmc, "call_tool", lambda name, args: {"items": items})
    doc = hrr.read_open(limit=2)
    assert doc["open"] == 3 and doc["shown"] == 2


def test_the_reader_asks_as_willow_grove_for_open_items(monkeypatch):
    asked = {}
    monkeypatch.setattr(
        hrr._wmc,
        "call_tool",
        lambda name, args: asked.update(name=name, **args) or {"items": []},
    )
    assert hrr.read_open()["items"] == []
    assert (
        asked["name"] == "human_required_list"
        and asked["app_id"] == "willow-grove"
        and asked["status"] == "open"
    )


def test_a_refusal_is_unreachable_with_willow_mcps_reason_never_empty(monkeypatch):
    monkeypatch.setattr(
        hrr._wmc,
        "call_tool",
        lambda name, args: {
            "error": "gate denied: 'willow-grove' not permitted for 'human_required_list'"
        },
    )
    with pytest.raises(Unreachable) as e:
        hrr.read_open()
    assert "willow-mcp refused" in e.value.reason and "not permitted" in e.value.reason


def test_no_answer_is_unreachable_and_says_why_when_the_child_said(monkeypatch):
    monkeypatch.setattr(hrr._wmc, "call_tool", lambda name, args: None)
    monkeypatch.setattr(
        hrr._wmc.get_client(),
        "_last_error",
        "willow-mcp exited 1: RetiredHomeError: Set WILLOW_HOME",
    )
    with pytest.raises(Unreachable) as e:
        hrr.read_open()
    assert "Set WILLOW_HOME" in e.value.reason


def test_several_json_blocks_are_the_list_they_came_as():
    blocks = [
        {"type": "text", "text": json.dumps({"id": "a", "content": "x"})},
        {"type": "text", "text": json.dumps({"id": "b", "content": "y"})},
    ]
    assert wmc._payload_from_content(blocks) == [
        {"id": "a", "content": "x"},
        {"id": "b", "content": "y"},
    ]
    assert wmc._payload_from_content(blocks[:1]) == {"id": "a", "content": "x"}
    assert (
        wmc._payload_from_content([{"type": "text", "text": "plain words"}])
        == "plain words"
    )


def test_a_one_entry_journal_is_one_atom_not_empty():
    atoms = journal_reader._atoms_from_payload(
        {"id": "E1", "content": "hello", "created_at": "2026-10-30T00:00:00Z"}
    )
    assert len(atoms) == 1


def test_an_sdk2_error_result_is_an_error_not_a_payload():
    class Text:
        text = "gate denied: 'willow-grove' not permitted"

    class Result:  # SDK 2.x: is_error, and the error as plain text
        is_error = True
        structured_content = None
        content = [Text()]

    assert wmc._parse_async_tool_result(Result()) == {"error": "tool_error"}, (
        "never the error text as a payload"
    )


def test_a_child_that_exits_leaves_its_last_words(tmp_path):
    script = tmp_path / "dies.py"
    script.write_text(
        textwrap.dedent("""
        import sys
        sys.stdin.readline()
        print("Traceback (most recent call last):", file=sys.stderr)
        print("RetiredHomeError: the default willow home has been retired. Set WILLOW_HOME", file=sys.stderr)
        sys.exit(1)
    """)
    )
    c = wmc.WillowMcpClient()
    c._url = ""
    c._stdio_argv = [sys.executable, str(script)]
    c._available = True
    assert c.call_tool("kb_journal_read", {}) is None
    assert (
        c.last_error().startswith("willow-mcp exited 1: RetiredHomeError")
        and "Set WILLOW_HOME" in c.last_error()
    )


def test_the_grove_tool_reads_the_live_queue_for_open_items(monkeypatch):
    monkeypatch.setattr(
        hrr, "read_open", lambda limit=50: {"items": [_item(1)], "stats": {}, "open": 1}
    )
    monkeypatch.setattr(
        mcp_local._grove_reader,
        "human_required_queue",
        lambda **kw: pytest.fail("the June table isn't the queue"),
    )
    assert [i["id"] for i in mcp_local.grove_human_required(limit=5)] == ["id1"]


def test_the_page_mounts_the_queue_on_its_live_endpoint():
    html = grove_html.render_page()
    assert (
        '<grove-human-required data-source="/api/human_required"></grove-human-required>'
        in html
    )
    assert "/web/components/grove-human-required.js" in html


def willow_home_gaps(template: str) -> list[str]:
    """What a grove-serve unit template lacks for the page to reach willow-mcp:
    the WILLOW_HOME line its stdio child inherits, and the install example's
    fill-in for it. Empty when it has both."""
    gaps = []
    if "Environment=WILLOW_HOME=@WILLOW_HOME@" not in template:
        gaps.append("no Environment=WILLOW_HOME=@WILLOW_HOME@")
    if "s#@WILLOW_HOME@#" not in template:
        gaps.append("the install example never fills @WILLOW_HOME@")
    return gaps


def test_a_template_without_willow_home_is_caught():
    planted = "[Service]\nEnvironment=WILLOW_DB_URL=@DB_URL@\nExecStart=@WORKDIR@/scripts/grove-serve-run\n"
    assert willow_home_gaps(planted) == [
        "no Environment=WILLOW_HOME=@WILLOW_HOME@",
        "the install example never fills @WILLOW_HOME@",
    ]


def test_the_unit_template_carries_willow_home():
    text = (ROOT / "deploy" / "grove-serve.service.template").read_text()
    assert willow_home_gaps(text) == []


def test_the_route_answers_in_three_states(monkeypatch):
    from starlette.testclient import TestClient

    import grove_serve

    client = TestClient(grove_serve.build_app())
    monkeypatch.setattr(
        hrr, "read_open", lambda limit=50: {"items": [_item(1)], "stats": {}, "open": 1}
    )
    got = client.get("/api/human_required")
    assert got.status_code == 200 and got.json()["state"] == "populated"
    monkeypatch.setattr(
        hrr, "read_open", lambda limit=50: {"items": [], "stats": {}, "open": 0}
    )
    assert client.get("/api/human_required").json()["state"] == "empty"

    def refused(limit=50):
        raise Unreachable("willow-mcp refused: gate denied")

    monkeypatch.setattr(hrr, "read_open", refused)
    got = client.get("/api/human_required")
    assert got.status_code == 503 and got.json() == {
        "state": "unreachable",
        "reason": "willow-mcp refused: gate denied",
    }
