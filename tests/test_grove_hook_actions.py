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

import pytest


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


@pytest.fixture(autouse=True)
def quiet_grove_inbox(tmp_path, monkeypatch):
    """Every test in this module runs against a quiet, hermetic Grove inbox:
    the reader is stubbed to `empty` and hook state lands under a tmp
    WILLOW_HOME, so no test touches Postgres or the box's anchors. The
    inbox tests below override the stub per case."""
    monkeypatch.setenv("WILLOW_HOME", str(tmp_path / "willow_home"))
    monkeypatch.setattr(grove_hook, "APP_ID", "willow")
    monkeypatch.setattr(grove_hook, "SESSION_ID", "sid_test")
    monkeypatch.setattr(
        grove_hook,
        "_grove_inbox_read",
        lambda app_id, since_id: {
            "state": "empty",
            "reason": "",
            "rows": [],
            "max_id": since_id,
        },
    )
    # The real read runs on a worker thread; tests keep it, so timeouts are
    # exercised where a test asks for them.
    yield


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


# ── B3+ Nestor-first at reinject ───────────────────────────────────────────


@pytest.fixture
def isolated_sentinel(tmp_path, monkeypatch):
    """Rebase the sentinel path to a tmp directory unique per test, so a
    test's sentinel doesn't leak across tests but IS persistent within one
    test (i.e. a second call to the same state sees the sentinel already
    exists — that is the "once per session" semantic under test)."""
    sentinel_dir = tmp_path / "sentinels"
    sentinel_dir.mkdir()

    def _sentinel(reach: str) -> Path:
        # Path is deterministic per (test, reach) — no side effects here.
        return sentinel_dir / f"grove-nestor-{reach}.flag"

    monkeypatch.setattr(grove_hook, "_status_line_sentinel_path", _sentinel)
    return sentinel_dir


def test_reinject_prepends_nestor_state_when_reachable(
    monkeypatch, capsys, isolated_sentinel
):
    """proposal §3 first row: when Nestor answers, its state travels ahead of
    the seat lines as attributed context."""
    monkeypatch.setattr(grove_hook, "_nestor_reach", lambda: "reachable")
    monkeypatch.setattr(
        grove_hook,
        "_nestor_ask",
        lambda prompt: {"state": "sealed", "age": 12},
    )
    _stub_stdin(monkeypatch, {"prompt": "what's the state of the port map?"})
    monkeypatch.setenv("GROVE_SEAT_FILE", "")
    rc = grove_hook.reinject()
    assert rc == 0
    out = capsys.readouterr().out
    lines = [line for line in out.split("\n") if line.strip()]
    # First non-empty line is the Nestor state
    assert lines[0].startswith("Nestor: sealed"), (
        f"Nestor state line should lead the reinject; got {lines[0]!r}"
    )
    # And the seat lines still appear.
    assert all(seat_line in out for seat_line in grove_hook.REINJECT)


def test_reinject_prints_not_installed_boot_line_once(
    monkeypatch, capsys, isolated_sentinel
):
    """proposal §3 second row: 'Nestor is not on this box' prints once per
    session, not on every prompt_submit."""
    monkeypatch.setattr(grove_hook, "_nestor_reach", lambda: "not_installed")
    monkeypatch.setenv("GROVE_SEAT_FILE", "")
    _stub_stdin(monkeypatch, {"prompt": "hi"})
    grove_hook.reinject()
    first = capsys.readouterr().out
    assert "Nestor is not on this box" in first

    _stub_stdin(monkeypatch, {"prompt": "second turn"})
    grove_hook.reinject()
    second = capsys.readouterr().out
    assert "Nestor is not on this box" not in second, (
        "boot line must print only once per session"
    )
    # Seat lines still there on the second turn.
    assert all(line in second for line in grove_hook.REINJECT)


def test_reinject_prints_not_answering_line(monkeypatch, capsys, isolated_sentinel):
    """proposal §3 third row: 'Nestor did not answer; unverified turn' is the
    single-line fail-open, first turn."""
    monkeypatch.setattr(grove_hook, "_nestor_reach", lambda: "installed_not_answering")
    monkeypatch.setenv("GROVE_SEAT_FILE", "")
    _stub_stdin(monkeypatch, {"prompt": "anything"})
    grove_hook.reinject()
    out = capsys.readouterr().out
    assert "Nestor did not answer; unverified turn" in out


