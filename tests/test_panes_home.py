"""tests/test_panes_home.py — desk render + home grid cells."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from panes.home import DeskData, render_desk
from widgets.card_store import BUILTIN_CARDS, load_home_cards


def test_render_desk_plain_section_labels():
    data = DeskData(running_tasks=2, pending_tasks=3, done_today=1)
    text = render_desk(data)
    assert "RUNNING[/]" in text
    assert "SYSTEM[/]" in text
    assert "2 running" in text
    assert "3 pending" in text
    assert "DONE TODAY[/]" in text
    assert "ATTENTION[/]" not in text


def test_render_desk_no_attention_section():
    data = DeskData(
        running_tasks=1,
        agents=[{"sender": "willow", "age_secs": 30}],
        sysinfo={"cpu": 12, "mem": 45},
    )
    text = render_desk(data)
    for bad in ("🔥", "📋", "⚙", "ATTENTION:", "RUNNING:"):
        assert bad not in text
    assert "ATTENTION[/]" not in text
    assert "RUNNING[/]" in text
    assert "willow" in text


def test_home_cards_dense_eight():
    assert len(BUILTIN_CARDS) == 10
    ids = [c["id"] for c in BUILTIN_CARDS]
    assert ids[0] == "user-todos"
    assert "mcp" in ids
    assert "think-map" in ids
    nav = {c["id"]: c["nav_target"] for c in BUILTIN_CARDS if c.get("nav_target")}
    assert nav["user-todos"] == "#pane-user-todos"
    assert nav["tasks"] == "#pane-tasks"
    assert nav["knowledge"] == "knowledge"


def test_load_home_cards_starts_with_my_desk():
    cards = load_home_cards()
    assert cards[0]["id"] == "user-todos"
