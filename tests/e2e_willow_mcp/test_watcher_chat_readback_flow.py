# b17: WGRV1 ΔΣ=42
"""C11 end-to-end: resident watcher LEFT-write → chat RIGHT-read.

Autonomous-continuity (``docs/design/autonomous-continuity.md``) C11
sealed the chat card as *operator (LEFT) → resident watcher writes
kb_journal → chat card reads kb_journal (RIGHT) → operator sees
Willow's answer*. This test pins the full loop with the mock
``willow-mcp`` in the middle, so the seam between
``grove/resident_watcher.py``, ``grove/journal_writer.py``, and
``grove/journal_reader.py`` is exercised as one system.

Three-state discipline (``docs/INVARIANTS.md`` §1) is what the loop
protects: the RIGHT-side read after a real LEFT-side write returns a
populated atom, not empty and not unreachable. §10 guards the CI
witness.

Postgres LISTEN is bypassed — we call ``ResidentWatcher._on_message``
directly with a synthesized row. That is the same seam the LISTEN
callback uses (see ``resident_watcher.py:_on_notify`` → the row it
enqueues has ``id``, ``sender``, ``content``, ``channel_id``), so
skipping the transport does not skip the classification / Nestor /
journal-write pipeline being tested.
"""
from __future__ import annotations

from grove import journal_reader
from grove.resident_watcher import DOMAINS, SENDER, ResidentWatcher


class _NestorPermits:
    """Stand-in for ``NestorClient`` that permits every decision (D7 posture)."""

    def decision_check(self, question):
        return None  # None → resident_watcher._nestor_permits returns True

    def close(self) -> None:
        return None


def test_watcher_writes_and_chat_reads_back_the_same_atom(mock_mcp):
    """One message through the watcher lands as a readable atom on the chat side.

    Assert the round-trip preserves sender=``resident-watcher`` (Q3
    lock, ``resident_watcher.py:29-30``), the classified domain
    (Q2 lock — a tag on the atom), and the original message bytes
    the watcher observed.
    """
    watcher = ResidentWatcher(db_url=None, model_name="testmodel:1b", heartbeat_seconds=3600)
    watcher._nestor = _NestorPermits()

    row = {"id": 1, "sender": "operator", "content": "please schedule my dentist"}

    # Stub the classifier at the method seam — isolates classification from
    # the journal MCP write path.
    watcher._classify_message = lambda text, sender: "pa"

    watcher._on_message(row)

    # RIGHT side — the same seam the chat card reads through
    # (`window.groveReadJournal` → `/api/journal/recent` →
    # `grove/journal_reader.read_recent`).
    atoms = journal_reader.read_recent(limit=10)
    assert len(atoms) == 1
    atom = atoms[0]

    # Q3 lock — sender is the watcher, not "operator" or a persona name.
    assert atom["sender"] == SENDER == "resident-watcher"

    # Q2 lock — the classified domain rides on the atom's tags.
    tags = mock_mcp.store.snapshot()[0]["tags"]
    assert "domain:pa" in tags
    assert "sender:resident-watcher" in tags
    assert "journal" in tags

    # V5-adjacent — the operator's text is embedded verbatim in the
    # journal atom. The watcher wraps it as `[<domain>] <sender>: <text>`;
    # the text itself is untouched inside the wrapper.
    assert "please schedule my dentist" in atom["text"]
    assert "[pa]" in atom["text"]
    assert "operator" in atom["text"]


def test_unknown_domain_still_round_trips(mock_mcp):
    """Ollama garbage → domain='unknown' → still lands on the chat side.

    D7 posture: a classifier hiccup is not a reason to drop the message.
    """
    watcher = ResidentWatcher(db_url=None, model_name="testmodel:1b", heartbeat_seconds=3600)
    watcher._nestor = _NestorPermits()

    row = {"id": 42, "sender": "operator", "content": "this is a chat-y message"}

    # Classifier stub returns 'unknown' — the D7 fallback membership.
    watcher._classify_message = lambda text, sender: "unknown"

    watcher._on_message(row)

    atoms = journal_reader.read_recent(limit=10)
    assert len(atoms) == 1
    assert atoms[0]["sender"] == "resident-watcher"
    assert "[unknown]" in atoms[0]["text"]
    # Every domain the watcher may emit — including the D7 fallback —
    # must still be a member of the closed vocabulary.
    tag_domains = [
        tag.split(":", 1)[1]
        for tag in mock_mcp.store.snapshot()[0]["tags"]
        if tag.startswith("domain:")
    ]
    assert tag_domains == ["unknown"]
    assert "unknown" in DOMAINS
