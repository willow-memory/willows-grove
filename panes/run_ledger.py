"""panes/run_ledger.py — Run Ledger dashboard pane.
b17: WGRV1  ΔΣ=42
"""
from datetime import datetime
from textual import work
from textual.containers import Container, Vertical, Horizontal
from textual.widgets import DataTable, Label, Static

import grove_db


def fetch_runs() -> dict:
    """Fetch current and recent runs from willow.runs."""
    result = {"active": 0, "total": 0, "runs": []}
    conn = None
    try:
        conn = grove_db.get_connection()
        cur = conn.cursor()

        # Count active vs total
        cur.execute("""
            SELECT
                COUNT(*) FILTER (WHERE status = 'running') AS active,
                COUNT(*) AS total
            FROM willow.runs
        """)
        row = cur.fetchone()
        result["active"] = row[0] or 0
        result["total"] = row[1] or 0

        # Get recent runs (active first, then recent)
        cur.execute("""
            SELECT
                id::text, initiator, purpose, status,
                started_at, ended_at,
                (SELECT COUNT(*) FROM willow.run_agents WHERE run_id = r.id)::text AS agents
            FROM willow.runs r
            ORDER BY CASE WHEN status = 'running' THEN 0 ELSE 1 END,
                     started_at DESC
            LIMIT 20
        """)
        result["runs"] = [
            {
                "id": r[0][:8],  # first 8 chars of uuid
                "initiator": r[1],
                "purpose": (r[2] or "")[:40],
                "status": r[3],
                "started": str(r[4])[:16] if r[4] else "-",
                "ended": str(r[5])[:16] if r[5] else "-",
                "agents": r[6]
            }
            for r in cur.fetchall()
        ]
    except Exception as e:
        result["error"] = str(e)
    finally:
        if conn is not None:
            grove_db.release_connection(conn)
    return result


class RunLedgerPane(Container):
    """Dashboard pane for Run Ledger (willow.runs schema)."""

    def compose(self):
        yield Label("  Run Ledger", id="run-ledger-title")

        # Status row
        with Horizontal(id="run-ledger-status"):
            yield Static("Active: 0", id="stat-active")
            yield Static("Total: 0", id="stat-total")

        # Runs table
        table = DataTable(id="runs-table", cursor_type="row")
        table.add_columns("ID", "Initiator", "Purpose", "Status", "Started", "Agents")
        yield table

    def on_mount(self) -> None:
        self.set_interval(10, self.refresh_data)
        self.refresh_data()

    @work(thread=True)
    def refresh_data(self) -> None:
        data = fetch_runs()
        self.app.call_from_thread(self._apply_data, data)

    def _apply_data(self, data: dict) -> None:
        # Update status
        active_el = self.query_one("#stat-active", Static)
        total_el = self.query_one("#stat-total", Static)
        active_el.update(f"Active: {data['active']}")
        total_el.update(f"Total: {data['total']}")

        # Update table
        table = self.query_one("#runs-table", DataTable)
        table.clear()

        for run in data.get("runs", []):
            status_color = {
                "running": "yellow",
                "completed": "green",
                "abandoned": "dim",
                "crashed": "red",
            }.get(run["status"], "dim")

            table.add_row(
                run["id"],
                run["initiator"],
                run["purpose"],
                f"[{status_color}]{run['status']}[/]",
                run["started"],
                run["agents"],
            )
