"""grove/apps/hero_stats.py — Live Grove + host stats for the hero band.
b17: WDASH  ΔΣ=42
"""
from __future__ import annotations

import shutil
from datetime import datetime, timezone

import grove_db
import grove_reader
from grove.apps.vitals import fetch_vitals, short_model_name

# Re-export for callers/tests
__all__ = ["fetch_hero_stats", "read_sysinfo"]


def _read_cpu_ticks() -> tuple[int, int]:
    try:
        with open("/proc/stat") as f:
            parts = f.readline().split()
        vals = [int(x) for x in parts[1:]]
        idle = vals[3] + (vals[4] if len(vals) > 4 else 0)
        return idle, sum(vals)
    except Exception:
        return 0, 1


def read_sysinfo(prev_cpu: tuple[int, int] | None = None) -> tuple[dict, tuple[int, int]]:
    """Return (metrics, cpu_snapshot). CPU is delta vs prev_cpu when provided."""
    prev = prev_cpu or _read_cpu_ticks()
    r: dict = {"cpu": 0, "mem": 0, "disk": 0, "temp": 0}
    cur_idle, cur_total = _read_cpu_ticks()
    delta_total = cur_total - prev[1]
    delta_idle = cur_idle - prev[0]
    if delta_total > 0:
        r["cpu"] = max(0, min(100, int((1 - delta_idle / delta_total) * 100)))
    try:
        mem: dict[str, int] = {}
        with open("/proc/meminfo") as f:
            for line in f:
                k, v = line.split(":", 1)
                mem[k.strip()] = int(v.strip().split()[0])
        total = mem.get("MemTotal", 1)
        avail = mem.get("MemAvailable", total)
        r["mem"] = max(0, min(100, int((total - avail) / total * 100)))
    except Exception:
        pass
    try:
        u = shutil.disk_usage("/")
        r["disk"] = max(0, min(100, int(u.used / u.total * 100)))
    except Exception:
        pass
    try:
        with open("/sys/class/thermal/thermal_zone0/temp") as f:
            r["temp"] = int(f.read().strip()) // 1000
    except Exception:
        pass
    return r, (cur_idle, cur_total)


def _channel_cursors() -> dict:
    try:
        import soil
        rec = soil.get("willow-dashboard/channel_cursors", "cursors")
        return rec if isinstance(rec, dict) else {}
    except Exception:
        return {}


def _ledger_ok() -> bool:
    conn = None
    try:
        conn = grove_db.get_connection()
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM public.frank_ledger")
        cur.fetchone()
        return True
    except Exception:
        return False
    finally:
        if conn is not None:
            grove_db.release_connection(conn)


def _agents_summary() -> dict:
    rows = grove_reader.grove_agent_fleet_rows(limit=12)
    online = [r for r in rows if r.get("ui_state") == "running"]
    idle = [r for r in rows if r.get("ui_state") == "idle"]
    top = online[0]["sender"] if online else (rows[0]["sender"] if rows else "")
    return {
        "rows": rows[:6],
        "online_count": len(online),
        "idle_count": len(idle),
        "top_agent": top,
    }


def _channels_summary() -> dict:
    channels = grove_reader.grove_channels(last_seen_ids=_channel_cursors())
    unread = sum(int(c.get("unread", 0)) for c in channels)
    hot = next((c for c in channels if c.get("unread", 0) > 0), None)
    return {
        "total": len(channels),
        "unread": unread,
        "hot_channel": hot["name"] if hot else "",
    }


def _routing_latest() -> dict | None:
    rows = grove_reader.routing_decisions(limit=1)
    if not rows:
        return None
    row = rows[0]
    ts = row.get("ts")
    if isinstance(ts, datetime):
        if ts.tzinfo is None:
            ts = ts.replace(tzinfo=timezone.utc)
        clock = ts.astimezone().strftime("%H:%M")
    else:
        clock = ""
    snippet = (row.get("prompt_snippet") or "")[:40]
    routed = row.get("routed_to") or "?"
    return {"clock": clock, "snippet": snippet, "routed_to": routed}


def fetch_hero_stats(prev_cpu: tuple[int, int] | None = None) -> dict:
    """Single poll bundle for HeroInfo, GroundStrip footer, collapsed strip."""
    sys, cpu_snap = read_sysinfo(prev_cpu)
    vitals = fetch_vitals()
    vitals["ledger"] = {"ok": _ledger_ok()}
    agents = _agents_summary()
    channels = _channels_summary()
    routing = _routing_latest()
    grove = vitals.get("grove", {})
    return {
        "vitals": vitals,
        "sys": sys,
        "cpu_snap": cpu_snap,
        "agents": agents,
        "channels": channels,
        "routing": routing,
        "grove_live": bool(grove.get("live")),
        "grove_model": short_model_name(grove.get("model") or ""),
    }
