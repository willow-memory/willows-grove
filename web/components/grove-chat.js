// b17: WGRV1 ΔΣ=42
/**
 * <grove-chat> — the workshop chat card. D14 metaphor: this is what
 * Tony says to Jarvis (LEFT) and what Jarvis says back (RIGHT).
 *
 * Three-state contract (see docs/INVARIANTS.md §1) for the RIGHT column:
 *   populated   — atoms present; each turn renders with sender chip + text.
 *   empty       — willow-mcp reached, no atoms; a muted italic
 *                 "no messages yet" placeholder renders in the column.
 *   unreachable — 503/fetch failure; a distinct amber banner reads
 *                 "read-back unreachable" at the top of the RIGHT column.
 *                 The banner is the ONLY content — the empty-state
 *                 placeholder is removed on entry to unreachable, so
 *                 the two states never share a pixel (INVARIANTS.md §1,
 *                 Grove v0.9 PR 12 Loki finding M11).
 *
 * Initial paint (before the first /api/journal/recent poll returns):
 * the RIGHT column shows a dashed "loading read-back…" skeleton, distinct
 * from BOTH the empty pixel and the unreachable banner. An unreached
 * surface must not read as "there is nothing there" (INVARIANTS.md §1,
 * Constraint 1). The skeleton is removed the moment the first poll
 * classifies the state as populated, empty, or unreachable.
 *
 * C11 (autonomous-continuity.md) sealed the LEFT side as an operator
 * write into willow-mcp's ``kb_journal`` via the small resident model,
 * and the RIGHT side as the resident watcher's read-back — atoms from
 * ``kb_journal`` rendered newest-first. Gate 5 lands the resident
 * watcher; this card ships the honest reader today: it tails
 * ``kb_journal`` via ``/api/journal/recent``, so the moment the watcher
 * starts writing there its turns surface here without a code change.
 *
 * Discipline: whatever the operator typed goes to ``/api/journal``
 * verbatim — no trim, no paraphrase, no normalize (mirrors V5's
 * refusal-verbatim discipline; operator words are also load-bearing).
 * Atom text on the RIGHT is likewise never innerHTML-ed — the
 * writer's bytes reach the DOM through textContent only.
 *
 * Attributes:
 *   home-edge — bottom (default) | top | left | right — D14 pop-out
 *               affordance. Passed through to the outer card container.
 *
 * Behaviour:
 *   - Two-column layout: LEFT is the composer + scrolling history of
 *     sent turns; RIGHT is the live read-back — atoms from
 *     ``/api/journal/recent`` polled every 5s (v1 cadence — slow enough
 *     that a quiet Grove is not chatty on the network, fast enough that
 *     a watcher turn appears within a couple of glances).
 *   - Submit POSTs {text, sender:"operator"} to ``/api/journal``.
 *     On 200: append the sent turn to the LEFT history alongside a
 *     ``<grove-cast-chip agent="operator">``, clear the textarea.
 *     On 503 or a network throw: show a subdued
 *     "kb_journal unreachable" chip and LEAVE the text in the composer
 *     so the operator can retry.
 *   - RIGHT column polling passes the newest-seen atom id as ``since``,
 *     so each poll fetches only new atoms. New atoms are prepended to
 *     the top of the list; if the operator is already at the top the
 *     view smooth-scrolls to reveal them, but if they are scrolled down
 *     reading older turns the view stays put (no yank).
 *   - RIGHT fetch failure shows a subdued "read-back unreachable" line
 *     at the top of the RIGHT column; polling keeps going so the line
 *     clears on the next successful poll. On entry, the loading skeleton
 *     and any empty-state div are removed.
 *   - Empty text: submit is a no-op.
 *   - Enter submits; Shift+Enter inserts a newline.
 *
 * Zero imports, pure vanilla per D9.
 *
 * @element grove-chat
 */

const READBACK_POLL_MS = 5000;
const READBACK_INITIAL_LIMIT = 25;

const OBSERVED = ["home-edge"];

class GroveChat extends HTMLElement {
  static get observedAttributes() { return OBSERVED; }

  constructor() {
    super();
    this._root = this.attachShadow({ mode: "open" });
    this._onSubmit = this._onSubmit.bind(this);
    this._onKeydown = this._onKeydown.bind(this);
    this._pollReadback = this._pollReadback.bind(this);
    // RIGHT-side polling state: newest atom id we have painted, and the
    // interval handle so disconnectedCallback can shut it down cleanly.
    this._newestReadbackId = null;
    this._readbackTimer = null;
    this._render();
  }

