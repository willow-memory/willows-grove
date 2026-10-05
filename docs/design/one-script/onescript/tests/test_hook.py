"""The one hook: a lookup in the record, ESCALATE when it isn't there."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

HOOK = Path(__file__).resolve().parents[2] / "hook.py"
sys.path.insert(0, str(HOOK.parent))

import hook  # noqa: E402

LS = {"tool_name": "Bash", "cwd": "/w", "tool_input": {"command": "ls"}}


def write(box: Path, *rows) -> None:
    box.mkdir(parents=True, exist_ok=True)
    data = b"".join(
        r if isinstance(r, bytes) else (json.dumps(r) + "\n").encode() for r in rows
    )
    (box / "record.jsonl").write_bytes(data)


def decision(event: dict, verdict: str) -> dict:
    act = hook.action_hash(event["tool_name"], event["cwd"], event["tool_input"])
    return {"kind": "decision", "action": act, "verdict": verdict}


def run(stdin: str, box: Path | None) -> tuple[int, dict]:
    env = {"PATH": os.environ.get("PATH", "/usr/bin:/bin")}
    if box is not None:
        env["ONESCRIPT_BOX"] = str(box)
    out = subprocess.run(
        [sys.executable, str(HOOK)],
        input=stdin,
        capture_output=True,
        text=True,
        env=env,
    )
    return out.returncode, json.loads(out.stdout)["hookSpecificOutput"]


def answer(event, box: Path | None) -> str:
    code, got = run(json.dumps(event), box)
    assert code == 0
    return got["permissionDecision"]


# ── the lookup ───────────────────────────────────────────────────────────────


def test_pass_in_the_record_allows(tmp_path):
    write(tmp_path, decision(LS, "pass"))
    assert answer(LS, tmp_path) == "allow"


def test_refused_in_the_record_denies(tmp_path):
    write(tmp_path, decision(LS, "refused"))
    assert answer(LS, tmp_path) == "deny"


def test_latest_row_wins(tmp_path):
    write(tmp_path, decision(LS, "pass"), decision(LS, "refused"))
    assert answer(LS, tmp_path) == "deny"


def test_not_in_the_record_escalates(tmp_path):
    write(tmp_path, decision(LS, "pass"))
    other = {**LS, "tool_input": {"command": "rm -rf x"}}
    _, got = run(json.dumps(other), tmp_path)
    assert got["permissionDecision"] == "ask"
    assert got["permissionDecisionReason"].startswith("ESCALATE")


def test_no_box_escalates():
    assert answer(LS, None) == "ask"


# ── what the action is ───────────────────────────────────────────────────────


def test_wording_is_not_part_of_the_action(tmp_path):
    write(tmp_path, decision(LS, "pass"))
    worded = {**LS, "tool_input": {"command": "ls", "description": "x", "timeout": 9}}
    assert answer(worded, tmp_path) == "allow"


def test_another_folder_is_another_action(tmp_path):
    write(tmp_path, decision(LS, "pass"))
    assert answer({**LS, "cwd": "/elsewhere"}, tmp_path) == "ask"


def test_hash_is_full_length_and_input_exact():
    a = hook.action_hash("Bash", "/w", {"command": "ls"})
    assert len(a) == 64
    assert a != hook.action_hash("Bash", "/w", {"command": "ls "})


# ── never fails open: each of these crashed the first version ────────────────


def test_garbled_line_escalates_everything(tmp_path):
    write(tmp_path, decision(LS, "pass"), b"{not json\n")
    _, got = run(json.dumps(LS), tmp_path)
    assert got["permissionDecision"] == "ask"
    assert "garbled" in got["permissionDecisionReason"]


def test_a_line_that_is_not_an_object_escalates(tmp_path):
    write(tmp_path, decision(LS, "pass"), b"1\n")
    assert answer(LS, tmp_path) == "ask"


def test_a_record_that_is_not_utf8_escalates(tmp_path):
    write(tmp_path, decision(LS, "pass"), b"\xff\xfe\n")
    assert answer(LS, tmp_path) == "ask"


def test_an_event_that_is_not_an_object_escalates(tmp_path):
    code, got = run("[]", tmp_path)
    assert (code, got["permissionDecision"]) == (0, "ask")


def test_an_event_that_is_not_json_escalates(tmp_path):
    code, got = run("not json", tmp_path)
    assert (code, got["permissionDecision"]) == (0, "ask")


# ── the vault ────────────────────────────────────────────────────────────────


def test_vault_is_denied_even_with_a_pass(tmp_path):
    ev = {
        "tool_name": "Read",
        "cwd": "/w",
        "tool_input": {"file_path": f"/home/s/{hook.VAULT}/k"},
    }
    write(tmp_path, decision(ev, "pass"))
    _, got = run(json.dumps(ev), tmp_path)
    assert got["permissionDecision"] == "deny"
    assert "vault" in got["permissionDecisionReason"]


def test_a_symlink_into_the_vault_is_denied(tmp_path):
    vault = tmp_path / hook.VAULT
    vault.mkdir()
    (tmp_path / "innocent").symlink_to(vault)
    ev = {
        "tool_name": "Read",
        "cwd": str(tmp_path),
        "tool_input": {"file_path": "innocent/k"},
    }
    assert answer(ev, None) == "deny"


def test_working_inside_the_vault_is_denied(tmp_path):
    ev = {**LS, "cwd": str(tmp_path / hook.VAULT / "sub")}
    assert answer(ev, None) == "deny"
