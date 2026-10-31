// b17: WGRV1 ΔΣ=42
/**
 * <grove-human-required> — what waits on the human, from the live queue.
 *
 * The queue is willow-mcp's (where the steward, the desk, Loki and the rest
 * file with human_required_enqueue), read through /api/human_required. Items
 * are grouped by priority (urgent, high, normal, low), newest first in each;
 * a row shows its title, who filed it and how long ago, and opens to its
 * summary.
 *
 * Three-state contract (docs/INVARIANTS.md §1):
 *   populated   — open items; grouped table renders, the count in the head.
 *   empty       — willow-mcp answered and nothing is open: "nothing waits on
 *                 you", muted.
 *   unreachable — 503 / fetch failure / willow-mcp refused: the amber banner
 *                 with willow-mcp's own reason (e.g. the willow-grove app
 *                 lacking human_loop_read). MUST look different from empty:
 *                 a queue that couldn't be read is never "nothing waits".
 *
 * Live-endpoint default (INVARIANTS.md §8): `/api/human_required`;
 * `data-source` is the fixture harness's override only. Refreshes every
 * minute. Read-only: resolving an item is the human's, elsewhere.
 *
 * Vanilla JS + Web Components (D9). Zero deps.
 */

import { EMPTY, POPULATED, UNREACHABLE } from "../lib/states.js";

const DEFAULT_SOURCE = "/api/human_required";
const ORDER = ["urgent", "high", "normal", "low"];

class GroveHumanRequired extends HTMLElement {
  static get observedAttributes() { return ["data-source"]; }

  constructor() {
    super();
    this._root = this.attachShadow({ mode: "open" });
    this._items = [];
    this._open = 0;
    /** @type {"populated"|"empty"|"unreachable"|null} */
    this._state = null;
    this._error = null;
    this._render();
  }

  connectedCallback() { this._load(); this._tick = setInterval(() => this._load(), 60000); }
  disconnectedCallback() { if (this._tick) clearInterval(this._tick); }

  attributeChangedCallback(name, oldVal, newVal) {
    if (name === "data-source" && oldVal !== newVal) this._load();
  }

  _unreachable(reason) {
    this._items = [];
    this._state = UNREACHABLE;
    this._error = reason;
    this._paint();
  }

  async _load() {
    const src = this.getAttribute("data-source") || DEFAULT_SOURCE;
    let res;
    try {
      res = await fetch(src, { headers: { accept: "application/json" } });
    } catch (err) {
      return this._unreachable(String(err && err.message ? err.message : err));
    }
    let doc = null;
    try { doc = await res.json(); } catch (_) { /* handled below */ }
    if (!res.ok || !doc || doc.state === UNREACHABLE) {
      return this._unreachable((doc && doc.reason) || `HTTP ${res.status}`);
    }
    if (!Array.isArray(doc.items)) return this._unreachable("unexpected response shape");
    this._items = doc.items;
    // willow-mcp's own count: the page holds the first `limit`, most urgent
    // first, and a long queue must not read as the length of the page.
    this._open = Number.isInteger(doc.open) && doc.open >= doc.items.length ? doc.open : doc.items.length;
    this._state = doc.items.length ? POPULATED : EMPTY;
    this._error = null;
    this._paint();
  }

  _render() {
    this._root.innerHTML = `
      <style>
        :host { display: block; font: 13px/1.4 system-ui, sans-serif; color: var(--grove-fg, #1a2a1a); }
        h3 { font-size: 13px; margin: 0 0 0.4rem; font-weight: 600; }
        h4 { font-size: 12px; margin: 0.6rem 0 0.2rem; text-transform: uppercase; letter-spacing: 0.04em; color: var(--grove-muted, #6a7a6a); }
        h4.urgent { color: #7a1a1a; } h4.high { color: #7a4a08; }
        details { border-bottom: 1px solid rgba(0,0,0,0.06); padding: 0.3rem 0.2rem; }
        summary { cursor: pointer; list-style: none; display: flex; gap: 0.6rem; align-items: baseline; }
        summary::-webkit-details-marker { display: none; }
        .title { flex: 1; }
        .who, .age { color: var(--grove-muted, #6a7a6a); font-size: 12px; white-space: nowrap; }
        .summary { margin: 0.3rem 0 0.2rem 0.4rem; white-space: pre-wrap; color: var(--grove-fg, #1a2a1a); font-size: 12px; }
        .ref { font-family: ui-monospace, monospace; font-size: 11px; color: var(--grove-muted, #6a7a6a); }
        .empty, .unreachable { padding: 0.75rem; font-style: italic; }
        .empty { color: var(--grove-muted, #6a7a6a); }
        .unreachable { color: #7a4a08; background: rgba(224,168,64,0.15); border: 1px solid rgba(224,168,64,0.35); border-radius: 4px; }
        .unreachable .reason { color: #6a4a0a; font-size: 11px; margin-top: 2px; font-style: normal; }
      </style>
      <div class="host"></div>
    `;
    this._host = this._root.querySelector(".host");
  }

  _paint() {
    if (this._state === UNREACHABLE) {
      this._host.innerHTML = `<div class="unreachable" part="unreachable">
        the human-required queue could not be read
        <div class="reason">${this._escape(this._error || "unreachable")}</div>
      </div>`;
      return;
    }
    if (!this._items.length) {
      this._host.innerHTML = `<div class="empty" part="empty">nothing waits on you.</div>`;
      return;
    }
    const groups = ORDER.map((p) => [p, this._items.filter((i) => (i.priority || "normal") === p)])
      .concat([["other", this._items.filter((i) => !ORDER.includes(i.priority || "normal"))]])
      .filter(([, list]) => list.length);
    const open = this._open || this._items.length;
    const part = open > this._items.length
      ? ` <span class="who">· the ${this._items.length} most urgent shown</span>` : "";
    this._host.innerHTML = `<h3>${open} wait${open === 1 ? "s" : ""} on you${part}</h3>` +
      groups.map(([p, list]) => `<h4 class="${p}">${p} · ${list.length}</h4>${list.map((i) => this._row(i)).join("")}`).join("");
  }

  _row(item) {
    return `
      <details data-item="${this._escape(item.id)}">
        <summary>
          <span class="title">${this._escape(item.title)}</span>
          <span class="who">${this._escape(item.source_agent || "")}</span>
          <span class="age">${this._age(item.created_at)}</span>
        </summary>
        <div class="summary">${this._escape(item.summary || "")}</div>
        <div class="ref">${this._escape(item.kind || "")} · ${this._escape(item.source_ref || "")} · ${this._escape(item.id)}</div>
      </details>
    `;
  }

  _age(when) {
    const then = Date.parse(when);
    if (Number.isNaN(then)) return "";
    const mins = Math.max(0, Math.round((Date.now() - then) / 60000));
    if (mins < 60) return `${mins}m`;
    if (mins < 2880) return `${Math.round(mins / 60)}h`;
    return `${Math.round(mins / 1440)}d`;
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

if (!customElements.get("grove-human-required")) {
  customElements.define("grove-human-required", GroveHumanRequired);
}
