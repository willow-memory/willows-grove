# regression/screenshots — visual baselines

b17: WGRV1  ΔΣ=42

Baseline PNGs for Grove's Playwright e2e regression pass (PR 9 of the
Grove v0.9 plan). Each PR that ships new rendered pixels lands its
baselines here; PR 9 stands up the comparator that fails a diff.

## Shape

- Viewport: **1200 × 900**, deviceScaleFactor 1, dark palette (Grove
  desktop chromium under `/opt/pw-browsers/chromium-1194/chrome-linux/chrome`).
- Filenames match the URL. `/seed/1` → `seed/1.png`, `/seed/` → `seed/index.png`.
- One baseline per movement, six PNGs under `seed/`.
- No animations, no JS-only pages — the seed route is server-side HTML,
  so the screenshot is deterministic once the palette is stable.

## PR 3 (this PR) — seed baselines

`seed/1.png` … `seed/6.png` are the six-movement baselines rendered
against the real canon at `/home/user/willow-memory/willow/seed/canon/`
(INVARIANTS.md §9). They exist when this PR was built on a host with
the Playwright chromium available; otherwise the folder is empty and
PR 9 generates them at its own build time. Either way the boot-time
integration tests in `tests/test_seed_canon_content.py` pin the
content — the baselines pin the pixels.

## PR 9 (later) — the comparator

PR 9 will add the Playwright runner + comparator: each run visits
`/seed/`, `/seed/1` … `/seed/6`, screenshots at the sizes above, and
diffs against the baselines under this directory. A diff that exceeds
the tolerance fails the suite and posts the diff image as an artifact.

## Regenerating a baseline

Deliberate visual change: delete the affected PNG(s), re-run PR 9's
generator, and commit the new baseline in the same PR that shipped the
visual change. Do not regenerate baselines to "fix" a failing diff —
that is how visual regressions land silently.
