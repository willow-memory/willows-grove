# b17: GRSET ΔΣ=42
"""grove seat — the one script at a terminal: the desk's command-line seat.

    scripts/grove-seat            # check-in, scope, served, chain, proposals

The third front end beside the web components and the phone APK. All three
call willow-bot's ``one-script/onescript/api.py``, so a seat run leaves the
same record rows the app does. This module only reads keys, prints, and
calls those functions; it holds no seal key, names no model provider, and
writes nothing but a scratch file per cloud turn.

The stages, in order, each shown in the prompt (``scope ▶``):

    checkin    api.checkin: the record, the probes, the four gates
    scope      api.scope proposes a stack and names its subject; no prompt
    served     api.serve is the silent start-check: it serves only a scope a
               past human seal already covers (three states, never collapsed)
    chain      api.escalate: D0 code, then the hash record, then a local rung
    flowering  for a piece the chain left, one cloud turn on the human's yes:
               ``ratatosk --onescript --class flowering`` (the ladder picks
               the provider), its rows judged by api.take_proposals
    proposals  each pass shown and left pooled; nothing is sealed here
    checkout   api.checkout, on exit, EOF or Ctrl-C alike; then the pool is
               deposited into Nestor as drafts (willow-mcp's
               ``onescript_deposit``, injectable) and ONE ``seal ↗`` offer
               points at the Nestor UI, the only place a seal is made

The seat never seals: no prompt asks for one, it holds no key, and the deposit
only proposes.

What the seat prints is the box stream (``grove/seat_boxes.py``, after
``web/demo/box-stream/box-stream-v1.3.html``): everything the agent says is a
box card or a reply made of cards, a line that is not one is the human's. A
reply's one sentence is said by a local model (``qwen3:4b`` on the Ollama
loopback, the injected ``say``; ``grove/seat_say.py``) and then checked by code
against the boxes: every cite served, every box cited, nothing the boxes lack,
the human's words quoted exactly. A sentence that fails a check is shown
struck and replaced by the sentence code composes from box facts plus fixed
glue, which is also what stands when the model can't be reached (an
``unreachable`` card, never a crash). With no ``say`` the seat is code only.
A chain turn shows two boxes at a time (``more?``), small talk is answered by
code, and a task asked again is shown again from the pile, stamped with when it
was first said. Under ``NO_COLOR`` or a non-tty the cards are plain ASCII with
no escape codes.

The operator, 2026-10-09: "The deterministic chain runs, esclates to local
models if need be, then to the cloud models"; "It should live in the grove,
along side the web and apk"; "not anthropic. there is already routing in the
crown. Agent agnostic". Two chain rules hold here too: a piece code cut as
over its cap never reaches a model, and an empty or unreachable scope is
escalated by code, never handed to one.

willow-bot is found at ``WILLOW_BOT_ROOT``, else beside this repo
(``../willow-bot``), the way the one script finds this repo.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import time
from collections.abc import Callable, Sequence
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from grove.seat_boxes import (
    Box,
    compose,
    human_line,
    checks_line,
    legend,
    pile_header,
    render_box,
    say_line,
    struck_line,
    use_color,
    who_line,
)
from grove.seat_say import (
    CHECK_NAMES,
    MODEL,
    SayUnreachable,
    build_prompt,
    ollama_say,
    passed,
    run_checks,
)

GROVE_ROOT = Path(__file__).resolve().parent.parent
ESCALATE_PATH = "ESCALATE"
#: Reasons a flowering turn may not take: code decided these, no model.
NO_FLOWER = frozenset({"cap", "empty_scope"})
DEFAULT_MAX_CHARS = 48_000
FLOWER_TIMEOUT = 300.0
NESTOR_UI = "http://127.0.0.1:8765"
NO_DEPOSIT = "deposit unavailable here: willow-mcp not on the path"
#: Boxes a reply shows before ``more?``.
PAGE = 2
#: What code answers to small talk: no boxes, nothing served.
SMALL_TALK = {
    "thanks": "Anytime.",
    "thank you": "Anytime.",
    "later": "Got it. It stays in the pile.",
}
MORE_YES = frozenset({"", "m", "more", "y", "yes"})
STAY = "Got it. It stays in the pile."
CHIPS = "chips: [later] [thanks]"


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


def bot_root() -> Path:
    got = os.environ.get("WILLOW_BOT_ROOT")
    return Path(got).expanduser() if got else GROVE_ROOT.parent / "willow-bot"


def load_bot(root: Path) -> Bot:
    one = root / "one-script"
    if not (one / "onescript" / "api.py").is_file():
        raise SeatUnavailable(
            f"unreachable: no one script at {one} (set WILLOW_BOT_ROOT)"
        )
    sys.path.insert(0, str(one))
    try:
        from onescript import api, escalate, gate, proposals
    except ImportError as e:
        raise SeatUnavailable(f"unreachable: the one script won't import: {e}") from e
    return Bot(
        api, escalate.cut, proposals.subject, escalate.PIECE_CHARS, gate.check_claims
    )


def config(bot: Bot, root: Path, grove: Path = GROVE_ROOT):
    """The Config the one script's own CLI builds, with the same defaults."""
    home = Path(os.environ.get("WILLOW_HOME", "~")).expanduser()
    return bot.api.Config(
        box=root / ".flow" / "onescript",
        keys=root / ".flow" / "onescript-keys" / "keys.json",
        constitution=grove / "governance" / "CONSTITUTION.md",
        ci=grove / ".github" / "workflows" / "tests.yml",
        root=root,
        grove=grove,
        venv=home / "venvs" / "willow-bot",
        keyring=bot.api.default_keyring(),
        nestor_db=bot.api.default_nestor_db(),
    )


