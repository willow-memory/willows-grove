/**
 * standing-boot — the ambient top strip's live state.
 *
 * The strip used to render "standing" / "grove stable" as static markup
 * (Loki finding #31): the operator read a status claim with no source
 * behind it. That was replaced with the neutral placeholder "reading
 * standing…", which is honest but permanent — the strip never told the
 * operator anything, in either direction.
 *
 * This module closes that: it polls ``GET /health`` (the served page's
 * own liveness route — ``{"ok": true, "commit": "<short sha>"}``) and
 * paints the strip from the answer, honoring the three-state contract
 * (INVARIANTS.md §1) at the visual layer:
 *
 *   loading      — "reading standing…"       (the pre-fetch sentinel,
 *                  already in the served markup so there is no flash)
 *   populated    — "seat live · <short sha>"  (the seat answered)
 *   unreachable  — "seat unreachable — <why>" (it did not)
 *
 * There is no "empty" branch here: /health either answers or it does
 * not. The two states that exist MUST look different to the operator,
 * so the strip carries `data-standing-state` and the page CSS paints
 * the dot differently per state.
 *
 * What the strip does NOT claim: that any seam behind the seat (Postgres,
 * willow-mcp, Nestor) is healthy. /health answers for the served-page
 * process only, and the wording says exactly that much. Each panel
 * reports its own seam's state in its own §1 vocabulary.
 *
 * Zero dependencies. No build step (premise D9).
 */

const LOG_TAG = "[standing-boot]";
const HEALTH_URL = "/health";
const DEFAULT_POLL_MS = 10000;
// Below this the poll is a busy-loop against the operator's own seat.
const MIN_POLL_MS = 1000;

// log-once, per the fleet's absence discipline — an unreachable seat
// must not fill the console with one line per poll.
let _loggedUnreachable = false;

/** @returns {HTMLElement|null} the strip's live-text slot, if present. */
function _slot() {
  try {
    return document.querySelector("[data-standing]");
  } catch (_e) {
    return null;
  }
}

/** @returns {HTMLElement|null} the strip itself (carries the state attr). */
function _strip(slot) {
  if (!slot) return null;
  return slot.closest ? slot.closest(".strip") : null;
}

function _paint(state, text) {
  const slot = _slot();
  if (!slot) return;
  slot.textContent = text;
  const strip = _strip(slot);
  if (strip) strip.setAttribute("data-standing-state", state);
}

function _pollMs() {
  const slot = _slot();
  const raw = slot && slot.getAttribute("data-poll-ms");
  const parsed = Number(raw);
  if (!raw || !Number.isFinite(parsed)) return DEFAULT_POLL_MS;
  return Math.max(MIN_POLL_MS, parsed);
}

async function _readHealth() {
  if (typeof fetch !== "function") {
    throw new Error("fetch() unavailable");
  }
  // cache: no-store — a cached 200 would keep the strip claiming the
  // seat is live after the process has gone away.
  const resp = await fetch(HEALTH_URL, {
    credentials: "same-origin",
    cache: "no-store",
  });
  if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
  const body = await resp.json();
  if (!body || body.ok !== true) {
    throw new Error("/health did not answer ok");
  }
  return body;
}

async function _tick() {
  // Skip the poll while the tab is hidden; repaint on the next visible
  // tick. Nothing on the strip changes while nobody is reading it.
  if (typeof document !== "undefined" && document.visibilityState === "hidden") {
    return;
  }
  try {
    const body = await _readHealth();
    // `commit` is "unknown" when git is absent or this is not a repo —
    // grove_serve answers honestly rather than fabricating a sha, and
    // the strip carries that word through rather than hiding it.
    const commit = String(body.commit || "unknown");
    _paint("populated", `seat live · ${commit}`);
    _loggedUnreachable = false;
  } catch (err) {
    const reason = (err && err.message) || String(err);
    _paint("unreachable", `seat unreachable — ${reason}`);
    if (!_loggedUnreachable) {
      _loggedUnreachable = true;
      if (typeof console !== "undefined" && console.info) {
        console.info(`${LOG_TAG} ${HEALTH_URL} unreachable:`, reason);
      }
    }
  }
}

function _boot() {
  if (window.__groveStandingBooted) return;
  window.__groveStandingBooted = true;
  // Exposed so an operator (or a test) can force a repaint without
  // waiting out the poll interval.
  window.groveReadStanding = _tick;
  _tick();
  const ms = _pollMs();
  const timer = setInterval(_tick, ms);
  // A repaint the moment the tab comes back, rather than up to one
  // full interval of stale text.
  try {
    document.addEventListener("visibilitychange", () => {
      if (document.visibilityState === "visible") _tick();
    });
  } catch (_e) { /* no visibility API — the interval still runs */ }
  window.__groveStandingTimer = timer;
}

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", _boot, { once: true });
} else {
  _boot();
}

export { _tick as readStanding };
