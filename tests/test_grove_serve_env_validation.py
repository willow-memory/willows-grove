# b17: WGRV1 · ΔΣ=42
"""tests/test_grove_serve_env_validation.py — pins Loki finding #37.

`grove_serve.main()` used to build `port` with a bare
`int(os.environ.get("GROVE_SERVE_PORT", ...))`. A set-but-non-numeric
value (a typo, a stray shell-quoting mistake) raised an undecorated
`ValueError` — a Python traceback on the operator's terminal instead of
an operator-legible refusal, and no defined exit code to script against.

This test runs `grove_serve.py` as a real subprocess (so the crash path
is exercised exactly as an operator would hit it — CPython's own
top-level exception handler and exit code, not something a mock could
approximate) with `GROVE_SERVE_PORT=nope` and asserts:

* the process exits non-zero, and
* stderr names the problem in the language an operator can act on
  ("not a valid port"), not a Python traceback.

It cannot pass against the unfixed code: `int("nope")` raises
`ValueError`, which is an *uncaught* exception there — Python's default
handler prints a traceback (not the words "not a valid port") and exits
with status 1, so the message assertion below fails until the fix wraps
the parse and prints the operator-legible refusal itself.
"""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPT = REPO_ROOT / "grove_serve.py"


def _run_with_env(**env_overrides: str) -> subprocess.CompletedProcess:
    env = dict(os.environ)
    env.update(env_overrides)
    return subprocess.run(
        [sys.executable, str(SCRIPT)],
        cwd=str(REPO_ROOT),
        env=env,
        capture_output=True,
        text=True,
        timeout=15,
        check=False,
    )


def test_non_numeric_port_refuses_with_legible_message_and_nonzero_exit():
    result = _run_with_env(GROVE_SERVE_PORT="nope")
    assert result.returncode != 0, (
        f"expected a non-zero exit for GROVE_SERVE_PORT=nope, got 0 "
        f"(stdout={result.stdout!r} stderr={result.stderr!r})"
    )
    assert "not a valid port" in result.stderr, (
        f"expected an operator-legible refusal naming the port in stderr, "
        f"got stderr={result.stderr!r}"
    )
    # The old failure mode was an uncaught ValueError traceback — assert
    # this isn't that.
    assert "Traceback" not in result.stderr


def test_non_numeric_port_exits_with_documented_code():
    result = _run_with_env(GROVE_SERVE_PORT="nope")
    assert result.returncode == 2


def test_obviously_bad_host_also_refuses():
    result = _run_with_env(GROVE_SERVE_HOST="127.0.0.1:8766")
    assert result.returncode != 0
    assert "not a valid host" in result.stderr
