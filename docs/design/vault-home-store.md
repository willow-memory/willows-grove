<!-- b17: WGRV1 -->
# Vault home store — the cut, two axes, not a move

Written 2026-09-08 from recorded complaints. Design note first; **operator
migration 2026-09-08 evening** moved live paths into the vault box (see
§6). Kart bind and Postgres data-directory move are still open.

Stack context: [seat-stack.md](seat-stack.md),
[phone-tier0-sync.md](phone-tier0-sync.md).
Architecture: [governance/architecture/README.md](../../governance/architecture/README.md),
[willow-v03-full.drawio](../../governance/architecture/willow-v03-full.drawio),
[willow-v04-full.drawio](../../governance/architecture/willow-v04-full.drawio),
[willow-v11-verification-edge.drawio](../../governance/architecture/willow-v11-verification-edge.drawio).
Blueprint: `willow-memory/willow-data-vault` `bootstrap/provision.sh`.

SOIL: `projects_willow_governance_decisions` /
`vault-declared-folders-2026-09-08`, `homecoming-vault-pg-2026-09-08`,
`vault-gate-placement-2026-09-08`.
KB: `68332C58`, `0FD9EDAD`, `BD549C08`. Gaps: `c54ddc5cc7e5`,
`97da538f7aa3`, `e2dd9c266eca`, `cb6623f63b32`, `cb2daa7a089f`,
`fb21e67693e6`, `a25bce68cebc`, `012cb735aab1`.

Nestor keep (vault box, `decision→decision`, verifier sean campbell,
2026-09-08 evening): split-brain vocabulary sealed —
`d7e107cd` constitutional ledger / Canonical Chain;
`f361f9ba` Nestor vs Jeles two-stores question;
`4dbacc03` personal/work memory admission gate;
`fcaae3a9` Kart vs gate boundary. Earlier drafts on same store may
include `4ea7d524` (when PG is written home), `d49409b6` (Kart declared
folders). `Cloud should not see PII unless granted` is **pending**.

---

## 1. Three-layer cut

Phone travel memory (USB-style / Capacitor store / optional on-device Nestor
export, phone-class models) is not the home store.

Homecoming is the tier-0 USB/`adb` deposit, then import
([phone-tier0-sync.md](phone-tier0-sync.md)). That file already forbids
`adb` of a live vault snapshot.

The home store is the vault-resident slice. Postgres lives there **when the
device is home**. Dumps under `sean-data-vault/postgres/` are a travel form.
The live cluster is still `/var/lib/postgresql/18/main` (`willow_20`).

v03/v04 already drew this: `(USER)-data-vault — target`, Postgres and SOIL
live here, marked **not built**, hub edge labeled **user-granted paths**.
The architecture README and `CURRENT-STATE-2026-08-28.md` still say that
headline is unbuilt.

[seat-stack.md](seat-stack.md) still says homecoming is USB/`adb` deposit
**to the box (not vault)**. That line mixed “the phone is not a vault
replica” with “the vault is not the home.” Gap `97da538f7aa3`. This note
does not rewrite the stack diagram.

## 2. Two axes, and the gate that belongs between them

**Path bind (Kart).** v11: `bind_try` is a declared list; a path not listed
does not exist to the task. `kart-sandbox-vault-unbind` later treated
*zero* vault binds as the decision so agents would not rummage personal
files. That flattened two scopes. Unbind-all is the wrong fix.

**Inference class.** Cloud does not see PII unless the user grants it.
Local models may read and write the declared slice. The existing knob is
`consent.cloud_llm` (box `consent.json`; see willow-mcp
`docs/design/consent-toggles.md`). It is read and shown. It does **not**
yet gate folders. `internet` is the consent key that actually has callers.

**Vault–agent gate (willow-gate).** Operator, this session: that is the
proper place for willow-gate — between the declared vault slice and the
agent system. It is part of getting the vault wired, not a side package.
Today the package is a willow-mcp library (`TRUST_LEVELS`,
`session_binder`, `tier_policy`). `WILLOW_MCP_ENFORCE_BINDING` is unset
on this box. The vault box already has
`willow-operator-box/gate/registry.json` and it is empty (`{}`). Live
`WILLOW_HOME` has no `gate/` directory. Kart does not call willow-gate.
This note names the seat. It does not flip the switch or register
agents.

willow-data-vault `provision.sh` creates a **box** (`config/`, `mcp_apps/`,
`ledgers/`, then root dbs). It does not name personal folders and has no
`cut()`. Nestor’s workshop export (`cut` at a ledger head) is the missing
verb: the declared slice **is** the cut.

## 3. Folder table — draft, 2026-09-08

Operator-named this session. Not sealed. Not a Kart bind.

Under `~/sean-data-vault`, Kart (and seats) **may** open:

