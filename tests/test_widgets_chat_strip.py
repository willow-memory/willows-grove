"""tests/test_widgets_chat_strip.py
b17: WGRV1  ΔΣ=42
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from widgets.chat_strip import format_strip_line, truncate_content

def test_format_strip_line_basic():
    line = format_strip_line("general", "hanuman", "hello world", 80)
    assert "#general" in line
    assert "hanuman" in line
    assert "hello world" in line
    assert "▶ open" in line

def test_format_strip_line_truncates_long_content():
    long_msg = "x" * 200
    line = format_strip_line("general", "hanuman", long_msg, 80)
    assert len(line) <= 80
    assert "…" in line

def test_format_strip_line_empty_content():
    line = format_strip_line("general", "hanuman", "", 80)
    assert "#general" in line
    assert "▶ open" in line

def test_truncate_content_short():
    assert truncate_content("hello", 20) == "hello"

def test_truncate_content_exact():
    assert truncate_content("hello", 5) == "hello"

def test_truncate_content_long():
    result = truncate_content("hello world", 8)
    assert len(result) <= 8
    assert result.endswith("…")
