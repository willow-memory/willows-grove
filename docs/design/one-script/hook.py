"""hook — the model only reads, and writes only if the user allows.

Read is allowed. Write asks the user. Every other tool is denied, including
ones that don't exist yet. Anything the hook can't read is denied, and a crash
exits 2, which blocks: it never fails open.

The model's job is to read what the last script produced; the scripts do the
rest. The vault is not checked here: its wall is that the agent's user can't
read it.

    python3 docs/design/one-script/hook.py    # Claude Code PreToolUse, matcher "*"
"""

import json
import sys

POLICY = {"Read": "allow", "Write": "ask"}

if __name__ == "__main__":
    try:
        event = json.load(sys.stdin)
        tool = event.get("tool_name") if isinstance(event, dict) else None
        decision = POLICY.get(tool, "deny")
        out = {"hookEventName": "PreToolUse", "permissionDecision": decision}
        print(json.dumps({"hookSpecificOutput": out}))
    except Exception:
        sys.exit(2)  # exit 2 blocks the tool in Claude Code