| Folder | Note |
|---|---|
| `willow-operator-box/` | Blueprint box stub: config, mcp_apps, ledgers, vault.db/key |
| `postgres/` | Dumps — travel form, not the live cluster |
| `schema/` | Vault-local blueprint copy |
| `bootstrap/` | Vault-local blueprint copy |
| `mcp/` | |
| `docs/` | |
| `scripts/` | |
| `made-by-willow/` | Session deposits, proposals |
| `knowledge-json/` | |
| `agent-indexes/` | |

**Out** (operator-only; do not bind wholesale):

`personal/`, `personal-research/`, `provided-by-sean/`, `journal/`,
`professional/`, `willow-root/`, `willow-store/`, archives, downloads,
experiments, session tarball piles.

Exact bind paths *inside* `willow-operator-box/` are not named here.

## 4. Kart / agent split — draft, 2026-09-08

Operator this turn. Split-brain **vocabulary** sealed in Nestor (`fcaae3a9`,
`4dbacc03`; see header). Nestor: `things put into the nest are fair game` is
still **pending** as a standalone pair.

**Kart** keeps doing Kart work: sandbox, `bind_try`, tests, builds, git
in the workshop. That is process. Do not shrink the jobs Kart already
runs.

**Agents** stay inside **Die-Namic Systems** — the company name in the
YC docs (KB `1C8DA1C1`). Scope is not a fixed repo list and not “only
the `Die-Namic-Systems/` git folder.” It is **whatever this box has
installed and wired**: some pieces come bundled, some are external
apps the user hooks in. This operator box has the full set because
he built them. Another install may be Forge only, or Nestor only —
that smaller graph *is* the company on that box. Agents may **pull**
from verified sources those apps expose. They do not rummage
`elsewhere`. The phrase `Die-Namic Systems` is still Nestor
**pending**.

**willow-gate** is a different shape from Kart's bind list. It is the
cut on *what may become system memory*:

- The Nest drop is the user saying this may enter.
- After sort: proper folders, keep, KB — what the user wants the system
  to retain.
- Elsewhere (personal vault layers, files never nested) is not fair
  game.

Live facts that collide with a naive reading:

- `nest/bridge.py` still calls `~/Desktop/Nest` the local-only PII zone
  and bridges **counts**, not fragment text.
- Tonight's Nest already holds journal / personal / legal / financial
  categories and `secret` fragments.
- Last night's folder table still leaves `personal/` and `journal/` out
  of Kart.
- `kart-sandbox.json` already `bind_try`s `{{HOME}}/Desktop` (the Nest
  drop parent).

So “nest = fair game” is a **promote-and-keep** rule for the gate, not
“Kart and every seat may read the raw Nest DB.” Cloud vs local still
applies after that cut.

## 5. Open slots — do not invent

- Exact `bind_try` entries under `willow-operator-box/`.
- Whether `postgres/` dumps are Kart-readable or operator-only travel.
- How `consent.cloud_llm` becomes a folder gate, not only a Nest egress
  switch.
- How willow-gate composes with Kart `bind_try` (who denies a path first)
  and with `consent.cloud_llm` (identity vs inference class).
- Whether `WILLOW_MCP_ENFORCE_BINDING` + `register-agent` is the cutover,
  and whether the roster lives in the vault box `gate/registry.json`.
- How “installed and wired” is detected on a box — survey:
  [install-graph-survey-2026-09-08.md](install-graph-survey-2026-09-08.md).
  Detector still open (`a0d7fd8ec389`).
- Whether nest-fair-game means after `nest_promote` / curate, or the raw
  Nest DB — and how that sits next to `nest/bridge.py`'s PII zone.
- Whether [seat-stack.md](seat-stack.md) retires “(not vault)”.
- Live Postgres cluster still not in the vault (`willow_20` at
  `/var/lib/postgresql/18/main`); dumps only under `postgres/`.
- Nestor UI launch still drifts from MCP canonical paths until a single
  launcher reads vault env (`cb6623f63b32`, `fb21e67693e6`).

## 6. Live paths after migration — 2026-09-08 evening

Operator box root: `~/sean-data-vault/willow-operator-box/`.

| Surface | Path / value |
|---|---|
| `WILLOW_HOME` | `~/sean-data-vault/willow-operator-box` |
| `WILLOW_STORE_ROOT` | `…/store` (SOIL collections) |
| `NESTOR_DB` / ledger / keyring | `…/nestor.db`, `…/ledger.jsonl`, `…/verifiers.json` |
| Envelope registry | `…/constitutional/pre-approved.json` (63 active grants) |
| MCP configs | Repointed across fleet `.mcp.json` / `projects.json` |

**Friction logged this session:** long-lived `nestor ui` pinned to old
`--db`/`decision→commitment` showed empty drafts while MCP wrote vault
(`cb6623f63b32`); UI warned `NESTOR_SEAL_KEY` unset / verifier typed-not-
proven (`fb21e67693e6`); `sign-session`/`attest-session` and desk UI not
Kart-eligible (`cb2daa7a089f`, `012cb735aab1`); MCP env hot-reload vs IDE
restart (`a25bce68cebc`).

v04 remains the last full picture. This note is the missing node, not a v12.
