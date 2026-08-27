# b17: WGRV1 ΔΣ=42
"""Regression pin for Loki finding M8 (Grove v0.9 PR 12).

INVARIANTS.md §1 — the three-state contract — says a reader either returns
a bounded value (populated / empty) OR raises ``grove.errors.Unreachable``.
Reached-but-rejected is *unreachable*, not empty. ``journal_writer`` already
honors that on line 198-200: an in-process ``{"error": ...}`` response from
``willow-mcp`` becomes ``raise Unreachable(str(err))``.

``journal_reader._try_import_read`` disagreed — it silently returned ``[]``
on the same shape, so ``grove_serve._journal_recent`` answered
200 ``{state:empty, atoms:[]}`` for a case that should have surfaced as
503 ``{state:unreachable}``. Writer and reader must agree on the seam.

This file pins two properties:

  1. In-process ``kb_journal_read`` returning ``{"error": ...}`` →
     ``Unreachable`` bubbles out of ``read_recent()``. FAILS on the
     pre-fix code (returns ``[]``).
  2. In-process ``kb_journal_read`` returning ``[]`` → ``read_recent()``
     returns ``[]``. Guards against a fix that over-widens the raise
     into the honest-empty case.

Monkeypatch shape mirrors ``tests/test_journal_reader.py``'s
``test_direct_import_path_when_present`` — install a fake ``willow_mcp``
package + ``willow_mcp.server`` module via ``patch.dict(sys.modules, ...)``,
so the reader's ``from willow_mcp import server`` import lands on our fake
and ``getattr(_wms, "kb_journal_read")`` returns our stub.

Sync ``unittest`` — no pytest-specific constructs — matching the sibling
tests in this directory.
"""
from __future__ import annotations

import os
import sys
import types
import unittest
from unittest.mock import patch


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from grove import journal_reader  # noqa: E402
from grove.errors import Unreachable  # noqa: E402


def _install_fake_willow_mcp(kb_journal_read):
    """Build a fake ``willow_mcp`` package that exposes ``kb_journal_read``.

    Returned as a ``patch.dict(sys.modules, ...)`` context manager — the
    caller uses it under ``with`` so the fake is scoped to the test.
    """
    fake_server = types.ModuleType("willow_mcp.server")
    fake_server.kb_journal_read = kb_journal_read  # type: ignore[attr-defined]
    fake_pkg = types.ModuleType("willow_mcp")
    fake_pkg.server = fake_server  # type: ignore[attr-defined]
    return patch.dict(
        sys.modules,
        {"willow_mcp": fake_pkg, "willow_mcp.server": fake_server},
    )


class JournalReaderInProcessErrorTests(unittest.TestCase):
    """INVARIANTS.md §1 pin: reached-but-rejected → Unreachable, not empty."""

    def setUp(self) -> None:
        journal_reader._reset_log_once_for_tests()
        # No WILLOW_MCP_URL — keep the HTTP fallback out of the picture so
        # the assertion is strictly about the in-process branch.
        self._saved_url = os.environ.pop("WILLOW_MCP_URL", None)

    def tearDown(self) -> None:
        if self._saved_url is not None:
            os.environ["WILLOW_MCP_URL"] = self._saved_url

    def test_in_process_error_shape_raises_unreachable(self) -> None:
        """Finding M8: ``{"error": ...}`` in-process must NOT become ``[]``.

        Mirrors ``journal_writer.py:198-200``. This is the case that fails
        on the pre-fix code: ``_try_import_read`` returns ``[]``, so
        ``read_recent()`` returns ``[]`` and the caller reads it as the
        honest-empty state instead of the reached-but-rejected state.
        """
        calls: list[dict] = []

        def _fake_kb_journal_read(app_id, limit=50, since_id=None):  # noqa: ARG001
            calls.append({"app_id": app_id, "limit": limit, "since_id": since_id})
            return {"error": "sim"}

        with _install_fake_willow_mcp(_fake_kb_journal_read):
            with self.assertRaises(Unreachable) as ctx:
                journal_reader.read_recent()

        # The in-process branch was actually taken (we're not accidentally
        # asserting the (c) no-backend Unreachable).
        self.assertEqual(len(calls), 1)
        # And the reason surfaces the willow-mcp error string — same
        # discipline as journal_writer.
        self.assertIn("sim", ctx.exception.reason)

    def test_in_process_empty_list_returns_empty_list(self) -> None:
        """Guard against over-widening: an honest empty read is still empty.

        ``list`` with zero atoms means willow-mcp was reached and had
        nothing new to report — that is the "empty" §1 state, distinct
        from Unreachable. This test locks the distinction so a future
        fix that raises on "anything not shaped like a populated list"
        cannot pass.
        """
        def _fake_kb_journal_read(app_id, limit=50, since_id=None):  # noqa: ARG001
            return []

        with _install_fake_willow_mcp(_fake_kb_journal_read):
            result = journal_reader.read_recent()

        self.assertEqual(result, [])


if __name__ == "__main__":
    unittest.main()
