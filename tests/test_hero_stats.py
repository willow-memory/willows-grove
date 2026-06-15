"""tests/test_hero_stats.py — hero stats bundle."""
import os
import sys
from unittest.mock import patch

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from grove.apps.hero_stats import fetch_hero_stats, read_sysinfo


def test_read_sysinfo_returns_metrics():
    sysinfo, snap = read_sysinfo()
    assert "cpu" in sysinfo
    assert "mem" in sysinfo
    assert isinstance(snap, tuple)


def test_fetch_hero_stats_structure():
    with patch("grove.apps.hero_stats.fetch_vitals") as fv:
        fv.return_value = {
            "pg": {"ok": True, "detail": "1 atoms"},
            "ollama": {"ok": True, "count": 2},
            "soil": {"ok": True},
            "kart": {"ok": True, "running": 0, "queued": 0},
            "grove": {"live": False, "model": ""},
        }
        with patch("grove.apps.hero_stats._ledger_ok", return_value=True):
            with patch("grove.apps.hero_stats._agents_summary", return_value={
                "rows": [], "online_count": 0, "idle_count": 0, "top_agent": "",
            }):
                with patch("grove.apps.hero_stats._channels_summary", return_value={
                    "total": 3, "unread": 0, "hot_channel": "",
                }):
                    with patch("grove.apps.hero_stats._routing_latest", return_value=None):
                        stats = fetch_hero_stats()
    assert stats["grove_live"] is False
    assert stats["grove_model"] == ""
    assert "cpu_snap" in stats
    assert stats["vitals"]["ledger"]["ok"] is True
