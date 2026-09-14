#!/usr/bin/env python3
"""Generate hooks/wiring.json from sealed Nestor rows.

KB 20BACCD0 / proposal 2026-09-02-grove-hooks-and-skills.md §6: the hook table
is derived, never hand-kept. The rows live in the sealed record
`governance/decisions/grove-hook-rows-sealed.json` (an export of the
sealed pairs from PR 70). Ambient scaffolding (command, env, ide-stack
pointer) is invariant of Grove's hook setup and lives here as module
constants — changing them is a code change, reviewed.

The previous `hooks/wiring.source.json` file is retired: its row content
is now proposed → sealed in Nestor UI → exported to the sealed record.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SEALED = ROOT / "governance" / "decisions" / "grove-hook-rows-sealed.json"
OUTPUT = ROOT / "hooks" / "wiring.json"

# ── ambient scaffolding (invariant of Grove's hook setup) ─────────────────

_B17 = "GRVHK"
_COMMAND = "hooks/grove-hook"
_ENV = {"GROVE_SEAT_FILE": "{{PROJECT_ROOT}}/hooks/seat.md"}
_NO_PRE_TOOL_USE = (
    "This Grove flowchart table stays free of PreToolUse (§7). The IDE "
    "stack that Cursor and Claude actually run is hooks/client-hooks.json "
    "— same willow PreToolUse gate, invoked through hooks/grove-hook "
    "before_* actions. One guard per event; sync via scripts/sync_desk_client_hooks.py "
    "(gap 651b4a1ccfab)."
)
_IDE_STACK = "hooks/client-hooks.json"
_GENERATED_BY = "scripts/generate_grove_hook_wiring.py"
_GENERATED_FROM = "governance/decisions/grove-hook-rows-sealed.json"


def render(sealed: dict[str, Any]) -> dict[str, Any]:
    """Compose the wiring.json shape from a sealed record + module scaffolding.

    Each sealed row becomes one entry in the `hooks` list. Ambient
    scaffolding comes from module constants above so a scaffolding change
    is a code change (reviewed) rather than a data change.
    """
    rows = sealed.get("rows")
    if not isinstance(rows, list) or not rows:
        raise ValueError(
            f"generate_grove_hook_wiring: {SEALED.name} has no `rows` array "
            "or the array is empty — a sealed record must carry at least "
            "one row."
        )
    hooks: list[dict[str, Any]] = []
    for row in rows:
        if not isinstance(row, dict):
            raise ValueError(
                f"generate_grove_hook_wiring: non-object row in {SEALED.name}: {row!r}"
            )
        for key in ("event", "action"):
            if not isinstance(row.get(key), str) or not row[key]:
                raise ValueError(
                    f"generate_grove_hook_wiring: row missing string `{key}`: {row!r}"
                )
        hooks.append(
            {
                "event": row["event"],
                "action": row["action"],
                "_answers": row.get("answers", ""),
            }
        )
    return {
        "version": 1,
        "_b17": _B17,
        "command": _COMMAND,
        "env": _ENV,
        "hooks": hooks,
        "_no_pre_tool_use": _NO_PRE_TOOL_USE,
        "_ide_stack": _IDE_STACK,
        "_generated_by": _GENERATED_BY,
        "_generated_from": _GENERATED_FROM,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="exit 1 if wiring.json does not match a fresh render (CI)",
    )
    args = parser.parse_args(argv)

    if not SEALED.is_file():
        print(f"missing sealed record: {SEALED}", file=sys.stderr)
        return 2
    sealed = json.loads(SEALED.read_text(encoding="utf-8"))
    if not isinstance(sealed, dict):
        print(f"{SEALED.name} must be an object", file=sys.stderr)
        return 2
    rendered = render(sealed)
    text = json.dumps(rendered, indent=2) + "\n"
    if args.check:
        if not OUTPUT.is_file():
            print(f"missing {OUTPUT}", file=sys.stderr)
            return 1
        on_disk = OUTPUT.read_text(encoding="utf-8")
        if on_disk != text:
            print(
                f"{OUTPUT} drifts from {SEALED} — run "
                "scripts/generate_grove_hook_wiring.py",
                file=sys.stderr,
            )
            return 1
        print(f"ok: {OUTPUT} matches {SEALED}")
        return 0
    OUTPUT.write_text(text, encoding="utf-8")
    print(f"wrote {OUTPUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
