"""tests/test_widgets_hero.py
b17: WGRV1  ΔΣ=42
"""
import sys, os
from unittest.mock import patch

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from widgets.hero import POSES, advance_frame, render_frame

def test_poses_exist():
    assert "L" in POSES and "C" in POSES and "R" in POSES

def test_each_pose_has_10_frames():
    for key, frames in POSES.items():
        assert len(frames) == 10, f"pose {key} has {len(frames)} frames"

def test_advance_frame_cycles():
    pose, frame = "L", 0
    with patch("widgets.hero.random.random", return_value=1.0):
        for _ in range(10):
            pose, frame = advance_frame(pose, frame)
    assert pose == "C"
    assert frame == 0

def test_advance_frame_full_cycle_returns_to_L():
    pose, frame = "L", 0
    with patch("widgets.hero.random.random", return_value=1.0):
        for _ in range(30):
            pose, frame = advance_frame(pose, frame)
    assert pose == "L"
    assert frame == 0

def test_render_frame_returns_six_lines():
    lines = render_frame("C", 4)
    assert isinstance(lines, tuple)
    assert len(lines) == 6
    assert all(isinstance(line, str) and len(line) > 0 for line in lines)
