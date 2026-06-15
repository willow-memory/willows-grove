"""panes/knowledge.py — KB search + atom detail from Postgres.
b17: WGRV1  ΔΣ=42
"""
from __future__ import annotations

import json
from contextlib import suppress

from rich.markup import escape
from textual import on, work
from textual.binding import Binding
from textual.containers import Container, Horizontal, VerticalScroll
from textual.message import Message
from textual.widgets import DataTable, Input, Static

import grove_db
from grove.theme_textual import ACCENT, PRIMARY, SECONDARY, markup_bold_accent, markup_dim


def truncate_text(text: str, max_len: int) -> str:
    if len(text) <= max_len:
        return text
    return text[:max_len] + "…"


def humanize_content(raw: str | dict | list | None) -> str:
    if raw is None:
        return ""
    if isinstance(raw, (dict, list)):
        return json.dumps(raw, indent=2, default=str)
    s = str(raw).strip()
    if not s:
        return ""
    try:
        parsed = json.loads(s)
        if isinstance(parsed, (dict, list)):
            return json.dumps(parsed, indent=2, default=str)
    except Exception:
        pass
    return s


def search_kb(query: str, limit: int = 50) -> list[dict]:
    if not query.strip():
        return []
    conn = None
    try:
        conn = grove_db.get_connection()
        cur = conn.cursor()
        cur.execute(
            """
            SELECT id, title, summary, project AS domain, weight
            FROM public.knowledge
            WHERE (title ILIKE %s OR summary ILIKE %s)
              AND invalid_at IS NULL
            ORDER BY weight DESC NULLS LAST, id DESC
            LIMIT %s
            """,
            (f"%{query}%", f"%{query}%", limit),
        )
        return [
            {
                "id": r[0],
                "title": r[1] or "",
                "summary": r[2] or "",
                "domain": r[3] or "",
                "weight": r[4] or 0,
            }
            for r in cur.fetchall()
        ]
    except Exception:
        return []
    finally:
        if conn is not None:
            grove_db.release_connection(conn)


def fetch_atom(atom_id: str, conn=None) -> dict | None:
    atom_id = str(atom_id).strip()
    if not atom_id:
        return None
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
        out = {
            "id": row[0],
            "title": row[1] or "",
            "summary": row[2] or "",
            "domain": row[3] or "",
            "weight": row[4] or 0,
        }
        if len(row) > 5:
            out["content"] = row[5] or ""
        return out
    except Exception:
        return None
    finally:
        if owned and conn is not None:
            grove_db.release_connection(conn)


def atom_header_markup(atom: dict) -> str:
    _H = markup_bold_accent()
    _D = markup_dim()
    atom_id = atom.get("id", "?")
    dom = atom.get("domain") or ""
    weight = atom.get("weight", 0)
    lines = [f"{_H}#{escape(str(atom_id))}[/]  {_D}{escape(dom)}  w={weight}[/]", ""]
    title = atom.get("title") or ""
    if title:
        lines.append(f"[bold {PRIMARY}]{escape(title)}[/]")
        lines.append("")
    summary = atom.get("summary", "")
    if summary:
        lines.append(f"{_D}SUMMARY[/]")
        lines.append(escape(summary))
        lines.append("")
    return "\n".join(lines)


def atom_body_plain(atom: dict) -> str:
    summary = (atom.get("summary") or "").strip()
    raw_content = atom.get("content")
    if isinstance(raw_content, str):
        content = humanize_content(raw_content)
    else:
        content = humanize_content(raw_content)
    if summary and content and content != summary:
        return summary + "\n\n" + content
    return content or summary


class _KbSearchDone(Message):
    def __init__(self, rows: list[dict]) -> None:
        super().__init__()
        self.rows = rows


class _AtomFetched(Message):
    def __init__(self, atom: dict | None) -> None:
        super().__init__()
        self.atom = atom


