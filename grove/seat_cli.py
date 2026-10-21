# b17: GRSET ΔΣ=42
"""grove seat — the one script at a terminal: the desk's command-line seat.

    scripts/grove-seat            # check-in, scope, served, chain, proposals
    scripts/grove-seat --check    # probe only: nothing checked in, nothing written
    scripts/grove-seat --no-say   # code only, no model asked
    scripts/grove-seat --model qwen3:8b   # this run's reply model

The third front end beside the web components and the phone APK. All three
call willow-bot's ``one-script/onescript/api.py``, so a seat run leaves the
same record rows the app does. This module only reads keys, prints, and
calls those functions; it holds no seal key, names no model provider, and
writes nothing but a scratch file per cloud turn.

``--no-say`` runs code only (no model is asked); ``--model NAME`` picks the reply
model for the run, winning over ``GROVE_SAY_MODEL``, and the two together exit 2.
``--help`` and ``--version`` print and exit 0; an unknown flag or argument exits
2 before the bot is loaded. None of them, and not ``--check`` (which reports the
bot root, the python in use, whether ``ratatosk`` resolves and whether the
Ollama loopback answers, each ``populated`` or ``unreachable`` or ``empty``),
calls ``api.checkin``: only a session does, and that writes record rows.

The stages, in order, each shown in the prompt (``scope ▶``):

    checkin    api.checkin: the record, the probes, the four gates; a line of a
               failed, not-installed or hard-closed check-in is a ``blocked``
               card, never a ``routine pass`` (``checkin_kind``)
    resume     api.resume: the newest human-sealed scope, spec pinned at its
               ``upto``. Found, the seat serves that snapshot and skips the
               group-by prompt, so the subject holds still while the desk adds
               rows. None, a fresh scope as below. Raises or missing (an older
               willow-bot): an ``unreachable`` card, then the fresh scope
    scope      api.scope proposes a stack and names its subject, after one
               prompt, ``group by (enter = who)``. Enter takes the default; an
               answer the api refuses as a usage error is said in a plain code
               line ("Group by takes who, what, when or where; you said ...")
               and asked again, never an ``unreachable`` card. Any other
               refusal is the ``refused`` card as before
    pooled     api.pooled, read once for display: ONE ``still pooled`` card for
               the proposals earlier runs left unsealed (count, a couple of
               subjects). Populated, empty, or ``unreachable`` (a raise or a
               missing ``pooled`` on an older willow-bot); it seals and
               deposits nothing, and the resume snapshot is unchanged by it
    opening    ONE code sentence that picks up from last time, said from what
               resume and pooled already returned (no call of its own, no model,
               no row): "Picking up from the sealed snapshot serve:... (rows up
               to N); 2 proposals still pooled from earlier runs." Each of
               nothing sealed, an unreadable resume, a pool that is empty, and a
               pool that cannot be read has its own clause, so an unreadable
               read is never said as "nothing to pick up". It carries the run's
               one ``Morning.`` (before noon), so the first reply does not say
               it again. When ``api.resume`` returns ``sealed_at`` (the seal
               row's own stamp, UTC with an explicit ``Z``, as willow-bot's
               record writes it) the sentence says when the human sealed:
               "the snapshot you sealed on 12 October (serve:..., rows up to
               N)", or "earlier today" when the stamp's UTC date is today's
               (``seat_boxes.sealed_on``). The date is the record's, read as
               written, never converted to a local zone and never from the
               clock (the clock only picks "earlier today" over the date). An
               older willow-bot with no ``sealed_at``, or a stamp that doesn't
               read, keeps the plain "the sealed snapshot serve:..." wording
    served     api.serve is the silent start-check: it serves only a scope a
               past human seal already covers (three states, never collapsed),
               after one prompt, ``cap in characters (enter = 48000)``; an
               answer that is not a whole number of 1 or more is said in a
               plain code line and asked again (no card, no state)
    chain      api.escalate: D0 code, then the hash record, then a local rung
               on the seat's one model (the reply model: ``--model`` or
               ``GROVE_SAY_MODEL``, default ``qwen3:4b``)
    flowering  for a piece the chain left, one cloud turn on the human's yes:
               ``ratatosk --onescript --class flowering`` (the ladder picks
               the provider), its rows judged by api.take_proposals
    proposals  each pass shown and left pooled; nothing is sealed here
    checkout   api.checkout, on exit, EOF or Ctrl-C alike; then the pool is
               deposited into Nestor as drafts (willow-mcp's
               ``onescript_deposit``, injectable) and ONE ``seal ↗`` offer
               points at the Nestor UI, the only place a seal is made. Last,
               ONE code sentence says what stays pooled for next time ("2
               proposals stay pooled for next time."), from the pool that
               close-out already read: ``populated``, ``empty`` ("Nothing stays
               pooled") or ``unreachable`` ("I couldn't read the pool") each
               said differently. It seals, deposits and writes nothing more

The seat never seals: no prompt asks for one, it holds no key, and the deposit
only proposes. When it served a pinned snapshot and the record has grown, the
one ``seal ↗`` offer also names the grown scope's subject, so the human can
advance the snapshot in Nestor.

What the seat prints is the box stream (``grove/seat_boxes.py``, after
``web/demo/box-stream/box-stream-v1.3.html``): everything the agent says is a
box card or a reply made of cards, a line that is not one is the human's. A
reply's one sentence is said by a local model (``qwen3:4b`` on the Ollama
loopback, the injected ``say``; ``grove/seat_say.py``) and then checked by code
against the boxes: every cite served, every box cited, nothing the boxes lack,
the human's words quoted exactly. A sentence that fails a check is shown
struck and replaced by the sentence code composes from box facts plus fixed
glue, which is also what stands when the model can't be reached (an
``unreachable`` card, never a crash; when it timed out right after the chain's local rung asked the same Ollama for a model, the card adds that as a maybe, ``queued_behind``). The model also sees the thread: the last two replies of this run (their boxes
with tags, and the human's lines as context only), so a sentence can say "that"
or "still"; a cite to one of those earlier boxes was served, a cite to any
other box (never shown, out of that window, or from a previous run) is not, and
``every box cited`` stays about the current page. With no ``say`` the seat is
code only, and the thread changes nothing there.
A chain piece's box says ``<rung>: <detail>``: an escalated piece's detail is
willow-bot's own (a rung that exited non-zero carries the end of its stderr, or of
its stdout summary line, so "ratatosk exited 1" arrives with its cause); an answered piece carries none, so
its box says its first row's claim (``CLAIM_CHARS``), and a local answer with no
claim and no data is said plainly, "The local model gave an empty answer", never
"Local:." (willow-bot now escalates such rows as ``silent`` with that detail).
A chain turn ranks its boxes (a heads-up first, then needs you, blocked,
decided, changed, routine pass) and shows two at a time (``more?``) from that
order. The code sentence is a short sentence per box; the run's one
``Morning.`` (before noon, by the turn's clock time) goes on the opening sentence,
or on the first reply when there was no opening; a stage whose
card is ``empty`` or ``unreachable`` also says so in a plain code line, except
where the opening or the closing sentence already says that same state (the
resume and still-pooled cards at start, the pool and an empty deposit at
check-out): the card stays, the plain line is held back, so the fact is not said
twice and an unreachable read is still said in words exactly once. Small
talk is answered by code (greetings, ``ok``, ``thanks``, ``later``, and ``help``,
a fixed line of what the seat understands; ``bye``, ``done`` and ``quit`` check
out like an empty line), and a task asked again is shown again from the pile,
stamped with when it was first said.

A reply ends with a row of chips built from the boxes it showed
(``seat_boxes.chips``): ``show me <ref>`` for a box worth opening, the options a
needs-you box carries, and always ``later`` and ``thanks``. The seat keeps the
last reply (``Thread``) and answers a typed line against it in code, before the
chain: a chip choice is acknowledged (``Got it: <choice>.``, nothing recorded
or sealed, the row spent); ``show me 712`` / ``open 712`` / a box id / ``the
second one`` / ``that`` show that box again with its full detail and a code
sentence; ``why`` / ``what's that`` / ``tell me more`` say the reason
(``seat_boxes.why_sentence``: the human's own words quoted exactly and led by who
said them, provenance such as an origin left to the card but a fixture still
marked ``(fixture)``; a box with nothing but provenance says there is no more);
``go on`` / ``more`` / ``next`` show the next page (by code, no model) or say
nothing is left. An ordinal past what was shown, or a ref that fits two boxes,
is a plain line, never a guess, and so is ``show me X`` / ``open X`` / ``show X``
that no shown box answers to when X reads as a reference (a number, an id-like
token such as ``PR 712``, ``#714`` or ``ABC-123``, a box id, an ordinal, or a
phrase of at most two words): "Nothing I showed answers to "14"; I showed: ...".
A longer X ("show me the tests that failed") reads as a task and goes to the
chain (``seat_boxes.looks_like_ref``). None of these plain lines asks a
model, calls ``api.escalate`` or writes a row; any other line that matches
nothing (and ``show me X`` before any turn) goes to the chain as before. A sentence never ends ``.".`` (``terminate``). A ``show me`` ref is a number of two digits or more, an id-like
token (``PR 712``) or a short box id (``b4``), never the first words of a value;
with none, no ``show me`` chip. ``No rush.`` is said at most once per turn, and
the chain's ``answered N, escalated M`` is said as a sentence of its own ("The
chain answered 1 and escalated 0."), never after a ``Heads up:`` and never
grouped into a pair or a run with a piece: its box carries ``role="count"``, as
the Nestor store's count does. Under ``NO_COLOR`` or a non-tty the cards are plain ASCII with
no escape codes.

A status question is not a chain task. "What is on the table (today)", "what is
my next task", "what's next", "what do I need to do", "what needs me", "where are
we" and the rest of ``seat_record.STATUS_PHRASES`` / ``WHERE_PHRASES`` (matched
whole, after normalisation: no substring, no fuzzy match, no model) are answered
from what the seat already has, read-only, by ``Seat.status``: the record's
``NEEDS YOU`` lines (``api.needs`` in willow-bot, the morning screen's section
read without checking out; one ``invocation`` row per ask, the same row every
api read writes, and no ``reconcile`` row) and, when ``api.default_nestor_db()``
(``$WILLOW_NESTOR_DB`` / ``$NESTOR_DB``) names one, the Nestor store
(``grove/seat_nestor.py``). The two are merged into one box list and said through
the same ranked converse, so ``show me``, ``why``, ``the second one`` and ``go
on`` work on them. Each source keeps its own state, ``populated``, ``empty`` or
``unreachable``, never collapsed: an unreadable ``api.needs`` (raised, refused,
or missing on an older willow-bot) is one ``unreachable`` box, a record with
nothing waiting one ``empty`` box. A Nestor store that is not configured is not
an ``unreachable`` read when the record answered: it adds no box, and the record
card says only the record was read; a configured store that cannot be read is
``unreachable`` as before. "Where are we" shows the store's whole state (count,
waiting drafts, refusals, decided) beside the record's lines; the other status
questions show only what waits on the human (the record's lines and the store's
waiting drafts, marked drafts). A ``fixture:`` origin stays on the card. No chain
runs, and nothing but the one ``invocation`` row is written.

The operator, 2026-10-09: "The deterministic chain runs, esclates to local
models if need be, then to the cloud models"; "It should live in the grove,
along side the web and apk"; "not anthropic. there is already routing in the
crown. Agent agnostic". Two chain rules hold here too: a piece code cut as
over its cap never reaches a model, and an empty or unreachable scope is
escalated by code, never handed to one.

The gate's toolchain check looks in the venv the seat runs in
(``resolve_venv``): the running interpreter's venv when it is one, else the
launcher's order (``GROVE_VENV``, the D2 bot venv, the legacy one, ``./.venv``).

willow-bot is found at ``WILLOW_BOT_ROOT``, else beside this repo
(``../willow-bot``), the way the one script finds this repo.

The table (box-build R13, no new panel): ``GROVE_SEAT_BOX`` points the seat at a
table's box, ``GROVE_SEAT_HUMAN_KEY`` and ``GROVE_SEAT_LEDGER`` give it the
human's key file and the ai-game-master ledger. "What's on the table" then shows
the wagers (reconciled, escalated, unreachable), the verdict sessions, the
agm_head state and the decision beats awaiting a seal, as boxes, through
``api.needs``; the close-out screen has the same in its TABLE section, through
``api.checkout``. "What happened at the table" says the served table's fact
boxes through ``table_boxes.narrate`` (the injected ``say``, or code). A line is
scrubbed of the key, seeds and key-sized hex before it is a box
(``seat_record.scrub``). ``GROVE_SEAT_GRAPH`` names a cbm project: a qualified
``file.py:name`` cite in a model sentence is read against its code graph as part
of ``every cite was served`` (T-cbm-1; a fifth check is the human's call).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
import tomllib
from collections.abc import Callable, Sequence
from dataclasses import dataclass, field, replace
from datetime import date, datetime, timezone
from importlib import metadata
from pathlib import Path
from typing import Any

try:
    from grove.seat_boxes import (
        Box,
        cap,
        carry_over,
        compose,
        human_line,
        checks_line,
        chips,
        clause,
        COUNTED,
        legend,
        looks_like_ref,
        matches,
        opening,
        parse_follow,
        pile_header,
        plural,
        plain_line,
        rank,
        ref_tokens,
        terminate,
        render_box,
        say_line,
        struck_line,
        use_color,
        who_line,
        why_sentence,
        _val,
    )
except ImportError as _no_states:
    # The three states are the one script's (flatten F5, F-18): with no one
    # script beside, the seat says so and exits 2, as load_bot does.
    if __name__ == "__main__":
        print(f"grove seat: {_no_states}", file=sys.stderr)
        raise SystemExit(2) from None
    raise
from grove.seat_nestor import lead_rank, read_store
from grove import onescript_reach
from grove import table_boxes as tb
from grove.seat_nestor import Reading
from grove.seat_record import read_needs, scrub, status_kind, story_kind
from grove.seat_say import (
    CHECK_NAMES,
    MODEL,
    SayUnreachable,
    THREAD_TURNS,
    build_prompt,
    ollama_probe,
    ollama_say,
    passed,
    run_checks,
    symbol_notes,
    symbol_rows,
)

ORD = ("first", "second", "third", "fourth")
GROVE_ROOT = Path(__file__).resolve().parent.parent
ESCALATE_PATH = "ESCALATE"
#: Reasons a flowering turn may not take: code decided these, no model.
NO_FLOWER = frozenset({"cap", "empty_scope"})
DEFAULT_MAX_CHARS = 48_000
#: The group-by prompt's default.
DEFAULT_BY = "who"
#: The one script's refusal of a group-by it doesn't take (``serve.py``): the
#: names it takes are read from it, so the seat holds no second list.
GROUP_BY_REFUSAL = re.compile(r"group by one or more of \((?P<names>[^)]*)\)")
FLOWER_TIMEOUT = 300.0
NESTOR_UI = "http://127.0.0.1:8765"
NO_DEPOSIT = "deposit unavailable here: willow-mcp not on the path"
#: The most of an answered piece's claim its box says.
CLAIM_CHARS = 160
#: A local or hash answer with no claim and no data, said plainly (willow-bot
#: now escalates such rows as ``silent`` with this very detail).
EMPTY_ANSWER = "the local model gave an empty answer"
#: Boxes a reply shows before ``more?``.
PAGE = 2
#: Boxes a store turn (``where are we``) shows per page, and with the count on
#: its first page: the count plus ``STORE_PAGE`` open items, then ``STORE_PAGE``
#: at a time. The chain's ``PAGE`` is unchanged.
STORE_PAGE = 4
#: How many refs an unmatched ``show me X`` line lists before "and N more".
UNMATCHED_LIST = 4
#: The typed ``show me X`` / ``show X`` / ``open X`` with the human's own case.
SHOW_RAW = re.compile(r"(?i)(?:show me|show|open)\s+(.+?)[\s?!.]*")
#: What code answers to small talk: no boxes, nothing served, no model. The
#: words are the sketch's glue ("Anytime.", "Got it.") or fixed code lines.
HELLO = "Hello. Give me a task, or say help."
HELP = (
    'Give me a task and the chain takes it. "what is on the table", "what needs '
    'me", "what\'s next" and "where are we" are read from the record\'s needs-you '
    "list and, when one is configured, your Nestor store (both read-only). "
    'After a reply you can say "show me 712", "why", '
    '"the second one" or "go on"; a longer "show me ..." is a task for the chain. '
    '"thanks" and "later" are only '
    'acknowledged; an empty line, "bye", "done" or "quit" checks out.'
)
SMALL_TALK = {
    "thanks": "Anytime.",
    "thank you": "Anytime.",
    "later": "Got it. It stays in the pile.",
    **dict.fromkeys(("hi", "hello", "hey", "morning", "good morning"), HELLO),
    **dict.fromkeys(("ok", "okay", "cool", "got it", "sure"), "Got it."),
    **dict.fromkeys(("help", "what can you do"), HELP),
}
#: The small talk that answers a ``more?`` it declines (the rest says ``STAY``).
THANKS_LATER = ("thanks", "thank you", "later")
#: Said like an empty line: check out.
FAREWELLS = frozenset({"bye", "done", "quit"})
MORE_YES = frozenset({"", "m", "more", "y", "yes"})
STAY = "Got it. It stays in the pile."
NOTHING_MORE = "Nothing more in the pile."
NO_DETAIL = "Nothing more is on the record for it."


class SeatUnavailable(Exception):
    """willow-bot's one script can't be imported here."""


@dataclass
class Bot:
    """What the seat uses from willow-bot: the api, and two pure helpers of
    the chain's, so a flowering turn sees exactly the piece the chain cut."""

    api: Any
    cut: Callable[[dict, str, int], list[dict]]
    subject: Callable[[dict], str]
    piece_chars: int
    #: The one script's layer-5 narration gate (``gate.check_claims``), the
    #: function ``Run.say`` wraps; the quote check calls it when it is here.
    claims: Callable[[str, dict], list[dict]] | None = None
    #: T-cbm-1: the code-graph reader (``graph.symbols_for`` bound to a cbm
    #: project, ``GROVE_SEAT_GRAPH``), so a qualified ``file.py:name`` cite in a
    #: model sentence is read against the graph. None: no symbol claims are made.
    symbols: Callable[[str], dict] | None = None


