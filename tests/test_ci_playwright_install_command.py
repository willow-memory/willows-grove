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
"""
from __future__ import annotations

from pathlib import Path

import yaml

_REPO_ROOT = Path(__file__).resolve().parents[1]
_WORKFLOW_PATH = _REPO_ROOT / ".github" / "workflows" / "tests.yml"


def _find_playwright_install_step():
    """Return the step dict for the Playwright browser install step.

    Walks every job's steps looking for the one whose ``run:`` command
    invokes ``playwright install`` (the browser-download step, not the
    ``npm install`` step or the ``npx playwright test`` run step).
    """
    workflow = yaml.safe_load(_WORKFLOW_PATH.read_text(encoding="utf-8"))
    jobs = workflow.get("jobs", {})
    for job in jobs.values():
        for step in job.get("steps", []):
            run_cmd = step.get("run")
            if not run_cmd:
                continue
            if "playwright install" in run_cmd:
                return step
    return None


def test_playwright_install_step_exists():
    """Sanity: the workflow must actually have a playwright install step."""
    step = _find_playwright_install_step()
    assert step is not None, (
        "No step running 'playwright install' found in "
        f"{_WORKFLOW_PATH} — INVARIANTS.md §10 requires one."
    )


def test_playwright_install_step_uses_yes_flag():
    """INVARIANTS.md §10 pins '--yes' on the playwright install command.

    Fails on the unfixed workflow, whose run: command is
    'npx playwright install --with-deps chromium' — no '--yes'.
    """
    step = _find_playwright_install_step()
    assert step is not None, "playwright install step not found"
    run_cmd = step["run"]
    assert "--yes" in run_cmd, (
        "Playwright browser install step must pass '--yes' to npx "
        f"(INVARIANTS.md §10). Got run: {run_cmd!r}"
    )
