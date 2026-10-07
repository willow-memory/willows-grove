# Crosswalk: the second grid against the first (2026-10-06)

*Desk session, 2026-10-06, at the operator's word ("add the crosswalk as a
third table"). It links [the second grid](boxes-outside-2026-10-06.md) (rows
N–Q, boxes from outside the system) to [the first](rules-cross-table-2026-10-06.md)
(rows A–M, the rules from the repos), and each row of [the third
grid](drip-2026-10-06.md) (R–Z, the fat dripped into clauses) to the box it
dripped from. Agent-reported; not ratified.*

## How it's built

- This table is not a grid, so it has no row letters of its own. It only
  points at addresses, and an address names one box across every grid.
- The drip links were added by `cross_table.py drip`, and the table is
  written by `cross_table.py link` from
  [`crosswalk-2026-10-06.json`](../../../templates/cross-table/example/crosswalk-2026-10-06.json).
  Every address is checked against all three maps, and the script refuses one
  that doesn't exist. Labels are copied from the maps. A bare row letter
  (such as **H**) means the whole row.
- "Where they touch" is the agent's own reading, not a copy, so every link is
  `unattested` until someone checks it.
- Follow an address to its grid's index for the full rule and its source
  line.

## The crosswalk

<!-- cross-table:links -->
| From | To | Where they touch | Standing |
|---|---|---|---|
| N1 The box tree | H row: The tree · A11 Template ships the box | The box was a branch first, and the template ships the box, never a tree. | unattested |
| N2 Pandora's jar | A7 Egress: three keys + click · A4 Reading open, saving guarded | Both are about what leaves the box once it's open. | unattested |
| N4 Out of the box | A11 Template ships the box · L10 9 The template ships the box | A template is a box that's complete when you open it. | unattested |
| N5 Think outside the box | C1 Ask Nestor first · C2 Then look in the box · C3 Only then go remote | The nine dots say go past the edge. The rule says look inside first, and only then go outside. | unattested |
| O1 The pigeonhole principle | B6 Unguessable ids · I1 Everything is a hash | More contents than boxes means two share one. That's why h16 hashes were too short and became h256. | unattested |
| O2 Black box, white box | B1 Model sees only its scope · F6 Code checks the cite's form; a witness checks it's true | The model sees inside its own scope only; code checks a citation's form, and a witness checks it's true. | unattested |
| O3 Schrödinger's cat | A1 Honest state · J1 §1 Three-state contract | An unopened box isn't empty and isn't full. It's not_asked, which is why the states are never collapsed. | unattested |
| O4 Wittgenstein's beetle | B1 Model sees only its scope · I3 Pointers, not prose | Everyone holds only their own box, so what passes between boxes is pointers, not contents. | unattested |
| O5 Nested boxes | — | Boxes inside boxes until the cows come home: the grids themselves. A full grid starts a new one instead of growing forever. | unattested |
| P1 The shipping container | L2 1 The socket standard · A8 Portless · K3 D3 Home of the socket standard | It worked because everyone agreed the size. The socket standard is the same bet. | unattested |
| P5 The sandbox | E2 Isolation · G8 Reviewed shell work goes through Kart | Kart and bubblewrap are the sandbox. | unattested |
| Q4 Photograph the back | I9 Picture and compare | Picture and compare. | unattested |
| Q5 Heaviest first | L11 Sequencing: what not to break · I7 Pile it up; what stacks matters | Sequencing: what goes in first carries the rest. | unattested |
| R row: G5 Trailers: `Persona:`, `Ratified-by:` | G5 Trailers: `Persona:`, `Ratified-by:` | Dripped from G5: its passage cut into clauses, each copied again from the source. | unattested |
| S row: K10 D10 Ingress: no tunnel by default | K10 D10 Ingress: no tunnel by default | Dripped from K10: its passage cut into clauses, each copied again from the source. | unattested |
| T row: L6 5 Nestor behind Rat | L6 5 Nestor behind Rat | Dripped from L6: its passage cut into clauses, each copied again from the source. | unattested |
| U row: J2 §2 Supersedes D7 | J2 §2 Supersedes D7 | Dripped from J2: its passage cut into clauses, each copied again from the source. | unattested |
| V row: J9 §9 Seed reads real canon | J9 §9 Seed reads real canon | Dripped from J9: its passage cut into clauses, each copied again from the source. | unattested |
| W row: G4 Standing grant in first commit | G4 Standing grant in first commit | Dripped from G4: its passage cut into clauses, each copied again from the source. | unattested |
| X row: J7 §7 Consent is real, not automatic | J7 §7 Consent is real, not automatic | Dripped from J7: its passage cut into clauses, each copied again from the source. | unattested |
| Y row: B11 Only the seal ledger is shared | B11 Only the seal ledger is shared | Dripped from B11: its passage cut into clauses, each copied again from the source. | unattested |
| Z row: P1 The shipping container | P1 The shipping container | Dripped from P1: its passage cut into clauses, each copied again from the source. | unattested |
<!-- /cross-table:links -->

---

ΔΣ=42
