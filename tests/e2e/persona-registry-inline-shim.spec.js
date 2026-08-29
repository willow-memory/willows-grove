// b17: WGRV1 ΔΣ=42
//
// Playwright pin for docs/INVARIANTS.md §8 — fixture-based rendering is
// opt-in, harness use only. Closes PR-14 carryover #11a
// (docs/design/pr14-carryovers.md): this spec replaces
// tests/test_persona_registry_inline_shim_opt_in.py, whose Python
// Playwright bindings are not in requirements.txt and which therefore
// `importorskip`ped on every CI run — a §10 false witness. Here the pin
// runs in the CI Playwright step, where chromium is installed.
//
// The contract: an inline `<script type="application/json">` shim inside
// a <grove-persona-registry> MUST NOT shadow the live /api/personas
// endpoint unless the element explicitly opted in via `data-fixture` or
// `data-source="_inline"`. Leftover harness markup must never silently
// become the operator's view of the fleet.

// @ts-check
const { test, expect } = require('@playwright/test');

const LIVE_MARKER = 'live-endpoint-payload';
const SHIM_MARKER = 'inline-shim-payload';

const payload = (marker) => ({
  schema: 'fleet-personas/v1',
  personas: { willow: { marker } },
});

/**
 * Mount a <grove-persona-registry> carrying an inline JSON shim, with the
 * given opt-in attribute (or none), and resolve once it settles.
 *
 * @param {import('@playwright/test').Page} page
 * @param {{attr: string|null, value?: string}} optIn
 */
async function mountWithShim(page, optIn) {
  return page.evaluate(async ({ optIn, shim }) => {
    const tag = 'grove-persona-registry';
    if (!customElements.get(tag)) {
      await new Promise((resolve) => {
        const s = document.createElement('script');
        s.type = 'module';
        s.src = `/web/components/${tag}.js`;
        s.addEventListener('load', resolve, { once: true });
        s.addEventListener('error', resolve, { once: true });
        document.head.appendChild(s);
      });
    }
    await customElements.whenDefined(tag);

    const el = document.createElement(tag);
    if (optIn.attr) el.setAttribute(optIn.attr, optIn.value || '');

    const script = document.createElement('script');
    script.type = 'application/json';
    script.textContent = JSON.stringify(shim);
    el.appendChild(script);

    const settled = new Promise((resolve) => {
      el.addEventListener('registry-loaded', resolve, { once: true });
      el.addEventListener('registry-unreachable', resolve, { once: true });
    });
    document.body.appendChild(el);
    await Promise.race([settled, new Promise((r) => setTimeout(r, 6000))]);

    const row = el.getPersona('willow');
    const state = el.state;
    el.remove();
    return { row, state };
  }, { optIn, shim: payload(SHIM_MARKER) });
}

test.beforeEach(async ({ page }) => {
  await page.goto('/');
  await page.route('**/api/personas**', (route) =>
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify(payload(LIVE_MARKER)),
    })
  );
});

test.describe('grove-persona-registry — §8 inline shim is opt-in', () => {
  test('no opt-in attribute: the live endpoint wins over the inline shim', async ({
    page,
  }) => {
    const { row, state } = await mountWithShim(page, { attr: null });
    expect(state).toBe('populated');
    expect(row, 'the live endpoint answered — a row is expected').not.toBeNull();
    expect(
      row.marker,
      'INVARIANTS §8: without data-fixture / data-source="_inline", an inline ' +
        'shim MUST NOT shadow /api/personas'
    ).toBe(LIVE_MARKER);
  });

  test('data-fixture: the inline shim wins', async ({ page }) => {
    const { row, state } = await mountWithShim(page, { attr: 'data-fixture' });
    expect(state).toBe('populated');
    expect(row.marker).toBe(SHIM_MARKER);
  });

  test('data-source="_inline": the inline shim wins', async ({ page }) => {
    const { row, state } = await mountWithShim(page, {
      attr: 'data-source',
      value: '_inline',
    });
    expect(state).toBe('populated');
    expect(row.marker).toBe(SHIM_MARKER);
  });
});
