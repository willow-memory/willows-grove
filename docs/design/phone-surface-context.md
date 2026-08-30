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

## 11. From the session that wrote this

Relevant because a phone surface implies a smaller model reading these payloads.
Measured today against a copy of the live 11,061-claim corpus and filed as
**Nestor #261**: `nestor_corpus_search` returns 1,249 bytes per claim of which
**28.5% is content**; `nestor_corpus_map` spends **5,328 bytes** to list 24
repositories. The non-authority posture costs 1.2% — the weight is
recomputability (three identities and two digests per row). The same payload as
pointers is 31% of served. A lean `fields` argument is proposed there.

If the phone surface calls Nestor, it pays this tax on every call.

## Open, for the operator

- A phone surface reverses D4's sealed loopback premise. That is a ratification.
- `:8766` has no authentication to widen. Reaching it from a phone means either
  authenticating it, or tunnelling it, or moving the surface to `:8765`.
- Nothing binds `~/Android` into Kart. Until it does, "the APK builder is
  installed" is true of the host and false of every sandboxed build.
- `willow-v08-toolchain-path.drawio` needs a REVISIONS line for §7.
