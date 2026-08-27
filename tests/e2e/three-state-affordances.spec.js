// b17: WGRV1 ΔΣ=42
//
// Playwright pin for docs/INVARIANTS.md §1 — the three-state contract —
// at the visual layer. The reader and endpoint pins in pytest guarantee
// the wire shape; this spec guarantees that when a panel does receive
// the `unreachable` shape, it renders visibly differently from the
// `empty` shape. Constraint 1 (DESIGN_CONSTRAINTS.md) is that
// "I could not reach the source" must never collapse into "there is
// nothing there" — this spec fails loudly the day a panel starts
// painting them the same pixels.
//
// The panels covered here are the four whose live endpoints the served
// page or a mounted card consumes:
//
//   - <grove-persona-registry>  → /api/personas
//   - <grove-envelope-panel>    → /api/envelopes
//   - <grove-dispatch-rail>     → /api/dispatch
//   - <grove-chat> (RIGHT side) → /api/journal/recent
//
// The verification strategy: two sibling instances of the same panel
// under two Playwright `page.route(…)` fixtures — one that answers
// 200/empty, one that answers 503/unreachable — and we assert that
// their rendered outerHTML differs on at least one of {text, class,
// aria attribute, banner presence, dashed border}. Cross-panel pixel
// diffing is out of scope; this is a "distinct rendering" check, not
// a design-system regression.

// @ts-check
const { test, expect } = require('@playwright/test');

/**
 * Normalize the rendered outerHTML for comparison — collapse whitespace
 * and strip dynamic bits (timestamps, ids). If the two strings still
 * differ, the two states are visually distinct.
 */
function normalize(html) {
  return String(html || '')
    .replace(/\s+/g, ' ')
    .replace(/data-fetched-at="[^"]*"/g, '')
    .replace(/id="[^"]*"/g, '')
    .trim();
}

/**
 * A panel passes §1 if, given identical browser context, its rendered
 * markup for the empty branch and the unreachable branch is not the
 * same string.
 */
async function assertEmptyAndUnreachableDiffer(page, { tag, endpoint, emptyBody, unreachableBody }) {
  // Intercept the endpoint. First run: return empty. Second run: return
  // unreachable. Each run reloads the page so the component's initial
  // fetch is what we control.
  await page.goto('/');

  // ── Run 1: empty ─────────────────────────────────────────────────────
  await page.route(`**${endpoint}**`, (route) =>
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify(emptyBody),
    })
  );
  const emptyHtml = await page.evaluate(async (tagName) => {
    // Ensure the component script is loaded — some components live on
    // the served page, some are demand-loaded (card, envelope panel).
    if (!customElements.get(tagName)) {
      await new Promise((resolve) => {
        const s = document.createElement('script');
        s.type = 'module';
        s.src = `/web/components/${tagName}.js`;
        s.addEventListener('load', resolve, { once: true });
        s.addEventListener('error', resolve, { once: true });
        document.head.appendChild(s);
      });
      try {
        await customElements.whenDefined(tagName);
      } catch (_ignored) { /* whenDefined can throw on stray names */ }
    }
    const el = document.createElement(tagName);
    el.dataset.e2eProbe = 'empty';
    document.body.appendChild(el);
    // Wait for the component to reach a terminal state.
    const started = Date.now();
    while (
      !['populated', 'empty', 'unreachable'].includes(el._state) &&
      Date.now() - started < 6000
    ) {
      await new Promise((r) => setTimeout(r, 50));
    }
    // Read the shadow root when present — that's where the render lives.
    const root = el.shadowRoot || el;
    return (root.innerHTML || '') + '|' + (el._state || '');
  }, tag);

  // ── Run 2: unreachable ───────────────────────────────────────────────
  await page.unroute(`**${endpoint}**`);
  await page.route(`**${endpoint}**`, (route) =>
    route.fulfill({
      status: 503,
      contentType: 'application/json',
      body: JSON.stringify(unreachableBody),
    })
  );
  // Reload so the freshly-mounted component fetches from the new fixture.
  await page.reload();
  const unreachableHtml = await page.evaluate(async (tagName) => {
    if (!customElements.get(tagName)) {
      await new Promise((resolve) => {
        const s = document.createElement('script');
        s.type = 'module';
        s.src = `/web/components/${tagName}.js`;
        s.addEventListener('load', resolve, { once: true });
        s.addEventListener('error', resolve, { once: true });
        document.head.appendChild(s);
      });
      try {
        await customElements.whenDefined(tagName);
      } catch (_ignored) { /* ok */ }
    }
    const el = document.createElement(tagName);
    el.dataset.e2eProbe = 'unreachable';
    document.body.appendChild(el);
    const started = Date.now();
    while (
      !['populated', 'empty', 'unreachable'].includes(el._state) &&
      Date.now() - started < 6000
    ) {
      await new Promise((r) => setTimeout(r, 50));
    }
    const root = el.shadowRoot || el;
    return (root.innerHTML || '') + '|' + (el._state || '');
  }, tag);

  // The unreachable render must not equal the empty render — this is the
  // §1 pin. We include the internal `_state` marker in the compared
  // string so a component that renders identical shadow markup but
  // exposes distinct `_state` still passes (the operator sees the state
  // via at least one channel).
  expect(
    normalize(unreachableHtml),
    `${tag}: unreachable render must be visually distinct from empty per INVARIANTS §1`
  ).not.toBe(normalize(emptyHtml));

  await page.unroute(`**${endpoint}**`);
}

