# Gerald atoms to the main table (2026-10-06)

*Desk session, 2026-10-06, at the operator's word: "build the table from the
Gerald atoms, and then connect it to the man. Two separate tasks." Asked which
one, the operator chose the main table (grid one). This is the second task. It links [the Gerald atoms table](gerald-atoms-table-2026-10-06.md)
(rows AA–AL) to [the main table](../one-box/rules-cross-table-2026-10-06.md)
(grid one, rows A–M). Agent-reported; not ratified.*

## How it's built

- **An atom links to a main-table box only where the atom names that box.**
  No link comes from a reading. The rule is a regular expression for a
  main-table address (A1–M13) over each atom's content, and it's run only on
  atoms whose source is one of the grid documents (the drip grid, grid one,
  grid two or the crosswalk). Elsewhere, a token like "B1" means something
  else.
- **Four tokens look like boxes but name something else,** so they're set
  aside wherever they appear, by the words around them:

  | Token | What it names | Atoms |
  |---|---|---|
  | D10 | the one-box plan's decision D10 (ingress) | S05, S06, S11 |
  | D7 | the premise doc's decision D7 | S06, S14 |
  | C3, in "C3 discipline" | INVARIANTS' C3 | S15 |
  | B1, in "B1 store" | the one script's boot step B1 | S18 |

- **The result:** 18 atoms link to 36 distinct boxes of the main table, 69
  references in all. Each link runs from the atom's box in the Gerald table
  to the boxes it names. The labels at both ends are copied from the maps,
  and `cross_table.py link` checked every address.
- **The other 116 atoms** name no main-table box. Most are Gerald canon, craft
  and the Aionic process, which the main table doesn't hold. That isn't a gap
  in the links. It's the measure of how far apart the two tables are.
- Every link is `unattested`.

## The links

<!-- cross-table:links -->
| From | To | Where they touch | Standing |
|---|---|---|---|
| AA3 S03 Why these parents: the … | G5 Trailers: `Persona:`, `Ratified-by:` · K10 D10 Ingress: no tunnel by default · L6 5 Nestor behind Rat · J2 §2 Supersedes D7 · J9 §9 Seed reads real canon · G4 Standing grant in first commit · J7 §7 Consent is real, not automatic · B11 Only the seal ledger is shared | Atom S03 names these boxes of the main table. | unattested |
| AA5 S05 Silent cells: a clause … | K10 D10 Ingress: no tunnel by default | Atom S05 names these boxes of the main table. | unattested |
| AA6 S06 Rows R to Z … | G5 Trailers: `Persona:`, `Ratified-by:` · K10 D10 Ingress: no tunnel by default · L6 5 Nestor behind Rat · J2 §2 Supersedes D7 · J9 §9 Seed reads real canon · G4 Standing grant in first commit · J7 §7 Consent is real, not automatic · B11 Only the seal ledger is shared | Atom S06 names these boxes of the main table. | unattested |
| AA9 S09 Row R (G5): every … | G5 Trailers: `Persona:`, `Ratified-by:` | Atom S09 names these boxes of the main table. | unattested |
| AA10 S10 Row R (G5), PR … | G5 Trailers: `Persona:`, `Ratified-by:` | Atom S10 names these boxes of the main table. | unattested |
| AA11 S11 Row S (K10, D10), … | K10 D10 Ingress: no tunnel by default | Atom S11 names these boxes of the main table. | unattested |
| AA12 S12 Row S (K10), vendor … | K10 D10 Ingress: no tunnel by default | Atom S12 names these boxes of the main table. | unattested |
| AA13 S13 Row T (L6, Nestor … | L6 5 Nestor behind Rat | Atom S13 names these boxes of the main table. | unattested |
| AB1 S14 Row U (J2, section … | J2 §2 Supersedes D7 | Atom S14 names these boxes of the main table. | unattested |
| AB2 S15 Row V (J9, section … | J9 §9 Seed reads real canon | Atom S15 names these boxes of the main table. | unattested |
| AB3 S16 Row W (G4, standing … | G4 Standing grant in first commit | Atom S16 names these boxes of the main table. | unattested |
| AB4 S17 Row X (J7, section … | J7 §7 Consent is real, not automatic | Atom S17 names these boxes of the main table. | unattested |
| AB5 S18 Row Y (B11, only … | B11 Only the seal ledger is shared | Atom S18 names these boxes of the main table. | unattested |
| AB9 S22 Grid one measure: 169 … | G6 Session branch name · G5 Trailers: `Persona:`, `Ratified-by:` · E7 No long-lived shells · F7 Unknown law is refused · F8 Amends waits for the seal · F10 Any internal error fails closed · F12 Same box → same bytes · K10 D10 Ingress: no tunnel by default · L6 5 Nestor behind Rat · J2 §2 Supersedes D7 · J9 §9 Seed reads real canon | Atom S22 names these boxes of the main table. | unattested |
| AC2 S28 Crosswalk links, part 1: … | C1 Ask Nestor first · C2 Then look in the box · C3 Only then go remote · B6 Unguessable ids · I1 Everything is a hash · A1 Honest state · J1 §1 Three-state contract | Atom S28 names these boxes of the main table. | unattested |
| AC3 S29 Crosswalk links, part 2: … | A11 Template ships the box · A7 Egress: three keys + click · A4 Reading open, saving guarded · B1 Model sees only its scope · F6 Code checks the cite's form; a witness checks it's true · I3 Pointers, not prose | Atom S29 names these boxes of the main table. | unattested |
| AC4 S30 Crosswalk links, part 3: … | L2 1 The socket standard · A8 Portless · K3 D3 Home of the socket standard · E2 Isolation · G8 Reviewed shell work goes through Kart · I9 Picture and compare · L11 Sequencing: what not to break · I7 Pile it up; what stacks matters · A11 Template ships the box · L10 9 The template ships the box | Atom S30 names these boxes of the main table. | unattested |
| AC5 S31 Crosswalk, O5 Nested boxes … | G5 Trailers: `Persona:`, `Ratified-by:` · K10 D10 Ingress: no tunnel by default · L6 5 Nestor behind Rat · J2 §2 Supersedes D7 · J9 §9 Seed reads real canon · G4 Standing grant in first commit · J7 §7 Consent is real, not automatic · B11 Only the seal ledger is shared | Atom S31 names these boxes of the main table. | unattested |
<!-- /cross-table:links -->

---

ΔΣ=42
