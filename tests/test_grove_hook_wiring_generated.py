"""wiring.json must be generated from wiring.source.json — never hand-kept.

KB 20BACCD0; proposal 2026-09-02-grove-hooks-and-skills.md §6.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "generate_grove_hook_wiring.py"
SOURCE = ROOT / "hooks" / "wiring.source.json"
OUTPUT = ROOT / "hooks" / "wiring.json"


def test_wiring_json_matches_generated_render():
    assert SOURCE.is_file(), "hooks/wiring.source.json is the editable input"
    assert OUTPUT.is_file(), "hooks/wiring.json must exist (run the generator)"
    proc = subprocess.run(
        [sys.executable, str(SCRIPT), "--check"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 0, proc.stderr or proc.stdout


def test_wiring_json_is_not_marked_hand_authored():
    data = json.loads(OUTPUT.read_text(encoding="utf-8"))
    assert "_provisional" not in data
    assert data.get("_generated_by") == "scripts/generate_grove_hook_wiring.py"
    assert isinstance(data.get("hooks"), list) and data["hooks"]
