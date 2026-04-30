"""tests/test_panes_settings.py
b17: WGRV1  ΔΣ=42
"""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from panes.settings import _read_consent, _write_consent, ConsentToggleRow


def test_read_consent_defaults_when_missing(tmp_path):
    result = _read_consent(tmp_path / "consent.json")
    assert result == {"internet": True, "cloud_llm": True, "lan": True}


def test_read_consent_returns_values(tmp_path):
    p = tmp_path / "consent.json"
    p.write_text(json.dumps({"internet": False, "cloud_llm": True, "lan": False}))
    result = _read_consent(p)
    assert result["internet"] is False
    assert result["cloud_llm"] is True
    assert result["lan"] is False


def test_read_consent_defaults_on_malformed(tmp_path):
    p = tmp_path / "consent.json"
    p.write_text("not json{{{")
    result = _read_consent(p)
    assert result == {"internet": True, "cloud_llm": True, "lan": True}


def test_write_consent_roundtrip(tmp_path):
    p = tmp_path / "consent.json"
    _write_consent({"internet": False, "cloud_llm": False, "lan": True}, p)
    result = _read_consent(p)
    assert result["internet"] is False
    assert result["cloud_llm"] is False
    assert result["lan"] is True


def test_write_consent_never_raises(tmp_path):
    _write_consent({"internet": True}, tmp_path / "nonexistent" / "consent.json")


def test_consent_toggle_row_stores_fields():
    row = ConsentToggleRow("internet", "Internet", "Allow outbound internet", True)
    assert row._key == "internet"
    assert row._label == "Internet"
    assert row._enabled is True


def test_consent_toggle_row_toggle_flips():
    row = ConsentToggleRow("lan", "LAN", "Local network", False)
    row.action_consent_toggle()
    assert row._enabled is True
    row.action_consent_toggle()
    assert row._enabled is False
