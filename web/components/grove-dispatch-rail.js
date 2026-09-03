// b17: WGRV1 ΔΣ=42
/**
 * <grove-dispatch-rail> — the Kart escalation surface on the operator seat.
 *
 * Three-state contract (see docs/INVARIANTS.md §1):
 *   populated   — one or more tasks in the queue; rows render.
 *   empty       — queue reached, no queued rows; "quiet queue ❦" line in
 *                 muted default color.
 *   unreachable — 503/fetch failure; a distinct muted-red banner reads
 *                 "queue source not reachable" with a red left border.
 *                 MUST be visually distinct from the empty state (which
 *                 is the plant sigil in muted color).
 *
 *
 * The autonomous-continuity doc (docs/design/autonomous-continuity.md,
 * C6-C8) names Kart as the seam every small-to-big handoff crosses: an
 * agent that hits its authority ceiling files a task with the
 * `authority_needed` it needs from a larger tier, and the operator (v1,
 * no auto-drain) picks the drain-tier from *this rail*. Optional `lens`
 * may still narrow the queue for quiet tooling; the operator-facing
 * Governance/PM/PA gearshift is demoted (C12 misfit / Jarvis addendum).
 * D12 says the rail is a summonable card — mounted at the home edge,
 * narrow, and evictable — not a permanent panel.
 *
 * Attributes:
 *   lens — optional quiet filter: "governance" | "pm" | "pa". Unset /
 *          empty / junk → unfiltered queue. Reactive:
 *          setAttribute("lens", "governance") re-fetches and re-renders.
 *
 * Data source:
 *   GET /api/dispatch or GET /api/dispatch?lens=<lens> — served by
 *   grove_serve.py, backed by grove/kart_reader.py. Returns a JSON array
 *   of task-row objects. Missing / unreachable → a single "dispatch
 *   unreachable" row + a 30 s retry.
 *
 * Rendering:
 *   Each row is:
 *     [cast-chip origin] [authority pill L1..L4] [urgency dot]
 *     [proposed_action, truncated to 80 chars] [→]
 *   An empty queue renders a subdued line with the plant sigil ❦ —
 *   "quiet queue" is a real state (D7), not a bug to hide.
 *
 * Events:
 *   dispatch-clicked — CustomEvent({detail: {task}}) fired on host when
 *                      the → end-caret is clicked. Bubbles + composed
 *                      so a page-level listener (the future model-tier
 *                      selector, C8) can pick it up once.
 *
 * Refresh:
 *   Every 30 s while connected. setInterval scheduled in
 *   connectedCallback, cleared in disconnectedCallback.
 *
 * Persona resolution:
 *   `origin` is passed through to <grove-cast-chip agent="..."> which
 *   resolves colour + sigil from a sibling <grove-persona-registry>
 *   per the D10 registry contract. This file does NOT import cast-chip
 *   or the registry — it uses them by tag name at render time, so this
 *   module stays pure vanilla + zero imports per D9.
 *
 * @element grove-dispatch-rail
 */

const OBSERVED = ["lens"];
const REFRESH_MS = 30_000;
const MAX_ACTION_CHARS = 80;
const QUIET_SIGIL = "❦"; // ❦

