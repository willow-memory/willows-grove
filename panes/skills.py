"""panes/skills.py — Skills list pane.
b17: WGRV1  ΔΣ=42
"""
import os
from pathlib import Path

from rich.markup import escape as _e
from textual.containers import Container
from textual.widgets import DataTable, Label, Static

WILLOW_ROOT = Path(os.environ.get("WILLOW_ROOT", Path.home() / "github" / "willow-1.9"))
SKILLS_DIR  = WILLOW_ROOT / "willow" / "fylgja" / "skills"


def _read_skills() -> list[dict]:
    skills = []
    if not SKILLS_DIR.exists():
        return skills
    for path in sorted(SKILLS_DIR.glob("*.md")):
        name = path.stem
        description = ""
        try:
            text = path.read_text()
            in_front = False
            for line in text.splitlines():
                if line.strip() == "---":
                    in_front = not in_front
                    continue
                if in_front and line.startswith("description:"):
                    description = line[len("description:"):].strip().strip('"')
                    break
        except Exception:
            pass
        skills.append({"name": name, "description": description, "path": str(path)})
    return skills


class SkillsPane(Container):
    def compose(self):
        yield Label(f"  Skills — {SKILLS_DIR}", id="skills-title")
        table = DataTable(id="skills-table", cursor_type="row")
        table.add_columns("Name", "Description")
        yield table
        yield Static("", id="skill-detail")

    def on_mount(self) -> None:
        self._skills: list[dict] = []

    def refresh_data(self) -> None:
        self._skills = _read_skills()
        table = self.query_one("#skills-table", DataTable)
        table.clear()
        for s in self._skills:
            desc = s["description"][:80] + "…" if len(s["description"]) > 80 else s["description"]
            table.add_row(s["name"], desc)

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        skills = self._skills
        if event.cursor_row < len(skills):
            skill = skills[event.cursor_row]
            try:
                content = Path(skill["path"]).read_text()[:500]
            except Exception:
                content = "(unreadable)"
            self.query_one("#skill-detail", Static).update(
                f"\n[bold]{_e(skill['name'])}[/]\n{_e(skill['description'])}\n\n{_e(content)}"
            )