def bot_root() -> Path:
    got = os.environ.get("WILLOW_BOT_ROOT")
    return Path(got).expanduser() if got else GROVE_ROOT.parent / "willow-bot"


def load_bot(root: Path) -> Bot:
    """The one script's modules the seat drives, found by the one reach
    (flatten-2 F6.5: ``onescript_reach.py``, whose "why" is the reach's). With
    none at ``root``, ``SeatUnavailable`` says so."""
    one = root / "one-script"
    try:
        api, escalate, gate, proposals = (
            onescript_reach.module(m, home=one)
            for m in ("api", "escalate", "gate", "proposals")
        )
    except onescript_reach.Unreachable as e:
        raise SeatUnavailable(f"unreachable: {e}") from e
    return Bot(
        api,
        escalate.cut,
        proposals.subject,
        escalate.PIECE_CHARS,
        gate.check_claims,
        graph_reader(),
    )


def graph_reader(environ: dict | None = None) -> Callable[[str], dict] | None:
    """T-cbm-1: ``GROVE_SEAT_GRAPH`` names the cbm project a model sentence's
    ``file.py:name`` cites are read against (``onescript.graph.symbols_for``).
    Unset, or a one script without the graph seam: None, and no symbol claim is
    made. The graph says ``stale`` or ``unreachable`` itself; nothing here
    re-indexes."""
    env = os.environ if environ is None else environ
    project = env.get("GROVE_SEAT_GRAPH", "").strip()
    if not project:
        return None
    try:
        from onescript import graph
    except ImportError:
        return None
    return lambda sentence: graph.symbols_for(sentence, project)


def _bot_box(env) -> Path | None:
    """The bot's box by the bot's own rule (flatten F-17: willow-bot's
    ``willow_bot.paths.env_box``, read with ``env``): ``$WILLOW_HOME``, else
    ``$WILLOW_VAULT_BOX``, an existing absolute directory; else None, never a
    guessed home. No willow-bot to read the rule from: None too. Where
    willow-bot is comes from ``env``, else this process (the seat's own
    ``WILLOW_BOT_ROOT``, as ``seat_boxes`` reads it), else beside Grove: it
    is where the rule's code lives, not part of the box ``env`` describes."""
    got = env.get("WILLOW_BOT_ROOT") or os.environ.get("WILLOW_BOT_ROOT")
    root = Path(got).expanduser() if got else GROVE_ROOT.parent / "willow-bot"
    if not (root / "willow_bot" / "paths.py").is_file():
        return None
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))
    from willow_bot import paths  # noqa: PLC0415  (the bot's rule, one copy)

    try:
        return paths.env_box(environ=env)
    except paths.BoxNotConfigured:
        return None


