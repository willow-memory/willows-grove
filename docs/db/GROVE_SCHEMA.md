# Grove schema reference (`grove.*`)

**b17:** GRSCH · ΔΣ=42  

Authoritative DDL: [`schema.sql`](../../schema.sql). Runtime owner: [`grove_db.py`](../../grove_db.py).

## Tables

### `grove.channels`

| Column | Type | Notes |
|--------|------|--------|
| `id` | BIGINT IDENTITY | PK |
| `name` | TEXT | UNIQUE — `#architecture`-style names stored plain |
| `channel_type` | TEXT | `direct` \| `group` \| `persona` \| `broadcast` |
| `description` | TEXT | |
| `agent_name` | TEXT | Optional persona binding |
| `created_at` / `updated_at` | TIMESTAMP | |
| `is_archived` | BOOLEAN | |

### `grove.messages`

| Column | Type | Notes |
|--------|------|--------|
| `id` | BIGINT IDENTITY | PK — **receipt id** for docs extractor |
| `channel_id` | BIGINT FK | → `channels.id` |
| `sender` | TEXT | |
| `content` | TEXT | Body — tags like `[DECISION]` live here |
| `message_type` | TEXT | `text` \| `system` \| `file_share` \| `reaction` |
| `reply_to_id` | BIGINT | Threading |
| `willow_indexed_at` | TIMESTAMP | KB/index pipeline marker |
| `to_agent` | TEXT | Default `__all__` — routing |
| `bus_type` | TEXT | See [`MESSAGE_ENVELOPE`](../contracts/MESSAGE_ENVELOPE.md) |
| `priority` | INTEGER | Default 3 |
| `correlation_id` | TEXT | Optional chaining |
| `ttl` | INTEGER | Optional |
| `created_at` | TIMESTAMP | |
| `is_deleted` | INTEGER | Soft delete flag |

### `grove.message_flags`

Flags per `(message_id, sender, flag)` with `flag ∈ {needs-reply, starred, read, urgent, resolved}`.

### `grove.agent_cursors`

Per-agent JSONB `cursors` for read positions / sync.

## Indexes

See `schema.sql`: channel, sender, created_at, reply_to, `to_agent`, `bus_type`, `priority`, partial index on `correlation_id`.

## Triggers / NOTIFY

`grove_notify_message()` → `pg_notify('grove_channel', NEW.channel_id::text)` on **INSERT** to `messages`. Clients LISTEN on `grove_channel`.

## How to verify

```sql
SET search_path = grove, public;
\d channels
\d messages
SELECT tgname FROM pg_trigger WHERE tgrelid = 'grove.messages'::regclass;
SELECT COUNT(*) FROM messages;
```

## Receipts

- `schema.sql` — `CREATE TABLE` / indexes / trigger
