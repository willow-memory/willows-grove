"""panes/knowledge.py — Knowledge base search pane.
b17: WGRV1  ΔΣ=42
"""
import os

from textual import on
from textual.containers import Container
from textual.widgets import DataTable, Input, Label


def _pg_conn():
    import psycopg2
    return psycopg2.connect(
        dbname=os.environ.get("WILLOW_PG_DB",   "willow_19"),
        user=os.environ.get("WILLOW_PG_USER", os.environ.get("USER", "")),
    )


def truncate_text(text: str, max_len: int) -> str:
    if len(text) <= max_len:
        return text
    return text[:max_len] + "…"


def search_kb(query: str, limit: int = 50) -> list[dict]:
    if not query.strip():
        return []
    try:
        conn = _pg_conn()
        cur  = conn.cursor()
        cur.execute("""
            SELECT id, title, summary, domain, weight
            FROM public.knowledge
            WHERE (title ILIKE %s OR summary ILIKE %s)
              AND domain != 'archived'
            ORDER BY weight DESC NULLS LAST, id DESC
            LIMIT %s
        """, (f"%{query}%", f"%{query}%", limit))
        rows = cur.fetchall()
        conn.close()
        return [
            {"id": r[0], "title": r[1] or "", "summary": r[2] or "",
             "domain": r[3] or "", "weight": r[4] or 0}
            for r in rows
        ]
    except Exception:
        return []


def fetch_atom(atom_id: int, conn=None) -> dict | None:
    """Fetch a single knowledge atom by id. Returns None if not found or on failure."""
    close = conn is None
    if conn is None:
        try:
            conn = _pg_conn()
        except Exception:
            return None
    try:
        cur = conn.cursor()
        try:
            cur.execute(
                "SELECT id, title, summary, domain, weight, content "
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
                "SELECT id, title, summary, domain, weight "
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
        if close:
            try:
                conn.close()
            except Exception:
                pass


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
        lines.append(f"[bold]{title}[/]")
        lines.append("")

    summary = atom.get("summary", "")
    if summary:
        lines.append(f"{_D}SUMMARY{_E}")
        lines.append(summary)
        lines.append("")

    content = atom.get("content", "")
    if content:
        lines.append(f"{_D}CONTENT{_E}")
        lines.append(content)

    return "\n".join(lines)


class KnowledgePane(Container):
    def compose(self):
        yield Label("  Knowledge — search (Enter to run)", id="kb-title")
        yield Input(placeholder="Search…", id="kb-search")
        table = DataTable(id="kb-table", cursor_type="row")
        table.add_columns("ID", "Title", "Domain", "W")
        yield table

    @on(Input.Submitted, "#kb-search")
    def _run_search(self, event: Input.Submitted) -> None:
        query = event.value.strip()
        table = self.query_one("#kb-table", DataTable)
        table.clear()
        if not query:
            return
        for row in search_kb(query):
            table.add_row(
                str(row["id"]),
                truncate_text(row["title"], 50),
                row["domain"],
                str(row["weight"]),
            )
