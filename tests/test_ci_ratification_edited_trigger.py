# b17: WGRV1 ΔΣ=42
"""Pin INVARIANTS.md §12 — the workflow must fire on ``edited`` PR events.

§12 makes a `Ratified-by:` line the gate on opening a PR, and
``scripts/check_ratification.py`` reads that line out of the
``pull_request`` event payload at ``$GITHUB_EVENT_PATH``.

That creates a trap the gate cannot escape on its own. GitHub's default
``pull_request`` types are ``opened``/``synchronize``/``reopened``, so a
body edit fires ``edited`` and triggers nothing. Re-running the failed
run does not help either: a re-run replays the ORIGINAL event payload,
carrying the original body. Measured on Grove PR 3 — the body was
corrected to carry a well-formed `Ratified-by:` line, the checker
passed against that body locally, and the re-run still failed quoting
the pre-edit body.

So a PR whose ratification arrives by body edit could only reach green
through an empty commit or a close-and-reopen — forging a code event to
satisfy a governance gate. §12 exists to make authorization legible;
routing it around a fake push is the opposite. ``edited`` closes it.

Must fail on the unfixed workflow — ``pull_request`` carries no
``types:`` key at all, so the default set applies.

Line-level parse, no PyYAML dependency, matching the house style of the
other ``tests/test_ci_*`` workflow pins.
"""
from __future__ import annotations

import re
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]
_WORKFLOW_PATH = _REPO_ROOT / ".github" / "workflows" / "tests.yml"

# The `types:` entry nested under the `pull_request:` trigger. Anchored to
# four-space indentation so a `types:` under some other key cannot satisfy it.
_PR_TYPES_RE = re.compile(
    r"^  pull_request:\s*$(?P<body>(?:\n(?:    .*)?$)*)", re.MULTILINE
)
_TYPES_LINE_RE = re.compile(r"^    types:\s*\[(?P<types>[^\]]*)\]\s*$", re.MULTILINE)


def _pull_request_trigger_types() -> list[str] | None:
    """The declared types under ``on.pull_request``, or None if unset."""
    text = _WORKFLOW_PATH.read_text(encoding="utf-8")
    block = _PR_TYPES_RE.search(text)
    if block is None:
        return None
    m = _TYPES_LINE_RE.search(block.group("body"))
    if m is None:
        return None
    return [t.strip().strip("\"'") for t in m.group("types").split(",") if t.strip()]


def test_workflow_declares_pull_request_types() -> None:
    """`on.pull_request` must name its types rather than take the default."""
    assert _WORKFLOW_PATH.exists(), f"missing workflow: {_WORKFLOW_PATH}"
    types = _pull_request_trigger_types()
    assert types is not None, (
        "on.pull_request declares no `types:` — the default "
        "opened/synchronize/reopened set does not include `edited`, so a "
        "§12 ratification line added by body edit can never re-run the check"
    )


def test_edited_is_among_the_pull_request_types() -> None:
    """`edited` is the one that lets a corrected body re-fire the §12 gate."""
    types = _pull_request_trigger_types() or []
    assert "edited" in types, (
        "`edited` missing from on.pull_request.types — a PR whose "
        "`Ratified-by:` line arrives by body edit would be stuck red, with an "
        f"empty commit or a close/reopen as the only way out; got: {types}"
    )


def test_the_default_triggers_are_not_dropped() -> None:
    """Naming `types:` replaces the default set — it does not extend it.

    Declaring only `edited` would silently stop running CI on new PRs and on
    every push to an open one, which is a far worse regression than the bug
    this pin fixes.
    """
    types = _pull_request_trigger_types() or []
    for required in ("opened", "synchronize", "reopened"):
        assert required in types, (
            f"`{required}` dropped from on.pull_request.types — declaring "
            "`types:` overrides the default set rather than adding to it, so "
            f"every default trigger must be listed explicitly; got: {types}"
        )
