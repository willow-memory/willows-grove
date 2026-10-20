# Deterministic systems the flatten didn't cover (2026-10-20)

§1 What the flatten covered · §2 Not covered: copies of one rule · §3 Not covered: randomness F-14 missed · §4 Kept out on purpose · §5 Method and limits

*Cloud session `012onBhQDT2rhEYjuoFDQtha`, 2026-10-20. Persona: willow, by desk default
(`session_enter` did not run). Agent-reported; not ratified. The operator: "take a look at the
one script, and come up with a list of other deterministic systems that are not covered by
what's come out of the flattening." Read beside [`flatten-2026-10-19.md`](flatten-2026-10-19.md).*

## §1 What the flatten covered

| Phase | One of each |
|---|---|
| F1 | The stream (`sha256-stream/v1`) |
| F2 | The record chain, for the table and the 5e scripts |
| F3 | The seal, for decision beats |
| F4 | The games' randomness: dice, dice5e, odds, pools, xorshift, the daily seed |
| F5 | The venv resolver and the Python three-state type |
| F6 | The wagers (deck, market) |

Everything below is code that gives the same output for the same input, runs in more than one
place (or is unseeded where it should be seeded), and has no flatten row.

## §2 Not covered: copies of one rule

Ranked by how much else depends on each one.

| # | System | What was found | Why it matters | Confidence |
|---|---|---|---|---|
| 1 | **Canonical JSON** (the bytes that get hashed) | About 25 definitions across six repos. The one script has two of its own (`record.canon`, `xref.canon`), plus `session.canonical`. Others: willow-bot `deposits._canonical`; willow-mcp (8: `constitutional`, `bound_receipt`, `dispatch_signing`, `session_binder`, …); safe-app-store `sap_gate`, `store_reconcile`; Forge `trust` | Every chain, seal and signature hashes these bytes. Two serializers that differ by one separator give different hashes for the same row | 90% |
| 2 | **Hash chains outside the one record** | willow-mcp: `receipts`, `governance_ledger`, `attribution_ledger`, `bound_receipt`, `commitment_ledger`. willow-bot: `deposits` (with its own `verify_chain`), `steward/tick`. safe-app-store: `playgate/audit`, `aristarchus/store`, `intake-desk` `verify_chains`, `ai-game-master/verify_ledger`, `agm_head`. Grove: `grove_db` | F-1 made one chain only for the table. About 12 other chains each have their own row shape and their own verifier | 85% |
| 3 | **Signing and keys** (Ed25519) | About 24 files. One script: `nestor_seal`, `serve`. Grove: `u2u/identity`, `u2u/packets`. safe-app-store: `sap_gate`. Forge: `promotion_trust`. willow-mcp: `keyring`, `seal_ring`, `net_signer`, `session_signing`, `human_session`, `egress_authorization`, … | F3's "one seal" covers decision beats only. The human's key is signed and checked by several separate code paths | 80% |
| 4 | **Calibration scoring** (`brier`, `log_score`, `bins`) | 5 copies, and every file hashes differently: `onescript/calibration.py` (vendored from Forge), `Forge/forge/calibration.py`, `safe-app-store/stores/_forge_extracted/calibration.py`, `oakenscrolls-office/calibration.py`, and `play.py`'s `brier` (frozen) | The ledger's whole claim is its scores. Copies that drift would grade the same call differently | 95% |
| 5 | **Clock and stamps** (`_utc_now`, `_now_iso`) | About 20 helpers (willow-mcp alone has 12), plus deadline arithmetic in `market` (13:00 UTC) and `beacon` | Stamps are hashed into rows, so their format is part of the hash. A test can't pin time without one clock seam | 75% |
| 6 | **Redaction and scrub** | About 12: `serve._scrub`, Grove `seat_record.scrub` and `grove_reader.redact_db_error`, ratatosk `redact` and `cassette.scrub_result`, nest-pipeline `secrets.redact_text`, willow-mcp `observability` and `push_executor`, willow-bot `steward/ingress.redact_url` | Each has its own list of what counts as secret. A secret one of them misses leaks through that surface | 80% |
| 7 | **Text normalizing and tokenizing for lookup** | `seed.words`, `pile.py`, Grove `seat_boxes._words` and `table_boxes._tokens`, ask-jeles `kb_search` and `search`, `loki/semantic` | The ladder's `bite_key` is a hash of normalized words. A second normalizer means the same bite gets a different count | 70% |
| 8 | **Routing ladders** | The one script's repetition `ladder.py`, the source ladder in `resolve.py`, `escalate.py`, ratatosk's `ladder.py` and `provider_ladder.json`, willow-bot `deterministic/policy.py` and `chain.py` | Five deterministic answers to "who answers this next". They don't duplicate each other line for line, but no single record says which one decides | 60% |
| 9 | **Three-state, the parts F-18 didn't reach** | 7 Grove JS modules (`web/components`, `web/boot`) restate the three states. In the one script itself, `boot.py`, `jeles_store.py` and `writeback.py` declare their own constants, including the variants `ranked` and `held` | F-18 made one type for Python only | 85% |
| 10 | **Byte-identical and drifted copies** | Identical: nest-pipeline `ocr`, `taxonomy`, `db` (safe-app-store `libs/` and willow-mcp `nest/`); willow-mcp `hooks/*` and `bundle/hooks/*`. Already differ: `subject_consent/core` (2), `changelog_dedup` (Forge, willow-mcp), `measure_panel` (Forge, `_forge_extracted`) | These are F-2 "one pile" candidates, outside randomness | 95% |

