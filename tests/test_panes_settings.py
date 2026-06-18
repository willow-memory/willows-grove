"""tests/test_panes_settings.py — consent I/O."""
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from panes.settings import format_health_block, read_consent, write_consent


def test_read_consent_defaults(tmp_path: Path, monkeypatch):
    monkeypatch.delenv("WILLOW_ROOT", raising=False)
    monkeypatch.delenv("WILLOW_SETTINGS_GLOBAL", raising=False)
    consent = read_consent(tmp_path / "missing.json")
    assert consent == {"internet": True, "cloud_llm": True, "lan": True}


def test_write_and_read_consent(tmp_path: Path):
    path = tmp_path / "settings.global.json"
    write_consent({"internet": False, "cloud_llm": True, "lan": False}, path)
    data = read_consent(path)
    assert data["internet"] is False
    assert data["lan"] is False
    stored = json.loads(path.read_text(encoding="utf-8"))
    assert stored["consent"]["internet"] is False


def test_format_health_block():
    block = format_health_block({
        "pg": {"ok": True, "detail": "12 atoms"},
        "ollama": {"ok": True, "count": 2},
        "kart": {"ok": True, "running": 1, "queued": 0},
        "soil": {"ok": True},
        "mcp": {"count": 2, "serve_up": False},
    })
    assert "Postgres" in block
    assert "12 atoms" in block
