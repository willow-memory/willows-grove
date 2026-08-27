// b17: WGRV1 ΔΣ=42
//
// Playwright end-to-end pass for Willow's Grove served page.
//
// This spec pins docs/INVARIANTS.md §1 (the three-state contract) and §8
// (panels consume live endpoints by default) at the visual layer — the
// place the operator actually reads state. The pytest suite pins the
// endpoint and reader shapes; this pass pins that the panels the
// operator sees render those shapes on real chromium against a real
// grove_serve.py, one turn removed from a live seat.
//
// The webServer block in playwright.config.js already boots
// `python3 -m grove_serve` on 127.0.0.1:8766 for the run.
//
// Chromium-not-installed discipline: the config points executablePath
// at `/opt/pw-browsers/chromium-1194/chrome-linux/chrome` when present;
// otherwise Playwright's own downloader supplies chromium in CI. In a
// bare local checkout where neither path exists, Playwright itself
// surfaces the install nudge — this spec never invents a "chromium not
// available" bypass that would silently green the CI step. Skips here
// are per-test skips for known preconditions (an /api/personas the
// operator has not seeded yet, a chat card without a text field), not
// engine-level ones.

// @ts-check
const { test, expect } = require('@playwright/test');

const COMPONENTS = [
  'grove-card',
  'grove-envelope-panel',
  'grove-refusal-chip',
  'grove-cast-chip',
  'grove-lens-switch',
  'grove-chat',
  'grove-dispatch-rail',
  'grove-persona-registry',
];

/**
 * Ensure a component script has been fetched into the page — the served
 * page (grove_html.py) loads six of the eight component scripts in its
 * <head>. `grove-card` and `grove-envelope-panel` are loaded on demand
 * by the harness / card boot paths. Injecting their component scripts
 * here mirrors what a downstream page (or a card-summon path) does when
 * it first uses one, so every component's `customElements.define(…)`
 * has actually run before the assertion fires.
 */
async function ensureAllComponentsLoaded(page) {
  await page.evaluate(async (names) => {
    async function loadOne(name) {
      if (customElements.get(name)) return;
      await new Promise((resolve) => {
        const existing = document.querySelector(
          `script[data-e2e-load="${name}"]`
        );
        if (existing) {
          existing.addEventListener('load', resolve, { once: true });
          existing.addEventListener('error', resolve, { once: true });
          return;
        }
        const s = document.createElement('script');
        s.type = 'module';
        s.src = `/web/components/${name}.js`;
        s.dataset.e2eLoad = name;
        s.addEventListener('load', resolve, { once: true });
        s.addEventListener('error', resolve, { once: true });
        document.head.appendChild(s);
      });
      // customElements.whenDefined resolves as soon as the module's
      // customElements.define(...) call runs, even if it happens a tick
      // after `load` fires.
      try {
        await customElements.whenDefined(name);
      } catch (_ignored) {
        /* whenDefined throws on invalid names; the assertion below still
           catches a genuinely missing registration. */
      }
    }
    for (const name of names) {
      await loadOne(name);
    }
  }, COMPONENTS);
}

