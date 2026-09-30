# Every seat hears the grove

**Status:** proposed · queued as [`forge-convergence.md`](forge-convergence.md) §6 step **10** · operator ratifies before build
**Asked:** operator, 2026-09-30: "we need to get that into rat? or the mcp? Not as a claude tool, but as something any agent can use."
**Forge project:** `fleet-spine` (`~/Forge/workshop/fleet-spine/FINDINGS.md`, joint 8). The spine's opening bite (2026-09-22) was "Wake an agent seat through ratatosk so forge checkpoints gate the turn and willow tools get used on the spine." It proved the wake rail; this is the rail's missing return direction. Joint 7, Forge checkpoints gating the turn, is the same kind of work and stays open beside it.

## What was tested

On 2026-09-30 the Willow desk armed a Monitor on its own event stream
(`ws://127.0.0.1:8766/events/willow`, sealed pair 13330d1c) and heard Cursor
Loki accept audit E1F42051 and return its PASS verdict on willow-mcp#684
while the operator typed nothing. The seat learned of the verdict from the
grove, not from a poll or a question.

That works for exactly one kind of seat: a Claude Code or Cursor session
opened in this repo, whose client has a Monitor tool and whose hooks come
from `hooks/client-hooks.json`.

## Where the pieces live today

| Piece | Where | Who can use it |
|---|---|---|
| The traffic | Postgres `grove.*`, read by willow-mcp `grove.inbox_bundle` (`src/willow_mcp/grove.py:901`) | any caller of willow-mcp |
| The live stream | Grove's served page, `/events/<seat>` (`grove_serve.py`) | a client that can hold a WebSocket |
| The "last seen" cursor | anchor files kept by `hooks/grove_hook.py` (`_grove_inbox_lines`, :416) | this repo's hook only |
| Per-prompt surfacing | `prompt_submit → reinject`, five lines per prompt | IDE harness only |
| Ratatosk listener | polls its seat's channel between wakes (`grove_get_history`, last 20, `ratatosk/listener.py:232`) behind its own cursor (`state.cursor`), and wakes the seat on what it finds; posts wake receipts | the listener only |
| Ratatosk crown (a wake in progress) | nothing read from the grove between model calls | — |

§2 of `forge-convergence.md` already measured why Ratatosk cannot run the
reinject row: it has no prompt-submit event, and it discards lifecycle hook
results. So a Loki wake on the free ladder hears nothing from the grove
mid-wake, and neither would any other agent that is not an IDE seat here.

## Shape

**1. willow-mcp owns the verb and the cursor.** One agent-agnostic read:

- `grove_events(app_id, limit)` returns the seat's new traffic (inbox bundle:
  @mentions, bus-addressed, its own `#<seat>` channel) in the three states,
  populated / empty / unreachable, and advances that seat's cursor past what
  it returned. An unreachable read never moves the cursor.
- A CLI twin, `willow-mcp grove events --app <id> --follow`, prints one line
  per event so any process can stream it without speaking MCP.
- The cursor is held server-side per seat. Two cursors already exist and move
  down into willow-mcp rather than being copied: the hook's anchor files and
  the Ratatosk listener's `state.cursor`. Consumers each holding their own
  cursor (hook, stream, listener, crown) would either show a message twice or
  skip it.

**2. Ratatosk polls between model calls.** In the crown's turn loop, before
each model call, call `grove_events` and append any new lines as one message,
the same way it appends the identity line. This is the step that makes it
work for agents that are not Claude. It rides with step 7 (Ratatosk renders
the rows), since both give Ratatosk a place to put a row's output. Optional in
the same bite: the daemon wakes a seat on an @mention, not only on a packet.

**3. Grove's stream and this repo's hook become consumers.** `/events/<seat>`
and `reinject` read through the same cursor instead of owning one. The
`orient` boot line keeps telling an IDE seat to arm its Monitor.

## Line format

Keep the one the hook already uses, `[grove #<channel> <sender>] <first 140
chars>`, oldest first, capped per injection, with a tail line naming the
cursor when more remain. A seat that reads the grove through the hook today
reads it the same way through Ratatosk tomorrow.

## Order

willow-mcp first, since the Ratatosk and Grove halves read through it.

## Known on the way

- After a `/clear` on 2026-09-30 the orient line that says "arm a Monitor"
  did not reach the new session, so the stream sat unarmed until asked about.
  Why is not yet known: the SessionStart hook in `.claude/settings.json` has
  no matcher, so it should fire on clear.
- Cursor Loki's packets leave a `[ratatosk] wake … entry refused: ERUNNER`
  line in `#willow` each time, because the ratatosk listener tries to wake a
  packet addressed to the Cursor seat. Correct refusal, noisy channel.

## Not decided

- Which events count beyond the inbox bundle: `desk_attention`,
  human-required, dispatch status changes.
- The per-injection cap for a model seat, where context is the budget.
- Whether a stale cursor (a seat not seen for days) replays or starts from
  now, as the hook's first run does.
