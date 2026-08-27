// b17: WGRV1 ΔΣ=42
//
// Playwright regression pass for the six-movement /seed/ route (D16 /
// INVARIANTS.md §9). This spec pins:
//
//   1. /seed/ landing renders a link to each of the six movements.
//   2. /seed/1 through /seed/6 each render a titled body.
//   3. Rendered pixels match the PR 3 baselines at
//      tests/regression/screenshots/seed/{1..6}.png within a headless-
//      renderer tolerance (~5% per-pixel-ratio, threshold 0.3 to
//      absorb sub-pixel AA differences between chromium builds).
//
// The route is server-side HTML with no animations, so the render is
// deterministic once the palette is stable — but "deterministic" is not
// "bit-identical" across Playwright chromium builds, so the comparator
// uses raw `pixelmatch` (via `pngjs` for PNG decode) with per-pixel
// threshold 0.3 and a 5% max diff-pixel ratio rather than an exact-match
// check. A large diff outside tolerance fails the suite; the diff PNG
// is written under test-results/ and CI surfaces it as an artifact.
//
// Baseline lifecycle is documented in
// tests/regression/screenshots/README.md — baselines are regenerated
// only for a deliberate visual change, never to "fix" a failing diff.
//
// This spec witnesses INVARIANTS §9 in content and §1 in that /seed/
// survives absence (the C3 stub still renders when canon is missing —
// pytest already pins the wire shape of the stub). This is the
// pixel-side witness.
//
// Loki finding #18 (M15-seed-canon-pixel-baseline) fix: raw pixelmatch
// against the on-disk PR-3 baselines, no per-spec snapshot-dir
// traversal. Baseline absent → runtime test.skip() (never a fake pass).

// @ts-check
const { test, expect } = require('@playwright/test');
const fs = require('fs');
const path = require('path');
const pixelmatch = require('pixelmatch');
const { PNG } = require('pngjs');

// Absolute-on-disk path to the PR-3 baseline dir. Read directly rather
// than via Playwright's per-spec snapshot dir (which refuses `..`
// traversal on outputPath). This is Loki finding #18's fix path.
const BASELINE_DIR_ON_DISK = path.resolve(
  __dirname,
  '..',
  'regression',
  'screenshots',
  'seed'
);

// Comparator tuning. Baselines were captured at 1200×900 dark-palette
// against the real canon (see tests/regression/screenshots/README.md).
// A per-pixel threshold of 0.3 absorbs sub-pixel AA differences between
// chromium builds; the max diff-pixel ratio of 5% is the fail line.
const PIXEL_THRESHOLD = 0.3;
const MAX_DIFF_RATIO = 0.05;

const MOVEMENTS = [1, 2, 3, 4, 5, 6];

test.describe('/seed/ six-movement canon — content + pixel baselines', () => {
  test.beforeEach(async ({ page }) => {
    // Baselines were captured at 1200×900 (see PR 3 baseline README) —
    // pin the viewport before every navigation so a headless default
    // (e.g. 1280×720) doesn't shift the pixels the comparator sees.
    await page.setViewportSize({ width: 1200, height: 900 });
  });

  test('/seed/ landing lists a link to every movement', async ({ page }) => {
    await page.goto('/seed/');
    // The chapter cards are <a href="/seed/1">…</a> through /seed/6.
    // (seed_html._page → render_seed_index emits one per movement.)
    const hrefs = await page.$$eval('a[href^="/seed/"]', (links) =>
      Array.from(new Set(links.map((a) => a.getAttribute('href'))))
    );
    for (const n of MOVEMENTS) {
      expect(
        hrefs.includes(`/seed/${n}`),
        `/seed/ landing must link to /seed/${n}`
      ).toBe(true);
    }
  });

  for (const n of MOVEMENTS) {
    test(`/seed/${n} renders a title and a non-empty body`, async ({ page }) => {
      const resp = await page.goto(`/seed/${n}`);
      expect(resp && resp.status()).toBe(200);

      const title = (await page.title()).trim();
      expect(title.length, `/seed/${n} must set a <title>`).toBeGreaterThan(0);
      expect(
        title.toLowerCase(),
        `/seed/${n} <title> should mention seed`
      ).toContain('seed');

      const h1 = await page
        .locator('article.movement h1, main h1')
        .first()
        .textContent();
      expect(
        (h1 || '').trim().length,
        `/seed/${n} must render an <h1> heading`
      ).toBeGreaterThan(0);

      const bodyText = await page
        .locator('article.movement, main')
        .first()
        .innerText();
      expect(
        (bodyText || '').trim().length,
        `/seed/${n} body must be non-empty`
      ).toBeGreaterThan(20);
    });

    // Pixel-baseline regression — raw pixelmatch against the on-disk
    // PR-3 baseline. Baseline absent (headless-less box) → runtime
    // test.skip() reports SKIPPED, never a fake pass. Loki #18 fix.
    test(`/seed/${n} pixels match PR-3 baseline within tolerance`, async ({ page }) => {
      const baselinePath = path.join(BASELINE_DIR_ON_DISK, `${n}.png`);
      test.skip(
        !fs.existsSync(baselinePath),
        `no PR-3 baseline on disk at ${baselinePath} — skip cleanly (never fake-pass)`
      );

      await page.goto(`/seed/${n}`);

      const shotBuf = await page.screenshot({ fullPage: false });
      const actual = PNG.sync.read(shotBuf);
      const baseline = PNG.sync.read(fs.readFileSync(baselinePath));

      // Dimension mismatch — fail loudly. A silently-clamped compare
      // would smuggle a visual regression through the door.
      expect(
        actual.width,
        `/seed/${n} screenshot width ${actual.width} != baseline ${baseline.width}`
      ).toBe(baseline.width);
      expect(
        actual.height,
        `/seed/${n} screenshot height ${actual.height} != baseline ${baseline.height}`
      ).toBe(baseline.height);

      const { width, height } = baseline;
      const diff = new PNG({ width, height });
      const diffPixels = pixelmatch(
        baseline.data,
        actual.data,
        diff.data,
        width,
        height,
        { threshold: PIXEL_THRESHOLD }
      );
      const ratio = diffPixels / (width * height);

      // Write the diff PNG as a CI artifact when we fail. Best-effort:
      // if test-results/ is not writable we still assert on the ratio.
      if (ratio >= MAX_DIFF_RATIO) {
        try {
          const outDir = path.resolve(__dirname, '..', '..', 'test-results');
          fs.mkdirSync(outDir, { recursive: true });
          fs.writeFileSync(
            path.join(outDir, `seed-${n}-diff.png`),
            PNG.sync.write(diff)
          );
        } catch (_) {
          // swallow — the assertion below is the load-bearing signal
        }
      }

      expect(
        ratio,
        `/seed/${n} pixel diff ratio ${ratio.toFixed(4)} exceeds ${MAX_DIFF_RATIO} (${diffPixels}/${width * height} px)`
      ).toBeLessThan(MAX_DIFF_RATIO);
    });
  }
});
