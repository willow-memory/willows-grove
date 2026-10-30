"""The three figures for posts/one-day.md, regenerated from their sources.

    python make_figures.py --willow PATH   # PATH: a clone of willow-memory/Willow holding eaa88b2

Each writes a .png beside this file (needs matplotlib and git).

fig1  add-ons built through the day: "N of M built" in ADDONS.md at each commit on Willow
      main's first-parent line, from e3fb64e (the last before 2026-10-29 07:00 UTC) to
      eaa88b2 (PR 100's merge), times in UTC.
fig2  built add-ons by section, before (e3fb64e) and added in the day (eaa88b2 less
      e3fb64e), from ADDONS.md's pools table at each.
fig3  known-gaps phase 2 (demo/known-gaps/README.md at eaa88b2, "The gates"): questions with
      a line hit in the top 10, against what chance gives. Copied as published.

Palette: the dataviz reference palette's light categorical slots 1-2 (blue, orange),
validated with validate_palette.js, light, all checks pass; "before" is the neutral muted
ink, named in the legend. Text in text inks, never series colors.
"""

from __future__ import annotations

import argparse
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.dates as mdates  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402

HERE = Path(__file__).resolve().parent
SURFACE, INK, INK2, MUTED, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#8a8984", "#e6e5e1"
BLUE, ORANGE, BEFORE = "#2a78d6", "#eb6834", "#c9c8c3"
START, END = "e3fb64e", "eaa88b2"

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


def git(willow: Path, *args: str) -> str:
    return subprocess.run(["git", "-C", str(willow), *args], check=True,
                          capture_output=True, text=True).stdout  # fmt: skip


def built(willow: Path, rev: str) -> int:
    m = re.search(r"(\d+) of \d+ built", git(willow, "show", f"{rev}:ADDONS.md"))
    return int(m.group(1))


def pools(willow: Path, rev: str) -> dict[str, int]:
    text = git(willow, "show", f"{rev}:ADDONS.md")
    block = text.split("<!-- willow:pools -->", 1)[1].split(
        "<!-- /willow:pools -->", 1
    )[0]
    return {m.group(1): int(m.group(2))
            for m in re.finditer(r"^\| ([A-Z][^|]+?) \| (\d+) \|", block, re.M)}  # fmt: skip


def _save(fig, name: str) -> None:
    fig.savefig(HERE / name, dpi=200, bbox_inches="tight", pad_inches=0.25)
    plt.close(fig)


def fig1(willow: Path) -> None:
    rows = git(
        willow,
        "log",
        "--first-parent",
        "--reverse",
        "--format=%h %cI",
        f"{START}^..{END}",
    )
    pts = []
    for line in rows.split("\n"):
        if line.strip():
            h, t = line.split()
            pts.append(
                (datetime.fromisoformat(t).astimezone(timezone.utc), built(willow, h))
            )
    xs, ys = [p[0] for p in pts], [p[1] for p in pts]
    fig, ax = plt.subplots(figsize=(9, 4.2))
    ax.step(xs, ys, where="post", color=BLUE, linewidth=2)
    ax.plot(
        xs[-1:],
        ys[-1:],
        "o",
        color=BLUE,
        markersize=8,
        markeredgecolor=SURFACE,
        markeredgewidth=2,
    )
    ax.annotate(
        f"{ys[0]} built",
        (xs[0], ys[0]),
        xytext=(0, -18),
        textcoords="offset points",
        color=INK2,
    )
    ax.annotate(f"{ys[-1]} built", (xs[-1], ys[-1]), xytext=(-12, 10), textcoords="offset points",
                color=INK, ha="right", fontweight="bold")  # fmt: skip
    ax.set_title(f"Willow's add-ons built through one day: {ys[0]} to {ys[-1]}")
    ax.set_ylabel("add-ons built")
    ax.xaxis.set_major_locator(
        mdates.HourLocator(byhour=[0, 6, 12, 18], tz=timezone.utc)
    )
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%a %H:%M", tz=timezone.utc))
    ax.set_xlabel("UTC")
    ax.set_ylim(ys[0] - 20, ys[-1] + 15)
    ax.grid(axis="y", color=GRID, linewidth=1)
    ax.set_axisbelow(True)
    _save(fig, "fig1-day.png")


def fig2(willow: Path) -> None:
    before, after = pools(willow, START), pools(willow, END)
    names = list(after)[::-1]
    b = [before[n] for n in names]
    added = [after[n] - before[n] for n in names]
    fig, ax = plt.subplots(figsize=(9, 5.2))
    ax.barh(names, b, color=BEFORE, height=0.62, label="built before the day")
    ax.barh(
        names,
        added,
        left=[x + 0.6 for x in b],
        color=BLUE,
        height=0.62,
        label="built in the day",
    )
    for i, (x, a) in enumerate(zip(b, added)):
        if a:
            ax.text(x + a + 1.6, i, f"+{a}", va="center", color=INK, fontsize=10)
    ax.set_title(f"Where the {sum(added)} new add-ons went, by section")
    ax.set_xlabel("add-ons built")
    ax.legend(frameon=False, loc="lower right")
    ax.grid(axis="x", color=GRID, linewidth=1)
    ax.set_axisbelow(True)
    _save(fig, "fig2-sections.png")


def fig3() -> None:
    groups = ["strong gaps\n(160 questions)", "weaker gaps\n(64 questions)"]
    found, chance = [44, 3], [5.55, 0.16]
    fig, ax = plt.subplots(figsize=(9, 3.6))
    ys = [1, 0]
    ax.barh(
        [y + 0.18 for y in ys],
        found,
        height=0.32,
        color=BLUE,
        label="found the fixed lines in the top 10",
    )
    ax.barh(
        [y - 0.18 for y in ys],
        chance,
        height=0.32,
        color=ORANGE,
        label="what chance gives",
    )
    for y, f, c in zip(ys, found, chance):
        ax.text(f + 0.8, y + 0.18, f"{f}", va="center", color=INK, fontweight="bold")
        ax.text(c + 0.8, y - 0.18, f"{c:g}", va="center", color=INK2)
    ax.set_yticks(ys, groups)
    ax.set_title("known-gaps, asked of the whole old tree: far above chance")
    ax.set_xlabel("questions")
    ax.set_xlim(0, 52)
    ax.legend(frameon=False, loc="lower right")
    ax.grid(axis="x", color=GRID, linewidth=1)
    ax.set_axisbelow(True)
    _save(fig, "fig3-known-gaps.png")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--willow", type=Path, required=True)
    w = p.parse_args().willow
    fig1(w)
    fig2(w)
    fig3()
