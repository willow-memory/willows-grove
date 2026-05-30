"""grove/theme_textual.py — Textual/Rich colors from grove/theme.py palette.
b17: WDASH  ΔΣ=42
"""
from __future__ import annotations

from grove.theme import _C


def xterm256(n: int) -> str:
    n = int(n)
    if n < 16:
        base = (
            "#000000", "#800000", "#008000", "#808000", "#000080", "#800080",
            "#008080", "#c0c0c0", "#808080", "#ff0000", "#00ff00", "#ffff00",
            "#0000ff", "#ff00ff", "#00ffff", "#ffffff",
        )
        return base[n]
    if n < 232:
        n -= 16
        r, g, b = n // 36, (n // 6) % 6, n % 6

        def _v(x: int) -> int:
            return 0 if x == 0 else 55 + x * 40

        return f"#{_v(r):02x}{_v(g):02x}{_v(b):02x}"
    grey = 8 + (n - 232) * 10
    return f"#{grey:02x}{grey:02x}{grey:02x}"


BG        = xterm256(_C["bg"])
BORDER    = xterm256(_C["border"])
SECONDARY = xterm256(_C["secondary"])
PRIMARY   = xterm256(_C["primary"])
ACCENT    = xterm256(_C["accent"])
UNREAD    = xterm256(_C["unread"])
HEALTHY   = xterm256(_C["healthy"])
IDLE      = xterm256(_C["idle"])
DEGRADED  = xterm256(_C["degraded"])
DOWN      = xterm256(_C["down"])
INPUT_BG  = xterm256(_C["input_bg"])


def markup_bold_accent() -> str:
    return f"[bold {ACCENT}]"


def markup_dim() -> str:
    return f"[dim {SECONDARY}]"


def markup_status_dot(on: bool) -> str:
    color = HEALTHY if on else DOWN
    return f"[{color}]●[/]"


FRESH_SHELL_CSS = f"""
    Screen {{ background: {BG}; }}

    Footer {{ background: {INPUT_BG}; }}

    #vitals-source {{ display: none; }}

    #main-body {{
        height: 1fr;
    }}

    ContextPanel {{
        width: 26;
        height: 1fr;
    }}

    ContentArea {{
        width: 1fr;
        height: 1fr;
        background: {BG};
    }}

    HomeGrid {{
        width: 1fr;
        height: 1fr;
    }}

    ProjectsPane, KnowledgePane, ProvidersPane, SettingsPane, HelpPane, MCPPane,
    TasksPane, AgentsPane, RoutingPane, GitStatusPane, OpenPRsPane, UserTodosPane,
    UpstreamPane, ThinkMapPane {{
        width: 1fr;
        height: 1fr;
    }}

    NavBar {{
        height: 1;
        background: {INPUT_BG};
    }}

    NavBar #nav-links {{
        width: auto;
        padding: 0 1;
        color: {SECONDARY};
    }}

    NavBar #nav-vitals {{
        width: 1fr;
        padding: 0 1;
        color: {SECONDARY};
        text-align: right;
    }}

    HeroInfo {{
        width: 1fr;
        height: 7;
        padding: 0 1 0 1;
        color: {SECONDARY};
    }}

    GroundStrip {{
        height: 3;
        width: 100%;
        color: #16a34a;
        padding: 0;
        content-align: left bottom;
    }}

    HeroCollapsedStrip {{
        color: {SECONDARY};
    }}

    HeroScene {{
        background: #0a0f07;
        border-bottom: solid #1e3a1e;
    }}
"""
