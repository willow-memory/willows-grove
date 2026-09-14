#!/usr/bin/env python3
# b17: GRVHK  ΔΣ=42
"""grove_hook.py — body for hooks/grove-hook <client> <action>.

Invoked only via the bash launcher (hooks/grove-hook), which resolves a
willow-capable interpreter first. See module docstring on the launcher.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SEAT_FILE = os.environ.get("GROVE_SEAT_FILE", "")
APP_ID = os.environ.get("WILLOW_APP_ID", "")

#: Words that read as "I'm claiming the work is done." A turn that ends with
#: one of these AND has no tool call this turn is what `gate` refuses on the
#: first Stop invocation. Second-round (`stop_hook_active`) is advisory.
_DONE_CLAIM_RE = re.compile(r"\b(all tests pass|done|complete)\b", re.IGNORECASE)

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


def _read_hook_stdin() -> dict[str, Any]:
    """Read the JSON payload Claude Code writes to a hook's stdin. Empty or
    invalid input reads as an empty dict so the hook fails open on shape
    changes."""
    try:
        raw = sys.stdin.read()
    except OSError:
        return {}
    if not raw.strip():
        return {}
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {}


def _iter_transcript(transcript_path: Path):
    """Yield decoded JSON entries from a Claude Code transcript (JSONL).
    Silently skips malformed lines so a corrupted transcript can't fail the
    hook itself."""
    if not transcript_path or not transcript_path.is_file():
        return
    with transcript_path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                yield json.loads(line)
            except json.JSONDecodeError:
                continue


def _turn_content_blocks(entry: dict) -> list:
    """Extract the content blocks from a transcript entry, accepting both
    the flat `entry["content"]` shape and the nested `entry["message"]["content"]`
    shape different Claude Code versions have shipped."""
    content = entry.get("content")
    if content is None:
        msg = entry.get("message")
        if isinstance(msg, dict):
            content = msg.get("content")
    if isinstance(content, list):
        return content
    if isinstance(content, str):
        return [{"type": "text", "text": content}]
    return []


def _last_assistant_turn(transcript_path: Path) -> dict | None:
    """Return the last assistant entry in the transcript, or None if no
    assistant entry exists / the file is unreadable."""
    last = None
    for entry in _iter_transcript(transcript_path):
        if entry.get("type") == "assistant" or entry.get("role") == "assistant":
            last = entry
    return last


def gate() -> int:
    """Stop-event gate: refuse a turn claiming done with no tool call this turn.
    Block once (first Stop of a turn); advisory on `stop_hook_active` (second
    and subsequent) so the flow can complete after Claude sees the block."""
    payload = _read_hook_stdin()

    if payload.get("stop_hook_active"):
        # Second-round Stop after a block: don't fight the pinentry flow the
        # approval broker §5c is designing; print an advisory and let go.
        print(
            "grove gate (advisory, stop_hook_active): allowing the turn to end.",
            file=sys.stderr,
        )
        return 0

    transcript_path_str = payload.get("transcript_path", "")
    if not transcript_path_str:
        return 0

    turn = _last_assistant_turn(Path(transcript_path_str))
    if not turn:
        return 0

    blocks = _turn_content_blocks(turn)
    text = "\n".join(
        b.get("text", "")
        for b in blocks
        if isinstance(b, dict) and b.get("type") == "text"
    )
    tool_calls = [
        b for b in blocks if isinstance(b, dict) and b.get("type") == "tool_use"
    ]

    if _DONE_CLAIM_RE.search(text) and not tool_calls:
        reason = (
            "grove gate: this turn reads 'all tests pass' / 'done' / 'complete' "
            "but has no tool call in the same turn. Run the check first, or cite "
            "the artifact that shows it passed. Second Stop invocation "
            "(stop_hook_active) will not block."
        )
        # Structured Stop hook response: `decision: block` + `reason` shows the
        # reason back to Claude, which retries. Same shape willow-mcp's stop
        # gate uses.
        print(json.dumps({"decision": "block", "reason": reason}))
        return 0

    return 0


def _deposit_dir() -> Path:
    """Where session summaries land. Honors $WILLOW_HOME (fleet convention),
    then falls back to ~/.willow/. The deposit lives at
    `<root>/deposits/<sid>.json`."""
    home = os.environ.get("WILLOW_HOME", "").strip()
    root = Path(home) if home else Path.home() / ".willow"
    return root / "deposits"


def _summarize_tool_calls(transcript_path: Path) -> dict:
    """Walk the transcript and count tool_use blocks by tool name."""
    counts: dict[str, int] = {}
    total = 0
    for entry in _iter_transcript(transcript_path):
        for block in _turn_content_blocks(entry):
            if isinstance(block, dict) and block.get("type") == "tool_use":
                name = block.get("name", "unknown")
                counts[name] = counts.get(name, 0) + 1
                total += 1
    return {"total": total, "by_tool": counts}


def deposit() -> int:
    """SessionEnd deposit: write a JSON summary of this session's tool calls
    to the deposits directory. SessionEnd cannot block per Nestor's finding;
    on any error the hook warns to stderr and exits zero. Nestor kb_journal
    + pair-proposal writes are a follow-up (design pass pending)."""
    payload = _read_hook_stdin()
    sid = (
        payload.get("session_id", "")
        or os.environ.get("CLAUDE_SESSION_ID", "")
        or "unknown"
    )
    transcript_path = Path(payload.get("transcript_path", ""))

    summary = {
        "session_id": sid,
        "app_id": APP_ID,
        "recorded_at": datetime.now(timezone.utc).isoformat(),
        "tool_calls": _summarize_tool_calls(transcript_path),
        "seat_drift": _seat_drift(),
    }
    outdir = _deposit_dir()
    try:
        outdir.mkdir(parents=True, exist_ok=True)
        (outdir / f"{sid}.json").write_text(
            json.dumps(summary, indent=2) + "\n", encoding="utf-8"
        )
    except OSError as exc:
        # SessionEnd cannot block; warn and continue.
        print(f"grove deposit: could not write under {outdir}: {exc}", file=sys.stderr)
    return 0


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
