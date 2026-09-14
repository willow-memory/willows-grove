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
import shutil
import socket
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SEAT_FILE = os.environ.get("GROVE_SEAT_FILE", "")
APP_ID = os.environ.get("WILLOW_APP_ID", "")
SESSION_ID = os.environ.get("CLAUDE_SESSION_ID", "")

#: The Nestor UI + keep store + keyring per PR 69's sealed port row 2. The
#: reachability probe uses this port as its truth source; if that seal moves
#: in a future bundle, this constant moves with it.
_NESTOR_PORT = 8765
_NESTOR_PROBE_TIMEOUT = 0.25  # seconds; must not delay a Claude Code turn
_NESTOR_ASK_TIMEOUT = 1.5  # seconds

_NESTOR_STATUS_BOOT_LINE = {
    "not_installed": "Nestor is not on this box.",
    "installed_not_answering": "Nestor did not answer; unverified turn.",
}

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

    # Nestor-first boot line, once per session (per proposal §3):
    # "the orient line says so once" for not-installed / not-answering.
    reach = _nestor_reach()
    boot_line = _emit_boot_line_once(reach)
    if boot_line:
        lines.append(boot_line)

    if lines:
        print("\n".join(lines), file=sys.stderr)
    return 0


def session_start() -> int:
    rc = _run_willow_module("willow_mcp.session_start_hook")
    orient()
    return rc


def reinject() -> int:
    """UserPromptSubmit / PreCompact reinject. Layout (proposal §3):

    1. Nestor-first row — one line ahead of the seat lines: either an
       attributed Nestor state (`Nestor: sealed`, etc.) when reachable, or
       the one-shot boot line for `not_installed` / `installed_not_answering`.
    2. The four byte-stable REINJECT tuple entries.
    3. Seat drift indicator, if `hooks/seat.md` no longer carries the anchor.

    All go to stdout — Claude Code injects reinject stdout as context ahead
    of the model's turn."""
    hook_payload = _read_hook_stdin()
    prompt = str(hook_payload.get("prompt", ""))
    reach = _nestor_reach()

    lines: list[str] = []
    nestor_line = _nestor_context_line(prompt, reach)
    if nestor_line:
        lines.append(nestor_line)
    lines.extend(REINJECT)

    drift = _seat_drift()
    if drift:
        lines.append(f"(seat drift: {drift})")

    print("\n".join(lines))
    return 0


def before_stop() -> int:
    return _run_willow_module("willow_mcp.stop_lint_hook")


def session_end() -> int:
    rc = _run_willow_module("willow_mcp.session_stop_hook")
    deposit()
    return rc


def _nestor_reach() -> str:
    """Probe Nestor's known port and CLI. Returns one of:
    - "reachable" — 8765 accepts a TCP connection.
    - "installed_not_answering" — 8765 refuses but the `nestor` CLI is on PATH.
    - "not_installed" — 8765 refuses and there is no `nestor` CLI.

    Bounded socket timeout (250ms) so a slow probe never delays a Claude Code
    turn. Any exception on the socket side falls to the CLI check.
    """
    try:
        with socket.create_connection(
            ("127.0.0.1", _NESTOR_PORT), timeout=_NESTOR_PROBE_TIMEOUT
        ):
            return "reachable"
    except (OSError, socket.timeout):
        pass
    return "installed_not_answering" if shutil.which("nestor") else "not_installed"


