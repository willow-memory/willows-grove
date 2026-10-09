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
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

GROVE_ROOT = Path(__file__).resolve().parent.parent
ESCALATE_PATH = "ESCALATE"
#: Reasons a flowering turn may not take: code decided these, no model.
NO_FLOWER = frozenset({"cap", "empty_scope"})
DEFAULT_MAX_CHARS = 48_000
FLOWER_TIMEOUT = 300.0
NESTOR_UI = "http://127.0.0.1:8765"
NO_DEPOSIT = "deposit unavailable here: willow-mcp not on the path"


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
        from onescript import api, escalate, proposals
    except ImportError as e:
        raise SeatUnavailable(f"unreachable: the one script won't import: {e}") from e
    return Bot(api, escalate.cut, proposals.subject, escalate.PIECE_CHARS)


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


class Seat:
    def __init__(
        self,
        bot: Bot,
        cfg: Any,
        *,
        flower: Callable[[dict, str], dict] | None = None,
        deposit: Callable[[dict], dict] | None = None,
        read: Callable[[str], str] = input,
        write: Callable[[str], None] = print,
    ):
        self.bot, self.api, self.cfg = bot, bot.api, cfg
        self.flower = flower or ratatosk_flowering()
        self.deposit = deposit or willow_mcp_deposit()
        self.read, self.write = read, write
        self.doc: dict | None = None
        self.pending: list[dict] = []  # passes not yet shown; the pool keeps them

    def ask(self, stage: str, prompt: str = "") -> str:
        return self.read(f"{stage} ▶ {prompt}").strip()

    def refused(self, res: dict) -> bool:
        if "refused" in res:
            self.write(f"  refused: {res['refused']}")
            return True
        return False

    # each stage returns False to end the run (checkout still follows)

    def checkin(self) -> bool:
        res = self.api.checkin(self.cfg)
        if self.refused(res):
            return False
        if "wont_open" in res:
            self.write(f"  box won't open: {res['wont_open']}")
            return False
        rep = res["report"]
        for line in rep.get("lines", []):
            self.write(f"  {line}")
        if rep.get("hard_close"):
            self.write("  HARD CLOSE: nothing moves until a check-in opens")
            return False
        return True

    def scope(self) -> bool:
        by = self.ask("scope", "group by [who]: ") or "who"
        res = self.api.scope(self.cfg, by=[w for w in by.split(",") if w])
        if self.refused(res):
            return False
        if not res.get("ids"):
            self.write("  empty — no table matches; nothing to serve")
            return False
        for t in res.get("stack", []):
            self.write(f"  {t['name']}  {t['rows']} rows  {t['id'][:12]}")
        self.write(f"  subject: {res['subject']}")
        self.spec = res["spec"]
        return True

    def served(self) -> bool:
        raw = self.ask("served", f"cap in characters [{DEFAULT_MAX_CHARS}]: ")
        try:
            cap = int(raw) if raw else DEFAULT_MAX_CHARS
        except ValueError:
            self.write("  not a whole number")
            return self.served()
        res = self.api.serve(self.cfg, self.spec, max_chars=cap)
        if self.refused(res):
            return False
        self.doc = res["doc"]
        self.write(f"  served: {three_state(res['state'], res.get('why', ''))}")
        return True

    def chain(self, task: str) -> None:
        res = self.api.escalate(self.cfg, task, piece_chars=self.bot.piece_chars)
        if self.refused(res):
            return
        for p in res.get("pieces", []):
            self.write(
                f"  {p['label']:24} {p['rung']:5} {p['piece'][:12]}  {p['detail']}"
            )
            if p["outcome"] == "answered" and p["rung"] != "d0":
                self.pending += [r for r in p.get("rows") or [] if _is_row(r)]
        self.write(
            f"  answered {res.get('answered', 0)}, escalated {res.get('escalated', 0)}"
        )
        left = [p for p in res.get("pieces", []) if p["outcome"] == "escalated"]
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
                self.write(f"  {tag}: code decided; it goes to the human card")
                continue
            piece = self.piece_for(question, r)
            if piece is None:
                self.write(f"  {tag}: unreachable — the piece isn't in the served file")
                continue
            if self.ask("flowering", f"{tag}: one cloud turn? [y/N] ").lower() != "y":
                continue
            got = self.flower(piece, question)
            self.write(f"  {got['summary']}")
            rows = [x for x in got["rows"] if not _escalates(x)]
            if len(rows) < len(got["rows"]):
                self.write("  the cloud turn escalated: it stays on the human card")
            if rows:
                taken = self.api.take_proposals(self.cfg, rows, bite="flowering")
                if not self.refused(taken):
                    for p in taken["out"].get("proposals", []):
                        if p.get("verdict") == "pass":
                            self.pending.append(p)
                        else:
                            self.write(f"  {p.get('verdict')}: {p.get('reason')}")

    def proposals(self) -> None:
        """Show each pass and leave it pooled: the rows are already on record
        (the chain and ``take_proposals`` wrote them); nothing is sealed here."""
        while self.pending:
            p = self.pending.pop(0)
            subject = p.get("subject") or self.bot.subject(
                {k: p[k] for k in ("path", "data", "cites", "claim")}
            )
            self.write(f"  {p['path']}  cites {len(p['cites'])}  — {p['claim']}")
            data = p["data"] if len(p["data"]) <= 400 else p["data"][:399] + "…"
            self.write("    " + data.replace("\n", "\n    "))
            self.write(f"    pooled: {subject}")

    def checkout(self) -> None:
        res = self.api.checkout(self.cfg)
        if not self.refused(res):
            self.write(res.get("screen", ""))
        self.close_out()

    def close_out(self) -> None:
        """Deposit the pool as Nestor drafts, then make the one seal offer."""
        pool = self.api.pooled(self.cfg)
        items = [p for p in pool.get("pooled") or [] if isinstance(p, dict)]
        if "refused" in pool:
            self.write(f"  pool: unreachable — {pool['refused']}")
            return
        try:
            got = self.deposit(pool)
        except Exception as e:  # noqa: BLE001 - the close-out must not raise
            got = {"state": "unreachable", "reason": f"{type(e).__name__}: {e}"}
        state = got.get("state")
        if state != "populated":
            self.write(f"  deposit: {three_state(state, got.get('reason', ''))}")
            if state != "empty":  # nothing went in; show what is pooled
                for p in items:
                    self.write(f"    pooled, not deposited: {p.get('subject')}")
            return
        drafts = got.get("deposited") or []
        self.write(f"  deposit: populated — {len(drafts)} in Nestor as drafts")
        for d in drafts:
            if d.get("status") == "error":
                self.write(f"    {d.get('subject')}  ERROR: {d.get('error')}")
            else:
                self.write(f"    {d.get('subject')}  {d.get('status')}")
        self.write(f"  seal ↗ {NESTOR_UI}  (the only place a seal is made)")

    def run(self) -> int:
        try:
            if not self.checkin():
                return 1
        except (EOFError, KeyboardInterrupt):
            return 1
        try:
            if self.scope() and self.served():
                while task := self.ask("chain", "task (empty to check out): "):
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
    return Seat(bot, config(bot, root)).run()


if __name__ == "__main__":
    sys.exit(main())
