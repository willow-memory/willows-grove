"""4 gate — the doors. Every change passes here; every gate fails closed and loud.

Cites: CONST-III (default-deny; standing grants), CONST-II, §0.2, §0.3, CONST-V.2,
App. B (the probes boot runs against this module).

A change is PR-shaped: it says what it Cites, what it Amends, or None, because...
"The law" is the fixed half (the constitution's Trace IDs) plus the user's half
(grants, precedents, sealed rows). Python checks that a citation exists, is
known, and matches what the change touches. Whether it is *true* is a witness's
job, and only the human's seal makes it so.
"""

from __future__ import annotations

import hashlib
import hmac
import sys
from dataclasses import dataclass, field
from pathlib import Path

from .record import Verified

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts" / "scan"))
import script_match as sm  # noqa: E402  (adopt, don't rewrite: checks 1-4 live there)

_TOKEN = object()  # the only key that mints a Verified; the record checks for it
HUMAN = "human"


class Refused(Exception):
    """A closed door. The reason is written down; nothing is guessed."""


@dataclass
class Decision:
    verdict: str  # pass | flagged | awaiting_seal | awaiting_grant | refused
    reason: str = ""
    card: dict = field(default_factory=dict)  # a grant or seal card, when one is needed
    match: dict = field(default_factory=dict)  # a script-match result, when relevant


def token() -> object:
    return _TOKEN


def sign(key: bytes, *parts: str) -> str:
    return hmac.new(key, "\x1f".join(parts).encode(), hashlib.sha256).hexdigest()


def verify(identity: dict, keys: dict[str, bytes]) -> Verified:
    """Box 2. The name and family are claims; the signature is the key."""
    who, family, sig = (
        identity.get("who"),
        identity.get("family", ""),
        identity.get("sig", ""),
    )
    key = keys.get(who or "")
    if key is None or not hmac.compare_digest(sign(key, who, family), sig):
        raise Refused(f"unsigned agent at the door: {who!r}")
    if who == HUMAN:
        raise Refused(
            "the human seat is not entered by signature; it is a key in a hand"
        )
    return Verified(who, family, _TOKEN)


def system() -> Verified:
    """The run itself, for the rows it writes about its own steps."""
    return Verified("run", "python", _TOKEN)


def verify_seal(subject: str, proof: str, human_key: bytes) -> bool:
    """Only the human's key produces this. Presence is a label; this is authority."""
    return hmac.compare_digest(sign(human_key, "seal", subject), proof)


def human(subject: str, proof: str, human_key: bytes) -> Verified:
    """The one way a 'human' stamp exists: a seal proof the human's key made."""
    if not verify_seal(subject, proof, human_key):
        raise Refused("seal proof does not verify; presence is a label, not a key")
    return Verified(HUMAN, HUMAN, _TOKEN)


def door(change: dict, law: dict, index: list[dict] | None = None) -> Decision:
    """Fail closed: any defect in the change, or in this function, is a refusal."""
    try:
        return _door(change, law, index or [])
    except Refused as e:
        return Decision("refused", str(e))
    except Exception as e:  # a gate that can't think clearly doesn't guess
        return Decision(
            "refused", f"gate error, failing closed: {type(e).__name__}: {e}"
        )


def _door(change: dict, law: dict, index: list[dict]) -> Decision:
    kind = change["kind"]
    known = set(law["trace_ids"]) | set(law.get("user_rules", []))

    if change.get("standing") in ("sealed", "witnessed") or kind == "seal":
        raise Refused("a seal or a standing cannot be awarded through the door (§0.2)")

    cites, amends = change.get("cites", []), change.get("amends", [])
    because = (change.get("none_because") or "").strip()
    if not cites and not amends and not because:
        raise Refused("cites nothing and says nothing about why")
    unknown = sorted(set(cites + amends) - known)
    if unknown:
        raise Refused(f"cites unknown law: {unknown}")

    if kind == "law" or amends:
        return Decision(
            "awaiting_seal",
            "changes the law; only the human's key can seal it",
            card={"what": change.get("what", ""), "amends": amends or ["(law file)"]},
        )

    if kind == "egress":
        grant = next(
            (
                g
                for g in law.get("grants", [])
                if g["who"] == change["who"] and g["where"] == change["where"]
            ),
            None,
        )
        if grant is None:
            return Decision(
                "awaiting_grant",
                "outbound, and no standing grant covers it",
                card={k: change.get(k) for k in ("who", "what", "where", "bytes")},
            )

    touches = set(change.get("touches", []))
    if touches and cites and not (touches & set(cites)):
        return Decision(
            "flagged", f"cites {sorted(cites)} but touches {sorted(touches)}"
        )

    if kind == "script":
        e = sm.entry(
            change["source"], change.get("label", "script"), change.get("name")
        )
        e = sm.match(index + [e])[-1]
        small = len(e.get("features", ())) < law.get("min_features", 6)
        if (
            e["verdict"] == "similar" and small
        ):  # tonight's finding: small scripts over-group
            e["verdict"], e["of"] = "new", None
        if e["verdict"] != "new":
            return Decision(
                "flagged",
                f"{e['verdict']} of index[{e['of']}]: use it, extend it, "
                f"or write new and say why",
                match=e,
            )
        return Decision("pass", match=e)

    return Decision("pass")
