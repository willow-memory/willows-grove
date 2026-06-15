"""tests/test_panes_providers.py — provider registry read."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from panes.providers import read_providers


def test_read_providers_includes_ollama(monkeypatch):
    monkeypatch.setattr(
        "panes.providers._ollama_models",
        lambda: ["llama3:latest"],
    )
    providers = read_providers()
    names = [p["name"] for p in providers]
    assert "ollama" in names
    ollama = next(p for p in providers if p["name"] == "ollama")
    assert ollama["enabled"] is True
    assert ollama["models"] == ["llama3:latest"]
