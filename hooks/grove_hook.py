#!/usr/bin/env python3
# b17: GRVHK  ΔΣ=42
"""grove_hook.py — body for hooks/grove-hook <client> <action>.

Invoked only via the bash launcher (hooks/grove-hook), which resolves a
willow-capable interpreter first. See module docstring on the launcher.
"""

from __future__ import annotations

import os
import subprocess
import sys

SEAT_FILE = os.environ.get("GROVE_SEAT_FILE", "")
APP_ID = os.environ.get("WILLOW_APP_ID", "")

#: Byte-stable reinject lines. Fourth line closes the Cursor gap that
#: `codebase-memory-mcp install` already fills for Claude/Codex (SessionStart
#: reminder) but only wires Cursor to ~/.cursor/mcp.json — no session prompt.
REINJECT = (
    "Three-state: populated / empty / unreachable — never collapsed.",
    "Decisions go to Nestor as pairs, not into prose.",
    "Check before asserting: read the artifact, not the recollection of it.",
    "Code graph: codebase-memory-mcp (search_graph / search_code / "
    "get_architecture) before grep when the repo is indexed.",
)

_WILLOW_PRE_TOOL = frozenset(
    {"before_bash", "before_mcp", "before_write", "before_web", "before_task"}
)


def _seat_drift() -> str | None:
    if not SEAT_FILE or not os.path.isfile(SEAT_FILE):
        return f"seat file missing: {SEAT_FILE or '(unset)'}"
    text = open(SEAT_FILE, encoding="utf-8").read()
    flat = " ".join(text.split())
    anchor = "derived from the trees, never maintained by hand"
    return (
        None if anchor in flat else "seat.md no longer carries the derived-index line"
    )


def _willow_python() -> str:
    return os.environ.get("WILLOW_MCP_PYTHON", "").strip() or sys.executable


def _run_willow_module(module: str) -> int:
    return subprocess.call([_willow_python(), "-m", module], stdin=sys.stdin)


def orient() -> int:
    lines = []
    try:
        from willow_mcp import blockers

        out = blockers.collect(
            APP_ID or "willow", os.environ.get("CLAUDE_SESSION_ID", "")
        )
        if out["count"]:
            lines.append(f"blocked on {out['count']}:")
            for item in out["items"]:
                lines.append(f"  - {item['summary']}")
                lines.append(f"    -> {item['effect']}")
    except Exception as exc:
        lines.append(f"blockers unreadable: {exc}")

    drift = _seat_drift()
    if drift:
        lines.append(f"seat drift: {drift}")

    if lines:
        print("\n".join(lines), file=sys.stderr)
    return 0


def session_start() -> int:
    rc = _run_willow_module("willow_mcp.session_start_hook")
    orient()
    return rc


def reinject() -> int:
    drift = _seat_drift()
    payload = list(REINJECT)
    if drift:
        payload.append(f"(seat drift: {drift})")
    print("\n".join(payload))
    return 0


def before_stop() -> int:
    return _run_willow_module("willow_mcp.stop_lint_hook")


def session_end() -> int:
    rc = _run_willow_module("willow_mcp.session_stop_hook")
    deposit()
    return rc


def unimplemented(action: str) -> int:
    print(
        f"grove-hook: {action} is declared but not built yet — failing open. "
        f"See proposal §3.",
        file=sys.stderr,
    )
    return 0


def gate() -> int:
    return unimplemented("gate")


def deposit() -> int:
    return unimplemented("deposit")


def main(argv: list[str]) -> int:
    if len(argv) < 3:
        print("usage: grove-hook <client> <action>", file=sys.stderr)
        return 0
    action = argv[2]
    if action == "session_start":
        return session_start()
    if action == "orient":
        return orient()
    if action == "reinject":
        return reinject()
    if action in _WILLOW_PRE_TOOL:
        return _run_willow_module("willow_mcp.pre_tool_hook")
    if action == "before_stop":
        return before_stop()
    if action == "session_end":
        return session_end()
    if action == "gate":
        return gate()
    if action == "deposit":
        return deposit()
    print(f"grove-hook: unknown action {action!r} — failing open", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
