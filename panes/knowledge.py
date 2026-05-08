"""panes/knowledge.py — Knowledge base search pane.
b17: WGRV1  ΔΣ=42
"""
from rich.markup import escape
from textual import work
from textual.containers import Container
from textual.message import Message
from textual.widgets import Static

import grove_db


def truncate_text(text: str, max_len: int) -> str:
    if len(text) <= max_len:
        return text
    return text[:max_len] + "…"


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


def render_atom(atom: dict) -> str:
    """Render a knowledge atom dict as Textual rich markup."""
    _H = "[bold #58a6ff]"
    _D = "[dim]"
    _E = "[/]"
    lines: list[str] = []

    lines.append(
        f"{_H}#{atom.get('id', '?')}[/]  "
        f"{_D}{atom.get('domain', '')}  w={atom.get('weight', 0)}{_E}"
    )
    lines.append("")

    title = atom.get("title", "")
    if title:
        lines.append(f"[bold]{escape(title)}[/]")
        lines.append("")

    summary = atom.get("summary", "")
    if summary:
        lines.append(f"{_D}SUMMARY{_E}")
        lines.append(escape(summary))
        lines.append("")

    content = atom.get("content", "")
    if content:
        lines.append(f"{_D}CONTENT{_E}")
        if isinstance(content, dict):
            lines.append(escape(str(content)))
        else:
            lines.append(escape(content))

    return "\n".join(lines)


class _AtomFetched(Message):
    def __init__(self, atom: dict | None) -> None:
        super().__init__()
        self.atom = atom


class KnowledgePane(Container):
    DEFAULT_CSS = """
    KnowledgePane {
        height: 1fr;
    }
    KnowledgePane #kb-atom {
        height: 1fr;
        padding: 1 2;
    }
    """

    def compose(self):
        yield Static(
            "[dim]Search knowledge in the left panel, then press Enter to view[/]",
            id="kb-atom",
            markup=True,
        )

    def display_atom(self, atom_id: int) -> None:
        self._fetch(atom_id)

    @work(thread=True)
    def _fetch(self, atom_id: int) -> None:
        atom = fetch_atom(atom_id)
        self.post_message(_AtomFetched(atom))

    def on__atom_fetched(self, event: _AtomFetched) -> None:
        from textual.css.query import NoMatches
        text = render_atom(event.atom) if event.atom else "[dim]Atom not found[/]"
        try:
            self.query_one("#kb-atom", Static).update(text)
        except NoMatches:
            pass
