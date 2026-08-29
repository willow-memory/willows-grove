// Playwright pin for the ambient top strip's live state — the browser
// half of tests/test_grove_html_standing_boot.py.
//
// The strip used to carry a static status claim (Loki finding #31), then
// a permanent "reading standing…" placeholder. /web/boot/standing-boot.js
// now polls GET /health and paints the strip from the answer. What this
// spec pins is INVARIANTS.md §1 at the visual layer: a seat that answered
// and a seat that did not must not read — or paint — the same.

// @ts-check
const { test, expect } = require('@playwright/test');

const SLOT = '[data-standing]';
const STRIP = '.strip';

/** Wait for the boot module to settle the strip out of `loading`. */
async function settled(page) {
  await page.waitForFunction(() => {
    const strip = document.querySelector('.strip');
    return !!strip && strip.getAttribute('data-standing-state') !== 'loading';
  }, null, { timeout: 6000 });
  return {
    state: await page.locator(STRIP).getAttribute('data-standing-state'),
    text: (await page.locator(SLOT).textContent()) || '',
  };
}

test.describe('ambient strip — standing reads from /health', () => {
  test('the seat answers: the strip carries the commit it reported', async ({
    page,
  }) => {
    await page.route('**/health', (route) =>
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ ok: true, commit: 'e2ec0m' }),
      })
    );
    await page.goto('/');

    const { state, text } = await settled(page);
    expect(state).toBe('populated');
    expect(text).toContain('e2ec0m');
    expect(
      text,
      'the live branch must not still be showing the pre-fetch sentinel'
    ).not.toContain('reading standing');
  });

  test('commit "unknown" travels through verbatim, not hidden', async ({
    page,
  }) => {
    // grove_serve answers `commit: "unknown"` when git is absent rather
    // than fabricating a sha. The strip must carry that word through —
    // hiding it would turn an honest gap into a silent one.
    await page.route('**/health', (route) =>
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ ok: true, commit: 'unknown' }),
      })
    );
    await page.goto('/');

    const { state, text } = await settled(page);
    expect(state).toBe('populated');
    expect(text).toContain('unknown');
  });

  test('the seat does not answer: unreachable, distinctly, with a reason', async ({
    page,
  }) => {
    await page.route('**/health', (route) => route.abort('failed'));
    await page.goto('/');

    const { state, text } = await settled(page);
    expect(state).toBe('unreachable');
    expect(text.toLowerCase()).toContain('unreachable');
    expect(
      text,
      'INVARIANTS §1: the operator is told WHY, not just that something is off'
    ).toMatch(/—\s*\S+/);
  });

  test('a 200 that is not ok:true is unreachable, not live', async ({ page }) => {
    // A body without `ok: true` is not an answer. Reading it as live is
    // exactly the collapse §1 forbids, in the other direction.
    await page.route('**/health', (route) =>
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ ok: false, commit: 'e2ec0m' }),
      })
    );
    await page.goto('/');

    const { state } = await settled(page);
    expect(state).toBe('unreachable');
  });

  test('live and unreachable do not paint the same strip', async ({ page }) => {
    // The wording differs, but §1 is a pixel contract: the dot changes
    // too, so the distinction survives a glance that does not read text.
    await page.route('**/health', (route) =>
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ ok: true, commit: 'e2ec0m' }),
      })
    );
    await page.goto('/');
    await settled(page);
    const liveDot = await page.locator('.strip .dot').evaluate((el) => {
      const s = getComputedStyle(el);
      return `${s.backgroundColor}|${s.boxShadow}|${s.borderColor}`;
    });

    await page.unroute('**/health');
    await page.route('**/health', (route) => route.abort('failed'));
    await page.reload();
    await settled(page);
    const deadDot = await page.locator('.strip .dot').evaluate((el) => {
      const s = getComputedStyle(el);
      return `${s.backgroundColor}|${s.boxShadow}|${s.borderColor}`;
    });

    expect(deadDot, 'the status dot must not look identical in both states').not.toBe(
      liveDot
    );
  });
});
