# b17: WGRV1 ΔΣ=42
"""End-to-end journal round-trip: writer → mock willow-mcp → reader.

Pins the C11 protocol seam (``docs/design/autonomous-continuity.md``
C11) and the three-state contract (``docs/INVARIANTS.md`` §1); §10
guards the CI witness that runs this suite.

Every test runs against the mock in ``mock_willow_mcp.py``. The mock
speaks the same routes as the real willow-mcp (``POST /tools/kb_journal``
+ GET/POST ``/tools/kb_journal_read``), which is what makes the
round-trip real rather than a shim.

Discipline pinned:

* the writer's payload lands in the mock as-is and comes back through
  the reader byte-for-byte (operator words are load-bearing, V5-adjacent);
* ``since_id`` trims to strictly-newer atoms in newest-first order;
* the mock's ``/kill`` toggle exercises the three-state discipline —
  ``Unreachable`` on both writer and reader when the source is not
  reachable, and immediate recovery once the mock is restored;
* special characters (quotes, unicode, embedded newlines) survive the
  round-trip verbatim.
"""
from __future__ import annotations

import unittest

import pytest

from grove import journal_reader, journal_writer
from grove.errors import Unreachable


# --- Test 1: single-atom round-trip ------------------------------------

def test_single_atom_round_trip(mock_mcp):
    """A single write goes in; the reader hands it back with text intact."""
    result = journal_writer.write_operator_turn(text="test 1", sender="operator")
    assert result["ok"] is True
    assert isinstance(result["id"], str) and result["id"]

    atoms = journal_reader.read_recent(limit=10)
    assert len(atoms) == 1
    atom = atoms[0]
    assert atom["text"] == "test 1"
    assert atom["sender"] == "operator"
    assert atom["id"] == result["id"]


# --- Test 2: five atoms, newest first ----------------------------------

def test_five_atoms_round_trip_newest_first(mock_mcp):
    """Five sequential writes come back newest-first through the reader."""
    payloads = ["atom-a", "atom-b", "atom-c", "atom-d", "atom-e"]
    for text in payloads:
        journal_writer.write_operator_turn(text=text, sender="operator")

    atoms = journal_reader.read_recent(limit=10)
    assert len(atoms) == 5
    # Newest-first: reversed insertion order.
    assert [a["text"] for a in atoms] == list(reversed(payloads))


# --- Test 3: since_id filter ------------------------------------------

def test_since_id_filters_to_strictly_newer_atoms(mock_mcp):
    """``since_id`` returns atoms strictly newer than the given id."""
    ids_by_text: dict[str, str] = {}
    for text in ("a", "b", "c", "d", "e"):
        result = journal_writer.write_operator_turn(text=text, sender="operator")
        ids_by_text[text] = result["id"]

    # `c` is the 3rd write; atoms strictly newer are `d` and `e`
    # (newest-first). Its own id should not appear in the filtered read.
    since = ids_by_text["c"]
    atoms = journal_reader.read_recent(limit=10, since_id=since)
    assert [a["text"] for a in atoms] == ["e", "d"]
    assert since not in {a["id"] for a in atoms}


# --- Test 4: three-state discipline — kill the mock -------------------

def test_kill_the_mock_raises_unreachable_on_both_seams(mock_mcp):
    """Kill the mock → writer AND reader raise ``Unreachable``.

    Three-state (INVARIANTS.md §1) says an unreachable source MUST NOT
    collapse into an empty return — the reader raises so the endpoint
    layer can answer 503 + ``state="unreachable"``. The writer raises
    for the same reason.
    """
    # Warm the path first so we know Unreachable is a state change,
    # not a static failure.
    journal_writer.write_operator_turn(text="pre-kill", sender="operator")
    atoms = journal_reader.read_recent(limit=10)
    assert atoms and atoms[0]["text"] == "pre-kill"

    mock_mcp.kill()

    with pytest.raises(Unreachable) as excinfo:
        journal_writer.write_operator_turn(text="post-kill", sender="operator")
    assert isinstance(excinfo.value.reason, str) and excinfo.value.reason

    with pytest.raises(Unreachable) as excinfo:
        journal_reader.read_recent(limit=10)
    assert isinstance(excinfo.value.reason, str) and excinfo.value.reason


# --- Test 5: restore the mock — the seam recovers ----------------------

def test_restore_the_mock_and_subsequent_writes_succeed(mock_mcp):
    """After ``/restore`` the writer and reader work again — no state stuck."""
    mock_mcp.kill()
    with pytest.raises(Unreachable):
        journal_writer.write_operator_turn(text="dropped", sender="operator")

    mock_mcp.restore()

    # Reset log-once so subsequent tests still see fresh emissions on
    # their own kill/restore cycles.
    journal_writer._reset_log_once_for_tests()
    journal_reader._reset_log_once_for_tests()

    result = journal_writer.write_operator_turn(text="after-restore", sender="operator")
    assert result["ok"] is True

    atoms = journal_reader.read_recent(limit=10)
    assert len(atoms) == 1
    assert atoms[0]["text"] == "after-restore"


# --- Test 6: verbatim preservation across special characters -----------

def test_verbatim_text_preservation_across_special_characters(mock_mcp):
    """Operator words survive quotes, unicode, and embedded newlines.

    V5-adjacent: the writer refuses to reshape ``text``. The mock
    stores the string as content, the reader returns it as text —
    no strip, no normalize, no re-encode.
    """
    weird = (
        'she said "hello" — with punctuation.\n'
        "second line\twith a tab,\n"
        "third line with unicode: 헤임달 · Ω · ✝ · 🜏\n"
        "    trailing spaces →   "
    )
    result = journal_writer.write_operator_turn(text=weird, sender="operator")
    assert result["ok"] is True

    atoms = journal_reader.read_recent(limit=10)
    assert len(atoms) == 1
    # Byte-for-byte — no unicode normalization, no whitespace collapse.
    assert atoms[0]["text"] == weird


# --- unittest wrapper so the module still runs under `python -m unittest` ---

class JournalRoundTripUnittest(unittest.TestCase):
    """Sentinel so a stray ``python -m unittest tests/...`` at least fails
    with a legible skip rather than looking like a broken suite.
    The real tests are the pytest functions above.
    """

    def test_this_module_needs_pytest(self) -> None:
        self.skipTest(
            "tests/e2e_willow_mcp/test_journal_roundtrip.py uses pytest "
            "fixtures (see conftest.py); run with pytest, not unittest."
        )