def _nestor_ask(prompt: str) -> dict | None:
    """Put `prompt` to Nestor. Returns a small dict {state, age, matches?} on
    success, None on any error.

    Discovery: at execute-time this expects a `nestor ask --json <prompt>` CLI
    surface. On the operator's box `nestor-meaning` provides this. If the shape
    is different in a future nestor-meaning release, the JSON parse fails and
    the caller falls back to the "installed, not answering" path — which is
    the right behavior: an unrecognized response is not an answer.
    """
    if not prompt.strip():
        return None
    try:
        result = subprocess.run(
            ["nestor", "ask", "--json"],
            input=prompt.encode("utf-8"),
            capture_output=True,
            timeout=_NESTOR_ASK_TIMEOUT,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
        return None
    if result.returncode != 0:
        return None
    try:
        parsed = json.loads(result.stdout.decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return None
    return parsed if isinstance(parsed, dict) else None


def _status_line_sentinel_path(reach: str) -> Path:
    """Per-session flag so the boot line for `not_installed` /
    `installed_not_answering` prints once at session_start / first reinject
    and does not repeat on every prompt_submit."""
    sid = SESSION_ID or "unknown"
    return Path(f"/tmp/willow-nestor-status-{sid}-{reach}.flag")


def _emit_boot_line_once(reach: str) -> str | None:
    """Return the boot line for this state if it hasn't been emitted this
    session yet; otherwise None. Uses a /tmp sentinel keyed on session id +
    state so a transition (not_installed → installed_not_answering) still
    prints once."""
    if reach not in _NESTOR_STATUS_BOOT_LINE:
        return None
    sentinel = _status_line_sentinel_path(reach)
    if sentinel.exists():
        return None
    try:
        sentinel.touch()
    except OSError:
        # Best effort: if /tmp is unwritable, print each turn rather than
        # crash the reinject.
        pass
    return _NESTOR_STATUS_BOOT_LINE[reach]


def _nestor_context_line(prompt: str, reach: str) -> str | None:
    """One-line attributed Nestor context ahead of a turn's reinject.

    Reachable → call _nestor_ask; template a single line from its response.
    Not installed / not answering → return the boot line ONCE per session
    (subsequent calls return None so we don't repeat).
    """
    if reach == "reachable":
        answer = _nestor_ask(prompt)
        if not answer:
            return None
        state = answer.get("state", "unknown")
        age = answer.get("age")
        age_str = f" (age {age}s)" if isinstance(age, (int, float)) else ""
        return f"Nestor: {state}{age_str}"
    return _emit_boot_line_once(reach)


def _count_unsealed_drafts() -> int:
    """Count draft pairs across willows-grove/nestor/*.json bundles. These are
    the pairs a session has proposed but the operator has not yet sealed —
    the input to the Jarvis close-out's first table row."""
    nestor_dir = Path(__file__).resolve().parent.parent / "nestor"
    if not nestor_dir.is_dir():
        return 0
    total = 0
    for bundle_path in nestor_dir.glob("*.json"):
        try:
            bundle = json.loads(bundle_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        for pair in bundle.get("pairs", []) or []:
            if isinstance(pair, dict) and pair.get("status") == "draft":
                total += 1
    return total


def _launch_nestor_ui() -> None:
    """Fire-and-forget: start `nestor ui` on the loopback keep store. No wait,
    no stdio hookup — if it succeeds, the next probe sees 8765 answering; if
    it fails, the next Jarvis line still reads correctly (unsealed drafts
    remain unsealed). Never raises."""
    try:
        subprocess.Popen(
            ["nestor", "ui", "--loopback"],
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
        )
    except OSError:
        pass


def _jarvis_close_out() -> str | None:
    """Compose the deposit's close-out line per proposal §3.

    Reads: number of unsealed drafts across this repo's nestor/ bundles, and
    whether Nestor UI is answering on 8765.

    - unsealed > 0, UI not serving → launch it fire-and-forget; return the line.
    - unsealed > 0, UI already serving → return the same line, no launch.
    - unsealed == 0 → None (voice says nothing).
    """
    unsealed = _count_unsealed_drafts()
    if unsealed == 0:
        return None
    if _nestor_reach() != "reachable":
        _launch_nestor_ui()
    return "The store is open if you'd like to sign them."


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

    # Jarvis close-out: one sentence, no checklist (proposal §3). Only prints
    # a line when there are unsealed drafts on disk; on the "unsealed + UI
    # not serving" state, also launches nestor ui fire-and-forget.
    jarvis = _jarvis_close_out()
    if jarvis:
        print(jarvis, file=sys.stderr)
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
