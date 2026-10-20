"""The four figures for posts/ledger.md, regenerated from their sources.

    python make_figures.py        # writes fig1..fig4 .png beside this file (needs matplotlib)

fig1  the Day 3 table's false confidence on each model's worst shape (posts/day-3.md;
      Kart XS5M7Y76, SWLBE2MH; Haiku N8ZMLM20, WR59LN7Y). Copied as published.
fig2  the Brier score, (p - outcome)^2, for both outcomes: arithmetic, no data.
fig3  the ledger's commitment window (willow-bot market.py: DEADLINE_UTC = 13; drand
      PERIOD = 30 s in beacon.py). New York's open and close are 13:30/20:00 UTC in
      summer time and 14:30/21:00 UTC in winter time.
fig4  a SIMULATION, seeded (SEED below): 100 coin-flip outcomes, one caller who says 80%
      on every call, and the coin who says 50%. Not market data and not a real record.

Palette: the dataviz reference palette's light categorical slots 1-3 (validated with
validate_palette.js, light, all checks pass), text in text inks, never series colors.
"""

from __future__ import annotations

import random
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

HERE = Path(__file__).resolve().parent
SURFACE, INK, INK2, MUTED, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#8a8984", "#e6e5e1"
BLUE, ORANGE, AQUA = "#2a78d6", "#eb6834", "#1baf7a"
SEED = 20261020

plt.rcParams.update(
    {
        "figure.facecolor": SURFACE,
        "axes.facecolor": SURFACE,
        "savefig.facecolor": SURFACE,
        "font.family": "DejaVu Sans",
        "font.size": 11,
        "text.color": INK,
        "axes.edgecolor": GRID,
        "axes.labelcolor": INK2,
        "xtick.color": INK2,
        "ytick.color": INK2,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.titlesize": 14,
        "axes.titleweight": "bold",
        "axes.titlelocation": "left",
    }
)


def _save(fig, name: str) -> None:
    fig.savefig(HERE / name, dpi=200, bbox_inches="tight", pad_inches=0.25)
    plt.close(fig)


def fig1() -> None:
    """False confidence on each model's worst shape, Day 3."""
    rows = [  # (model, false confidence on the worst shape), the Day 3 table
        ("Gemini 3.7 Flash", 0.00), ("Gemini 3.1 Pro", 0.00), ("Claude Sonnet 5", 0.10),
        ("Claude Opus 5", 0.10), ("Gemini 3.8 Flash", 0.00), ("GPT-5.5", 0.00),
        ("Qwen3 235B Instruct", 0.25), ("Claude Haiku 4.5 †", 0.90), ("Gemma 4 26B", 0.08),
        ("gpt-oss-20b", 0.20), ("DeepSeek-R1", 0.00), ("GPT-5.4 nano", 0.20),
    ]  # fmt: skip
    rows.sort(key=lambda r: r[1])
    fig, ax = plt.subplots(figsize=(8, 5.6))
    y = range(len(rows))
    ax.barh(list(y), [r[1] for r in rows], height=0.62, color=BLUE, zorder=2)
    for i, (_, v) in enumerate(rows):
        ax.text(v + 0.015, i, "0.00" if v == 0 else f"{v:.2f}", va="center",
                fontsize=10, color=INK if v >= 0.5 else INK2)  # fmt: skip
    ax.set_yticks(list(y), [r[0] for r in rows])
    ax.set_xlim(0, 1.0)
    ax.xaxis.grid(True, color=GRID, zorder=0)
    ax.set_xlabel("Answered anyway when ESCALATE was the only right reply")
    ax.set_title("The floor, not the average")
    fig.text(0.0, -0.04, "Worst of four shapes per model; 0.00 means it never answered when it "
             "should have stopped.\n† Haiku 4.5: route unmeasured (every call errored), so "
             "three shapes. Source: Day 3 table.", fontsize=9, color=MUTED)  # fmt: skip
    _save(fig, "fig1-floor.png")


def fig2() -> None:
    """Brier score against the stated probability, for both outcomes."""
    ps = [i / 100 for i in range(101)]
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(ps, [(p - 1) ** 2 for p in ps], color=BLUE, lw=2, zorder=3)
    ax.plot(ps, [p**2 for p in ps], color=ORANGE, lw=2, zorder=3)
    ax.scatter([0.5], [0.25], s=90, color=SURFACE, edgecolor=INK, lw=2, zorder=4)
    ax.annotate("50% — the coin\nscores 0.25 either way", (0.5, 0.25), (0.53, 0.47),
                fontsize=10, color=INK,
                arrowprops={"arrowstyle": "-", "color": MUTED, "lw": 1})  # fmt: skip
    ax.plot([0.26, 0.30], [0.95, 0.95], color=BLUE, lw=2)
    ax.text(0.315, 0.95, "it happened", color=INK2, fontsize=10, va="center")
    ax.plot([0.52, 0.56], [0.95, 0.95], color=ORANGE, lw=2)
    ax.text(0.575, 0.95, "it didn't", color=INK2, fontsize=10, va="center")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1.0)
    ax.yaxis.grid(True, color=GRID, zorder=0)
    ax.set_xlabel("The probability you gave that it would happen")
    ax.set_ylabel("Brier score (lower is better)")
    ax.set_title("Saying “I don’t know” has a price, and it’s fixed")
    fig.text(0.0, -0.03, "Brier = (p − outcome)²: a confident miss costs up to 1.00; "
             "a 50% call always costs 0.25.", fontsize=9, color=MUTED)  # fmt: skip
    _save(fig, "fig2-brier.png")


