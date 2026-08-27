# b17: WGRV1 ΔΣ=42
"""HTML string builders for the `/seed/` six-movement onboarding route (D16).

D16 seals: the six-part story *IS* the human onboarding. INVARIANTS.md §9
adds the render-side discipline: no content is invented here at render
time — the movement bodies flow through this module verbatim (HTML-
escaped), and the stub-on-absence path exists only so /seed/ is proof
of life when the fleet_charter mirror is not mounted. This module
renders each movement — and the landing index — as a server-side page
that shares `grove_html.py`'s dark-warm desk palette. There is no JS
here; the seed pages are static HTML by design (they are the human
onboarding, not an API, so they must survive a browser without JS and
they must never route through a Web Component the story does not need).

Two entry points:

* :func:`render_seed_index` — the ``/seed/`` landing page with six
  chapter cards, each linking to ``/seed/<n>``.
* :func:`render_seed_movement` — one movement page with the body
  rendered from Markdown, plus prev/next nav.

The Markdown renderer is stdlib-only — a small, escape-first handler
for headings, paragraphs, bold, italic, inline code, links, and lists.
It is *not* a full CommonMark implementation; it is enough to render
the charter's chapter files legibly. Escaping is unconditional so a
future non-local seed source cannot inject HTML through the route.
"""
from __future__ import annotations

import html
import re
from typing import Any, Iterable


