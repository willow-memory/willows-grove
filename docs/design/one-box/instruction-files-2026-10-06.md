# Instruction files across every CLI — AGENTS.md, CLAUDE.md and the rest (2026-10-06)

Desk session `session_01AEYnPWKuWa4xmU3ZnsAZTS`, 2026-10-06, persona `willow`.
Companion to [`research-2026-10-06.md`](research-2026-10-06.md) (the pre-tool
hook matrix): same CLIs, same source rule, a different question — **how does
each agent find, combine and present its instruction files?**

Operator's ask, verbatim: "I want to know how those all respond to agent. MD or
call.md, obviously I know that one, type files." Pushed to its own branch at the
operator's word ("you can push it to a new branch and I'll just merge it into the
one I'm working on").

**Agent-reported. Nothing here is sealed.** Nothing was wired or changed outside
this file and the one-box README's reading list.

---

## 0. Source rule and tags

Five research agents, one per group, under the same rule as the hook matrix:
the vendor's docs page read directly; if blocked, the docs or source in the
vendor's own GitHub repo (shallow-cloned, read, never run); search extracts only
as a last resort, marked as such. No mirrors or third-party blogs.

| Tag | Meaning |
|-----|---------|
| **D** | vendor docs page, read directly |
| **R** | vendor's official repo — committed docs (`R-doc`) or the loader's source (`R-src`), with file:line and commit |
| **B** | strings in the vendor's published binary (Amp only) |
| **S** | search-engine extract, **not read** — a lead, not a finding |

**Read directly (D):** Claude Code only (`code.claude.com/docs/en/memory`).
**Blocked:** cursor.com, docs.cursor.com, docs.windsurf.com, docs.devin.ai,
kiro.dev, geminicli.com, qwenlm.github.io, agents.md, developers.openai.com,
docs.github.com, ampcode.com, docs.factory.ai, docs.augmentcode.com,
docs.warp.dev, junie.jetbrains.com, www.jetbrains.com.

**Repos read, by commit:**