## §3 Not covered: randomness F-14 missed

F-14 said "all of them", but these sources were not brought in.

| Where | What it does | Confidence |
|---|---|---|
| `aetheris5e/gm5e.py:53`, `sealed_run.py:45`, `combat.py:295` | Seeds from `os.urandom`. The run is on neither the stream nor the beacon, so it can't be replayed | 90% |
| the-table `baseline.py`, `pools.py:170`, `proof.py:76`; `aetheris5e/monte_carlo.py` | The random play policy uses a Mersenne `random.Random(seed)`, not `sha256-stream/v1` | 85% |
| the-table `game_engine_adapter.py:203`, `story_session.py:218` | The global `random.seed(seed)`, marked "LEGACY only" | 90% |
| Four adapters (`backgammon`, `hearts`, `crazy_eights`, `liars_dice`) | Fall back to `random.Random(seed)` when no `rng_factory` is passed | 75% |
| game-lab `sims/` (7 files), semantic-translator `quiz`, ask-jeles `hero_scene`, civics | Seeded on their own. game-lab left F-14's scope when F-13 withdrew the move | 60% |

## §4 Kept out on purpose

These are not gaps.

| Item | Decision |
|---|---|
| catgrid and bureau `web/engine.js` xorshift | F-15: kept for the JS ports, held by a parity test |
| The gates (`gate.py`, willow-mcp `pre_tool_use`, `sap_gate`, `egress_authorization`, playgate) | Flatten §4: "the walls" stay untouched |
| `play.py`, `peaks.py`, the baselines | Frozen records (rule 12) |

## §5 Method and limits

- **Method:** grep for function definitions, file hashes (md5) and imports across willow-bot,
  willows-grove, safe-app-store, willow-mcp, ratatosk and Forge at their default branches on
  2026-10-20, with test directories left out. Counts are approximate.
- **Not searched:** Nestor and Jeles were not in the session's container.
- **Biggest single lever:** a canonical-JSON module in `onescript/` that the other copies
  import. The chains (§2 row 2) and the signing paths (row 3) both rest on those bytes, so they
  would follow from it.
- **Status:** a list, not a decision. No phase is opened by it; each row waits on the operator.
