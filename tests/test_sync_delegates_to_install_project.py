"""PR 2c: sync_desk_client_hooks delegates its tracked-file write to
willow-mcp's `install_project.apply_hooks`. The delegation is not decorative:
it fixes a preservation gap the previous wholesale write had. A hand-added
third-party PreToolUse row in `.claude/settings.json` must survive a re-sync.
"""

from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

import pytest

pytest.importorskip(
    "willow_mcp.install_project",
    reason="willow-mcp install_project verb ships the merge",
)

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import sync_desk_client_hooks as sync  # noqa: E402


THIRD_PARTY = {
    "matcher": "Bash",
    "hooks": [
        {"type": "command", "command": "python3 ~/my-private-guard.py"},
    ],
}


def _write_settings(path: Path, body: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(body, indent=2) + "\n", encoding="utf-8")


def _read(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _run_write(monkeypatch, out_dir: Path) -> None:
    """Point sync at a temp `.claude/settings.json` and run its writer."""
    fake_claude = out_dir / "settings.json"
    fake_cursor = out_dir / "hooks.json"
    monkeypatch.setattr(sync, "CLAUDE_OUT", fake_claude)
    monkeypatch.setattr(sync, "CURSOR_OUT", fake_cursor)
    sync.write()


def test_third_party_pretooluse_survives_resync(tmp_path, monkeypatch):
    """A user's hand-added PreToolUse entry lives across the sync."""
    fake_claude = tmp_path / "settings.json"
    _, claude = sync.render()
    # Seed on-disk with the managed block PLUS a third-party PreToolUse row.
    seed = copy.deepcopy(claude)
    seed["hooks"].setdefault("PreToolUse", [])
    seed["hooks"]["PreToolUse"].append(THIRD_PARTY)
    _write_settings(fake_claude, seed)

    monkeypatch.setattr(sync, "CLAUDE_OUT", fake_claude)
    monkeypatch.setattr(sync, "CURSOR_OUT", tmp_path / "hooks.json")
    sync.write()

    landed = _read(fake_claude)
    cmds = [h["command"] for e in landed["hooks"]["PreToolUse"] for h in e["hooks"]]
    assert any("my-private-guard.py" in c for c in cmds), (
        "third-party PreToolUse row was eaten by the sync — regression."
    )
    assert any("grove-hook" in c for c in cmds), (
        "grove-hook row must still be present after re-sync."
    )


def test_check_drift_gate_fires_on_hooks_drift(tmp_path, monkeypatch):
    """`--check` returns non-zero when on-disk hooks disagree with what the
    sync would produce. This is the CI drift gate; it must stay noisy."""
    fake_claude = tmp_path / "settings.json"
    _, claude = sync.render()
    drifted = copy.deepcopy(claude)
    # Bake a nonsense command into the on-disk file that no re-render would
    # produce: the check must call this out.
    drifted["hooks"]["PreToolUse"][0]["hooks"][0]["command"] = "echo bogus"
    _write_settings(fake_claude, drifted)

    monkeypatch.setattr(sync, "CLAUDE_OUT", fake_claude)
    monkeypatch.setattr(sync, "CURSOR_OUT", tmp_path / "hooks.json")
    rc = sync.check()
    assert rc == 1, "drift gate must fire when hooks disagree with re-render"


def test_check_drift_gate_passes_when_third_party_row_present(tmp_path, monkeypatch):
    """Preservation invariant + drift gate co-exist: adding a third-party
    row to the on-disk file does NOT trip `--check`, because after a fresh
    write `apply_hooks` would preserve it too. The check compares "what
    would land" to "what's on disk", not the fresh render alone."""
    fake_claude = tmp_path / "settings.json"
    _, claude = sync.render()
    seed = copy.deepcopy(claude)
    seed["hooks"].setdefault("PreToolUse", [])
    seed["hooks"]["PreToolUse"].append(THIRD_PARTY)
    _write_settings(fake_claude, seed)

    monkeypatch.setattr(sync, "CLAUDE_OUT", fake_claude)
    monkeypatch.setattr(sync, "CURSOR_OUT", tmp_path / "hooks.json")
    rc = sync.check()
    assert rc == 0, (
        "a third-party row must not appear as drift — the whole point of "
        "PR 2c was that the caller's block is merged over what's on disk."
    )


def test_previously_managed_grove_row_is_replaced_not_stacked(
    tmp_path,
    monkeypatch,
):
    """A stale grove-hook row from a previous sync must be replaced by the
    fresh one, not stacked next to it. This is what `_MANAGED_SIGNATURES`
    gaining the grove-hook substring buys us."""
    fake_claude = tmp_path / "settings.json"
    _, claude = sync.render()
    stale = copy.deepcopy(claude)
    # Corrupt the managed PreToolUse hooks so replacement is observable.
    for entry in stale["hooks"]["PreToolUse"]:
        for hook in entry["hooks"]:
            hook["command"] = hook["command"].replace("grove-hook", "grove-hook-STALE")
    _write_settings(fake_claude, stale)

    _run_write(monkeypatch, tmp_path)

    landed = _read(fake_claude)
    for entry in landed["hooks"]["PreToolUse"]:
        for hook in entry["hooks"]:
            assert "STALE" not in hook["command"], (
                "stale managed row survived — replacement, not merge, is "
                "the required semantic for fleet-managed rows."
            )
