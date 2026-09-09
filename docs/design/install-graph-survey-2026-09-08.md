<!-- b17: WGRV1 -->
# Install-graph survey — Grove docs vs this box

Written 2026-09-08. Answers gap `a0d7fd8ec389`: how would a box know
what is installed and wired? This is a survey, not a detector.

Companion: [vault-home-store.md](vault-home-store.md) §4.

---

## What Grove already says

**Base vs add-on**
([willow-grove-premise.md](willow-grove-premise.md)): Grove’s base is
willow-mcp + the willow-memory charter + this repo. Everything else is
opt-in. Absence is a state, not a failure. Nestor, Jeles, Oakenscrolls,
UTETY, almanacs, homestead, Forge, Ratatosk, vault, gate, Kart,
corpus-lens are add-ons when present.

**Die faces / Möbius**
([FLEET_PLACEMENT_DRAFT.md](../../governance/FLEET_PLACEMENT_DRAFT.md)):
GitHub orgs do not nest. Die-Namic Systems is the **center** (Nestor),
not a hub that owns the other orgs. Faces take **versioned contracts**,
not “import the other app.” Die-Namic expands by **more installs**, not
more repos (~1 product: `nestor`).

**Circular test graph**
([fleet-standup.md](fleet-standup.md)):

```
willows-grove → willow-mcp → kartikeya
                    ├─────────► jeles
                    └─────────► nestor [nestor extra]
                                    └──► willow-gate [gate extra]
nestor ──(charter cases)──► willows-grove
```

**Five transports**
([fleet-wiring.md](fleet-wiring.md)): Postgres, Nestor stdio JSON-RPC,
in-process/HTTP journal, willow-mcp socket PG, agent MCP. Plus Python
imports (mcp→Kart, nestor→gate) and a filesystem path (nestor→charter).

**Canon**
(`governance/seed/canon/05-the-world.md`): willow-mcp is the memory
server; Kart is a hard dependency; gate is check-in plus friction_floor.

Stale in those docs (this box has moved): `forge-play` is no longer
“WIP”; Forge lives under `forge-play/`, not only `rudi193-cmd/Forge`;
Jeles is `hornbook-knowledge/Jeles`; live PG here is 18 / `willow_20`.

---

## What is wired on this box (2026-09-08)

**Org folders under `~/github`:** Die-Namic-Systems, willow-memory,
almanac-data, hornbook-knowledge, homestead-affairs, forge-play,
terpsi-programs, plus leftover `willow-mcp/` and `kartikeya/` at the
github root (pre-org copies).

**Checkouts that matter for “one org”:**

| Org | On disk | In `projects.json` |
|---|---|---|
| Die-Namic-Systems | `nestor`, `dotgithub` | `nestor` |
| willow-memory | mcp, grove, gate, kart, ratatosk, vault, corpus-lens | grove, willow-mcp, ratatosk |
| hornbook-knowledge | Jeles, UTETY, oakenscrolls-office | all three |
| almanac-data | template + verticals + org meta | 14 almanac-related rows |
| homestead-affairs | homestead, -law, -health, -ledger, awesome-sovereign | `homestead-law` only |
| forge-play | Forge, forge-jig, forge-workshop | `Forge` |
| terpsi-programs | terpsi-music | none |
| safe-app-store-public | (personal-account catalog) | yes |
| extras | DispatchesFromReality, courtlistener-mcp, `github` workspace | yes |

`projects.json`: **27** rows. Most declare servers `willow-mcp` +
`nestor`. Nestor’s own row is `profile: core`, tracked hooks,
`nestor serve` + keep store.

**MCP app manifests** (`$WILLOW_HOME/mcp_apps/`): willow, hanuman, loki,
jeles, ada, skirnir, vishwakarma, heimdallr, ratatosk, utety,
willow-grove, willow-mcp, plus a `nestor/` dir. Specialist registry
ships **7** (no heimdallr / ratatosk / utety in `specialists.json`).

**Federation (operator-ratified):** one — `jeles-corpus`
(`8cae3d1dcdf4`), 2026-09-02.

**Integrations:** live github, huggingface, jeles-remote, utety,
pangolin. Stubs: gmail, slack, notion, drive, datadog, jira.

**Grove heartbeats:** willow (this session), vishwakarma stale (Sep 3),
hanuman ancient (June).

**Python (willow-mcp `.venv`, not system):** willow-mcp 2.24.3,
kartikeya 0.0.13, willow-gate 0.1.0, jeles 0.8.1.dev, forge-play 0.1.0,
willow-ratatosk 1.2.9, **nestor-meaning 0.3.0**. willow-mcp’s extra
asks `nestor-meaning>=0.7.0`. willows-grove is **not** in that venv.
System Python has almost none of the fleet.

**Not a wiring signal:** Kart `bind_try` (workshop process). Empty
`gate/registry.json`. Unset `WILLOW_MCP_ENFORCE_BINDING`.

---

## One org installed and wired — first cut

Not “clone the org folder.” Per Möbius + premise, an org-worth is
**that face’s product plus the contracts it pins**.

| If they install… | Bundled (docs + pyproject) | Wired means | This box also has (optional) |
|---|---|---|---|
| **Die-Namic only** (Nestor) | `nestor` CLI/UI/keep | keep + keyring + `nestor` MCP in the IDE | Grove charter cases (for Nestor’s own audit tests); `[gate]` → willow-gate |
| **willow-memory platform** | willow-mcp **requires** kartikeya, jeles, willow-gate; `[nestor]` extra optional | `WILLOW_HOME` + `mcp_apps` + Kart worker + PG if they use KB/Grove | Grove desk, Ratatosk, vault, corpus-lens |
| **Hornbook** | Jeles / UTETY / oakenscrolls as chosen | Jeles: checkout or remote + optional corpus MCP | Almanacs if Oakenscrolls should cite local clones |
| **Almanac** | template + verticals (data) | present on disk; Grove does not consume them directly | Jeles/Oakenscrolls to *use* them |
| **Forge / Play** | forge-play | `~/.forge/projects/<id>` workshop | Nestor keep is a soft dep |
| **Homestead** | chosen seat (law/health/ledger) | that app’s own serve/rungs | not on this `projects.json` except homestead-law |
| **Terpsi** | terpsi-music | not wired here | — |

A Forge-only box should see Forge + whatever it imports, not 27
`projects.json` rows and 12 MCP identities. This author’s box is the
full graph because every org folder is cloned **and** entered in
`projects.json` / `mcp_apps` / federation.

---

## Detector candidates (still open)

None of these alone is the graph:

1. `mcp_apps/*/manifest.json` — seats, not products.
2. `.willow/mcp/projects.json` — this box’s author roster.
3. `importlib` extras in the **running** venv — runtime pins; this
   venv’s Nestor is behind the declared extra.
4. Kart `bind_try` — too wide (Desktop, almanacs, homestead, …).
5. Grove premise add-on table — right *shape*, stale paths.

The live tell for “wired” is closer to: **a manifest or `projects.json`
row + a process or MCP server that answers.** Clone-only is not wired.
