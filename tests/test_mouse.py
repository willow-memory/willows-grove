"""Tests for HitMap mouse region routing.
b17: WDASH  ΔΣ=42
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from grove.mouse import HitRegion, HitMap


def test_hitmap_resolve_exact():
    hm = HitMap()
    hm.register(HitRegion(y=0, x=0, h=10, w=40, app_id="chat"))
    assert hm.resolve(5, 20) == "chat"


def test_hitmap_resolve_miss():
    hm = HitMap()
    hm.register(HitRegion(y=0, x=0, h=10, w=40, app_id="chat"))
    assert hm.resolve(15, 50) is None


def test_hitmap_last_registered_wins():
    hm = HitMap()
    hm.register(HitRegion(y=0, x=0, h=10, w=40, app_id="chat"))
    hm.register(HitRegion(y=0, x=0, h=10, w=40, app_id="models"))
    assert hm.resolve(5, 20) == "models"


def test_hitmap_clear():
    hm = HitMap()
    hm.register(HitRegion(y=0, x=0, h=10, w=40, app_id="chat"))
    hm.clear()
    assert hm.resolve(5, 20) is None


def test_local_coords():
    hm = HitMap()
    hm.register(HitRegion(y=5, x=10, h=20, w=60, app_id="chat"))
    assert hm.local_coords(12, 25) == (7, 15)
