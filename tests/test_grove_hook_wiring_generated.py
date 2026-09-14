"""wiring.json is generated from sealed Nestor rows — never hand-kept.

KB 20BACCD0; proposal 2026-09-02-grove-hooks-and-skills.md §6. Under PR 73
(Chunk B2 of Phase B), the source changed from the hand-kept
`hooks/wiring.source.json` to `governance/decisions/grove-hook-rows-sealed.json`
— an export of the 5 pairs the operator sealed via PR 70's Nestor bundle.
Ambient scaffolding (command, env, ide-stack pointer) moved into
`scripts/generate_grove_hook_wiring.py` as module constants.
"""

from __future__ import annotations

import copy
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "generate_grove_hook_wiring.py"
SEALED = ROOT / "governance" / "decisions" / "grove-hook-rows-sealed.json"
OUTPUT = ROOT / "hooks" / "wiring.json"

if str(ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(ROOT / "scripts"))
import generate_grove_hook_wiring as gen  # noqa: E402


def test_wiring_json_matches_generated_render():
    """The core drift pin: run the generator with --check against the
    tracked `wiring.json` and assert exit 0. Fails on either a hand-edit
    to `wiring.json` OR a sealed-record edit without regenerate."""
    assert SEALED.is_file(), (
        "governance/decisions/grove-hook-rows-sealed.json is the input"
    )
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
    """The generated file names its generator + source so a reader knows
    hand-editing it is wrong (the pin above will fail, but a reader looking
    at the file should also see the derivation trail up front)."""
    data = json.loads(OUTPUT.read_text(encoding="utf-8"))
    assert "_provisional" not in data
    assert data.get("_generated_by") == "scripts/generate_grove_hook_wiring.py"
    assert (
        data.get("_generated_from")
        == "governance/decisions/grove-hook-rows-sealed.json"
    )
    assert isinstance(data.get("hooks"), list) and data["hooks"]


def test_hand_edit_of_sealed_record_row_fails_the_pin():
    """Prove-it-can-fail plant. Mutate a row's action in a copy of the
    sealed record; assert the render's output no longer matches the
    tracked `wiring.json`. This is exactly the drift the pin catches when
    someone edits the sealed record without re-running the generator."""
    sealed = json.loads(SEALED.read_text(encoding="utf-8"))
    mutated = copy.deepcopy(sealed)
    mutated["rows"][0]["action"] = "orient-PLANTED-DRIFT"
    rendered_mutated = gen.render(mutated)
    text_mutated = json.dumps(rendered_mutated, indent=2) + "\n"
    on_disk = OUTPUT.read_text(encoding="utf-8")
    assert on_disk != text_mutated, (
        "planted mutation did not change the render output — plant is broken"
    )


def test_render_rejects_a_sealed_record_with_no_rows():
    """A sealed record with `rows: []` is a user error (they exported the
    wrong domain, or renamed a field). The generator raises rather than
    silently emitting a wiring.json with an empty hooks list."""
    import pytest

    with pytest.raises(ValueError, match="rows"):
        gen.render({"rows": []})


def test_render_rejects_a_row_missing_event_or_action():
    """Each row must have both `event` and `action` strings. A row missing
    either is a caller bug and raises rather than emitting a malformed
    hooks entry."""
    import pytest

    with pytest.raises(ValueError, match="event"):
        gen.render({"rows": [{"action": "orient"}]})
    with pytest.raises(ValueError, match="action"):
        gen.render({"rows": [{"event": "session_start"}]})
