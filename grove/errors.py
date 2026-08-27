# b17: WGRV1 ΔΣ=42
"""Grove's bounded error vocabulary.

The three-state contract (INVARIANTS.md §1) says every reader returns
EITHER a value with a bounded shape (populated OR empty) OR raises
``Unreachable`` — a distinct sentinel that a caller / endpoint / Web
Component can render as its own state, never collapsed into "empty".

The premise doc's D7 ("absence is a state, not a failure") was widely
misread as "empty-on-failure is acceptable". INVARIANTS.md §2 supersedes
that reading: absence is a state AND rendering it distinctly is required.
This module is the tiny surface every reader agrees on so the endpoint
layer can translate a raised ``Unreachable`` into a ``503 +
{"state": "unreachable", "reason": ...}`` payload without guessing.

Sync only, no threading — an exception is the vocabulary the readers
already know how to raise. See ``docs/INVARIANTS.md §1``.
"""
from __future__ import annotations


class Unreachable(Exception):
    """A reader could not reach its source. See docs/INVARIANTS.md §1.

    ``reason`` is a short human-readable phrase the endpoint hands to the
    client verbatim as the ``"reason"`` field of the 503 payload. It is
    the operator's evidence — keep it factual (what path was probed, what
    env var was unset), not paraphrase.
    """

    def __init__(self, reason: str) -> None:
        super().__init__(reason)
        self.reason = reason


__all__ = ["Unreachable"]
