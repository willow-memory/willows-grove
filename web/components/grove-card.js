// b17: WGRV1 ΔΣ=42
/**
 * <grove-card> — the summonable card primitive for Willow's Grove.
 *
 * Cards float above the meadow floor, slide in from one of four edges,
 * and are dismissed via `esc`, click-outside, or the `close` slot button.
 * State transitions are driven entirely by attributes so the DOM is the
 * source of truth; JS just animates.
 *
 * Attributes:
 *   name       — human-readable card name (rendered in the titlebar).
 *   sigil      — persona sigil glyph (e.g. §, ¬, ⌸).
 *   color      — CSS color token for the card's accent border.
 *   state      — idle | summoned | primary | secondary | dismissed.
 *   home-edge  — top | bottom | left | right — the edge the card slides
 *                from (and returns to on dismiss).
 *   persona    — id of a sibling <grove-persona> element; when set the
 *                card copies color+sigil from that persona.
 *
 * Events:
 *   summon   — fired when state transitions into summoned/primary.
 *   dismiss  — fired when state transitions into dismissed.
 *
 * Slotted content is projected into the card body; a `close` slot may
 * carry a custom dismiss button (a default one is provided).
 *
 * Zero dependencies. Vanilla JS + Web Components, per D9.
 */

const TRANSITION = "250ms cubic-bezier(0.22, 1, 0.36, 1)";
const OBSERVED = ["name", "sigil", "color", "state", "home-edge", "persona"];
const EDGES = new Set(["top", "bottom", "left", "right"]);
const STATES = new Set(["idle", "summoned", "primary", "secondary", "dismissed"]);

const OFFSCREEN = {
  top: "translateY(-120%)",
  bottom: "translateY(120%)",
  left: "translateX(-120%)",
  right: "translateX(120%)",
};

class GroveCard extends HTMLElement {
  static get observedAttributes() { return OBSERVED; }

  constructor() {
    super();
    this._root = this.attachShadow({ mode: "open" });
    this._onEsc = this._onEsc.bind(this);
    this._onDocClick = this._onDocClick.bind(this);
    this._onCloseClick = this._onCloseClick.bind(this);
    this._render();
  }

  connectedCallback() {
    if (!this.hasAttribute("state")) this.setAttribute("state", "idle");
    if (!this.hasAttribute("home-edge")) this.setAttribute("home-edge", "bottom");
    this._syncPersona();
    this._applyState();
    document.addEventListener("keydown", this._onEsc);
    document.addEventListener("click", this._onDocClick, true);
  }

  disconnectedCallback() {
    document.removeEventListener("keydown", this._onEsc);
    document.removeEventListener("click", this._onDocClick, true);
  }

  attributeChangedCallback(name, oldVal, newVal) {
    if (oldVal === newVal) return;
    if (name === "state") {
      this._applyState(oldVal, newVal);
      return;
    }
    if (name === "persona") {
      this._syncPersona();
    }
    this._paint();
  }

  // ---- public helpers ----
  summon() { this.setAttribute("state", "summoned"); }
  dismiss() { this.setAttribute("state", "dismissed"); }
  promote() { this.setAttribute("state", "primary"); }

  // ---- internals ----
  _render() {
    this._root.innerHTML = `
      <style>
        :host {
          position: fixed;
          display: block;
          min-width: 220px;
          max-width: min(90vw, 520px);
          box-sizing: border-box;
          font: 14px/1.4 system-ui, sans-serif;
          color: var(--grove-fg, #1a2a1a);
          background: var(--grove-bg, #fdfef7);
          border: 1px solid var(--card-accent, #6faa6a);
          border-radius: 10px;
          box-shadow: 0 8px 24px rgba(24, 42, 24, 0.18);
          opacity: 0;
          transform: translateY(120%);
          transition:
            transform ${TRANSITION},
            opacity ${TRANSITION};
          z-index: 10;
          pointer-events: none;
        }
        :host([state="summoned"]),
        :host([state="primary"]) {
          opacity: 1;
          transform: translate(0, 0);
          pointer-events: auto;
        }
        :host([state="primary"]) { z-index: 20; }
        :host([state="secondary"]) {
          opacity: 0.55;
          transform: translate(0, 0);
          pointer-events: auto;
          z-index: 5;
        }
        :host([state="dismissed"]),
        :host([state="idle"]) {
          opacity: 0;
          pointer-events: none;
        }
        header {
          display: flex;
          align-items: center;
          gap: 0.5rem;
          padding: 0.5rem 0.75rem;
          border-bottom: 1px solid rgba(0,0,0,0.06);
        }
        .sigil {
          font-size: 1.1rem;
          color: var(--card-accent, currentColor);
        }
        .name { font-weight: 600; flex: 1; }
        button.close {
          all: unset;
          cursor: pointer;
          padding: 0.15rem 0.4rem;
          border-radius: 4px;
          color: var(--grove-muted, #6a7a6a);
        }
        button.close:hover { background: rgba(0,0,0,0.05); }
        .body { padding: 0.75rem; }
      </style>
      <header>
        <span class="sigil" part="sigil"></span>
        <span class="name" part="name"></span>
        <slot name="close">
          <button class="close" aria-label="dismiss" type="button">×</button>
        </slot>
      </header>
      <div class="body"><slot></slot></div>
    `;
    const btn = this._root.querySelector("button.close");
    if (btn) btn.addEventListener("click", this._onCloseClick);
    this._root.addEventListener("slotchange", () => {
      const slot = this._root.querySelector('slot[name="close"]');
      if (!slot) return;
      for (const el of slot.assignedElements({ flatten: true })) {
        el.removeEventListener("click", this._onCloseClick);
        el.addEventListener("click", this._onCloseClick);
      }
    });
  }

