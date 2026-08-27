# b17: MKGRV  ΔΣ=42
"""Pins the Makefile against phantom targets (Grove v0.9 PR 12, Loki #33).

INVARIANTS.md §6 (manifests describe code, not aspirations) extends to the
Makefile: a target that shells out to a script which does not exist is a
manifest claiming a capability the tree doesn't have. The origin case was
``make grove-docs``, which chmod'd and then invoked
``scripts/grove_docs_refresh.sh`` — a script that was never delivered. Any
caller running the advertised command gets ``No such file or directory``.

This test reads the Makefile, extracts every target's recipe, and for each
shell-script invocation in that recipe asserts the referenced script exists
on disk — unless the invocation is itself guarded (``|| true`` / ``|| :``)
so it cannot fail the build. A ``chmod +x ... || true`` guard tolerates a
missing file for the chmod step, but does not excuse an *unguarded*
invocation of that same missing script two lines later; those still fail
this test.
"""

from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
MAKEFILE_PATH = REPO_ROOT / "Makefile"

# A target header: starts at column 0, name is a bare word (no leading
# whitespace, no leading tab -- that's a recipe line), followed by a colon
# that is not part of `:=` / `::=` assignment syntax.
_TARGET_RE = re.compile(r"^([A-Za-z0-9_.\-]+)\s*:(?!=)")

# A reference to a script under scripts/, with a file extension, appearing
# as a whitespace-delimited token (optionally prefixed by ./ or an
# interpreter like bash/sh/python3 immediately before it -- that prefix is
# not part of the captured group, we just need the path).
_SCRIPT_TOKEN_RE = re.compile(r"(?<![\w./-])(\.{0,2}/?scripts/[\w./-]+\.\w+)")

# A trailing guard that makes a shell command line unconditionally succeed
# regardless of what the guarded command did (exit code swallowed).
_GUARD_RE = re.compile(r"\|\|\s*(true|:)\s*$")


def _iter_targets(makefile_text: str) -> dict[str, list[str]]:
    """Return {target_name: [recipe_line, ...]} for every target block.

    Recipe lines are the raw (unstripped) lines that begin with a tab and
    immediately follow a target header, up to the next target header or
    EOF. Pattern/special targets (leading '.', e.g. .PHONY) are captured
    like any other -- they simply tend to have no recipe lines.
    """
    lines = makefile_text.splitlines()
    targets: dict[str, list[str]] = {}
    current: str | None = None
    for line in lines:
        header = _TARGET_RE.match(line) if not line.startswith("\t") else None
        if header:
            current = header.group(1)
            targets.setdefault(current, [])
            continue
        if line.startswith("\t") and current is not None:
            targets[current].append(line)
        elif line.strip() == "":
            # blank line does not end a recipe block by itself in real make,
            # but for this Makefile's shape it's never load-bearing; leave
            # `current` as-is so a stray blank line inside a recipe (none
            # exist today) wouldn't misattribute a later block.
            continue
        else:
            current = None
    return targets


def _would_fail_on_missing_script(recipe_line: str) -> str | None:
    """Return the referenced script path if this line invokes a script
    under scripts/ in a way that is NOT guarded against failure, else None.
    """
    body = recipe_line.strip()
    if not body:
        return None
    body = body.lstrip("@")  # '@' only silences echo, not failure semantics
    if _GUARD_RE.search(body):
        return None  # `... || true` / `... || :` swallows any failure
    match = _SCRIPT_TOKEN_RE.search(body)
    if not match:
        return None
    return match.group(1)


def test_makefile_exists():
    assert MAKEFILE_PATH.is_file(), f"expected a Makefile at {MAKEFILE_PATH}"


def test_every_target_script_invocation_resolves():
    """Every non-guarded script invocation in every target must point at a
    script that actually exists in the tree.

    This is the manifest-honesty invariant (INVARIANTS.md §6) applied to
    the Makefile: `make <target>` is a promise to the operator. A target
    whose recipe unconditionally runs a nonexistent script breaks that
    promise with `No such file or directory` the moment it's invoked.
    """
    text = MAKEFILE_PATH.read_text(encoding="utf-8")
    targets = _iter_targets(text)

    broken: list[tuple[str, str]] = []
    for name, recipe_lines in targets.items():
        for line in recipe_lines:
            script_ref = _would_fail_on_missing_script(line)
            if script_ref is None:
                continue
            script_path = (REPO_ROOT / script_ref.lstrip("./")).resolve()
            if not script_path.is_file():
                broken.append((name, script_ref))

    assert not broken, (
        "Makefile target(s) unconditionally invoke a script that does not "
        f"exist (would fail with 'No such file or directory'): {broken}. "
        "Either deliver the script or remove the target (INVARIANTS.md §6)."
    )