def test_reinject_reachable_but_ask_returns_none(
    monkeypatch, capsys, isolated_sentinel
):
    """When _nestor_ask returns None (transient failure — timeout, unexpected
    stdout shape) the reinject shows no Nestor line and still emits the seat
    lines. Fail open at the row, not at the reinject itself."""
    monkeypatch.setattr(grove_hook, "_nestor_reach", lambda: "reachable")
    monkeypatch.setattr(grove_hook, "_nestor_ask", lambda prompt: None)
    monkeypatch.setenv("GROVE_SEAT_FILE", "")
    _stub_stdin(monkeypatch, {"prompt": "hi"})
    grove_hook.reinject()
    out = capsys.readouterr().out
    assert "Nestor:" not in out
    assert all(line in out for line in grove_hook.REINJECT)


# ── B3+ Jarvis close-out at deposit ────────────────────────────────────────


def _make_draft_bundle(nestor_dir: Path, name: str, count: int) -> None:
    """Write a Nestor bundle with `count` draft pairs. Just enough shape for
    `_count_unsealed_drafts` to see them."""
    nestor_dir.mkdir(parents=True, exist_ok=True)
    body = {
        "nestor_bundle": 4,
        "pairs": [{"status": "draft"} for _ in range(count)],
    }
    (nestor_dir / name).write_text(json.dumps(body), encoding="utf-8")


def test_deposit_jarvis_close_out_when_drafts_and_ui_off(tmp_path, monkeypatch, capsys):
    """proposal §3 close-out row 1: unsealed drafts, UI not serving →
    line printed AND nestor ui launched fire-and-forget."""
    grove_dir = tmp_path / "willows-grove"
    (grove_dir / "hooks").mkdir(parents=True)
    grove_hook_dst = grove_dir / "hooks" / "grove_hook.py"
    grove_hook_dst.write_text("# placeholder for path anchor", encoding="utf-8")
    _make_draft_bundle(grove_dir / "nestor", "b.json", count=3)

    monkeypatch.setattr(grove_hook, "__file__", str(grove_hook_dst))
    monkeypatch.setattr(grove_hook, "_nestor_reach", lambda: "not_installed")
    popen_calls: list[list[str]] = []

    def _fake_popen(cmd, **_kwargs):
        popen_calls.append(cmd)

        class _P:
            pass

        return _P()

    monkeypatch.setattr(grove_hook.subprocess, "Popen", _fake_popen)
    willow_home = tmp_path / "willow_home"
    monkeypatch.setenv("WILLOW_HOME", str(willow_home))
    _stub_stdin(monkeypatch, {"session_id": "sid_j1", "transcript_path": ""})

    grove_hook.deposit()
    err = capsys.readouterr().err
    assert "The store is open if you'd like to sign them." in err
    assert popen_calls and popen_calls[0][:2] == ["nestor", "ui"], (
        "close-out row 1 must launch `nestor ui` fire-and-forget"
    )


def test_deposit_jarvis_close_out_when_drafts_and_ui_serving(
    tmp_path, monkeypatch, capsys
):
    """proposal §3 close-out row 2: unsealed drafts + UI already serving →
    same line, no Popen (don't spawn a duplicate)."""
    grove_dir = tmp_path / "willows-grove"
    (grove_dir / "hooks").mkdir(parents=True)
    grove_hook_dst = grove_dir / "hooks" / "grove_hook.py"
    grove_hook_dst.write_text("# placeholder", encoding="utf-8")
    _make_draft_bundle(grove_dir / "nestor", "b.json", count=1)

    monkeypatch.setattr(grove_hook, "__file__", str(grove_hook_dst))
    monkeypatch.setattr(grove_hook, "_nestor_reach", lambda: "reachable")
    popen_calls: list[list[str]] = []

    def _fake_popen(cmd, **_kwargs):
        popen_calls.append(cmd)

        class _P:
            pass

        return _P()

    monkeypatch.setattr(grove_hook.subprocess, "Popen", _fake_popen)
    willow_home = tmp_path / "willow_home"
    monkeypatch.setenv("WILLOW_HOME", str(willow_home))
    _stub_stdin(monkeypatch, {"session_id": "sid_j2", "transcript_path": ""})

    grove_hook.deposit()
    err = capsys.readouterr().err
    assert "The store is open if you'd like to sign them." in err
    assert popen_calls == [], (
        "close-out row 2 must not spawn nestor ui when 8765 already answers"
    )


