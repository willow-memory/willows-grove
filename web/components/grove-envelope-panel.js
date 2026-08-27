// b17: WGRV1 ΔΣ=42
/**
 * <grove-envelope-panel> — renders the Governance-lens envelope roster.
 *
 * Fetches an envelope registry (schema envelope-registry/v1.1) from
 * either `/api/envelopes` (default) or a local JSON path passed via the
 * `data-source` attribute (used by the fixture harness). Rows show
 * id, grantee, kind/mode, description, expiry countdown, and — where
 * `max_count` is defined — a meter of `used_count / max_count`. Each
 * row links out to its constitutional article (P1 evidence).
 *
 * P1 attestation states render distinctly:
 *   attested             — quiet checkmark.
 *   attestation_missing  — amber warning + inline "re-attest" button
 *                          which fires a `reattest` custom event with
 *                          the envelope id as detail.
 *   attestation_invalid  — red block glyph + refusal chip.
 *
 * Refuses to render partial state on fetch failure — shows a single
 * "registry unreachable" row instead. Vanilla JS + Web Components (D9).
 * Zero deps.
 */

const DEFAULT_SOURCE = "/api/envelopes";
const CONST_URL = "https://willow.local/const/";

const ATTEST_META = {
  attested:              { glyph: "✓", label: "attested",             tone: "ok" },
  attestation_missing:   { glyph: "!", label: "attestation missing",  tone: "warn" },
  attestation_invalid:   { glyph: "×", label: "attestation invalid",  tone: "err" },
};

class GroveEnvelopePanel extends HTMLElement {
  static get observedAttributes() { return ["data-source"]; }

  constructor() {
    super();
    this._root = this.attachShadow({ mode: "open" });
    this._envelopes = [];
    this._error = null;
    this._render();
  }

  connectedCallback() { this._load(); this._tickHandle = setInterval(() => this._paint(), 30000); }
  disconnectedCallback() { if (this._tickHandle) clearInterval(this._tickHandle); }

  attributeChangedCallback(name, oldVal, newVal) {
    if (name === "data-source" && oldVal !== newVal) this._load();
  }

  async _load() {
    const src = this.getAttribute("data-source") || DEFAULT_SOURCE;
    try {
      const res = await fetch(src, { headers: { accept: "application/json" } });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const doc = await res.json();
      if (!doc || doc.schema !== "envelope-registry/v1.1" || !Array.isArray(doc.pre_approved)) {
        throw new Error("unexpected schema");
      }
      this._envelopes = doc.pre_approved;
      this._error = null;
    } catch (err) {
      this._envelopes = [];
      this._error = String(err && err.message ? err.message : err);
    }
    this._paint();
  }

  _render() {
    this._root.innerHTML = `
      <style>
        :host { display: block; font: 13px/1.4 system-ui, sans-serif; color: var(--grove-fg, #1a2a1a); }
        table { width: 100%; border-collapse: collapse; }
        th, td { padding: 0.4rem 0.6rem; text-align: left; border-bottom: 1px solid rgba(0,0,0,0.06); vertical-align: top; }
        th { font-weight: 600; color: var(--grove-muted, #6a7a6a); background: rgba(111,170,106,0.08); }
        .id { font-family: ui-monospace, monospace; font-size: 12px; }
        .desc { color: var(--grove-muted, #6a7a6a); font-size: 12px; }
        .meter { background: rgba(0,0,0,0.08); height: 6px; border-radius: 3px; overflow: hidden; margin-top: 4px; min-width: 80px; }
        .meter > span { display: block; height: 100%; background: var(--grove-accent, #6faa6a); }
        .chip { display: inline-flex; align-items: center; gap: 0.25rem; padding: 0.1rem 0.4rem; border-radius: 3px; font-size: 12px; }
        .chip.ok   { background: rgba(111,170,106,0.15); color: #2f6a2a; }
        .chip.warn { background: rgba(224,168,64,0.18);  color: #7a4a08; }
        .chip.err  { background: rgba(200,80,80,0.18);   color: #7a1a1a; }
        button.reattest { all: unset; cursor: pointer; margin-left: 0.4rem; text-decoration: underline; color: #7a4a08; font-size: 12px; }
        .empty, .error { padding: 0.75rem; color: var(--grove-muted, #6a7a6a); font-style: italic; }
        .error { color: #7a1a1a; }
        a { color: inherit; text-decoration: none; border-bottom: 1px dotted currentColor; }
      </style>
      <div class="host"></div>
    `;
    this._host = this._root.querySelector(".host");
    this._host.addEventListener("click", (e) => {
      const btn = e.target.closest("button.reattest");
      if (!btn) return;
      const id = btn.dataset.envelope;
      this.dispatchEvent(new CustomEvent("reattest", {
        bubbles: true, composed: true, detail: { id },
      }));
    });
  }

