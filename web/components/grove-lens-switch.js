// b17: WGRV1 ΔΣ=42
/**
 * <grove-lens-switch> — tri-modal lens toggle for Willow's Grove desk.
 *
 * Premise doc anchors:
 *   P8  — the tri-modal seat: Governance / PM / PA. One operator, three
 *         posture-lenses on the same fleet, not three separate workspaces.
 *   C12 — the switch is a lens on the Kart queue first, not a workspace
 *         divider. Each lens filters queue/cards by which operator-persona
 *         cares:
 *           governance → L4-authority items + envelopes + refusal chips.
 *           pm         → L2/L3 items + proposals.
 *           pa         → L1 items + reminders + drafts (least-surprising
 *                        landing on first boot — Tony's own drafts and low-
 *                        stakes items are what he opens the desk to).
 *   D9  — vanilla JS + Web Components + no build step, zero imports.
 *   D14 — workshop metaphor: the lens picks a working posture, not a room.
 *
 * Renders three toggle buttons (inline, evenly spaced). The active button
 * wears the willow-frond green (#4ade80); the two inactive ones wear the
 * pigeon color (#94a3b8) the rest of the grove already uses for a resting
 * chrome tone. Background is the same warm #1a1409 the other components
 * share so the switch sits on the top strip without a seam.
 *
 * Persona sigils (V6 stand-ins — a real persona registry lookup can replace
 * these later; the sigils are stable enough to hard-code as a fallback):
 *   Governance ⚖   PM ▤   PA ~
 *
 * Behavior:
 *   * Emits `lens-change` CustomEvent({detail: {lens}}) on every click.
 *     Bubbles + composed so listeners outside the shadow tree can hook it.
 *   * Persists the last-picked lens to localStorage key `grove:lens:v1`,
 *     wrapped in try/catch — same discipline as `web/lib/layout-memory.js`
 *     (private windows / cleared storage / quota all throw silently, we
 *     never crash the boot).
 *   * On first boot with no stored value, defaults to `pa` — the lens with
 *     the smallest blast radius and the highest chance of matching what
 *     Tony wanted when he opened the browser.
 *   * Sets `data-lens="<lens>"` on `document.body` on every change (and on
 *     first paint) so page-scoped CSS can hide/show cards per lens with
 *     rules like `[data-lens="governance"] .lens-pa { display: none }`.
 *
 * Attributes:
 *   lens — current lens; one of "governance" | "pm" | "pa". Attribute-
 *          reactive: setAttribute("lens", "pm") re-paints and mirrors to
 *          document.body without a click. Setting an unknown value is a
 *          no-op (the previous lens stays active); this mirrors the
 *          registry-miss stance in <grove-cast-chip>.
 *
 * @element grove-lens-switch
 */

const STORAGE_KEY = "grove:lens:v1";
const DEFAULT_LENS = "pa";
const LENSES = ["governance", "pm", "pa"];
const LENS_SET = new Set(LENSES);
const SIGILS = { governance: "⚖", pm: "▤", pa: "~" };
const LABELS = { governance: "governance", pm: "pm", pa: "pa" };

const ACTIVE = "#4ade80";
const PIGEON = "#94a3b8";
const BG = "#1a1409";
const BORDER = "#3a2c1f";

const OBSERVED = ["lens"];

function _storage() {
  try {
    return globalThis.localStorage || null;
  } catch (_e) {
    return null;
  }
}

function _readStored() {
  const store = _storage();
  if (!store) return null;
  let raw = null;
  try {
    raw = store.getItem(STORAGE_KEY);
  } catch (_e) {
    return null;
  }
  if (!raw || !LENS_SET.has(raw)) return null;
  return raw;
}

function _writeStored(lens) {
  if (!LENS_SET.has(lens)) return;
  const store = _storage();
  if (!store) return;
  try {
    store.setItem(STORAGE_KEY, lens);
  } catch (_e) {
    /* drop — quota / private mode / disabled storage */
  }
}

function _mirrorBody(lens) {
  try {
    const body = globalThis.document && globalThis.document.body;
    if (body && body.setAttribute) body.setAttribute("data-lens", lens);
  } catch (_e) {
    /* drop — no document (SSR / node --check) */
  }
}

