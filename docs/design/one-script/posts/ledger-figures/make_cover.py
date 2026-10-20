"""The cover for posts/ledger.md, drawn as flat vector shapes (matplotlib).

    python make_cover.py        # writes cover.png beside this file, 1000x420 (DEV's cover size)

Style matched to the series covers (posts/day-3-cover-prompt.md): flat vector, mid-century
retro, clay orange / steel blue / charcoal / cream, black outlines, a checkered floor, one
CRT-headed robot. The scene: an open ledger where the misses are written down beside the
hits, and a robot holding up a coin marked 50%, the forecaster's ESCALATE.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import Circle, FancyBboxPatch, Polygon, Rectangle  # noqa: E402

HERE = Path(__file__).resolve().parent
CREAM, CREAM2, ORANGE, BLUE = "#f3ead8", "#e8dcc2", "#d9773f", "#3f6e94"
CHARCOAL, INK, PAPER, MISS = "#3a3a3a", "#1d1d1d", "#fbf6ea", "#b8452c"
LW = 2.2


def _box(ax, x, y, w, h, fc, r=0.0, lw=LW, z=2):
    ax.add_patch(
        FancyBboxPatch(
            (x, y),
            w,
            h,
            boxstyle=f"round,pad=0,rounding_size={r}",
            fc=fc,
            ec=INK,
            lw=lw,
            zorder=z,
        )  # fmt: skip
    )


def floor(ax):
    """A checkered floor in perspective, orange and steel blue."""
    horizon, top, n = 0.0, 1.55, 16
    rows = [0.0, 0.22, 0.48, 0.80, 1.20, 1.55]
    for i in range(len(rows) - 1):
        y0, y1 = rows[i], rows[i + 1]
        for j in range(-n, n):

            def xs(y, k):
                spread = 1 + (top - y) * 0.9
                return 5 + (k - 0) * 0.62 * spread

            quad = [
                (xs(y0, j), y0),
                (xs(y0, j + 1), y0),
                (xs(y1, j + 1), y1),
                (xs(y1, j), y1),
            ]
            c = ORANGE if (i + j) % 2 == 0 else BLUE
            ax.add_patch(Polygon(quad, closed=True, fc=c, ec=INK, lw=0.8, zorder=1))
    ax.plot([0, 10], [top, top], color=INK, lw=LW, zorder=1)
    _ = horizon


def ledger(ax):
    """An open book on a stand: hits and misses written down alike."""
    _box(ax, 3.25, 0.95, 3.5, 0.35, CHARCOAL, r=0.05)  # the desk top
    _box(ax, 3.45, 0.1, 0.25, 0.85, CHARCOAL)
    _box(ax, 6.3, 0.1, 0.25, 0.85, CHARCOAL)
    for x0, sign in ((3.45, -1), (5.0, 1)):
        page = Polygon(
            [(x0, 1.3), (x0 + 1.55, 1.38), (x0 + 1.55, 3.55), (x0, 3.45)]
            if sign < 0 else
            [(x0, 1.38), (x0 + 1.55, 1.3), (x0 + 1.55, 3.45), (x0, 3.55)],
            closed=True, fc=PAPER, ec=INK, lw=LW, zorder=3,
        )  # fmt: skip
        ax.add_patch(page)
    ax.plot([5.0, 5.0], [1.38, 3.55], color=INK, lw=LW, zorder=4)
    ax.text(4.22, 3.12, "LEDGER", ha="center", va="center", fontsize=15,
            fontweight="bold", color=INK, family="DejaVu Sans", zorder=5)  # fmt: skip
    rows = [
        ("✓", BLUE),
        ("✗", MISS),
        ("✓", BLUE),
        ("✗", MISS),
        ("✗", MISS),
        ("✓", BLUE),
    ]
    for k, (mark, col) in enumerate(rows):
        y = 2.72 - k * 0.22
        for x0 in (3.65,):
            ax.plot([x0, x0 + 0.95], [y, y], color=CHARCOAL, lw=1.4, zorder=4)
            ax.text(x0 + 1.15, y + 0.02, mark, ha="center", va="center", fontsize=12,
                    color=col, fontweight="bold", zorder=5)  # fmt: skip
    # right page: a falling-then-flat line, the running score
    xs = [5.2, 5.45, 5.7, 5.95, 6.2, 6.45, 6.6]
    ys = [3.2, 2.45, 2.75, 2.55, 2.62, 2.58, 2.6]
    ax.plot(xs, ys, color=ORANGE, lw=3, zorder=5, solid_capstyle="round")
    ax.plot([5.2, 6.6], [2.25, 2.25], color=BLUE, lw=3, zorder=5)
    for k in range(5):
        y = 1.95 - k * 0.12
        ax.plot([5.2, 6.55], [y, y], color=CHARCOAL, lw=1.0, zorder=4)


def robot(ax):
    """A boxy CRT-headed robot holding up a coin marked 50%."""
    x = 7.6
    _box(ax, x - 0.15, 0.1, 0.35, 0.9, CHARCOAL, r=0.05)  # legs
    _box(ax, x + 0.45, 0.1, 0.35, 0.9, CHARCOAL, r=0.05)
    _box(ax, x - 0.4, 0.95, 1.45, 1.35, BLUE, r=0.12)  # body
    _box(ax, x - 0.1, 1.25, 0.85, 0.5, CREAM2, r=0.06, z=3)  # chest panel
    for k, c in enumerate((ORANGE, CHARCOAL, ORANGE)):
        ax.add_patch(
            Circle((x + 0.08 + k * 0.25, 1.5), 0.07, fc=c, ec=INK, lw=1.2, zorder=4)
        )
    _box(ax, x - 0.35, 2.35, 1.35, 1.05, CHARCOAL, r=0.14)  # CRT head
    _box(ax, x - 0.2, 2.5, 1.05, 0.75, "#cfe0d9", r=0.12, z=3)  # screen
    ax.add_patch(Circle((x + 0.12, 2.92), 0.06, fc=INK, ec=INK, zorder=4))
    ax.add_patch(Circle((x + 0.52, 2.92), 0.06, fc=INK, ec=INK, zorder=4))
    ax.plot(
        [x + 0.12, x + 0.32, x + 0.52], [2.68, 2.62, 2.68], color=INK, lw=2, zorder=4
    )
    ax.plot([x + 0.32, x + 0.32], [3.4, 3.62], color=INK, lw=LW, zorder=2)  # antenna
    ax.add_patch(Circle((x + 0.32, 3.68), 0.07, fc=ORANGE, ec=INK, lw=1.5, zorder=3))
    # raised arm and the coin
    ax.add_patch(Polygon([(x + 1.0, 2.1), (x + 1.25, 2.2), (x + 1.65, 3.05), (x + 1.42, 3.12)],
                         closed=True, fc=BLUE, ec=INK, lw=LW, zorder=2))  # fmt: skip
    ax.add_patch(Circle((x + 1.62, 3.42), 0.42, fc="#e2b04a", ec=INK, lw=LW, zorder=4))
    ax.add_patch(Circle((x + 1.62, 3.42), 0.33, fc="none", ec=INK, lw=1.2, zorder=5))
    ax.text(x + 1.62, 3.42, "50%", ha="center", va="center", fontsize=13,
            fontweight="bold", color=INK, zorder=6)  # fmt: skip
    # the other arm resting toward the ledger
    ax.add_patch(Polygon([(x - 0.4, 2.05), (x - 0.4, 1.8), (x - 0.95, 1.45), (x - 1.05, 1.62)],
                         closed=True, fc=BLUE, ec=INK, lw=LW, zorder=2))  # fmt: skip


def sign(ax):
    """The series' hanging sign, this time saying what the coin means."""
    ax.plot([1.0, 1.0], [4.2, 3.75], color=INK, lw=1.5, zorder=2)
    ax.plot([2.6, 2.6], [4.2, 3.75], color=INK, lw=1.5, zorder=2)
    _box(ax, 0.55, 3.05, 2.5, 0.72, ORANGE, r=0.06)
    ax.text(1.8, 3.41, "ESCALATE", ha="center", va="center", fontsize=15,
            fontweight="bold", color=PAPER, zorder=5)  # fmt: skip
    for x in (1.2, 2.4):  # the card hangs from the sign
        ax.plot([x, x], [3.05, 2.85], color=INK, lw=1.5, zorder=2)
    _box(ax, 0.75, 2.35, 2.1, 0.5, CREAM2, r=0.05)
    ax.text(1.8, 2.6, "= “I don’t know” = 50%", ha="center", va="center",
            fontsize=10.5, color=INK, zorder=5)  # fmt: skip


def main() -> None:
    fig = plt.figure(figsize=(10, 4.2), dpi=100)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 4.2)
    ax.axis("off")
    ax.add_patch(Rectangle((0, 0), 10, 4.2, fc=CREAM, ec="none", zorder=0))
    floor(ax)
    sign(ax)
    ledger(ax)
    robot(ax)
    fig.savefig(HERE / "cover.png", dpi=100, facecolor=CREAM)
    plt.close(fig)
    print("wrote cover.png (1000x420)")


if __name__ == "__main__":
    main()
