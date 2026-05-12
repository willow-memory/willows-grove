"""panes/knowledge.py — Knowledge base search pane.
b17: WGRV1  ΔΣ=42
"""
from __future__ import annotations

import json

from textual import work
from textual.containers import VerticalScroll
from textual.message import Message
from textual.widget import Widget
from textual.widgets import Static

import grove_db

from rich.markup import escape


def truncate_text(text: str, max_len: int) -> str:
    if len(text) <= max_len:
        return text
    return text[:max_len] + "…"


_BODY_FIRST_KEYS: frozenset[str] = frozenset(
    {
        "body",
        "text",
        "content",
        "message",
        "description",
        "summary",
        "notes",
        "details",
        "markdown",
        "md",
        "plaintext",
        "statement",
        "answer",
        "result",
        "insight",
    }
)


def _try_decode_json(s: str):
    """Return parsed JSON or None."""
    try:
        return json.loads(s)
    except Exception:
        return None


def _scalar_str(v: object) -> str:
    if v is None:
        return ""
    if isinstance(v, bool):
        return "yes" if v else "no"
    return str(v)


def _structure_to_text(obj: object, depth: int = 0) -> str:
    """Flatten JSON-like structures into readable lines."""
    if depth > 14:
        return "…"
    pad = "  " * depth
    if isinstance(obj, str):
        t = obj.strip()
        if not t:
            return ""
        if len(t) > 2:
            decoded = None
            if (t.startswith("{") and t.endswith("}")) or (t.startswith("[") and t.endswith("]")):
                decoded = _try_decode_json(t)
            elif t.startswith('"') and t.endswith('"'):
                decoded = _try_decode_json(t)
            if decoded is not None:
                return _structure_to_text(decoded, depth)
        return obj

    if isinstance(obj, (int, float)) and not isinstance(obj, bool):
        return _scalar_str(obj)

    if isinstance(obj, bool):
        return _scalar_str(obj)

    if obj is None:
        return ""

    if isinstance(obj, list):
        if not obj:
            return ""
        chunks: list[str] = []
        for i, item in enumerate(obj[:200]):
            line = _structure_to_text(item, depth + (0 if isinstance(item, (dict, list)) else 0))
            if not line.strip():
                continue
            if isinstance(item, (dict, list)):
                chunks.append(line)
            else:
                bullets = f"{pad}• {line}" if pad else f"• {line}"
                chunks.append(bullets)
        return "\n".join(chunks)

    if isinstance(obj, dict):
        if not obj:
            return ""

        def _key_ord(k: object) -> tuple[int, str]:
            ks = str(k).lower()
            prio = 0 if ks in _BODY_FIRST_KEYS else 1
            return prio, ks

        lines_out: list[str] = []
        for k in sorted(obj.keys(), key=_key_ord):
            v = obj[k]
            if v in (None, "", [], {}):
                continue
            key_s = _scalar_str(k)
            if isinstance(v, (dict, list)):
                inner = _structure_to_text(v, depth + 1)
                if inner:
                    lines_out.append(f"{pad}{key_s}:")
                    lines_out.append(inner)
                continue
            val = _scalar_str(v).strip()
            if not val:
                continue
            if "\n" in val:
                lines_out.append(f"{pad}{key_s}:")
                for ln in val.splitlines():
                    lines_out.append(f"{pad}  {ln}".rstrip())
            else:
                lines_out.append(f"{pad}{key_s}: {val}")
        return "\n".join(lines_out)

    return _scalar_str(obj)


def humanize_content(raw: str | None) -> str:
    """Turn atom `content` into readable prose; safely unwrap JSON and nested payloads."""
    if raw is None:
        return ""
    s = raw.strip()
    if not s:
        return ""
    decoded: object | None
    decoded = _try_decode_json(s)
    if decoded is None:
        return s
    text = _structure_to_text(decoded)
    return text.strip() if text.strip() else s