def resolve_venv(
    environ: dict | None = None,
    prefix: str | None = None,
    base_prefix: str | None = None,
    grove: Path = GROVE_ROOT,
) -> Path | None:
    """The venv the gate's toolchain check (``Config.venv``) looks in: the one
    the seat runs in. When the running interpreter is a venv, that venv (the
    launcher ``scripts/grove-seat`` already chose it by seal D2, so the gate
    and the seat can't disagree); otherwise the launcher's own order:
    ``GROVE_VENV``, ``<box>/willow-bot/venvs/willow-bot`` (D2), the legacy
    ``<box>/venvs/willow-bot``, ``<grove>/.venv``, each only if it has a
    ``bin/python3``, the box being the bot's (``_bot_box``, F-17). With none,
    the D2 path in the box, so a missing toolchain is reported against the
    place it belongs; with no box either, None, and the gate says why."""
    env = os.environ if environ is None else environ
    prefix = sys.prefix if prefix is None else prefix
    base_prefix = sys.base_prefix if base_prefix is None else base_prefix
    if prefix != base_prefix:
        return Path(prefix)
    box = _bot_box(env)
    new = box / "willow-bot" / "venvs" / "willow-bot" if box is not None else None
    cands = []
    if env.get("GROVE_VENV"):
        cands.append(Path(env["GROVE_VENV"]).expanduser())
    if box is not None:
        cands += [new, box / "venvs" / "willow-bot"]
    cands.append(grove / ".venv")
    found = next((c for c in cands if (c / "bin" / "python3").is_file()), None)
    if found:
        return found
    return new


def config(bot: Bot, root: Path, grove: Path = GROVE_ROOT, environ: dict | None = None):
    """The Config the one script's own CLI builds, with the same defaults.

    SPEC R13: ``GROVE_SEAT_BOX`` points the seat at another box, a table's, and
    ``GROVE_SEAT_KEYS`` at that box's keys file; unset, the seat's own box and
    keys as always. Nothing else about the seat changes: it reads the table
    through ``api.needs`` and ``api.checkout``, never the record file."""
    env = os.environ if environ is None else environ
    box = env.get("GROVE_SEAT_BOX", "").strip()
    keys = env.get("GROVE_SEAT_KEYS", "").strip()
    return _make_config(bot, root, grove, box, keys, env)


def table_config(
    bot: Bot, root: Path, grove: Path = GROVE_ROOT, environ: dict | None = None
):
    """Q1: the Config of a SECOND box the seat only watches
    (``GROVE_SEAT_TABLE_BOX``; keys ``GROVE_SEAT_TABLE_KEYS``, else the box's OWN,
    ``<box parent>/keys/keys.json``, never the seat's: the sealed tip's anchor
    sits beside the keys file, and another box's keys call an honest chain
    rewritten), or None when none is named. Keys that are not there make the
    table ``unreachable`` in ``Seat.status``, never a fallback. It is read with ``api.peek``, which writes
    nothing to it, so the human's sealed tip is never moved by the seat looking."""
    env = os.environ if environ is None else environ
    box = env.get("GROVE_SEAT_TABLE_BOX", "").strip()
    if not box:
        return None
    keys = env.get("GROVE_SEAT_TABLE_KEYS", "").strip()
    if not keys:
        # the table box's OWN keys, beside it (the sealed tip's anchor lives there);
        # never the seat's, which would call an honest chain rewritten
        keys = str(Path(box).expanduser().parent / "keys" / "keys.json")
    return _make_config(bot, root, grove, box, keys, env)


def _make_config(bot, root, grove, box, keys, env):
    extra = {}
    if env.get("GROVE_SEAT_DRAND", "").strip():  # R23: off unless asked, like --drand
        try:
            from onescript import beacon

            extra["beacon"] = beacon.drand_reader
        except ImportError:
            pass
    return bot.api.Config(
        **extra,
        box=Path(box).expanduser() if box else root / ".flow" / "onescript",
        keys=Path(keys).expanduser()
        if keys
        else root / ".flow" / "onescript-keys" / "keys.json",
        constitution=grove / "governance" / "CONSTITUTION.md",
        ci=grove / ".github" / "workflows" / "tests.yml",
        root=root,
        grove=grove,
        venv=resolve_venv(grove=grove),
        keyring=bot.api.default_keyring(),
        nestor_db=bot.api.default_nestor_db(),
    )


def table_root(environ: dict | None = None) -> Path:
    """The-table's app directory (``THE_TABLE_ROOT``), where ``the_table.agm_head``
    is: the ledger reader for the table's agm_head check."""
    env = os.environ if environ is None else environ
    got = env.get("THE_TABLE_ROOT", "").strip()
    return (
        Path(got).expanduser()
        if got
        else GROVE_ROOT.parent / "safe-app-store" / "apps" / "the-table"
    )


def ledger_reader(db: str, root: Path | None = None) -> Callable[[], dict]:
    """``read_head`` for ``api.needs`` and ``api.checkout``: recompute the
    ai-game-master ledger head at ``db`` (``GROVE_SEAT_LEDGER``) with the-table's
    own ``agm_head.reader``. Imported on first use, so a missing the-table is
    the agm_head check's ``unreachable`` (it raises, and the check says why),
    never a crash and never a pass."""

    def read() -> dict:
        base = root or table_root()
        if str(base) not in sys.path:
            sys.path.append(str(base))
        try:
            from the_table import agm_head
        except ImportError as e:
            raise OSError(f"the-table is not importable from {base}: {e}") from e
        return agm_head.reader(db)()

    return read


def read_key_secrets(path: Path | None) -> tuple[str, ...]:
    """The human key's text and hex, for ``seat_record.scrub``: what no line may
    show. An unreadable file yields none (the read itself will say it)."""
    if path is None:
        return ()
    try:
        text = Path(path).read_text().strip()
        raw = bytes.fromhex(text)
    except (OSError, ValueError):
        return ()
    return tuple(x for x in {text, raw.hex(), raw.decode("latin-1")} if len(x) >= 8)


# --- the flowering rung --------------------------------------------------------


def resolve_ratatosk() -> str:
    """The ``ratatosk`` console script beside this python (the venv's bin),
    else the bare name for PATH. A missing one is a clean ``rung_error`` /
    ``can't run`` row downstream, never a traceback."""
    beside = Path(sys.executable).parent / "ratatosk"
    return str(beside) if beside.is_file() else "ratatosk"


def ratatosk_flowering(
    cmd: Sequence[str] = ("ratatosk",), timeout: float = FLOWER_TIMEOUT
) -> Callable[[dict, str], dict]:
    """One cloud turn per piece through Rat. The seat's environment passes
    through unchanged: Rat reads the provider keys the ladder names from it."""

    def flower(piece: dict, question: str) -> dict:
        with tempfile.TemporaryDirectory(prefix="grove-seat-") as d:
            served, out = Path(d) / "piece.json", Path(d) / "rows.jsonl"
            served.write_text(json.dumps(piece, sort_keys=True), encoding="utf-8")
            argv = [*cmd, "--onescript", "--class", "flowering"]
            argv += ["--served", str(served), "--out", str(out), question]
            try:
                done = subprocess.run(
                    argv,
                    cwd=d,
                    stdin=subprocess.DEVNULL,
                    capture_output=True,
                    text=True,
                    timeout=timeout,
                    check=False,
                )
            except subprocess.TimeoutExpired:
                return {"code": 1, "summary": f"no return in {timeout:g}s", "rows": []}
            except OSError as e:
                return {"code": 2, "summary": f"can't run {cmd[0]}: {e}", "rows": []}
            lines = (done.stdout or "").strip().splitlines()
            summary = lines[-1] if lines else (done.stderr or "").strip()
            rows: list = []
            if out.is_file():
                for ln in out.read_text(
                    encoding="utf-8", errors="replace"
                ).splitlines():
                    if ln.strip():
                        try:
                            rows.append(json.loads(ln))
                        except ValueError:
                            rows.append(ln)  # take_proposals refuses it, recorded
            return {"code": done.returncode, "summary": summary, "rows": rows}

    return flower


# --- the deposit ---------------------------------------------------------------


def pool_state(pool: dict) -> dict:
    """``api.pooled``'s answer in the state shape ``onescript_deposit`` reads."""
    if "refused" in pool:
        return {"state": "unreachable", "reason": str(pool["refused"])}
    items = pool.get("pooled") or []
    if not items:
        return {"state": "empty", "reason": "the pool is empty"}
    return {"state": "populated", "stdout_json": {"pooled": items}}


def willow_mcp_deposit(app_id: str = "willow") -> Callable[[dict], dict]:
    """The default deposit: willow-mcp's ``onescript_deposit.deposit`` over the
    pool ``api.pooled`` read. It proposes drafts into Nestor and seals nothing.
    willow-mcp is imported here, on first use, so this module loads without it;
    where it isn't importable the answer is ``unreachable``, never ``empty``."""

    def deposit(pool: dict) -> dict:
        try:
            from willow_mcp.db import Store
            from willow_mcp.onescript_deposit import deposit as put
        except ImportError as e:
            return {"state": "unreachable", "reason": f"{NO_DEPOSIT} ({e})"}
        return put(app_id, store=Store(), read_pool=lambda: pool_state(pool))

    return deposit


# --- the seat ------------------------------------------------------------------


def row_count(rows: object) -> str:
    """A table's row count as the stack gave it, ``1 row`` not ``1 rows``; a
    value that is not a whole number is said as it came."""
    return plural(rows, "row") if isinstance(rows, int) else f"{rows} rows"


def three_state(state: str | None, why: str = "") -> str:
    if state == "populated":
        return "populated"
    if state == "empty":
        return f"empty — {why or 'nothing in scope'}"
    return f"unreachable — {why or 'no answer'}"