// Small palette matching grove_html.py — the dark warm desk, not a cold
// monitor. Kept in-shadow so cast-chip's own dark background sits flat.
const CSS = `
  :host {
    display: block;
    box-sizing: border-box;
    padding: 0.5rem 0.6rem;
    background: #1a140f;
    color: #efe6d8;
    border-left: 1px solid #3a2c1f;
    font: 12px/1.45 ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
    min-width: 260px;
    max-width: 360px;
  }
  header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 0.4rem;
    padding-bottom: 0.4rem;
    margin-bottom: 0.4rem;
    border-bottom: 1px solid #3a2c1f;
    color: #a3927a;
    letter-spacing: 0.04em;
    text-transform: lowercase;
  }
  header .lens {
    color: #d4a373;
    font-weight: 600;
  }
  ul.rows {
    list-style: none;
    margin: 0;
    padding: 0;
    display: flex;
    flex-direction: column;
    gap: 0.35rem;
  }
  li.row {
    display: grid;
    grid-template-columns: auto auto auto 1fr auto;
    align-items: center;
    gap: 0.4rem;
    padding: 0.3rem 0.35rem;
    background: #241a12;
    border: 1px solid #3a2c1f;
    border-radius: 4px;
  }
  li.row .authority {
    display: inline-block;
    padding: 1px 6px;
    border-radius: 3px;
    font-size: 10px;
    font-weight: 600;
    letter-spacing: 0.05em;
    background: #3a2c1f;
    color: #efe6d8;
    border: 1px solid #4a3a2a;
  }
  li.row .authority[data-tier="L1"] { color: #a8d18a; border-color: #4a5f3a; }
  li.row .authority[data-tier="L2"] { color: #d4a373; border-color: #5a4a2a; }
  li.row .authority[data-tier="L3"] { color: #d47373; border-color: #5a2f2a; }
  li.row .authority[data-tier="L4"] { color: #c9a074; border-color: #7a5a3a; background: #2a1f14; }
  li.row .urgency {
    width: 7px;
    height: 7px;
    border-radius: 50%;
    background: #a3927a;
    flex-shrink: 0;
  }
  li.row .urgency[data-level="operator-blocking"] {
    background: #d47373;
    box-shadow: 0 0 5px #d47373;
  }
  li.row .urgency[data-level="operator-visible"] {
    background: #d4a373;
    box-shadow: 0 0 4px #d4a373;
  }
  li.row .action {
    color: #efe6d8;
    font-size: 11px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    /* docs/design/phone-surface-context.md §13: the legibility budget is
       characters, not pixels. Without a floor here, the ellipsis clips
       wherever the grid's 1fr column happens to land -- measured at ~22
       visible chars at this component's own declared 260px min-width,
       below the 28-char rule. min-width forces the row (and, if needed,
       the host) to make room instead of silently dropping the budget. */
    min-width: 28ch;
  }
  li.row .caret {
    color: #d4a373;
    cursor: pointer;
    padding: 0 4px;
    user-select: none;
    font-weight: 600;
    transition: filter 120ms ease-out;
  }
  li.row .caret:hover { filter: brightness(1.4); }
  li.row .caret:focus-visible {
    outline: 2px solid #d4a373;
    outline-offset: 2px;
    border-radius: 2px;
  }
  .quiet {
    color: #a3927a;
    font-style: italic;
    padding: 0.4rem 0.3rem;
    display: flex;
    align-items: center;
    gap: 0.4rem;
  }
  .quiet .sigil {
    color: #7fb069;
    font-style: normal;
  }
  /* INVARIANTS.md §1: unreachable MUST render distinctly from empty. */
  .unreachable {
    color: #f0a3a3;
    padding: 0.4rem 0.5rem;
    font-style: italic;
    background: #2a1414;
    border-left: 3px solid #d47373;
    border-radius: 3px;
  }
  .unreachable .reason {
    color: #b98080;
    font-size: 10px;
    font-style: normal;
    margin-top: 2px;
  }
`;

/** Cheap truncation — no dependencies, unicode-safe enough for ASCII actions. */
function truncate(text, max) {
  if (typeof text !== "string") return "";
  if (text.length <= max) return text;
  return text.slice(0, max - 1).trimEnd() + "…";
}

/** Escape a value for injection into HTML text nodes / attributes. */
function escapeHtml(value) {
  if (value === null || value === undefined) return "";
  return String(value)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
}

/** Pick the best "action text" the row can offer — D7 tolerance for either
 * shape (new: `proposed_action`; legacy schema: `task` or `cmd`). */
function actionOf(task) {
  return (
    task.proposed_action ||
    task.task ||
    task.cmd ||
    (task.kind ? `[${task.kind}]` : "") ||
    "(no action)"
  );
}

class GroveDispatchRail extends HTMLElement {
  static get observedAttributes() {
    return OBSERVED;
  }

  constructor() {
    super();
    this._root = this.attachShadow({ mode: "open" });
    this._timer = null;
    this._retryTimer = null;
    this._tasks = [];
    this._state = "loading"; // loading | populated | empty | unreachable (INVARIANTS §1)
    this._render();
  }

  connectedCallback() {
    this._fetch();
    this._timer = setInterval(() => this._fetch(), REFRESH_MS);
  }

  disconnectedCallback() {
    if (this._timer !== null) {
      clearInterval(this._timer);
      this._timer = null;
    }
    if (this._retryTimer !== null) {
      clearTimeout(this._retryTimer);
      this._retryTimer = null;
    }
  }

  attributeChangedCallback(name, oldVal, newVal) {
    if (oldVal === newVal) return;
    if (name === "lens") this._fetch();
  }

  // ---- internals ----------------------------------------------------------
  _url() {
    const lens = (this.getAttribute("lens") || "").trim().toLowerCase();
    return lens ? `/api/dispatch?lens=${encodeURIComponent(lens)}` : "/api/dispatch";
  }