class GroveLensSwitch extends HTMLElement {
  static get observedAttributes() { return OBSERVED; }

  constructor() {
    super();
    this._root = this.attachShadow({ mode: "open" });
    this._onClick = this._onClick.bind(this);
    this._render();
  }

  connectedCallback() {
    // Resolve the initial lens: attribute > stored > default. Do not fire
    // an event on first paint — the operator did not click anything yet.
    let initial = this.getAttribute("lens");
    if (!LENS_SET.has(initial)) initial = _readStored();
    if (!LENS_SET.has(initial)) initial = DEFAULT_LENS;
    // Set attribute silently: attributeChangedCallback handles paint+mirror.
    if (this.getAttribute("lens") !== initial) {
      this.setAttribute("lens", initial);
    } else {
      this._paint();
      _mirrorBody(initial);
    }
    this._root.addEventListener("click", this._onClick);
  }

  disconnectedCallback() {
    this._root.removeEventListener("click", this._onClick);
  }

  attributeChangedCallback(name, oldVal, newVal) {
    if (oldVal === newVal) return;
    if (name !== "lens") return;
    if (!LENS_SET.has(newVal)) {
      // Reject unknown values by reverting to the old one (or default).
      const restore = LENS_SET.has(oldVal) ? oldVal : DEFAULT_LENS;
      if (restore !== newVal) this.setAttribute("lens", restore);
      return;
    }
    this._paint();
    _mirrorBody(newVal);
  }

  // ---- internals ----
  _render() {
    this._root.innerHTML = `
      <style>
        :host {
          display: inline-flex;
          align-items: center;
          gap: 0.35rem;
          padding: 3px;
          background: ${BG};
          border: 1px solid ${BORDER};
          border-radius: 999px;
          font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
          font-size: 12px;
          line-height: 1.4;
          user-select: none;
        }
        button {
          display: inline-flex;
          align-items: center;
          gap: 0.3rem;
          padding: 3px 10px;
          background: transparent;
          color: ${PIGEON};
          border: 1px solid transparent;
          border-radius: 999px;
          font: inherit;
          cursor: pointer;
          transition: color 120ms ease-out, border-color 120ms ease-out,
                      background 120ms ease-out;
        }
        button:hover { filter: brightness(1.15); }
        button:focus-visible {
          outline: 2px solid ${ACTIVE};
          outline-offset: 2px;
        }
        button[aria-pressed="true"] {
          color: ${ACTIVE};
          border-color: ${ACTIVE};
          background: rgba(74, 222, 128, 0.08);
        }
        .sigil { font-weight: 600; }
        .name  { color: inherit; }
      </style>
      <div role="group" aria-label="grove lens">
        ${LENSES.map((lens) => `
          <button type="button" part="button ${lens}"
                  data-lens="${lens}"
                  aria-pressed="false"
                  title="lens: ${LABELS[lens]}">
            <span class="sigil" aria-hidden="true">${SIGILS[lens]}</span>
            <span class="name">${LABELS[lens]}</span>
          </button>
        `).join("")}
      </div>
    `;
    this._buttons = Array.from(this._root.querySelectorAll("button[data-lens]"));
  }

  _paint() {
    const active = this.getAttribute("lens") || DEFAULT_LENS;
    for (const btn of this._buttons || []) {
      const on = btn.getAttribute("data-lens") === active;
      btn.setAttribute("aria-pressed", on ? "true" : "false");
    }
  }

  _onClick(ev) {
    const target = ev.target && ev.target.closest && ev.target.closest("button[data-lens]");
    if (!target) return;
    const lens = target.getAttribute("data-lens");
    if (!LENS_SET.has(lens)) return;
    if (lens === this.getAttribute("lens")) return;
    this.setAttribute("lens", lens);
    _writeStored(lens);
    this.dispatchEvent(new CustomEvent("lens-change", {
      bubbles: true, composed: true, detail: { lens },
    }));
  }
}

if (typeof customElements !== "undefined" && !customElements.get("grove-lens-switch")) {
  customElements.define("grove-lens-switch", GroveLensSwitch);
}

export { GroveLensSwitch, STORAGE_KEY, DEFAULT_LENS, LENSES };
