// b17: WGRV1 ΔΣ=42
/**
 * <grove-chat> — the workshop chat card. D14 metaphor: this is what
 * Tony says to Jarvis (LEFT) and what Jarvis says back (RIGHT).
 *
 * C11 (autonomous-continuity.md) sealed the LEFT side as an operator
 * write into willow-mcp's ``kb_journal`` via the small resident model.
 * The RIGHT side is the resident watcher's read-back and lands in a
 * follow-up PR; this card ships the write path only.
 *
 * Discipline: whatever the operator typed goes to ``/api/journal``
 * verbatim — no trim, no paraphrase, no normalize (mirrors V5's
 * refusal-verbatim discipline; operator words are also load-bearing).
 *
 * Attributes:
 *   home-edge — bottom (default) | top | left | right — D14 pop-out
 *               affordance. Passed through to the outer card container.
 *
 * Behaviour:
 *   - Two-column layout: LEFT is the composer + scrolling history of
 *     sent turns; RIGHT is a placeholder for the resident watcher's
 *     read-back (labelled "pending resident-watcher").
 *   - Submit POSTs {text, sender:"operator"} to ``/api/journal``.
 *     On 200: append the sent turn to the LEFT history alongside a
 *     ``<grove-cast-chip agent="operator">``, clear the textarea.
 *     On 503 or a network throw: show a subdued
 *     "kb_journal unreachable" chip and LEAVE the text in the composer
 *     so the operator can retry.
 *   - Empty text: submit is a no-op.
 *   - Enter submits; Shift+Enter inserts a newline.
 *
 * Zero imports, pure vanilla per D9.
 *
 * @element grove-chat
 */

const OBSERVED = ["home-edge"];

class GroveChat extends HTMLElement {
  static get observedAttributes() { return OBSERVED; }

  constructor() {
    super();
    this._root = this.attachShadow({ mode: "open" });
    this._onSubmit = this._onSubmit.bind(this);
    this._onKeydown = this._onKeydown.bind(this);
    this._render();
  }

  connectedCallback() {
    if (!this.hasAttribute("home-edge")) this.setAttribute("home-edge", "bottom");
    const btn = this._root.querySelector("button.send");
    const ta = this._root.querySelector("textarea.composer");
    if (btn) btn.addEventListener("click", this._onSubmit);
    if (ta) ta.addEventListener("keydown", this._onKeydown);
  }

  disconnectedCallback() {
    const btn = this._root.querySelector("button.send");
    const ta = this._root.querySelector("textarea.composer");
    if (btn) btn.removeEventListener("click", this._onSubmit);
    if (ta) ta.removeEventListener("keydown", this._onKeydown);
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
          <div class="placeholder">
            resident watcher read-back &mdash; pending resident-watcher
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
}

if (!customElements.get("grove-chat")) {
  customElements.define("grove-chat", GroveChat);
}

export { GroveChat };
