<!-- b17: WGRV1  ΔΣ=42 -->
# Phone surface — context for the remote UI session

Written 2026-08-30 for the Grove UI session moving from a web surface to a
phone surface. Everything below was read off this box today. Line numbers are
from the commit this file lands on.

## 1. The one thing to know first

`grove_serve.py:5` states it plainly: the served page has

> *"no MCP, no auth of its own beyond the loopback boundary."*

**The loopback bind is the entire access control.** There is no token, no
cookie, no bearer check anywhere in `grove_serve.py`. Every panel it renders —
agents, dispatches, envelopes, refusals, journal — is readable by anything that
can open the socket.

## 2. And it warns, it does not refuse

This is the part that matters most for a phone, and it is easy to read the
wrong way:

```python
if host not in ("127.0.0.1", "localhost", "::1"):
    # Grove's served page is a desk-surface, not an internet-facing app.
    # Match gates_serve.py's stance: allow the override, but say so loudly.
    print("WARNING: binding grove_serve to ... a public bind widens who can
           see the desk.")
uvicorn.run(build_app(), host=host, port=port, ...)
```

`grove_serve.py:474-486`, with `GROVE_SERVE_HOST` read at `:510`. A non-loopback
host **prints and then binds**. `_host_looks_invalid` refuses malformed values,
not public ones.

So a phone-reachable Grove is one environment variable away, and what keeps the
desk private today is a **default, not a gate**. If the phone surface works by
setting `GROVE_SERVE_HOST`, the result is an unauthenticated desk surface on the
LAN. Do not let a warning that scrolls past stand in for a decision.

## 3. It is also a governance change, not only a code change

`CLAUDE.md` rule 1: *"No web ports for the dashboard. Portless means portless."*
`grove_serve.py:14` records that the premise doc **D4 sealed** served HTML on
127.0.0.1 as the desk surface. A phone surface reverses a sealed premise, so it
needs a ratification, not a patch. Propose before acting (rule 4).

## 4. The port that already has an auth story is the other one

| port | what it is | auth |
| --- | --- | --- |
| **8766** | the served page (Starlette + uvicorn) | **none** — loopback only |
| **8765** | Grove MCP in `--serve` mode | OAuth 2.0 / PKCE, `grove/mcp_auth.py::GroveOAuthProvider` |

If the phone needs to reach Grove over anything but loopback, `:8765` is the
seam that already has an authorization server in front of it. `:8766` has
nothing, and adding auth there is new work, not configuration.

## 5. u2u is signed, not private

`docs/design/u2u-security-limits.md`. u2u gives **authenticity, integrity, and
non-repudiation** within the signing-key boundary — every packet carries an
Ed25519 signature validated before dispatch. It does **not** give
confidentiality: the wire format is plaintext JSON on a bare TCP socket, and
encryption is planned for Gate 6.

That doc exists because the manifest previously advertised u2u as "End-to-end
encrypted" when it was not (`CODE_REVIEW.md` P0), against INVARIANTS §6 —
*the manifest describes code, not aspirations*. Carrying Grove content to a
phone over u2u is carrying it in the clear on the LAN. Say so if it happens.

## 6. The cheap half is already done

`grove_html.py:259` already emits
`<meta name="viewport" content="width=device-width,initial-scale=1">`.
Responsive layout is declared; the transport and the auth are the hard parts.

---

## 7. APK — what is actually installed, as of last night

This **changes a diagram that is still in the repo.**
`governance/architecture/willow-v08-toolchain-path.drawio` says
`apk (gradle + SDK — neither installed)`. That was true when it was drawn and is
false now. Measured 2026-08-30:

```
~/Android/Sdk/          installed 2026-08-29 23:57
  build-tools/          34.0.0, 35.0.0
  platforms/            android-34, android-36
  cmdline-tools/latest  commandlinetools-linux-11076708
  platform-tools/       adb present at /usr/bin/adb
  licenses/             accepted
~/.gradle/              2026-08-30 00:02 — caches, daemon, native, wrapper
  wrapper/dists/gradle-8.14.3-all
```

