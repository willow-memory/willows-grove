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

``LedgerWriteFailed`` is the write-side companion (Loki v0.9 finding
#23, Grove v0.9 PR 12): a distinct sentinel the FRANK ledger writer
raises when a tamper-evident append cannot land. Silently swallowing
the failure to stdout was the anti-pattern — the ledger claims
tamper-evidence, so a swallowed write is a lie. Callers that want
best-effort semantics wrap the call in ``try/except LedgerWriteFailed``
at the call site, so the primitive is honest and the policy is local.
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


class LedgerWriteFailed(Exception):
    """A tamper-evident ledger append could not complete.

    Raised by ``grove_db._frank_ledger_append`` when the underlying
    Postgres write fails for any reason — connection refused, statement
    timeout, or (critically) the ``frank_ledger_no_fork`` anti-fork
    guard tripping on the partial unique index. Callers that treat the
    ledger write as best-effort catch this at the call site; the
    primitive itself never swallows.

    See INVARIANTS.md §1 (the write-side analogue) and Loki v0.9
    finding #23.
    """

    def __init__(self, reason: str) -> None:
        super().__init__(reason)
        self.reason = reason


__all__ = ["Unreachable", "LedgerWriteFailed"]
