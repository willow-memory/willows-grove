"""tests/test_panes_knowledge.py
b17: WGRV1  ΔΣ=42
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from unittest.mock import patch
from panes.knowledge import search_kb, truncate_text

def test_search_kb_no_db():
    with patch("panes.knowledge._pg_conn", side_effect=Exception("no db")):
        rows = search_kb("test query")
    assert rows == []

def test_search_kb_empty_query():
    assert search_kb("") == []

def test_truncate_short():
    assert truncate_text("hello", 20) == "hello"

def test_truncate_long():
    result = truncate_text("a" * 100, 20)
    assert len(result) <= 23
    assert result.endswith("…")
