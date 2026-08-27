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
const { existsSync } = require('fs');

// Reuse the pre-installed Chromium image ship (see the CI image build)
// when it is present; otherwise fall through to Playwright's own
// download path.
const PREINSTALLED_CHROMIUM =
  '/opt/pw-browsers/chromium-1194/chrome-linux/chrome';

const chromiumUse = {};
if (existsSync(PREINSTALLED_CHROMIUM)) {
  chromiumUse.executablePath = PREINSTALLED_CHROMIUM;
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