  connectedCallback() {
    if (!this.hasAttribute("home-edge")) this.setAttribute("home-edge", "bottom");
    const btn = this._root.querySelector("button.send");
    const ta = this._root.querySelector("textarea.composer");
    if (btn) btn.addEventListener("click", this._onSubmit);
    if (ta) ta.addEventListener("keydown", this._onKeydown);
    // Fire once immediately so an operator who opens the page sees whatever
    // is already on the wire without waiting POLL_MS for the first tick.
    this._pollReadback();
    this._readbackTimer = setInterval(this._pollReadback, READBACK_POLL_MS);
  }

  disconnectedCallback() {
    const btn = this._root.querySelector("button.send");
    const ta = this._root.querySelector("textarea.composer");
    if (btn) btn.removeEventListener("click", this._onSubmit);
    if (ta) ta.removeEventListener("keydown", this._onKeydown);
    if (this._readbackTimer !== null) {
      clearInterval(this._readbackTimer);
      this._readbackTimer = null;
    }
  }

  attributeChangedCallback(name, oldVal, newVal) {
    if (oldVal === newVal) return;
    // home-edge is a positional hint only — the card renders inline for now.
    // (The pop-out affordance ships with the D14 window-detach follow-up.)
  }

  // ---- internals ----
  _render() {
    this._root.innerHTML = `
      <style>
        :host {
          display: block;
          box-sizing: border-box;
          width: 100%;
          max-width: 100%;
          margin: 1.5rem auto;
          /* Dark warm palette matches grove-cast-chip + grove_html.py. */
          --chat-bg: #241a12;
          --chat-bg-soft: #1a140f;
          --chat-border: #3a2c1f;
          --chat-text: #efe6d8;
          --chat-muted: #a3927a;
          --chat-accent: #d4a373;
          --chat-frond: #7fb069;
          --chat-warn: #b97a4a;
          background: var(--chat-bg);
          color: var(--chat-text);
          border: 1px solid var(--chat-border);
          border-radius: 10px;
          box-shadow: 0 8px 24px rgba(0, 0, 0, 0.35);
          font: 14px/1.5 -apple-system, BlinkMacSystemFont, "Segoe UI",
                "Helvetica Neue", sans-serif;
        }
        :host([home-edge="top"]),
        :host([home-edge="bottom"]) { max-width: 900px; }
        header {
          display: flex;
          align-items: center;
          gap: 0.5rem;
          padding: 0.5rem 0.9rem;
          border-bottom: 1px solid var(--chat-border);
          color: var(--chat-muted);
          font-size: 0.78rem;
          letter-spacing: 0.02em;
        }
        header .name { color: var(--chat-text); font-weight: 600; }
        header .home-edge {
          margin-left: auto;
          font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
          font-size: 0.72rem;
          color: var(--chat-muted);
        }
        .columns {
          display: grid;
          grid-template-columns: 1fr 1fr;
          gap: 1px;
          background: var(--chat-border);
        }
        @media (max-width: 620px) {
          .columns { grid-template-columns: 1fr; }
        }
        .col {
          background: var(--chat-bg);
          padding: 0.75rem;
          display: flex;
          flex-direction: column;
          min-height: 240px;
        }
        .col h3 {
          margin: 0 0 0.5rem;
          font-size: 0.72rem;
          text-transform: uppercase;
          letter-spacing: 0.08em;
          color: var(--chat-muted);
          font-weight: 600;
        }
        .history {
          flex: 1;
          overflow-y: auto;
          display: flex;
          flex-direction: column;
          gap: 0.5rem;
          padding: 0.25rem 0;
          margin-bottom: 0.5rem;
          min-height: 120px;
          max-height: 260px;
        }
        .turn {
          display: flex;
          gap: 0.5rem;
          align-items: flex-start;
          padding: 0.4rem 0.55rem;
          background: var(--chat-bg-soft);
          border: 1px solid var(--chat-border);
          border-radius: 6px;
        }
        .turn .body {
          flex: 1;
          white-space: pre-wrap;
          word-break: break-word;
          color: var(--chat-text);
        }
        .turn .ts {
          font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
          font-size: 0.68rem;
          color: var(--chat-muted);
          flex-shrink: 0;
          padding-top: 2px;
        }
        textarea.composer {
          box-sizing: border-box;
          width: 100%;
          min-height: 64px;
          resize: vertical;
          background: var(--chat-bg-soft);
          color: var(--chat-text);
          border: 1px solid var(--chat-border);
          border-radius: 6px;
          padding: 0.5rem 0.6rem;
          font: inherit;
          margin-bottom: 0.5rem;
        }
        textarea.composer:focus {
          outline: none;
          border-color: var(--chat-accent);
        }
        .compose-row {
          display: flex;
          align-items: center;
          gap: 0.5rem;
        }
        button.send {
          all: unset;
          cursor: pointer;
          background: var(--chat-accent);
          color: #1a140f;
          padding: 0.35rem 0.9rem;
          border-radius: 6px;
          font-weight: 600;
          font-size: 0.85rem;
        }
        button.send:hover { filter: brightness(1.08); }
        button.send:focus-visible { outline: 2px solid var(--chat-frond); outline-offset: 2px; }
        .status {
          margin-left: auto;
          font-size: 0.75rem;
          color: var(--chat-muted);
          display: none;
        }
        .status[data-state="unreachable"] {
          display: inline-flex;
          align-items: center;
          gap: 0.35rem;
          color: var(--chat-warn);
        }
        .status[data-state="sending"] {
          display: inline-flex;
          color: var(--chat-muted);
        }
        .placeholder {
          flex: 1;
          display: flex;
          align-items: center;
          justify-content: center;
          text-align: center;
          color: var(--chat-muted);
          font-style: italic;
          border: 1px dashed var(--chat-border);
          border-radius: 6px;
          padding: 1rem;
        }
        .readback {
          flex: 1;
          overflow-y: auto;
          display: flex;
          flex-direction: column;
          gap: 0.5rem;
          padding: 0.25rem 0;
          min-height: 120px;
          max-height: 320px;
          scroll-behavior: smooth;
        }
        .readback-status {
          font-size: 0.72rem;
          color: var(--chat-warn);
          padding: 0.25rem 0.4rem;
          border: 1px solid var(--chat-border);
          border-radius: 4px;
          background: var(--chat-bg-soft);
          display: none;
        }
        /* INVARIANTS.md §1: unreachable MUST render distinctly from empty —
           amber banner + border, distinct copy, so the operator sees the
           difference between the empty affordance and the unreachable one. */
        .readback-status[data-state="unreachable"] {
          display: block;
          border-color: var(--chat-warn);
          background: rgba(185, 122, 74, 0.15);
        }
        .readback-status[data-state="unreachable"]::before {
          content: "\\26A0  "; /* ⚠ */
        }
        .readback-empty {
          flex: 1;
          display: flex;
          align-items: center;
          justify-content: center;
          text-align: center;
          color: var(--chat-muted);
          font-style: italic;
          padding: 1rem;
        }
        /* INVARIANTS.md §1 (Grove v0.9 PR 12, Loki finding M11): the initial
           paint of the RIGHT column, before the first poll classifies the
           state, is a distinct dashed skeleton — NOT the empty-state pixel.
           An unreached surface must not read as "there is nothing there". */
        .readback-loading {
          flex: 1;
          display: flex;
          align-items: center;
          justify-content: center;
          text-align: center;
          color: var(--chat-muted);
          border: 1px dashed var(--chat-accent);
          border-radius: 6px;
          padding: 1rem;
          font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
          font-size: 0.78rem;
          letter-spacing: 0.04em;
          opacity: 0.55;
          animation: readback-loading-pulse 1.4s ease-in-out infinite;
        }
        @keyframes readback-loading-pulse {
          0%, 100% { opacity: 0.35; }
          50%      { opacity: 0.75; }
        }
      </style>
      <header>
        <span class="name">chat</span>
        <span>·</span>
        <span>willow &middot; operator</span>
        <span class="home-edge" part="home-edge"></span>
      </header>
      <div class="columns">
        <section class="col left" aria-label="operator to willow">
          <h3>operator → willow</h3>
          <div class="history" part="history" role="log" aria-live="polite"></div>
          <textarea class="composer" placeholder="say something to willow&hellip;" rows="3"></textarea>
          <div class="compose-row">
            <button type="button" class="send">send</button>
            <span class="status" part="status"></span>
          </div>
        </section>
        <section class="col right" aria-label="willow to operator">
          <h3>willow → operator</h3>
          <div class="readback-status" part="readback-status"></div>
          <div class="readback" part="readback" role="log" aria-live="polite">
            <div class="readback-loading" aria-label="loading read-back">loading read-back&hellip;</div>
          </div>
        </section>
      </div>
    `;
    // paint home-edge label (helpful for D14 debugging).
    const label = this._root.querySelector(".home-edge");
    if (label) label.textContent = "home-edge: " + (this.getAttribute("home-edge") || "bottom");
  }