# --- the flowering rung --------------------------------------------------------


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


def three_state(state: str | None, why: str = "") -> str:
    if state == "populated":
        return "populated"
    if state == "empty":
        return f"empty — {why or 'nothing in scope'}"
    return f"unreachable — {why or 'no answer'}"


def _norm(text: str) -> str:
    return " ".join(text.lower().split())


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


@dataclass
class Turn:
    """One answered question, kept in the pile: what was said, and what is
    still waiting behind ``more?``. Asking again replays ``shown``."""

    at: str
    rest: list[Box]
    shown: list[Said] = field(default_factory=list)


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
    ):
        self.bot, self.api, self.cfg = bot, bot.api, cfg
        self.flower = flower or ratatosk_flowering()
        self.deposit = deposit or willow_mcp_deposit()
        #: The local model's sentence, ``say(prompt) -> str``. None: code only.
        self.say, self.model = say, model
        self.read, self.write = read, write
        self.color = use_color() if color is None else color
        self.clock = clock
        self.doc: dict | None = None
        self.pending: list[dict] = []  # passes not yet shown; the pool keeps them
        self.turns: dict[str, Turn] = {}  # the pile of what was asked and said
        self.pile_n = 0
        self._n = 0

    # -- the stream: cards, replies, the human's line

    def ask(self, stage: str, prompt: str = "") -> str:
        return self.read(f"{stage} ▶ {prompt}").strip()

    def nid(self) -> str:
        self._n += 1
        return f"b{self._n}"

    def put(self, text: str) -> None:
        for ln in text.split("\n"):
            self.write(ln)

    def show(self, *boxes: Box) -> None:
        for b in boxes:
            self.put(render_box(b, self.color))

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
        self.show(*said.batch, *said.cards)
        who = said.replay_who.format(at=at) if at else said.who
        self.write(who_line(who, self.color))
        for ln in said.lines:
            self.write(ln)
        if said.checks:
            prefix = f"checks as they passed at {at}:" if at else "checks:"
            self.write(checks_line(said.checks, CHECK_NAMES, prefix, self.color))
        for ln in said.tail:
            self.write(ln)

    def speak(self, batch: list[Box], first: bool, human: str) -> Said:
        """One reply's sentence. The model says it and code checks it; a
        sentence that fails a check is struck and code's stands; a model that
        can't be reached is an ``unreachable`` card and code's stands. Code's
        sentence is composed either way and is never a crash."""
        n = len(batch)
        code = compose(batch, first=first)
        again = "{at}"
        if self.say is None:
            return Said(
                batch,
                f"code · said {n} boxes, no model asked",
                "code · shown again from the pile, no model asked now",
                [say_line(code)],
            )
        replay = (
            f"{self.model} at {again} · shown again from the pile, no model asked now"
        )
        try:
            sentence = " ".join(
                str(self.say(build_prompt(batch, human, first))).split()
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
                f"code · {self.model} {state} · said {n} boxes by code",
                "code · shown again from the pile, no model asked now",
                [say_line(code)],
                cards=[self.state_card("say", state, f"{self.model}: {why}")],
            )
        results = run_checks(sentence, batch, human, self.bot.claims)
        if passed(results):
            return Said(
                batch,
                f"{self.model} · said {n} boxes",
                replay,
                [say_line(sentence)],
                checks=results,
            )
        return Said(
            batch,
            f"{self.model} · failed a check · replaced by a code sentence",
            replay,
            [struck_line(sentence, self.color)],
            checks=results,
            tail=[say_line(code)],
        )

    def code_reply(self, text: str) -> None:
        self.write(who_line("code · no model, nothing served", self.color))
        self.write(say_line(text))

    def converse(self, key: str, boxes: list[Box], human: str = "") -> None:
        """A turn's reply: the boxes, then one sentence over them (the model's
        if it passed its checks, else code's). Asked again, the same boxes and
        sentence come back from the pile with when they were first said;
        nothing is recomputed and no model is asked."""
        turn = self.turns.get(key)
        if turn is None:
            turn = self.turns[key] = Turn(self.clock(), list(boxes))
        else:
            self.write(f"as noted at {turn.at} · same boxes, nothing new since")
            for said in turn.shown:
                self.emit(said, turn.at)
        while turn.rest:
            if turn.shown and not self.more(len(turn.rest)):
                return
            batch, turn.rest = turn.rest[:PAGE], turn.rest[PAGE:]
            said = self.speak(batch, not turn.shown, human)
            turn.shown.append(said)
            self.emit(said)
        self.write(CHIPS)

    def more(self, left: int) -> bool:
        ans = self.ask("more?", f"{left} more in the pile [enter = show, else keep]: ")
        self.you(ans or "more")
        if _norm(ans) in MORE_YES:
            return True
        self.code_reply(SMALL_TALK.get(_norm(ans), STAY))
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
            self.show(self.card("pass", "check-in", str(line)))
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

    def scope(self) -> bool:
        by = self.ask("scope", "group by [who]: ") or "who"
        res = self.api.scope(self.cfg, by=[w for w in by.split(",") if w])
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
                    "pass", "table", str(t["name"]), f"{t['rows']} rows", t["id"][:12]
                )
            )
        self.show(self.card("pass", "subject", str(res["subject"])))
        self.pile_n = sum(
            t["rows"] for t in res.get("stack", []) if isinstance(t.get("rows"), int)
        )
        self.spec = res["spec"]
        return True

    def served(self) -> bool:
        raw = self.ask("served", f"cap in characters [{DEFAULT_MAX_CHARS}]: ")
        try:
            cap = int(raw) if raw else DEFAULT_MAX_CHARS
        except ValueError:
            self.show(self.card("block", "served", "not a whole number"))
            return self.served()
        res = self.api.serve(self.cfg, self.spec, max_chars=cap)
        if self.refused(res):
            return False
        self.doc = res["doc"]
        self.show(self.state_card("served", res["state"], res.get("why", "")))
        self.write(pile_header(self.pile_n))
        self.write(legend(self.color))
        return True

    def piece_box(self, p: dict) -> Box:
        if p["outcome"] == "answered":
            kind, detail = "pass", ""
        else:
            kind = "you" if p.get("reason") in NO_FLOWER else "block"
            detail = f"reason: {p.get('reason', p['label'])}"
        return Box(
            p["piece"][:12], kind, p["label"], f"{p['rung']}: {p['detail']}", detail
        )

    def chain(self, task: str) -> None:
        key = _norm(task)
        self.you(task)
        if key in self.turns:  # asked again: from the pile, no recompute
            self.converse(key, [], task)
            return
        res = self.api.escalate(self.cfg, task, piece_chars=self.bot.piece_chars)
        if self.refused(res):
            return
        pieces = res.get("pieces", [])
        if pieces:
            boxes = [
                self.card(
                    "pass",
                    "chain",
                    f"answered {res.get('answered', 0)}, escalated {res.get('escalated', 0)}",
                )
            ]
            boxes += [self.piece_box(p) for p in pieces]
        else:
            boxes = [self.state_card("chain", "empty", "the chain cut nothing")]
        for p in pieces:
            if p["outcome"] == "answered" and p["rung"] != "d0":
                self.pending += [r for r in p.get("rows") or [] if _is_row(r)]
        self.converse(key, boxes, task)
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
        try:
            res = self.api.checkout(self.cfg)
        except Exception as e:  # noqa: BLE001 - the close-out must not be lost
            self.show(self.gone("morning screen", f"{type(e).__name__}: {e}"))
        else:
            if not self.refused(res):
                screen = str(res.get("screen", "")).strip()
                self.show(
                    self.card("pass", "morning screen", screen)
                    if screen
                    else self.state_card("morning screen", "empty", "nothing to report")
                )
        self.close_out()

    def close_out(self) -> None:
        """Deposit the pool as Nestor drafts, then make the one seal offer."""
        try:
            pool = self.api.pooled(self.cfg)
        except Exception as e:  # noqa: BLE001 - the close-out must not raise
            self.show(self.gone("pool", f"{type(e).__name__}: {e}"))
            return
        items = [p for p in pool.get("pooled") or [] if isinstance(p, dict)]
        if "refused" in pool:
            self.show(self.gone("pool", str(pool["refused"])))
            return
        try:
            got = self.deposit(pool)
        except Exception as e:  # noqa: BLE001 - the close-out must not raise
            got = {"state": "unreachable", "reason": f"{type(e).__name__}: {e}"}
        state = got.get("state")
        if state != "populated":
            self.show(self.state_card("deposit", state, got.get("reason", "")))
            if state != "empty":  # nothing went in; show what is pooled
                for p in items:
                    self.show(
                        self.card("pr", "pooled, not deposited", str(p.get("subject")))
                    )
            return
        drafts = got.get("deposited") or []
        self.show(self.card("dec", "deposit", f"{len(drafts)} in Nestor as drafts"))
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
        self.show(
            self.card(
                "you",
                "seal ↗",
                NESTOR_UI,
                f"the only place a seal is made · to seal: {subjects or 'none'}",
            )
        )

    def run(self) -> int:
        try:
            if not self.checkin():
                return 1
        except (EOFError, KeyboardInterrupt):
            return 1
        try:
            if self.scope() and self.served():
                while task := self.ask("chain", "task (empty to check out): "):
                    if _norm(task) in SMALL_TALK:  # small talk: code, no boxes
                        self.you(task)
                        self.code_reply(SMALL_TALK[_norm(task)])
                        continue
                    self.chain(task)
                    self.proposals()
            return 0
        except (EOFError, KeyboardInterrupt):
            self.write("")
            return 0
        finally:
            self.checkout()


def _is_row(r: object) -> bool:
    return isinstance(r, dict) and all(
        k in r for k in ("path", "data", "cites", "claim")
    )


def _escalates(r: object) -> bool:
    return isinstance(r, dict) and r.get("path") == ESCALATE_PATH


def main(argv: list[str] | None = None) -> int:
    root = bot_root()
    try:
        bot = load_bot(root)
    except SeatUnavailable as e:
        print(f"grove seat: {e}", file=sys.stderr)
        return 2
    return Seat(bot, config(bot, root), say=ollama_say()).run()


if __name__ == "__main__":
    sys.exit(main())