#: A gate verdict that is not a pass: the check-in line it made is a ``block``.
GATE_BAD = frozenset({"failing", "unreachable"})


def checkin_kind(line: str, rep: dict) -> str:
    """The card kind of one check-in line, from the row's own status and never
    from a default. The one script writes a line only for a problem
    (``hard_close`` is "there are lines"), as ``<gate>: <where>: <why>`` for a
    gate. So: a line made by a ``failing`` or ``unreachable`` gate (a failed
    test run, a toolchain that isn't installed) is ``block``; any other line of
    a hard-closed report (a record break, a turn never closed) is ``block``;
    a line of a report that did not hard-close, from a gate whose verdict is
    not bad, is ``pass``."""
    for g in rep.get("gates") or []:
        if (
            isinstance(g, dict)
            and line == f"{g.get('gate')}: {g.get('where')}: {g.get('why')}"
        ):
            return "block" if g.get("verdict") in GATE_BAD else "pass"
    return "block" if rep.get("hard_close") else "pass"


def _norm(text: str) -> str:
    return " ".join(text.lower().split())


def _talk(text: str) -> str:
    """A line as small talk is matched: ``_norm`` without a closing ``?!.``
    (a curly or straight apostrophe is dropped, so ``what's`` is ``whats``)."""
    return _norm(text).replace("'", "").replace("’", "").rstrip("?!. ")


@dataclass
class Said:
    """One reply as it stood: the boxes, who said the sentence, and the lines
    after the who-line. ``checks`` is empty unless a model sentence was
    checked; ``tail`` is the code sentence that replaced a struck one."""

    batch: list[Box]
    who: str
    replay_who: str
    lines: list[str]
    cards: list[Box] = field(default_factory=list)
    checks: list = field(default_factory=list)
    tail: list[str] = field(default_factory=list)
    #: The names of ``checks``, in order: the seat's four, or the table's six.
    names: tuple[str, ...] = CHECK_NAMES
    #: Code cites the graph did not verify and did not strike (``symbol_notes``):
    #: said under the checks, never left as a silent pass.
    notes: list[str] = field(default_factory=list)


@dataclass
class Turn:
    """One answered question, kept in the pile: what was said, and what is
    still waiting behind ``more?``. Asking again replays ``shown``."""

    at: str
    rest: list[Box]
    shown: list[Said] = field(default_factory=list)
    #: A store turn that opens with its heads-ups, its counts and the first open
    #: items (those leading boxes plus ``STORE_PAGE`` on page one) and says it plainly (no ``Looks like``); ``rush=False``: ``No rush.`` is not
    #: said over a store that holds a refusal.
    lead: bool = False
    rush: bool = True

    def take(self) -> list[Box]:
        """The next page off ``rest``: ``PAGE`` boxes; on a lead (store) turn
        the count plus ``STORE_PAGE`` open items first, then ``STORE_PAGE``."""
        n = PAGE
        if self.lead:
            n = STORE_PAGE
            if not self.shown:  # the heads-ups and counts that lead are not items
                n += next(
                    (
                        i
                        for i, b in enumerate(self.rest)
                        if b.state == "populated" and b.role != "count"
                    ),
                    len(self.rest),
                )
        batch, self.rest = self.rest[:n], self.rest[n:]
        return batch

    def said_rush(self) -> bool:
        """``No rush.`` was already said on a page of this turn (it is said
        once per turn), whoever's sentence has it."""
        return any(
            "no rush" in ln.lower()
            for said in self.shown
            for ln in (*said.lines, *said.tail)
        )


@dataclass
class Thread:
    """The last reply, kept so a follow-up can be resolved against it: its
    turn (every box shown so far, and what waits behind ``more?``), the chip
    choices it offered, and the box last opened (``focus``)."""

    turn: Turn
    choices: list[str] = field(default_factory=list)
    focus: Box | None = None

    def boxes(self) -> list[Box]:
        return [b for said in self.turn.shown for b in said.batch]