  async _fetch() {
    // A prior render's retryTimer can fire after a fresh manual refresh —
    // clear it so we don't stack refetches.
    if (this._retryTimer !== null) {
      clearTimeout(this._retryTimer);
      this._retryTimer = null;
    }
    try {
      const resp = await fetch(this._url(), {
        headers: { Accept: "application/json" },
      });
      if (!resp.ok) {
        // 503 body carries {state:"unreachable", reason} per INVARIANTS.md §1.
        let reason = `HTTP ${resp.status}`;
        try {
          const errBody = await resp.json();
          if (errBody && errBody.reason) reason = errBody.reason;
        } catch (_) { /* body wasn't JSON — keep HTTP status */ }
        this._state = "unreachable";
        this._reason = reason;
        this._tasks = [];
        this._retryTimer = setTimeout(() => this._fetch(), REFRESH_MS);
        this._paint();
        return;
      }
      const body = await resp.json();
      // Endpoint returns {state, tasks} under INVARIANTS.md §1; tolerate
      // the pre-INVARIANTS bare-list shape too so a stale server does not
      // become the unreachable case.
      if (body && body.state === "unreachable") {
        this._state = "unreachable";
        this._reason = body.reason || "endpoint reported unreachable";
        this._tasks = [];
        this._retryTimer = setTimeout(() => this._fetch(), REFRESH_MS);
        this._paint();
        return;
      }
      const list = Array.isArray(body)
        ? body
        : (body && Array.isArray(body.tasks) ? body.tasks : []);
      this._tasks = list;
      // INVARIANTS.md §1 three-state contract: distinguish populated from
      // empty at the observable-state layer (the Playwright pin at
      // tests/e2e/grove-served-page.spec.js reads `_state` directly).
      this._state = list.length > 0 ? "populated" : "empty";
      this._reason = null;
    } catch (err) {
      this._state = "unreachable";
      this._reason = (err && err.message) || String(err);
      this._tasks = [];
      // One retry in 30 s (matches the normal refresh cadence — C6-C8:
      // the seam heals itself on the next tick, no operator intervention).
      this._retryTimer = setTimeout(() => this._fetch(), REFRESH_MS);
    }
    this._paint();
  }

  _render() {
    this._root.innerHTML = `
      <style>${CSS}</style>
      <header>
        <span>dispatch</span>
        <span class="lens" part="lens"></span>
      </header>
      <div class="body" part="body"></div>
    `;
    this._lensEl = this._root.querySelector(".lens");
    this._bodyEl = this._root.querySelector(".body");
    this._bodyEl.addEventListener("click", (ev) => this._onBodyClick(ev));
    this._bodyEl.addEventListener("keydown", (ev) => this._onBodyKey(ev));
  }

  _paint() {
    const lens = (this.getAttribute("lens") || "").trim().toLowerCase();
    this._lensEl.textContent = lens || "(all)";

    if (this._state === "unreachable") {
      const reasonHtml = this._reason
        ? `<div class="reason">${escapeHtml(this._reason)}</div>` : "";
      this._bodyEl.innerHTML =
        `<div class="unreachable" part="unreachable">queue source not reachable${reasonHtml}</div>`;
      return;
    }
    if (this._state === "loading") {
      this._bodyEl.innerHTML = `<div class="quiet" part="loading">
        <span class="sigil" aria-hidden="true">${QUIET_SIGIL}</span>
        <span>listening…</span>
      </div>`;
      return;
    }
    if (!this._tasks.length) {
      this._bodyEl.innerHTML = `<div class="quiet" part="quiet">
        <span class="sigil" aria-hidden="true">${QUIET_SIGIL}</span>
        <span>quiet queue</span>
      </div>`;
      return;
    }

    const items = this._tasks.map((task, index) => this._rowHtml(task, index)).join("");
    this._bodyEl.innerHTML = `<ul class="rows" part="rows">${items}</ul>`;
  }

  _rowHtml(task, index) {
    const origin = escapeHtml(task.origin || "unknown");
    const authority = String(task.authority_needed || "").toUpperCase();
    const validAuthority = /^L[1-4]$/.test(authority) ? authority : "";
    const urgency = task.urgency || "";
    const action = truncate(actionOf(task), MAX_ACTION_CHARS);

    return `
      <li class="row" data-index="${index}">
        <grove-cast-chip agent="${origin}"></grove-cast-chip>
        <span class="authority" data-tier="${escapeHtml(validAuthority)}"
              aria-label="authority ${escapeHtml(validAuthority || "unknown")}">
          ${escapeHtml(validAuthority || "·")}
        </span>
        <span class="urgency" data-level="${escapeHtml(urgency)}"
              aria-label="urgency ${escapeHtml(urgency || "background")}"></span>
        <span class="action" title="${escapeHtml(actionOf(task))}">${escapeHtml(action)}</span>
        <span class="caret" role="button" tabindex="0"
              data-index="${index}"
              aria-label="dispatch this task">&rarr;</span>
      </li>
    `;
  }

  _onBodyClick(ev) {
    const caret = ev.target && ev.target.closest && ev.target.closest(".caret");
    if (!caret) return;
    this._emitClicked(caret.getAttribute("data-index"));
  }

  _onBodyKey(ev) {
    if (ev.key !== "Enter" && ev.key !== " ") return;
    const caret = ev.target && ev.target.closest && ev.target.closest(".caret");
    if (!caret) return;
    ev.preventDefault();
    this._emitClicked(caret.getAttribute("data-index"));
  }

  _emitClicked(indexAttr) {
    const index = Number.parseInt(indexAttr, 10);
    if (!Number.isFinite(index)) return;
    const task = this._tasks[index];
    if (!task) return;
    this.dispatchEvent(new CustomEvent("dispatch-clicked", {
      bubbles: true,
      composed: true,
      detail: { task },
    }));
  }
}

if (!customElements.get("grove-dispatch-rail")) {
  customElements.define("grove-dispatch-rail", GroveDispatchRail);
}

export { GroveDispatchRail };