def test_deposit_jarvis_silent_when_no_drafts(tmp_path, monkeypatch, capsys):
    """proposal §3 close-out row 3: no unsealed drafts → voice says nothing."""
    grove_dir = tmp_path / "willows-grove"
    (grove_dir / "hooks").mkdir(parents=True)
    (grove_dir / "nestor").mkdir()  # empty dir — no bundles
    grove_hook_dst = grove_dir / "hooks" / "grove_hook.py"
    grove_hook_dst.write_text("# placeholder", encoding="utf-8")

    monkeypatch.setattr(grove_hook, "__file__", str(grove_hook_dst))
    monkeypatch.setattr(grove_hook, "_nestor_reach", lambda: "not_installed")
    willow_home = tmp_path / "willow_home"
    monkeypatch.setenv("WILLOW_HOME", str(willow_home))
    _stub_stdin(monkeypatch, {"session_id": "sid_j3", "transcript_path": ""})

    grove_hook.deposit()
    err = capsys.readouterr().err
    assert "store is open" not in err
    assert "sign them" not in err
    # Deposit summary still landed.
    assert (willow_home / "deposits" / "sid_j3.json").is_file()


# ── Grove inbox at reinject (sealed pair 11ccb0f7) ─────────────────────────


def _inbox_rows(*specs: tuple[int, str, str, str]) -> list[dict]:
    """Exactly the shape willow_mcp.grove.inbox_bundle returns: {id, channel,
    sender, content} — no timestamp reaches the hook (Loki 15D211C7)."""
    return [
        {"id": i, "channel": ch, "sender": who, "content": text}
        for i, ch, who, text in specs
    ]


def _stub_inbox(
    monkeypatch,
    rows: list[dict],
    *,
    state: str | None = None,
    max_id: int | None = None,
):
    calls: list[int] = []

    def _read(app_id: str, since_id: int) -> dict:
        calls.append(since_id)
        # Malformed rows (no id, not a dict) ride along unfiltered — the
        # formatter under test is what must cope with them.
        unread = [
            r
            for r in rows
            if not isinstance(r, dict) or int(r.get("id") or 0) > since_id
        ]
        ids = [int(r["id"]) for r in rows if isinstance(r, dict) and r.get("id")]
        top = max_id if max_id is not None else max(ids + [since_id])
        return {
            "state": state or ("populated" if unread else "empty"),
            "reason": "" if state != "unreachable" else "postgres unavailable",
            "rows": unread,
            "max_id": top,
        }

    monkeypatch.setattr(grove_hook, "_grove_inbox_read", _read)
    return calls


def _seed_anchor(session_id: str, last_id: int) -> None:
    grove_hook._write_anchor(
        grove_hook._grove_anchor_path("session", session_id), last_id
    )


def _quiet_nestor(monkeypatch):
    """No Nestor line, no seat-drift line: the real hooks/seat.md carries the
    anchor, so the only lines left are REINJECT plus whatever the inbox adds."""
    monkeypatch.setattr(grove_hook, "_nestor_reach", lambda: "reachable")
    monkeypatch.setattr(grove_hook, "_nestor_ask", lambda prompt: None)
    seat = str(HOOKS / "seat.md")
    monkeypatch.setenv("GROVE_SEAT_FILE", seat)
    monkeypatch.setattr(grove_hook, "SEAT_FILE", seat)


def _reinject_lines(monkeypatch, capsys, session_id: str = "sid_test") -> list[str]:
    _stub_stdin(monkeypatch, {"prompt": "hi", "session_id": session_id})
    assert grove_hook.reinject() == 0
    return [ln for ln in capsys.readouterr().out.split("\n") if ln.strip()]


