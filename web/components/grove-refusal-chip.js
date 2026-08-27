/**
 * <grove-refusal-chip> — verbatim Nestor refusal renderer (V5).
 *
 * Renders a compact chip that carries a persona's refusal speech act
 * exactly as the persona emitted it. Payload is produced upstream by
 * `grove/nestor_client.py::NestorClient.refusal(act, **facts)` and
 * shaped as:
 *
 *   {
 *     persona: "nestor",              // persona id (looked up in a
 *                                     //   sibling <grove-persona-registry>
 *                                     //   for sigil + color)
 *     act: "durable_rejection",       // speech-act name
 *     body: "<verbatim text>",        // the speech act itself — this
 *                                     //   string is rendered via
 *                                     //   textContent only, never
 *                                     //   paraphrased, never truncated,
 *                                     //   never ellipsised (V5)
 *     warrant_ids: ["..."],           // optional; opaque strings
 *     evidence_ids: ["..."],          // optional; opaque strings
 *     seal_sig: "..."                 // optional; opaque signature
 *   }
 *
 * @element grove-refusal-chip
 *
 * Consumption:
 *   Set the JSON `payload` attribute or assign the parsed object to the
 *   `data` property. When the payload is missing, malformed, or its
 *   `body` is empty, the chip renders nothing (no placeholder).
 *
 * Events:
 *   refusal-expanded — CustomEvent<{persona, act}>, bubbles + composed,
 *   fired when the chip is clicked to toggle the verbatim body panel.
 *
 * V5 discipline (docs/design/willow-grove-premise.md — D11 evidence
 * clause, "V5 — Nestor's refusal must render verbatim with negation
 * preserved"):
 *   - `body` is written via `textContent`, never `innerHTML`.
 *   - No truncation, no ellipsis, no reflow.
 *   - No editorial framing around the body: the chip surrounds it with
 *     its own vocabulary (persona sigil + act name) but the body itself
 *     is untouched.
 *
 * Vanilla JS + Web Component. Zero dependencies. Per D9 (no build step).
 */

const PIGEON = "#94a3b8";
const FALLBACK_SIGIL = { nestor: "¬" };
const REGISTRY_TAG = "grove-persona-registry";

class GroveRefusalChip extends HTMLElement {
  static get observedAttributes() { return ["payload"]; }

  constructor() {
    super();
    this._root = this.attachShadow({ mode: "open" });
    this._data = null;
    this._expanded = false;
    this._render();
  }

  connectedCallback() {
    if (this._data === null && this.hasAttribute("payload")) {
      this._ingestAttribute(this.getAttribute("payload"));
    }
    this._paint();
  }

  attributeChangedCallback(name, oldVal, newVal) {
    if (name === "payload" && oldVal !== newVal) {
      this._ingestAttribute(newVal);
      this._paint();
    }
  }

  // ---- public property ----
  get data() { return this._data; }
  set data(value) {
    this._data = this._normalize(value);
    this._paint();
  }

  // ---- internals ----
  _ingestAttribute(raw) {
    if (raw == null || raw === "") { this._data = null; return; }
    try {
      const parsed = JSON.parse(raw);
      this._data = this._normalize(parsed);
    } catch (_err) {
      // Malformed payload: render nothing rather than a placeholder.
      this._data = null;
    }
  }

  _normalize(value) {
    if (!value || typeof value !== "object") return null;
    const body = typeof value.body === "string" ? value.body : "";
    if (!body) return null;
    // INVARIANTS.md §1: mode="unreachable" is the L4-seam-down variant;
    // the chip renders it subdued and distinct from a real refusal so
    // the operator can tell "Nestor refused" apart from "could not
    // reach Nestor". Every other value falls to "refusal" (default).
    const mode = value.mode === "unreachable" ? "unreachable" : "refusal";
    return {
      persona: typeof value.persona === "string" ? value.persona : "",
      act: typeof value.act === "string" ? value.act : "",
      body: body,
      mode: mode,
      warrant_ids: Array.isArray(value.warrant_ids) ? value.warrant_ids.slice() : [],
      evidence_ids: Array.isArray(value.evidence_ids) ? value.evidence_ids.slice() : [],
      seal_sig: typeof value.seal_sig === "string" ? value.seal_sig : "",
    };
  }

  _lookupPersona(personaId) {
    if (!personaId) return { sigil: "", color: "" };
    const root = this.getRootNode();
    const scopes = [];
    if (root && root !== document) scopes.push(root);
    scopes.push(document);
    for (const scope of scopes) {
      const registries = scope.querySelectorAll ? scope.querySelectorAll(REGISTRY_TAG) : [];
      for (const reg of registries) {
        // Property-based lookup (preferred).
        if (typeof reg.lookup === "function") {
          try {
            const found = reg.lookup(personaId);
            if (found && (found.sigil || found.color)) {
              return {
                sigil: found.sigil || "",
                color: found.color || "",
              };
            }
          } catch (_err) { /* fall through */ }
        }
        // Attribute-based lookup: <grove-persona id="nestor" sigil="¬" color="#..."/>
        const el = reg.querySelector ? reg.querySelector(`#${CSS.escape(personaId)}`) : null;
        if (el) {
          return {
            sigil: el.getAttribute("sigil") || "",
            color: el.getAttribute("color") || "",
          };
        }
      }
    }
    return { sigil: FALLBACK_SIGIL[personaId] || "", color: "" };
  }