class KnowledgePane(Container):
    BINDINGS = [Binding("r", "refresh_search", "Search")]

    DEFAULT_CSS = f"""
    KnowledgePane {{
        height: 1fr;
        padding: 0 1;
    }}
    KnowledgePane #kb-search {{
        height: 3;
        margin-bottom: 1;
    }}
    KnowledgePane #kb-body {{
        height: 1fr;
    }}
    KnowledgePane #kb-results {{
        width: 1fr;
        height: 1fr;
        border-right: solid {SECONDARY};
    }}
    KnowledgePane #kb-detail-scroll {{
        width: 1fr;
        height: 1fr;
    }}
    KnowledgePane #kb-header {{
        height: auto;
        padding: 0 1;
    }}
    KnowledgePane #kb-body-text {{
        height: auto;
        padding: 0 1;
    }}
    """

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self._rows: list[dict] = []
        self._last_query = ""

    def compose(self):
        yield Input(placeholder="Search knowledge… press Enter", id="kb-search")
        with Horizontal(id="kb-body"):
            results = DataTable(id="kb-results", cursor_type="row")
            results.add_columns(
                ("ID", "id"),
                ("Title", "title"),
                ("Domain", "domain"),
            )
            yield results
            with VerticalScroll(id="kb-detail-scroll"):
                yield Static(
                    f"[dim {SECONDARY}]Search, then select a row to view an atom.[/]",
                    id="kb-header",
                    markup=True,
                )
                yield Static("", id="kb-body-text")

    def refresh_data(self) -> None:
        query = self.query_one("#kb-search", Input).value.strip()
        if query:
            self._run_search(query)

    def action_refresh_search(self) -> None:
        self.refresh_data()

    @on(Input.Submitted, "#kb-search")
    def _on_search(self, event: Input.Submitted) -> None:
        self._run_search(event.value.strip())

    @work(thread=True, exit_on_error=False)
    def _run_search(self, query: str) -> None:
        rows = search_kb(query) if query else []
        self.post_message(_KbSearchDone(rows))

    def on__kb_search_done(self, event: _KbSearchDone) -> None:
        try:
            self._apply_search(event.rows)
        except Exception as exc:
            self._show_error(f"search UI error: {exc}")

    def _apply_search(self, rows: list[dict]) -> None:
        self._rows = rows
        table = self.query_one("#kb-results", DataTable)
        table.clear()
        if not self._rows:
            table.add_row("", "no matches", "")
            return
        for row in self._rows:
            title = truncate_text(row.get("title") or "(untitled)", 28)
            domain = truncate_text(row.get("domain") or "", 12)
            table.add_row(str(row["id"]), title, domain)

    @on(DataTable.RowHighlighted, "#kb-results")
    def _on_row(self, event: DataTable.RowHighlighted) -> None:
        try:
            self._select_row(event.cursor_row)
        except Exception as exc:
            self._show_error(f"select error: {exc}")

    def _select_row(self, row_index: int) -> None:
        if row_index < 0 or row_index >= len(self._rows):
            return
        atom_id = str(self._rows[row_index].get("id") or "").strip()
        if not atom_id:
            return
        self._fetch_atom(atom_id)

    @work(thread=True, exit_on_error=False)
    def _fetch_atom(self, atom_id: str) -> None:
        self.post_message(_AtomFetched(fetch_atom(atom_id)))

    def on__atom_fetched(self, event: _AtomFetched) -> None:
        try:
            self._apply_atom(event.atom)
        except Exception as exc:
            self._show_error(f"atom UI error: {exc}")

    def _apply_atom(self, atom: dict | None) -> None:
        if not atom:
            with suppress(Exception):
                self.query_one("#kb-header", Static).update("[dim]Atom not found[/]")
                self.query_one("#kb-body-text", Static).update("")
            return
        hdr = atom_header_markup(atom)
        body = atom_body_plain(atom).strip() or "(No body text for this atom.)"
        with suppress(Exception):
            self.query_one("#kb-header", Static).update(hdr)
            self.query_one("#kb-body-text", Static).update(body)

    def _show_error(self, text: str) -> None:
        with suppress(Exception):
            self.query_one("#kb-header", Static).update(f"[red]{escape(text)}[/]")
            self.query_one("#kb-body-text", Static).update("")
