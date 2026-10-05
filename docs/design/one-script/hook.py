"""hook — the one hook: read what the last script run produced.

The hook decides nothing. The scripts write their answers into the record
ahead of time; the hook looks the current action up by its hash and returns
what it finds (next-pile.md, "a hook may read the record, never the voice"):

  a pass row for this action     -> allow
  a refused row for this action  -> deny
  nothing on it                  -> ask: ESCALATE to the human
  anything touching the vault    -> deny, whatever the record says
  anything the hook can't read   -> ask: it never fails open

An action is the tool, the working directory, and the tool's input without
its wording (`description`, `timeout`). A record row it reads:
{"kind": "decision", "action": <sha256>, "verdict": "pass" | "refused"}.
The latest row for an action wins. A line that isn't a JSON object means the
record can't be trusted, so every action escalates until it's fixed.

The vault check catches the name anywhere in the input, any path field that
resolves into it (symlinks included), and a working directory inside it.
It can't catch a shell command that reaches the vault indirectly (a variable,
an encoded path): the wall for that is the vault being unreadable by the
agent's user, not this hook.

Read only. Stdlib only. Wired as a Claude Code PreToolUse command hook:

    ONESCRIPT_BOX=… python3 docs/design/one-script/hook.py

Env: ONESCRIPT_BOX, the folder holding record.jsonl (unset: every action
escalates, never guessed).
"""

from __future__ import annotations

import hashlib
import json
import os
import sys
from pathlib import Path

VAULT = "sean-data-vault"
NOISE = frozenset({"description", "timeout"})
PATH_FIELDS = ("file_path", "path", "notebook_path")


def action_hash(tool: str, cwd: str, tool_input) -> str:
    """One full-length hash per action: the tool, where, and what it was given."""
    if isinstance(tool_input, dict):
        tool_input = {k: v for k, v in tool_input.items() if k not in NOISE}
    body = json.dumps(
        {"tool": tool, "cwd": cwd, "input": tool_input},
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )
    return hashlib.sha256(body.encode()).hexdigest()


def in_vault(cwd: str, tool_input) -> bool:
    if VAULT in json.dumps(tool_input, ensure_ascii=False):
        return True
    paths = [cwd] if cwd else []
    if isinstance(tool_input, dict):
        paths += [
            os.path.join(cwd, p)
            for k in PATH_FIELDS
            if isinstance(p := tool_input.get(k), str) and p
        ]
    return any(VAULT in Path(os.path.realpath(p)).parts for p in paths)


def lookup(record: Path | None, action: str) -> tuple[str, str]:
    """The record's last word on this action, as (verdict, why)."""
    if record is None or not record.is_file():
        return "escalate", "no record to read"
    verdict = ""
    try:
        lines = record.read_bytes().decode("utf-8").splitlines()
    except (OSError, UnicodeDecodeError) as e:
        return "escalate", f"record unreadable ({type(e).__name__}); nothing is trusted"
    for n, line in enumerate(lines):
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except ValueError:
            row = None
        if not isinstance(row, dict):
            return "escalate", f"record line {n} is garbled; nothing is trusted"
        if row.get("kind") == "decision" and row.get("action") == action:
            verdict = row.get("verdict", "")
    if verdict in ("pass", "refused"):
        return verdict, f"the record says {verdict}"
    return "escalate", "not in the record"


def decide(event, box: Path | None) -> tuple[str, str]:
    if not isinstance(event, dict):
        return "ask", "ESCALATE: the event is not an object"
    tool = str(event.get("tool_name", ""))
    cwd = str(event.get("cwd", ""))
    tool_input = event.get("tool_input") or {}
    action = action_hash(tool, cwd, tool_input)
    if in_vault(cwd, tool_input):
        return "deny", f"the vault is Sean's key ({action})"
    verdict, why = lookup(box / "record.jsonl" if box else None, action)
    answer = {"pass": "allow", "refused": "deny"}.get(verdict, "ask")
    tag = "ESCALATE: " if answer == "ask" else ""
    return answer, f"{tag}{why} ({action})"


def main() -> int:
    try:
        _box = os.environ.get("ONESCRIPT_BOX", "").strip()
        answer, why = decide(
            json.loads(sys.stdin.read()), Path(_box).expanduser() if _box else None
        )
    except Exception as e:  # any failure escalates; a crash would let the tool run
        answer, why = "ask", f"ESCALATE: hook error ({type(e).__name__})"
    print(
        json.dumps(
            {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": answer,
                    "permissionDecisionReason": why,
                }
            }
        )
    )
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(2)  # exit 2 blocks the tool in Claude Code
