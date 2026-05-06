-- Willow Grove — database bootstrap
-- Run once against your Postgres database:
--   psql -d willow_19 -f schema.sql
--
-- All statements are idempotent (IF NOT EXISTS / OR REPLACE).
-- Safe to re-run against an existing database.

-- pg_trgm enables GIN trigram index for ILIKE mention queries
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- ────────────────────────────────────────────────────────────
-- Grove schema — messaging bus
-- ────────────────────────────────────────────────────────────

CREATE SCHEMA IF NOT EXISTS grove;
SET search_path = grove, public;

CREATE TABLE IF NOT EXISTS channels (
    id              BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name            TEXT NOT NULL UNIQUE,
    channel_type    TEXT NOT NULL CHECK (channel_type IN ('direct','group','persona','broadcast')),
    description     TEXT,
    agent_name      TEXT,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_archived     BOOLEAN DEFAULT FALSE
);

CREATE TABLE IF NOT EXISTS messages (
    id                  BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    channel_id          BIGINT NOT NULL REFERENCES channels(id),
    sender              TEXT NOT NULL,
    content             TEXT NOT NULL,
    message_type        TEXT NOT NULL DEFAULT 'text'
                            CHECK (message_type IN ('text','system','file_share','reaction')),
    reply_to_id         BIGINT REFERENCES messages(id),
    willow_indexed_at   TIMESTAMP,
    to_agent            TEXT DEFAULT '__all__',
    bus_type            TEXT DEFAULT 'EVENT',
    priority            INTEGER DEFAULT 3,
    correlation_id      TEXT,
    ttl                 INTEGER,
    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_deleted          INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS message_flags (
    id          BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    message_id  BIGINT NOT NULL REFERENCES messages(id) ON DELETE CASCADE,
    sender      TEXT NOT NULL,
    flag        TEXT NOT NULL CHECK (flag IN ('needs-reply','starred','read','urgent','resolved')),
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (message_id, sender, flag)
);

CREATE TABLE IF NOT EXISTS agent_cursors (
    agent      TEXT PRIMARY KEY,
    cursors    JSONB NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_channels_name      ON channels (name);
CREATE INDEX IF NOT EXISTS idx_channels_type             ON channels (channel_type);
CREATE INDEX IF NOT EXISTS idx_messages_channel          ON messages (channel_id);
CREATE INDEX IF NOT EXISTS idx_messages_sender           ON messages (sender);
CREATE INDEX IF NOT EXISTS idx_messages_created          ON messages (created_at);
CREATE INDEX IF NOT EXISTS idx_messages_reply            ON messages (reply_to_id);
CREATE INDEX IF NOT EXISTS idx_messages_to_agent         ON messages (to_agent);
CREATE INDEX IF NOT EXISTS idx_messages_bus_type         ON messages (bus_type);
CREATE INDEX IF NOT EXISTS idx_messages_priority         ON messages (priority);
CREATE INDEX IF NOT EXISTS idx_messages_correlation      ON messages (correlation_id) WHERE correlation_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_flags_message             ON message_flags (message_id);
CREATE INDEX IF NOT EXISTS idx_flags_flag                ON message_flags (flag);
-- GIN trigram index — accelerates ILIKE '%@handle%' mention queries
CREATE INDEX IF NOT EXISTS idx_messages_content_trgm
    ON messages USING GIN (content gin_trgm_ops);

-- LISTEN/NOTIFY trigger — fires on every new message
CREATE OR REPLACE FUNCTION grove_notify_message()
RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
    PERFORM pg_notify('grove_channel', NEW.channel_id::text);
    RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS trg_grove_notify ON messages;
CREATE TRIGGER trg_grove_notify
    AFTER INSERT ON messages
    FOR EACH ROW EXECUTE FUNCTION grove_notify_message();

-- Seed the general channel (safe to re-run)
INSERT INTO channels (name, channel_type, description)
VALUES ('general', 'group', 'General discussion')
ON CONFLICT (name) DO NOTHING;

-- ────────────────────────────────────────────────────────────
-- Willow schema — routing decisions
-- ────────────────────────────────────────────────────────────

CREATE SCHEMA IF NOT EXISTS willow;

CREATE TABLE IF NOT EXISTS willow.routing_decisions (
    id            BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    ts            TIMESTAMPTZ NOT NULL DEFAULT now(),
    session_id    TEXT,
    prompt_snippet TEXT,
    routed_to     TEXT,
    rule_matched  TEXT,
    confidence    FLOAT,
    latency_ms    INTEGER
);

CREATE INDEX IF NOT EXISTS idx_routing_decisions_ts
    ON willow.routing_decisions (ts DESC);

-- ────────────────────────────────────────────────────────────
-- Public schema — tasks and knowledge
-- (Willow system tables — created here for standalone setups;
--  willow-1.9 also manages these via its own migrations.)
-- ────────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS public.tasks (
    id           BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    task         TEXT NOT NULL,
    status       TEXT NOT NULL DEFAULT 'pending'
                     CHECK (status IN ('pending','queued','running','complete','completed','failed','error')),
    submitted_by TEXT,
    cmd          TEXT,
    result       JSONB,
    created_at   TIMESTAMPTZ DEFAULT now(),
    updated_at   TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_tasks_status ON public.tasks (status);

-- ────────────────────────────────────────────────────────────
-- Binder schema — proposed edges and filed JSONLs
-- ────────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS public.binder_edges (
    id              BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    agent           TEXT NOT NULL,
    source_atom     TEXT NOT NULL,
    target_atom     TEXT NOT NULL,
    edge_type       TEXT NOT NULL,
    status          TEXT NOT NULL DEFAULT 'proposed'
                        CHECK (status IN ('proposed','filed','rejected')),
    proposed_at     TIMESTAMPTZ DEFAULT now(),
    filed_at        TIMESTAMPTZ,
    created_at      TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS public.binder_files (
    id              BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    agent           TEXT NOT NULL,
    jsonl_id        TEXT NOT NULL,
    dest_path       TEXT NOT NULL,
    status          TEXT NOT NULL DEFAULT 'filed'
                        CHECK (status IN ('filed','archived')),
    filed_at        TIMESTAMPTZ DEFAULT now(),
    created_at      TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_binder_edges_status ON public.binder_edges (status);
CREATE INDEX IF NOT EXISTS idx_binder_edges_agent ON public.binder_edges (agent);
CREATE INDEX IF NOT EXISTS idx_binder_edges_proposed ON public.binder_edges (proposed_at DESC) WHERE status = 'proposed';
CREATE INDEX IF NOT EXISTS idx_binder_files_status ON public.binder_files (status);
CREATE INDEX IF NOT EXISTS idx_binder_files_agent ON public.binder_files (agent);
CREATE INDEX IF NOT EXISTS idx_binder_files_filed ON public.binder_files (filed_at DESC) WHERE status = 'filed';

-- public.knowledge is owned by willow-1.9/core/pg_bridge.py (_SCHEMA).
-- Do NOT define it here — this file's stale DDL (BIGINT id, body, domain)
-- does not match the live schema (TEXT id, summary, project, weight, etc.)
-- and would silently break dashboard queries if applied before pg_bridge connects.
