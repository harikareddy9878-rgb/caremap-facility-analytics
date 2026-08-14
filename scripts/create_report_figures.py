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
    print("Wrote five report figures")


if __name__ == "__main__":
    main()
