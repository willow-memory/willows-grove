"""Grove's hook manifest, checked against willow-mcp's own compiler.

`governance/proposals/2026-09-02-grove-hooks-and-skills.md` §8 check 1. The
point of loading it through `project_wiring` rather than asserting on the JSON
shape by hand is that the shape is not ours to decide — a manifest that passes
our idea of the schema and fails willow-mcp's is a manifest that will fail at
`project sync`, which is the only moment that matters.

Context worth keeping: when this was written, no project in the 27-entry
registry declared a `hook_manifest` at all. This path had never run.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

pw = pytest.importorskip(
    "willow_mcp.project_wiring",
    reason="willow-mcp is the consumer of this manifest; without it there is "
    "nothing to check the manifest against",
)

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "hooks" / "wiring.json"

#: A registry entry as `project sync` would pass one. `agent` matters: it is
#: what `_manifest_env` turns into WILLOW_APP_ID, and getting it wrong is what
#: forced the seat env to be hand-pinned in a tracked settings.json.
ENTRY = {
    "path": str(ROOT),
    "agent": "willow",
    "wiring": {"claude_settings": "project", "hook_manifest": "hooks/wiring.json"},
}


@pytest.fixture
def manifest():
    return pw._load_hook_manifest("willows-grove", ENTRY)


def test_the_manifest_loads_through_willow_mcp(manifest):
    assert manifest["version"] == 1
    assert manifest["hooks"]


def test_it_declares_the_five_rows_the_proposal_names(manifest):
    got = [(h["event"], h["action"]) for h in manifest["hooks"]]
    assert got == [
        ("session_start", "orient"),
        ("prompt_submit", "reinject"),
        ("pre_compact", "reinject"),
        ("stop", "gate"),
        ("session_end", "deposit"),
    ]


def test_it_adds_no_second_gate_on_tool_calls(manifest):
    """§7: willow-mcp's PreToolUse stays the one guard. Grove's stop gate
    gates turns, which is a different event."""
    assert not any(h["event"] == "pre_tool_use" for h in manifest["hooks"])


@pytest.mark.parametrize(
    "client,expected",
    [
        (
            "claude",
            {"SessionStart", "UserPromptSubmit", "PreCompact", "Stop", "SessionEnd"},
        ),
        (
            "cursor",
            {"sessionStart", "beforeSubmitPrompt", "preCompact", "stop", "sessionEnd"},
        ),
    ],
)
def test_it_compiles_for_both_dialects(manifest, client, expected):
    compiled = pw._compile_hook_manifest(
        "willows-grove", ENTRY, manifest, client=client
    )
    assert set(compiled) == expected


def test_the_command_is_owned_by_the_project(manifest):
    """_owned_path refuses anything escaping the root. A hook command outside
    the repo would be a project reaching past itself."""
    for client in ("claude", "cursor"):
        compiled = pw._compile_hook_manifest(
            "willows-grove", ENTRY, manifest, client=client
        )
        for entries in compiled.values():
            blob = json.dumps(entries)
            assert "hooks/grove-hook" in blob
            assert str(ROOT) in blob


def test_the_seat_env_comes_from_the_registry_not_from_a_hand_edit(manifest):
    """The whole argument of §6, in one assertion: the agent field drives the
    seat env, so nothing has to pin WILLOW_APP_ID by hand in a tracked file."""
    env = pw._manifest_env("willows-grove", ENTRY, manifest)
    assert env["WILLOW_APP_ID"] == "willow"
    assert env["WILLOW_AGENT_NAME"] == "willow"
    assert env["WILLOW_PROJECT_ROOT"] == str(ROOT)


def test_the_seat_file_env_placeholder_is_substituted(manifest):
    env = pw._manifest_env("willows-grove", ENTRY, manifest)
    assert env["GROVE_SEAT_FILE"] == str(ROOT / "hooks" / "seat.md")


# ── the artifacts the manifest points at ─────────────────────────────────────


def test_the_hook_command_exists_and_is_executable():
    cmd = ROOT / "hooks" / "grove-hook"
    assert cmd.is_file()
    assert cmd.stat().st_mode & 0o111, "grove-hook must be executable"


def test_the_seat_file_carries_the_line_the_reinject_pins():
    """§8 check 3's drift detection has to have something to detect.

    Matched against whitespace-normalised text because the anchor spans a line
    break in the file. Re-wrapping a paragraph is not drift, and a check that
    says it is gets ignored.
    """
    text = (ROOT / "hooks" / "seat.md").read_text(encoding="utf-8")
    assert "derived from the trees, never maintained by hand" in " ".join(text.split())


def test_the_manifest_still_admits_it_is_provisional():
    """§6 requires this file to be generated from sealed rows. It is not yet.
    This test fails when someone deletes the admission without building the
    derivation script — the honest failure mode is loud, not quiet."""
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    scripts = list((ROOT / "scripts").glob("*hook*"))
    if not scripts:
        assert "_provisional" in data, (
            "no derivation script exists under scripts/, so wiring.json is "
            "still hand-authored and must say so"
        )
