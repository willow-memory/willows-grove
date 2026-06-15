"""grove/apps/vitals.py — System vitals strip for NavBar.
b17: WDASH  ΔΣ=42
"""
from __future__ import annotations

import json
import os
import urllib.request
from pathlib import Path

import grove_db
from grove.apps.mcp_registry import probe_serve_port, server_count

_GROVE_PID = Path.home() / ".willow" / "grove.pid"
_GROVE_PORT = int(os.environ.get("WILLOW_GROVE_PORT", "7777"))


def _pg_ok() -> tuple[bool, str]:
    conn = None
    try:
        conn = grove_db.get_connection()
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM public.knowledge")
        count = cur.fetchone()[0]
        return True, f"{count:,} atoms"
    except Exception as e:
        return False, str(e)[:30]
    finally:
        if conn is not None:
            grove_db.release_connection(conn)


def _ollama_ok() -> dict:
    """Ollama reachability + model count — not a Grove live model picker."""
    try:
        with urllib.request.urlopen("http://localhost:11434/api/tags", timeout=2) as r:
            data = json.loads(r.read())
        models = [m["name"] for m in data.get("models", [])]
        return {"ok": True, "count": len(models)}
    except Exception:
        return {"ok": False, "count": 0}


def _soil_ok() -> bool:
    store = Path(os.environ.get("WILLOW_STORE_ROOT",
                 str(Path.home() / ".willow" / "store")))
    return store.exists()


def _kart_ok() -> dict:
    conn = None
    try:
        conn = grove_db.get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT
                COUNT(*) FILTER (WHERE status='running') AS running,
                COUNT(*) FILTER (WHERE status='queued')  AS queued
            FROM public.tasks
        """)
        row = cur.fetchone()
        return {"ok": True, "running": row[0] or 0, "queued": row[1] or 0}
    except Exception:
        return {"ok": False, "running": 0, "queued": 0}
    finally:
        if conn is not None:
            grove_db.release_connection(conn)


def _grove_serve_pid_alive() -> bool:
    if not _GROVE_PID.exists():
        return False
    try:
        os.kill(int(_GROVE_PID.read_text().strip()), 0)
        return True
    except (OSError, ValueError):
        return False


def _grove_health_ok() -> bool:
    try:
        with urllib.request.urlopen(
            f"http://127.0.0.1:{_GROVE_PORT}/health", timeout=1,
        ) as r:
            return r.status == 200
    except Exception:
        return False


def grove_live() -> bool:
    """True when grove_serve (or equivalent) is running on this machine."""
    return _grove_serve_pid_alive() or _grove_health_ok()


def grove_live_model() -> str:
    """Active Grove model from SOIL — only when Grove is live; else empty."""
    if not grove_live():
        return ""
    try:
        import soil
        rec = soil.get("willow-dashboard/config", "active_model")
        if rec and rec.get("value"):
            return str(rec["value"]).strip()
    except Exception:
        pass
    return ""


def short_model_name(name: str) -> str:
    if not name:
        return ""
    base = name.split(":")[0].replace("yggdrasil", "ygg")
    ver = name.split(":")[-1] if ":" in name else ""
    return f"{base}:{ver}" if ver and ver != base else base


def fetch_vitals() -> dict:
    pg_ok, pg_detail = _pg_ok()
    live = grove_live()
    model = grove_live_model()
    mcp_count = server_count()
    mcp_serve = probe_serve_port()
    return {
        "pg":     {"ok": pg_ok, "detail": pg_detail},
        "ollama": _ollama_ok(),
        "soil":   {"ok": _soil_ok()},
        "kart":   _kart_ok(),
        "grove":  {"live": live, "model": model},
        "mcp":    {"count": mcp_count, "serve_up": mcp_serve},
    }


def format_vitals_line(v: dict) -> str:
    def dot(ok: bool) -> str:
        return "●" if ok else "○"

    pg_str = f"pg{dot(v['pg']['ok'])}"
    olla_str = f"olla{dot(v['ollama']['ok'])}"
    kart = v.get("kart", {})
    kart_str = (
        f"kart {kart['running']}/{kart['running'] + kart['queued']}"
        if kart.get("ok") else "kart○"
    )
    soil_str = f"soil{dot(v['soil']['ok'])}"
    mcp = v.get("mcp", {})
    mcp_str = f"mcp{mcp.get('count', 0)}"
    if mcp.get("serve_up"):
        mcp_str += "●"
    base = f" {pg_str}  {olla_str}  {kart_str}  {soil_str}  {mcp_str}"
    grove = v.get("grove", {})
    if grove.get("live") and grove.get("model"):
        return f"{base}  {short_model_name(grove['model'])}"
    return base


def format_vitals_markup(v: dict) -> str:
    """Rich markup for NavBar — same semantics as format_vitals_line."""
    from grove.theme_textual import HEALTHY, IDLE, SECONDARY

    def dot(ok: bool) -> str:
        if ok:
            return f"[{HEALTHY}]●[/]"
        return f"[{IDLE}]○[/]"

    pg = f"pg{dot(v['pg']['ok'])}"
    olla = f"olla{dot(v['ollama']['ok'])}"
    kart = v.get("kart", {})
    if kart.get("ok"):
        kart_s = f"kart {kart['running']}/{kart['running'] + kart['queued']}"
    else:
        kart_s = f"kart{dot(False)}"
    soil = f"soil{dot(v['soil']['ok'])}"
    mcp = v.get("mcp", {})
    mcp_s = f"mcp {mcp.get('count', 0)}"
    if mcp.get("serve_up"):
        mcp_s = f"{mcp_s} [{HEALTHY}]●[/]"
    body = f" {pg}  {olla}  {kart_s}  {soil}  {mcp_s}"
    grove = v.get("grove", {})
    if grove.get("live") and grove.get("model"):
        model = short_model_name(grove["model"])
        return f"[{SECONDARY}]{body}  {model}[/]"
    return f"[{SECONDARY}]{body}[/]"