class Seat:
    def __init__(
        self,
        bot: Bot,
        cfg: Any,
        *,
        flower: Callable[[dict, str], dict] | None = None,
        deposit: Callable[[dict], dict] | None = None,
        say: Callable[[str], str] | None = None,
        model: str = MODEL,
        read: Callable[[str], str] = input,
        write: Callable[[str], None] = print,
        color: bool | None = None,
        clock: Callable[[], str] = lambda: time.strftime("%H:%M"),
        today: Callable[[], date] = lambda: datetime.now(timezone.utc).date(),
        human_key: Path | None = None,
        read_head: Callable[[], dict] | None = None,
        table_cfg: Any = None,
        table_own: bool = False,
    ):
        self.bot, self.api, self.cfg = bot, bot.api, cfg
        #: Q1: a second box the seat only watches (``api.peek``, nothing written),
        #: and whether the seat's own box is a table's (``GROVE_SEAT_BOX``).
        self.table_cfg, self.table_own = table_cfg, table_own
        #: R13: the human's key file (outside the box) and the table's ledger
        #: reader, handed to ``api.needs`` and ``api.checkout`` when set; the
        #: key's own text is a secret no line may show.
        self.human_key, self.read_head = human_key, read_head
        self.secrets = read_key_secrets(human_key)
        self.ratatosk = resolve_ratatosk()
        self.flower = flower or ratatosk_flowering(cmd=(self.ratatosk,))
        self.deposit = deposit or willow_mcp_deposit()
        #: The local model's sentence, ``say(prompt) -> str``. None: code only.
        self.say, self.model = say, model
        self.read, self.write = read, write
        self.color = use_color() if color is None else color
        self.clock = clock
        #: The UTC date, only to choose "earlier today" over a date when the
        #: opening names the seal; the seal's date itself is the record's.
        self.today = today
        self.doc: dict | None = None
        self.pending: list[dict] = []  # passes not yet shown; the pool keeps them
        self.turns: dict[str, Turn] = {}  # the pile of what was asked and said
        self.pile_n: int | None = 0
        self._n = 0
        self.greeted = False  # the run's one time-of-day greeting
        #: Set when the opening sentence was said. Until then an unreachable
        #: resume is held (``held``) so the opening can say it once.
        self.opened = False
        #: A resume that could not be read: its card is shown without its plain
        #: line because the opening says it; if the run ends before the opening
        #: (the scope stage failed), ``run`` says the held plain line instead.
        self.held: Box | None = None
        #: The last reply (chain turns only), for follow-ups and chip choices.
        self.thread: Thread | None = None
        #: The sealed snapshot being served ({spec, subject}), else None.
        self.sealed: dict | None = None
        #: The grown scope's subject when it differs from the sealed one.
        self.grown: str | None = None
        #: What ``api.resume`` and ``api.pooled`` said at start, for the one
        #: opening sentence (``seat_boxes.opening``); nothing is read again.
        #: What this run has said, newest last: (the human's line, the boxes).
        #: The last ``THREAD_TURNS`` go to the model as the thread; it dies with
        #: the Seat, so a box from a previous run is never in it.
        self.exchanges: list[tuple[str, list[Box]]] = []
        #: The models the chain's local rung asked of the Ollama for the chain
        #: turn being said (empty otherwise): the one hint a reply model that
        #: timed out gets (``Seat.queued_behind``).
        self.rung_models: list[str] = []
        self.start_resume: tuple = ("none",)
        self.start_pool: tuple = ("unreachable",)

    # -- the stream: cards, replies, the human's line

    def ask(self, stage: str, prompt: str = "") -> str:
        return self.read(f"{stage} ▶ {prompt}").strip()

    def nid(self) -> str:
        self._n += 1
        return f"b{self._n}"

    def put(self, text: str) -> None:
        for ln in text.split("\n"):
            self.write(ln)

    def show(self, *boxes: Box, plain: bool = True) -> None:
        """The cards. A stage's ``empty`` or ``unreachable`` card is also said
        in a plain code line (``plain``); a reply's cards are not, since the
        reply's sentence already says them."""
        for b in boxes:
            self.put(render_box(b, self.color))
            if plain and b.state != "populated":
                self.code_reply(plain_line(b))

    def card(
        self, kind: str, label: str, value: str, detail: str = "", id: str = ""
    ) -> Box:
        return Box(id or self.nid(), kind, label, value, detail)

    def state_card(self, label: str, state: str | None, why: str = "") -> Box:
        """A reader's answer in its own state, never collapsed (INVARIANTS 1)."""
        st = state if state in ("populated", "empty") else "unreachable"
        return Box(self.nid(), "pass", label, three_state(st, why), state=st)

    def gone(self, label: str, why: str) -> Box:
        return self.state_card(label, "unreachable", why)

    def you(self, text: str) -> None:
        self.write(human_line(text, self.color))

    def emit(self, said: Said, at: str = "") -> None:
        """A reply: boxes, who said the sentence, the sentence, its check chips
        and any code sentence that replaced a struck one. ``at`` is set when it
        is shown again from the pile."""
        self.show(*said.batch, *said.cards, plain=False)
        who = said.replay_who.format(at=at) if at else said.who
        self.write(who_line(who, self.color))
        for ln in said.lines:
            self.write(ln)
        if said.checks:
            prefix = f"checks as they passed at {at}:" if at else "checks:"
            self.write(checks_line(said.checks, said.names, prefix, self.color))
        for ln in said.notes:
            self.write(f"note · {ln}")
        for ln in said.tail:
            self.write(ln)

    def greeting(self, at: str) -> str:
        """``Morning.`` on the run's first reply when it is before noon, once.
        Read from the turn's own clock time, so a test's clock decides it; any
        other hour, or a time that doesn't parse, says no greeting."""
        if self.greeted:
            return ""
        self.greeted = True
        try:
            return "Morning." if 0 <= int(at.split(":")[0]) < 12 else ""
        except ValueError:
            return ""

    def speak(
        self,
        batch: list[Box],
        first: bool,
        human: str,
        page: int = 0,
        at: str = "",
        model: bool = True,
        rush: bool = True,
        look: bool = True,
    ) -> Said:
        """One reply's sentence. The model says it and code checks it; a
        sentence that fails a check is struck and code's stands; a model that
        can't be reached is an ``unreachable`` card and code's stands. Code's
        sentence is composed either way and is never a crash."""
        n = len(batch)
        earlier = self.exchanges[-THREAD_TURNS:]
        self.exchanges.append((human, list(batch)))
        code = compose(
            batch,
            first=first,
            page=page,
            greet=self.greeting(at) if first else "",
            rush=rush,
            look=look,
        )
        again = "{at}"
        if self.say is None or not model:
            return Said(
                batch,
                f"code · said {plural(n, 'box', 'boxes')}, no model asked",
                "code · shown again from the pile, no model asked now",
                [say_line(code)],
            )
        replay = (
            f"{self.model} at {again} · shown again from the pile, no model asked now"
        )
        try:
            sentence = " ".join(
                str(self.say(build_prompt(batch, human, first, earlier))).split()
            )
            state, why = ("populated", "") if sentence else ("empty", "said nothing")
        except Exception as e:  # noqa: BLE001 - a model problem is a state, not a crash
            state = "unreachable"
            why = (
                str(e) if isinstance(e, SayUnreachable) else f"{type(e).__name__}: {e}"
            )
        if state != "populated":
            return Said(
                batch,
                f"code · {self.model} {state} · said {plural(n, 'box', 'boxes')} by code",
                "code · shown again from the pile, no model asked now",
                [say_line(code)],
                cards=[
                    self.state_card(
                        "say", state, f"{self.model}: {why}{self.queued_behind(why)}"
                    )
                ],
            )
        syms = symbol_rows(sentence, self.bot.claims, self.bot.symbols)
        results = run_checks(
            sentence,
            batch,
            human,
            self.bot.claims,
            earlier=[b for _, boxes in earlier for b in boxes],
            symbols=syms,
        )
        notes = symbol_notes(syms)
        if passed(results):
            return Said(
                batch,
                f"{self.model} · said {plural(n, 'box', 'boxes')}",
                replay,
                [say_line(sentence)],
                checks=results,
                notes=notes,
            )
        return Said(
            batch,
            f"{self.model} · failed a check · replaced by a code sentence",
            replay,
            [struck_line(sentence, self.color)],
            checks=results,
            tail=[say_line(code)],
            notes=notes,
        )

    def queued_behind(self, why: str) -> str:
        """The likely cause, said as a maybe, when the reply model timed out right
        after the chain's local rung asked the same Ollama for a model: Ollama
        serves one model at a time on a small box, so the reply waited for the
        rung's model to finish or unload. Nothing else timing out gets a hint,
        and neither does a reply with no local rung before it. The facts are the
        rung's own (``model`` on its pieces)."""
        if not self.rung_models or "timed out" not in why.lower():
            return ""
        asked = ", ".join(self.rung_models)
        return (
            f" (the chain's local rung had just asked this Ollama for {asked}; "
            "the reply may have waited behind it)"
        )

    def code_reply(self, text: str) -> None:
        self.write(who_line("code · no model, nothing served", self.color))
        self.write(say_line(text))

    def converse(
        self,
        key: str,
        boxes: list[Box],
        human: str = "",
        *,
        lead: bool = False,
        rush: bool = True,
    ) -> None:
        """A turn's reply: the boxes, then one sentence over them (the model's
        if it passed its checks, else code's). Asked again, the same boxes and
        sentence come back from the pile with when they were first said;
        nothing is recomputed and no model is asked."""
        turn = self.turns.get(key)
        if turn is None:
            # a lead turn arrives in its own order (``lead_rank``), not re-ranked
            turn = self.turns[key] = Turn(
                self.clock(), list(boxes) if lead else rank(boxes), lead=lead, rush=rush
            )
        else:
            self.write(f"as noted at {turn.at} · same boxes, nothing new since")
            for said in turn.shown:
                self.emit(said, turn.at)
        self.thread = thread = Thread(turn)
        while turn.rest:
            if turn.shown and not self.more(len(turn.rest)):
                return
            batch = turn.take()
            said = self.speak(
                batch,
                not turn.shown,
                human,
                page=len(turn.shown),
                at=turn.at,
                rush=turn.rush and not turn.said_rush(),
                look=not turn.lead,
            )
            turn.shown.append(said)
            self.emit(said)
        self.offer(thread)

    def status(self, task: str) -> None:
        """A status question ("what is on the table", "what's next", "what needs
        me", "where are we": ``seat_record.status_kind``) answered from what the
        seat already has, no chain and no model: the record's NEEDS YOU lines
        (``api.needs``, one ``invocation`` row and nothing else) and, when one is
        configured, the Nestor store (read-only), merged into one box list and
        said through the same converse as a chain turn, so ``show me``, ``why``,
        ``the second one`` and ``go on`` work on them.

        Each source keeps its own state (``populated``, ``empty``,
        ``unreachable``). A Nestor store that is not configured adds no box when
        the record answered (the record's first box says only the record was
        read); with the record also unreachable it is the ``unreachable`` box it
        always was. A configured store is read as before. "Where are we" opens
        with the counts and the first open items (page one: the counts plus
        ``STORE_PAGE`` boxes, said plainly, no ``Looks like``, and no ``No
        rush.`` over a store that holds a refusal or a waiting draft), then the
        waiting drafts, the refusals, the decided and the other changes
        (``seat_nestor.lead_rank``); every other status question shows only what
        waits on the human: the record's lines and the store's waiting drafts
        (raised to ``needs you``, still marked drafts), and says so in an
        ``empty`` box when the store holds none. ``more?`` and ``go on`` page
        that order."""
        self.you(task)
        path = getattr(self.cfg, "nestor_db", None)
        asked = status_kind(task) == "needs"
        rec = read_needs(
            self.api,
            self.cfg,
            human_key=self.human_key,
            read_head=self.read_head,
            secrets=self.secrets,
            known=self.public_ids(),
        )
        boxes = list(rec.boxes)
        watched: list[Box] = []
        if (
            self.table_cfg is not None
            and not Path(str(getattr(self.table_cfg, "keys", ""))).is_file()
        ):
            tab = Reading(
                "unreachable",
                "no keys",
                [
                    Box(
                        "tstate",
                        "pass",
                        "table",
                        "unreachable — the table box's own keys are not at "
                        f"{getattr(self.table_cfg, 'keys', '?')} "
                        "(set GROVE_SEAT_TABLE_KEYS)",
                        state="unreachable",
                    )
                ],
            )
            boxes += tab.boxes
            watched = tab.boxes
        elif self.table_cfg is not None:  # Q1: watched, never written to
            tab = read_needs(
                self.api,
                self.table_cfg,
                human_key=self.human_key,
                read_head=self.read_head,
                secrets=self.secrets,
                source="table",
                known=self.public_ids(),
            )
            boxes += tab.boxes
            watched = tab.boxes
        if self.table_cfg is not None or self.table_own:
            boxes += self.beacon_note()
        counts: dict[str, int] = {}
        if path is not None and str(path).strip():
            got = read_store(path, drafts_as="you" if asked else "pr")
            counts = got.counts
            theirs = got.boxes
            if asked and got.state == "populated":
                theirs = [b for b in theirs if b.kind == "you"] or [
                    Box(
                        "nwait",
                        "pass",
                        "nestor drafts",
                        "empty — none waiting on you",
                        state="empty",
                    )
                ]
            boxes += theirs
            try:
                st = Path(path).stat()
                sig = f"{st.st_mtime_ns}:{st.st_size}"
            except (OSError, TypeError):
                sig = got.state  # a store that can't be read has no version
        else:
            sig = "none"
            if rec.state == "unreachable":  # nothing answered: say both
                boxes += read_store(None).boxes
            else:
                rec.boxes[0].detail = "\n".join(
                    [d for d in (rec.boxes[0].detail,) if d]
                    + ["no Nestor store is configured, so only the record was read"]
                )
        seen = hashlib.sha1(
            "|".join(f"{b.id}{b.value}" for b in [*rec.boxes, *watched]).encode()
        )
        self.converse(
            f"status:{status_kind(task)}:{path}:{sig}:{seen.hexdigest()[:10]}",
            lead_rank(sorted(boxes, key=open_tier)),
            task,
            lead=any(b.state == "populated" for b in boxes),
            rush=not counts.get("rejected"),
        )

    def public_ids(self) -> tuple[str, ...]:
        """The 64-hex ids the seat itself holds as public: the served tables of
        this run's served file and the sealed scope's subject hash. A poisoned
        line cannot add to it, because it comes from the api's own answers."""
        out = set()
        for t in (
            (self.doc or {}).get("tables", []) if isinstance(self.doc, dict) else []
        ):
            tid = str(t.get("id", "")) if isinstance(t, dict) else ""
            if len(tid) == 64:
                out.add(tid)
        for v in (self.sealed or {}).values() if isinstance(self.sealed, dict) else []:
            tail = str(v).rsplit(":", 1)[-1]
            if len(tail) == 64:
                out.add(tail)
        return tuple(out)

    def beacon_note(self) -> list[Box]:
        """R23: the CLI is offline unless ``GROVE_SEAT_DRAND`` (or ``--drand`` on
        the one script) asks for drand. Off, a table forecast's beacon round
        cannot be read, so no table outcome can be shown to be real: said."""
        cfgs = [c for c in (self.table_cfg, self.cfg if self.table_own else None) if c]
        if all(getattr(c, "beacon", None) is not None for c in cfgs):
            return []
        return [
            Box(
                "tbeacon",
                "block",
                "beacon",
                "unreachable — beacon reader off: table outcomes unreachable",
                "set GROVE_SEAT_DRAND to read drand rounds",
                state="unreachable",
            )
        ]

    def clean(self, b: Box, known: tuple[str, ...] = ()) -> Box:
        """A box with its words scrubbed (``seat_record.scrub``); ``known`` are
        the served ids that may stand."""
        return replace(
            b,
            value=scrub(b.value, self.secrets, known),
            detail=scrub(b.detail, self.secrets, known),
        )

    def table_story(self, task: str) -> None:
        """The table's story (R12, R21; ``table_boxes.narrate``): the served
        table's fact boxes said as one sentence. ``self.say`` is the injected
        model (None: code only); the sentence stands only if every table check
        passes, else it is struck and code's sentence stands. A seal, a
        decision or an escalated pick is shown and never said (C16); an ESCALATE
        from the model is the human's card. Nothing is rolled or written."""
        self.you(task)
        doc = (
            self.doc
            if isinstance(self.doc, dict)
            else {"state": "empty", "why": "no served file stands in this check-in"}
        )
        boxes = tb.served_boxes(doc)
        got = tb.narrate(boxes, task, say=self.say)
        n = len(tb.sayable(boxes))
        code = [say_line(got["code"])] if got["code"] else []
        cards: list[Box] = []
        if got["source"] == "model":
            who, lines, tail = (
                f"{self.model} · said {plural(n, 'box', 'boxes')}",
                [say_line(got["sentence"])],
                [],
            )
        elif got["struck"]:
            who = f"{self.model} · failed a check · replaced by a code sentence"
            lines, tail = [struck_line(got["model"], self.color)], code
        else:
            who = f"code · said {plural(n, 'box', 'boxes')} · {got['why'] or 'by code'}"
            lines, tail = code, []
            if got["escalated"]:
                cards = [
                    self.card("you", "human card", "the model escalated", got["why"])
                ]
        # a served id is a 64-hex before `_N`: known from the boxes, not from a bracket
        ids = tuple({b.id.split("_")[0] for b in boxes})
        clean = lambda t: scrub(t, self.secrets, ids)  # noqa: E731 - every line, B2/S4
        said = Said(
            [self.clean(b, ids) for b in boxes],
            clean(who),
            "code · shown again from the pile, no model asked now",
            [clean(x) for x in lines],
            cards=[self.clean(b, ids) for b in cards],
            checks=got["checks"] or [],
            tail=[clean(x) for x in tail],
            names=tb.TABLE_CHECK_NAMES,
        )
        self.emit(said)

    def offer(self, thread: Thread) -> None:
        """The chip row for what the turn showed. Its choices are remembered so
        a typed one is acknowledged, nothing more."""
        got = chips(thread.boxes())
        thread.choices = got.choices
        self.write(got.row())

    def choice(self, task: str) -> bool:
        """A typed line that is a choice chip just offered: acknowledged by
        code, never sent to the chain. It changes no record, seals nothing and
        writes no row; the row is spent."""
        th = self.thread
        hit = next(
            (c for c in (th.choices if th else []) if _norm(c) == _norm(task)), ""
        )
        if not hit:
            return False
        self.you(task)
        self.code_reply(terminate(f"Got it: {hit}"))
        th.choices = []
        return True

    def follow_up(self, task: str) -> bool:
        """Resolve a typed line against the last reply by fixed rules, in code:
        no model, no ``api.escalate``, no record row. False: not one, the line
        goes to the chain as before. A ``show me X`` / ``open X`` / ``show X``
        that no shown box answers to splits on its target
        (``seat_boxes.looks_like_ref``): a reference (a number, an id-like
        token, a box id, an ordinal or a phrase of at most two words) is a
        follow-up that found nothing, a plain code line (``unmatched``); a
        longer phrase reads as a task and goes to the chain. With no previous
        turn there is nothing to resolve against and the line is a task."""
        th = self.thread
        got = parse_follow(task) if th else None
        if th is None or got is None:
            return False
        kind, arg, prefixed = got
        boxes = th.boxes()
        if kind == "more":
            self.you(task)
            self.go_on(th)
            return True
        found: Box | None = None
        if kind == "ord":
            n = int(arg)
            if n >= len(boxes):
                return self.said(
                    task, terminate(f"{self.only(boxes)}, so there is no {ORD[n]} one")
                )
            found = boxes[n]
        elif kind in ("that", "why"):
            last = th.turn.shown[-1].batch if th.turn.shown else []
            found = th.focus or (last[0] if last else None)
        elif prefixed:
            hits = [b for b in boxes if matches(b, arg)]
            if len(hits) > 1:
                return self.said(
                    task,
                    terminate(
                        f'"{arg}" fits {plural(len(hits), "box", "boxes")}: {self.list_of(hits)}'
                    ),
                )
            found = hits[0] if hits else None
        else:
            hits = [b for b in boxes if b.id.lower() == arg]
            found = hits[0] if len(hits) == 1 else None
        if found is None:
            if kind == "ref" and prefixed and looks_like_ref(arg):
                # a reference that found nothing; a longer phrase is a task
                return self.said(task, self.unmatched(task, arg, boxes))
            return False
        th.focus = found
        self.you(task)
        if kind == "why":
            self.code_reply(self.detail_sentence(found))
        else:
            self.show(found, plain=False)
            self.code_reply(self.open_sentence(found))
        return True

    @staticmethod
    def unmatched(task: str, arg: str, boxes: list[Box]) -> str:
        """``show me X`` / ``open X`` that no shown box answers to: a fixed code
        line (the human's words quoted exactly, then up to ``UNMATCHED_LIST``
        refs of what was shown, a box's own id when it has no better ref, and a count
        of the rest), never the chain."""
        m = SHOW_RAW.fullmatch(task.strip())
        said = m[1] if m else arg
        refs = list(
            dict.fromkeys(
                (ref_tokens(b) or [b.id])[0] for b in boxes if b.role not in COUNTED
            )
        )
        head = f'Nothing I showed answers to "{said}"'
        if not refs:
            return terminate(head)
        shown, rest = refs[:UNMATCHED_LIST], len(refs) - UNMATCHED_LIST
        tail = ", ".join(shown) + (f" and {rest} more" if rest > 0 else "")
        return terminate(f"{head}; I showed: {tail}")

    def said(self, task: str, text: str) -> bool:
        self.you(task)
        self.code_reply(text)
        return True

    @staticmethod
    def list_of(boxes: list[Box]) -> str:
        return "; ".join(f"{b.id}: {_val(b.value)}" for b in boxes)

    def only(self, boxes: list[Box]) -> str:
        n = len(boxes)
        return f"I showed {plural(n, 'box', 'boxes')} ({self.list_of(boxes)})"

    @staticmethod
    def open_sentence(box: Box) -> str:
        """A box said once more: its own phrase, from its own facts."""
        return terminate(cap(clause(box)))

    @staticmethod
    def detail_sentence(box: Box) -> str:
        """``why``: the reason, said naturally (``why_sentence``): the human's
        own quoted words led by who said them, provenance left to the card but
        a fixture still marked ``(fixture)``. With nothing but provenance or
        no detail, the box's own phrase and a line saying there is no more."""
        if box.state != "populated":
            return plain_line(box)
        got = why_sentence(box)
        return got or f"{terminate(cap(clause(box)))} {NO_DETAIL}"

    def go_on(self, th: Thread) -> None:
        """The next page of the last reply, said by code (no model is asked), or
        a line saying nothing is left."""
        turn = th.turn
        if not turn.rest:
            return self.code_reply(NOTHING_MORE)
        batch = turn.take()
        said = self.speak(
            batch,
            False,
            "",
            page=len(turn.shown),
            at=turn.at,
            model=False,
            rush=turn.rush and not turn.said_rush(),
            look=not turn.lead,
        )
        turn.shown.append(said)
        self.emit(said)
        if not turn.rest:
            self.offer(th)

    def more(self, left: int) -> bool:
        ans = self.ask("more?", f"{left} more in the pile [enter = show, else keep]: ")
        self.you(ans or "more")
        if _norm(ans) in MORE_YES:
            return True
        self.code_reply(SMALL_TALK[_talk(ans)] if _talk(ans) in THANKS_LATER else STAY)
        return False

    def refused(self, res: dict) -> bool:
        if "refused" in res:
            self.show(self.gone("refused", str(res["refused"])))
            return True
        return False

    # each stage returns False to end the run (checkout still follows)

    def checkin(self) -> bool:
        res = self.api.checkin(self.cfg)
        if self.refused(res):
            return False
        if "wont_open" in res:
            self.show(self.gone("check-in", f"box won't open: {res['wont_open']}"))
            return False
        rep = res["report"]
        for line in rep.get("lines", []):
            self.show(self.card(checkin_kind(str(line), rep), "check-in", str(line)))
        if rep.get("hard_close"):
            self.show(
                self.card(
                    "block",
                    "check-in",
                    "HARD CLOSE",
                    "nothing moves until a check-in opens",
                )
            )
            return False
        return True

    def resume(self) -> bool:
        """Serve the human's newest sealed snapshot, pinned at its ``upto``.
        True: ``self.spec`` is that pinned spec, no group-by prompt. False: no
        snapshot (``{resume: None}``, or an unreachable resume), so the caller
        scopes fresh. Never ``empty`` for a failure (INVARIANTS 1)."""
        try:
            res = self.api.resume(self.cfg)
        except (EOFError, KeyboardInterrupt):
            raise
        except Exception as e:  # noqa: BLE001 - older willow-bot, or a read failure
            self.start_resume = ("unreachable",)
            self.hold(
                self.gone("resume", f"{type(e).__name__}: {e}; scoping fresh instead")
            )
            return False
        if not isinstance(res, dict) or "refused" in res:
            why = res.get("refused") if isinstance(res, dict) else "not a record"
            self.start_resume = ("unreachable",)
            self.hold(self.gone("resume", f"{why}; scoping fresh instead"))
            return False
        spec, subject = res.get("spec"), res.get("subject")
        if not isinstance(spec, dict) or not subject:
            self.start_resume = ("none",)
            return False  # {resume: None}: nothing sealed yet, today's bootstrap
        self.start_resume = (
            "sealed",
            str(subject),
            spec.get("upto"),
            res.get("sealed_at"),  # the seal row's own stamp; absent on an older bot
        )
        self.sealed = {"spec": spec, "subject": str(subject)}
        self.spec = spec
        self.pile_n = (
            None  # no stack was proposed; the snapshot's size is not recounted
        )
        self.show(
            self.card(
                "pass",
                "sealed snapshot",
                str(subject),
                f"serving the human's seal at upto={spec.get('upto')}; "
                "the desk's later rows stay out of this scope",
            )
        )
        return True

    def pooled_at_start(self) -> None:
        """One ``still pooled`` card: the proposals earlier runs left pooled
        and unsealed (``api.pooled``'s read, the same the close-out deposits),
        so the human sees them before adding more. Populated, empty and
        unreachable look different; a raise or a missing ``pooled`` (an older
        willow-bot) is an ``unreachable`` card, never a crash. It shows and
        counts only: nothing is sealed, deposited or kept."""
        label = "still pooled"
        try:
            pool = self.api.pooled(self.cfg)
        except (EOFError, KeyboardInterrupt):
            raise
        except Exception as e:  # noqa: BLE001 - older willow-bot, or a read failure
            self.start_pool = ("unreachable",)
            return self.show(self.gone(label, f"{type(e).__name__}: {e}"), plain=False)
        got = pool.get("pooled") if isinstance(pool, dict) else None
        if not isinstance(pool, dict) or "refused" in pool or not isinstance(got, list):
            why = pool.get("refused") if isinstance(pool, dict) else None
            self.start_pool = ("unreachable",)
            return self.show(
                self.gone(label, str(why or "not a pool record")), plain=False
            )
        items = [p for p in got if isinstance(p, dict)]
        if not items:
            self.start_pool = ("empty",)
            return self.show(
                self.state_card(label, "empty", "nothing pooled from earlier runs"),
                plain=False,
            )
        self.start_pool = ("populated", len(items))
        names = [str(p.get("subject") or p.get("path") or "?") for p in items]
        more = f" (+{len(names) - 2} more)" if len(names) > 2 else ""
        self.show(
            Box(
                self.nid(),
                "pr",
                label,
                f"{len(items)} from earlier runs, unsealed",
                f"{'; '.join(names[:2])}{more}\nseal in Nestor; the seat seals nothing",
            )
        )

    def hold(self, box: Box) -> None:
        """Show an unreadable resume's card without its plain line: the opening
        sentence says it (``I couldn't read the last sealed snapshot``), once.
        The box is kept so ``run`` can say its plain line if no opening comes."""
        self.held = box
        self.show(box, plain=False)

    def open_with(self) -> None:
        """The run's one opening sentence, said by code from what resume and
        pooled already returned (``seat_boxes.opening``): no api call, no model,
        no row. It carries the run's one ``Morning.`` when it is before noon, so
        the first reply does not say it again. It also says the resume and pool
        states the cards before it showed, so those cards' plain lines are not
        said as well (the same fact once)."""
        self.opened = True
        self.code_reply(
            opening(
                self.start_resume,
                self.start_pool,
                self.greeting(self.clock()),
                self.today(),
            )
        )

    def grown_scope(self) -> None:
        """Before check-out, for a served snapshot: what a fresh scope at the
        latest row would be called. If it differs from the sealed subject it
        joins the one ``seal ↗`` offer. This only proposes a scope; the seat
        seals nothing."""
        if not self.sealed or self.doc is None:
            return
        spec = self.sealed["spec"]
        try:
            res = self.api.scope(
                self.cfg, by=list(spec.get("by") or ["who"]), match=spec.get("match")
            )
        except Exception as e:  # noqa: BLE001 - the close-out must not be lost
            self.show(self.gone("grown scope", f"{type(e).__name__}: {e}"))
            return
        if self.refused(res):
            return
        now = res.get("subject")
        if now and now != self.sealed["subject"]:
            self.grown = str(now)

    def scope(self) -> bool:
        while True:
            by = self.ask("scope", f"group by (enter = {DEFAULT_BY}): ") or DEFAULT_BY
            words = [w.strip() for w in by.split(",") if w.strip()]
            res = self.api.scope(self.cfg, by=words or [DEFAULT_BY])
            usage = self.bad_group_by(res, by)
            if not usage:
                break
            self.code_reply(usage)  # the human's answer was refused: say so, re-ask
        if self.refused(res):
            return False
        if not res.get("ids"):
            self.show(
                self.state_card("scope", "empty", "no table matches; nothing to serve")
            )
            return False
        for t in res.get("stack", []):
            self.show(
                self.card(
                    "pass", "table", str(t["name"]), row_count(t["rows"]), t["id"][:12]
                )
            )
        self.show(self.card("pass", "subject", str(res["subject"])))
        self.pile_n = sum(
            t["rows"] for t in res.get("stack", []) if isinstance(t.get("rows"), int)
        )
        self.spec = res["spec"]
        return True

    @staticmethod
    def bad_group_by(res: dict, said: str) -> str:
        """The plain line for a refusal that is the human's answer at the
        group-by prompt (a usage error, read from the refusal's own words): the
        words it takes, and what was said. ``""`` for any other refusal, which
        stays a ``refused`` card; the stage is not unreachable for a typo."""
        got = GROUP_BY_REFUSAL.search(str(res.get("refused", "")))
        if not got:
            return ""
        names = re.findall(r"[\w-]+", got["names"])
        if not names:
            return ""
        head = ", ".join(names[:-1]) + (" or " if len(names) > 1 else "") + names[-1]
        return f'Group by takes {head}; you said "{said}".'

    def served(self) -> bool:
        while True:
            raw = self.ask(
                "served", f"cap in characters (enter = {DEFAULT_MAX_CHARS}): "
            )
            if not raw:
                cap = DEFAULT_MAX_CHARS
            elif raw.isascii() and raw.isdigit() and int(raw) >= 1:
                cap = int(raw)
            else:  # the human's answer, said as it is; no card, no state
                self.code_reply(
                    f'The cap takes a whole number, 1 or more; you said "{raw}".'
                )
                continue
            break
        res = self.api.serve(self.cfg, self.spec, max_chars=cap)
        if self.refused(res):
            return False
        self.doc = res["doc"]
        self.show(self.state_card("served", res["state"], res.get("why", "")))
        if self.pile_n is not None:
            self.write(pile_header(self.pile_n))
        self.write(legend(self.color))
        return True

    def piece_box(self, p: dict) -> Box:
        if p["outcome"] == "answered":
            kind, detail = "pass", ""
        else:
            kind = "you" if p.get("reason") in NO_FLOWER else "block"
            detail = f"reason: {p.get('reason', p['label'])}"
        return Box(p["piece"][:12], kind, p["label"], self.piece_value(p), detail)

    @staticmethod
    def piece_value(p: dict) -> str:
        """What a piece's box says: ``<rung>: <detail>``. An answered piece
        carries no detail of its own (willow-bot leaves it empty), so it says its
        first row's claim (``CLAIM_CHARS`` at most) in its place; a local or hash
        answer with nothing to say, an empty claim and no data, is said plainly
        ("the local model gave an empty answer"), never as ``Local:.``."""
        rung, detail = p["rung"], str(p.get("detail") or "").strip()
        if detail or p["outcome"] != "answered":
            return f"{rung}: {detail}"
        said = next(
            (
                " ".join(r[k].split())
                for r in p.get("rows") or []
                if isinstance(r, dict)
                for k in ("claim", "answer")
                if isinstance(r.get(k), str) and r[k].strip()
            ),
            "",
        )
        if said:
            if len(said) > CLAIM_CHARS:
                said = said[: CLAIM_CHARS - 1] + "…"
            return f"{rung}: {said}"
        return EMPTY_ANSWER if rung != "d0" else f"{rung}: nothing to say"

    def chain(self, task: str) -> None:
        key = _norm(task)
        self.you(task)
        if key in self.turns:  # asked again: from the pile, no recompute
            self.converse(key, [], task)
            return
        res = self.api.escalate(
            self.cfg,
            task,
            model=self.model,  # one model: the local rung uses the reply model
            piece_chars=self.bot.piece_chars,
            ratatosk=(self.ratatosk,),
        )
        if self.refused(res):
            return
        pieces = res.get("pieces", [])
        if pieces:
            # role "count": the summary is a count of pieces, not a piece, so it
            # is said on its own ("The chain answered 1 and escalated 0.") and
            # never paired or run with a piece, as the store's count is not
            boxes = [
                Box(
                    self.nid(),
                    "pass",
                    "chain",
                    f"answered {res.get('answered', 0)}, escalated {res.get('escalated', 0)}",
                    role="count",
                )
            ]
            boxes += [self.piece_box(p) for p in pieces]
        else:
            boxes = [self.state_card("chain", "empty", "the chain cut nothing")]
        for p in pieces:
            if p["outcome"] == "answered" and p["rung"] != "d0":
                self.pending += [r for r in p.get("rows") or [] if _is_row(r)]
        self.rung_models = sorted(
            {
                str(p["model"])
                for p in pieces
                if p.get("rung") == "local" and p.get("model")
            }
        )
        try:
            self.converse(key, boxes, task)
        finally:
            self.rung_models = []
        left = [p for p in pieces if p["outcome"] == "escalated"]
        if left:
            self.flowering(res["task"], left)

    def piece_for(self, question: str, result: dict) -> dict | None:
        if result["rung"] == "d0":
            return self.doc
        for p in self.bot.cut(self.doc or {}, question, self.bot.piece_chars):
            if p["hash"] == result["piece"]:
                return p["piece"]
        return None

    def flowering(self, question: str, left: list[dict]) -> None:
        for r in left:
            tag = f"{r['piece'][:12]} ({r.get('reason', r['label'])})"
            if r.get("reason") in NO_FLOWER or self.doc is None:
                self.show(
                    self.card(
                        "you",
                        "human card",
                        tag,
                        "code decided; it goes to the human card",
                    )
                )
                continue
            piece = self.piece_for(question, r)
            if piece is None:
                self.show(
                    self.gone("flowering", f"{tag}: the piece isn't in the served file")
                )
                continue
            if self.ask("flowering", f"{tag}: one cloud turn? [y/N] ").lower() != "y":
                continue
            got = self.flower(piece, question)
            self.show(
                self.card("pass", "cloud turn", str(got["summary"] or "no summary"))
            )
            rows = [x for x in got["rows"] if not _escalates(x)]
            if len(rows) < len(got["rows"]):
                self.show(
                    self.card(
                        "you",
                        "human card",
                        "the cloud turn escalated",
                        "it stays on the human card",
                    )
                )
            if rows:
                taken = self.api.take_proposals(self.cfg, rows, bite="flowering")
                if not self.refused(taken):
                    for p in taken["out"].get("proposals", []):
                        if p.get("verdict") == "pass":
                            self.pending.append(p)
                        else:
                            self.show(
                                self.card(
                                    "block",
                                    str(p.get("verdict")),
                                    str(p.get("reason")),
                                )
                            )

    def proposals(self) -> None:
        """Show each pass and leave it pooled: the rows are already on record
        (the chain and ``take_proposals`` wrote them); nothing is sealed here."""
        while self.pending:
            p = self.pending.pop(0)
            subject = p.get("subject") or self.bot.subject(
                {k: p[k] for k in ("path", "data", "cites", "claim")}
            )
            data = p["data"] if len(p["data"]) <= 400 else p["data"][:399] + "…"
            self.show(
                self.card(
                    "pr",
                    "pooled",
                    f"{p['path']} · cites {len(p['cites'])} — {p['claim']}",
                    f"{data}\npooled: {subject}",
                    str(subject).split(":")[-1][:12],
                )
            )

    def checkout(self) -> None:
        kw = {
            k: v
            for k, v in (("human_key", self.human_key), ("read_head", self.read_head))
            if v
        }
        try:
            res = self.api.checkout(self.cfg, **kw)
        except Exception as e:  # noqa: BLE001 - the close-out must not be lost
            self.show(self.gone("morning screen", f"{type(e).__name__}: {e}"))
        else:
            if not self.refused(res):
                screen = scrub(str(res.get("screen", "")), self.secrets).strip()
                self.show(
                    self.card("pass", "morning screen", screen)
                    if screen
                    else self.state_card("morning screen", "empty", "nothing to report")
                )
        self.close_out()

    def close_out(self) -> None:
        """Deposit the pool as Nestor drafts, make the one seal offer, then say
        what stays pooled for next time (``seat_boxes.carry_over``): one code
        sentence from the pool this close-out already read, in its own
        ``populated``, ``empty`` or ``unreachable`` clause. It seals, deposits
        and writes nothing beyond what the close-out already does. A pool card
        it already says (unreadable, or an empty deposit of an empty pool) has no
        plain line of its own, so the fact is said once."""
        self.carry: tuple = ("unreachable",)
        try:
            self.deposit_pool()
        finally:
            self.code_reply(carry_over(self.carry))

    def deposit_pool(self) -> None:
        try:
            pool = self.api.pooled(self.cfg)
        except Exception as e:  # noqa: BLE001 - the close-out must not raise
            self.show(self.gone("pool", f"{type(e).__name__}: {e}"), plain=False)
            return self.offer_grown()  # the closing sentence says it
        if not isinstance(pool, dict) or "refused" in pool:
            why = pool.get("refused") if isinstance(pool, dict) else "not a pool record"
            self.show(self.gone("pool", str(why)), plain=False)
            return self.offer_grown()  # the closing sentence says it
        items = [p for p in pool.get("pooled") or [] if isinstance(p, dict)]
        self.carry = ("populated", len(items)) if items else ("empty",)
        try:
            got = self.deposit(pool)
        except Exception as e:  # noqa: BLE001 - the close-out must not raise
            got = {"state": "unreachable", "reason": f"{type(e).__name__}: {e}"}
        state = got.get("state")
        if state != "populated":
            # an empty deposit of an empty pool is what the closing says
            # ("Nothing stays pooled"): the card stays, the plain line waits
            self.show(
                self.state_card("deposit", state, got.get("reason", "")),
                plain=not (state == "empty" and self.carry == ("empty",)),
            )
            if state != "empty":  # nothing went in; show what is pooled
                for p in items:
                    self.show(
                        self.card("pr", "pooled, not deposited", str(p.get("subject")))
                    )
            return self.offer_grown()
        drafts = got.get("deposited") or []
        self.show(
            self.card(
                "dec",
                "deposit",
                f"{len(drafts)} in Nestor as {'a draft' if len(drafts) == 1 else 'drafts'}",
            )
        )
        for d in drafts:
            if d.get("status") == "error":
                self.show(
                    self.card(
                        "block",
                        "draft",
                        str(d.get("subject")),
                        f"ERROR: {d.get('error')}",
                    )
                )
            else:
                self.show(
                    self.card(
                        "pr", "draft", str(d.get("subject")), str(d.get("status"))
                    )
                )
        subjects = ", ".join(
            str(d.get("subject")) for d in drafts if d.get("status") != "error"
        )
        self.seal_offer(subjects)

    def offer_grown(self) -> None:
        """No draft to seal, but a grown scope: the offer carries just that."""
        if self.grown:
            self.seal_offer()

    def seal_offer(self, subjects: str = "") -> None:
        """The one ``seal ↗`` card. A grown scope's subject rides on it."""
        detail = f"the only place a seal is made · to seal: {subjects or 'none'}"
        if self.grown:
            detail += f" · advance the snapshot: {self.grown}"
        self.show(self.card("you", "seal ↗", NESTOR_UI, detail))

    def run(self) -> int:
        try:
            if not self.checkin():
                return 1
        except (EOFError, KeyboardInterrupt):
            return 1
        try:
            if self.resume() or self.scope():
                self.pooled_at_start()
                self.open_with()
                if self.served():
                    while task := self.ask("chain", "task (empty to check out): "):
                        if _talk(task) in FAREWELLS:  # like an empty line
                            self.you(task)
                            break
                        if _talk(task) in SMALL_TALK:  # small talk: code, no boxes
                            self.you(task)
                            self.code_reply(SMALL_TALK[_talk(task)])
                            continue
                        if self.choice(task) or self.follow_up(task):
                            continue  # code answered it: no chain, no model
                        if status_kind(task):
                            self.status(task)  # the record and the store: no chain
                            continue
                        if story_kind(task):
                            self.table_story(task)  # the served table's boxes, said
                            continue
                        self.chain(task)
                        self.proposals()
            return 0
        except (EOFError, KeyboardInterrupt):
            self.write("")
            return 0
        finally:
            if self.held is not None and not self.opened:
                self.code_reply(plain_line(self.held))  # no opening: say it here
            self.grown_scope()
            self.checkout()


