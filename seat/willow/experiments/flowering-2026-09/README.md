# Flowering step 0 fixtures (2026-09)

Frozen scenario prompts and excerpt bundles for the pre-registered protocol in
`docs/design/forge-convergence-flowering-experiment.md`.

- **Ids:** `S-growth-01` … `S-growth-12` frozen 2026-09-24 from the live desk queue, open forge-convergence gaps, and two policy excerpts. Uncommitted. G4 `S-growth-10` is excluded from the *T* numerator.
- **Hash:** `manifest.json` T0 partial — directory digest + git rev from Kart `M0G98TQ8`; wiring hash and full Ollama tag snapshot still open.
- **Runner (verified):** Host `serve` + Kart `client` with `$WILLOW_HOME` in the worker env (`DUM8A507`, `SWFPHQNB`). **One Ollama model at a time** — serial batches only (one Kart `batch` task per model, or one task that runs `client` for each tier in order). Do not submit parallel `client` tasks for different models; they contend on GPU and the socket and multiply Kart retries. Restart `serve` after willow-bot code changes (Ollama timeout). Kart wrapper must not use `set -e` on `client` when partial fixture errors are expected, or Kart will retry the whole tier. `ladder` is for the host or a single serial Kart task after `serve` is current. Measured bad: `UVYL87MG`, parallel `W6J22XPK` / `MWPR2N7N` / `T42324JX`. Good: `054501Z` (llama3.2:3b), `054523Z` (willow-lane4-3b). Per-class rubric scoring not run yet.
- **§8 chain (2026-09-24):** Four tiers clean via `CTR0WBSE` (`075953Z` … `082425Z`). **`qwen3:4b` blocked** — latest Kart batch `C963U3U6` → `174449Z`, **11/12** errors, **~120.1s** timeouts (same wall as `133444Z`); probe timed out at **90s**. Use Kart **`lane=batch`** (not `fast`’s **300s** wall). `think:false` in tree did not change latencies on that run — desk added **`ollama_chat_timeout_s`** (600) in policy + `status` reports `runner.ollama_chat_timeout_s`. After `pip install -e` + unit restart, copy `ollama_chat_timeout_s` into `$WILLOW_HOME/willow-bot/deterministic-policy.json`, then rerun qwen on **batch** lane. Manifest: `qwen3_step0_think_false_C963U3U6`.

Nothing in the scenario files is model output — only frozen inputs.