# ── Shared style block ───────────────────────────────────────────────────────
# Mirrors grove_html.py's palette + type. Kept local so `/seed/` renders
# even if `grove_html.py` is later refactored — the seed pages are their
# own surface (D16), not a subview of the dispatch page.
_CSS = """
  :root {
    --bg: #1a140f;
    --bg-soft: #241a12;
    --bg-card: #2a1e14;
    --border: #3a2c1f;
    --border-hover: #6b4d33;
    --text: #efe6d8;
    --muted: #a3927a;
    --frond: #7fb069;
    --frond-glow: #a8d18a;
    --trunk: #c9a074;
    --accent: #d4a373;
    --link: #d4a373;
    --link-hover: #efe6d8;
  }
  * { box-sizing: border-box; }
  html, body { height: 100%; }
  body {
    margin: 0;
    background: var(--bg);
    color: var(--text);
    font: 15px/1.55 -apple-system, BlinkMacSystemFont, "Segoe UI",
          "Helvetica Neue", sans-serif;
    display: flex;
    flex-direction: column;
    min-height: 100vh;
  }
  header.strip {
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
  header.strip .dot {
    width: 6px; height: 6px; border-radius: 50%;
    background: var(--frond-glow);
    box-shadow: 0 0 6px var(--frond-glow);
    flex-shrink: 0;
  }
  header.strip .name { color: var(--text); font-weight: 600; }
  header.strip .grow { flex: 1; }
  header.strip a { color: var(--link); text-decoration: none; }
  header.strip a:hover { color: var(--link-hover); }
  main {
    flex: 1;
    padding: 2.5rem 1.5rem 3rem;
    max-width: 60rem;
    width: 100%;
    margin: 0 auto;
  }
  h1.title {
    margin: 0 0 .35rem;
    font-size: 1.55rem;
    color: var(--text);
    font-weight: 500;
    letter-spacing: .01em;
  }
  p.subtitle {
    margin: 0 0 2rem;
    color: var(--muted);
    font-size: .95rem;
  }
  ul.chapters {
    list-style: none;
    padding: 0;
    margin: 0;
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(15rem, 1fr));
    gap: 1rem;
  }
  ul.chapters li { margin: 0; }
  a.card {
    display: block;
    padding: 1.15rem 1.2rem;
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 6px;
    color: var(--text);
    text-decoration: none;
    transition: border-color .15s ease, transform .15s ease;
  }
  a.card:hover {
    border-color: var(--border-hover);
    transform: translateY(-1px);
  }
  a.card .n {
    display: block;
    font-family: "SFMono-Regular", ui-monospace, Menlo, Consolas, monospace;
    font-size: .75rem;
    color: var(--accent);
    letter-spacing: .08em;
    margin-bottom: .35rem;
  }
  a.card .h {
    display: block;
    font-size: 1.1rem;
    color: var(--text);
    margin-bottom: .35rem;
    letter-spacing: .01em;
  }
  a.card .b {
    display: block;
    font-size: .85rem;
    color: var(--muted);
    line-height: 1.5;
  }
  article.movement { max-width: 42rem; margin: 0 auto; }
  article.movement h1,
  article.movement h2,
  article.movement h3 {
    color: var(--text);
    letter-spacing: .01em;
    margin: 1.6rem 0 .6rem;
    font-weight: 500;
  }
  article.movement h1 { font-size: 1.55rem; margin-top: 0; }
  article.movement h2 { font-size: 1.2rem; }
  article.movement h3 { font-size: 1.05rem; color: var(--muted); }
  article.movement p {
    margin: 0 0 1rem;
    color: var(--text);
  }
  article.movement ul,
  article.movement ol {
    margin: 0 0 1rem;
    padding-left: 1.5rem;
    color: var(--text);
  }
  article.movement li { margin: .25rem 0; }
  article.movement code {
    font-family: "SFMono-Regular", ui-monospace, Menlo, Consolas, monospace;
    font-size: .88em;
    background: var(--bg-soft);
    border: 1px solid var(--border);
    padding: .05rem .3rem;
    border-radius: 3px;
    color: var(--accent);
  }
  article.movement a {
    color: var(--link);
    text-decoration: none;
    border-bottom: 1px dotted var(--border-hover);
  }
  article.movement a:hover { color: var(--link-hover); }
  article.movement blockquote {
    margin: 1rem 0;
    padding: .1rem 1rem;
    border-left: 3px solid var(--accent);
    color: var(--muted);
    font-style: italic;
  }
  article.movement em { color: var(--muted); font-style: italic; }
  article.movement strong { color: var(--frond-glow); font-weight: 600; }
  nav.movement-nav {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 1rem;
    margin: 3rem 0 0;
    padding-top: 1.25rem;
    border-top: 1px solid var(--border);
    font-size: .9rem;
  }
  nav.movement-nav a {
    color: var(--link);
    text-decoration: none;
  }
  nav.movement-nav a:hover { color: var(--link-hover); }
  nav.movement-nav .spacer { flex: 1; text-align: center; color: var(--muted); }
  footer.strip {
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


_FOOTER = (
    '<footer class="strip">'
    'grove.seed · six movements · b17: WGRV1 ΔΣ=42'
    '</footer>'
)


def _esc(text: str) -> str:
    """HTML-escape every user-visible string.

    Even though seed content is local files, the discipline is worth the
    ~1 line: a route that renders untrusted markdown safely today keeps
    rendering safely when someone later points the reader at a non-local
    source.
    """
    return html.escape(text, quote=True)


# ── Small Markdown → HTML converter ──────────────────────────────────────────
# Stdlib-only, escape-first. Not CommonMark — enough for the charter's
# chapter files (headings, paragraphs, lists, blockquotes, and the four
# common inline forms). Every plain text run is escaped before an inline
# transform runs, so ``<script>`` in a source file lands as literal text.

_LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)\s]+)\)")
_CODE_RE = re.compile(r"`([^`]+)`")
_BOLD_RE = re.compile(r"\*\*([^*]+)\*\*")
_ITAL_RE = re.compile(r"(?<!\*)\*([^*\n]+)\*(?!\*)")


def _render_inline(text: str) -> str:
    """Escape then apply inline Markdown (code, bold, italic, links).

    Order matters: inline code first (its contents are not further
    transformed), then bold, then italic, then links. Placeholders keep
    already-transformed spans out of later regex sweeps.
    """
    placeholders: list[str] = []

    def _stash(fragment: str) -> str:
        placeholders.append(fragment)
        return f"\x00P{len(placeholders) - 1}\x00"

    # Inline code first — capture the raw text, escape it, wrap in <code>.
    def _code(m: re.Match[str]) -> str:
        return _stash(f"<code>{_esc(m.group(1))}</code>")

    text = _CODE_RE.sub(_code, text)

    # Links — capture label + href, escape both, wrap in <a>.
    def _link(m: re.Match[str]) -> str:
        label = _esc(m.group(1))
        href = _esc(m.group(2))
        # Refuse javascript:/data: hrefs — belt-and-braces since seed is
        # local, but the same reason we escape everything else.
        low = href.lower().strip()
        if low.startswith(("javascript:", "data:", "vbscript:")):
            href = "#"
        return _stash(f'<a href="{href}">{label}</a>')

    text = _LINK_RE.sub(_link, text)

    # Escape everything that remains — this is the load-bearing step.
    text = _esc(text)

    # Bold and italic on the escaped text; the ``**`` and ``*`` markers
    # are unaffected by html.escape so the regex still finds them.
    text = _BOLD_RE.sub(lambda m: f"<strong>{m.group(1)}</strong>", text)
    text = _ITAL_RE.sub(lambda m: f"<em>{m.group(1)}</em>", text)

    # Reinsert stashed already-safe spans.
    def _unstash(m: re.Match[str]) -> str:
        return placeholders[int(m.group(1))]

    text = re.sub(r"\x00P(\d+)\x00", _unstash, text)
    return text


def _render_markdown(md: str) -> str:
    """Render a small subset of Markdown to HTML.

    Handles ATX headings (# .. ######), unordered and ordered lists,
    blockquotes, and paragraphs. Everything else is treated as a
    paragraph run. Every text region flows through :func:`_render_inline`.
    """
    lines = md.splitlines()
    out: list[str] = []
    i = 0

    def _flush_list(items: list[str], ordered: bool) -> None:
        if not items:
            return
        tag = "ol" if ordered else "ul"
        out.append(f"<{tag}>")
        for it in items:
            out.append(f"  <li>{_render_inline(it)}</li>")
        out.append(f"</{tag}>")

    def _flush_para(buf: list[str]) -> None:
        if not buf:
            return
        joined = " ".join(s.strip() for s in buf).strip()
        if joined:
            out.append(f"<p>{_render_inline(joined)}</p>")

    def _flush_quote(buf: list[str]) -> None:
        if not buf:
            return
        joined = " ".join(s.strip() for s in buf).strip()
        if joined:
            out.append(f"<blockquote>{_render_inline(joined)}</blockquote>")

    para_buf: list[str] = []
    quote_buf: list[str] = []
    ul_items: list[str] = []
    ol_items: list[str] = []

    def _flush_all() -> None:
        _flush_para(para_buf)
        para_buf.clear()
        _flush_quote(quote_buf)
        quote_buf.clear()
        _flush_list(ul_items, ordered=False)
        ul_items.clear()
        _flush_list(ol_items, ordered=True)
        ol_items.clear()

    while i < len(lines):
        raw = lines[i]
        line = raw.rstrip()
        stripped = line.lstrip()

        if not stripped:
            _flush_all()
            i += 1
            continue

        # ATX heading
        m = re.match(r"^(#{1,6})\s+(.+?)\s*#*\s*$", stripped)
        if m:
            _flush_all()
            level = len(m.group(1))
            body = _render_inline(m.group(2))
            out.append(f"<h{level}>{body}</h{level}>")
            i += 1
            continue

        # Blockquote (may continue over multiple lines)
        if stripped.startswith(">"):
            # Flush non-quote buffers so the quote starts clean.
            _flush_para(para_buf); para_buf.clear()
            _flush_list(ul_items, False); ul_items.clear()
            _flush_list(ol_items, True); ol_items.clear()
            quote_buf.append(stripped.lstrip(">").strip())
            i += 1
            continue
        elif quote_buf:
            _flush_quote(quote_buf); quote_buf.clear()

        # Unordered list item (-, *, +)
        m = re.match(r"^[-*+]\s+(.+)$", stripped)
        if m:
            _flush_para(para_buf); para_buf.clear()
            _flush_list(ol_items, True); ol_items.clear()
            ul_items.append(m.group(1))
            i += 1
            continue
        elif ul_items:
            _flush_list(ul_items, False); ul_items.clear()

        # Ordered list item
        m = re.match(r"^\d+[.)]\s+(.+)$", stripped)
        if m:
            _flush_para(para_buf); para_buf.clear()
            _flush_list(ul_items, False); ul_items.clear()
            ol_items.append(m.group(1))
            i += 1
            continue
        elif ol_items:
            _flush_list(ol_items, True); ol_items.clear()

        # Paragraph text
        para_buf.append(stripped)
        i += 1

    _flush_all()
    return "\n".join(out)


# ── Page builders ────────────────────────────────────────────────────────────
def _top_strip(here: str, back_link: tuple[str, str] | None = None) -> str:
    """The dark warm top strip. `back_link` is (href, label) or None."""
    back_html = ""
    if back_link is not None:
        href, label = back_link
        back_html = f'<a href="{_esc(href)}">{_esc(label)}</a>'
    return (
        '<header class="strip">'
        '<span class="dot"></span>'
        '<span class="name">ƒ willow</span>'
        '<span>·</span>'
        f'<span>{_esc(here)}</span>'
        '<span class="grow"></span>'
        f'{back_html}'
        '</header>'
    )


def _page(title: str, body_inner: str) -> str:
    """Wrap a page body in the shared shell (doctype, head, footer)."""
    return (
        "<!doctype html>\n"
        "<html lang=\"en\">\n"
        "<head>\n"
        '<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width,initial-scale=1">\n'
        f"<title>{_esc(title)}</title>\n"
        f"<style>{_CSS}</style>\n"
        "</head>\n"
        "<body>\n"
        f"{body_inner}\n"
        f"{_FOOTER}\n"
        "</body>\n"
        "</html>\n"
    )


def render_seed_index(movements: Iterable[dict[str, Any]]) -> str:
    """The ``/seed/`` landing page — six chapter cards in a grid."""
    strip = _top_strip("seed · six movements", back_link=("/", "return to the grove"))
    cards: list[str] = []
    for m in movements:
        n = int(m.get("n", 0))
        title = str(m.get("title", ""))
        body = str(m.get("body", ""))
        # First line/sentence of the body as the card blurb.
        blurb = ""
        for line in body.splitlines():
            s = line.strip()
            if s and not s.startswith(("#", ">", "*", "-", "`")):
                blurb = s
                break
        if not blurb:
            for line in body.splitlines():
                s = line.strip("# >").strip()
                if s:
                    blurb = s
                    break
        cards.append(
            '  <li>'
            f'<a class="card" href="/seed/{n}">'
            f'<span class="n">movement {n:02d}</span>'
            f'<span class="h">{_esc(title)}</span>'
            f'<span class="b">{_esc(blurb)}</span>'
            '</a></li>'
        )
    main = (
        "<main>\n"
        '<h1 class="title">The six movements</h1>\n'
        '<p class="subtitle">'
        'The onboarding walks the canon. One chapter per movement — '
        'the story is the install.'
        '</p>\n'
        '<ul class="chapters">\n'
        + "\n".join(cards) + "\n"
        '</ul>\n'
        "</main>"
    )
    return _page("seed · the six movements", strip + "\n" + main)


def render_seed_movement(
    movement: dict[str, Any],
    prev_url: str | None,
    next_url: str | None,
) -> str:
    """One movement page — title, body, prev/next nav.

    ``prev_url`` and ``next_url`` are absolute paths under ``/seed/`` (or
    None for the ends of the arc). Body is rendered from Markdown with
    the local, escape-first converter.
    """
    n = int(movement.get("n", 0))
    title = str(movement.get("title", ""))
    body = str(movement.get("body", ""))
    strip = _top_strip(
        f"seed · movement {n:02d}",
        back_link=("/seed/", "all six movements"),
    )
    body_html = _render_markdown(body)

    prev_link = (
        f'<a href="{_esc(prev_url)}">← previous movement</a>'
        if prev_url else '<span class="spacer">·</span>'
    )
    next_link = (
        f'<a href="{_esc(next_url)}">next movement →</a>'
        if next_url else '<span class="spacer">·</span>'
    )
    nav = (
        '<nav class="movement-nav">'
        f'{prev_link}'
        '<span class="spacer">'
        f'<a href="/seed/">seed index</a>'
        '</span>'
        f'{next_link}'
        '</nav>'
    )

    main = (
        "<main>\n"
        '<article class="movement">\n'
        f'<h1>{_esc(title)}</h1>\n'
        f'{body_html}\n'
        "</article>\n"
        f"{nav}\n"
        "</main>"
    )
    return _page(f"seed · {title}", strip + "\n" + main)
