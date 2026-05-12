"""tests/test_panes_knowledge.py
b17: WGRV1  ΔΣ=42
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from unittest.mock import MagicMock, patch
from panes.knowledge import (
    fetch_atom,
    humanize_content,
    render_atom,
    search_kb,
    truncate_text,
)


# ── truncate_text ─────────────────────────────────────────────────────────────

def test_truncate_short():
    assert truncate_text("hello", 10) == "hello"


def test_truncate_long():
    result = truncate_text("hello world", 5)
    assert result == "hello…"
    assert len(result) == 6


# ── humanize_content ─────────────────────────────────────────────────────────


def test_humanize_plain_returns_stripped():
    assert humanize_content("  hello  ") == "hello"


def test_humanize_json_object_body_key():
    raw = '{"body": "The answer is 42.", "meta": 1}'
    out = humanize_content(raw)
    assert "answer" in out
    assert "meta: 1" in out


def test_humanize_json_array_strings():
    import json

    raw = json.dumps(["a", "b", "c"])
    out = humanize_content(raw)
    assert "a" in out and "b" in out


# ── render_atom ───────────────────────────────────────────────────────────────

def test_render_atom_is_string():
    atom = {"id": 1, "title": "T", "summary": "S", "domain": "d", "weight": 1}
    assert isinstance(render_atom(atom), str)


def test_render_atom_contains_title():
    atom = {"id": 1, "title": "My Atom", "summary": "", "domain": "test", "weight": 0}
    assert "My Atom" in render_atom(atom)


def test_render_atom_shows_id():
    atom = {"id": 42, "title": "", "summary": "", "domain": "d", "weight": 0}
    assert "42" in render_atom(atom)


def test_render_atom_missing_content_key():
    atom = {"id": 1, "title": "X", "summary": "s", "domain": "d", "weight": 0}
    out = render_atom(atom)
    assert isinstance(out, str)
    assert "CONTENT" not in out


def test_render_atom_includes_content():
    atom = {"id": 1, "title": "X", "summary": "", "domain": "d", "weight": 0,
            "content": "full text here"}
    assert "full text here" in render_atom(atom)


# ── fetch_atom ────────────────────────────────────────────────────────────────

def test_fetch_atom_returns_none_on_missing_row():
    conn = MagicMock()
    cur = MagicMock()
    conn.cursor.return_value = cur
    cur.fetchone.return_value = None
    result = fetch_atom(42, conn=conn)
    assert result is None


def test_fetch_atom_returns_dict_on_success():
    conn = MagicMock()
    cur = MagicMock()
    conn.cursor.return_value = cur
    cur.fetchone.return_value = (42, "My Title", "A summary", "test", 5, "full content")
    result = fetch_atom(42, conn=conn)
    assert result is not None
    assert result["id"] == 42
    assert result["title"] == "My Title"
    assert result["content"] == "full content"


def test_fetch_atom_returns_none_on_db_error():
    conn = MagicMock()
    cur = MagicMock()
    conn.cursor.return_value = cur
    cur.execute.side_effect = Exception("db error")
    result = fetch_atom(42, conn=conn)
    assert result is None


# ── search_kb ─────────────────────────────────────────────────────────────────

def test_search_kb_empty_query():
    assert search_kb("") == []


def test_search_kb_no_db():
    with patch("grove_db.get_connection", side_effect=Exception("no db")):
        result = search_kb("anything")
    assert result == []
