# b17: WGRV1 ΔΣ=42
"""Tests for grove.nestor_client — mocked stdio + real-binary probe."""
from __future__ import annotations

import io
import json
import shutil
from unittest.mock import patch

import pytest

from grove import nestor_client
from grove.errors import Unreachable
from grove.nestor_client import NestorClient


class _FakeProc:
    """Minimal Popen stand-in that echoes JSON-RPC over stdio."""

    def __init__(self, responses):
        self._responses = list(responses)
        self.stdin = io.StringIO()
        self.stdout = io.StringIO()
        self._alive = True

    def poll(self):
        return None if self._alive else 0

    # Grove writes; we pop one canned response into stdout each call.
    def _serve(self):
        if not self._responses:
            return ""
        resp = self._responses.pop(0)
        return json.dumps(resp) + "\n"

    def terminate(self):
        self._alive = False

    def wait(self, timeout=None):
        self._alive = False
        return 0

    def kill(self):
        self._alive = False


def _install_fake(monkeypatch, responses):
    # Force the availability probe true, and hand back a fake Popen.
    monkeypatch.setattr(nestor_client.shutil, "which", lambda _exe: "/usr/local/bin/nestor")

    fake = _FakeProc(responses)

    class _StubStdin:
        def __init__(self, parent): self.parent = parent; self.closed = False
        def write(self, s):
            # trigger next canned response
            self.parent._pending = self.parent._serve()
        def flush(self): pass
        def close(self): self.closed = True

    class _StubStdout:
        def __init__(self, parent): self.parent = parent
        def readline(self):
            pending = getattr(self.parent, "_pending", "")
            self.parent._pending = ""
            return pending

    fake.stdin = _StubStdin(fake)
    fake.stdout = _StubStdout(fake)

    def _fake_popen(*args, **kwargs):
        return fake

    monkeypatch.setattr(nestor_client.subprocess, "Popen", _fake_popen)
    return fake


def test_decision_check_returns_response(monkeypatch):
    sealed_payload = {
        "passage": {
            "source": "may we merge?",
            "target": "yes",
            "state": "sealed",
            "meta": {"pair_id": "p42", "verifier": "rita"},
        }
    }
    # Fake stdio child so __enter__/_ensure_session do not mark the client
    # unavailable when CI has no nestor binary (decision_check probes PATH first).
    _install_fake(monkeypatch, [
        {"jsonrpc": "2.0", "id": 1, "result": {"protocolVersion": "2025-06-18", "capabilities": {}}},
    ])
    monkeypatch.setattr(NestorClient, "_tool", lambda self, name, args: sealed_payload)
    with NestorClient() as nc:
        out = nc.decision_check("may we merge?")
    assert out == {
        "verdict": "sealed",
        "pair": {"pair_id": "p42", "source": "may we merge?", "target": "yes", "verifier": "rita"},
    }


def test_evidence_and_warrant(monkeypatch):
    _install_fake(monkeypatch, [
        {"jsonrpc": "2.0", "id": 1, "result": {"evidence": ["ev1"]}},
        {"jsonrpc": "2.0", "id": 2, "result": {"warrant": "citation"}},
    ])
    with NestorClient() as nc:
        e = nc.evidence_for("p42")
        w = nc.warrant_for("p42")
    assert e["result"] == {"evidence": ["ev1"]}
    assert w["result"] == {"warrant": "citation"}


def test_refusal_is_returned_verbatim(monkeypatch):
    verbatim = "I will not do that. There is no sealed pair for this act."
    _install_fake(monkeypatch, [{"jsonrpc": "2.0", "id": 1, "result": {"text": verbatim}}])
    with NestorClient() as nc:
        out = nc.refusal("merge", branch="main")
    assert out == verbatim, "V5: refusal must be VERBATIM, not paraphrased"


