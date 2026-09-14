"""Contract tests for grove-hook's four actions — one test per sealed row of
the wiring manifest, plus their fail-safe behaviors.

The wiring manifest itself is pinned by `tests/test_grove_hook_wiring_generated.py`;
this file pins what happens WHEN each row fires. Together the two say:
the truth table is what the sealed rows say, and each action does what its
row says it does.

Contract mapping (proposal §3, PR 70 pairs 1–5):
- orient / session_start — blockers + seat drift printed; nonblank
- reinject / prompt_submit + pre_compact — three byte-stable seat lines
- gate / stop — block once on a done-claim without a tool call this turn;
  advisory on stop_hook_active
- deposit / session_end — tool-call summary written to the deposits dir;
  cannot block; hard errors warn and continue
"""

from __future__ import annotations

import io
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HOOKS = ROOT / "hooks"
if str(HOOKS) not in sys.path:
    sys.path.insert(0, str(HOOKS))

import grove_hook  # noqa: E402


# ── fixtures ───────────────────────────────────────────────────────────────


def _write_transcript(path: Path, entries: list[dict]) -> None:
    """Write a JSONL transcript. One entry per line, decodable by
    grove_hook._iter_transcript."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for entry in entries:
            f.write(json.dumps(entry) + "\n")


def _asst_text(text: str) -> dict:
    """A transcript entry: assistant turn with one text block."""
    return {"type": "assistant", "content": [{"type": "text", "text": text}]}


def _asst_text_and_tool(text: str, tool_name: str = "Bash") -> dict:
    """Assistant turn with text AND a tool_use — the shape gate must not block."""
    return {
        "type": "assistant",
        "content": [
            {"type": "text", "text": text},
            {"type": "tool_use", "name": tool_name, "input": {}},
        ],
    }


def _stub_stdin(monkeypatch, payload: dict) -> None:
    monkeypatch.setattr(sys, "stdin", io.StringIO(json.dumps(payload)))


# ── reinject ───────────────────────────────────────────────────────────────


def test_reinject_prints_the_four_byte_stable_lines(capsys, monkeypatch):
    """proposal §3 — reinject is three byte-stable lines from seat.md, plus
    (post-CMM addendum) a fourth about the code graph. The tuple is the
    contract; the print order and content are pinned here."""
    monkeypatch.setenv("GROVE_SEAT_FILE", "")
    rc = grove_hook.reinject()
    assert rc == 0
    out = capsys.readouterr().out
    # Each REINJECT tuple entry appears verbatim in the output.
    for line in grove_hook.REINJECT:
        assert line in out, f"reinject dropped a contract line: {line!r}"


def test_reinject_flags_seat_drift_when_anchor_is_missing(
    capsys, monkeypatch, tmp_path
):
    """reinject also carries a seat-drift indicator so a session catches the
    moment the governance anchor stops living in seat.md."""
    seat = tmp_path / "seat.md"
    seat.write_text("nothing about the anchor here", encoding="utf-8")
    monkeypatch.setenv("GROVE_SEAT_FILE", str(seat))
    grove_hook.SEAT_FILE = str(seat)  # module read once at import
    grove_hook.reinject()
    out = capsys.readouterr().out
    assert "seat drift" in out


# ── gate ───────────────────────────────────────────────────────────────────


def test_gate_blocks_done_claim_with_no_tool_call(tmp_path, capsys, monkeypatch):
    """The sealed contract: refuse a turn claiming done with no evidence
    token. MVP evidence-token semantic = a tool_use block in the same turn."""
    transcript = tmp_path / "transcript.jsonl"
    _write_transcript(
        transcript,
        [
            _asst_text("Looked over the code. All tests pass."),
        ],
    )
    _stub_stdin(monkeypatch, {"transcript_path": str(transcript)})
    rc = grove_hook.gate()
    assert rc == 0
    out = capsys.readouterr().out
    decision = json.loads(out)
    assert decision["decision"] == "block"
    assert "grove gate" in decision["reason"]


def test_gate_allows_done_claim_with_a_tool_call_this_turn(
    tmp_path, capsys, monkeypatch
):
    """The 'evidence token' MVP: a tool call in the same turn is enough. Even
    if the text says 'all tests pass', the tool call proves work happened."""
    transcript = tmp_path / "transcript.jsonl"
    _write_transcript(
        transcript,
        [
            _asst_text_and_tool("Running the tests. All tests pass.", tool_name="Bash"),
        ],
    )
    _stub_stdin(monkeypatch, {"transcript_path": str(transcript)})
    rc = grove_hook.gate()
    assert rc == 0
    # No JSON decision on stdout — the hook allowed the stop.
    assert capsys.readouterr().out == ""


def test_gate_is_advisory_on_stop_hook_active(tmp_path, capsys, monkeypatch):
    """Second Stop after a block is advisory: don't fight the pinentry flow
    approval-broker §5c is designing. Message to stderr, exit 0, no block."""
    transcript = tmp_path / "transcript.jsonl"
    _write_transcript(transcript, [_asst_text("all tests pass")])
    _stub_stdin(
        monkeypatch, {"transcript_path": str(transcript), "stop_hook_active": True}
    )
    rc = grove_hook.gate()
    assert rc == 0
    captured = capsys.readouterr()
    assert captured.out == ""
    assert "advisory" in captured.err


def test_gate_fails_open_on_missing_transcript(monkeypatch, capsys):
    """A malformed hook payload or a missing transcript is not this hook's
    problem to police — fail open, exit 0."""
    _stub_stdin(monkeypatch, {})
    rc = grove_hook.gate()
    assert rc == 0
    assert capsys.readouterr().out == ""


def test_gate_allows_a_neutral_stop(tmp_path, capsys, monkeypatch):
    """A turn that doesn't claim 'done' passes without comment."""
    transcript = tmp_path / "transcript.jsonl"
    _write_transcript(
        transcript,
        [_asst_text("Left a note in the plan file. Waiting on your call.")],
    )
    _stub_stdin(monkeypatch, {"transcript_path": str(transcript)})
    rc = grove_hook.gate()
    assert rc == 0
    assert capsys.readouterr().out == ""


