"""Render a Power BI style analytical evidence page."""

from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

ROOT = Path(__file__).resolve().parents[1]


def load_rows() -> list[dict]:
    with (ROOT / "data/processed/telangana_health_facilities.csv").open(encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def draw_kpi(ax, x: float, value: str, label: str, colour: str) -> None:
    ax.add_patch(FancyBboxPatch((x, 0.79), 0.205, 0.135, boxstyle="round,pad=0.012", facecolor="#ffffff", edgecolor="#d7e2de"))
    ax.text(x + 0.018, 0.86, value, fontsize=20, weight="bold", color=colour)
    ax.text(x + 0.018, 0.815, label, fontsize=9, color="#53615d")


def build_dashboard() -> Path:
    rows = load_rows()
    summary = json.loads((ROOT / "data/processed/quality_summary.json").read_text())
    types = Counter(row["facility_type"] for row in rows).most_common(7)
    districts = Counter(row["district"] for row in rows if row["district"] != "Unknown").most_common(8)

    fig = plt.figure(figsize=(16, 9), facecolor="#f3f7f5")
    canvas = fig.add_axes((0, 0, 1, 1))
    canvas.axis("off")
    canvas.text(0.045, 0.965, "TELANGANA PUBLIC HEALTH FACILITY OVERVIEW", fontsize=19, weight="bold", color="#143d35", va="top")
    canvas.text(0.045, 0.93, "Published facility records • geographic coverage • data quality", fontsize=10, color="#64736e")
    draw_kpi(canvas, 0.045, f"{len(rows):,}", "Clean facility records", "#087f5b")
    draw_kpi(canvas, 0.285, str(summary["districts"]), "Districts represented", "#16697a")
    draw_kpi(canvas, 0.525, f"{summary['mapped_records_pct']}%", "Records with coordinates", "#b66d0d")
    draw_kpi(canvas, 0.765, str(len(summary["facility_types"])), "Facility categories", "#7048a8")

    ax1 = fig.add_axes((0.06, 0.39, 0.42, 0.33), facecolor="white")
    labels, values = zip(*reversed(types))
    ax1.barh(labels, values, color="#1f9d78")
    ax1.set_title("Facility mix", loc="left", weight="bold", color="#24312e")
    ax1.spines[["top", "right", "left"]].set_visible(False)
    ax1.tick_params(axis="y", labelsize=8, length=0)
    ax1.grid(axis="x", color="#e8efec")
    ax1.set_axisbelow(True)

    ax2 = fig.add_axes((0.55, 0.39, 0.39, 0.33), facecolor="white")
    dlabels, dvalues = zip(*reversed(districts))
    ax2.barh(dlabels, dvalues, color="#397d91")
    ax2.set_title("Districts with most records", loc="left", weight="bold", color="#24312e")
    ax2.spines[["top", "right", "left"]].set_visible(False)
    ax2.tick_params(axis="y", labelsize=8, length=0)
    ax2.grid(axis="x", color="#e8efec")
    ax2.set_axisbelow(True)

    quality = [summary["mapped_records_pct"], round(100 * summary["records_at_least_83_pct_complete"] / max(len(rows), 1), 1)]
    ax3 = fig.add_axes((0.06, 0.09, 0.42, 0.19), facecolor="white")
    ax3.barh(["Coordinates present", "Core fields complete"], quality, color=["#d98923", "#7d5bb3"])
    ax3.set_xlim(0, 100)
    ax3.set_title("Record quality", loc="left", weight="bold", color="#24312e")
    ax3.spines[["top", "right", "left"]].set_visible(False)
    ax3.tick_params(axis="y", labelsize=9, length=0)
    ax3.grid(axis="x", color="#e8efec")

    canvas.add_patch(FancyBboxPatch((0.54, 0.08), 0.405, 0.21, boxstyle="round,pad=0.012", facecolor="#143d35", edgecolor="#143d35"))
    canvas.text(0.565, 0.255, "ANALYSIS NOTE", fontsize=10, weight="bold", color="#a8e0cf")
    canvas.text(0.565, 0.215, "Counts describe published map records, not live bed capacity.", fontsize=11, color="white")
    canvas.text(0.565, 0.18, "Missing fields are made visible before geographic comparison.", fontsize=11, color="white")
    canvas.text(0.565, 0.135, f"{summary['duplicates_removed']} exact duplicate records removed", fontsize=10, color="#d8ebe5")
    canvas.text(0.565, 0.105, "Source: TGRAC Health Facilities Mapping service", fontsize=9, color="#b8ccc6")

    output = ROOT / "evidence/facility_dashboard.png"
    output.parent.mkdir(exist_ok=True)
    fig.savefig(output, dpi=180, bbox_inches="tight")
    plt.close(fig)
    return output


if __name__ == "__main__":
    print(build_dashboard())

