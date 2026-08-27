// b17: WGRV1 ΔΣ=42
/**
 * layout-memory-boot — page-side wiring for web/lib/layout-memory.
 *
 * On DOM ready this module walks every ``<grove-card id="…">`` on the
 * served page and calls ``attach(cardEl)`` so per-viewer edge/state
 * choices are remembered across reloads (D12 — summonable cards, D14 —
 * the workshop remembers where you docked a card).
 *
 * It then reads ``pinned()`` and calls ``.summon()`` on every pinned
 * card whose element is present. Cards the viewer pinned at last close
 * reopen on the next visit; nothing crosses the wire.
 *
 * Ordering discipline: this script is loaded AFTER the ``grove-card``
 * component script, so ``customElements.define("grove-card", …)`` has
 * already run by the time we walk the DOM by tag name.
 *
 * Idempotence:
 *   - ``attach`` in ``layout-memory.js`` already carries a WeakSet
 *     guard so a card is only wired once even if this module runs
 *     twice.
 *   - This module additionally sets ``window.__groveLayoutBooted``
 *     the first time through and short-circuits on any subsequent
 *     import — a single explicit line for anyone reading the code.
 *
 * Zero dependencies beyond the sibling ``web/lib/layout-memory.js``.
 */

import { attach, pinned } from "../lib/layout-memory.js";

const LOG_TAG = "[layout-memory-boot]";

// Track ids we failed to wire so we log each one only once (log-once).
const _wireFailWarned = new Set();

function _boot() {
  let cards = [];
  try {
    cards = Array.from(
      document.querySelectorAll("grove-card[id]")
    );
  } catch (_e) {
    cards = [];
  }

  for (const card of cards) {
    const id = card && card.id;
    if (!id) continue;
    try {
      attach(card);
    } catch (_e) {
      if (!_wireFailWarned.has(id)) {
        _wireFailWarned.add(id);
        try {
          // eslint-disable-next-line no-console
          console.info(LOG_TAG, "attach failed for", id);
        } catch (_ignored) { /* console can also throw */ }
      }
    }
  }

  let pins = [];
  try {
    pins = pinned() || [];
  } catch (_e) {
    pins = [];
  }
  for (const id of pins) {
    if (!id) continue;
    let el = null;
    try {
      el = document.getElementById(id);
    } catch (_e) {
      el = null;
    }
    if (!el) continue;
    // ``.summon()`` is the <grove-card> public helper. Guard for the
    // case where a non-<grove-card> element happens to share the id.
    if (typeof el.summon === "function") {
      try {
        el.summon();
      } catch (_e) {
        /* drop — summon should not throw, but if it does, don't take
           the whole boot down. */
      }
    }
  }
}

function _run() {
  if (typeof window === "undefined") return;
  if (window.__groveLayoutBooted) return;
  window.__groveLayoutBooted = true;

  const doc = typeof document !== "undefined" ? document : null;
  if (!doc) return;

  if (doc.readyState === "loading") {
    doc.addEventListener("DOMContentLoaded", _boot, { once: true });
  } else {
    _boot();
  }
}

_run();

export { _boot as __bootForTest };