  _setStatus(state, message) {
    const el = this._root.querySelector(".status");
    if (!el) return;
    if (!state) {
      el.removeAttribute("data-state");
      el.textContent = "";
      return;
    }
    el.setAttribute("data-state", state);
    el.textContent = message || "";
  }

  _appendTurn(text, ts) {
    const history = this._root.querySelector(".history");
    if (!history) return;
    const wrap = document.createElement("div");
    wrap.className = "turn";
    const chip = document.createElement("grove-cast-chip");
    chip.setAttribute("agent", "operator");
    const body = document.createElement("div");
    body.className = "body";
    // textContent — preserve the operator's exact bytes; never innerHTML.
    body.textContent = text;
    const stamp = document.createElement("span");
    stamp.className = "ts";
    stamp.textContent = ts || "";
    wrap.appendChild(chip);
    wrap.appendChild(body);
    wrap.appendChild(stamp);
    history.appendChild(wrap);
    // Scroll to newest.
    history.scrollTop = history.scrollHeight;
  }

  _onKeydown(e) {
    // Enter submits; Shift+Enter keeps its default newline.
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      this._onSubmit();
    }
  }

  async _onSubmit() {
    const ta = this._root.querySelector("textarea.composer");
    if (!ta) return;
    // Read the raw value — do not trim it before sending. The server's
    // JSON parser is the one that decides "empty"; UI-side we only check
    // that at least one non-whitespace character is present, so an operator
    // cannot accidentally send a pure-whitespace turn.
    const raw = ta.value;
    if (!raw || !raw.replace(/\s+/g, "")) {
      return; // no-op on empty
    }
    this._setStatus("sending", "sending&hellip;");
    let res;
    try {
      res = await fetch("/api/journal", {
        method: "POST",
        headers: {
          "content-type": "application/json",
          "accept": "application/json",
        },
        body: JSON.stringify({ text: raw, sender: "operator" }),
      });
    } catch (_err) {
      // Network throw — same operator-facing state as a 503.
      this._setStatus("unreachable", "kb_journal unreachable");
      return; // leave text in the composer for retry
    }
    if (!res.ok) {
      // 400 / 503 / anything non-2xx — leave text, show unreachable.
      this._setStatus("unreachable", "kb_journal unreachable");
      return;
    }
    let doc = null;
    try { doc = await res.json(); } catch (_) { doc = null; }
    const ts = (doc && typeof doc.ts === "string") ? doc.ts : "";
    this._appendTurn(raw, ts);
    ta.value = "";
    this._setStatus(null);
  }

  // ---- RIGHT-side read-back ----
  _setReadbackStatus(state, message) {
    const el = this._root.querySelector(".readback-status");
    if (!el) return;
    if (!state) {
      el.removeAttribute("data-state");
      el.textContent = "";
      return;
    }
    el.setAttribute("data-state", state);
    el.textContent = message || "";
  }

  _renderReadbackAtom(atom) {
    const wrap = document.createElement("div");
    wrap.className = "turn";
    const chip = document.createElement("grove-cast-chip");
    // Sender falls back to "watcher" when the atom doesn't name one — the
    // resident-watcher case, once it lands. Empty string never reaches
    // the DOM as an agent attribute.
    const sender = (atom && typeof atom.sender === "string" && atom.sender)
      ? atom.sender
      : "watcher";
    chip.setAttribute("agent", sender);
    const body = document.createElement("div");
    body.className = "body";
    // textContent — the writer's bytes reach the DOM verbatim; never innerHTML.
    body.textContent = (atom && typeof atom.text === "string") ? atom.text : "";
    const stamp = document.createElement("span");
    stamp.className = "ts";
    stamp.textContent = (atom && typeof atom.ts === "string") ? atom.ts : "";
    wrap.appendChild(chip);
    wrap.appendChild(body);
    wrap.appendChild(stamp);
    return wrap;
  }

  _prependReadbackAtoms(atoms) {
    const list = this._root.querySelector(".readback");
    if (!list || !atoms || atoms.length === 0) return;
    // Populated — remove the loading skeleton (initial paint) and any
    // stale empty-state div. INVARIANTS.md §1: the three states never
    // share pixels.
    const loading = list.querySelector(".readback-loading");
    if (loading) loading.remove();
    const empty = list.querySelector(".readback-empty");
    if (empty) empty.remove();
    // atoms arrive newest-first from the reader; prepend in reverse so
    // the newest ends up at the very top of the column.
    const atTop = list.scrollTop <= 4;
    for (let i = atoms.length - 1; i >= 0; i -= 1) {
      const node = this._renderReadbackAtom(atoms[i]);
      list.insertBefore(node, list.firstChild);
    }
    // Only pull the view up when the operator was already reading from
    // the top — never yank them out of scroll-back.
    if (atTop) list.scrollTop = 0;
  }

  _paintReadbackUnreachable() {
    // INVARIANTS.md §1 (Grove v0.9 PR 12, Loki finding M11): unreachable
    // renders as the amber banner ALONE — the empty-state placeholder
    // and the loading skeleton are both removed on entry so an unreached
    // read-back never shares a pixel with a reached-but-empty one.
    const list = this._root.querySelector(".readback");
    if (list) {
      const loading = list.querySelector(".readback-loading");
      if (loading) loading.remove();
      const empty = list.querySelector(".readback-empty");
      if (empty) empty.remove();
    }
    this._setReadbackStatus("unreachable", "read-back unreachable");
  }

  _paintReadbackEmpty() {
    // Reached-but-empty — clear any stale unreachable banner, drop the
    // loading skeleton, and paint the "no messages yet" placeholder if it
    // isn't already there. Distinct pixel from the unreachable banner
    // per INVARIANTS.md §1.
    this._setReadbackStatus(null);
    const list = this._root.querySelector(".readback");
    if (!list) return;
    const loading = list.querySelector(".readback-loading");
    if (loading) loading.remove();
    if (!list.querySelector(".readback-empty")) {
      const div = document.createElement("div");
      div.className = "readback-empty";
      div.textContent = "no messages yet";
      list.appendChild(div);
    }
  }

  async _pollReadback() {
    // Not connected any more — belt-and-braces against a late-firing timer.
    if (!this.isConnected) return;
    const params = new URLSearchParams();
    // First fetch pulls the initial window; subsequent fetches carry the
    // newest-seen id as `since` so the server only returns new atoms.
    if (this._newestReadbackId) {
      params.set("since", this._newestReadbackId);
    } else {
      params.set("limit", String(READBACK_INITIAL_LIMIT));
    }
    let res;
    try {
      res = await fetch("/api/journal/recent?" + params.toString(), {
        headers: { "accept": "application/json" },
      });
    } catch (_err) {
      this._paintReadbackUnreachable();
      return;
    }
    if (!res.ok) {
      this._paintReadbackUnreachable();
      return;
    }
    let body = null;
    try { body = await res.json(); } catch (_) { body = null; }
    // INVARIANTS.md §1: 200 body carries {state, atoms}. Tolerate the
    // pre-INVARIANTS bare-list shape so a stale server doesn't collapse
    // to unreachable spuriously.
    let atoms = null;
    if (Array.isArray(body)) {
      atoms = body;
    } else if (body && body.state === "unreachable") {
      this._paintReadbackUnreachable();
      return;
    } else if (body && Array.isArray(body.atoms)) {
      atoms = body.atoms;
    }
    if (!Array.isArray(atoms)) {
      this._paintReadbackUnreachable();
      return;
    }
    if (atoms.length === 0) {
      this._paintReadbackEmpty();
      return;
    }
    this._setReadbackStatus(null);
    this._prependReadbackAtoms(atoms);
    // Update the newest-seen cursor from the first (newest) atom.
    const head = atoms[0];
    if (head && typeof head.id === "string" && head.id) {
      this._newestReadbackId = head.id;
    }
  }
}

if (!customElements.get("grove-chat")) {
  customElements.define("grove-chat", GroveChat);
}

export { GroveChat };