# ── deposit ────────────────────────────────────────────────────────────────


def test_deposit_writes_summary_to_deposits_dir(tmp_path, monkeypatch):
    """SessionEnd deposit shape: a JSON file at
    $WILLOW_HOME/deposits/<sid>.json with session_id, recorded_at, and a
    tool-call summary. `total` and `by_tool` come from a walk of the
    transcript's tool_use blocks."""
    transcript = tmp_path / "transcript.jsonl"
    _write_transcript(
        transcript,
        [
            _asst_text_and_tool("first", tool_name="Bash"),
            _asst_text_and_tool("second", tool_name="Bash"),
            _asst_text_and_tool("third", tool_name="Read"),
        ],
    )
    willow_home = tmp_path / "willow_home"
    monkeypatch.setenv("WILLOW_HOME", str(willow_home))
    _stub_stdin(
        monkeypatch,
        {"session_id": "sid_abc", "transcript_path": str(transcript)},
    )
    rc = grove_hook.deposit()
    assert rc == 0
    landed = willow_home / "deposits" / "sid_abc.json"
    assert landed.is_file(), "deposit did not write the summary JSON"
    body = json.loads(landed.read_text())
    assert body["session_id"] == "sid_abc"
    assert body["tool_calls"]["total"] == 3
    assert body["tool_calls"]["by_tool"] == {"Bash": 2, "Read": 1}


def test_deposit_never_raises_on_unwritable_dir(tmp_path, monkeypatch, capsys):
    """SessionEnd cannot block (Nestor's finding). If the deposits dir is
    unwritable the hook warns to stderr and exits zero, so a session can
    still tear down cleanly."""
    unwritable = tmp_path / "readonly_root"
    unwritable.mkdir()
    # Make the target path collide with a REGULAR FILE the mkdir refuses to
    # replace with a directory — the write fails, we still exit 0.
    (unwritable / "deposits").write_text("not a directory", encoding="utf-8")
    monkeypatch.setenv("WILLOW_HOME", str(unwritable))
    _stub_stdin(monkeypatch, {"session_id": "sid_xyz", "transcript_path": ""})
    rc = grove_hook.deposit()
    assert rc == 0
    captured = capsys.readouterr()
    assert "could not write" in captured.err


def test_deposit_handles_missing_transcript_gracefully(tmp_path, monkeypatch):
    """No transcript means no tool-call counts, not a crash. The summary still
    lands with total=0."""
    willow_home = tmp_path / "willow_home"
    monkeypatch.setenv("WILLOW_HOME", str(willow_home))
    _stub_stdin(
        monkeypatch,
        {"session_id": "sid_empty", "transcript_path": ""},
    )
    rc = grove_hook.deposit()
    assert rc == 0
    landed = willow_home / "deposits" / "sid_empty.json"
    body = json.loads(landed.read_text())
    assert body["tool_calls"] == {"total": 0, "by_tool": {}}
