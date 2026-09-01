# b17: WGRV1 ΔΣ=42
"""tests/test_mock_willow_mcp_surface.py — the mock may not outrun upstream.

``tests/e2e_willow_mcp/mock_willow_mcp.py`` stands in for willow-mcp so
Grove's C11 loop can be pinned in CI without the real server. A mock is
only worth its green if the thing it imitates exists: the moment it
serves a tool willow-mcp does not have, the suite stops testing a seam
and starts testing the mock's imagination.

That had happened. ``kb_journal_read`` is routed here and appears
**zero times** in willow-mcp — not as a tool, not in its docs. Both of
Grove's read paths look for it (``grove/journal_reader.py:188`` by
``getattr``, then ``POST {WILLOW_MCP_URL}/tools/kb_journal_read``), so
the read-back suite has been green against a tool that was never built,
while the same call against real willow-mcp raises ``Unreachable``.
Grove's own docstring says Gate 5 will land it upstream; nothing
reported that it still had not. Issue #16.

The obvious pin — *every mock route must exist upstream* — would be
born failing, because the divergence is real and outside this
repository's control. A pin that cannot pass is not a pin; it gets
skipped, marked xfail, or deleted, and the gap goes back to being
invisible. That is the failure this repo has now fixed four times.

So the divergence is **enumerated instead of excused**, in
``_PENDING_UPSTREAM``, and the pin fails in *both* directions:

* a mock route that is neither upstream nor listed → **new drift**, fail;
* a listed name that turns up upstream → **the dependency landed**, fail,
  with instructions to strike it from the list.

The second is the important half. It makes the allowance self-retiring:
when Gate 5 ships ``kb_journal_read``, this test tells someone the
read-back suite has become a real test and the note can go. An
allowance that never expires is just an excuse with better manners.

``ToolSurfaceTests`` needs the real ``willow_mcp`` importable and skips
without it — CI runs the mock suite deliberately without upstream
installed, so that absence is an environment fact, not a defect being
waved through. ``MockRouteInventoryTests`` needs nothing but the mock
and runs everywhere; it carries the drift-catching load in every
environment, so the skip above can never hide a new route.

Routes are read from the live ``build_app()`` object rather than grepped
out of the source, so the pin sees what Starlette actually serves.
"""
from __future__ import annotations

import importlib.util
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MOCK_DIR = os.path.join(ROOT, "tests", "e2e_willow_mcp")
for _p in (ROOT, MOCK_DIR):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import mock_willow_mcp

#: MCP tool names the mock registers. Everything else the mock serves
#: (`/health`, `/kill`, `/restore`, `/reset`) is harness control surface
#: with no upstream counterpart and is deliberately out of scope.
_EXPECTED_TOOL_NAMES = frozenset({"kb_journal", "kb_journal_read"})

#: Tool routes the mock serves that willow-mcp does not implement yet,
#: each with the reason it is tolerated. Not a general escape hatch: the
#: test asserts these are STILL missing upstream, so the entry deletes
#: itself the day the dependency lands.
_PENDING_UPSTREAM: dict[str, str] = {}


def _tool_names() -> set[str]:
    """Tool names the mock actually registers."""
    return set(mock_willow_mcp.tool_names())


class MockRouteInventoryTests(unittest.TestCase):
    """Runs everywhere. Catches a new mock route with no upstream review."""

    def test_the_audit_actually_finds_tools(self) -> None:
        names = _tool_names()
        self.assertTrue(
            names,
            "found no MCP tools on mock_willow_mcp — the inventory has "
            "stopped matching and this file is no longer auditing anything",
        )

    def test_tool_names_are_exactly_the_expected_set(self) -> None:
        self.assertEqual(
            _tool_names(), set(_EXPECTED_TOOL_NAMES),
            "the mock's tool surface changed. Adding a tool here means the "
            "C11 suite starts asserting a contract — check it exists in "
            "willow-mcp first, then update _EXPECTED_TOOL_NAMES (and "
            "_PENDING_UPSTREAM if it does not exist yet).",
        )

    def test_every_pending_entry_is_a_tool_we_actually_serve(self) -> None:
        stale = sorted(set(_PENDING_UPSTREAM) - _tool_names())
        self.assertEqual(
            stale, [],
            f"_PENDING_UPSTREAM names tools the mock no longer serves: {stale}",
        )


@unittest.skipIf(
    importlib.util.find_spec("willow_mcp") is None,
    "real willow_mcp not installed — CI runs the mock suite without upstream "
    "on purpose. MockRouteInventoryTests above runs everywhere and is what "
    "catches a new route; this class adds the upstream comparison when the "
    "package happens to be present (pip install -e ../willow-mcp).",
)
class ToolSurfaceTests(unittest.TestCase):
    """Compares the mock's tool surface against the installed willow-mcp."""

    def setUp(self) -> None:
        from willow_mcp import server as wms

        self.upstream = wms

    def test_non_pending_tools_exist_upstream(self) -> None:
        missing = sorted(
            name for name in _tool_names() - set(_PENDING_UPSTREAM)
            if not hasattr(self.upstream, name)
        )
        self.assertEqual(
            missing, [],
            "the mock serves MCP tools willow-mcp does not implement, and "
            "they are not recorded in _PENDING_UPSTREAM. The C11 suite would "
            f"go green against contracts nothing upstream honours: {missing}",
        )

    def test_pending_entries_have_not_landed_yet(self) -> None:
        """Self-retiring. When the dependency ships, this fails on purpose.

        Deleting the entry is the whole fix: the read-back suite stops
        being a protocol test and becomes evidence the seam works.
        """
        landed = sorted(
            name for name in _PENDING_UPSTREAM if hasattr(self.upstream, name)
        )
        self.assertEqual(
            landed, [],
            f"{landed} now exists in willow-mcp — the dependency landed. "
            "Remove it from _PENDING_UPSTREAM, drop the pending note from "
            "tests/e2e_willow_mcp/conftest.py, and close GAP-007: the C11 "
            "read-back suite is a real end-to-end test now.",
        )


if __name__ == "__main__":
    unittest.main()