def open_tier(b: Box) -> int:
    """Where a box stands among what waits on the human in a status turn:
    proposals first, then the store's waiting drafts, then any other record
    line, then the re-checks (the many), so the first page shows both sources.
    Every other box is tier 0 and keeps its place (the sort is stable)."""
    if b.state != "populated":
        return 0
    if b.kind == "you" and b.label == "proposal":
        return 1
    if b.role == "draft" or (b.kind == "you" and b.role == "more"):
        return 2
    if b.kind == "you" and b.label == "record":
        return 3
    return 4 if b.kind == "you" and b.label == "re-check" else 0


def _is_row(r: object) -> bool:
    return isinstance(r, dict) and all(
        k in r for k in ("path", "data", "cites", "claim")
    )


def _escalates(r: object) -> bool:
    return isinstance(r, dict) and r.get("path") == ESCALATE_PATH


def grove_version() -> str:
    """The grove package version: the installed distribution's, else the hatch
    ``fallback-version`` in ``pyproject.toml`` (a checkout that isn't installed,
    which is what ``scripts/grove-seat`` runs), else ``unknown``."""
    try:
        return metadata.version("willows-grove")
    except metadata.PackageNotFoundError:
        pass
    try:
        with (GROVE_ROOT / "pyproject.toml").open("rb") as f:
            return str(tomllib.load(f)["tool"]["hatch"]["version"]["fallback-version"])
    except (OSError, KeyError, ValueError):
        return "unknown"


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="grove-seat",
        description="The desk's command-line seat. With no flag it opens a "
        "session: check-in (which writes record rows), scope, chain, check-out.",
    )
    p.add_argument(
        "--version", action="version", version=f"grove-seat {grove_version()}"
    )
    p.add_argument(
        "--check",
        action="store_true",
        help="probe only: bot root, python, ratatosk, the Ollama loopback; "
        "no check-in, nothing written; exit 0 only if all are populated",
    )
    p.add_argument(
        "--no-say",
        action="store_true",
        help="code only: no local model says the reply sentence, Ollama is never asked",
    )
    p.add_argument(
        "--model",
        metavar="NAME",
        help=f"the run's one model: it says the reply and is the chain's local rung "
        f"(default {MODEL}, or GROVE_SAY_MODEL; the flag wins over the env); "
        "not with --no-say",
    )
    return p


