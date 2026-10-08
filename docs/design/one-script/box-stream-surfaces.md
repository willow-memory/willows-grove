<!-- b17: WGRV1  ΔΣ=42 -->
# Which parts of the Grove can run as a box stream

§1 Status · §2 The test · §3 Fits fully · §4 Boxes, but no narration · §5 Not this way · §6 Order · §7 The dispatch rail as a box stream · §8 The envelope panel as a box stream

## §1 Status

**Proposal.** Written 2026-10-08. The operator: *"What other sections of the
UI can run this way now?"* then *"write them all down, and sketch the dispatch
rail as a box stream"*. Built on [`local-flow-and-ui.md`](local-flow-and-ui.md)
§5 and the box stream sketches ([v1](box-stream-v1.html),
[v1.1](box-stream-v1.1.html)). Fit percentages are the agent's reading.

## §2 The test

"This way" means:

- code makes the boxes;
- everything an agent outputs is a box, and the human's lines stay plain;
- a small model may say the boxes as one sentence;
- code checks that sentence (every cite served, every box cited, nothing the
  boxes lack, the human's words quoted exactly).

A part of the UI fits when its data is already a set of structured facts. The
list below walks the premise's composition table
([`../willow-grove-premise.md`](../willow-grove-premise.md), "Composition
sketch") and the readers in `grove/`.

## §3 Fits fully: boxes plus a narrated line

| Part | Source of the boxes | Reader in `grove/` | Narrated line, e.g. | Fit |
|---|---|---|---|---|
| Dispatch rail | `dispatch_list()`: `origin`, `urgency`, `authority_needed`, `proposed_action`, `status` | yes: `kart_reader.py` | "7 tasks queued, 2 need L3 or above" | 90% |
| Morning screen (check-out) | NEEDS YOU, DISAGREEMENTS, AGREED NOT SEALED, GRADES, QUIET | the one script's `view`, `deep_thought.py` | "2 need you; nothing disagrees; the gates are quiet" | 90% |
| Human-required queue | `grove_human_required()`: each row cites its blocking decision | not yet | "3 things wait on you, the oldest from Tuesday" | 85% |
| Envelope panel | `envelopes/pre-approved.json`: expiry, `current/max`, grantee | yes: `envelope_reader.py` | "Kart's grant is 2 of 3 used and expires Friday" | 85% |
| Fleet status | `grove_fleet_status`: one row per agent | yes: `fleet_presence.py`, `persona_roster.py` | "Loki is auditing, Kart is idle, Ada hasn't checked in" | 80% |
| PA card | `pa/commitments`, due soonest first | no | "Next: X, due today" | 75% |

## §4 Boxes, but no narration

| Part | Why no sentence | Fit for boxes |
|---|---|---|
| Refusal voice | Nestor's refusals render verbatim, never paraphrased (V5). The box shows them exactly; no model retells them. | 95% |
| Standing strip (`/health`) | One box: the commit, live or unreachable. Nothing to add. | 90% |
| Governance answers ("may we?") | Seals belong to Nestor and the human. A model sentence about seal state is the riskiest claim it could make; show the seal card and its evidence boxes only. | 85% |
| Ambient memory strip | Ledger receipts are ambient; a sentence would pull attention it shouldn't. | 80% |
| Persona horizon | The glyphs and colors are already the box. A state change can drop into the stream as a box. | 70% |

## §5 Not this way

| Part | Why |
|---|---|
| The willow (the hero) | Animation and easter eggs, no data. It stays outside the served set. |
| The seed canon (`/seed/1-6`) | Frozen canon text (CLAUDE.md rule 12), read as written. |
| Voice-triggered panels | The human's speech is a plain line. Picking the panel is classification, not narration. |

## §6 Order

1. **Dispatch rail.** Its reader exists, its rows are state-carrying records,
   its three states are pinned by the e2e suite, and the v1 sketch already
   draws proposals as the same kind of card. Sketched in §7.
2. **Envelope panel.** Numbers and dates make check 3 strict and cheap.
3. **Morning screen.** It is the box stream's own content.

## §7 The dispatch rail as a box stream

Sketch: [`dispatch-rail-stream-v1.html`](dispatch-rail-stream-v1.html).

| Piece | In the sketch |
|---|---|
| The pile | Every Kart task by state: queued, working, complete, verified, cleared |
| Boxes | One summary box made by code (the count, how many need L3 or above), then the queued tasks in the reader's order: `urgency` first, then oldest. Each shows origin, authority pill, urgency, `proposed_action` verbatim, and age. |
| Who wrote it | `proposed_action` is agent text, so it is a box. The human's drain choice is a plain line. |
| The sentence | Cites every box; counts come only from the summary box |
| Human action | "Drain at L1–L4" and "Hold" on a task. The choice appears as the human's plain line; picking the drain tier is the human's act (C8). |
| States | Populated; a task arriving; a sentence that invents a tier and is struck; the quiet queue ❦ (no model asked); Kart unreachable with its reason |

## §8 The envelope panel as a box stream

The operator: *"pick a third"*. The agent picked the envelope panel, next in
§6's order. Sketch: [`envelope-panel-stream-v1.html`](envelope-panel-stream-v1.html).

| Piece | In the sketch |
|---|---|
| The pile | Every envelope on record by attestation: attested, attestation missing, attestation invalid, retired |
| Boxes | A summary box made by code (count by attestation), then one box per grant: grantee, kind and mode, attestation pill, a `used_count / max_count` meter, expiry as code computed it |
| Who wrote it | A grant is an Operator Key act, so its `notes` are the human's words: marked "you wrote, at grant", and either "shown to you, not served" or "served, quoted exactly" |
| Never served | `paths` are shown to the human but never served to the model |
| The checker | "attested" is allowed only when the cited box holds it; a wrong one reads as a safe grant |
| No grant button | Grove renders, never grants (CONST-0-3); renewing is the human's act in the charter |
| States | On file; near a limit (the human's notes served and quoted); a sentence that calls a missing attestation "attested" and is struck; one file that won't parse, kept as its own box so it is counted, not lost; none on file, with no model asked |
