"""Tests for TabsLayout and TabBar.
b17: WDASH  ΔΣ=42
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from grove.layouts.tabs import TabsLayout, TabBar


def test_tabbar_renders_labels():
    bar = TabBar(["Chat", "Journal", "Models"])
    text = bar.render_text(active=0, width=80)
    assert "Chat" in text
    assert "Journal" in text
    assert "Models" in text


def test_tabbar_active_bracketed():
    bar = TabBar(["Chat", "Journal"])
    text = bar.render_text(active=0, width=80)
    assert "[Chat]" in text


def test_tabbar_inactive_plain():
    bar = TabBar(["Chat", "Journal"])
    text = bar.render_text(active=0, width=80)
    assert "Journal" in text
    assert "[Journal]" not in text


def test_tabs_layout_regions():
    layout = TabsLayout(tab_labels=["Chat", "Models"], rows=40, cols=120)
    regions = layout.compute_regions()
    ids = {r["id"] for r in regions}
    assert "tabbar" in ids
    assert "content" in ids
    assert "status" in ids


def test_tabs_layout_content_fills_middle():
    layout = TabsLayout(tab_labels=["Chat"], rows=40, cols=120)
    regions = layout.compute_regions()
    content = next(r for r in regions if r["id"] == "content")
    assert content["row"] > 0
    assert content["row"] + content["h"] < 40
