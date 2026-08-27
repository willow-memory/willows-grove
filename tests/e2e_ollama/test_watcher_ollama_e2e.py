# b17: WGRV1 ΔΣ=42
"""End-to-end pin for the C11 LEFT-side write path (INVARIANTS.md §10).

This is the integration companion to ``tests/test_resident_watcher.py``.
The unit tests mock psycopg2, urllib, and journal_writer; this test
wires the real Postgres LISTEN/NOTIFY seam to a real Ollama classifier
and asserts the resulting journal writes carry the invariants named in
``grove/resident_watcher.py``'s Gate 5 three-question lock:

* ``sender="resident-watcher"`` — Q3 lock; nothing else may sign this
  atom.
* a ``domain:<value>`` tag in the closed set ``DOMAINS`` — Q2 lock;
  classification is a tag, never a persona-route.
* ``text`` written verbatim (V5 discipline; the operator's words are
  load-bearing — ``journal_writer.write_operator_turn`` never
  paraphrases).

The whole test skips (never fails) when Ollama is unreachable, when
Postgres is unreachable, or when no tiny model can be pulled — the
suite is CI-first per INVARIANTS.md §10, but the operator-side build
is entitled to run green without either service. Skip reasons are
visible in the pytest log so a CI regression reads as a fail, not a
silent skip.

Cost caveat: pulling the model is slow (~30-60s) on a cold CI runner.
The ``pulled_model`` fixture is session-scoped and caches the winner,
so the readiness canary and this test share one pull.
"""
from __future__ import annotations

import os
import sys
import time
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from grove import resident_watcher  # noqa: E402
from grove.resident_watcher import DOMAINS, SENDER, ResidentWatcher  # noqa: E402


# Test messages — mixed content so we exercise the classification surface
# rather than pinning one output. The classifier is a tiny model and can
# read any of these three as ``unknown``; that is still a valid domain
# per the closed set, and still exercises the write path. The assertion
# below is on the *shape* of the write, not on which domain the model
# picked.
_TEST_MESSAGES = [
    ("alice", "hey, how's your weekend going?"),           # chat-shaped
    ("board", "We move to seal the pair; motion carries."),  # governance-shaped
    ("pm-bot", "Ship PR 8 by EOD Friday. Blocker on CI."),   # pm-shaped
]

_WAIT_FOR_JOURNAL_TIMEOUT = 60.0  # generous — model warm-up on cold CI


def _insert_message(dsn: str, channel_id: int, sender: str, content: str) -> None:
    """Insert one row into ``grove.messages`` — the NOTIFY trigger fires."""
    import psycopg2  # type: ignore

    conn = psycopg2.connect(dsn)
    conn.autocommit = True
    try:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO grove.messages (channel_id, sender, content) "
            "VALUES (%s, %s, %s);",
            (channel_id, sender, content),
        )
    finally:
        try:
            conn.close()
        except Exception:  # noqa: BLE001
            pass


def _wait_for_captures(captures: list, n: int, deadline: float) -> None:
    """Poll until ``captures`` has at least ``n`` rows or the deadline lapses."""
    while time.monotonic() < deadline and len(captures) < n:
        time.sleep(0.25)


