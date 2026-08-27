// b17: WGRV1 ΔΣ=42
/**
 * <grove-cast-chip> — compact persona-attribution chip for Willow's Grove cast.
 *
 * A chip renders one agent as {sigil + name}, colored from the unified persona
 * registry (D10). Consumers pass just the agent key; the chip resolves visual
 * fields (`visual.color`, `visual.sigil`) from a sibling <grove-persona-registry>
 * element the way <grove-card> resolves its <grove-persona> sibling — same
 * getRootNode() scope + document fallback, same "attributes-are-truth" contract.
 *
 * Attributes:
 *   agent  — the agent's key in the fleet-personas/v1 registry
 *            (e.g. "willow", "loki", "nestor"). Attribute-reactive:
 *            setAttribute("agent", "loki") re-renders in place.
 *
 * State reflection:
 *   data-unknown="true"  — set on the host when the registry has no row for
 *                          this agent; renders `?` sigil + raw agent string in
 *                          the pigeon color (#94a3b8) so CSS can hook the state.
 *
 * Events:
 *   cast-selected  — CustomEvent({detail: {agent}}) fired on host click.
 *                    Bubbles and composed so cast rows can listen once.
 *
 * Registry contract (per D10 — a single truth for persona visual/voice):
 *   The chip walks the DOM for the nearest <grove-persona-registry> sibling
 *   and reads one of:
 *     1. registry.getPersona(agent)     — preferred, when the registry
 *        becomes a real component with a method surface.
 *     2. registry.personas[agent]       — an object property populated by the
 *        registry element (fleet-personas/v1 shape).
 *     3. a <script type="application/json"> child holding the same shape,
 *        keyed by agent name — the shim the fixture harness uses today.
 *   The chip does NOT define <grove-persona-registry>; grove-card.js's
 *   contract owns it. This file is a pure consumer.
 *
 * Vanilla JS + Web Components, per D9. Zero dependencies.
 *
 * @element grove-cast-chip
 */

const OBSERVED = ["agent"];
const PIGEON = "#94a3b8";
const UNKNOWN_SIGIL = "?";

class GroveCastChip extends HTMLElement {
  static get observedAttributes() { return OBSERVED; }

  constructor() {
    super();
    this._root = this.attachShadow({ mode: "open" });
    this._onClick = this._onClick.bind(this);
    this._render();
  }

  connectedCallback() {
    this.addEventListener("click", this._onClick);
    this._paint();
  }

  disconnectedCallback() {
    this.removeEventListener("click", this._onClick);
  }

  attributeChangedCallback(name, oldVal, newVal) {
    if (oldVal === newVal) return;
    if (name === "agent") this._paint();
  }

  // ---- internals ----
  _render() {
    this._root.innerHTML = `
      <style>
        :host {
          display: inline-flex;
          align-items: center;
          gap: 0.35rem;
          padding: 2px 8px;
          background: #1a1409;
          color: var(--chip-color, ${PIGEON});
          border: 1px solid var(--chip-color, ${PIGEON});
          border-radius: 999px;
          font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
          font-size: 12px;
          line-height: 1.4;
          cursor: pointer;
          user-select: none;
          transition: filter 120ms ease-out;
        }
        :host(:hover) { filter: brightness(1.15); }
        :host(:focus-visible) { outline: 2px solid var(--chip-color, ${PIGEON}); outline-offset: 2px; }
        .sigil { font-weight: 600; }
        .name { color: inherit; }
        :host([data-unknown="true"]) .name { font-style: italic; }
      </style>
      <span class="sigil" part="sigil"></span><span class="name" part="name"></span>
    `;
    this._sigilEl = this._root.querySelector(".sigil");
    this._nameEl = this._root.querySelector(".name");
  }

  _paint() {
    const agent = this.getAttribute("agent") || "";
    const persona = this._resolvePersona(agent);
    if (persona && persona.visual && (persona.visual.color || persona.visual.sigil)) {
      const color = persona.visual.color || PIGEON;
      const sigil = persona.visual.sigil || UNKNOWN_SIGIL;
      this.style.setProperty("--chip-color", color);
      this._sigilEl.textContent = sigil;
      this._nameEl.textContent = agent;
      if (this.getAttribute("data-unknown") === "true") {
        this.removeAttribute("data-unknown");
      }
    } else {
      this.style.setProperty("--chip-color", PIGEON);
      this._sigilEl.textContent = UNKNOWN_SIGIL;
      this._nameEl.textContent = agent;
      if (this.getAttribute("data-unknown") !== "true") {
        this.setAttribute("data-unknown", "true");
      }
    }
  }

  _resolvePersona(agent) {
    if (!agent) return null;
    const registry = this._findRegistry();
    if (!registry) return null;
    // 1. Method surface — preferred once the registry is a real component.
    if (typeof registry.getPersona === "function") {
      try {
        const row = registry.getPersona(agent);
        if (row) return row;
      } catch (_) { /* fall through */ }
    }
    // 2. Property surface — populated by the registry element itself.
    if (registry.personas && typeof registry.personas === "object") {
      const row = registry.personas[agent];
      if (row) return row;
    }
    // 3. Inline <script type="application/json"> child — the fixture shim.
    const script = registry.querySelector('script[type="application/json"]');
    if (script && script.textContent) {
      try {
        const doc = JSON.parse(script.textContent);
        const rows = doc && doc.personas && typeof doc.personas === "object"
          ? doc.personas
          : doc;
        if (rows && typeof rows === "object") {
          const row = rows[agent];
          if (row) return row;
        }
      } catch (_) { /* malformed json — treat as miss */ }
    }
    return null;
  }

  _findRegistry() {
    const root = this.getRootNode();
    const scope = root && root.querySelector ? root : document;
    return scope.querySelector("grove-persona-registry")
        || document.querySelector("grove-persona-registry");
  }

  _onClick() {
    const agent = this.getAttribute("agent") || "";
    this.dispatchEvent(new CustomEvent("cast-selected", {
      bubbles: true, composed: true, detail: { agent },
    }));
  }
}

if (!customElements.get("grove-cast-chip")) {
  customElements.define("grove-cast-chip", GroveCastChip);
}

export { GroveCastChip };
