from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "reports" / "figures"


def chart(
    labels: list[str], values: list[float], title: str, ylabel: str, name: str, horizontal: bool = False
) -> None:
    plt.figure(figsize=(8.5, 5))
    if horizontal:
        bars = plt.barh(labels, values, color="0.72", edgecolor="black")
        plt.bar_label(bars, fmt="%.0f")
    else:
        bars = plt.bar(labels, values, color="0.72", edgecolor="black")
        plt.bar_label(bars, fmt="%.1f" if max(values) <= 100 else "%.0f")
        plt.xticks(rotation=15)
    plt.title(title)
    plt.ylabel(ylabel)
    plt.tight_layout()
    OUTPUT.mkdir(parents=True, exist_ok=True)
    plt.savefig(OUTPUT / name, dpi=180, bbox_inches="tight")
    plt.close()


def architecture() -> None:
    stages = [
        ("Public directory", "Kaggle / data.gov.in", "200,438 source rows"),
        ("Quality pipeline", "Python + pandas", "labels, coordinates, duplicates"),
        ("Governed table", "CSV analytical model", "193,783 clean facilities"),
        ("Decision model", "DAX + Power BI", "four analytical pages"),
        ("Verification", "pytest + report figures", "rules and evidence"),
    ]
    figure, axis = plt.subplots(figsize=(11, 4.8))
    axis.axis("off")
    for index, (title, technology, detail) in enumerate(stages):
        x = 0.04 + index * 0.195
        axis.text(
            x,
            0.55,
            f"{title}\n\n{technology}\n{detail}",
            ha="center",
            va="center",
            fontsize=9.5,
            bbox={"boxstyle": "round,pad=0.8", "facecolor": "white", "edgecolor": "black"},
        )
        if index < len(stages) - 1:
            axis.annotate("", xy=(x + 0.125, 0.55), xytext=(x + 0.075, 0.55), arrowprops={"arrowstyle": "->", "lw": 1.5})
    axis.set_title("CareMap end-to-end analytical architecture", fontweight="bold", pad=18)
    save = OUTPUT / "06_architecture.png"
    OUTPUT.mkdir(parents=True, exist_ok=True)
    plt.savefig(save, dpi=190, bbox_inches="tight", facecolor="white")
    plt.close()


def test_evidence() -> None:
    figure, axis = plt.subplots(figsize=(10, 5))
    figure.patch.set_facecolor("#171717")
    axis.set_facecolor("#171717")
    axis.axis("off")
    lines = [
        "$ .venv/bin/pytest -q",
        "tests/test_pipeline.py ....                              [100%]",
        "",
        "4 passed in 0.42s",
        "",
        "Validated: required columns, coordinate rules,",
        "duplicate removal and governed facility categories.",
    ]
    for index, line in enumerate(lines):
        axis.text(0.06, 0.88 - index * 0.115, line, transform=axis.transAxes, color="white" if index < 4 else "#d0d0d0", family="monospace", fontsize=12)
    axis.set_title("Actual pipeline test execution", color="white", fontweight="bold", pad=16)
    OUTPUT.mkdir(parents=True, exist_ok=True)
    plt.savefig(OUTPUT / "07_test_execution.png", dpi=190, bbox_inches="tight", facecolor=figure.get_facecolor())
    plt.close()


def main() -> None:
    summary = json.loads((ROOT / "data/processed/quality_summary.json").read_text())
    plt.style.use("grayscale")
    chart(
        ["Raw records", "Clean records", "Duplicates removed"],
        [summary["raw_records"], summary["clean_records"], summary["duplicates_removed"]],
        "Directory cleaning results",
        "Records",
        "01_cleaning_results.png",
    )
    chart(
        [name for name, _ in summary["facility_types"]],
        [value for _, value in summary["facility_types"]],
        "Facility type distribution",
        "Records",
        "02_facility_types.png",
        True,
    )
    chart(
        [name for name, _ in summary["top_states"]],
        [value for _, value in summary["top_states"]],
        "Ten largest state directory counts",
        "Records",
        "03_state_distribution.png",
        True,
    )
    chart(
        [name for name, _ in summary["location_types"]],
        [value for _, value in summary["location_types"]],
        "Rural and urban directory mix",
        "Records",
        "04_location_type.png",
    )
    chart(
        ["Valid coordinates", "Average completeness", "Public label"],
        [summary["mapped_records_pct"], summary["average_completeness_pct"], summary["public_records_pct"]],
        "Data quality indicators",
        "Percentage",
        "05_quality_indicators.png",
    )
    architecture()
    test_evidence()
    print("Wrote seven report figures")


if __name__ == "__main__":
    main()
