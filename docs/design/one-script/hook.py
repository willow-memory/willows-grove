"""hook — the one hook: read what the last script run produced.

The hook decides nothing. The scripts write their answers into the record
ahead of time; the hook looks the current action up by its hash and returns
what it finds (next-pile.md, "a hook may read the record, never the voice"):

  a pass row for this action     -> allow
  a refused row for this action  -> deny
  nothing on it                  -> ask: ESCALATE to the human
  anything touching the vault    -> deny, whatever the record says

A record row it reads: {"kind": "decision", "action": <sha256>, "verdict":
"pass" | "refused"}. The latest row for an action wins. A line it can't parse
means the record can't be trusted, so every action escalates until it's fixed.

Read only. Stdlib only. Wired as a Claude Code PreToolUse command hook:

    ONESCRIPT_BOX=… python3 docs/design/one-script/hook.py

Env: ONESCRIPT_BOX, the folder holding record.jsonl (unset: every action
escalates, never guessed). ONESCRIPT_VAULT, the vault's folder name
(default sean-data-vault).
"""

from __future__ import annotations

import hashlib
import json
import os
import sys
from pathlib import Path

VAULT = os.environ.get("ONESCRIPT_VAULT", "sean-data-vault")


def action_hash(tool: str, tool_input: dict) -> str:
    """One full-length hash per action: the tool and exactly what it was given."""
    body = json.dumps(
        {"tool": tool, "input": tool_input},
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )
    return hashlib.sha256(body.encode()).hexdigest()


def lookup(record: Path | None, action: str) -> tuple[str, str]:
    """The record's last word on this action, as (verdict, why)."""
    if record is None or not record.is_file():
        return "escalate", "no record to read"
    verdict = ""
    for n, line in enumerate(record.read_text(encoding="utf-8").splitlines()):
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except ValueError:
            return "escalate", f"record line {n} is garbled; nothing is trusted"
        if row.get("kind") == "decision" and row.get("action") == action:
            verdict = row.get("verdict", "")
    if verdict in ("pass", "refused"):
        return verdict, f"the record says {verdict}"
    return "escalate", "not in the record"


def decide(event: dict, box: Path | None) -> tuple[str, str]:
    tool = event.get("tool_name", "")
    tool_input = event.get("tool_input") or {}
    action = action_hash(tool, tool_input)
    if VAULT in json.dumps(tool_input, ensure_ascii=False):
        return "deny", f"the vault is Sean's key ({action})"
    verdict, why = lookup(box / "record.jsonl" if box else None, action)
    answer = {"pass": "allow", "refused": "deny"}.get(verdict, "ask")
    tag = "ESCALATE: " if answer == "ask" else ""
    return answer, f"{tag}{why} ({action})"


def main() -> int:
    try:
        event = json.load(sys.stdin)
    except ValueError:
        event = {}
    _box = os.environ.get("ONESCRIPT_BOX", "").strip()
    answer, why = decide(event, Path(_box).expanduser() if _box else None)
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
    sys.exit(main())