def test_inbox_unread_items_emit_lines_and_advance_the_anchor(monkeypatch, capsys):
    """The sealed clause: a red on a PR this seat opened is in front of the
    seat on its next prompt. One line per unread item, newest last; the
    anchor moves past them so the next prompt is quiet."""
    _quiet_nestor(monkeypatch)
    _seed_anchor("sid_test", 100)
    _stub_inbox(
        monkeypatch,
        _inbox_rows(
            (
                101,
                "willow",
                "willows-bot",
                "CI red: willow-memory/ratatosk#48 @ 632225c — lint — https://x/job/1",
            ),
            (102, "willow", "loki", "audit 4177ABB8 written"),
        ),
    )
    lines = _reinject_lines(monkeypatch, capsys)
    inbox = [ln for ln in lines if ln.startswith("[grove")]
    assert inbox == [
        "[grove #willow willows-bot] CI red: willow-memory/ratatosk#48 @ 632225c — lint — https://x/job/1",
        "[grove #willow loki] audit 4177ABB8 written",
    ]
    assert all(seat_line in lines for seat_line in grove_hook.REINJECT)
    assert (
        grove_hook._read_anchor(grove_hook._grove_anchor_path("session", "sid_test"))
        == 102
    )
    assert (
        grove_hook._read_anchor(grove_hook._grove_anchor_path("seat", "willow")) == 102
    )
    # Next prompt: nothing new → no inbox line at all.
    again = _reinject_lines(monkeypatch, capsys)
    assert not [ln for ln in again if ln.startswith("[grove")]


def test_inbox_quiet_emits_exactly_the_seat_lines(monkeypatch, capsys):
    """Silence is the populated-empty case: no inbox line, the byte-stable
    seat lines and nothing else."""
    _quiet_nestor(monkeypatch)
    _seed_anchor("sid_test", 7)
    _stub_inbox(monkeypatch, [])
    lines = _reinject_lines(monkeypatch, capsys)
    assert lines == list(grove_hook.REINJECT)


def test_inbox_unreachable_emits_one_line_and_leaves_the_anchor(monkeypatch, capsys):
    """Grove down is said once and plainly; the anchor does not move, so
    whatever landed while it was down surfaces when it is back."""
    _quiet_nestor(monkeypatch)
    _seed_anchor("sid_test", 50)
    _stub_inbox(
        monkeypatch,
        _inbox_rows((51, "willow", "willows-bot", "CI red")),
        state="unreachable",
    )
    lines = _reinject_lines(monkeypatch, capsys)
    inbox = [ln for ln in lines if ln.startswith("[grove")]
    assert inbox == ["[grove unreachable: postgres unavailable]"]
    assert (
        grove_hook._read_anchor(grove_hook._grove_anchor_path("session", "sid_test"))
        == 50
    )


def test_inbox_timeout_reads_as_unreachable(monkeypatch, capsys):
    """A hung read is bounded: the worker is abandoned at the budget and the
    reinject says `unreachable: timeout`, never blocks the turn."""
    import time

    _quiet_nestor(monkeypatch)
    _seed_anchor("sid_test", 1)
    monkeypatch.setattr(grove_hook, "_GROVE_INBOX_TIMEOUT_S", 0.05)

    def _hang(app_id, since_id):
        time.sleep(0.5)
        return {"state": "empty", "reason": "", "rows": [], "max_id": since_id}

    monkeypatch.setattr(grove_hook, "_grove_inbox_read", _hang)
    lines = _reinject_lines(monkeypatch, capsys)
    inbox = [ln for ln in lines if ln.startswith("[grove")]
    assert inbox == ["[grove unreachable: timeout after 0s]"]
    assert (
        grove_hook._read_anchor(grove_hook._grove_anchor_path("session", "sid_test"))
        == 1
    )


def test_inbox_backlog_is_paged_oldest_first_and_nothing_is_consumed(
    monkeypatch, capsys
):
    """Eight unread: the first prompt shows the oldest five and a tail naming
    the anchor; the anchor moves only past what was shown, so the second
    prompt shows the remaining three and the third prompt is quiet (Loki
    15D211C7: a backlog beyond the bound must not be consumed by the tail)."""
    _quiet_nestor(monkeypatch)
    _seed_anchor("sid_test", 0)
    rows = _inbox_rows(*[(i, "willow", "bot", f"item {i}") for i in range(1, 9)])
    _stub_inbox(monkeypatch, rows)

    first = [
        ln
        for ln in _reinject_lines(monkeypatch, capsys)
        if ln.startswith("[grove") or ln.startswith("…")
    ]
    assert len(first) == 6
    assert first[0].endswith("item 1") and first[4].endswith("item 5")
    assert first[5] == "… and 3 more — next prompt, or grove_inbox(since_id=5)"
    assert (
        grove_hook._read_anchor(grove_hook._grove_anchor_path("session", "sid_test"))
        == 5
    )

    second = [
        ln
        for ln in _reinject_lines(monkeypatch, capsys)
        if ln.startswith("[grove") or ln.startswith("…")
    ]
    assert [ln[-6:] for ln in second] == ["item 6", "item 7", "item 8"]
    assert (
        grove_hook._read_anchor(grove_hook._grove_anchor_path("session", "sid_test"))
        == 8
    )

    third = [
        ln for ln in _reinject_lines(monkeypatch, capsys) if ln.startswith("[grove")
    ]
    assert third == []


