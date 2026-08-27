# b17: WGRV1 ΔΣ=42
"""Pin INVARIANTS.md §10 — the Playwright browser install step.

Grove v0.9 PR 12 — Loki finding #35 (m35-playwright-install-yes).

INVARIANTS.md §10 pins the install step as
``npx --yes playwright install --with-deps chromium`` — the ``--yes``
token opts ``npx`` out of its interactive "ok to download this
package?" prompt. Without it, a runner whose npx build is not already
primed with the ``playwright`` package can hang the job waiting on
stdin instead of installing browsers non-interactively.

Delivered had ``npx playwright install --with-deps chromium`` (no
``--yes``) at .github/workflows/tests.yml:103ish.

Must fail on the unfixed workflow — the run: command for the
"Install Playwright browsers (chromium)" step does not contain
``--yes``.

Line-level regex grep, no PyYAML dependency — the workflow yml is
tracked-code and this pin is about a substring, not the structural
shape of the file.
"""
from __future__ import annotations

import re
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]
_WORKFLOW_PATH = _REPO_ROOT / ".github" / "workflows" / "tests.yml"

# The step's `run:` line invokes `playwright install …`. Match the value.
_PLAYWRIGHT_INSTALL_RE = re.compile(
    r"^\s*run:\s*(.*playwright\s+install.*)$", re.MULTILINE
)


def _find_playwright_install_run_command() -> str | None:
    text = _WORKFLOW_PATH.read_text(encoding="utf-8")
    m = _PLAYWRIGHT_INSTALL_RE.search(text)
    return m.group(1).strip() if m else None


def test_playwright_install_step_exists():
    """Sanity: the workflow must actually have a playwright install step."""
    cmd = _find_playwright_install_run_command()
    assert cmd is not None, (
        "No step running 'playwright install' found in "
        f"{_WORKFLOW_PATH} — INVARIANTS.md §10 requires one."
    )


def test_playwright_install_step_uses_yes_flag():
    """INVARIANTS.md §10 pins '--yes' on the playwright install command.

    Fails on the unfixed workflow, whose run: command is
    'npx playwright install --with-deps chromium' — no '--yes'.
    """
    cmd = _find_playwright_install_run_command()
    assert cmd is not None, "playwright install step not found"
    assert "--yes" in cmd, (
        "Playwright browser install step must pass '--yes' to npx "
        f"(INVARIANTS.md §10). Got run: {cmd!r}"
    )
