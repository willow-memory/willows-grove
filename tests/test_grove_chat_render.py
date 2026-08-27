"""tests/test_grove_chat_render.py — pin INVARIANTS.md §1 at the
`web/components/grove-chat.js` render layer.

Loki finding M11-grove_chat-empty-state-persists (Grove v0.9 PR 12
audit): the RIGHT column of `<grove-chat>` initialized its shadow DOM
with a literal ``no messages yet`` placeholder BEFORE
``/api/journal/recent`` was consulted, and ``_pollReadback`` set the
unreachable banner without removing that placeholder. Both states
therefore shared the placeholder pixel — the exact collapse
INVARIANTS.md §1 forbids ("empty and unreachable render distinctly").

These tests grep the component source. They MUST fail on the unfixed
code and pass once the fix lands.
"""

import pathlib
import re

COMPONENT = (
    pathlib.Path(__file__).resolve().parents[1]
    / "web"
    / "components"
    / "grove-chat.js"
)


def _method_body(source: str, name: str) -> str:
    """Return the ``{ … }`` body of a class method whose declaration line
    begins with ``<name>(`` (optionally prefixed by ``async``), matched
    at the two-space class-body indent so call sites don't fool the
    search.
    """
    pattern = rf"\n  (?:async\s+)?{re.escape(name)}\s*\("
    m = re.search(pattern, source)
    assert m, f"method {name!r} not found as a class-body declaration"
    brace = source.index("{", m.end())
    depth = 0
    for i in range(brace, len(source)):
        ch = source[i]
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return source[brace : i + 1]
    raise AssertionError(f"couldn't close method body of {name!r}")


def test_initial_render_has_no_empty_state_pixel():
    """(a) The initial ``_render()`` must not seed the RIGHT column with
    the empty-state ``no messages yet`` pixel. Before the first poll
    returns, the state is unknown — a loading placeholder is correct,
    the empty pixel is not (INVARIANTS.md §1: an unreached surface must
    not read as "there is nothing there").
    """
    src = COMPONENT.read_text(encoding="utf-8")
    body = _method_body(src, "_render")
    assert "no messages yet" not in body.lower(), (
        "grove-chat._render() seeds the RIGHT column with the "
        "'no messages yet' placeholder BEFORE /api/journal/recent is "
        "consulted. The initial paint must be a distinct loading "
        "affordance — the empty pixel belongs to the reached-but-empty "
        "state alone (INVARIANTS.md §1)."
    )


def test_unreachable_branch_clears_empty_state_div():
    """(b) On the unreachable branch, the render code must clear any
    empty-state div so the amber ``read-back unreachable`` banner is
    the only content — the two states never share a pixel.

    Concretely: ``_pollReadback`` must not call the bare
    ``_setReadbackStatus("unreachable", …)`` (that setter only touches
    the banner element); it must dispatch through a helper whose body
    both sets the unreachable state AND removes ``.readback-empty``.
    """
    src = COMPONENT.read_text(encoding="utf-8")
    poll = _method_body(src, "_pollReadback")

    assert '_setReadbackStatus("unreachable"' not in poll, (
        "grove-chat._pollReadback calls _setReadbackStatus(\"unreachable\", "
        "...) directly. That setter only touches the amber banner element "
        "and cannot clear the .readback-empty placeholder, so the "
        "unreachable banner ends up sharing a pixel with the empty state. "
        "Route the branch through a helper that removes the placeholder "
        "before painting the banner (INVARIANTS.md §1)."
    )
    assert "_setReadbackStatus('unreachable'" not in poll, (
        "same as above (single-quoted form)."
    )

    helpers = set(re.findall(r"this\.(_[A-Za-z]+)\(", poll))
    for helper in helpers:
        try:
            hbody = _method_body(src, helper)
        except AssertionError:
            continue
        if "unreachable" in hbody and "readback-empty" in hbody:
            return
    raise AssertionError(
        "no method invoked by grove-chat._pollReadback both sets the "
        "unreachable state AND removes the .readback-empty div. The "
        "unreachable branch must clear the empty-state placeholder so "
        "the banner is the only content on the RIGHT column "
        "(INVARIANTS.md §1)."
    )