def test_inbox_malformed_message_is_counted_not_crashed(monkeypatch, capsys):
    _quiet_nestor(monkeypatch)
    _seed_anchor("sid_test", 0)
    rows = _inbox_rows((1, "willow", "bot", "fine")) + [
        {"id": 2, "channel": "willow"},
        "not a dict",
    ]
    _stub_inbox(monkeypatch, rows, max_id=2)
    lines = _reinject_lines(monkeypatch, capsys)
    inbox = [ln for ln in lines if ln.startswith("[grove")]
    assert inbox == [
        "[grove #willow bot] fine",
        "[grove: 2 unreadable message(s) skipped]",
    ]
    # An unreadable row is consumed (never re-shown), so the anchor covers it.
    assert (
        grove_hook._read_anchor(grove_hook._grove_anchor_path("session", "sid_test"))
        == 2
    )


def test_inbox_first_run_seeds_the_anchor_at_now_and_says_nothing(monkeypatch, capsys):
    """No anchor for the session or the seat: the seat starts from the
    current high-water mark rather than replaying history."""
    _quiet_nestor(monkeypatch)
    _stub_inbox(
        monkeypatch, _inbox_rows((300, "willow", "bot", "old news")), max_id=300
    )
    lines = _reinject_lines(monkeypatch, capsys)
    assert not [ln for ln in lines if ln.startswith("[grove")]
    assert (
        grove_hook._read_anchor(grove_hook._grove_anchor_path("session", "sid_test"))
        == 300
    )
    assert (
        grove_hook._read_anchor(grove_hook._grove_anchor_path("seat", "willow")) == 300
    )


def test_inbox_new_session_inherits_the_seat_anchor(monkeypatch, capsys):
    """A red that landed between two sessions surfaces once, in the next
    session: the new session's anchor is seeded from the seat's."""
    _quiet_nestor(monkeypatch)
    grove_hook._write_anchor(grove_hook._grove_anchor_path("seat", "willow"), 10)
    _stub_inbox(
        monkeypatch, _inbox_rows((11, "willow", "willows-bot", "CI red: overnight"))
    )
    lines = _reinject_lines(monkeypatch, capsys, session_id="sid_next")
    inbox = [ln for ln in lines if ln.startswith("[grove")]
    assert inbox == ["[grove #willow willows-bot] CI red: overnight"]
    assert (
        grove_hook._read_anchor(grove_hook._grove_anchor_path("session", "sid_next"))
        == 11
    )


def test_inbox_unreadable_seat_anchor_is_said_not_seeded_over(monkeypatch, capsys):
    """Loki 7AA9F436: a corrupt seat anchor with no session anchor used to
    read as absent, get seeded at the high-water mark, and drop the backlog.
    Now: one line naming the file, nothing read, nothing written."""
    _quiet_nestor(monkeypatch)
    seat = grove_hook._grove_anchor_path("seat", "willow")
    seat.parent.mkdir(parents=True, exist_ok=True)
    seat.write_text("{not json", encoding="utf-8")
    calls = _stub_inbox(monkeypatch, _inbox_rows((5, "willow", "bot", "backlog")))
    lines = _reinject_lines(monkeypatch, capsys)
    inbox = [ln for ln in lines if ln.startswith("[grove")]
    assert inbox == [f"[grove anchor unreadable: {seat}]"]
    assert calls == [], "nothing is read while the anchor is unreadable"
    assert seat.read_text(encoding="utf-8") == "{not json", "never rewritten"
    assert not grove_hook._grove_anchor_path("session", "sid_test").exists()


