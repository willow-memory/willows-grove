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
  /* INVARIANTS.md §1 at the visual layer: a seat that answered and a
     seat that did not must not paint the same pixels. The dot carries
     the distinction alongside the wording. */
  .strip[data-standing-state="loading"] .dot {
    background: var(--muted);
    box-shadow: none;
    opacity: .5;
  }
  .strip[data-standing-state="unreachable"] .dot {
    background: transparent;
    box-shadow: none;
    border: 1px solid var(--accent);
  }
  .strip[data-standing-state="unreachable"] .standing { color: var(--accent); }
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


# INVARIANTS.md §8 / Constraint 1 (DESIGN_CONSTRAINTS.md): "I could not
# reach the source" must never collapse into "there is nothing there."
# This strip used to render "standing" / "grove stable" as static
# markup — no endpoint, no state check — so the operator read "grove
# stable" whether or not any seam was reachable. It then carried a
# permanent neutral placeholder, which was honest but told the operator
# nothing in either direction. ``/web/boot/standing-boot.js`` now polls
# ``GET /health`` and paints the slot below: "seat live · <sha>" when
# the seat answers, "seat unreachable — <why>" when it does not. The
# markup here is only the pre-fetch sentinel.
_TOP_STRIP = (
    '<div class="strip" data-standing-state="loading">'
    '<span class="dot"></span>'
    '<span class="name">ƒ willow</span>'
    '<span>·</span>'
    # `data-standing` is the slot ``/web/boot/standing-boot.js`` paints
    # from ``GET /health``. The served markup carries the pre-fetch
    # sentinel so there is no flash of a status claim before the first
    # answer — and so the page still makes no claim if JS never runs.
    '<span class="standing" data-standing>reading standing…</span>'
    '</div>'
)


# Lens switch demoted (Jarvis addendum 2026-09-02 / C12 misfit):
# component file retained under web/components/ for harness or quiet tooling;
# it is NOT mounted in the first viewport. One continuous Jarvis seat —
# brand strip, conversation, priority surface — without a Governance/PM/PA
# gearshift. Optional ?lens= on /api/dispatch remains for quiet filters.
_LENS_SWITCH_REMOVED_FROM_HERO = True  # documentation pin for greppers


# Constitutional / envelope panels — subject is the fleet's grant surface,
# not an operator "Governance mode." Kept as a section wrapper so sibling
# panels can mount without implying a mode switch.
# INVARIANTS.md §8 — the served page consumes /api/envelopes live via
# <grove-envelope-panel>. The `data-source` attribute is set to the live
# endpoint verbatim (not a fixture path); the served page never carries
# an explicit fixture-path data-source per §8.
_CONSTITUTIONAL_PANELS = (
    '<section class="constitutional-panels">'
    '<grove-envelope-panel data-source="/api/envelopes"></grove-envelope-panel>'
    '</section>'
)


