"""The operator's verifier name never lands in the tracked settings block.

`WILLOW_OPERATOR_VERIFIER` opts the session_start hook into the presence
pinentry and the Claude seat needs it — but it is a person's name, and this
is a public repo. It rides in the gitignored `.claude/settings.local.json`,
written by the same sync so the seat still attests at boot; the tracked
`.claude/settings.json` must never carry it, and `--check` refuses one that
does. (Operator, 2026-09-14: "item 1 has a hardcoded path in it".)
"""

from __future__ import annotations

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


def _entry_with_verifier(name: str = "a real person") -> dict:
    entry = sync._entry()
    entry["env"] = {**(entry.get("env") or {}), "WILLOW_OPERATOR_VERIFIER": name}
    return entry


def test_the_rendered_tracked_block_never_carries_the_verifier():
    entry = _entry_with_verifier()
    claude = sync._render_claude(sync._load_pw(), entry)
    assert "WILLOW_OPERATOR_VERIFIER" not in claude["env"]
    assert "a real person" not in json.dumps(claude)


def test_the_verifier_goes_to_the_local_seat_file_and_nothing_else_moves(
    tmp_path, monkeypatch
):
    local = tmp_path / "settings.local.json"
    local.write_text(
        json.dumps(
            {
                "env": {"WILLOW_HOME": "/somewhere"},
                "permissions": {"allow": ["Read(*)"]},
            }
        )
        + "\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(sync, "CLAUDE_LOCAL", local)

    changed = sync._write_local_seat_env(sync._local_seat_env(_entry_with_verifier()))
    assert changed is True
    data = json.loads(local.read_text(encoding="utf-8"))
    assert data["env"]["WILLOW_OPERATOR_VERIFIER"] == "a real person"
    assert data["env"]["WILLOW_HOME"] == "/somewhere"
    assert data["permissions"] == {"allow": ["Read(*)"]}
    # idempotent: a second write with the same value changes nothing
    assert (
        sync._write_local_seat_env({"WILLOW_OPERATOR_VERIFIER": "a real person"})
        is False
    )


def test_the_local_seat_file_is_created_when_absent(tmp_path, monkeypatch):
    local = tmp_path / "nested" / "settings.local.json"
    monkeypatch.setattr(sync, "CLAUDE_LOCAL", local)
    assert sync._write_local_seat_env({"WILLOW_OPERATOR_VERIFIER": "x"}) is True
    assert json.loads(local.read_text(encoding="utf-8")) == {
        "env": {"WILLOW_OPERATOR_VERIFIER": "x"}
    }


def test_nothing_is_written_when_no_verifier_is_configured(tmp_path, monkeypatch):
    local = tmp_path / "settings.local.json"
    monkeypatch.setattr(sync, "CLAUDE_LOCAL", local)
    entry = sync._entry()
    entry["env"] = {
        k: v
        for k, v in (entry.get("env") or {}).items()
        if k != "WILLOW_OPERATOR_VERIFIER"
    }
    assert sync._local_seat_env(entry) == {}
    assert sync._write_local_seat_env({}) is False
    assert not local.exists()


def test_check_refuses_a_tracked_block_that_carries_the_verifier(
    tmp_path, monkeypatch, capsys
):
    """Planted: the tracked file with the name in its env. The drift gate must
    name it, whatever else matches."""
    _, claude = sync.render()
    fake = tmp_path / "settings.json"
    seeded = json.loads(json.dumps(claude))
    seeded["env"]["WILLOW_OPERATOR_VERIFIER"] = "a real person"
    fake.write_text(json.dumps(seeded, indent=2) + "\n", encoding="utf-8")
    monkeypatch.setattr(sync, "CLAUDE_OUT", fake)
    monkeypatch.setattr(sync, "CURSOR_OUT", tmp_path / "absent-cursor.json")

    assert sync.check() == 1
    err = capsys.readouterr().err
    assert "WILLOW_OPERATOR_VERIFIER" in err and "settings.local.json" in err


def test_the_tracked_settings_on_disk_carry_no_verifier():
    """The real file, as committed."""
    tracked = json.loads(
        (ROOT / ".claude" / "settings.json").read_text(encoding="utf-8")
    )
    assert "WILLOW_OPERATOR_VERIFIER" not in (tracked.get("env") or {})
