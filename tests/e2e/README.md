# tests/e2e — Playwright browser-driven suite

b17: WGRV1  ΔΣ=42

Grove's operator-facing panels are Web Components against a served page.
This suite drives them through real chromium so the pytest suite's wire
pins (readers, endpoints) are met at the visual layer.

## What it verifies

- **`grove-served-page.spec.js`** — INVARIANTS.md §1 (three-state) and §8
  (live-endpoint default). Every expected component upgrades, the persona
  registry, envelope panel, and dispatch rail render one of the three §1
  states, the chat card LEFT column posts + updates history, the RIGHT
  column shows atoms or an unreachable read-back distinctly from empty,
  the lens switch updates `document.body[data-lens]`, and a summoned
  `<grove-card>` transitions via CSS into the summoned state.
- **`three-state-affordances.spec.js`** — INVARIANTS.md §1 at the pixel
  layer. For each panel + endpoint pair, we fixture `/api/*` first
  empty then unreachable via `page.route(…)`, and assert the rendered
  markup is not the same string. "I could not reach the source" must
  never collapse into "there is nothing there" — this spec fails loudly
  the day a panel starts painting them identically.
- **`persona-registry-state.spec.js`** — INVARIANTS.md §1 for
  `<grove-persona-registry>`. The registry is a data element
  (`:host { display: none }`), so its three states are observable as the
  `.state` property and the `registry-loaded` / `registry-unreachable`
  window events, not as markup. Pins that an empty roster never fires
  `registry-unreachable`, that a 503 does and carries the endpoint's
  reason verbatim, and that an unreachable declared in a 200 body is
  honored rather than read as empty.
- **`persona-registry-inline-shim.spec.js`** — INVARIANTS.md §8. An
  inline `<script type="application/json">` shim only wins when the
  element opted in via `data-fixture` or `data-source="_inline"`;
  otherwise the live `/api/personas` endpoint wins. (Replaces the
  Python-bindings test that skipped on every CI run.)
- **`standing-strip.spec.js`** — INVARIANTS.md §1 / §8 for the ambient
  top strip. `web/boot/standing-boot.js` polls `GET /health`; the spec
  fixtures that endpoint live, `ok:false`, and failed, and asserts the
  strip reads `seat live · <sha>` vs `seat unreachable — <why>`, carries
  a `commit: "unknown"` through verbatim, and paints the status dot
  differently in the two states.
- **`seed-canon.spec.js`** — INVARIANTS.md §9. `/seed/` lists six
  chapter links; `/seed/1` … `/seed/6` each render a titled body; each
  page's screenshot matches the PR 3 baseline at
  `tests/regression/screenshots/seed/{1..6}.png` within a ~5% per-pixel
  ratio and per-channel threshold 0.3 (headless-renderer tolerance).

## Cost

Each spec pays for one chromium launch + one page load (~5–15 s per
spec on the CI runner). Cross-page tests reuse a single browser
context; only the `webServer` boot (`python3 -m grove_serve` on
127.0.0.1:8766) is paid up-front, once for the whole run.

## Run locally

```
npx playwright install --with-deps chromium  # once
npx playwright test                          # every run
# or, via the package.json script alias:
npm run test:e2e
```

The `webServer` block in `playwright.config.js` boots grove_serve on
`http://127.0.0.1:8766` for the duration of the run and tears it down
when the suite exits. The seed reader finds the real canon on its own
now that it ships in this repo (`governance/seed/`); set
`WILLOW_HOME=/path/to/a/dir/containing/seed` only if you need to
override it with a per-node copy. Otherwise `/seed/` renders the
six-movement stub and the content pins still pass.

## Run in CI

Automatic via `.github/workflows/tests.yml` (PR 4). The install step
runs when `playwright.config.js` is present; the run step runs when
`tests/e2e/*.spec.*` is present. Baselines used by `seed-canon.spec.js`
are checked into the repo at `tests/regression/screenshots/seed/`.

## Regenerating a baseline

Delete the affected PNG(s) under `tests/regression/screenshots/seed/`
and re-run with `--update-snapshots`:

```
npx playwright test tests/e2e/seed-canon.spec.js --update-snapshots
```

Commit the new baseline in the same PR that shipped the deliberate
visual change. Never regenerate baselines to "fix" a failing diff —
that is how visual regressions land silently
(`tests/regression/screenshots/README.md` for the rest of the
baseline discipline).