  _paint() {
    if (this._error) {
      this._host.innerHTML = `<div class="error">envelope registry unreachable — ${this._escape(this._error)}</div>`;
      return;
    }
    if (!this._envelopes.length) {
      this._host.innerHTML = `<div class="empty">no envelopes currently registered.</div>`;
      return;
    }
    const rows = this._envelopes.map((e) => this._row(e)).join("");
    this._host.innerHTML = `
      <table>
        <thead>
          <tr>
            <th>envelope</th>
            <th>grantee</th>
            <th>scope</th>
            <th>expiry</th>
            <th>usage</th>
            <th>attestation</th>
          </tr>
        </thead>
        <tbody>${rows}</tbody>
      </table>
    `;
  }

  _row(env) {
    const attest = ATTEST_META[env.attestation] || ATTEST_META.attestation_missing;
    const countdown = this._expiryText(env.expires_at);
    const meter = this._meter(env);
    const constRef = env.constitutional_ref || "";
    const chip = `<span class="chip ${attest.tone}" title="${attest.label}">${attest.glyph} ${attest.label}</span>`;
    const reattest = env.attestation === "attestation_missing"
      ? `<button type="button" class="reattest" data-envelope="${this._escape(env.id)}">re-attest</button>`
      : "";
    const article = constRef
      ? `<a href="${CONST_URL}${this._escape(constRef)}" rel="noreferrer">${this._escape(constRef)}</a>`
      : "";
    return `
      <tr data-envelope="${this._escape(env.id)}">
        <td>
          <div class="id">${this._escape(env.id)}</div>
          <div class="desc">${this._escape(env.notes || "")} ${article}</div>
        </td>
        <td>${this._escape(env.grantee || "—")}</td>
        <td>${this._escape(env.kind || "")} · <code>${this._escape(env.mode || "")}</code></td>
        <td>${countdown}</td>
        <td>${meter}</td>
        <td>${chip}${reattest}</td>
      </tr>
    `;
  }

  _meter(env) {
    if (env.max_count == null) {
      return `<span class="desc">unmetered (${env.used_count ?? 0} used)</span>`;
    }
    const used = Number(env.used_count) || 0;
    const cap = Number(env.max_count) || 1;
    const pct = Math.max(0, Math.min(100, (used / cap) * 100));
    return `
      <div>${used} / ${cap}</div>
      <div class="meter" role="progressbar" aria-valuemin="0" aria-valuemax="${cap}" aria-valuenow="${used}">
        <span style="width:${pct.toFixed(1)}%"></span>
      </div>
    `;
  }

  _expiryText(expires) {
    if (expires == null) return `<span class="desc">no expiry</span>`;
    const then = Date.parse(expires);
    if (Number.isNaN(then)) return `<span class="desc">${this._escape(expires)}</span>`;
    const delta = then - Date.now();
    const days = Math.round(delta / 86400000);
    if (delta <= 0) return `<span class="chip err">expired ${(-days)}d ago</span>`;
    if (days <= 7) return `<span class="chip warn">in ${days}d</span>`;
    return `<span class="desc">in ${days}d</span>`;
  }

  _escape(s) {
    return String(s == null ? "" : s)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#39;");
  }
}

if (!customElements.get("grove-envelope-panel")) {
  customElements.define("grove-envelope-panel", GroveEnvelopePanel);
}

export { GroveEnvelopePanel };
