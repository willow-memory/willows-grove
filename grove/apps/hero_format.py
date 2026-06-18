"""grove/apps/hero_format.py — Rich/plain formatters for hero band regions.
b17: WDASH  ΔΣ=42
"""
from __future__ import annotations

from datetime import datetime

from rich.markup import escape as rich_escape

from grove.theme_textual import ACCENT, HEALTHY, SECONDARY, UNREAD

_WILLOW_ART = [
    r"_  _  _  __ __  __    _  _  _  _",
    r"\\ \\ \\ || ||  ||  / o\ \\ \\ \\ ",
    r" \\/ \// || |_] |_} \__/  \\/ \//",
]


def _state_glyph(state: str) -> str:
    if state == "running":
        return "●"
    if state == "idle":
        return "◐"
    if state == "blocked":
        return "◆"
    return "○"


def format_ground_footer_plain(stats: dict, width: int) -> str:
    """Bottom hero row: Postgres · Ollama · Grove · agent · kart · ledger."""
    v = stats["vitals"]
    pg = v["pg"]
    olla = v["ollama"]
    kart = v.get("kart", {})
    ledger = v.get("ledger", {})

    parts: list[str] = []
    parts.append(f"▣ Postgres {pg['detail']}" if pg.get("ok") else "▣ Postgres ○")
    if olla.get("ok"):
        parts.append(f"⬡ Ollama {olla.get('count', 0)}")
    else:
        parts.append("⬡ Ollama ○")

    if stats.get("grove_live"):
        g = "⌁ Grove live"
        if stats.get("grove_model"):
            g += f" · {stats['grove_model']}"
    else:
        g = "⌁ Grove idle"
    parts.append(g)

    top = (stats.get("agents") or {}).get("top_agent") or ""
    if top:
        parts.append(f"♟ {top}")

    if kart.get("ok"):
        r, q = kart.get("running", 0), kart.get("queued", 0)
        parts.append(f"kart {r}/{r + q}")
    else:
        parts.append("kart ○")

    parts.append("ledger ●" if ledger.get("ok") else "ledger ○")

    ch = stats.get("channels") or {}
    if ch.get("unread", 0) > 0:
        parts.append(f"unread {ch['unread']}")

    line = "  ".join(parts)
    return line[: max(0, width)]


def format_ground_footer_markup(stats: dict) -> str:
    v = stats["vitals"]
    pg = v["pg"]
    olla = v["ollama"]
    kart = v.get("kart", {})
    ledger = v.get("ledger", {})

    def seg(text: str, accent: bool = False) -> str:
        color = ACCENT if accent else SECONDARY
        return f"[{color}]{rich_escape(text)}[/]"

    parts: list[str] = []
    parts.append(seg(f"▣ Postgres {pg['detail']}" if pg.get("ok") else "▣ Postgres ○"))
    parts.append(seg(f"⬡ Ollama {olla.get('count', 0)}" if olla.get("ok") else "⬡ Ollama ○"))

    if stats.get("grove_live"):
        g = "⌁ Grove live"
        if stats.get("grove_model"):
            g += f" · {stats['grove_model']}"
        parts.append(seg(g, accent=True))
    else:
        parts.append(seg("⌁ Grove idle"))

    top = (stats.get("agents") or {}).get("top_agent") or ""
    if top:
        parts.append(seg(f"♟ {top}"))

    if kart.get("ok"):
        r, q = kart.get("running", 0), kart.get("queued", 0)
        parts.append(seg(f"kart {r}/{r + q}"))
    else:
        parts.append(seg("kart ○"))

    parts.append(seg("ledger ●" if ledger.get("ok") else "ledger ○"))

    ch = stats.get("channels") or {}
    if ch.get("unread", 0) > 0:
        parts.append(f"[{UNREAD}]{ch['unread']} unread[/]")

    return "  ".join(parts)


def format_hero_info_markup(stats: dict) -> str:
    """HeroInfo right panel: wordmark · grove · sys · agents · clock."""
    s = stats["sys"]
    temp = f"{s['temp']}°C" if s.get("temp") else "n/a"
    art = "\n".join(f"[{ACCENT} bold]{rich_escape(l)}[/]" for l in _WILLOW_ART)

    if stats.get("grove_live"):
        grove_line = f"[{ACCENT}]⌁ live[/]"
        if stats.get("grove_model"):
            grove_line += f"  [{SECONDARY}]{rich_escape(stats['grove_model'])}[/]"
    else:
        grove_line = f"[dim {SECONDARY}]⌁ idle[/]"

    agents = stats.get("agents") or {}
    agent_bits: list[str] = []
    for row in agents.get("rows", [])[:4]:
        name = row.get("sender", "")
        if not name:
            continue
        glyph = _state_glyph(row.get("ui_state", "unknown"))
        color = HEALTHY if row.get("ui_state") == "running" else SECONDARY
        agent_bits.append(f"[{color}]{glyph} {rich_escape(name)}[/]")
    agents_line = "  ".join(agent_bits) if agent_bits else f"[dim {SECONDARY}]no agents on the bus[/]"

    routing = stats.get("routing")
    route_line = ""
    if routing:
        route_line = (
            f"\n[dim {SECONDARY}]{routing.get('clock', '')} "
            f"→ {rich_escape(routing.get('routed_to', ''))}[/]"
        )

    ch = stats.get("channels") or {}
    ch_line = ""
    if ch.get("unread", 0) > 0:
        hot = ch.get("hot_channel") or "?"
        ch_line = f"\n[{UNREAD}]{ch['unread']} unread[/] [{SECONDARY}]· #{rich_escape(hot)}[/]"

    from datetime import datetime
    now = datetime.now()
    t = now.strftime("%H:%M")
    d = now.strftime("%a %b %-d")

    return (
        f"{art}\n"
        f"\n"
        f"{grove_line}{route_line}{ch_line}\n"
        f"[dim {SECONDARY}]cpu {s['cpu']:3d}%  mem {s['mem']:3d}%  "
        f"disk {s['disk']:3d}%  {temp}[/]\n"
        f"{agents_line}\n"
        f"[dim {SECONDARY}]{t} · {d}[/]"
    )


def format_collapsed_strip_markup(stats: dict, meadow_plain: str) -> str:
    """Collapsed hero: ⬡ time · grove state · meadow tick."""
    from datetime import datetime
    t = datetime.now().strftime("%H:%M")
    if stats.get("grove_live"):
        g = f"[{ACCENT}]⌁ live[/]"
        if stats.get("grove_model"):
            g += f" [{SECONDARY}]{rich_escape(stats['grove_model'])}[/]"
    else:
        g = f"[dim {SECONDARY}]⌁ idle[/]"
    return (
        f"[{ACCENT}]⬡[/] [{SECONDARY}]{t}[/]  "
        f"{g}  [{SECONDARY}]{rich_escape(meadow_plain)}[/]"
    )
