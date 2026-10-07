"""`python -m onescript`: one run across invocations, on a real box layout."""

from __future__ import annotations

import json
import stat
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from onescript import __main__ as cli  # noqa: E402


def venv_with(tmp: Path, ruff: str | None) -> Path:
    v = tmp / "venv"
    (v / "bin").mkdir(parents=True)
    if ruff is not None:
        exe = v / "bin" / "ruff"
        exe.write_text(f"#!/bin/sh\necho 'ruff {ruff}'\n")
        exe.chmod(0o755)
    return v


def run(tmp: Path, venv: Path, *cmd: str) -> int:
    return cli.main(
        [
            "--box",
            str(tmp / "box"),
            "--keys",
            str(tmp / "keys" / "keys.json"),
            "--venv",
            str(venv),
            "--now",
            "2026-10-06T00:00:00Z",
            "--no-tests",
            *cmd,
        ]
    )


def rows(tmp: Path) -> list[dict]:
    text = (tmp / "box" / "record.jsonl").read_text()
    return [json.loads(x) for x in text.splitlines()]


def test_checkin_turn_checkout_is_one_run(tmp_path, capsys):
    v = venv_with(
        tmp_path,
        cli._gate_cfg(True, cli.CI.read_text(), tmp_path)["pins"]["tools"]["ruff"],
    )
    assert run(tmp_path, v, "checkin") == 0
    assert run(tmp_path, v, "turn", "a bite") == 0
    assert run(tmp_path, v, "checkout") == 0
    kinds = [r["kind"] for r in rows(tmp_path)]
    assert kinds.count("invocation") == 3
    assert "boot" in kinds and "turn_open" in kinds and "turn_close" in kinds
    assert kinds[-1] == "reconcile"
    # the first morning has no reconcile behind it, and says so
    assert "coverage: no reconcile on record" in capsys.readouterr().out
    # the second has one, read from the record by a fresh invocation
    assert run(tmp_path, v, "checkin") == 0
    assert run(tmp_path, v, "checkout") == 0
    assert "NEEDS YOU\n  · nothing" in capsys.readouterr().out


def test_every_invocation_names_its_inputs(tmp_path):
    v = venv_with(tmp_path, "0.16.7")
    run(tmp_path, v, "checkin")
    inv = rows(tmp_path)[0]
    assert inv["kind"] == "invocation" and inv["cmd"] == "checkin"
    assert set(inv["inputs"]) == {
        "governance/CONSTITUTION.md",
        ".github/workflows/tests.yml",
        "onescript",
        "git_head",
        "python",
        "venv_ruff",
    }
    assert inv["venv"] == str(v) and inv["inputs"]["venv_ruff"] == "0.16.7"


def test_the_tests_gate_never_nests(monkeypatch):
    """The gate's suite runs checkin; a checkin under the gate must not run the
    gate again (2026-10-06: an unguarded loop took the box's memory)."""
    monkeypatch.delenv(cli.NESTED, raising=False)
    assert "tests" in cli._gate_cfg(False, "", Path("/v"))
    assert cli.os.environ[cli.NESTED] == "1"
    assert "tests" not in cli._gate_cfg(False, "", Path("/v"))


def test_the_toolchain_gate_reads_the_bot_venv_not_path(tmp_path, capsys):
    v = venv_with(tmp_path, "0.15.0")
    assert run(tmp_path, v, "checkin") == 1
    out = capsys.readouterr().out
    assert "HARD CLOSE" in out and f"ruff: 0.15.0 in {v}" in out


def test_a_hard_close_holds_across_invocations(tmp_path, capsys):
    """Loki 2CC8701A F1: the hard close lives in the record, not in memory."""
    v = venv_with(tmp_path, "0.15.0")
    assert run(tmp_path, v, "checkin") == 1
    assert run(tmp_path, v, "turn", "go anyway") == 1
    assert run(tmp_path, v, "checkout") == 0
    out = capsys.readouterr().out
    assert "refused: the last check-in hard-closed" in out
    assert "HARD CLOSE · toolchain: ruff" in out and "options:" in out
    refused = [r for r in rows(tmp_path) if r["kind"] == "refused"]
    assert refused[-1]["at"] == "turn" and refused[-1]["bite"] == "go anyway"
    assert not any(r["kind"] == "turn_open" for r in rows(tmp_path))


def test_no_turn_without_a_checkin(tmp_path, capsys):
    assert run(tmp_path, venv_with(tmp_path, "0.16.7"), "turn", "x") == 1
    assert "no check-in on record" in capsys.readouterr().out


def test_the_law_reads_the_constitutions_own_ids():
    """Loki 2CC8701A F2: Article 0 and hyphenated clauses are law too."""
    ids = cli._law(cli.CONSTITUTION.read_text(encoding="utf-8"))["trace_ids"]
    assert {"CONST-0", "CONST-0-1", "CONST-I", "CONST-I-1"} <= set(ids)
    assert cli._law("CONST-IV-12 CONST-0-6 CONST-XII")["trace_ids"] == [
        "CONST-0-6",
        "CONST-IV-12",
        "CONST-XII",
    ]


def test_an_exposed_keys_file_is_refused(tmp_path, capsys):
    v = venv_with(tmp_path, "0.16.7")
    run(tmp_path, v, "checkin")
    k = tmp_path / "keys" / "keys.json"
    k.chmod(0o644)
    assert run(tmp_path, v, "checkin") == 2
    assert "readable beyond its owner" in capsys.readouterr().out
    assert stat.S_IMODE(k.parent.stat().st_mode) == 0o700


def test_a_venv_without_ruff_is_a_hard_close(tmp_path, capsys):
    assert run(tmp_path, venv_with(tmp_path, None), "checkin") == 1
    assert "ruff: not installed" in capsys.readouterr().out


def test_keys_never_live_in_the_box(tmp_path, capsys):
    rc = cli.main(
        [
            "--box",
            str(tmp_path / "box"),
            "--keys",
            str(tmp_path / "box" / "keys.json"),
            "--venv",
            str(venv_with(tmp_path, "0.16.7")),
            "--no-tests",  # a regressed refusal must not recurse into this suite
            "checkin",
        ]
    )
    assert rc == 2 and "can't live inside the box" in capsys.readouterr().out
    assert not (tmp_path / "box" / "keys.json").exists()


def test_the_keys_file_is_owner_only(tmp_path):
    run(tmp_path, venv_with(tmp_path, "0.16.7"), "checkin")
    mode = stat.S_IMODE((tmp_path / "keys" / "keys.json").stat().st_mode)
    assert mode == 0o600


@pytest.mark.parametrize("cmd", [("checkin",), ("turn", "x"), ("checkout",)])
def test_the_record_chain_holds_after_each_command(tmp_path, cmd):
    v = venv_with(tmp_path, "0.16.7")
    run(tmp_path, v, *cmd)
    from onescript import gate, record

    rec = record.Record(tmp_path / "box", lambda: "", "", gate.token())
    assert rec.verify_chain() == []
