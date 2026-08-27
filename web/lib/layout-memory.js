// b17: WGRV1 ΔΣ=42
/**
 * layout-memory — per-viewer persistence for <grove-card> position + state.
 *
 * Grove's cards are summonable (D12) and slide from a visible home edge
 * (D14). Tony's desk should be quiet by default, yet remember which panels
 * he lives with: which edge each one is docked to, whether it was up when
 * he last closed the browser, whether he pinned it to summon on boot.
 * This module is the little brain that keeps those choices around, per
 * viewer, in the browser — nothing crosses the wire.
 *
 * Storage:
 *   localStorage key `grove:layout:v1:<cardId>` → JSON
 *     { edge: "top"|"bottom"|"left"|"right",
 *       state: "idle"|"summoned"|"primary"|"secondary"|"dismissed",
 *       pinned: boolean }
 *
 *   The `v1` in the key is an explicit version marker. If the value shape
 *   must ever change, bump to `v2` — never migrate in place.
 *
 * Every localStorage access is wrapped in try/catch: private windows,
 * cleared storage, and browsers with site-data disabled will throw. Writes
 * silently drop; reads return null. A corrupted value in a key is treated
 * as absent (recall → null), not thrown up to the caller.
 *
 * Zero dependencies, vanilla ES module, per D9. Does not modify
 * <grove-card> — wires to it via its public `summon` / `dismiss` events
 * and its state / home-edge attributes.
 */

const KEY_PREFIX = "grove:layout:v1:";
const EDGES = new Set(["top", "bottom", "left", "right"]);
const STATES = new Set(["idle", "summoned", "primary", "secondary", "dismissed"]);
const LOG_TAG = "[layout-memory]";

// Track keys we've already warned about so we don't spam the console on
// repeated write failures for the same card.
const _warnedKeys = new Set();

// WeakSet of card elements already attached; guards against double-wiring.
const _attached = new WeakSet();

function _storage() {
  // Access via a try/catch — even reading `globalThis.localStorage` can
  // throw in some browser privacy modes.
  try {
    return globalThis.localStorage || null;
  } catch (_e) {
    return null;
  }
}

function _keyFor(cardId) {
  return KEY_PREFIX + String(cardId);
}

function _sanitize(rec) {
  if (!rec || typeof rec !== "object") return null;
  const out = {};
  if (typeof rec.edge === "string" && EDGES.has(rec.edge)) out.edge = rec.edge;
  if (typeof rec.state === "string" && STATES.has(rec.state)) out.state = rec.state;
  if (typeof rec.pinned === "boolean") out.pinned = rec.pinned;
  return Object.keys(out).length ? out : null;
}

/**
 * Persist a card's remembered layout. Silently drops on storage failure
 * (private window, cleared site data, quota); logs a single console.info
 * per key on first failure so a viewer can see it if they look, but no
 * console.error — this is not an error, it's the browser doing its job.
 */
function remember(cardId, patch) {
  if (!cardId) return;
  const clean = _sanitize(patch);
  if (!clean) return;
  const key = _keyFor(cardId);
  const store = _storage();
  if (!store) return;
  let existing = null;
  try {
    const raw = store.getItem(key);
    if (raw) existing = _sanitize(JSON.parse(raw));
  } catch (_e) {
    existing = null;
  }
  const merged = Object.assign({}, existing || {}, clean);
  try {
    store.setItem(key, JSON.stringify(merged));
  } catch (_e) {
    if (!_warnedKeys.has(key)) {
      _warnedKeys.add(key);
      try {
        // eslint-disable-next-line no-console
        console.info(LOG_TAG, "write dropped for", key);
      } catch (_ignored) { /* console can also throw */ }
    }
  }
}

/**
 * Return the remembered layout for a card id, or null when nothing has
 * been stored (or the stored value is corrupted / storage is unreachable).
 */
function recall(cardId) {
  if (!cardId) return null;
  const store = _storage();
  if (!store) return null;
  let raw;
  try {
    raw = store.getItem(_keyFor(cardId));
  } catch (_e) {
    return null;
  }
  if (!raw) return null;
  let parsed;
  try {
    parsed = JSON.parse(raw);
  } catch (_e) {
    return null;
  }
  return _sanitize(parsed);
}

/**
 * Remove a card's remembered layout entirely. No-op when storage is
 * unreachable or the key isn't there.
 */
function forget(cardId) {
  if (!cardId) return;
  const store = _storage();
  if (!store) return;
  try {
    store.removeItem(_keyFor(cardId));
  } catch (_e) {
    /* drop */
  }
}

/**
 * List the card ids currently marked pinned — for a summon-on-boot pass.
 * Ids are returned in whatever order localStorage yields them; callers
 * that need a stable order should sort themselves.
 */
function pinned() {
  const store = _storage();
  if (!store) return [];
  let n = 0;
  try {
    n = store.length || 0;
  } catch (_e) {
    return [];
  }
  const out = [];
  for (let i = 0; i < n; i++) {
    let key;
    try {
      key = store.key(i);
    } catch (_e) {
      continue;
    }
    if (!key || !key.startsWith(KEY_PREFIX)) continue;
    let raw;
    try {
      raw = store.getItem(key);
    } catch (_e) {
      continue;
    }
    if (!raw) continue;
    let rec;
    try {
      rec = JSON.parse(raw);
    } catch (_e) {
      continue;
    }
    const clean = _sanitize(rec);
    if (clean && clean.pinned) {
      out.push(key.slice(KEY_PREFIX.length));
    }
  }
  return out;
}

/**
 * Wire a <grove-card id="…"> element to layout-memory. On attach, applies
 * any remembered edge/state via setAttribute; then listens for the card's
 * `summon` and `dismiss` events to persist future changes. Idempotent —
 * attaching the same element twice is a no-op.
 */
function attach(cardEl) {
  if (!cardEl) return;
  if (_attached.has(cardEl)) return;
  const id = cardEl.id;
  if (!id) return;
  _attached.add(cardEl);

  const stored = recall(id);
  if (stored) {
    if (stored.edge && cardEl.setAttribute) {
      cardEl.setAttribute("home-edge", stored.edge);
    }
    if (stored.state && cardEl.setAttribute) {
      cardEl.setAttribute("state", stored.state);
    }
  }

  const onSummon = (ev) => {
    const detailState =
      (ev && ev.detail && typeof ev.detail.state === "string" && ev.detail.state) ||
      (cardEl.getAttribute && cardEl.getAttribute("state")) ||
      "summoned";
    const edge = cardEl.getAttribute && cardEl.getAttribute("home-edge");
    const patch = { state: detailState };
    if (edge) patch.edge = edge;
    remember(id, patch);
  };
  const onDismiss = () => {
    const edge = cardEl.getAttribute && cardEl.getAttribute("home-edge");
    const patch = { state: "dismissed" };
    if (edge) patch.edge = edge;
    remember(id, patch);
  };

  cardEl.addEventListener("summon", onSummon);
  cardEl.addEventListener("dismiss", onDismiss);
}

export { remember, recall, forget, attach, pinned, KEY_PREFIX };
