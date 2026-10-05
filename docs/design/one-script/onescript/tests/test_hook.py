"""The hook: Read allowed, Write asks, everything else denied, never fails open."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

HOOK = Path(__file__).resolve().parents[2] / "hook.py"


def run(stdin: str) -> tuple[int, str | None]:
    out = subprocess.run(
        [sys.executable, str(HOOK)], input=stdin, capture_output=True, text=True
    )
    if out.returncode != 0:
        return out.returncode, None
    return 0, json.loads(out.stdout)["hookSpecificOutput"]["permissionDecision"]


def tool(name) -> str:
    return json.dumps({"tool_name": name, "tool_input": {}})


def test_read_is_allowed():
    assert run(tool("Read")) == (0, "allow")


def test_write_asks_the_user():
    assert run(tool("Write")) == (0, "ask")


def test_everything_else_is_denied():
    for name in ["Bash", "Edit", "Glob", "WebFetch", "Agent", "mcp__x__y"]:
        assert run(tool(name)) == (0, "deny"), name


def test_a_tool_that_does_not_exist_yet_is_denied():
    assert run(tool("SomethingNew")) == (0, "deny")


def test_no_tool_name_is_denied():
    assert run("{}") == (0, "deny")
    assert run("[]") == (0, "deny")
    assert run(tool(None)) == (0, "deny")


def test_unreadable_input_blocks():
    assert run("not json") == (2, None)
    assert run("") == (2, None)
