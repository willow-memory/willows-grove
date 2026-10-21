# The smallest one script: handoff, 2026-10-21

§1 Start here · §2 Branches and PRs · §3 What was done · §4 What 42 means now · §5 Where things are · §6 Running it on your machine · §7 Measurements · §8 What's left · §9 Open questions · §10 What the cloud container held

Cloud session `012onBhQDT2rhEYjuoFDQtha`
(https://claude.ai/code/session_012onBhQDT2rhEYjuoFDQtha). Agent-written,
not sealed. The decisions are the operator's, quoted where they were made.

## §1 Start here

| Order | Do |
|---|---|
| 1 | Merge willow-memory/willow-mcp#728 **before** willow-memory/willow-bot#158. #158 makes `onescript turn` exit 42; #728 teaches willow-mcp's executor that 42 ran to a verdict. In the other order, every turn carrying proposals shows as `unreachable` there. |
| 2 | Then #158. It holds 9 commits (§3). Its description still describes only the first one (`stamp.py`); rewrite it when you say (F-42). |
| 3 | Grove `claude/flatten-2-rulings` (F-39 to F-43, O-6, O-7) and `claude/flatten-gaps` (the guesses doc) are pushed with no PR. |
| 4 | `genesis.py` is on willow-bot `claude/genesis`, committed in the container and **not pushed** (§10). |

## §2 Branches and PRs

| Repo | Branch | Head | PR | State |
|---|---|---|---|---|
| willow-bot | `claude/stamp` | `7b13b7a` | willow-memory/willow-bot#158 | Open, CI green, mergeable |
| willow-mcp | `claude/stoic-cerf-hv9y8s` | `a817646` | willow-memory/willow-mcp#728 | Open, CI running at writing |
| willows-grove | `claude/flatten-2-rulings` | `92e07f8` | none | Pushed |
| willows-grove | `claude/flatten-gaps` | `342fd69` | none | Pushed (guesses G23 to G28) |
| willows-grove | `claude/smallest-one-script-handoff` | this file | none | Pushed |
| willow-bot | `claude/genesis` | `4b40db9` | none | **Container only** |
| willow-bot | `main` | `3129271` | — | Already holds the prompt-path cut (#156: `opening.py`, `prompt_path.py`, 18 modules not 39) |

## §3 What was done

On #158 (`claude/stamp`), oldest first:

| Commit | What |
|---|---|
| `8a2e462` | `stamp.py`: the record's write token moved out of `gate`; the prompt path drops `gate`, `graph`, `nestor_seal` (16 modules) |
| `7c62f10` | `pile.ChunkReader`: one `git cat-file --batch` per repo for a prompt's chunks |
| `435a411` | The record remembers its last parse, keyed by the file's stat |
| `debbf0b` | Check-in leaves its `--repo` map beside the keys (`repos.json`); the prompt hook reads it (F-41) |
| `fff0ac8` | A prompt reads the record from the human's sealed tip (`anchor.json`) on, not from row 0 (F-39) |
| `34b93e3` | The store is read lazily: totals and a row check by SQL at open; a chunk's row only when a bite touches it. Answers identical on the 20-repo box |
| `1942548` | The row check's fallback no longer writes out a state word (the states guard caught it) |
| `907c2ac` | Exit 42 (first read wrongly as "handed to the human") |
| `7b13b7a` | 42 as the operator defined it (§4); Jeles serves `human` nuggets only; a 42 seed is logged as a Jeles gap |

Elsewhere:

| Where | What |
|---|---|
| willow-mcp `a817646` (#728) | The executor shapes exit 42 like 0, with `escalate: true` |
| Grove `92e07f8` | F-43 (§4), O-6, O-7 |
| willow-bot `7831eae`, `4b40db9` (`claude/genesis`) | `one-script/genesis.py`: the smallest one script's reference. One stdlib file, Python 3.9+, rows in the one script's own format (`Record.verify_chain` checks a genesis box unchanged), exit 0 / 42 / 2. Built from the Grok sketch, fixing its unhashed fields, its fork from GENESIS on a torn line, and its test that deleted the ledger in the current directory. Tested on 3.9.25 and 3.13 |

## §4 What 42 means now

The operator, 2026-10-21 (F-43):

> "42 just means I don't have enough information to say a human said this was true."
> "Think about the pile that is in this box. These are things I've already said yes to"
> "They are 0. A human said it was true." (of Jeles's public-record nuggets)

| Verb | 0 | 42 |
|---|---|---|
| `seed` | The pile holds the bite, a `human` Jeles nugget answers it, or a sealed write-back holds it | Otherwise; the bite is logged as an open Jeles gap |
| `lookup` | Hits | Nothing found |
| `turn` | No proposals | The model's proposals, until sealed |
| `prompt` (hook) | Always exits 0 (Claude Code) | Its document carries `code: 42` when nothing is found |
| `escalate` | No card | The card |
| `reconcile`, `read-misses` | Every outcome shown sealed | Otherwise |

1 / 2 / 3 are unchanged: refused or `unreachable`, a bad command line, the box won't open. The three states (INVARIANTS.md §1) are untouched; 42 is the exit code, not a fourth state. Escalating is the step a 42 asks for.

## §5 Where things are

| File | Holds |
|---|---|
| `one-script/onescript/opening.py` | The box's front door: Config, keys, law, `open_box`, `repos.json` |
| `one-script/onescript/prompt_path.py` | `prompt`, and its `ESCALATE` copy |
| `one-script/onescript/boxstore.py` | Store key, `_open_store`, `_lookup` |
| `one-script/onescript/stamp.py` | The write token |
| `one-script/onescript/record.py` | Parse cache, sealed-tip readers (`tail_state`, `since_last`, `has_kind`) |
| `one-script/onescript/pile.py` | `Cached` (lazy), `_bad_rows`, `ChunkReader`, `merge`, `score_grams` |
| `one-script/onescript/api.py` | `ESCALATE = 42` and its doc; the 42 rule per verb |
| `one-script/onescript/jeles_store.py` | Jeles as the pile's next rung; `log_gap` |
| `one-script/genesis.py` | The reference (`claude/genesis`) |
| `one-script/onescript/tests/test_human_said.py`, `test_store_lazy.py`, `test_record_tip.py`, `test_record_cache.py`, `test_prompt_path.py` | The tests for the above |
| willow-mcp `src/willow_mcp/onescript_executor.py` | `ESCALATE`, `_shape`, `_finish` |
| Grove `docs/design/one-script/flatten-2-2026-10-21.md` | Rulings F-1 to F-43, open questions O-1 to O-7 (`claude/flatten-2-rulings`) |
| Grove `docs/design/one-script/flatten-2-guesses-2026-10-21.md` | Guesses and their Brier score (`claude/flatten-gaps`) |

## §6 Running it on your machine

Paths are the container's; put your own checkouts in their place.

| Step | Command |
|---|---|
| A box over many repos | `python -m onescript --box <box> --keys <keys-dir>/keys.json --repo willow-bot=<path> --repo willows-grove=<path> … --no-tests checkin` (from `willow-bot/one-script`). The container's box used 20 repos: willow-bot, willows-grove, willow-mcp, ratatosk, Forge, safe-app-store, nestor, corpus-lens, homestead, homestead-law, homestead-ledger, kartikeya, utety, willow-gate, homestead-health, almanac-template, forge-workshop, willow-reconciler, jeles, oakenscrolls-office. The store builds in the background (about 4 minutes there) |
| A lookup | `echo '{"prompt": "…"}' \| python -m onescript --box <box> --keys <keys>/keys.json prompt`; the `--repo` list is read back from `repos.json` |
| Jeles | `pip install <jeles checkout>` into the bot venv; `jeles-seed --init-local` (signs the manifest with your own GPG key); export the three variables it prints; `jeles-seed`. A pair lands as yours only if it carries a Nestor seal that verifies on your machine |
| The reference | `python one-script/genesis.py test`; `python one-script/genesis.py run --box DIR --check "pytest -q"` |
| Index only merged work | Check each repo out at its default branch before check-in (§8, item H) |

## §7 Measurements

20-repo box (835,855 chunks, 9,155 files, 292 MB store):

| Prompt | Before (main) | After (`7b13b7a`) |
|---|---|---|
| "record append chain anchor" | 14.71 s | 1.45 s |
| "the store key lives in the keys dir" | 14.47 s | 4.30 s |
| "calibration brier bins" | 9.49 s | 1.41 s |
| Opening the store | 8.7 to 16.2 s | 0.66 s |

Of a common-word prompt now (about 4.3 s): `rank` scoring every hit about 3.6 s under the profiler, the row check 0.67 to 0.84 s, the store's `file_sha256` 0.27 to 0.57 s. Test box: hook modules 39 → 16; a 20,036-row record with a sealed tip prompts in 23 ms.

## §8 What's left

| # | Item | Size |
|---|---|---|
| A | Check the store's rows once per store hash, not every open (saves 0.7 to 0.8 s a prompt) | about 20 lines |
| B | Rank by chunk id and read rows only for the top hits (most of the 3.6 s) | about 60 lines |
| C | An over-cap prompt says `empty` ("narrow the stack"); a ruling is needed | — |
| D | `checkout` can send wagers to the human and still exits 0 | small, now that #728 exists |
| E | Compaction of the record (F-40 ratified, nothing built) | — |
| F | The prompt hook never asks Jeles; only `seed` does | — |
| G | Rat exits 0 on "escalated"; under F-43 its unanswered pieces are 42 | ratatosk |
| H | The container's box indexed Grove at `claude/flatten-gaps`, 7 commits past `master`: not all of the pile was the operator's yes | — |
| I | `genesis.py`: push, and decide whether its 0 can mean more than "the checks passed" | — |
| J | Jeles labels public-record commons `human`, with `verified_at` the load date and `evidence.sealed: false`; nuggets with no kind count as `human` | Jeles |

## §9 Open questions

From the rulings doc: O-1 where the session was meant to go; O-2 NFC and folding; O-3 extra merge gates; O-4 which loop closes first; O-5 the side bar, words or hashes; O-6 how ΔΣ=42 is stamped on documents (a stamp outside the hashed bytes moved from 42 to 43 unseen in willow-mcp `91a752e`); O-7 the stamp for a finished document.

## §10 What the cloud container held

Gone when the container is reclaimed:

| Item | Where it was |
|---|---|
| `claude/genesis` (`7831eae`, `4b40db9`) | willow-bot worktree `/home/user/wt/genesis`, not pushed |
| The 20-repo box, its keys and store | `willow-bot/.flow/onescript-all*` |
| A Jeles store (1,149 nuggets: 821 public record, 328 asserted) and a throwaway gpg key | the session scratchpad |
| Jeles 0.16.1 installed in the bot venv | `/root/willow-bot/venvs/willow-bot` |

ΔΣ=42