def test_watcher_listen_classify_journal_e2e(
    ollama_ready,
    pulled_model,
    grove_pg_schema,
    willow_mcp_capture,
    monkeypatch,
):
    """LISTEN → Ollama classify → journal write, end-to-end (INVARIANTS.md §10).

    Timeline:

    1. Instantiate ``ResidentWatcher`` with the CI DSN + the pulled model
       + a fast (2s) heartbeat + the real Ollama URL.
    2. Widen ``_OLLAMA_TIMEOUT_SECONDS`` for the test — the watcher's
       production default (2.0s) is deliberately aggressive so a slow
       model degrades to ``unknown`` rather than blocking the seat; on
       a cold CI runner the first generate takes longer than that, so
       the test-time constant lets us actually pin the classification
       path instead of always seeing the D7 fallback.
    3. ``start()`` — LISTEN/worker/heartbeat threads come up.
    4. Insert three messages via ``grove.messages``; the trigger fires
       ``pg_notify('grove_channel', channel_id::text)``.
    5. Wait up to ``_WAIT_FOR_JOURNAL_TIMEOUT`` for three journal
       captures.
    6. Assert every capture carries ``source="resident-watcher"``, a
       ``domain:<value>`` tag in ``DOMAINS``, and includes the source
       text verbatim in the content.
    7. ``stop()`` — clean shutdown, threads join.
    """
    # Widen the classifier's per-call timeout for the duration of the test.
    monkeypatch.setattr(resident_watcher, "_OLLAMA_TIMEOUT_SECONDS", 45.0)

    dsn = grove_pg_schema["dsn"]
    channel_id = grove_pg_schema["channel_id"]

    watcher = ResidentWatcher(
        db_url=dsn,
        model_name=pulled_model,
        ollama_url=ollama_ready,
        heartbeat_seconds=2,
    )
    watcher.start()

    try:
        # Wait a beat for the LISTEN thread to actually issue LISTEN before
        # sending. Without this the first INSERT can fire NOTIFY before the
        # subscription is live and the row is silently missed on some runners.
        time.sleep(1.0)

        for sender, content in _TEST_MESSAGES:
            _insert_message(dsn, channel_id, sender, content)
            # Space the inserts so classify calls serialize through the
            # single worker without racing on a warmup burst.
            time.sleep(0.2)

        deadline = time.monotonic() + _WAIT_FOR_JOURNAL_TIMEOUT
        _wait_for_captures(willow_mcp_capture, len(_TEST_MESSAGES), deadline)

        assert len(willow_mcp_capture) >= len(_TEST_MESSAGES), (
            f"expected {len(_TEST_MESSAGES)} journal writes, "
            f"got {len(willow_mcp_capture)} within "
            f"{_WAIT_FOR_JOURNAL_TIMEOUT:.0f}s: {willow_mcp_capture!r}"
        )
    finally:
        watcher.stop(timeout=5.0)

    # ------------------------------------------------------------------
    # Assertions — one per Gate 5 three-question lock (Q2, Q3) + V5.
    # ------------------------------------------------------------------

    # Map each source utterance to at least one capture that carries it verbatim.
    remaining = list(_TEST_MESSAGES)
    for capture in willow_mcp_capture[: len(_TEST_MESSAGES)]:
        # Q3 lock — every write carries sender="resident-watcher".
        assert capture["source"] == SENDER, (
            f"Q3 violation: journal write source={capture['source']!r}, "
            f"expected {SENDER!r} (INVARIANTS.md §10 pinning "
            f"resident_watcher Q3)."
        )

        tags = capture["tags"]
        assert isinstance(tags, list), f"tags not a list: {tags!r}"

        # Base tag surface — journal_writer._build_tags contract.
        assert "journal" in tags, f"missing 'journal' base tag: {tags!r}"
        sender_tags = [t for t in tags if t.startswith("sender:")]
        assert sender_tags == [f"sender:{SENDER}"], (
            f"sender tag drift: {sender_tags!r}"
        )
        ts_tags = [t for t in tags if t.startswith("ts:")]
        assert len(ts_tags) == 1, f"expected exactly one ts:* tag, got {ts_tags!r}"

        # Q2 lock — classification lands as a domain:<value> tag in DOMAINS.
        domain_tags = [t for t in tags if t.startswith("domain:")]
        assert len(domain_tags) == 1, (
            f"expected exactly one domain:* tag, got {domain_tags!r}"
        )
        domain = domain_tags[0].split(":", 1)[1]
        assert domain in DOMAINS, (
            f"Q2 violation: domain {domain!r} not in closed set {DOMAINS!r}."
        )

        # V5 discipline — the operator's utterance is in the atom verbatim.
        # journal_writer receives the ``content`` field as
        # ``f"[{domain}] {sender}: {text}"`` (see ResidentWatcher._on_message)
        # so the source text must appear inside content.
        content = capture["content"]
        assert isinstance(content, str) and content, f"empty content: {capture!r}"

        matched: tuple[str, str] | None = None
        for sender, text in remaining:
            if text in content and sender in content:
                matched = (sender, text)
                break
        assert matched is not None, (
            f"V5 violation: no source utterance found verbatim in {content!r}. "
            f"remaining candidates: {remaining!r}"
        )
        remaining.remove(matched)

    assert not remaining, (
        f"not every source message produced a journal write: {remaining!r} "
        f"remained un-matched after {len(willow_mcp_capture)} captures."
    )