Gradle has been run at least once (a daemon and caches exist). `java` is on
PATH.

## 8. Installed is not reachable

Two gaps sit between this SDK and a build the fleet can drive:

- **Not on PATH.** `gradle`, `sdkmanager`, `apksigner` and `aapt2` are not
  resolvable as commands; only `adb`, `java` and `waydroid` are. It is an
  Android-Studio-shaped SDK, reached by absolute path.
- **Kart cannot see it.** `kart-sandbox.json` mentions android / gradle / sdk
  **zero times**. A sandboxed build cannot open `~/Android`. This is the same
  bind gap the v0.8 diagram already records for the forge toolchain, now with a
  second occupant.

So the honest status is: **the toolchain exists on the host and does not exist
inside the sandbox.** A phone build driven through Kart will fail on a missing
SDK, not on a missing install.

## 9. playgate is the APK gate — and it is an installer, not a builder

`safe-app-store-public/apps/playgate`, manifest `app_id: playgate`, v0.2.0. Keep
the distinction sharp: the SDK above **builds** APKs; playgate **admits** them.

What it does, from its own manifest and README:

- A child asks from a fixed roster an adult wrote. A parent grants or refuses
  **with a reason either way**, into an append-only JSONL log where a correction
  is a new row beside the old one, never an edit.
- A grant **verifies the APK's SHA256 and shells `adb install`** into a running
  Waydroid session, and records the outcome *including failure*.
- **It never downloads an APK.** It verifies a digest for a file an operator
  already placed on disk, and *"refuses outright when no digest is recorded."*
- `permissions: ["file_read", "file_write"]`. `privacy_tier: client_only`,
  `local_processing: 1.0`.
- Network: loopback listener on **8424** only; `serve()` refuses any
  non-loopback bind, and `tests/test_no_egress.py` scans the core for network
  imports *at all*. **Note the contrast with §2** — playgate's serve refuses
  where Grove's warns.
- Persistence resolves through `libs/vault-paths`: the log and the operator's
  APK directory land under the vault, never a home path. Only `paths.py` imports
  the resolver and `tests/test_paths.py` enforces that.

Its own recorded blind spot, worth carrying into any phone work:

> *"What no suite in this repo can see: whether Waydroid actually installs
> anything. The adb path is exercised against an injected runner and against a
> genuinely absent adb on the CI runner, never against a real device."*

## 10. If the phone UI renders playgate's catalog, do not add a score

Every entry carries four **unweighted** interruption facts — `count_per_10min`,
`dismissal`, `observed_version`/`_at`/`_by`, and a `provenance` of
`assumed` / `fitted` / `measured` — and **no composite score anywhere**. That is
a stated refusal, not an omission:

> *"A single displayed number would be built from weights somebody picked,
> sorted on, and within two releases optimised against — measuring compliance
> with the scoring function instead of interruption."*

Also: every shipped entry reads `assumed`, **and a test enforces that**, because
reaching `measured` requires ten minutes, a child, and someone watching. A phone
UI that sorts, stars, or ranks this catalog breaks the app's central argument.
Render the four facts and let the parent decide.

## 11. Small models — the offload case, measured

The reason this section exists: if the phone can do work rather than only
display it, the box stops being the only thing that can think. What follows is
what the box already has, and what the payloads cost against it.

### The models are already installed

```
qwen2.5:0.5b        397 MB   2 days ago
llama3.2:1b         1.3 GB   3 months
llama3.2:3b         2.0 GB   3 months     <- nestor's default draft model
willow-lane4-3b     2.0 GB   7 weeks      <- the fleet's own, Q4_K_M, tools-capable
gemma3:4b           3.3 GB   36 hours
qwen3:4b            2.5 GB   36 hours
mistral:7b · llama3.1:8b · qwen2.5vl:7b · nomic-embed-text
```

The first four are phone-class today. The 7b/8b are not, and are not the point.