def test_missing_binary_decision_check_raises_unreachable(monkeypatch):
    """INVARIANTS.md §1: unreachable is a distinct sentinel, not None.
    decision_check() raises when the binary is not on PATH; the other
    evidence/warrant/refusal helpers keep returning None (they operate
    on already-resolved pair ids and callers already know available()
    is a probe)."""
    monkeypatch.setattr(nestor_client.shutil, "which", lambda _exe: None)
    nc = NestorClient()
    assert nc.available() is False
    with pytest.raises(Unreachable):
        nc.decision_check("anything")
    assert nc.evidence_for("x") is None
    assert nc.warrant_for("x") is None
    assert nc.refusal("x") is None
    nc.close()  # must not raise


def test_missing_binary_reachable_reached_no_match_still_returns_none(monkeypatch):
    """Available and reached, but the fake process sends nothing → None.

    This is the "reachable but no sealed pair" case (the 200 pending
    branch on the endpoint). It stays as ``None`` — Unreachable is
    reserved for the source-not-reached state."""
    _install_fake(monkeypatch, [])  # no canned responses → empty readline
    with NestorClient() as nc:
        assert nc.decision_check("q") is None


def test_transport_error_returns_none(monkeypatch):
    _install_fake(monkeypatch, [])
    with NestorClient() as nc:
        # override stdin to raise
        def _boom(_s):
            raise BrokenPipeError("closed")
        nc._proc.stdin.write = _boom
        assert nc.decision_check("q") is None


def _clear_store_env(monkeypatch):
    for env in nestor_client._DEFAULT_STORE_ENVS + ("WILLOW_HOME",):
        monkeypatch.delenv(env, raising=False)


def test_default_store_path_falls_back_cleanly(monkeypatch, tmp_path):
    _clear_store_env(monkeypatch)
    monkeypatch.setattr(nestor_client.Path, "home", classmethod(lambda cls: tmp_path))
    # no candidate dirs or household db file → returns None
    assert nestor_client._default_store_path() is None


def test_default_store_path_prefers_household_keep_db(monkeypatch, tmp_path):
    """~/.nestor/keep/nestor.db wins when present — the canonical household pin."""
    _clear_store_env(monkeypatch)
    monkeypatch.setattr(nestor_client.Path, "home", classmethod(lambda cls: tmp_path))
    household_db = tmp_path / ".nestor" / "keep" / "nestor.db"
    household_db.parent.mkdir(parents=True)
    household_db.touch()
    assert nestor_client._default_store_path() == household_db


def test_default_store_path_finds_household_dot_nestor(monkeypatch, tmp_path):
    """~/.nestor lands as the fallback when no Willow-scoped store exists.

    Bug 3 (standup finding): with store envs and ~/.willow/nestor all absent,
    the client used to return ``None`` and Grove fell through to Nestor's own
    CLI default of ``./data/nestor.db`` — which polluted the repo cwd on every
    grove_serve run. The operator's actual household store lives at ~/.nestor,
    so probing it here keeps Grove pointing at the real store instead of
    dropping a scratch DB.
    """
    _clear_store_env(monkeypatch)
    monkeypatch.setattr(nestor_client.Path, "home", classmethod(lambda cls: tmp_path))
    household = tmp_path / ".nestor"
    household.mkdir()
    resolved = nestor_client._default_store_path()
    assert resolved == household


def test_default_store_path_prefers_willow_over_household(monkeypatch, tmp_path):
    """When both ~/.willow/nestor and ~/.nestor exist, the Willow-scoped
    store wins — the household store is only the belt-and-suspenders
    fallback for operators without a Willow overlay."""
    _clear_store_env(monkeypatch)
    monkeypatch.setattr(nestor_client.Path, "home", classmethod(lambda cls: tmp_path))
    willow = tmp_path / ".willow" / "nestor"
    willow.mkdir(parents=True)
    household = tmp_path / ".nestor"
    household.mkdir()
    assert nestor_client._default_store_path() == willow


@pytest.mark.skipif(shutil.which("nestor") is None, reason="real nestor binary not installed")
def test_real_nestor_available_probe():
    nc = NestorClient()
    assert nc.available() is True
    nc.close()
