# tests/test_theme.py
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from grove import theme

def test_agent_color_stable():
    c1 = theme.agent_color_index("hanuman")
    c2 = theme.agent_color_index("hanuman")
    assert c1 == c2

def test_agent_color_different_names():
    colors = {theme.agent_color_index(n) for n in ["hanuman","ganesha","jeles","heimdallr"]}
    assert len(colors) > 1

def test_border_chars_complete():
    b = theme.BORDERS
    for k in ("tl","tr","bl","br","h","v"):
        assert k in b
        assert len(b[k]) == 1

def test_status_glyph_known_states():
    assert theme.status_glyph("online")  == "●"
    assert theme.status_glyph("idle")    == "○"
    assert theme.status_glyph("busy")    == "◐"
    assert theme.status_glyph("unknown") == "·"

def test_truncate():
    assert theme.truncate("hello world", 5) == "hello"
    assert theme.truncate("hi", 10) == "hi"
    assert theme.truncate("hello world", 8) == "hello..."

def test_agent_pair_and_color_index_same_slot():
    from grove.theme import _agent_idx, _AGENT_PAIR_BASE
    name = "hanuman"
    assert theme.agent_pair(name) == _AGENT_PAIR_BASE + _agent_idx(name)