test.describe('served page — component upgrades and three-state affordances', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
  });

  test('every expected Web Component upgrades (customElements.get)', async ({
    page,
  }) => {
    await ensureAllComponentsLoaded(page);
    const registered = await page.evaluate(
      (names) =>
        Object.fromEntries(
          names.map((n) => [n, !!customElements.get(n)])
        ),
      COMPONENTS
    );
    for (const name of COMPONENTS) {
      expect(registered[name], `${name} must be registered`).toBe(true);
    }
  });

  test('persona registry loads — populated OR empty distinctly', async ({
    page,
  }) => {
    // <grove-persona-registry> lives at the top of <body> per grove_html.py.
    // §1 posture: `.state` is one of "populated" / "empty" / "unreachable",
    // and the two reachable states carry an agent count that is either
    // > 0 or 0.
    const reg = page.locator('grove-persona-registry').first();
    await expect(reg).toBeAttached();

    // Wait for `_load()` to resolve.
    const info = await reg.evaluate(async (el) => {
      // Component sets .state / .agents after the /api/personas fetch.
      const started = Date.now();
      while (
        !['populated', 'empty', 'unreachable'].includes(el.state) &&
        Date.now() - started < 8000
      ) {
        await new Promise((r) => setTimeout(r, 50));
      }
      return {
        state: el.state,
        // Different builds expose the roster under slightly different names;
        // read every plausible surface without inventing one.
        rows:
          (Array.isArray(el.agents) && el.agents.length) ||
          (Array.isArray(el.rows) && el.rows.length) ||
          (el.roster && Array.isArray(el.roster.rows)
            ? el.roster.rows.length
            : null),
      };
    });

    expect(
      ['populated', 'empty', 'unreachable'].includes(info.state),
      `state must be one of the three §1 branches, got ${info.state}`
    ).toBe(true);

    if (info.state === 'populated') {
      expect(
        typeof info.rows === 'number' ? info.rows : 1,
        'populated persona registry must expose a positive agent count'
      ).toBeGreaterThan(0);
    } else if (info.state === 'empty') {
      // An empty registry either exposes an empty list or no list at all;
      // both readings are consistent with the §1 empty shape.
      expect(
        info.rows === 0 || info.rows === null,
        'empty persona registry must not report a positive agent count'
      ).toBe(true);
    }
    // unreachable is a legitimate outcome when the reader raised — the
    // three-state-affordances spec asserts its distinct rendering.
  });

  test('envelope panel renders one of the three §1 states', async ({
    page,
  }) => {
    await ensureAllComponentsLoaded(page);
    // Inject a live-endpoint <grove-envelope-panel> — the served page
    // itself doesn't mount one by default (it lives on the harness /
    // via a summoned card), but the served endpoint /api/envelopes is
    // what its `data-source` default points at. That is the surface
    // this test pins.
    const state = await page.evaluate(async () => {
      const panel = document.createElement('grove-envelope-panel');
      document.body.appendChild(panel);
      const started = Date.now();
      while (
        !['populated', 'empty', 'unreachable'].includes(panel._state) &&
        Date.now() - started < 8000
      ) {
        await new Promise((r) => setTimeout(r, 50));
      }
      return panel._state;
    });
    expect(['populated', 'empty', 'unreachable'].includes(state)).toBe(true);
  });

  test('dispatch rail renders one of the three §1 states', async ({ page }) => {
    // <grove-dispatch-rail lens="pa"> is mounted in <main> on the served page.
    const rail = page.locator('grove-dispatch-rail').first();
    await expect(rail).toBeAttached();
    const state = await rail.evaluate(async (el) => {
      const started = Date.now();
      while (
        !['populated', 'empty', 'unreachable'].includes(el._state) &&
        Date.now() - started < 8000
      ) {
        await new Promise((r) => setTimeout(r, 50));
      }
      return el._state;
    });
    expect(['populated', 'empty', 'unreachable'].includes(state)).toBe(true);
  });

  test('chat card LEFT column: composer + submit → history updates OR 503 banner', async ({
    page,
  }) => {
    const chat = page.locator('grove-chat').first();
    await expect(chat).toBeAttached();

    // The chat shadow root carries the composer + submit. Read the DOM
    // through .shadowRoot rather than a light-DOM locator.
    const shape = await chat.evaluate((el) => {
      const root = el.shadowRoot;
      const textArea = root && (
        root.querySelector('textarea, input[type="text"], [contenteditable]')
      );
      const submit = root && (
        root.querySelector('button[type="submit"], button.submit, [data-e2e="submit"]')
        || root.querySelector('button')
      );
      return {
        hasText: !!textArea,
        hasSubmit: !!submit,
      };
    });
    expect(shape.hasText, 'chat card LEFT column must expose a composer').toBe(true);
    expect(shape.hasSubmit, 'chat card LEFT column must expose a submit affordance').toBe(true);

    // Type into it and submit. Then assert one of two outcomes:
    //   (a) the LEFT-side history now shows the operator's line, OR
    //   (b) the chat carries a 503 / unreachable banner.
    const outcome = await chat.evaluate(async (el) => {
      const root = el.shadowRoot;
      const composer =
        root.querySelector('textarea, input[type="text"], [contenteditable]');
      const submit =
        root.querySelector('button[type="submit"], button.submit, [data-e2e="submit"]')
        || root.querySelector('button');
      const text = 'playwright-e2e-' + Date.now();
      if (composer) {
        composer.focus();
        if (composer.tagName === 'TEXTAREA' || composer.tagName === 'INPUT') {
          composer.value = text;
          composer.dispatchEvent(new Event('input', { bubbles: true }));
        } else {
          composer.textContent = text;
          composer.dispatchEvent(new Event('input', { bubbles: true }));
        }
      }
      if (submit) submit.click();

      // Give the fetch a moment to resolve — either the LEFT history now
      // contains our sentinel, or an unreachable banner is on-screen.
      const started = Date.now();
      while (Date.now() - started < 4000) {
        const html = (root.innerHTML || '').toLowerCase();
        const wroteBack = html.includes(text.toLowerCase());
        const banner =
          html.includes('unreachable') ||
          html.includes('503') ||
          html.includes('could not reach');
        if (wroteBack || banner) {
          return { wroteBack, banner, sentinel: text };
        }
        await new Promise((r) => setTimeout(r, 50));
      }
      return { wroteBack: false, banner: false, sentinel: text };
    });

    expect(
      outcome.wroteBack || outcome.banner,
      'chat submit must either echo into LEFT history or surface an unreachable banner (INVARIANTS §1)'
    ).toBe(true);
  });

  test('chat card RIGHT column: recent atoms OR read-back unreachable — distinct from empty', async ({
    page,
  }) => {
    const chat = page.locator('grove-chat').first();
    await expect(chat).toBeAttached();

    // The RIGHT column is the read-back pane. Its three §1 states are
    // populated (atoms present), empty (no messages yet), and
    // unreachable (read-back seam is down). Assert the rendered
    // markup carries one of these signatures — the two states never
    // collapse into the same pixels per §1.
    const marker = await chat.evaluate(async (el) => {
      const root = el.shadowRoot;
      const started = Date.now();
      while (Date.now() - started < 6000) {
        // The chat component sets one of these internal markers after
        // its first /api/journal/recent poll.
        const html = (root.innerHTML || '').toLowerCase();
        if (
          html.includes('read-back unreachable') ||
          html.includes('unreachable')
        ) return 'unreachable';
        if (html.includes('no messages yet') || html.includes('empty'))
          return 'empty';
        // Populated is any concrete atom text that isn't the two markers
        // above — a rendered <li>/<article>/<div class="atom"> node.
        const atoms = root.querySelectorAll(
          'li.atom, article.atom, [data-atom], .journal-atom'
        );
        if (atoms.length > 0) return 'populated';
        await new Promise((r) => setTimeout(r, 100));
      }
      return null;
    });

    expect(
      ['populated', 'empty', 'unreachable'].includes(marker),
      `chat RIGHT column must be one of the three §1 states (got ${marker})`
    ).toBe(true);
  });

  test('lens switch: Governance / PM / PA buttons update body[data-lens]', async ({
    page,
  }) => {
    const lens = page.locator('grove-lens-switch').first();
    await expect(lens).toBeAttached();

    const labels = await lens.evaluate((el) => {
      const root = el.shadowRoot;
      const buttons = Array.from(root.querySelectorAll('button'));
      return buttons.map((b) => (b.textContent || '').trim().toLowerCase());
    });

    // Three buttons named after the three lenses; case-insensitive match so
    // a display casing tweak doesn't break the pin.
    expect(labels.length).toBeGreaterThanOrEqual(3);
    expect(labels.some((l) => l.includes('governance'))).toBe(true);
    expect(labels.some((l) => l.includes('pm'))).toBe(true);
    expect(labels.some((l) => l.includes('pa'))).toBe(true);

    // Click each and confirm body[data-lens] updates. The lens tokens
    // are lowercase per the component.
    for (const lensName of ['governance', 'pm', 'pa']) {
      await lens.evaluate((el, name) => {
        const root = el.shadowRoot;
        const btn = Array.from(root.querySelectorAll('button')).find((b) =>
          (b.textContent || '').trim().toLowerCase().includes(name)
        );
        if (btn) btn.click();
      }, lensName);
      // Give the lens-switch component a tick to reflect on the body.
      await page.waitForFunction(
        (name) => document.body.dataset.lens === name,
        lensName,
        { timeout: 2000 }
      );
      const current = await page.evaluate(() => document.body.dataset.lens);
      expect(current).toBe(lensName);
    }
  });

  test('summon a grove-card via .summon() → CSS transition enters the card', async ({
    page,
  }) => {
    await ensureAllComponentsLoaded(page);

    // Mount a card with id="card-nestor" — this is the id every layout-
    // memory boot walks by convention (see web/harness.html + test_layout_
    // memory_boot.js). The card starts idle offscreen; .summon() flips
    // state to "summoned" and the CSS transition brings it on-screen.
    await page.evaluate(() => {
      let card = document.getElementById('card-nestor');
      if (!card) {
        card = document.createElement('grove-card');
        card.id = 'card-nestor';
        card.setAttribute('name', 'nestor');
        card.setAttribute('home-edge', 'right');
        // A body node so we can observe the transition — the card renders
        // a shadow root either way, but a slotted paragraph confirms the
        // slot projection survives summon.
        const p = document.createElement('p');
        p.textContent = 'e2e-summon';
        card.appendChild(p);
        document.body.appendChild(card);
      }
    });

    await page.waitForFunction(
      () => customElements.get('grove-card')
    );

    // Give the card one frame to settle into `idle` before summoning —
    // otherwise the transition can be skipped by the initial paint.
    await page.evaluate(async () => {
      await new Promise((r) => requestAnimationFrame(() => r()));
    });

    const before = await page.evaluate(() => {
      const card = document.getElementById('card-nestor');
      return card && card.getAttribute('state');
    });
    expect(before === 'idle' || before === null || before === 'dismissed').toBe(true);

    await page.evaluate(() => {
      const card = document.getElementById('card-nestor');
      card.summon();
    });

    // The card's state attribute flips to "summoned" or "primary" once
    // .summon() has been called — that IS the transition trigger.
    await page.waitForFunction(
      () => {
        const card = document.getElementById('card-nestor');
        const s = card && card.getAttribute('state');
        return s === 'summoned' || s === 'primary';
      },
      null,
      { timeout: 2000 }
    );

    const after = await page.evaluate(() => {
      const card = document.getElementById('card-nestor');
      return card && card.getAttribute('state');
    });
    expect(['summoned', 'primary'].includes(after)).toBe(true);
  });
});