def test_inbox_unreadable_session_anchor_falls_back_to_the_seat_anchor(
    monkeypatch, capsys
):
    _quiet_nestor(monkeypatch)
    sess = grove_hook._grove_anchor_path("session", "sid_test")
    sess.parent.mkdir(parents=True, exist_ok=True)
    sess.write_text('{"last_id": -3}', encoding="utf-8")  # malformed value
    grove_hook._write_anchor(grove_hook._grove_anchor_path("seat", "willow"), 10)
    _stub_inbox(monkeypatch, _inbox_rows((11, "willow", "bot", "after ten")))
    lines = _reinject_lines(monkeypatch, capsys)
    assert [ln for ln in lines if ln.startswith("[grove")] == [
        "[grove #willow bot] after ten"
    ]
    assert grove_hook._read_anchor(sess) == 11


def test_read_anchor_three_states(tmp_path):
    p = tmp_path / "a.json"
    assert grove_hook._read_anchor(p) is None
    p.write_text("garbage", encoding="utf-8")
    assert grove_hook._read_anchor(p) == grove_hook._ANCHOR_UNREADABLE
    p.write_text('{"last_id": true}', encoding="utf-8")
    assert grove_hook._read_anchor(p) == grove_hook._ANCHOR_UNREADABLE
    grove_hook._write_anchor(p, 7)
    assert grove_hook._read_anchor(p) == 7


def test_inbox_read_helper_treats_missing_willow_mcp_as_unreachable(monkeypatch):
    """The real reader, with the import made to fail: `unreachable` with the
    reason — never an empty inbox."""
    import builtins

    real_import = builtins.__import__

    def _no_willow(name, *args, **kwargs):
        if name.startswith("willow_mcp"):
            raise ImportError("no willow_mcp here")
        return real_import(name, *args, **kwargs)

    original = _original_inbox_read()
    monkeypatch.setattr(builtins, "__import__", _no_willow)
    out = original("willow", 0)
    assert out["state"] == "unreachable"
    assert "willow_mcp import" in out["reason"]


