// playwright.config.js — Grove browser-driven end-to-end suite config.
// b17: GRPW · ΔΣ=42
//
// Configuration only in Grove v0.9 PR 4. The `tests/e2e/` suite itself
// is populated by PR 9. Downstream repos and CI can install browsers
// (`npx playwright install chromium`) and lint this config today.
//
// Guard rails:
//   - baseURL points at the loopback ephemeral port grove_serve binds to
//     during CI (8766, distinct from the production 8765 in
//     `run_mcp.sh --serve` so tests don't collide with a running seat).
//   - The `webServer` block spins Grove's served page for the run and
//     is torn down when the suite exits.
//   - The Chromium project is the only browser configured — the tunnel/
//     seat page is chromium-first; the other engines can be added when
//     a real cross-browser gap surfaces.

// @ts-check
const { defineConfig } = require('@playwright/test');
const { existsSync, readdirSync } = require('fs');
const { join } = require('path');

// Reuse a pre-installed Chromium from the image (see the CI image build)
// when one is present; otherwise fall through to Playwright's own
// download path. The browsers root is overridable via
// PLAYWRIGHT_BROWSERS_PATH, and the build number is NOT pinned — an
// image carrying `chromium-1194` today may carry a newer build
// tomorrow, and a hardcoded number silently stops matching.
const BROWSERS_ROOT = process.env.PLAYWRIGHT_BROWSERS_PATH || '/opt/pw-browsers';

function preinstalledChromium() {
  if (!existsSync(BROWSERS_ROOT)) return null;
  const builds = readdirSync(BROWSERS_ROOT)
    // headless-shell builds are a different binary layout; full chromium only.
    .filter((name) => /^chromium-\d+$/.test(name))
    // Highest build number first, so a refreshed image wins over a stale one.
    .sort((a, b) => Number(b.split('-')[1]) - Number(a.split('-')[1]));
  for (const build of builds) {
    const candidate = join(BROWSERS_ROOT, build, 'chrome-linux', 'chrome');
    if (existsSync(candidate)) return candidate;
  }
  return null;
}

// `executablePath` is a launch option, not a top-level `use` key — set
// directly on `use` it is silently ignored and Playwright goes looking
// for the headless shell of whatever build its own version pins.
const chromiumUse = {};
const preinstalled = preinstalledChromium();
if (preinstalled) {
  chromiumUse.launchOptions = { executablePath: preinstalled };
}

module.exports = defineConfig({
  testDir: 'tests/e2e',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 1 : 0,
  reporter: process.env.CI ? [['list'], ['github']] : 'list',

  use: {
    baseURL: 'http://127.0.0.1:8766',
    trace: 'retain-on-failure',
    screenshot: 'only-on-failure',
  },

  webServer: {
    command: 'python3 -m grove_serve',
    port: 8766,
    timeout: 30_000,
    reuseExistingServer: !process.env.CI,
  },

  projects: [
    {
      name: 'chromium',
      use: {
        browserName: 'chromium',
        ...chromiumUse,
      },
    },
  ],
});