Two facts worth holding on to:

- `nestor/engine.py:28` — `OLLAMA_DRAFT_MODEL = "llama3.2:3b"`. Nestor's default
  local model is **already** phone-class. Running small is not a downgrade the
  phone forces; it is the configured normal.
- `willow-lane4-3b` declares `capabilities: completion, tools` and
  `num_ctx 4096`. It can call MCP verbs, and **4096 is the fleet's own chosen
  budget**, so that is the honest yardstick — not a model's 131072 maximum.

### What the payloads cost against that budget

Bytes measured today; tokens at ~4 bytes each, so treat them as the right order
of magnitude rather than exact.

| call | served | tok | of 4096 | lean | tok | of 4096 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `nestor_corpus_map()` | 5,328 | 1,332 | **32.5%** | 477 | 119 | 2.9% |
| `nestor_corpus_search(limit=3)` | 3,749 | 937 | **22.9%** | 1,176 | 294 | 7.2% |
| `nestor_ask()` | 880 | 220 | 5.4% | 100 | 25 | 0.6% |
| **map + one search** | **9,077** | **2,269** | **55.4%** | 1,653 | 413 | **10.1%** |

**A roster call and one three-result search consume 55% of the window before the
model has read an instruction or written a token.** The same information as
pointers is 10%. That is the difference between a phone that can hold a task and
one that spends its context on digests it will never recompute.

This is not an argument against the provenance. It is an argument that the
provenance should be *requestable* rather than *unconditional* — Nestor **#261**.
On the box the 45× difference is invisible. On the phone it is the whole
feasibility question.

### What can actually move, and what cannot

`the-forge-shape.md` §9 already argues the model's job was shrunk seven times by
seven authors — the Nest cascade, Jeles' demote-only judges, a model-free
`friction_floor`, fixed onboarding questions, a decided flowchart, precomputed
edges, and a corpus that answers instead of being read. Those are the pieces
that belong on a phone: cheap, bounded, mostly retrieval and traversal.

What honestly does not move: turning a person's opening sentence into a project
shape, and writing the code. Two expensive calls at the top and at the point of
writing, twenty cheap steps around them. **The phone is the twenty steps.**

### The tension to resolve before building

Offloading work to the phone and keeping the desk on loopback (§2) pull against
each other:

- If the phone runs a model but the **data stays on the box**, the phone must
  reach the box — which is exactly the unauthenticated surface in §2. Speed of
  offload becomes the argument for widening the bind, which is how the warning
  gets clicked past.
- If the phone **carries its own store**, that problem disappears and a
  different one appears: 11,061 corpus claims and a copy of the seals, on a
  device that leaves the house. That is a lane question, not a performance one.

The per-project nestor from `the-forge-shape.md` §6 narrows the second one: a
store whose whole content is one build's world — disposable, portable, ships
with the project. A phone carrying *a project's* corpus is a different risk from
a phone carrying *the box's*.

**But the dilemma itself was false, and §12 is the operator's answer.** Both
horns assume the phone is a network peer. It is not.

One guard to carry wherever the model runs: `engine.py:178` filters context to
verified rows only, because *"a forged 'sealed' row must not reach the engine's
context."* If the phone assembles its own context, that filter has to run there
too, or it stops running at all.

### Two flags gate all of this

- `nestor_draft` refuses unless `--engine ollama`: *"nestor_draft requires
  --engine ollama; no local model was ..."* (`serve.py:772-774`).
- `nestor_corpus_map` / `nestor_corpus_search` are only registered when
  `--corpus-dir` is set — which is why Nestor's own `describe()` currently names
  them as withheld.

A phone-side Nestor needs both set. Neither is set in the fleet's live config
today.


## 12. The phone is a thumb drive

Operator, 2026-08-30, stated directly:

> *"The phone is just another thumb drive. It just connects with home computer
> just the way that a thumb drive would. So it doesn't matter that a system runs
> APK on a phone as long as when it's plugged in the data is synced in the same
> way that the vault is. The work is done where the work is done, as long as
> home base knows about it."*

