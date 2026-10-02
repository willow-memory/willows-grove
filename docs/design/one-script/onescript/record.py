"""3 record — append-only rows, the stamp, pile pointers.

Cites: CONST-VI (append and read; content inviolable), §0.5.

The record is the reference. Everything else is a view of it or a check on it.
Every row is stamped here, at the door, never by the thing that produced it:
who (an identity the gate verified), standing (always "unattested" on write),
the run's own version, the turn, and the time from the injected clock. Rows are
hash-chained, so an edit to a past row breaks every hash after it.
"""

from __future__ import annotations

import hashlib
import json
import os
import tempfile
from pathlib import Path
from typing import Callable

GENESIS = "0" * 16


def canon(obj) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def h16(data: bytes | str) -> str:
    return hashlib.sha256(
        data if isinstance(data, bytes) else data.encode()
    ).hexdigest()[:16]


def version_of(pkg_dir: Path) -> str:
    """The run's own version: one hash over every .py file in the package, in order."""
    files = sorted(p for p in pkg_dir.glob("*.py"))
    return h16(b"".join(p.name.encode() + b"\0" + p.read_bytes() for p in files))


class Verified:
    """An identity the gate checked. Only gate.verify() makes one."""

    __slots__ = ("who", "family", "_token")

    def __init__(self, who: str, family: str, token: object):
        self.who, self.family, self._token = who, family, token


class Record:
    def __init__(
        self, box: Path, clock: Callable[[], str], version: str, token: object
    ):
        self.box, self.clock, self.version, self._token = box, clock, version, token
        self.path = box / "record.jsonl"
        self.pile_path = box / "pile.json"
        box.mkdir(parents=True, exist_ok=True)

    # ── rows ────────────────────────────────────────────────────────────────
    def rows(self) -> list[dict]:
        if not self.path.exists():
            return []
        return [json.loads(x) for x in self.path.read_text().splitlines() if x.strip()]

    def append(self, kind: str, who: Verified, **fields) -> dict:
        if not isinstance(who, Verified) or who._token is not self._token:
            raise PermissionError(
                "record: unverified identity; the stamp comes from the gate"
            )
        rows = self.rows()
        row = {
            "n": len(rows),
            "kind": kind,
            "who": who.who,
            "family": who.family,
            "standing": "sealed"
            if (kind == "seal" and who.who == "human")
            else "unattested",
            "version": self.version,
            "ts": self.clock(),
            "prev": rows[-1]["hash"] if rows else GENESIS,
            **fields,
        }
        row["hash"] = h16(canon(row))
        with self.path.open("a", encoding="utf-8") as f:
            f.write(canon(row) + "\n")
            f.flush()
            os.fsync(f.fileno())
        return row

    def verify_chain(self) -> list[str]:
        """Every break, by row number. Empty means the chain holds."""
        breaks, prev = [], GENESIS
        for row in self.rows():
            body = {k: v for k, v in row.items() if k != "hash"}
            if row.get("prev") != prev or h16(canon(body)) != row.get("hash"):
                breaks.append(f"row {row.get('n')}: chain broken")
            prev = row.get("hash")
        return breaks

    # ── turns: a crash leaves an open row, not a gap ─────────────────────────
    def open_turn(self, who: Verified, turn: int, intent: str) -> dict:
        return self.append("turn_open", who, turn=turn, intent=intent)

    def close_turn(self, who: Verified, turn: int) -> dict:
        return self.append("turn_close", who, turn=turn)

    # ── files: every write adds its own pointer ──────────────────────────────
    def pile(self) -> dict:
        if not self.pile_path.exists():
            return {"items": []}
        return json.loads(self.pile_path.read_text())

    def _save_pile(self, pile: dict) -> None:
        pile["items"].sort(key=lambda i: i["where"])
        _atomic(
            self.pile_path, (json.dumps(pile, indent=1, sort_keys=True) + "\n").encode()
        )

    def write_file(
        self,
        who: Verified,
        rel: str,
        data: bytes,
        *,
        live: bool = False,
        expect_vanish: bool = False,
        cites: list[str] | None = None,
        provenance: str = "unknown",
    ) -> dict:
        """`provenance` is where the bytes came from: authored, transcript,
        memory or third-party. It's stamped at write time so a push never has
        to guess it; "unknown" never leaves the box (gate.push_card)."""
        if rel.startswith(("/tmp", "tmp/")) and not expect_vanish:
            raise PermissionError(
                f"record: '{rel}' is temp; nothing kept is written to temp"
            )
        target = self.box / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        _atomic(target, data)
        ptr = {
            "where": rel,
            "sha": h16(data),
            "bytes": len(data),
            "provenance": provenance,
        }
        if live:
            ptr["live"] = True
        if expect_vanish:
            ptr["expect_vanish"] = True
        pile = self.pile()
        pile["items"] = [i for i in pile["items"] if i["where"] != rel] + [ptr]
        self._save_pile(pile)
        return self.append("write", who, path=rel, sha=ptr["sha"], cites=cites or [])


def _atomic(path: Path, data: bytes) -> None:
    """Never a half-written file, and readable like any other file (0644)."""
    fd, tmp = tempfile.mkstemp(dir=path.parent, suffix=".tmp")
    with os.fdopen(fd, "wb") as f:
        f.write(data)
        f.flush()
        os.fsync(f.fileno())
    os.chmod(tmp, 0o644)
    os.replace(tmp, path)
