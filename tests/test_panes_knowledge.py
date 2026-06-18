"""tests/test_panes_knowledge.py — KB search helpers."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from panes.knowledge import atom_body_plain, humanize_content, search_kb, truncate_text


def test_truncate_text():
    assert truncate_text("hello", 10) == "hello"
    assert truncate_text("hello world", 8) == "hello wo…"


def test_humanize_content_json():
    out = humanize_content('{"a": 1}')
    assert '"a"' in out


def test_search_kb_empty_query():
    assert search_kb("") == []
    assert search_kb("   ") == []


def test_atom_body_plain_prefers_content():
    atom = {"summary": "sum", "content": '{"x": 1}'}
    body = atom_body_plain(atom)
    assert "sum" in body
    assert '"x"' in body


def test_atom_body_plain_jsonb_dict():
    atom = {"summary": "", "content": {"key": "value"}}
    body = atom_body_plain(atom)
    assert '"key"' in body
    assert "value" in body


def test_fetch_atom_accepts_hex_string_id(monkeypatch):
    captured: list[str] = []

    class FakeCursor:
        def execute(self, sql, params):
            captured.append(params[0])

        def fetchone(self):
            return ("B57E8988", "t", "s", "dom", 1.0, {"body": "x"})

    class FakeConn:
        def cursor(self):
            return FakeCursor()

        def rollback(self):
            pass

    monkeypatch.setattr(
        "panes.knowledge.grove_db.get_connection",
        lambda: FakeConn(),
    )
    monkeypatch.setattr("panes.knowledge.grove_db.release_connection", lambda _c: None)
    atom = __import__("panes.knowledge", fromlist=["fetch_atom"]).fetch_atom("B57E8988")
    assert captured == ["B57E8988"]
    assert atom is not None
    assert atom["id"] == "B57E8988"
