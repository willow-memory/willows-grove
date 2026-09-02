// b17: WGRV1 ΔΣ=42
/**
 * <grove-lens-switch> — DEPRECATED as hero chrome (Jarvis addendum 2026-09-02).
 *
 * C12 misfit: shipping this as an operator Governance / PM / PA gearshift
 * oversold P8. Tony's Jarvis does not ask Tony to switch modes. The served
 * page (`grove_html.render_page`) no longer mounts this element.
 *
 * Retained for harness / quiet tooling. Optional Kart `?lens=` may still
 * filter the dispatch API without putting this chrome in the first viewport.
 *
 * Historical notes (do not restore as hero):
 *   P8  — offices are back-of-house triage questions for Willow.
 *   C12 — demoted; was "lens on Kart queue the operator picks."
 *   D9  — vanilla JS + Web Components + no build step, zero imports.
 *
 * @element grove-lens-switch
 * @deprecated Not mounted on the served Grove page.
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
