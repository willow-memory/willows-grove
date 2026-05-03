"""
grove_db.py — Bridge shim. Canonical implementation lives in safe-app-grove/grove_db.py.
Re-exports everything from there and adds bridge-specific helpers.
b17: WGRV1  ΔΣ=42
"""
import importlib.util
import os
import sys
from pathlib import Path

_CANONICAL = Path(__file__).parent.parent / "safe-app-grove" / "grove_db.py"
_spec = importlib.util.spec_from_file_location("_grove_db_canonical", _CANONICAL)
_mod  = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)

# Re-export everything from canonical
SCHEMA              = _mod.SCHEMA
VALID_CHANNEL_TYPES = _mod.VALID_CHANNEL_TYPES
VALID_MESSAGE_TYPES = _mod.VALID_MESSAGE_TYPES
VALID_FLAGS         = _mod.VALID_FLAGS
BUS_TYPES           = _mod.BUS_TYPES
BUS_PRIORITY        = _mod.BUS_PRIORITY
BUS_BROADCAST       = _mod.BUS_BROADCAST

_get_pool         = _mod._get_pool
get_connection    = _mod.get_connection
release_connection= _mod.release_connection
init_schema       = _mod.init_schema
create_channel    = _mod.create_channel
list_channels     = _mod.list_channels
get_channel       = _mod.get_channel
archive_channel   = _mod.archive_channel
send_message      = _mod.send_message
get_history       = _mod.get_history
get_thread        = _mod.get_thread
delete_message    = _mod.delete_message
search_messages   = _mod.search_messages
set_flag          = _mod.set_flag
clear_flag        = _mod.clear_flag
get_flags         = _mod.get_flags
get_flagged       = _mod.get_flagged
bus_send          = _mod.bus_send
bus_receive       = _mod.bus_receive
cursor_save       = _mod.cursor_save
cursor_load       = _mod.cursor_load
get_unindexed     = _mod.get_unindexed
mark_indexed      = _mod.mark_indexed


def listen_connection():
    """Open a dedicated autocommit connection for LISTEN — not from the pool.

    Callers own this connection for its lifetime and must close() it themselves.
    """
    import psycopg2
    pg_db   = os.getenv("WILLOW_PG_DB",   "willow_19")
    pg_user = os.getenv("WILLOW_PG_USER",  os.getenv("USER", ""))
    dsn     = os.getenv("WILLOW_DB_URL",   "") or f"dbname={pg_db} user={pg_user}"
    conn    = psycopg2.connect(dsn)
    conn.autocommit = True
    return conn


def ensure_card_builder_channel() -> None:
    """Idempotent: create #card-builder channel with agent_name='heimdallr' if absent."""
    conn = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO grove.channels (name, channel_type, description, agent_name)
            VALUES ('card-builder', 'group', 'Heimdallr card builder interview', 'heimdallr')
            ON CONFLICT (name) DO NOTHING
        """)
        conn.commit()
    except Exception:
        pass
    finally:
        if conn is not None:
            release_connection(conn)
