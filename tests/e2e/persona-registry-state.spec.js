// Playwright pin for docs/INVARIANTS.md §1 — the three-state contract —
// on <grove-persona-registry>, closing PR-14 carryover #2
// (docs/design/pr14-carryovers.md).
//
// The registry is a DATA element: its shadow root is
// `<style>:host { display: none }</style>` in every state, so the
// DOM-diff strategy used by three-state-affordances.spec.js is
// categorically wrong for it — empty and unreachable render the same
// markup by design, because the registry renders nothing at all.
//
// What the registry actually exposes to consumers is:
//
//   - `.state` — "loading" | "populated" | "empty" | "unreachable"
//   - a `registry-loaded` event   (populated | empty branch)
//   - a `registry-unreachable` event with `detail.reason`
//
// Both events are dispatched `bubbles: true, composed: true`, so a
// consumer listening on `window` sees them — that is the observable the
// boot modules (web/boot/refusal-summon-boot.js) actually consume, and
// it is what this spec pins. The pytest layer (test_grove_serve_personas)
// pins the wire shape the endpoint sends; this pins what the browser
// does with it.

// @ts-check
const { test, expect } = require('@playwright/test');

const ENDPOINT = '**/api/personas**';

/**
 * Mount a fresh <grove-persona-registry> on the served page, record every
 * registry event that reaches `window`, and resolve once the element
 * settles out of "loading".
 *
 * Returns the observable surface only — `.state` plus the events seen —
 * never the shadow markup, which is empty in all three states.
 */
async function mountAndObserve(page) {
  return page.evaluate(async () => {
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

    /** @type {{name: string, detail: any}[]} */
    const events = [];
    const record = (name) => (ev) => {
      // Only count events from the probe element — the served page mounts
      // its own registry, whose load would otherwise pollute the record.
      if (!(ev.target instanceof HTMLElement)) return;
      if (ev.target.dataset.e2eProbe !== 'registry-state') return;
      events.push({ name, detail: ev.detail });
    };
    const onLoaded = record('registry-loaded');
    const onUnreachable = record('registry-unreachable');
    window.addEventListener('registry-loaded', onLoaded);
    window.addEventListener('registry-unreachable', onUnreachable);

    const el = document.createElement(tag);
    el.dataset.e2eProbe = 'registry-state';
    document.body.appendChild(el);

    const started = Date.now();
    while (el.state === 'loading' && Date.now() - started < 6000) {
      await new Promise((r) => setTimeout(r, 25));
    }

    window.removeEventListener('registry-loaded', onLoaded);
    window.removeEventListener('registry-unreachable', onUnreachable);
    el.remove();

    return { state: el.state, personaCount: Object.keys(el.personas).length, events };
  });
}

const names = (result) => result.events.map((e) => e.name);

test.describe('grove-persona-registry — §1 three-state observable', () => {
  test('empty: registry-loaded fires with state "empty"; registry-unreachable does NOT', async ({
    page,
  }) => {
    await page.goto('/');
    await page.route(ENDPOINT, (route) =>
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ schema: 'fleet-personas/v1', personas: {} }),
      })
    );

    const result = await mountAndObserve(page);

    expect(result.state, 'an empty roster is "empty", never "unreachable"').toBe('empty');
    expect(result.personaCount).toBe(0);
    expect(names(result)).toContain('registry-loaded');
    expect(
      names(result),
      'INVARIANTS §1: an empty roster MUST NOT announce itself as unreachable'
    ).not.toContain('registry-unreachable');

    const loaded = result.events.find((e) => e.name === 'registry-loaded');
    expect(loaded.detail).toMatchObject({ count: 0, state: 'empty' });
  });

  test('unreachable (503): registry-unreachable fires carrying the reason; registry-loaded does NOT', async ({
    page,
  }) => {
    await page.goto('/');
    const reason = 'e2e-fixture: persona roster unreadable';
    await page.route(ENDPOINT, (route) =>
      route.fulfill({
        status: 503,
        contentType: 'application/json',
        body: JSON.stringify({ state: 'unreachable', reason }),
      })
    );

    const result = await mountAndObserve(page);

    expect(result.state).toBe('unreachable');
    expect(result.personaCount, 'unreachable carries no personas').toBe(0);
    expect(names(result)).toContain('registry-unreachable');
    expect(
      names(result),
      'INVARIANTS §1: an unreachable roster MUST NOT settle as loaded'
    ).not.toContain('registry-loaded');

    const unreachable = result.events.find((e) => e.name === 'registry-unreachable');
    // The reason travels verbatim from the endpoint's 503 body — the
    // operator is told WHY, not just that something went wrong.
    expect(unreachable.detail.reason).toContain(reason);
  });

  test('unreachable declared in a 200 body is honored, not read as empty', async ({
    page,
  }) => {
    // The endpoint does not currently produce this shape, but the
    // component tolerates it (grove-persona-registry.js `_settle`), and
    // §1 says a declared unreachable must never collapse into empty.
    await page.goto('/');
    await page.route(ENDPOINT, (route) =>
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ state: 'unreachable', reason: 'e2e-fixture: 200-carried' }),
      })
    );

    const result = await mountAndObserve(page);

    expect(result.state).toBe('unreachable');
    expect(names(result)).toEqual(['registry-unreachable']);
    expect(result.events[0].detail.reason).toContain('e2e-fixture: 200-carried');
  });
});