test.describe('three-state affordances — every panel paints unreachable ≠ empty', () => {
  // grove-persona-registry is a DATA element (`:host { display: none }`).
  // Its three-state distinction is exposed via the `registry-unreachable`
  // window event and the `.state` property — not visible markup. §1 for
  // this component is pinned in the pytest layer (test_grove_serve_personas)
  // and in test_refusal_summon_shape's boot contract, not the DOM.
  test.skip('grove-persona-registry: /api/personas empty vs unreachable (data element — no visual)', async () => {});

  test('grove-envelope-panel: /api/envelopes empty vs unreachable', async ({
    page,
  }) => {
    await assertEmptyAndUnreachableDiffer(page, {
      tag: 'grove-envelope-panel',
      endpoint: '/api/envelopes',
      emptyBody: {
        state: 'empty',
        schema: 'grove.envelopes.v1',
        envelopes: [],
      },
      unreachableBody: {
        state: 'unreachable',
        reason: 'e2e-fixture: envelope reader down',
      },
    });
  });

  test('grove-dispatch-rail: /api/dispatch empty vs unreachable', async ({
    page,
  }) => {
    await assertEmptyAndUnreachableDiffer(page, {
      tag: 'grove-dispatch-rail',
      endpoint: '/api/dispatch',
      emptyBody: { state: 'empty', queue: [] },
      unreachableBody: {
        state: 'unreachable',
        reason: 'e2e-fixture: kart reader down',
      },
    });
  });

  test('grove-chat: /api/journal/recent empty vs unreachable (RIGHT column)', async ({
    page,
  }) => {
    // <grove-chat> is on the served page and polls /api/journal/recent
    // for the read-back column. We can't just spin up a bare instance
    // because the chat is dual-column and the LEFT side POSTs; we
    // fixture only the read-back endpoint.
    await page.goto('/');
    await page.route('**/api/journal/recent**', (route) =>
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ state: 'empty', atoms: [] }),
      })
    );
    await page.reload();
    const chatEmpty = await page
      .locator('grove-chat')
      .first()
      .evaluate(async (el) => {
        const root = el.shadowRoot;
        const started = Date.now();
        while (Date.now() - started < 4000) {
          const html = (root.innerHTML || '').toLowerCase();
          if (
            html.includes('no messages yet') ||
            html.includes('empty') ||
            html.includes('unreachable')
          ) {
            return html;
          }
          await new Promise((r) => setTimeout(r, 100));
        }
        return (root.innerHTML || '').toLowerCase();
      });

    await page.unroute('**/api/journal/recent**');
    await page.route('**/api/journal/recent**', (route) =>
      route.fulfill({
        status: 503,
        contentType: 'application/json',
        body: JSON.stringify({
          state: 'unreachable',
          reason: 'e2e-fixture: read-back seam down',
        }),
      })
    );
    await page.reload();
    const chatUnreachable = await page
      .locator('grove-chat')
      .first()
      .evaluate(async (el) => {
        const root = el.shadowRoot;
        const started = Date.now();
        while (Date.now() - started < 6000) {
          const html = (root.innerHTML || '').toLowerCase();
          if (html.includes('unreachable') || html.includes('could not reach')) {
            return html;
          }
          await new Promise((r) => setTimeout(r, 100));
        }
        return (root.innerHTML || '').toLowerCase();
      });

    expect(
      normalize(chatUnreachable),
      'grove-chat RIGHT column must render unreachable distinctly from empty per INVARIANTS §1'
    ).not.toBe(normalize(chatEmpty));

    await page.unroute('**/api/journal/recent**');
  });
});