def check_line(label: str, state: str, why: str = "") -> str:
    """One probe line, its state spelled out (INVARIANTS 1): ``populated`` is
    followed by what was found, ``empty`` and ``unreachable`` by why."""
    return f"{label:<10} {state}" + (f" — {why}" if why else "")


def probe(root: Path, model: str | None = MODEL) -> list[tuple[str, str, str]]:
    """What ``--check`` reports, as ``(label, state, why)``. It imports no
    willow-bot module, calls no api function and writes nothing. ``model``
    None (``--no-say``) leaves the Ollama row out: a code-only run never asks."""
    one = root / "one-script" / "onescript" / "api.py"
    bot_ = (
        ("populated", str(root))
        if one.is_file()
        else ("unreachable", f"no one script at {one.parent} (set WILLOW_BOT_ROOT)")
    )
    venv = "a venv" if sys.prefix != sys.base_prefix else "no venv"
    rat = resolve_ratatosk()
    where = rat if Path(rat).is_file() else shutil.which(rat)
    return [
        ("bot root", *bot_),
        ("python", "populated", f"{sys.executable} ({venv}: {sys.prefix})"),
        (
            "ratatosk",
            *(
                ("populated", where)
                if where
                else ("unreachable", f"{rat} is not on the path")
            ),
        ),
        *([("ollama", *ollama_probe(model))] if model else []),
    ]