def search_kb(query: str, limit: int = 50) -> list[dict]:
    if not query.strip():
        return []
    conn = None
    try:
        conn = grove_db.get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT id, title, summary, project AS domain, weight
            FROM public.knowledge
            WHERE (title ILIKE %s OR summary ILIKE %s)
              AND invalid_at IS NULL
            ORDER BY weight DESC NULLS LAST, id DESC
            LIMIT %s
        """, (f"%{query}%", f"%{query}%", limit))
        rows = cur.fetchall()
        return [
            {"id": r[0], "title": r[1] or "", "summary": r[2] or "",
             "domain": r[3] or "", "weight": r[4] or 0}
            for r in rows
        ]
    except Exception:
        return []
    finally:
        if conn is not None:
            grove_db.release_connection(conn)


def fetch_atom(atom_id: int, conn=None) -> dict | None:
    """Fetch a single knowledge atom by id. Returns None if not found or on failure."""
    owned = conn is None
    if owned:
        try:
            conn = grove_db.get_connection()
        except Exception:
            return None
    try:
        cur = conn.cursor()
        try:
            cur.execute(
                "SELECT id, title, summary, project, weight, content "
                "FROM public.knowledge WHERE id = %s",
                (atom_id,),
            )
            row = cur.fetchone()
            if not row:
                return None
            return {
                "id": row[0], "title": row[1] or "", "summary": row[2] or "",
                "domain": row[3] or "", "weight": row[4] or 0, "content": row[5] or "",
            }
        except Exception:
            conn.rollback()
            cur.execute(
                "SELECT id, title, summary, project, weight "
                "FROM public.knowledge WHERE id = %s",
                (atom_id,),
            )
            row = cur.fetchone()
            if not row:
                return None
            return {
                "id": row[0], "title": row[1] or "", "summary": row[2] or "",
                "domain": row[3] or "", "weight": row[4] or 0,
            }
    except Exception:
        return None
    finally:
        if owned and conn is not None:
            grove_db.release_connection(conn)


def atom_header_markup(atom: dict) -> str:
    """Rich-text header (bounded markup — title escaped)."""
    _H = "[bold #58a6ff]"
    _D = "[dim]"
    _E = "[/]"
    atom_id = atom.get("id", "?")
    dom = atom.get("domain") or ""
    weight = atom.get("weight", 0)
    lines = [f"{_H}#{atom_id}[/]  {_D}{escape(dom)}  w={weight}{_E}", ""]
    title = atom.get("title") or ""
    if title:
        lines.append(f"[bold]{escape(title)}[/]")
    return "\n".join(lines)


def atom_body_plain(atom: dict) -> str:
    """Plain-text body from summary + humanized content (no markup)."""
    summary = (atom.get("summary") or "").strip()
    raw_content = atom.get("content")
    plain_c = humanize_content(raw_content if isinstance(raw_content, str) else "")

    if summary and plain_c:
        if plain_c.startswith(summary) or summary in plain_c[: len(summary) + 5]:
            return plain_c
        return summary + "\n\n" + plain_c
    if plain_c:
        return plain_c
    return summary


def render_atom(atom: dict) -> str:
    """Render atom for snapshots/tests: markup header plus plain body."""
    return atom_header_markup(atom) + "\n\n" + atom_body_plain(atom)


class KnowledgeRailPreview(Message):
    """Posted when an atom finishes loading — right rail can show excerpt."""

    def __init__(self, atom_id: int, title: str, excerpt: str) -> None:
        super().__init__()
        self.atom_id = atom_id
        self.title   = title
        self.excerpt = excerpt


class _AtomFetched(Message):
    def __init__(self, atom: dict | None) -> None:
        super().__init__()
        self.atom = atom


class KnowledgePane(Widget):
    DEFAULT_CSS = """
    KnowledgePane {
        height: 1fr;
    }
    KnowledgePane #kb-scroll {
        height: 1fr;
        padding: 1 2;
    }
    KnowledgePane #kb-header {
        height: auto;
    }
    KnowledgePane #kb-body {
        height: auto;
        margin-top: 1;
        color: #c9d1d9;
    }
    """

    def compose(self):
        with VerticalScroll(id="kb-scroll"):
            yield Static(
                "[dim]Search knowledge in the left panel, then press Enter to view[/]",
                id="kb-header",
                markup=True,
            )
            yield Static("", id="kb-body", markup=False)

    def display_atom(self, atom_id: int) -> None:
        self._fetch(atom_id)

    @work(thread=True, exit_on_error=False)
    def _fetch(self, atom_id: int) -> None:
        import logging
        try:
            atom = fetch_atom(atom_id)
            self.post_message(_AtomFetched(atom))
        except Exception:
            logging.exception("KnowledgePane._fetch failed for atom %s", atom_id)
            self.post_message(_AtomFetched(None))

    def on__atom_fetched(self, event: _AtomFetched) -> None:
        from textual.css.query import NoMatches

        atom = event.atom
        if not atom:
            try:
                self.query_one("#kb-header", Static).update("[dim]Atom not found[/]")
                self.query_one("#kb-body", Static).update("")
            except NoMatches:
                pass
            return

        hdr = atom_header_markup(atom)
        body = atom_body_plain(atom).strip()
        if not body:
            body_plain = "(No body text for this atom.)"
        else:
            body_plain = body

        try:
            self.query_one("#kb-header", Static).update(hdr)
            self.query_one("#kb-body", Static).update(body_plain)
        except NoMatches:
            pass

        title = (atom.get("title") or "").strip() or f"Atom #{atom['id']}"
        ex_src = atom_body_plain(atom).replace("\n", " ").strip()
        excerpt = truncate_text(ex_src, 420)
        self.post_message(KnowledgeRailPreview(atom["id"], title, excerpt))

