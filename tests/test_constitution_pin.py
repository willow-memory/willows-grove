"""governance/CONSTITUTION.md is a pinned copy of the law, never edited here.

The law's home is willow-memory/Willow, where it is amended and always a
draft (VIII.4). governance/constitution.pin names the commit and the sha256 of
the bytes copied from it; this test fails if the copy and the pin disagree,
so a correction made here instead of there fails, and so does a re-pin that
moves one without the other.
"""

import hashlib
import json
import re
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent
_COPY = _REPO_ROOT / "governance" / "CONSTITUTION.md"
_PIN = _REPO_ROOT / "governance" / "constitution.pin"


def _pin() -> dict:
    return json.loads(_PIN.read_text(encoding="utf-8"))


def _holds(copy: bytes, pin: dict) -> bool:
    return hashlib.sha256(copy).hexdigest() == pin["sha256"]


def test_the_pin_names_the_laws_home_a_commit_and_a_hash():
    pin = _pin()
    assert pin["repo"] == "willow-memory/Willow" and pin["path"] == "CONSTITUTION.md"
    assert re.fullmatch(r"[0-9a-f]{40}", pin["commit"]), pin["commit"]
    assert re.fullmatch(r"[0-9a-f]{64}", pin["sha256"]), pin["sha256"]


def test_the_copy_is_the_pinned_bytes():
    assert _holds(_COPY.read_bytes(), _pin()), (
        "governance/CONSTITUTION.md isn't the bytes constitution.pin names: "
        "correct the law in willow-memory/Willow, then re-pin both together"
    )


def test_one_byte_changed_here_breaks_the_pin():
    """The gate can fail: an edit made in grove's copy is refused."""
    copy = _COPY.read_bytes()
    assert not _holds(copy.replace(b"Always a draft", b"Always a drafT", 1), _pin())
    assert not _holds(copy + b"\n", _pin())
