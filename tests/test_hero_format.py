"""tests/test_hero_format.py — hero band formatters."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from grove.apps.hero_format import (
    format_collapsed_strip_markup,
    format_ground_footer_plain,
    format_hero_info_markup,
)


def _sample_stats(*, live: bool = False, model: str = "") -> dict:
    return {
        "vitals": {
            "pg": {"ok": True, "detail": "540 atoms"},
            "ollama": {"ok": True, "count": 4},
            "kart": {"ok": True, "running": 1, "queued": 2},
            "ledger": {"ok": True},
        },
        "sys": {"cpu": 12, "mem": 34, "disk": 56, "temp": 44},
        "agents": {
            "rows": [{"sender": "hanuman", "ui_state": "running"}],
            "top_agent": "hanuman",
        },
        "channels": {"unread": 0, "hot_channel": ""},
        "routing": None,
        "grove_live": live,
        "grove_model": model,
    }


def test_ground_footer_idle_no_model():
    line = format_ground_footer_plain(_sample_stats(), 120)
    assert "⌁ Grove idle" in line
    assert "mistral" not in line
    assert "540 atoms" in line


def test_ground_footer_live_shows_model():
    line = format_ground_footer_plain(_sample_stats(live=True, model="qwen2.5:3b"), 120)
    assert "⌁ Grove live" in line
    assert "qwen2.5:3b" in line


def test_hero_info_idle():
    text = format_hero_info_markup(_sample_stats())
    assert "idle" in text
    assert "hanuman" in text
    assert "BETA" not in text


def test_collapsed_strip_idle():
    text = format_collapsed_strip_markup(_sample_stats(), ", . ✿")
    assert "idle" in text
    assert "✿" in text or "," in text
