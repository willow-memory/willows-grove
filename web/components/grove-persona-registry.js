// b17: WGRV1 ΔΣ=42
/**
 * <grove-persona-registry> — the single source of truth for persona visual +
 * voice fields inside Willow's Grove served page.
 *
 * Three-state contract (see docs/INVARIANTS.md §1):
 *   populated   — registry.personas is a non-empty {agent: row} map.
 *   empty       — registry.personas is an empty map (fetched, no rows).
 *   unreachable — .state === "unreachable"; a `registry-unreachable` event
 *                 fires; getPersona() returns null for every agent.
 *
 * Consumers MUST check `.state === "unreachable"` (or listen for the
 * `registry-unreachable` event) rather than treating an empty map as
 * "everything is fine, there are no personas" — that's the pattern
 * INVARIANTS.md §2 supersedes.
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
 *   1. The inline `<script type="application/json">` child element is read
 *      ONLY when the element explicitly opts in via `data-source="_inline"`
 *      or a `data-fixture` attribute — the fixture / harness shim path is
 *      opt-in, never the default (INVARIANTS.md §8). Without one of those
 *      opt-in attributes, an inline shim present in the DOM is ignored.
 *   2. Otherwise, the `data-source` attribute, if present (and not the
 *      `"_inline"` sentinel), is fetched as the registry URL. Reloads
 *      whenever the attribute changes.
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
 *   data-source  — optional URL to fetch instead of the default
 *                  `/api/personas`. The literal value `"_inline"` opts into
 *                  the inline JSON shim (harness/fixture use only —
 *                  INVARIANTS.md §8) instead of naming a URL.
 *                  Attribute-reactive: setAttribute("data-source", ...)
 *                  triggers a fresh fetch and a new `registry-loaded` event.
 *   data-fixture — optional boolean-style attribute (presence only) that
 *                  also opts into the inline JSON shim, for harness pages
 *                  that prefer an explicit fixture-mode flag over
 *                  overloading `data-source`.
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
    /** @type {"populated"|"empty"|"unreachable"|"loading"} */
    this.state = "loading";
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

    // 1. The inline shim is opt-in only (INVARIANTS.md §8): it is read
    //    ONLY when the element explicitly asked for it via
    //    data-source="_inline" or a data-fixture attribute. Absent that
    //    opt-in, an inline shim present in the DOM (e.g. leftover harness
    //    markup) MUST NOT shadow the live endpoint.
    const dataSource = this.getAttribute("data-source");
    const fixtureOptIn = dataSource === "_inline" || this.hasAttribute("data-fixture");
    if (fixtureOptIn) {
      const inline = this._readInlineShim();
      if (inline !== null) {
        this._settle(inline, token);
        return;
      }
    }

    // 2. Otherwise fetch `data-source` if present (and not the `_inline`
    //    sentinel), else the default live endpoint.
    const source = (dataSource && dataSource !== "_inline") ? dataSource : DEFAULT_SOURCE;
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
      this._logOnce("fetch() is not available — registry is unreachable");
      this._settleUnreachable("fetch() unavailable", token);
      return;
    }
    fetch(url, { credentials: "same-origin" })
      .then((resp) => {
        if (!resp.ok) {
          // 503 body carries {state: "unreachable", reason: ...} per
          // INVARIANTS.md §1. Read it before we throw so the reason
          // reaches the operator via the log-once + event.
          return resp.json().then((body) => {
            throw Object.assign(new Error(`HTTP ${resp.status}`), {
              status: resp.status, body,
            });
          }, () => {
            throw new Error(`HTTP ${resp.status}`);
          });
        }
        return resp.json();
      })
      .then((doc) => this._settle(doc, token))
      .catch((err) => {
        const reason = (err && err.body && err.body.reason)
          || (err && err.message)
          || String(err);
        this._logOnce(`fetch ${url} failed: ${reason}`);
        this._settleUnreachable(reason, token);
      });
  }

  _settle(doc, token) {
    if (token !== this._loadToken) return; // superseded by a newer reload
    // INVARIANTS.md §1: a 200 body may itself carry state="unreachable"
    // if the endpoint added it — we don't produce that shape, but tolerate.
    if (doc && doc.state === "unreachable") {
      this._settleUnreachable(doc.reason || "endpoint reported unreachable", token);
      return;
    }
    this.personas = this._normalize(doc);
    this._loaded = true;
    this.state = Object.keys(this.personas).length > 0 ? "populated" : "empty";
    this.dispatchEvent(new CustomEvent("registry-loaded", {
      bubbles: true, composed: true,
      detail: { count: Object.keys(this.personas).length, state: this.state },
    }));
  }

  _settleUnreachable(reason, token) {
    if (token !== this._loadToken) return;
    // Distinct from "empty" — an unreachable registry MUST render distinctly
    // per INVARIANTS.md §1. Consumers check `.state === "unreachable"`
    // and/or listen for the `registry-unreachable` event.
    this.personas = Object.create(null);
    this._loaded = true;
    this.state = "unreachable";
    this.dispatchEvent(new CustomEvent("registry-unreachable", {
      bubbles: true, composed: true,
      detail: { reason: String(reason || "unreachable") },
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

    // Shape C: bare agent → row map, OR the charter shape from the on-disk
    // fleet_personas.json — every top-level key that isn't `_meta` / `schema`
    // is an agent row (`{_meta:{schema:"fleet-personas/v1"}, willow:{...},
    // heimdallr:{...}, ...}`). Meta keys are skipped so the registry does not
    // accidentally treat them as personas.
    const META_KEYS = new Set(["_meta", "schema", "agents", "personas", "state", "reason"]);
    for (const [key, row] of Object.entries(doc)) {
      if (META_KEYS.has(key)) continue;
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
