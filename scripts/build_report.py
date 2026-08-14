from __future__ import annotations

import json
from pathlib import Path

from report_template import build_research_report

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "reports/CareMap_Facility_Analytics_Report.pdf"
FIGURES = ROOT / "reports/figures"


def build_report() -> Path:
    summary = json.loads((ROOT / "data/processed/quality_summary.json").read_text())
    sections = [
        {
            "title": "Project overview and problem statement",
            "paragraphs": [
                "CareMap turns a historical national health-centre directory into a governed facility-level analytical table and Power BI implementation plan. I built it because a large directory can still contain duplicates, invalid coordinates, old geography labels, and inconsistent facility types that distort maps and counts.",
                "The analytical purpose is to compare the distribution and quality of published facility records while keeping the source date visible. The result is not a current service locator and does not measure staffing, beds, medicine availability, clinical quality, or patient access.",
            ],
        },
        {
            "title": "Source and preparation method",
            "paragraphs": [
                "The project downloads the All India Health Centres Directory from Kaggle. Its description attributes the data to data.gov.in and dates the snapshot to 7 October 2016. That historical date is a central interpretation constraint.",
                "I standardised nulls and five facility categories, merged an outdated Andhra Pradesh label, validated coordinates against a broad India range, calculated field completeness, and removed exact duplicate signatures using location and facility attributes.",
            ],
            "table": [
                ["Measure", "Result"],
                ["Raw records", f"{summary['raw_records']:,}"],
                ["Clean records", f"{summary['clean_records']:,}"],
                ["Duplicates removed", f"{summary['duplicates_removed']:,}"],
                ["State and union territory labels", str(summary["states_and_union_territories"])],
                ["State-district combinations", str(summary["districts"])],
            ],
        },
        {
            "title": "Analytical and Power BI design",
            "paragraphs": [
                "The clean table preserves facility name, type, ownership, location type, state, district, subdistrict, address, coordinates, activity fields, and record completeness. Reusable DAX measures calculate facility count, geography coverage, mapped percentage, public-label percentage, and average completeness.",
                "The four Power BI pages cover national overview, geographic exploration, state comparison, and data quality. Counts are always described as directory records rather than current capacity.",
            ],
        },
        {
            "title": "Experiment 1: cleaning results",
            "figure": FIGURES / "01_cleaning_results.png",
            "caption": "Figure 1. Raw records, clean records, and removed duplicate signatures.",
            "explanation": [
                [
                    "What I tested",
                    "Whether the signature rule identifies exact repeated facilities without collapsing similarly named facilities in different places.",
                ],
                [
                    "What the graph shows",
                    f"The pipeline removes {summary['duplicates_removed']:,} duplicates and retains {summary['clean_records']:,} clean rows.",
                ],
                [
                    "Conclusion",
                    "Deduplication changes the national total materially and must occur before dashboard aggregation.",
                ],
            ],
        },
        {
            "title": "Experiment 2: facility type distribution",
            "figure": FIGURES / "02_facility_types.png",
            "caption": "Figure 2. Clean directory records by standardised facility type.",
            "explanation": [
                [
                    "What I tested",
                    "How the five governed facility categories contribute to the national directory.",
                ],
                [
                    "What the graph shows",
                    "Sub Centres dominate, followed by Primary Health Centres; hospitals form a much smaller share.",
                ],
                [
                    "Conclusion",
                    "State totals mainly describe lower-level facilities, so facility type must remain visible in comparisons.",
                ],
            ],
        },
        {
            "title": "Experiment 3: state distribution",
            "figure": FIGURES / "03_state_distribution.png",
            "caption": "Figure 3. Ten largest state directory counts in the historical snapshot.",
            "explanation": [
                ["What I tested", "Whether directory records are evenly distributed across states."],
                [
                    "What the graph shows",
                    "Uttar Pradesh has the largest count, followed by Rajasthan and Maharashtra.",
                ],
                [
                    "Conclusion",
                    "The ranking describes source coverage and administrative scale, not health need or per-person access.",
                ],
            ],
        },
        {
            "title": "Experiment 4: rural and urban mix",
            "figure": FIGURES / "04_location_type.png",
            "caption": "Figure 4. Directory records by source location-type label.",
            "explanation": [
                ["What I tested", "How the source labels facilities across rural and urban settings."],
                [
                    "What the graph shows",
                    "The directory is overwhelmingly rural, with only 8,420 urban records and two unusual Public labels.",
                ],
                [
                    "Conclusion",
                    "The location field requires governance, and the dataset is not balanced for general urban-versus-rural capacity claims.",
                ],
            ],
        },
        {
            "title": "Experiment 5: data quality indicators",
            "figure": FIGURES / "05_quality_indicators.png",
            "caption": "Figure 5. Coordinate, completeness, and public-label quality measures.",
            "explanation": [
                [
                    "What I tested",
                    "Whether the clean records contain the core fields required for mapping and segmentation.",
                ],
                [
                    "What the graph shows",
                    f"Valid coordinates are {summary['mapped_records_pct']} percent and average completeness is {summary['average_completeness_pct']} percent.",
                ],
                [
                    "Conclusion",
                    "Field presence is strong, but it does not prove that historical coordinates or ownership labels remain current.",
                ],
            ],
        },
        {
            "title": "Results and interpretation",
            "paragraphs": [
                f"The final table contains {summary['clean_records']:,} records across {summary['states_and_union_territories']} state and union territory labels and {summary['districts']} state-district combinations. {summary['mapped_records']:,} rows contain coordinates inside the broad validation range.",
                "The largest facility type is Sub Centre. Uttar Pradesh has the largest directory count. These findings describe a 2016 snapshot and should not be converted into statements about current service quality, utilisation, staffing, or population access.",
            ],
        },
        {
            "title": "Limitations and reproducibility",
            "paragraphs": [
                "The dataset is old, largely public-facility focused, and lacks current verification, population denominators, road networks, travel time, beds, staff, services, and outcomes. Coordinate presence is not independent location validation.",
                "The repository versions the acquisition, cleaning pipeline, quality summary, dashboard generator, DAX, tests, five figures, and this report. A future study should obtain a current authoritative register, validate a geographic sample, join compatible population data, and calculate travel-time coverage for a carefully defined service level.",
            ],
        },
        {
            "title": "Conclusion",
            "paragraphs": [
                "CareMap demonstrates that facility analytics must begin with source age, duplicates, geography labels, coordinate rules, and interpretation boundaries. I produced a clean national table, auditable quality metrics, five evidence figures, and a Power BI plan while avoiding the unsupported claim that a historical directory measures present healthcare access."
            ],
        },
    ]
    return build_research_report(
        OUTPUT,
        "CareMap Facility Analytics",
        "Harika",
        [
            "This report documents the preparation and analysis of a historical national health-centre directory containing 200,438 records. I standardised facility types and geography labels, validated coordinates, measured field completeness, removed 6,655 exact duplicate signatures, and created a 193,783-row analytical table.",
            "Five experiments examine data cleaning, facility type distribution, state concentration, rural and urban labels, and quality indicators. The project supplies a four-page Power BI design while clearly separating historical directory coverage from current healthcare capacity or access.",
        ],
        "health facility directory; data quality; geospatial analysis; Power BI; public health data",
        sections,
    )


if __name__ == "__main__":
    print(build_report())
