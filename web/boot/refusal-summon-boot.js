// b17: WGRV1 ΔΣ=42
/**
 * refusal-summon-boot — page-side auto-summon wiring for Nestor refusals.
 *
 * This module keeps two contracts:
 *
 *  1. Listen for a global ``window`` ``nestor-refusal`` CustomEvent whose
 *     ``detail`` is a verbatim Nestor refusal payload (as shaped by
 *     ``grove/nestor_client.py::NestorClient.refusal`` and passed through
 *     ``POST /api/nestor/decide`` unchanged — V5 discipline, no paraphrase
 *     on our side). On receive, construct a ``<grove-refusal-chip>``,
 *     assign the payload to its ``data`` property, append it to
 *     ``#refusal-chip-mount`` at the bottom of ``<body>``, and — if the
 *     element defines one — call ``.summon()`` so the chip un-hides.
 *
 *  2. Expose ``window.groveNestorAsk(claim)`` — a console/operator helper
 *     that POSTs ``{"claim": ...}`` to ``/api/nestor/decide`` and, when
 *     the verdict is ``refused``, dispatches the ``nestor-refusal``
 *     window CustomEvent with the refusal payload as the event detail.
 *     A proper UI hook (button on a card, form on a page) is a follow-up.
 *
 * V5 discipline: the refusal payload is neither reshaped nor summarised
 * on its way from ``fetch`` to the CustomEvent to the chip. The chip
 * itself renders ``body`` via ``textContent`` (see
 * ``web/components/grove-refusal-chip.js``).
 *
 * Idempotence: guarded by ``window.__groveRefusalBooted``. Safe to load
 * this module twice — the second import short-circuits before any
 * listener is attached or helper is redefined.
 *
 * Zero imports beyond the sibling ``grove-refusal-chip`` component (whose
 * component script the page loads before this boot module), and even
 * that is a *page-level* load rather than an ES ``import`` here — this
 * file only needs the custom element to be already ``customElements``
 * defined by the time an event arrives.
 */

const LOG_TAG = "[refusal-summon-boot]";
const MOUNT_ID = "refusal-chip-mount";
const EVENT_NAME = "nestor-refusal";
const DECIDE_URL = "/api/nestor/decide";

function _findOrCreateMount() {
  if (typeof document === "undefined") return null;
  let mount = null;
  try {
    mount = document.getElementById(MOUNT_ID);
  } catch (_e) {
    mount = null;
  }
  if (mount) return mount;
  // The served page ships #refusal-chip-mount in <body>, but if the
  // module is imported into a bare document (a test harness, a fragment
  // preview) we still want to keep working — synthesize the mount.
  try {
    if (!document.body) return null;
    mount = document.createElement("div");
    mount.id = MOUNT_ID;
    document.body.appendChild(mount);
    return mount;
  } catch (_e) {
    return null;
  }
}

function _summonRefusalChip(payload) {
  if (!payload || typeof payload !== "object") return null;
  const mount = _findOrCreateMount();
  if (!mount) return null;
  let chip = null;
  try {
    chip = document.createElement("grove-refusal-chip");
  } catch (_e) {
    return null;
  }
  // V5: pass the payload through without touching a byte.
  try {
    chip.data = payload;
  } catch (_e) {
    // Element not upgraded yet, or setter rejects — fall back to the
    // attribute path so the chip still ingests the payload.
    try {
      chip.setAttribute("payload", JSON.stringify(payload));
    } catch (_e2) { /* drop — nothing else to try */ }
  }
  try {
    mount.appendChild(chip);
  } catch (_e) {
    return null;
  }
  if (typeof chip.summon === "function") {
    try { chip.summon(); } catch (_e) { /* summon must not take the boot down */ }
  }
  return chip;
}

function _onRefusalEvent(ev) {
  const detail = ev && ev.detail;
  if (!detail) return;
  _summonRefusalChip(detail);
}

async function _groveNestorAsk(claim) {
  if (typeof claim !== "string" || !claim.trim()) {
    return { verdict: "invalid", reason: "claim required" };
  }
  let resp;
  try {
    resp = await fetch(DECIDE_URL, {
      method: "POST",
      headers: {
        "content-type": "application/json",
        "accept": "application/json",
      },
      body: JSON.stringify({ claim: claim }),
    });
  } catch (err) {
    try {
      // eslint-disable-next-line no-console
      console.info(LOG_TAG, "fetch failed:", err);
    } catch (_ignored) { /* console can also throw */ }
    return { verdict: "unavailable", reason: "network error" };
  }
  let body = null;
  try {
    body = await resp.json();
  } catch (_e) {
    body = null;
  }
  if (body && body.verdict === "refused" && body.refusal) {
    try {
      // V5: dispatch the refusal payload unchanged.
      window.dispatchEvent(new CustomEvent(EVENT_NAME, { detail: body.refusal }));
    } catch (_e) { /* dispatch failing should not shadow the caller */ }
  }
  return body;
}

function _run() {
  if (typeof window === "undefined") return;
  if (window.__groveRefusalBooted) return;
  window.__groveRefusalBooted = true;

  try {
    window.addEventListener(EVENT_NAME, _onRefusalEvent);
  } catch (_e) { /* addEventListener should not throw here */ }

  try {
    window.groveNestorAsk = _groveNestorAsk;
  } catch (_e) { /* assigning to window can throw in exotic sandboxes */ }
}

_run();

export {
  _groveNestorAsk as __askForTest,
  _onRefusalEvent as __onRefusalForTest,
  _summonRefusalChip as __summonForTest,
};
