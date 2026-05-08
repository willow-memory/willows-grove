"""panes/binder.py — Binder state pane (filed JSONLs + proposed edges).
b17: BNDP1  ΔΣ=42
"""
from rich.markup import escape as _e
from textual import work
from textual.containers import Container
from textual.widgets import DataTable, Label

import grove_db
from widgets.status_row import StatusRow


def fetch_binder() -> dict:
    result = {
        "proposed": 0,
        "filed":    0,
        "edges":    [],
        "files":    [],
    }
    conn = None
    try:
        conn = grove_db.get_connection()
        cur  = conn.cursor()

        cur.execute("""
            SELECT agent, source_atom, target_atom, edge_type,
                   to_char(proposed_at, 'YYYY-MM-DD HH24:MI') AS ts
            FROM public.binder_edges
            WHERE status = 'proposed'
            ORDER BY proposed_at DESC
            LIMIT 50
        """)
        edge_rows = cur.fetchall()
        result["proposed"] = len(edge_rows)
        result["edges"] = [
            {"agent": r[0], "src": r[1], "tgt": r[2], "kind": r[3], "ts": r[4]}
            for r in edge_rows
        ]

        cur.execute("""
            SELECT agent, jsonl_id, dest_path,
                   to_char(filed_at, 'YYYY-MM-DD HH24:MI') AS ts
            FROM public.binder_files
            ORDER BY filed_at DESC
            LIMIT 50
        """)
        file_rows = cur.fetchall()
        result["filed"] = len(file_rows)
        result["files"] = [
            {"agent": r[0], "jsonl": r[1], "path": r[2], "ts": r[3]}
            for r in file_rows
        ]
    except Exception:
        pass
    finally:
        if conn is not None:
            grove_db.release_connection(conn)
    return result


class BinderPane(Container):
    def compose(self):
        yield Label("  Binder", id="binder-title")
        yield StatusRow("Proposed edges", id="stat-proposed")
        yield StatusRow("Filed files   ", id="stat-filed")

        yield Label("  Proposed Edges", id="binder-edges-label")
        edges = DataTable(id="binder-edges-table", cursor_type="row")
        edges.add_columns("Agent", "Source", "Target", "Type", "Time")
        yield edges

        yield Label("  Filed JSONLs", id="binder-files-label")
        files = DataTable(id="binder-files-table", cursor_type="row")
        files.add_columns("Agent", "JSONL", "Dest", "Time")
        yield files

    def on_mount(self) -> None:
        self.set_interval(30, self.refresh_data)
        self.refresh_data()

    @work(thread=True, exit_on_error=False)
    def refresh_data(self) -> None:
        data = fetch_binder()
        self.app.call_from_thread(self._apply_data, data)

    def _apply_data(self, data: dict) -> None:
        proposed = data["proposed"]
        filed    = data["filed"]

        self.query_one("#stat-proposed", StatusRow).set_status(
            proposed == 0, str(proposed)
        )
        self.query_one("#stat-filed", StatusRow).set_status(
            None, str(filed)
        )

        edges = self.query_one("#binder-edges-table", DataTable)
        edges.clear()
        for row in data["edges"]:
            edges.add_row(
                _e(row["agent"]),
                _e(row["src"][:20]),
                _e(row["tgt"][:20]),
                _e(row["kind"]),
                row["ts"] or "",
            )

        files = self.query_one("#binder-files-table", DataTable)
        files.clear()
        for row in data["files"]:
            files.add_row(
                _e(row["agent"]),
                _e(row["jsonl"][:24]),
                _e(row["path"][-40:] if row["path"] else ""),
                row["ts"] or "",
            )
