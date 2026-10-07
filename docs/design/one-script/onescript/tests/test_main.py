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
    }
    assert inv["venv"] == str(v)


def test_the_toolchain_gate_reads_the_bot_venv_not_path(tmp_path, capsys):
    assert run(tmp_path, venv_with(tmp_path, "0.15.0"), "checkin") == 1
    out = capsys.readouterr().out
    assert "HARD CLOSE" in out and "ruff: 0.15.0 on PATH" in out


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
