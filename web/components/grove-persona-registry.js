// b17: WGRV1 ΔΣ=42
/**
 * <grove-persona-registry> — the single source of truth for persona visual +
 * voice fields inside Willow's Grove served page.
 *
 * D10 (premise) mandates one unified persona registry (`fleet-personas/v1`);
 * every cast chip, card, and refusal chip resolves its `visual.color`,
 * `visual.sigil`, and `voice.*` against the same store. This element is the
 * front-end reflection of that store — it fetches the registry once at
 * connect time and exposes it as a data element to sibling components in the
 * same DOM scope. V6 (visual — sigil + color + name) is what the consumers
 * render; D9 (vanilla JS + Web Components, no build step) is the shape.
 *
 * Data sources (probed in this order):
 *
 *   1. The `data-source` attribute, if present, is fetched as the registry
 *      URL. Reloads whenever the attribute changes.
 *   2. Otherwise, an inline `<script type="application/json">` child element
 *      is parsed — the fixture / harness shim path the earlier Web Components
 *      already tolerated.
 *   3. Otherwise, `/api/personas` is fetched — the default backed by
 *      `grove_serve.py`'s route over the `PersonaRoster` reader.
 *
 * The registry accepts both the `fleet-personas/v1` document shape
 * (`{schema, agents:[{agent, ...}, ...]}` or `{schema, personas:{agent:{...}}}`)
 * and a bare agent-keyed object (`{willow:{...}, loki:{...}}`). Rows are
 * normalized into an `agent` → row map keyed by the row's `agent` / `name` /
 * `id` field so `getPersona("willow")` works regardless of the incoming shape.
 *
 * Public surface:
 *
 *   - `getPersona(agent)` — returns the row for `agent`, or `null` on miss.
 *     Consumers (grove-card, grove-cast-chip) call this first.
 *   - `personas` — property whose value is the agent → row map. The same
 *     consumers fall through to this if the method surface is absent.
 *   - `registry-loaded` CustomEvent — fired once the registry is populated
 *     (or, on failure, once it settles into an empty state). Bubbles + composed
 *     so a listener bound on `<body>` catches it.
 *
 * Rendering:
 *   The element renders nothing (it is a data element). Shadow-root CSS pins
 *   `:host { display: none }` so the element takes no layout space — but the
 *   custom-element definition still gets attribute-reactivity + a shadow root
 *   for encapsulation.
 *
 * Failure discipline:
 *   A failed fetch (network error, 404, malformed JSON) is logged **once** via
 *   `console.info("[grove-persona-registry]", ...)` — never `console.error`,
 *   never a thrown exception — and the registry settles into an empty state.
 *   Every consumer already treats a missing row as "unknown persona" (pigeon
 *   color + `?` sigil), so the page remains functional without the sidecar
 *   registry file on disk. This matches D7 (`absence is a state, not a
 *   failure`) on the Python side.
 *
 * Attributes:
 *   data-source — optional URL to fetch instead of the default `/api/personas`.
 *                 Attribute-reactive: setAttribute("data-source", ...) triggers
 *                 a fresh fetch and a new `registry-loaded` event.
 *
 * @element grove-persona-registry
 */

const OBSERVED = ["data-source"];
const DEFAULT_SOURCE = "/api/personas";

let _loggedFailure = false;

class GrovePersonaRegistry extends HTMLElement {
  static get observedAttributes() { return OBSERVED; }

  constructor() {
    super();
    this._root = this.attachShadow({ mode: "open" });
    this._root.innerHTML = `<style>:host { display: none; }</style>`;
    /** @type {Object<string, object>} */
    this.personas = Object.create(null);
    this._loaded = false;
    this._loadToken = 0;
  }

  connectedCallback() {
    this._reload();
  }

  attributeChangedCallback(name, oldVal, newVal) {
    if (oldVal === newVal) return;
    if (!this.isConnected) return;
    if (name === "data-source") this._reload();
  }

