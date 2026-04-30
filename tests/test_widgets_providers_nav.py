"""tests/test_widgets_providers_nav.py
b17: WGRV1  ΔΣ=42
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from widgets.providers_nav import ProviderRowSelected, ProvidersNavRow


def test_provider_row_selected_stores_name():
    msg = ProviderRowSelected("ollama")
    assert msg.name == "ollama"


def test_providers_nav_row_stores_fields():
    row = ProvidersNavRow("claude", True, "cloud")
    assert row._name == "claude"
    assert row._enabled is True
    assert row._ptype == "cloud"


def test_providers_nav_row_update_row():
    row = ProvidersNavRow("claude", True, "cloud")
    row.update_row(False, "local")
    assert row._enabled is False
    assert row._ptype == "local"