def main(argv: list[str] | None = None) -> int:
    p = parser()
    try:
        args = p.parse_args([] if argv is None else argv)
        if args.no_say and args.model is not None:
            p.error("--no-say and --model conflict: no model is asked")
        if args.model is not None and not args.model.strip():
            p.error("--model needs a model name")
    except SystemExit as e:  # --help and --version exit 0, a bad flag 2
        return int(e.code or 0)
    model = (args.model or "").strip() or MODEL  # the flag wins over GROVE_SAY_MODEL
    if args.check:
        got = probe(bot_root(), None if args.no_say else model)
        print("\n".join(check_line(*g) for g in got))
        return 0 if all(g[1] == "populated" for g in got) else 1
    root = bot_root()
    try:
        bot = load_bot(root)
    except SeatUnavailable as e:
        print(f"grove seat: {e}", file=sys.stderr)
        return 2
    say = None if args.no_say else ollama_say(model=model)
    key = os.environ.get("GROVE_SEAT_HUMAN_KEY", "").strip()
    ledger = os.environ.get("GROVE_SEAT_LEDGER", "").strip()
    return Seat(
        bot,
        config(bot, root),
        table_cfg=table_config(bot, root),
        table_own=bool(os.environ.get("GROVE_SEAT_BOX", "").strip()),
        say=say,
        model=model,
        human_key=Path(key).expanduser() if key else None,
        read_head=ledger_reader(ledger) if ledger else None,
    ).run()


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
