"""The one hook: a lookup in the record, ESCALATE when it isn't there."""

import json
import subprocess
import sys
from pathlib import Path

HOOK = Path(__file__).resolve().parents[2] / "hook.py"
sys.path.insert(0, str(HOOK.parent))

import hook  # noqa: E402

LS = {"tool_name": "Bash", "tool_input": {"command": "ls"}}


def write(box: Path, *rows) -> None:
    box.mkdir(parents=True, exist_ok=True)
    (box / "record.jsonl").write_text(
        "".join(r if isinstance(r, str) else json.dumps(r) + "\n" for r in rows)
    )


def decision(event: dict, verdict: str) -> dict:
    act = hook.action_hash(event["tool_name"], event["tool_input"])
    return {"kind": "decision", "action": act, "verdict": verdict}


def run(event: dict, box: Path | None) -> dict:
    env = {"PATH": "/usr/bin:/bin"}
    if box is not None:
        env["ONESCRIPT_BOX"] = str(box)
    out = subprocess.run(
        [sys.executable, str(HOOK)],
        input=json.dumps(event),
        capture_output=True,
        text=True,
        env=env,
        check=True,
    )
    return json.loads(out.stdout)["hookSpecificOutput"]


def test_pass_in_the_record_allows(tmp_path):
    write(tmp_path, decision(LS, "pass"))
    assert run(LS, tmp_path)["permissionDecision"] == "allow"


def test_refused_in_the_record_denies(tmp_path):
    write(tmp_path, decision(LS, "refused"))
    assert run(LS, tmp_path)["permissionDecision"] == "deny"


def test_latest_row_wins(tmp_path):
    write(tmp_path, decision(LS, "pass"), decision(LS, "refused"))
    assert run(LS, tmp_path)["permissionDecision"] == "deny"


def test_not_in_the_record_escalates(tmp_path):
    write(tmp_path, decision(LS, "pass"))
    other = {"tool_name": "Bash", "tool_input": {"command": "rm -rf x"}}
    got = run(other, tmp_path)
    assert got["permissionDecision"] == "ask"
    assert got["permissionDecisionReason"].startswith("ESCALATE")


def test_no_box_escalates():
    assert run(LS, None)["permissionDecision"] == "ask"


def test_garbled_line_escalates_everything(tmp_path):
    write(tmp_path, decision(LS, "pass"), "{not json\n")
    got = run(LS, tmp_path)
    assert got["permissionDecision"] == "ask"
    assert "garbled" in got["permissionDecisionReason"]


def test_vault_is_denied_even_with_a_pass(tmp_path):
    ev = {"tool_name": "Read", "tool_input": {"file_path": "/home/s/sean-data-vault/k"}}
    write(tmp_path, decision(ev, "pass"))
    got = run(ev, tmp_path)
    assert got["permissionDecision"] == "deny"
    assert "vault" in got["permissionDecisionReason"]


def test_hash_is_full_length_and_input_exact():
    a = hook.action_hash("Bash", {"command": "ls"})
    assert len(a) == 64
    assert a != hook.action_hash("Bash", {"command": "ls "})
