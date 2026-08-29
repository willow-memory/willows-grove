#!/usr/bin/env python3
# b17: GRRAT · ΔΣ=42
"""scripts/check_ratification.py — ratification CI check (§12).

Enforces INVARIANTS.md §12: PR-open and merge require a recorded
human authorization. The mechanism is a `Ratified-by:` line as the
LAST non-blank line of the PR body (open case) or the merge commit
message (merge case).

Last, not first, and deliberately so: the authorizing quote is the
human's, and it signs off beneath the work and beneath the marks the
agents left on it (`Persona:` trailers, attribution footers) — the
same place a signature goes on anything else. A body that opens with
the authorization buries the description under its own paperwork.

Line format:
    Ratified-by: <identifier> — "<verbatim quote>"

- The em dash may also be the ASCII sequence " - " (space-hyphen-space)
  for tools that mangle Unicode.
- <identifier> is a short human-legible key (name, email local-part,
  fleet key). It is not validated against any list — the check only
  proves an identifier is present and a quote follows.
- <verbatim quote> is the human message that authorized the action,
  quoted with " or curly quotes.

Runtime:
- CI: reads `$GITHUB_EVENT_PATH` (set by GitHub Actions) and pulls
  `pull_request.body` on `pull_request` events, or the merge commit
  message on merge events.
- Local: pass a body via `--body-file <path>` or stdin.

Exits 0 when the ratification line is present and well-formed;
non-zero otherwise.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path

# The em dash (U+2014), an en dash (U+2013), or a spaced hyphen are all accepted.
RATIFICATION_RE = re.compile(
    r'^\s*Ratified-by:\s*'
    r'([A-Za-z0-9_.\-@]+)'
    r'\s*(?:—|–|-)\s*'
    r'["“](.+?)["”]\s*$'
)


def _last_nonblank_line(text: str) -> str:
    for raw in reversed(text.splitlines()):
        s = raw.strip()
        if s:
            return s
    return ""


def check_body(body: str) -> tuple[bool, str]:
    """Return (ok, message)."""
    if not body or not body.strip():
        return False, "body is empty — no Ratified-by line possible"
    last = _last_nonblank_line(body)
    m = RATIFICATION_RE.match(last)
    if not m:
        return False, (
            "last non-blank line does not match "
            "'Ratified-by: <identifier> — \"<verbatim quote>\"' — got:\n  "
            + last
        )
    identifier, quote = m.group(1), m.group(2).strip()
    if not identifier:
        return False, "Ratified-by identifier is empty"
    if not quote:
        return False, "Ratified-by quote is empty"
    return True, f"ratified by {identifier}: \"{quote}\""


def _load_github_event() -> tuple[str, str]:
    """Return (kind, body) from GITHUB_EVENT_PATH; ('', '') on absence."""
    path = os.environ.get("GITHUB_EVENT_PATH")
    if not path or not Path(path).exists():
        return "", ""
    try:
        event = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return "", ""
    if event.get("pull_request"):
        return "pull_request", event["pull_request"].get("body") or ""
    if event.get("head_commit"):
        return "push", event["head_commit"].get("message") or ""
    return "", ""


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="§12 ratification check")
    parser.add_argument("--body-file", type=Path, default=None)
    parser.add_argument("--body", type=str, default=None)
    args = parser.parse_args(argv)

    if args.body is not None:
        body = args.body
        source = "argv"
    elif args.body_file is not None:
        body = args.body_file.read_text(encoding="utf-8")
        source = str(args.body_file)
    else:
        kind, body = _load_github_event()
        if not kind:
            if not sys.stdin.isatty():
                body = sys.stdin.read()
                source = "stdin"
            else:
                print(
                    "ratification: no body source found "
                    "(pass --body / --body-file or set GITHUB_EVENT_PATH)",
                    file=sys.stderr,
                )
                return 2
        else:
            source = f"github-event({kind})"

    ok, msg = check_body(body)
    if ok:
        print(f"ratification: clean — {msg} (source: {source})")
        return 0
    print(f"ratification: FAIL ({source}): {msg}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
