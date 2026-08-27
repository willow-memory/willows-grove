"""grove_html.py — proof-of-life HTML for Willow's Grove served page.
b17: WGRV1  ΔΣ=42

This is the placeholder body served by `grove_serve.py` on 127.0.0.1:8766.
The premise doc (`docs/design/willow-grove-premise.md`, D9) pins the front
end as vanilla JS + Web Components + no build step. This first pass is
static — no JS — so the very first thing the operator sees when the serve
scaffold is stood up is a page that says "the grove is here" over the same
willow ASCII the rest of the fleet already knows from `widgets/hero.py`.

The tree pose is `widgets/hero.py`'s pose "C" frame 4 (`render_frame("C", 4)`
at rest — center trunk, mid-swing pendulum position). Inlined verbatim
rather than imported so this module has no `textual` dependency; if the
frame text in `widgets/hero.py` ever changes the drift is caught by
`tests/test_grove_serve.py` re-reading the file at some later pass.

D4 (served HTML on 127.0.0.1) is the pattern this joins:
`willow-mcp/src/willow_mcp/gates_serve.py` — same shape, different port.
"""
from __future__ import annotations


# Pose "C" frame 4 from widgets/hero.py — the tree at rest, center-swing.
# 6 lines: crown_top, crown_mid[C][4], crown_base[4],
#          POSES[C][4], POSES[C][8], POSES[C][9].
_WILLOW_C4: tuple[str, ...] = (
    "ƒƒ  * . * . *   ",
    "ƒ ƒ . ƒ . ƒ . ƒ ",
    "ƒ ƒ  (║ . .) ƒ  ",
    "ƒ  ƒ  ║  ƒ  ƒ   ",
    "ƒ     ║ƒ    ƒ  ƒ",
    "ƒ     ║ƒ     ƒ  ",
)


_CSS = """
  :root {
    /* dark warm background — the fleet's evening desk, not a cold monitor */
    --bg: #1a140f;
    --bg-soft: #241a12;
    --border: #3a2c1f;
    --text: #efe6d8;
    --muted: #a3927a;
    --frond: #7fb069;
    --frond-glow: #a8d18a;
    --trunk: #c9a074;
    --accent: #d4a373;
  }
  * { box-sizing: border-box; }
  html, body { height: 100%; }
  body {
    margin: 0;
    background: var(--bg);
    color: var(--text);
    font: 14px/1.5 -apple-system, BlinkMacSystemFont, "Segoe UI",
          "Helvetica Neue", sans-serif;
    display: flex;
    flex-direction: column;
    min-height: 100vh;
  }
  .strip {
    display: flex;
    align-items: center;
    gap: .6rem;
    padding: .55rem 1rem;
    background: var(--bg-soft);
    border-bottom: 1px solid var(--border);
    font-size: .78rem;
    color: var(--muted);
    letter-spacing: .02em;
  }
  .strip .dot {
    width: 6px; height: 6px; border-radius: 50%;
    background: var(--frond-glow);
    box-shadow: 0 0 6px var(--frond-glow);
    flex-shrink: 0;
  }
  .strip .name { color: var(--text); font-weight: 600; }
  main {
    flex: 1;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 3rem 1rem;
    gap: 2rem;
  }
  pre.tree {
    margin: 0;
    font-family: "SFMono-Regular", ui-monospace, Menlo, Consolas, monospace;
    font-size: 1.05rem;
    line-height: 1.15;
    color: var(--frond);
    text-shadow: 0 0 4px rgba(127, 176, 105, .18);
    white-space: pre;
    opacity: .78;
    letter-spacing: .02em;
  }
  .here {
    margin: 0;
    font-size: 1.35rem;
    color: var(--text);
    letter-spacing: .01em;
    font-weight: 400;
  }
  footer {
    padding: .55rem 1rem;
    background: var(--bg-soft);
    border-top: 1px solid var(--border);
    font-size: .72rem;
    color: var(--muted);
    letter-spacing: .04em;
    font-family: "SFMono-Regular", ui-monospace, Menlo, Consolas, monospace;
    text-align: center;
  }
"""


_TOP_STRIP = (
    '<div class="strip">'
    '<span class="dot"></span>'
    '<span class="name">ƒ willow</span>'
    '<span>·</span>'
    '<span>standing</span>'
    '<span>·</span>'
    '<span>grove stable</span>'
    '</div>'
)


_FOOTER = (
    '<footer>'
    'grove.willow_20 · 127.0.0.1:8766 · b17: WGRV1 ΔΣ=42'
    '</footer>'
)


def _tree_block() -> str:
    """Pose C frame 4, wrapped in a <pre>. Static — no JS, no animation."""
    body = "\n".join(_WILLOW_C4)
    return f'<pre class="tree" aria-hidden="true">{body}</pre>'


def render_page() -> str:
    """Full HTML document for `GET /`.

    Proof-of-life: dark warm background, the willow tree at rest, an ambient
    top strip, and a footer. No JS. This is the "the grove is here" moment
    before any card, chip, or persona shows up.
    """
    return (
        "<!doctype html>\n"
        "<html lang=\"en\">\n"
        "<head>\n"
        '<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width,initial-scale=1">\n'
        "<title>willow's grove</title>\n"
        f"<style>{_CSS}</style>\n"
        # C11 chat card (LEFT-side write path). Registered here as an ES module
        # so ``<grove-chat>`` upgrades in place. The RIGHT-side read-back is a
        # follow-up PR (resident-watcher work). Additive only — no existing
        # markup is moved or reshaped.
        '<script type="module" src="/web/components/grove-chat.js"></script>\n'
        "</head>\n"
        "<body>\n"
        f"{_TOP_STRIP}\n"
        "<main>\n"
        f"  {_tree_block()}\n"
        '  <p class="here">the grove is here.</p>\n'
        '  <grove-chat home-edge="bottom"></grove-chat>\n'
        "</main>\n"
        f"{_FOOTER}\n"
        "</body>\n"
        "</html>\n"
    )
