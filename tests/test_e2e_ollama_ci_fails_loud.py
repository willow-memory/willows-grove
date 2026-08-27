# b17: WGRV1 ΔΣ=42
"""Pin INVARIANTS.md §10 — CI witnesses fail loudly, not silently skip.

Grove v0.9 PR 12 — Loki finding #17 (M14-e2e_ollama-fail-not-skip).

The ``tests/e2e_ollama/`` fixtures (``ollama_ollama_ready``, ``pulled_model``,
``grove_pg_schema``) used to ``pytest.skip`` unconditionally when Ollama,
a candidate model, ``psycopg2``, or Postgres was missing. On a CI runner
that is a lie: the CI sidecars MUST be there — their absence is a broken
environment, not an operator-side excuse to green the build. Every §10
assertion downstream is gated on all three fixtures succeeding, so a
missing sidecar makes CI green with no §10 witness actually run.

Discipline:

* On CI (``$GITHUB_ACTIONS=true``) any missing prerequisite is a hard
  failure — the runner MUST provide the service.
* Off CI (developer machines) a skip stays — the suite is expensive and
  operators shouldn't need Ollama running to green unrelated work.

The fix routes every ``pytest.skip`` call in ``tests/e2e_ollama/conftest.py``
through a ``_missing_witness(reason)`` helper that reads
``$GITHUB_ACTIONS`` and calls ``pytest.fail`` on CI or ``pytest.skip``
locally. This test pins that helper by name and drives the
``ollama_ready`` fixture body through both env modes with an unreachable
Ollama host and the poll deadline collapsed to zero (no sleeps, no real
network waits).

Must fail on the unfixed tree — the helper is absent and the fixture
raises ``Skipped`` even on CI.
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))


def _load_e2e_ollama_conftest():
    """Import ``tests/e2e_ollama/conftest.py`` by path.

    The e2e_ollama directory is a pytest sub-package, not something
    pytest auto-imports from the tests/ root, so ``importlib.util`` is
    the honest way to get at its module object.
    """
    path = _REPO_ROOT / "tests" / "e2e_ollama" / "conftest.py"
    spec = importlib.util.spec_from_file_location(
        "tests.e2e_ollama._conftest_probe", path
    )
    assert spec is not None and spec.loader is not None, path
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _fixture_body(fixture_obj):
    """Return the raw callable beneath a ``@pytest.fixture`` decorator.

    Pytest 8 wraps fixtures in a ``FixtureFunctionDefinition`` whose
    original function lives on ``_fixture_function``; older pytest
    returns the function directly with a marker attribute. Handle both.
    """
    for attr in ("_fixture_function", "__wrapped__"):
        candidate = getattr(fixture_obj, attr, None)
        if callable(candidate):
            return candidate
    wrapped = getattr(fixture_obj, "__pytest_wrapped__", None)
    if wrapped is not None and hasattr(wrapped, "obj") and callable(wrapped.obj):
        return wrapped.obj
    return fixture_obj


def test_missing_witness_helper_is_defined():
    """The fix adds a ``_missing_witness`` helper — pin its presence.

    A regression that removes the helper (or renames it silently) trips
    this before any of the fixtures are exercised.
    """
    conftest = _load_e2e_ollama_conftest()
    assert hasattr(conftest, "_missing_witness"), (
        "tests/e2e_ollama/conftest.py must expose a _missing_witness "
        "helper that dispatches on $GITHUB_ACTIONS (INVARIANTS.md §10)."
    )
    assert callable(conftest._missing_witness), (
        "_missing_witness must be callable."
    )


def test_missing_witness_fails_on_ci(monkeypatch):
    """``$GITHUB_ACTIONS=true`` → the helper raises ``pytest.fail``."""
    conftest = _load_e2e_ollama_conftest()
    monkeypatch.setenv("GITHUB_ACTIONS", "true")
    with pytest.raises(pytest.fail.Exception):
        conftest._missing_witness("simulated missing witness (CI branch)")


def test_missing_witness_skips_off_ci(monkeypatch):
    """No ``$GITHUB_ACTIONS`` → the helper raises ``pytest.skip``."""
    conftest = _load_e2e_ollama_conftest()
    monkeypatch.delenv("GITHUB_ACTIONS", raising=False)
    with pytest.raises(pytest.skip.Exception):
        conftest._missing_witness("simulated missing witness (local branch)")


def test_missing_witness_treats_false_as_off_ci(monkeypatch):
    """``$GITHUB_ACTIONS=false`` (or any non-true) must still be a skip.

    Guards against a naive ``os.environ.get("GITHUB_ACTIONS")`` truthiness
    check that would fail on the literal string 'false'.
    """
    conftest = _load_e2e_ollama_conftest()
    monkeypatch.setenv("GITHUB_ACTIONS", "false")
    with pytest.raises(pytest.skip.Exception):
        conftest._missing_witness("simulated missing witness (false branch)")


def test_ollama_ready_fails_loud_on_ci(monkeypatch):
    """``ollama_ready`` fixture body under CI + unreachable Ollama fails.

    Pointing ``$OLLAMA_HOST`` at ``127.0.0.1:1`` (nothing listens) and
    collapsing the poll deadline to ``0.0`` makes the fixture reach its
    terminal branch immediately — no sleeps, no real network waits.
    Under the fix that branch is ``_missing_witness``, which raises
    ``pytest.fail`` because ``$GITHUB_ACTIONS=true``. Under the unfixed
    code that branch is a raw ``pytest.skip`` — the CI witness silently
    goes green, which is exactly the §10 violation this test pins.
    """
    conftest = _load_e2e_ollama_conftest()
    monkeypatch.setenv("OLLAMA_HOST", "http://127.0.0.1:1")
    monkeypatch.setenv("GITHUB_ACTIONS", "true")
    monkeypatch.setattr(conftest, "_OLLAMA_READY_TIMEOUT_SECONDS", 0.0)
    raw = _fixture_body(conftest.ollama_ready)
    with pytest.raises(pytest.fail.Exception):
        raw()


def test_ollama_ready_skips_off_ci(monkeypatch):
    """Same unreachable-Ollama scenario off CI stays a skip.

    Preserves developer ergonomics: an operator running the full test
    tree on a laptop without Ollama shouldn't have to see red.
    """
    conftest = _load_e2e_ollama_conftest()
    monkeypatch.setenv("OLLAMA_HOST", "http://127.0.0.1:1")
    monkeypatch.delenv("GITHUB_ACTIONS", raising=False)
    monkeypatch.setattr(conftest, "_OLLAMA_READY_TIMEOUT_SECONDS", 0.0)
    raw = _fixture_body(conftest.ollama_ready)
    with pytest.raises(pytest.skip.Exception):
        raw()