  // ---- public API ----
  /**
   * Return the persona row for `agent`, or `null` if not present.
   * @param {string} agent
   * @returns {object|null}
   */
  getPersona(agent) {
    if (!agent) return null;
    const row = this.personas[agent];
    return row || null;
  }

  // ---- internals ----
  _reload() {
    // Bump the token so any in-flight load from a prior data-source resolves
    // into a no-op (last-writer-wins on rapid attribute changes).
    const token = ++this._loadToken;

    // 1. Inline shim wins over the default fetch — the fixture path.
    const inline = this._readInlineShim();
    if (inline !== null) {
      this._settle(inline, token);
      return;
    }

    // 2. Otherwise fetch `data-source` if present, else the default.
    const source = this.getAttribute("data-source") || DEFAULT_SOURCE;
    this._fetch(source, token);
  }

  _readInlineShim() {
    const script = this.querySelector('script[type="application/json"]');
    if (!script || !script.textContent) return null;
    try {
      return JSON.parse(script.textContent);
    } catch (_) {
      // Malformed inline shim — degrade to empty, same as a failed fetch.
      this._logOnce("inline JSON shim did not parse — using empty registry");
      return {};
    }
  }

  _fetch(url, token) {
    // fetch is not available in some very old sandboxes; guard anyway.
    if (typeof fetch !== "function") {
      this._logOnce("fetch() is not available — using empty registry");
      this._settle({}, token);
      return;
    }
    fetch(url, { credentials: "same-origin" })
      .then((resp) => {
        if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
        return resp.json();
      })
      .then((doc) => this._settle(doc, token))
      .catch((err) => {
        this._logOnce(`fetch ${url} failed: ${err && err.message ? err.message : err}`);
        this._settle({}, token);
      });
  }

  _settle(doc, token) {
    if (token !== this._loadToken) return; // superseded by a newer reload
    this.personas = this._normalize(doc);
    this._loaded = true;
    this.dispatchEvent(new CustomEvent("registry-loaded", {
      bubbles: true, composed: true,
      detail: { count: Object.keys(this.personas).length },
    }));
  }

  /**
   * Turn any of the accepted shapes into a flat {agent: row} map.
   *  - `{schema, agents: [ {agent, ...}, ... ]}` → keyed by `agent` / `name` / `id`
   *  - `{schema, personas: {agent: row, ...}}`   → passed through
   *  - `{agent: row, ...}`                       → passed through
   * @param {any} doc
   * @returns {Object<string, object>}
   */
  _normalize(doc) {
    const out = Object.create(null);
    if (!doc || typeof doc !== "object") return out;

    // Shape A: `agents` list — the canonical fleet-personas/v1 shape.
    if (Array.isArray(doc.agents)) {
      for (const row of doc.agents) {
        if (!row || typeof row !== "object") continue;
        const key = (typeof row.agent === "string" && row.agent)
          || (typeof row.name === "string" && row.name)
          || (typeof row.id === "string" && row.id)
          || null;
        if (key) out[key] = row;
      }
      return out;
    }

    // Shape B: envelope with a `personas` object.
    if (doc.personas && typeof doc.personas === "object" && !Array.isArray(doc.personas)) {
      for (const [key, row] of Object.entries(doc.personas)) {
        if (row && typeof row === "object") out[key] = row;
      }
      return out;
    }

    // Shape C: bare agent → row map. Skip meta keys (`schema` etc).
    for (const [key, row] of Object.entries(doc)) {
      if (row && typeof row === "object" && !Array.isArray(row)) {
        out[key] = row;
      }
    }
    return out;
  }

  _logOnce(msg) {
    if (_loggedFailure) return;
    _loggedFailure = true;
    // Info-level, never error — this is a soft degradation per the module docs.
    // eslint-disable-next-line no-console
    console.info("[grove-persona-registry]", msg);
  }
}

if (!customElements.get("grove-persona-registry")) {
  customElements.define("grove-persona-registry", GrovePersonaRegistry);
}

export { GrovePersonaRegistry };
