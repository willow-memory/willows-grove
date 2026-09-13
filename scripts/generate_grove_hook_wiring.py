#!/usr/bin/env python3
"""Generate hooks/wiring.json from hooks/wiring.source.json.

KB 20BACCD0 / proposal 2026-09-02-grove-hooks-and-skills.md §6: the hook table
is derived, never hand-kept. The source file is the editable/sealed input;
wiring.json is the compiled output. A hand edit to wiring.json fails the
companion test.

When Nestor sealed rows exist for Grove hook events, replace wiring.source.json
from those rows in the same PR that seals them — this script stays the only
writer of wiring.json.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "hooks" / "wiring.source.json"
OUTPUT = ROOT / "hooks" / "wiring.json"

_DROP_KEYS = {"_source", "_provisional"}


def render(source: dict) -> dict:
    out = {k: v for k, v in source.items() if k not in _DROP_KEYS}
    out["_generated_by"] = "scripts/generate_grove_hook_wiring.py"
    out["_generated_from"] = "hooks/wiring.source.json"
    return out


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="exit 1 if wiring.json does not match a fresh render (CI)",
    )
    args = parser.parse_args(argv)
    source = json.loads(SOURCE.read_text(encoding="utf-8"))
    if not isinstance(source, dict):
        print("wiring.source.json must be an object", file=sys.stderr)
        return 2
    rendered = render(source)
    text = json.dumps(rendered, indent=2) + "\n"
    if args.check:
        if not OUTPUT.is_file():
            print(f"missing {OUTPUT}", file=sys.stderr)
            return 1
        on_disk = OUTPUT.read_text(encoding="utf-8")
        if on_disk != text:
            print(
                f"{OUTPUT} drifts from {SOURCE} — run "
                "scripts/generate_grove_hook_wiring.py",
                file=sys.stderr,
            )
            return 1
        print(f"ok: {OUTPUT} matches {SOURCE}")
        return 0
    OUTPUT.write_text(text, encoding="utf-8")
    print(f"wrote {OUTPUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