def fig3() -> None:
    """The commitment window on a close date, in UTC."""
    fig, ax = plt.subplots(figsize=(9, 3.4))
    ax.set_xlim(-6, 24)
    ax.set_ylim(0, 4)
    ax.axis("off")
    ax.plot([-6, 24], [1.2, 1.2], color=INK2, lw=1)
    for h in range(-6, 25, 3):
        ax.plot([h, h], [1.1, 1.3], color=INK2, lw=1)
        label = f"{h % 24:02d}:00" + ("\nday before" if h < 0 else "")
        ax.text(h, 0.75, label, ha="center", va="top", fontsize=8.5, color=INK2)
    ax.axvspan(-6, 13, ymin=0.33, ymax=0.62, color=BLUE, alpha=0.16, lw=0)
    ax.text(
        3.5, 1.85, "call + seal must land here", ha="center", fontsize=10.5, color=INK
    )
    ax.plot([13, 13], [1.2, 3.3], color=INK, lw=2)
    ax.text(13, 3.45, "deadline 13:00 UTC", ha="center", fontsize=10, color=INK,
            fontweight="bold")  # fmt: skip
    for x0, x1, y, txt in ((13.5, 20, 2.45, "open, summer: 13:30–20:00"),
                           (14.5, 21, 1.75, "open, winter: 14:30–21:00")):  # fmt: skip
        ax.plot([x0, x1], [y, y], color=ORANGE, lw=6, solid_capstyle="round")
        ax.text((x0 + x1) / 2 + 0.6, y + 0.22, txt, ha="center", va="bottom", fontsize=9,
                color=INK2)  # fmt: skip
    ax.annotate("resolve:\nread the close", (22.8, 1.3), (22.8, 3.3), ha="center",
                fontsize=9, color=INK2,
                arrowprops={"arrowstyle": "->", "color": MUTED, "lw": 1})  # fmt: skip
    ax.set_title("Committed before the market could be known (times in UTC)")
    fig.text(0.0, -0.06, "The clock is drand's, not the computer's: a round every 30 s, and "
             "round N's time is fixed by N. Open: New York, summer and winter time.\nThe call and the seal each record drand's newest "
             "round; the round after it must fire before 13:00 UTC.", fontsize=9,
             color=MUTED)  # fmt: skip
    _save(fig, "fig3-window.png")


def fig4() -> None:
    """A seeded simulation: an always-80% caller against the coin on coin flips."""
    rng = random.Random(SEED)
    outcomes = [rng.random() < 0.5 for _ in range(100)]
    loud = [(0.8 - (1 if o else 0)) ** 2 for o in outcomes]
    coin = [0.25] * len(outcomes)

    def running(xs):
        out, tot = [], 0.0
        for i, x in enumerate(xs, 1):
            tot += x
            out.append(tot / i)
        return out

    n = range(1, len(outcomes) + 1)
    hits = [x for x, o in zip(loud, outcomes) if o]
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(n, running(loud), color=ORANGE, lw=2, zorder=3)
    ax.plot(n, running(coin), color=BLUE, lw=2, zorder=3)
    ax.plot(
        n, [sum(hits) / len(hits)] * len(n), color=AQUA, lw=2, ls=(0, (4, 3)), zorder=3
    )
    last = len(outcomes)
    ax.text(last + 1.5, running(loud)[-1], "the 80% caller,\nevery call counted",
            va="center", fontsize=9.5, color=INK)  # fmt: skip
    ax.text(last + 1.5, 0.25, "the coin (50%)", va="center", fontsize=9.5, color=INK)
    ax.text(last + 1.5, hits[0], "the same caller,\nhits only", va="center", fontsize=9.5,
            color=INK)  # fmt: skip
    ax.set_xlim(1, last)
    ax.set_ylim(0, 0.7)
    ax.yaxis.grid(True, color=GRID, zorder=0)
    ax.set_xlabel("Calls made")
    ax.set_ylabel("Average Brier score so far (lower is better)")
    ax.set_title("The highlight reel and the ledger")
    fig.text(0.0, -0.04, f"Simulated, not market data: 100 coin-flip outcomes (seed {SEED}). "
             f"{sum(outcomes)} hits, {last - sum(outcomes)} misses.\nShow only the hits and the "
             "loud caller looks brilliant; count every call and it loses to the coin.",
             fontsize=9, color=MUTED)  # fmt: skip
    _save(fig, "fig4-reel.png")


if __name__ == "__main__":
    for f in (fig1, fig2, fig3, fig4):
        f()
    print("wrote", ", ".join(sorted(p.name for p in HERE.glob("fig*.png"))))
