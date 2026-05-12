"""tests/test_panes_routing.py
b17: WGRV1  ΔΣ=42
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from unittest.mock import patch
from panes.routing import fetch_routing

def test_fetch_routing_no_db():
    with patch("grove_reader.routing_decisions", side_effect=Exception("no db")):
        rows = fetch_routing()
    assert rows == []