def _original_inbox_read():
    """The un-stubbed reader: the autouse fixture replaces the module
    attribute, so load a fresh copy of the hook module and take the function
    it defines."""
    import importlib.util

    spec = importlib.util.spec_from_file_location(
        "grove_hook_fresh", HOOKS / "grove_hook.py"
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module._grove_inbox_read


# ── events boot line (sealed 13330d1c; probe reworked per Loki 1BA3415E Q2) ─
#
# `orient` (session_start) gains one line naming the seat's own event
# stream — the hook cannot arm a Monitor itself, it only says the line.
# Every test below patches `_events_health_probe` explicitly (Loki FA0EFB5F
# low, extended by 1BA3415E Q2) rather than relying on Kart's own box
# having nothing on 127.0.0.1:8766 — a probe result is a fact this suite
# asserts, not an environment accident it happens to benefit from.


def test_orient_prints_events_boot_line_with_seat_id(capsys, monkeypatch):
    monkeypatch.delenv("GROVE_SERVE_PORT", raising=False)
    monkeypatch.setattr(
        grove_hook, "_events_health_probe", lambda: {"state": "populated"}
    )
    rc = grove_hook.orient()
    assert rc == 0
    err = capsys.readouterr().err
    assert "arm a Monitor on ws://127.0.0.1:8766/events/willow?since_id=" in err
    assert "30-minute timeout, re-arm on expiry" in err


def test_orient_prints_page_down_line_when_events_port_unreachable(capsys, monkeypatch):
    monkeypatch.setattr(grove_hook, "_events_health_probe", lambda: None)
    rc = grove_hook.orient()
    assert rc == 0
    err = capsys.readouterr().err
    assert "served page down; reinject inbox is the path" in err
    assert "arm a Monitor" not in err


def test_orient_prints_stream_dark_line_when_events_not_populated(capsys, monkeypatch):
    """Loki 1BA3415E F1/Q2: the page can be up with the stream dark (a WS
    library that failed to install offline) — the boot line must say so,
    not promise a Monitor against a route that will 404 every upgrade."""
    monkeypatch.setattr(
        grove_hook,
        "_events_health_probe",
        lambda: {"state": "unreachable", "reason": "no websocket library"},
    )
    rc = grove_hook.orient()
    assert rc == 0
    err = capsys.readouterr().err
    assert "stream dark: no websocket library; reinject inbox is the path" in err
    assert "arm a Monitor" not in err


def test_events_boot_line_honors_grove_serve_port_override(monkeypatch):
    monkeypatch.setenv("GROVE_SERVE_PORT", "9999")
    import importlib

    reloaded = importlib.reload(grove_hook)
    monkeypatch.setattr(
        reloaded, "_events_health_probe", lambda: {"state": "populated"}
    )
    try:
        line = reloaded._events_boot_line("willow")
        assert line is not None
        assert "ws://127.0.0.1:9999/events/willow" in line
    finally:
        monkeypatch.delenv("GROVE_SERVE_PORT", raising=False)
        importlib.reload(grove_hook)


def test_events_boot_line_none_without_app_id(monkeypatch):
    monkeypatch.setattr(
        grove_hook, "_events_health_probe", lambda: {"state": "populated"}
    )
    assert grove_hook._events_boot_line("") is None


def test_events_boot_line_since_id_resumes_from_seat_anchor(tmp_path, monkeypatch):
    monkeypatch.setenv("WILLOW_HOME", str(tmp_path / "willow_home"))
    monkeypatch.setattr(grove_hook, "APP_ID", "hanuman")
    monkeypatch.setattr(
        grove_hook, "_events_health_probe", lambda: {"state": "populated"}
    )
    grove_hook._write_anchor(grove_hook._grove_anchor_path("seat", "hanuman"), 42)
    line = grove_hook._events_boot_line("hanuman")
    assert line is not None
    assert "since_id=42" in line


def test_events_boot_line_defaults_since_id_zero_with_no_anchor(tmp_path, monkeypatch):
    monkeypatch.setenv("WILLOW_HOME", str(tmp_path / "willow_home_fresh"))
    monkeypatch.setattr(
        grove_hook, "_events_health_probe", lambda: {"state": "populated"}
    )
    line = grove_hook._events_boot_line("hanuman")
    assert line is not None
    assert "since_id=0" in line


def test_events_boot_line_says_page_down_when_unreachable(monkeypatch):
    monkeypatch.setattr(grove_hook, "_events_health_probe", lambda: None)
    line = grove_hook._events_boot_line("hanuman")
    assert line == "served page down; reinject inbox is the path"


def test_events_boot_line_says_stream_dark_with_reason(monkeypatch):
    monkeypatch.setattr(
        grove_hook,
        "_events_health_probe",
        lambda: {"state": "unreachable", "reason": "no websocket library"},
    )
    line = grove_hook._events_boot_line("hanuman")
    assert line == "stream dark: no websocket library; reinject inbox is the path"


def test_events_boot_line_says_stream_dark_unknown_when_reason_missing(monkeypatch):
    monkeypatch.setattr(
        grove_hook, "_events_health_probe", lambda: {"state": "unreachable"}
    )
    line = grove_hook._events_boot_line("hanuman")
    assert line == "stream dark: unknown; reinject inbox is the path"


def _serve_health_once(events_body: dict):
    """A minimal real HTTP server answering exactly one GET /health with
    {"ok": true, "commit": "test", "events": events_body}, on a free
    loopback port. Returns (server, thread, port); caller shuts it down."""
    import http.server
    import threading as _threading

    payload = json.dumps({"ok": True, "commit": "test", "events": events_body}).encode(
        "utf-8"
    )

    class _Handler(http.server.BaseHTTPRequestHandler):
        def do_GET(self):  # noqa: N802 — stdlib method name
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(payload)

        def log_message(self, *_a):  # silence stderr access logs
            pass

    server = http.server.HTTPServer(("127.0.0.1", 0), _Handler)
    thread = _threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server, thread, server.server_address[1]


def test_events_health_probe_reads_events_field_from_a_real_server(monkeypatch):
    """The probe is a real HTTP GET, not a stub — proven against an actual
    loopback HTTP server answering /health."""
    server, thread, port = _serve_health_once({"state": "populated"})
    monkeypatch.setattr(grove_hook, "_EVENTS_PORT", str(port))
    try:
        assert grove_hook._events_health_probe() == {"state": "populated"}
    finally:
        server.shutdown()
        thread.join(timeout=2.0)
        server.server_close()


def test_events_health_probe_none_when_nothing_listens(monkeypatch):
    import socket as _socket

    probe = _socket.socket(_socket.AF_INET, _socket.SOCK_STREAM)
    probe.bind(("127.0.0.1", 0))
    free_port = probe.getsockname()[1]
    probe.close()
    monkeypatch.setattr(grove_hook, "_EVENTS_PORT", str(free_port))
    assert grove_hook._events_health_probe() is None