  _paint() {
    const nameEl = this._root.querySelector(".name");
    const sigilEl = this._root.querySelector(".sigil");
    if (nameEl) nameEl.textContent = this.getAttribute("name") || "";
    if (sigilEl) sigilEl.textContent = this.getAttribute("sigil") || "";
    const color = this.getAttribute("color");
    if (color) this.style.setProperty("--card-accent", color);
    this._positionAtEdge();
  }

  _positionAtEdge() {
    const edge = this.getAttribute("home-edge") || "bottom";
    if (!EDGES.has(edge)) return;
    // Reset positional style so exactly one edge governs.
    this.style.top = this.style.bottom = this.style.left = this.style.right = "";
    switch (edge) {
      case "top":
        this.style.top = "1rem";
        this.style.left = "50%";
        this.style.transform = this._stateIsVisible() ? "translate(-50%, 0)" : "translate(-50%, -120%)";
        break;
      case "bottom":
        this.style.bottom = "1rem";
        this.style.left = "50%";
        this.style.transform = this._stateIsVisible() ? "translate(-50%, 0)" : "translate(-50%, 120%)";
        break;
      case "left":
        this.style.left = "1rem";
        this.style.top = "50%";
        this.style.transform = this._stateIsVisible() ? "translate(0, -50%)" : "translate(-120%, -50%)";
        break;
      case "right":
        this.style.right = "1rem";
        this.style.top = "50%";
        this.style.transform = this._stateIsVisible() ? "translate(0, -50%)" : "translate(120%, -50%)";
        break;
    }
  }

  _stateIsVisible() {
    const s = this.getAttribute("state");
    return s === "summoned" || s === "primary" || s === "secondary";
  }

  _applyState(oldVal, newVal) {
    const s = this.getAttribute("state") || "idle";
    if (!STATES.has(s)) {
      this.setAttribute("state", "idle");
      return;
    }
    this._paint();
    if (newVal === "summoned" || newVal === "primary") {
      this.dispatchEvent(new CustomEvent("summon", { bubbles: true, composed: true, detail: { state: newVal } }));
    } else if (newVal === "dismissed") {
      this.dispatchEvent(new CustomEvent("dismiss", { bubbles: true, composed: true }));
    }
  }

  _syncPersona() {
    const personaId = this.getAttribute("persona");
    if (!personaId) return;
    const root = this.getRootNode();
    const scope = root && root.getElementById ? root : document;
    const el = scope.getElementById(personaId) || document.getElementById(personaId);
    if (!el) return;
    const color = el.getAttribute("color");
    const sigil = el.getAttribute("sigil");
    if (color && !this.getAttribute("color")) this.setAttribute("color", color);
    if (sigil && !this.getAttribute("sigil")) this.setAttribute("sigil", sigil);
  }

  _onEsc(e) {
    if (e.key !== "Escape") return;
    if (!this._stateIsVisible()) return;
    this.dismiss();
  }

  _onDocClick(e) {
    if (!this._stateIsVisible()) return;
    // click-outside dismiss; ignore clicks within our own host.
    const path = e.composedPath ? e.composedPath() : [];
    if (path.includes(this)) return;
    this.dismiss();
  }

  _onCloseClick(e) {
    e.stopPropagation();
    this.dismiss();
  }
}

if (!customElements.get("grove-card")) {
  customElements.define("grove-card", GroveCard);
}

export { GroveCard };