This is the governing decision for everything above, and it removes a problem
rather than solving one.

### What it settles

**The phone is not a network peer.** It is a removable volume that happens to
compute. Nothing in §2 needs to change: `:8766` stays on loopback, `D4` stays
sealed, rule 1 holds, no bind is widened, and the WARNING at `grove_serve.py:478`
is never reached — because the phone never asks to reach the desk. The dilemma
in §11 assumed a network; there isn't one.

**"Home base knows about it" is a record, not a connection.** Where the work
happens stops mattering once the record comes home. That is a claim about
provenance and sync, not about topology or compute placement.

### The APK suite is three things on one wire

Not one app. Three, and they compose:

| stage | what | where it runs |
| --- | --- | --- |
| **build** | Android SDK + gradle (§7) | the box |
| **admit** | playgate — digest check, parent grant, `adb install` (§9) | the box → the phone |
| **sync** | the vault's mobile half — the record comes home | the phone → the box |

**The transport already exists and is already used.** `adb` is at
`/usr/bin/adb`, and playgate *already* shells `adb install` across it into
Waydroid. The wire that installs an APK is the same wire that carries the vault
sync. Nothing new has to be invented to move bytes between the two devices; USB
is already the fleet's phone transport, in production, in one direction.

### The vault already has a slot for this

`sean-data-vault/README.md` names three layers. The phone is the third — it is
not a new category:

| layer | travels? |
| --- | --- |
| Blueprint — `schema/`, `bootstrap/` | yes, that is the point |
| The snapshot — a populated box | **no** |
| **A live box** — provisioned locally | **never committed at all; sovereign, stays home** |

A phone running a small model against a project store is **a live box**. The
doctrine for it is already written: provisioned locally, never committed,
persistent, sovereign.

The direction is already written too. `LOCAL-ONLY.md`: *"this data lives on this
box and does not leave it"* — `git pull` works, `git push` is refused
mechanically at the transport. **Home base pulls.** A phone that plugs in and is
read from is the same motion the vault already performs, pointed at a different
volume.

### And it answers the "device that leaves the house" worry

§11 raised the risk of a corpus and a copy of the seals riding around on a
phone. The vault's crypto linchpin already answers it, unchanged from willow:
secrets are **Fernet ciphertext, meaningless without `vault.key`**, which is
`0600`, generated locally, and **never committed** — `.gitignore` blocks `*.key`.

The phone carries ciphertext. **The key stays home.** A lost phone is a lost
thumb drive, which is the threat model the vault was already built for. What
still needs deciding is which *plaintext* a project store legitimately holds, not
whether the device is trustworthy.

### Honest gap in this record

The operator recalls substantial earlier work on a mobile version of the vault,
from sessions since compacted. **I searched and did not find a dedicated record
of it** — no mobile-vault design doc, no phone-sync script, nothing in
`sean-data-vault/docs/` or `libs/vault-paths`. `adb pull`/`adb push` appear
nowhere in either tree.

So that thinking may exist only in a compacted transcript. This section is
written from the operator's statement tonight plus what the vault's own README
and LOCAL-ONLY.md already establish — not from the earlier design, which should
be recovered before anyone builds the sync half.

## Open, for the operator

- A phone surface reverses D4's sealed loopback premise. That is a ratification.
- `:8766` has no authentication to widen. Reaching it from a phone means either
  authenticating it, or tunnelling it, or moving the surface to `:8765`.
- Nothing binds `~/Android` into Kart. Until it does, "the APK builder is
  installed" is true of the host and false of every sandboxed build.
- `willow-v08-toolchain-path.drawio` needs a REVISIONS line for §7.
- ~~Offload vs. loopback~~ — answered by §12: neither. The phone plugs in.
- Recover the earlier mobile-vault design before building the sync half (§12).
- Which plaintext a project store may hold on a device that leaves the house.
- The APK suite has a build stage and an admit stage and no sync stage yet.