  _render() {
    this._root.innerHTML = `
      <style>
        :host {
          display: inline-block;
          font: 12px/1.4 ui-monospace, SFMono-Regular, Menlo, monospace;
          color: var(--grove-warm-fg, #e8ddc4);
          --chip-border: ${PIGEON};
        }
        :host([hidden]), :host(.empty) { display: none; }
        .chip {
          display: inline-flex;
          align-items: center;
          gap: 0.4rem;
          padding: 0.2rem 0.55rem;
          background: #1a1409;
          border: 1px solid var(--chip-border);
          border-radius: 4px;
          cursor: pointer;
          user-select: none;
          max-width: 100%;
          box-sizing: border-box;
        }
        .chip:hover { filter: brightness(1.1); }
        .chip:focus-visible { outline: 2px solid var(--chip-border); outline-offset: 2px; }
        /* INVARIANTS.md §1: unreachable mode is visually distinct from
           a real refusal — dashed border + subdued opacity so the
           operator reads "seam down" and not "Nestor refused". */
        .chip.mode-unreachable {
          border-style: dashed;
          opacity: 0.78;
          background: #14100a;
        }
        .chip.mode-unreachable .act { color: var(--grove-warm-muted, #8a7d5f); font-weight: 500; }
        .sigil {
          font-size: 13px;
          color: var(--chip-border);
          line-height: 1;
        }
        .act {
          font-weight: 600;
          letter-spacing: 0.02em;
        }
        .hint {
          color: var(--grove-warm-muted, #8a7d5f);
          font-size: 11px;
        }
        .body {
          margin-top: 0.4rem;
          padding: 0.6rem 0.75rem;
          background: #1a1409;
          border: 1px solid var(--chip-border);
          border-radius: 4px;
          white-space: pre-wrap;
          word-break: normal;
          overflow-wrap: anywhere;
          font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
          font-size: 12px;
          line-height: 1.5;
          color: var(--grove-warm-fg, #e8ddc4);
        }
        .body[hidden] { display: none; }
        .meta {
          margin-top: 0.35rem;
          color: var(--grove-warm-muted, #8a7d5f);
          font-size: 11px;
        }
        .meta code { font-family: inherit; }
      </style>
      <button class="chip" type="button" part="chip" aria-expanded="false">
        <span class="sigil" part="sigil"></span>
        <span class="act" part="act"></span>
        <span class="hint" part="hint"></span>
      </button>
      <div class="body" part="body" hidden></div>
    `;
    this._chip = this._root.querySelector(".chip");
    this._sigil = this._root.querySelector(".sigil");
    this._act = this._root.querySelector(".act");
    this._hint = this._root.querySelector(".hint");
    this._body = this._root.querySelector(".body");
    this._chip.addEventListener("click", (e) => this._onClick(e));
  }

  _paint() {
    if (!this._data) {
      // Renders nothing when the payload is absent or empty.
      this.classList.add("empty");
      this._chip.setAttribute("hidden", "");
      this._body.setAttribute("hidden", "");
      return;
    }
    this.classList.remove("empty");
    this._chip.removeAttribute("hidden");
    // Toggle the visual distinction between refusal and unreachable
    // (INVARIANTS.md §1) so the operator reads the two states apart.
    if (this._data.mode === "unreachable") {
      this._chip.classList.add("mode-unreachable");
    } else {
      this._chip.classList.remove("mode-unreachable");
    }

    const persona = this._lookupPersona(this._data.persona);
    const color = persona.color || PIGEON;
    this.style.setProperty("--chip-border", color);

    // textContent everywhere — never innerHTML for persona data.
    this._sigil.textContent = persona.sigil || FALLBACK_SIGIL[this._data.persona] || "";
    this._act.textContent = this._data.act || "refusal";
    this._hint.textContent = this._expanded ? "hide" : "expand";

    // V5: body is written via textContent — verbatim, no reflow.
    this._body.textContent = this._data.body;
    if (this._expanded) {
      this._body.removeAttribute("hidden");
      this._chip.setAttribute("aria-expanded", "true");
    } else {
      this._body.setAttribute("hidden", "");
      this._chip.setAttribute("aria-expanded", "false");
    }
  }

  _onClick(e) {
    e.preventDefault();
    e.stopPropagation();
    this._expanded = !this._expanded;
    this._paint();
    this.dispatchEvent(new CustomEvent("refusal-expanded", {
      bubbles: true,
      composed: true,
      detail: {
        persona: this._data ? this._data.persona : "",
        act: this._data ? this._data.act : "",
        expanded: this._expanded,
      },
    }));
  }
}

if (!customElements.get("grove-refusal-chip")) {
  customElements.define("grove-refusal-chip", GroveRefusalChip);
}

export { GroveRefusalChip };
