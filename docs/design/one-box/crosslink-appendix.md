# One-box crosslink appendix — strengthen vs contradict

Reads that sit beside the plan: nest notes, Sovereignty Test language, gate
runbooks, Ollama posture. Goal: name what **strengthens** one-box and what
**contradicts** it so the next bite does not paper over the seams.

Sources: SOIL orgpass folds, nest-inbox-read (no PII),
[outside-2026-10-02.md](outside-2026-10-02.md).

---

## Strengthen

| Source | How it strengthens |
|--------|--------------------|
| nest P5 overnight / morning | Same shape as D6 SessionEnd detach + desk view |
| nest P6 stamp chain | Receipts for OUT / packet custody |
| nest P7 heartbeat | Timing for reverse without wall-clock-only timers |
| outside OW5 Cursor V | `followup_message` + loop_limit make Cursor OUT real |
| outside OW6 Goose / Windsurf | Narrows which events can actually block |
| outside F8 frp pin | Concrete floor for D10 tool choice |
| net_signer 0660 + peercred pattern | Template for forge.sock / bot sock hardening |
| Nestor WebCrypto seal | Browser-side confirm already unforgeable by loopback process |

---

## Contradict (or tension)

| Source | Tension |
|--------|---------|
| **Ollama on HTTP 127.0.0.1:11434** | Declared exception in README §2b; nest / local-model notes treat HTTP as normal. Portless rule has an honest hole until OW2 UDS lands (still open) |
| **Sovereignty Test vs D10** | Sovereignty language can read as "no remote ingress ever"; D10 allows **opt-in** frp under operator control. Keep both: default closed, declared exception when opened |
| **Gate runbook / `gates --serve`** | Runbooks that assume a Gate *service* clash with "willow-gate is a library." Authless :8788 is a hazard, not the Gate |
| **polyhook as Phase 3 adopt** | #78 open — Windsurf wire format wrong; JSON respond ignored. Hold or dual-path |
| **Kiro ACP opacity** | PreToolUse exit-2 may not reach ACP clients (#9494) — OUT dialect table must say so |

---

## Three-dialect OUT (born-next #2)

One `render_stop` / block reason must speak three dialects:

| Dialect | Front ends | Mechanism |
|---------|------------|-----------|
| **Cursor JSON** | Cursor | Hook JSON: `followup_message` / permission fields; respect **loop_limit** (default 5) |
| **exit 2** | Windsurf, Kiro (shell hooks) | `pre_*` hooks refuse with process exit code 2; post hooks cannot block. Kiro: may be invisible to ACP clients |
| **Goose PreToolUse** | Goose | Only **PreToolUse** and **Stop** honor block; BeforeShellExecution / UserPromptSubmit denials are **ignored** |

Claude Code / Codex / Gemini / Qwen remain the better-verified OUT set in
research §2b; this table is the *minimum* for the commercial second proof
(D9) once Cursor / Windsurf / Goose are in scope.

---

## Operator questions this appendix carries

| Id | Question |
|----|----------|
| **Q3** | Does Sovereignty Test language need a one-line amendment to match D10 opt-in frp? |
| **Q4** | Soft verify: any 0.0.0.0 listener beyond Matrix bridge? (Kart / host measure) |
| **Q5** | Which commercial front end is the second OUT proof (D9) — Cursor first? |
| **Q6** | Retire or auth `gates --serve` before writing more Gate runbook? |
| **Q7** | Keep Ollama HTTP as standing exception, or block Phase 7 until UDS? |
| **Q9** | polyhook: pin + wait #78, or write native Windsurf adapter now? |

Q3 / Q5 / Q6 / Q7 / Q9 need operator words. Q4 is verify-pass.

---

## What this appendix does not do

Invent seals. Close Q1–Q18. Drain nest. Re-index CBM (Q18).
