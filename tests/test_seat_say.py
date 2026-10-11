# b17: GRSYT ΔΣ=42
"""Tests for the seat's reply-model selection and the qwen3 ``/no_think``."""

from __future__ import annotations

import importlib
import io
import json

from grove import seat_say


class _Opener:
    """Captures the one request the default say makes."""

    def __init__(self):
        self.body: dict = {}

    def open(self, req, timeout=None):
        self.body = json.loads(req.data.decode("utf-8"))
        return io.BytesIO(json.dumps({"response": "ok"}).encode("utf-8"))


def _prompt_sent(model: str) -> dict:
    op = _Opener()
    assert seat_say.ollama_say(model=model, opener=op)("hello") == "ok"
    return op.body


def _reload_model(monkeypatch, value):
    if value is None:
        monkeypatch.delenv("GROVE_SAY_MODEL", raising=False)
    else:
        monkeypatch.setenv("GROVE_SAY_MODEL", value)
    try:
        return importlib.reload(seat_say).MODEL
    finally:
        monkeypatch.delenv("GROVE_SAY_MODEL", raising=False)
        importlib.reload(seat_say)


def test_model_env_override(monkeypatch):
    assert _reload_model(monkeypatch, "llama3.2:3b") == "llama3.2:3b"


def test_model_default_when_unset_or_empty(monkeypatch):
    assert _reload_model(monkeypatch, None) == "qwen3:4b"
    assert _reload_model(monkeypatch, "") == "qwen3:4b"


def test_qwen3_prompt_gets_no_think():
    body = _prompt_sent("qwen3:4b")
    assert body["prompt"] == "hello /no_think"
    assert body["think"] is False


def test_non_qwen3_prompt_has_no_no_think():
    body = _prompt_sent("llama3.2:3b")
    assert body["prompt"] == "hello"
    assert body["think"] is False