| Repo | Commit |
|------|--------|
| google-gemini/gemini-cli | `fb972b2f87fe` |
| QwenLM/qwen-code | `b2c95e04dc53` |
| agentsmd/agents.md (the spec site's source) | `d001185d792e` |
| openai/codex | `822e58cc3d66` |
| github/docs | `45a0f053ac67` |
| microsoft/vscode-docs | `279a4a77ecb4` |
| microsoft/vscode-copilot-chat | `5863f5a70889` |
| @sourcegraph/amp (npm, binary strings) | `0.0.1791244891-g160ca9` |
| cursor/cookbook, cursor/cursor, cursor/plugins | `6733ef8`, `654b1b4`, `df58112` |
| kirodotdev/Kiro, kirodotdev/spirit-of-kiro | `bfe7ff3`, `ff0c8c2` |
| Exafunction/codeium, Exafunction/windsurf.vim | `5909346`, `3c0a4f8` (no rule loader in either) |
| aaif-goose/goose | `104ddde585` |
| cline/cline | `dec80dadfa` |
| RooCodeInc/Roo-Code | `b867ec9145` |
| anomalyco/opencode | `652c090dc1` |
| Aider-AI/aider | `5dc9490bb3` |
| continuedev/continue | `5522c6f44c` |
| charmbracelet/crush | `8da349060b` |
| Factory-AI/factory (docs) | `c6ea470` |
| warpdotdev/docs | `46935ea` |
| zed-industries/zed | `a1b7107` |
| aws/amazon-q-developer-cli | `15cc8f3` |
| augmentcode/auggie | `9cc3ead` (changelog only) |
| JetBrains/junie | `e75d6ee` (installers only) |

---

## 1. The matrix

**Walk** = reads parent directories. **Nested** = reads files in subdirectories,
and when. **Where** = where the text lands in the model's context.

| CLI | Own file | AGENTS.md | CLAUDE.md | Walk | Nested | Combine | Imports | Where | Tier |
|-----|----------|-----------|-----------|------|--------|---------|---------|-------|------|
| **Claude Code** | `CLAUDE.md`, `.claude/CLAUDE.md`, `CLAUDE.local.md` | **only if no CLAUDE.md** anywhere up the tree (default; setting can change) | yes | to filesystem root, at launch | lazy, on Read/Write/Edit there | concatenate; root → cwd, local after | `@path`, 4 hops | **user message** after the system prompt | D |
| **Gemini CLI** | `GEMINI.md` | **only if configured** (`context.fileName`) | no | to git root (`.git` marker) | lazy (JIT), on tool access | concatenate with `--- Context from ---` | `@path`, depth 5 | **system prompt** ("foundational mandates") | R |
| **Qwen Code** | `QWEN.md`, `.qwen/QWEN.local.md` | **yes, by default** | no | to git root, else home | not found (rules with `paths:` are lazy) | concatenate; all QWEN.md before all AGENTS.md | `@path`, depth 5 | system prompt suffix | R |
| **Codex CLI** | `AGENTS.override.md` → `AGENTS.md` → fallbacks | **yes** | no (fallback config only) | git root → cwd, eager | not loaded; model told to look | concatenate root → cwd; **32 KiB total, then truncated** | none | **user** message | R |
| **Copilot CLI** | `.github/copilot-instructions.md`, `.github/instructions/**/*.instructions.md` | yes | yes (+ GEMINI.md) | root, cwd and between | dirs on paths being worked on | additive, "no general precedence order" | `@relpath`, repo only | ? | R |
| **Copilot cloud agent** | same | yes, nearest wins | root only | — | AGENTS.md anywhere | additive | — | ? | R |
| **Copilot in VS Code** | same + `.claude/rules` | yes | yes (setting) | — | nested AGENTS.md **off by default** | additive, "do not depend on a file order" | Markdown links | **system** by default | R |
| **Amp** | `AGENTS.md` (fallback `AGENT.md`, `CLAUDE.md`) | yes | fallback | to `$HOME` | lazy, when a subtree file is read | additive; **oversized files dropped** | `@path`, globs | ? | S / B |
| **Cursor** | `.cursor/rules/*.mdc`, legacy `.cursorrules` | yes | yes, always applied | ? | nested `.cursor/rules` | Team → Project → User | ? | ? | S |
| **Windsurf / Devin Desktop** | `.devin/rules/*.md` (→ `.windsurf/rules`), legacy `.windsurfrules`, `global_rules.md` | yes (root always-on; subdir as glob rule) | unconfirmed | ? | subdir AGENTS.md as glob rule | system rules merged without overriding; 6k / 12k char caps | @-mention by name | ? | S |
| **Kiro** | `.kiro/steering/*.md` | yes, always included | not found | — | AGENTS.md "next to the code" | workspace beats global | `#[[file:…]]`, `file://` | ? | S |
| **Factory droid** | `AGENTS.md`, `~/.factory/AGENTS.md` | yes | changelog line only | to repo root | subfolders worked in | **docs contradict** (first match / closest / collect all) | none | "system reminders" | R |
| **Augment Auggie** | `.augment/rules/**`, `.augment-guidelines` | yes | yes (read first) | edited file → workspace root | yes (AGENTS/CLAUDE only) | all; 24,576 / 49,512 char caps | none | attached to request | S (+R changelog) |
| **Zed** | `.rules` + 8 others, **first match only** | yes (7th) | yes (8th) | **none** | **none** | one file per worktree root; project beats personal | none | **system prompt**, fenced | R |
| **Warp** | `AGENTS.md`, `WARP.md` (wins in same dir) | yes (default) | **no** (`/init` can link) | root + current dir | subdir best-effort | subdir → root → global | none | ? | R |
| **Junie** | `.junie/AGENTS.md` (exclusive), else root `AGENTS.md` + `.junie/rules/*` | yes | not mentioned | root only | no | exclusive tiers, else concatenated | none | ? | S |
| **Amazon Q CLI** | `AmazonQ.md`, `README.md`, `.amazonq/rules/**` | yes (**source; docs omit it**) | no | relative to cwd | no | all loaded; **75% of context, oversized dropped** | glob resources | **user message**, fenced | R |
| **Goose** | `.goosehints` | yes | only if configured | git root → cwd, eager | lazy, from tool-call paths | Global Hints, then Project Hints | `@path`, depth 3, 1 MB, git-root bounded | system prompt | R |
| **Cline** | `.clinerules` (file/dir), `.cline/rules/` | yes (root + `~/.agents`) | no | no | no | keyed by name; **later dir overwrites — global beats workspace** | none | system prompt `# Rules` | R |
| **Roo Code** | `.roo/rules*/`, `.roorules[-mode]`, `.clinerules[-mode]` | yes (+ `AGENT.md`, `AGENTS.local.md`) | no | no | only with `enableSubfolderRules` | global → mode → AGENTS → generic | none | system prompt | R |
| **OpenCode** | `AGENTS.md` → `CLAUDE.md` → `CONTEXT.md` (first name that exists) | yes | yes (fallback) | cwd → worktree root, eager | lazy via read tool, as `<system-reminder>` | global first, then project | **none** (`instructions` config: globs, URLs) | system prompt | R |
| **Aider** | **none** | no (only via `--read`) | no | — | — | — | — | **user message**, "READ ONLY files" | R |
| **Continue** | `.continue/rules/**`, `.continuerules`, `rules.md` anywhere | yes — **effectively the only agent file (bug)** | listed, unreachable in IDE | — | `rules.md` scoped to its dir | globs, regex, alwaysApply | none | system message | R |
| **Crush** | `CRUSH.md` + 15 others (copilot, cursor, CLAUDE, GEMINI…) | yes | yes | **no** (working dir only) | no | **map order — not deterministic** | none | system prompt `<project_context>` | R |

---

## 2. What answers the operator's question

### Who reads AGENTS.md

**Read natively (19 of 22):** Qwen, Codex, Copilot (all surfaces), Amp, Cursor,
Windsurf, Kiro, Factory, Augment, Zed, Warp, Junie, Amazon Q (source), Goose,
Cline, Roo, OpenCode, Continue, Crush.

**Conditionally:**
- **Claude Code** — only when no `CLAUDE.md`, `.claude/CLAUDE.md` or
  `CLAUDE.local.md` exists in the working directory or above. The *Project
  instructions* setting can be `claude-md-and-agents-md` to read both [D].
- **Gemini CLI** — only when added through `context.fileName`; the setting adds
  names in front of `GEMINI.md` rather than replacing it [R-src].
- **Aider** — never by name; only when passed with `--read` or `read:` [R-src].

### Who reads CLAUDE.md

Claude Code (natively), Copilot (CLI, cloud agent, VS Code by setting), Amp
(fallback), Cursor (always applied, S), Augment (read before AGENTS.md, S), Zed
(8th in its first-match list), OpenCode (fallback after AGENTS.md; also
`~/.claude/CLAUDE.md`), Crush, Continue (listed but unreachable in the IDE —
bug), Factory (one changelog line). **Not:** Gemini, Qwen, Codex, Kiro (not
found), Warp, Junie (not mentioned), Amazon Q, Goose (unless configured), Cline,
Roo, Aider. Windsurf Desktop unconfirmed; the separate Devin CLI reads it (S).

### The AGENTS.md convention vs what tools do

The spec (agentsmd/agents.md @ `d001185`) says: a file at the repository root;
"the closest one takes precedence"; "explicit user chat prompts override
everything"; plain Markdown, no required fields, no imports, no size rule. It is
"stewarded by the Agentic AI Foundation under the Linux Foundation" [R-src].

**Almost nobody implements "closest wins".** Claude Code, Gemini, Qwen, Codex,
Goose, OpenCode and Copilot CLI *concatenate* every file found and rely on order
or prompt wording to resolve conflicts. Zed, Junie and Codex's per-directory
candidate list are *first match*. Only Copilot's cloud agent states nearest-wins
as behaviour, and Codex states it in the base prompt rather than the loader.

The spec's own list of supporting tools omits Claude Code and Qwen Code — both
read AGENTS.md in some form.

### Where the text lands — and what the model is told about it

| Lands as | CLIs |
|----------|------|
| **system prompt / system message** | Gemini ("foundational mandates… absolute precedence over… tool defaults", but not over safety), Qwen, Zed, Goose, Cline, Roo, OpenCode, Continue, Crush, Copilot in VS Code (default) |
| **user message** | Claude Code ("context, not enforced configuration"), Codex (`<INSTRUCTIONS>`), Amazon Q (`--- CONTEXT ENTRY ---`), Aider ("READ ONLY files") |
| **tool output** (lazy finds) | Gemini JIT (`--- Newly Discovered Project Context ---`), OpenCode (`<system-reminder>`) |
| **unknown** | Copilot CLI and cloud agent, Amp, Cursor, Windsurf, Kiro, Warp, Junie |

**None of the 22 treats instruction files as untrusted data.** Gemini wraps tool
and MCP output in `<untrusted_context>` but not context files. The nearest things
to a guard: Claude Code asks before an `@import` leaves the project; Goose bounds
`@` imports to the git root and skips `.gitignore`d files; Qwen and Codex skip
project files in untrusted folders; Zed gates project *skills* (not rules) on
worktree trust.

---

## 3. Bugs and docs-vs-source disagreements found on the way

| CLI | Finding | Tier |
|-----|---------|------|
| Continue | `loadMarkdownRules.ts:47`: the `break` runs whether or not the file exists, so after `AGENTS.md` the loop stops — `AGENT.md` and `CLAUDE.md` are never checked in the IDE | R-src |
| Crush | Paths deduped by `strings.ToLower` and the key claimed even when the file is missing (`prompt.go:153-161`), after a sort (`load.go:626`): on a case-sensitive filesystem `crush.md`, `Crush.md`, `gemini.md`, `agents.md`, `Agents.md` are never read. The prompt is built by ranging over a Go map (`prompt.go:233-238`), so file order is not deterministic | R-src |
| Cline | Docs say `.cursorrules`/`.windsurfrules` are auto-detected and `paths:` conditional rules work; the live SDK loader does neither (only unreached legacy code does). Docs say workspace rules win; in source a later directory overwrites an earlier one by name, and global dirs come last — **global beats workspace** | R-src vs R-doc |
| Goose | Docs give the default order as `AGENTS.md`, `.goosehints`; source has `.goosehints` first (`load_hints.rs:13-24`). Source also reads an undocumented `~/.agents/AGENTS.md` | R-src vs R-doc |
| OpenCode | `OPENCODE_DISABLE_CLAUDE_CODE_PROMPT` drops the project `CLAUDE.md` too, not only `~/.claude/CLAUDE.md` as documented; global is added before local, the reverse of the docs | R-src vs R-doc |
| Amazon Q | Default agent loads `AGENTS.md` in source; the docs' list omits it | R-src vs R-doc |
| Codex | Base prompt says AGENTS.md is "included with the developer message"; the code sends it as a `user`-role fragment | R-src |
| Factory | One page says "first match wins", the same page says the closer file "takes precedence", and the changelog says "collect all AGENTS.md and CLAUDE.md files" | R-doc |
| Gemini / Qwen | `context.fileName` *adds* to `GEMINI.md` in Gemini but *replaces* `QWEN.md, AGENTS.md` in Qwen — neither docs page says so | R-src |

---

## 4. What this means here

**This repo has a `CLAUDE.md` and no `AGENTS.md`.** So today:

- Claude Code reads `CLAUDE.md`. An `AGENTS.md` added beside it would be
  **ignored** by Claude Code under its default setting.
- Copilot, Amp (fallback), Cursor, Augment, Zed, OpenCode (fallback) and Crush
  read the `CLAUDE.md`.
- Gemini, Qwen, Codex, Kiro, Warp, Junie, Amazon Q, Goose, Cline, Roo and Aider
  see **no instructions at all** from this repo.

**The one layout that reaches nearly every CLI without inventing anything** —
using only behaviour the matrix records, for the operator to choose:

1. `AGENTS.md` at the root holds the instructions (read natively by 19 of 22).
2. `CLAUDE.md` shrinks to one line, `@AGENTS.md`. Claude Code imports it (D:
   `@path` imports, 4 hops); Copilot CLI expands `@relpath` in CLAUDE.md too.
   Zed, Crush, OpenCode and Augment would then see either file — Zed takes only
   the first match (`AGENTS.md` precedes `CLAUDE.md` in its list), OpenCode
   stops at `AGENTS.md`.
3. Gemini needs one setting (`context.fileName: ["AGENTS.md"]`), Aider one
   `read: AGENTS.md`. Everything else needs nothing.

Caveats on that layout: Claude Code puts it in a user message, Gemini in the
system prompt — the same file carries different weight per CLI. Codex truncates
past 32 KiB total, Amazon Q and Amp drop oversized files, Windsurf caps a
workspace rule at 12,000 characters (S): keep it short. And the seat: CLAUDE.md
says the seat comes from `session_enter`, not from prose — that sentence would
need to live in `AGENTS.md` for the other CLIs to see it.

**For serve and the trust labels.** No CLI treats an instruction file as data.
Anything written into `AGENTS.md`, `CLAUDE.md` or a rules folder reaches the
model as instructions on every one of the 22. That settles where the served file
must *not* go: a file carrying `untrusted` tables cannot be an instruction file,
or a rules-directory entry, or anything a CLI auto-loads — or its trust label is
read as an order. Serve's output belongs in a path no CLI's loader matches, read
by the hook-allowed `Read`.

---

## 5. Open items

| Item | Whose |
|------|-------|
| Choose whether to adopt the `AGENTS.md` + `@AGENTS.md` layout (§4) | operator |
| Allow the blocked docs domains (§0) to lift Cursor, Windsurf, Kiro, Amp, Junie and Augment out of S | operator |
| Report the Continue, Crush and Cline loader bugs upstream | operator's call |
| Confirm where Copilot CLI, the cloud agent, Amp, Cursor, Windsurf, Kiro, Warp and Junie inject instruction text | next pass |

## 6. What this doc does not do

- It does not add, move or change any `AGENTS.md`, `CLAUDE.md` or settings.
- It does not promote S-tier cells to findings.
- It does not touch the vault. The vault is Sean's key.
