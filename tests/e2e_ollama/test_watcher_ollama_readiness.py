# b17: WGRV1 ΔΣ=42
"""Canary for the ``tests/e2e_ollama/`` suite (INVARIANTS.md §10).

Small test that just verifies:

1. Ollama is reachable at ``$OLLAMA_HOST`` (``/api/tags`` answers 200).
2. The suite can pull one of the tiny model candidates end-to-end.

If this test skips, the operator can read the reason directly instead of
sifting through the full watcher e2e's tracebacks; if it passes, the
watcher e2e's failure is a real failure, not an environment gap.

The canary uses the shared ``ollama_ready`` + ``pulled_model`` fixtures
from ``conftest.py`` — the model it pulls is cached for the sibling
watcher e2e in the same session, so no double-pay of the ~30-60s pull
cost.
"""
from __future__ import annotations

import json
import urllib.error
import urllib.request


def _post_json(url: str, payload: dict, timeout: float = 30.0) -> dict:
    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(  # noqa: S310 — loopback
        url,
        data=body,
        method="POST",
        headers={"content-type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:  # noqa: S310
        raw = resp.read().decode("utf-8", errors="replace")
    return json.loads(raw)


def test_ollama_service_reachable(ollama_ready):
    """The container answers 200 on ``/api/tags`` — the readiness invariant."""
    assert isinstance(ollama_ready, str) and ollama_ready.startswith("http")


def test_ollama_can_pull_and_generate(ollama_ready, pulled_model):
    """A pulled model can produce a short completion.

    ``/api/generate`` with ``stream=False`` returns the whole body in one
    JSON — the response's ``response`` field is a non-empty string. This
    is the exact shape ``ResidentWatcher._classify_message`` reads, so if
    this test passes the watcher can classify. A generous 60s timeout
    absorbs the first cold-load — Ollama warms the model into memory on
    the first generate call, which is slower than steady-state.
    """
    assert pulled_model, "pulled_model fixture returned an empty name"
    data = _post_json(
        ollama_ready + "/api/generate",
        {
            "model": pulled_model,
            "prompt": "Reply with the single word: ready",
            "stream": False,
        },
        timeout=60.0,
    )
    assert isinstance(data, dict), f"unexpected body: {data!r}"
    response = data.get("response")
    assert isinstance(response, str) and response.strip(), (
        f"model {pulled_model!r} returned no response: {data!r}"
    )
