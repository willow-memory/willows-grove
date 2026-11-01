@markdownai v1.0
<!-- b17: WGRV1  ΔΣ=42 -->

# Local models on the one-script rung — the night of 2026-10-31

**Status:** a record, not a ruling. It was written from the desk session
`e35a0a1d-8c06-40ec-845d-c4ce6c20a6fc`. Every number below is from a
receipt named next to it. The SOIL records beside it are
`projects_willow_stack/freeze-onescript-local-model-run-2026-11-01`
(frozen, unchanged), `…/onescript-local-model-resumed-2026-11-01` and
`…/onescript-model-board-2026-11-01`.

Contents: §1 What was asked · §2 What landed · §3 The finding · §4 The model board · §5 What was wrong along the way · §6 What was declined · §7 Open gaps · §8 Running it again

## §1 What was asked

The operator wanted to pick up the model work from Willow #134 and run it
through the one script's live spine on this box (`checkin → scope → seal →
serve → rat_turn → turn → checkout`). Local models only, the ones already
proven on the box, and the pinned kernel had to be current first.

## §2 What landed

| PR | What it changed | Why |
|---|---|---|
| willow-bot#213 | one-script's `kernel.pin` → Willow `e53e30d` | The pinned kernel's `propose` exited 0 when every row was refused, which reads as "a person said it". HEAD always exits 42. |
| willow-mcp#744 | `rat_turn` takes `max_turns` (1–16) | A model that writes one row per request needs N+1 turns for N rows, so the default of 4 capped a clean run at 3 rows |
| willow-mcp#746 | `rat_turn` returns the run's `transcript` (bounded, redacted, never in the receipt) | Silent, capped and ctx-full runs could only be guessed at. Loki FAIL on `fafb75c` (U+2028 split a JSON line) → fixed in `957690e` → PASS |
| willow-mcp#748 | `rat_turn` takes `ctx` (512–16384) | The request that let a finished model stop ran over the 4096-token window |
| ratatosk#89 (1.17.0) | `cites` sent as the text of a list is read as that list | llama3.2:3b sent `"[\"id\"]"`, a string, and had 0 of 20 calls accepted at temperature 0. Loki FAIL on `38b107a` (RecursionError on 3.10/3.11) → fixed in `df25267` → PASS |
| willow-bot#219 | serve gives a turn-bearing table as one fact per turn, keeping each row, and one `return` line for both readers | See §3. Loki FAIL on `0400bfd` (per-key de-duplication broke served == sealed) → fixed in `b12b233` → PASS |
| willow-mcp#750 | every one-script child gets `ONESCRIPT_HOME` = the verified clone | ratatosk's reach walked up to the vault's `.git` and its redact failed closed, hiding every provider error |
| ratatosk#90 (1.17.1) | Ollama is sent `think: false`; an empty answer gets the one nudge | qwen3:4b spent its whole budget on thinking that the client drops |

The operator's rebuilt one-script (willow-bot #215 and #217, release 1.33.0)
landed during the session too. Checkin, seed and escalate were probed on
Bernadette's pile and held up.

## §3 The finding

**The deterministic layer, not the model, was what stood between a small
model and a correct answer.** That was the operator's call
("I don't think it's the model. Something about the way the deterministic
system is putting things together"), and the record bears it out.

The text the model actually received was rebuilt from `served.json` with
ratatosk's own `load_served` and `render_served` (Kart `QRGMNFKD`). It was
one 2.8k-character line of sorted-key JSON. Each turn was split across
`turn_open` (intent), `proposal` (verdict) and `turn_close` (nothing). About
44% of every row was constants. And serve's `return` line ("one JSON object
per line") contradicted ratatosk's system prompt ("call propose").

| Run | What the model read | Result |
|---|---|---|
| `03c17037` | 11 event rows, two contradictory output instructions | 6 rows: turns 3–6 wrong or invented, never stopped (`turn_cap`) |
| `ed9cfbe9` | 4 joined facts (each row kept), one `return` line | **4 rows, all true, `end=done`** → `turn` `fc1c84a4`: 4/4 pass |

The model (llama3.2:3b), the brief, `ctx 8192` and `max_turns 6` were the
same in both runs. Willow #134 found the same thing the other way round:
the small model did well once code had labelled the facts.

## §4 The model board

Every model ran the same joined serve, the same 4-row brief and
`max_turns 6`, on a T500 with 4 GB and Ollama 0.35.0.

| Model | Result | Limit |
|---|---|---|
| **llama3.2:3b** | `done`, 4 true rows (`ed9cfbe9`) | Claims copy each turn's intent and leave out its outcome |
| willow-lane4-3b | `done`, 1 true row (`9e029ec0`) | Writes its second call as text, with broken JSON |
| qwen3:4b | `silent` at ctx 4096 (`757767b6`, 155 s); `timeout` at 8192 (`80cbd236`) | Reasons in prose, reads the table correctly, never calls `propose` even after the nudge |
| gemma3:4b | HTTP 400 (`8bc47fc3`) | `"registry.ollama.ai/library/gemma3:4b does not support tools"`, because its Ollama template has no tool calls |
| qwen2.5:0.5b | `silent` (`06574462`) | Echoes the task text back |

With the stack fixes in, every remaining failure comes from the model.

## §5 What was wrong along the way

These are recorded so they aren't repeated.

| Claim at the time | What the record showed |
|---|---|
| `d75a39f1` (ctx_full, 0 rows) was every call refused | The transcript (`49e7eb23`) showed 4 clean rows and then ctx_full on the stop request |
| "ratatosk sends no temperature" | `OllamaToolClient` already sent `temperature: 0`. Runs that flip are an input difference, not sampling |
| The served-fact merge across sessions was live | Latent only: `Run.turn` numbers turns across the whole record (Loki F4) |
| The 58 failures in the ratatosk worktree were mine | They fail identically on unchanged main in a worktree (a sibling-path lookup). CI's clean checkout passed |
| `…/venvs/willow-mcp/bin/pip install` upgraded the live venv | `bin/pip` is a stale script pointing at the retired `~/.willow` venv. Use `bin/python -m pip` |

## §6 What was declined

The four llama rows from `fc1c84a4` (rows 1074–1077, `desk-turns/turn-1..4.md`)
were staged as Nestor drafts `8fd7d54f`, `da9beb50`, `c26d47bf` and
`9be1de1f`. The operator chose not to seal them for now ("Let's delete those
seals for now"). The SOIL decision records behind them were soft-deleted.
The proposal rows stay on the one-script chain, which is append-only, and
wait unsealed. The Nestor drafts were never sealed. Nestor's MCP can't
reject a pair, so clearing them is done in the 8765 UI.

## §7 Open gaps

| Gap | What |
|---|---|
| `6465210a60a0` | llama's claims leave out the outcome (`pass` / `link_fail`) the brief asked for |
| `bf47297704b7` | Layout half: ratatosk still renders the served doc as one line |
| `9ffb21763780` | A capped or ctx-full run discards rows that already passed the door |
| `9037dfbc56f9` | The bot venv's `nestor` lacks `session_seal`; sessions wait unsealed |
| `796bdea7a947` | The before_stop gate reads `end=done` (an end reason) as a completion claim |

Resolved tonight: `511e511e64f8`, `b2349bd6f5a8`, `2fc9c02a989e`,
`536cfd120588`, and `c0a4aed6f308` (partly).

## §8 Running it again

From the desk, with willow-bot ≥ `e288177`, willow-mcp ≥ `34df934` and
willow-ratatosk 1.17.1 in the willow-mcp venv:

1. `checkin` with `resolve: "put_back"`
2. `scope` with `by: ["who"], match: {"who": "desk"}, upto: 753`, which gives the already-sealed subject `serve:ab467c43…`
3. `seal` with that subject and pair `e15314dd`
4. `serve` with the same spec, `max_chars: 6000`
5. `rat_turn` with `model: "llama3.2:3b", max_turns: 6, ctx: 8192`, then the brief
6. Read `transcript`, then `turn`, then `checkout`

The served table's id changes on every `serve`, so write a brief that names
an id only after `serve`.
