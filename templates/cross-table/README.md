# Cross table — a template

*Desk session, 2026-10-06. Built from the rules cross table at the
operator's word ("yes, make it a template"). Agent-reported; not ratified.*

> "This isn't about making everything fit in a box — it's about making a box
> that the user and the system can grow together." (operator, 2026-10-01)

A cross table is a grid of addresses. Each cell is filled by **copying** a
passage from a source file, never by writing one. The template is the
box: the grid, the map, the filler and the standing column. What goes in it
is yours to choose.

## What's here

| File | What it is |
|---|---|
| [`cross_table.py`](cross_table.py) | The filler. Stdlib only, deterministic: the same map and the same files give the same bytes. |
| [`example/rules-map-2026-10-06.json`](example/rules-map-2026-10-06.json) | The worked example: the map behind [`rules-cross-table-2026-10-06.md`](../../docs/design/one-box/rules-cross-table-2026-10-06.md), 13 × 13, 168 cells found and 1 silent. |
| [`example/boxes-outside-map-2026-10-06.json`](example/boxes-outside-map-2026-10-06.json) | The second example: a 4 × 5 grid (rows N–Q, after the first grid's A–M) whose source is a notes section inside the same document ([`boxes-outside-2026-10-06.md`](../../docs/design/one-box/boxes-outside-2026-10-06.md)). It shows that the source can be the document itself, as long as the notes are marked for what they are. |
| [`example/crosswalk-2026-10-06.json`](example/crosswalk-2026-10-06.json) | The third example: a crosswalk between the two grids, written by `link` into [`crosswalk-2026-10-06.md`](../../docs/design/one-box/crosswalk-2026-10-06.md). |

## The four parts

1. **A grid of addresses.** Rows are letters (A–Z) and columns are numbers.
   Once an address is given out it is never renumbered. When the grid is
   full, start a second one, with its rows starting where the last grid
   stopped (`new --after`). An address names one box across every grid, so
   two grids never share a row letter (`check --with` and `fill --with`
   refuse it).
2. **A map** (JSON). For each row: a title and the row's source. For each
   cell: a label, a file, a pattern that finds the passage, a mode, and a
   standing.
3. **The filler** copies the matching passage with its file and line. It
   never guesses. A cell it can't fill says why:

   | State | Means |
   |---|---|
   | `found` | The pattern matched, and the passage is copied with its line. |
   | `source silent` | The map names no source for this cell (add a `note` saying why). |
   | `unreachable` | The file isn't there. |
   | `not found` | The file is there, and the pattern matched nothing in it. |

   These are never collapsed into one another (INVARIANTS §1).
4. **Standing:** `unattested`, `witnessed` or `sealed`. It lives in the map,
   and the script only copies it. An agent writes `unattested`. A second,
   independent check can move a cell to `witnessed`. Only the operator
   writes `sealed`.

## Use it

```sh
# 1. A blank map: 13 × 13 by default, any size up to 26 rows.
python3 templates/cross-table/cross_table.py new my-map.json --rows 13 --cols 13 --title "My table"
#    A second grid, rows starting after the first one's last row (A–M → N…).
python3 templates/cross-table/cross_table.py new next-map.json --rows 4 --cols 5 --after my-map.json

# 2. Fill in the map by hand: rows[].title and source, and per cell the
#    label, file, pattern, mode. This is the part that decides what the
#    box is for, and it's the person's call.

# 3. See what every cell finds. Exits 1 if anything is unreachable or not found.
#    --with refuses the map if it shares a row letter with another grid.
python3 templates/cross-table/cross_table.py check next-map.json --with my-map.json

# 4. Write the grid, the row sources and the index into a document.
python3 templates/cross-table/cross_table.py fill my-map.json my-table.md
```

- File paths in the map are relative to the map's `root`, which is itself
  relative to the map file. The example's root is the folder that holds the
  three repos side by side. `--root` overrides it.
- `fill` writes only between the `<!-- cross-table:grid -->`,
  `<!-- cross-table:sources -->` and `<!-- cross-table:index -->` markers. The
  rest of the document is left alone, so it can carry its own introduction
  and notes. A new document gets the three sections appended.
- `new` refuses to overwrite a map that already exists.

## Crosswalks between grids

```sh
python3 templates/cross-table/cross_table.py link links.json crosswalk.md --map my-map.json --map next-map.json
```

A crosswalk isn't a grid, so it has no rows of its own. Each link is
`{"from": "N1", "to": ["H", "A11"], "why": "…", "standing": "unattested"}`.
Every address is checked against the maps and refused if it doesn't exist,
and a bare row letter means the whole row. Labels are copied from the maps.
The `why` is a reading, not a copy, so it carries its own standing. The
table is written between `<!-- cross-table:links -->` markers.

## Modes

| Mode | Copies |
|---|---|
| `para` | The whole block that matches: a list item, a paragraph, or a docstring. |
| `sent` | Only the sentences in that block that match. |
| `row` | A table row, with its cells joined by " — ". |
| `head` | A heading and the block that follows it. |
| `line` | The matching line, plus `span` lines after it. Comment markers are stripped. Use this for code. |

Write patterns as Python regular expressions. A space in a pattern matches
any run of whitespace, so a passage that wraps across lines still matches.
Copied text is collapsed to one line and trimmed at about 420 characters (…).
The source line is where the rest is.

## Fixed for anyone using it

These are the rules from the example, carried over:

- **Copy, don't compose.** If the source and the label disagree, the source
  wins, and you flag the label.
- **One cell, one source line.**
- **Propose, don't seal.** A filled table is a proposal until a person seals
  it.
- **Look in the box first.** Sources are local files, never the web.
- **Leave the vault alone.** Nothing under the operator's vault is a source.