# INVARIANTS.md §1 guidance: a component's state event has a page-level
# listener. <grove-persona-registry> dispatches `registry-unreachable`
# (bubbles + composed) when its /api/personas fetch fails. Log the event
# once at info (not error) with a visible marker per the §1 guidance, and
# stamp `body.registry-unreachable` so a follow-up PR can style around it.
# Kept as an inline non-module <script> so it runs at parse time and is
# ready before the persona-registry element upgrades — and so it does
# NOT disturb the `<script type="module" src="…">` ordering that
# `tests/test_grove_html_boot_wire.py::test_boot_script_is_last_module_in_head`
# pins on the layout-memory boot tag.
_REGISTRY_UNREACHABLE_LISTENER = (
    '<script>'
    '(function(){'
    'try{'
    'var logged=false;'
    'window.addEventListener("registry-unreachable",function(ev){'
    'try{'
    'if(!logged){'
    'logged=true;'
    'var reason=(ev&&ev.detail&&ev.detail.reason)||"unknown";'
    'if(window.console&&console.info){'
    'console.info("[grove] registry-unreachable:",reason);'
    '}'
    '}'
    '}catch(_e){}'
    'try{'
    'if(document&&document.body&&document.body.classList){'
    'document.body.classList.add("registry-unreachable");'
    '}'
    '}catch(_e){}'
    '});'
    '}catch(_e){}'
    '})();'
    '</script>'
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
    top strip, chat, dispatch rail, constitutional panels, and a footer —
    one Jarvis composition without an operator mode switch in the first
    viewport (C12 demoted).
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
        '<script type="module" src="/web/components/grove-cast-chip.js"></script>\n'
        '<script type="module" src="/web/components/grove-dispatch-rail.js"></script>\n'
        # D10 unified persona registry: mounted in <head> so the definition is
        # ready before the <body> instance upgrades; the instance itself sits
        # first in <body> so its /api/personas fetch is in flight before every
        # other component connects and reads visual.color / visual.sigil / voice.
        '<script type="module" src="/web/components/grove-persona-registry.js"></script>\n'
        # D11/V5 verbatim refusal chip — registered here so the boot module
        # below can construct one on demand and the element upgrades in place.
        '<script type="module" src="/web/components/grove-refusal-chip.js"></script>\n'
        # Refusal auto-summon boot: listens for the ``nestor-refusal`` window
        # CustomEvent and mounts a <grove-refusal-chip> into #refusal-chip-mount
        # with the verbatim payload. Also exposes ``window.groveNestorAsk``
        # as an operator/console summon path. MUST be loaded after the
        # ``grove-refusal-chip`` component script above so the constructor is
        # defined by the time the boot fires an event.
        '<script type="module" src="/web/boot/refusal-summon-boot.js"></script>\n'
        # INVARIANTS.md §8: the served page consumes /api/envelopes live via
        # <grove-envelope-panel> mounted in the constitutional-panels region.
        # Component module registered here so the tag upgrades on connect.
        '<script type="module" src="/web/components/grove-envelope-panel.js"></script>\n'
        # D12/D14 summonable card primitive. Mounted even though the shell
        # renders no <grove-card> markup of its own: the layout-memory boot
        # below walks the DOM by tag name and cards are summoned at runtime,
        # so `customElements.define("grove-card", …)` has to have run or the
        # primitive is defined in a file nothing on this page ever loads.
        # It was exactly that until now — the only importer in the tree was
        # `web/harness.html`, so layout memory was live under test and inert
        # on the served page, and the ordering guarantee asserted in
        # `layout-memory-boot.js`'s own docstring had nothing behind it.
        '<script type="module" src="/web/components/grove-card.js"></script>\n'
        # INVARIANTS.md §1 page-level listener for `registry-unreachable`
        # (dispatched by <grove-persona-registry>). Inline non-module script
        # so it registers at parse time — before the element upgrades — and
        # so it does NOT participate in the module-src ordering pinned by
        # `tests/test_grove_html_boot_wire.py`.
        f'{_REGISTRY_UNREACHABLE_LISTENER}\n'
        # Ambient-strip standing boot — polls GET /health and paints the
        # top strip's `data-standing` slot with the seat's live state
        # (INVARIANTS.md §1 / §8). Touches only the strip, defines no
        # custom element, so it carries no ordering constraint against
        # the component scripts above; it stays ahead of the layout
        # boot, which `tests/test_grove_html_boot_wire.py` pins as the
        # last module script in <head>.
        '<script type="module" src="/web/boot/standing-boot.js"></script>\n'
        # Layout-memory boot — walks <grove-card id="…"> nodes and wires each
        # to per-viewer localStorage so remembered edge/state persists across
        # reloads, and pinned cards summon on boot (D12 + D14). Ordering
        # matters: this MUST come after every component script above so all
        # ``customElements.define(…)`` calls have run by the time the boot
        # walks the DOM by tag name.
        '<script type="module" src="/web/boot/layout-memory-boot.js"></script>\n'
        "</head>\n"
        "<body>\n"
        '<grove-persona-registry></grove-persona-registry>\n'
        f"{_TOP_STRIP}\n"
        "<main>\n"
        f"  {_tree_block()}\n"
        '  <p class="here">the grove is here.</p>\n'
        '  <grove-chat home-edge="bottom"></grove-chat>\n'
        # Default dispatch rail without operator mode switch (C12 demoted).
        '  <grove-dispatch-rail></grove-dispatch-rail>\n'
        f"  {_CONSTITUTIONAL_PANELS}\n"
        "</main>\n"
        f"{_FOOTER}\n"
        # Mount point for verbatim refusal chips summoned by
        # ``/web/boot/refusal-summon-boot.js`` in response to
        # ``nestor-refusal`` window events (D11/V5).
        '<div id="refusal-chip-mount"></div>\n'
        "</body>\n"
        "</html>\n"
    )
