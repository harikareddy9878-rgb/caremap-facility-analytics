"""Prepare the All India Health Centres Directory for access analysis."""

from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data/raw/geocode_health_centre.csv"
OUTPUT = ROOT / "data/processed/india_health_facilities.csv"
SUMMARY = ROOT / "data/processed/quality_summary.json"

FIELDS = [
    "facility_id",
    "state",
    "district",
    "subdistrict",
    "facility_type",
    "facility_name",
    "facility_address",
    "latitude",
    "longitude",
    "active_flag",
    "notional_physical",
    "location_type",
    "ownership_type",
    "nin",
    "record_completeness_pct",
]


def clean_text(value: object, fallback: str = "Unknown") -> str:
    if value is None or pd.isna(value):
        return fallback
    cleaned = re.sub(r"\s+", " ", str(value)).strip(" ,")
    if not cleaned or cleaned.casefold() in {"na", "n/a", "nan", "null", "none"}:
        return fallback
    return cleaned


def clean_coordinate(value: object, minimum: float, maximum: float) -> float | None:
    try:
        coordinate = float(value)
    except (TypeError, ValueError):
        return None
    return round(coordinate, 6) if minimum <= coordinate <= maximum else None


def normalise_facility_type(value: object) -> str:
    raw = clean_text(value).casefold()
    aliases = {
        "sc": "Sub Centre",
        "sub_cen": "Sub Centre",
        "sub centre": "Sub Centre",
        "sub-center": "Sub Centre",
        "phc": "Primary Health Centre",
        "chc": "Community Health Centre",
        "dh": "District Hospital",
        "dis_h": "District Hospital",
        "s_t_h": "Sub-District Hospital",
    }
    return aliases.get(raw, raw.title() if raw != "unknown" else "Unknown")


def transform_row(row: dict, index: int) -> dict:
    prepared = {
        "facility_id": f"IN-HF-{index:06d}",
        "state": clean_text(row.get("State Name")).replace("Andhra Pradesh Old", "Andhra Pradesh"),
        "district": clean_text(row.get("District Name")),
        "subdistrict": clean_text(row.get("Subdistrict Name")),
        "facility_type": normalise_facility_type(row.get("Facility Type")),
        "facility_name": clean_text(row.get("Facility Name"), "Unnamed facility"),
        "facility_address": clean_text(row.get("Facility Address")),
        "latitude": clean_coordinate(row.get("Latitude"), 6.0, 38.0),
        "longitude": clean_coordinate(row.get("Longitude"), 68.0, 98.0),
        "active_flag": clean_text(row.get("ActiveFlag_C")),
        "notional_physical": clean_text(row.get("NOTIONAL_PHYSICAL")),
        "location_type": clean_text(row.get("Location Type")),
        "ownership_type": clean_text(row.get("Type Of Facility")),
        "nin": clean_text(row.get("Nin_N")),
    }
    assessed = ["state", "district", "subdistrict", "facility_type", "facility_name", "latitude", "longitude", "ownership_type"]
    completed = sum(prepared[field] not in {None, "Unknown", "Unnamed facility"} for field in assessed)
    prepared["record_completeness_pct"] = round(100 * completed / len(assessed), 1)
    return prepared


def deduplicate(rows: list[dict]) -> tuple[list[dict], int]:
    seen: set[tuple] = set()
    clean: list[dict] = []
    for row in rows:
        key = (
            row["state"].casefold(),
            row["district"].casefold(),
            row["facility_name"].casefold(),
            row["facility_type"].casefold(),
            row["latitude"],
            row["longitude"],
        )
        if key in seen:
            continue
        seen.add(key)
        clean.append(row)
    return clean, len(rows) - len(clean)


def build_outputs() -> dict:
    source = pd.read_csv(RAW, low_memory=False)
    rows = [transform_row(record, index) for index, record in enumerate(source.to_dict("records"), 1)]
    clean, duplicates = deduplicate(rows)
    frame = pd.DataFrame(clean, columns=FIELDS).sort_values(
        ["state", "district", "facility_type", "facility_name"]
    )
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(OUTPUT, index=False)
    mapped = int(frame["latitude"].notna().mul(frame["longitude"].notna()).sum())
    public = int(frame["ownership_type"].str.contains("public", case=False, na=False).sum())
    summary = {
        "raw_records": int(len(source)),
        "clean_records": int(len(frame)),
        "duplicates_removed": int(duplicates),
        "states_and_union_territories": int(frame["state"].nunique()),
        "districts": int(frame[["state", "district"]].drop_duplicates().shape[0]),
        "mapped_records": mapped,
        "mapped_records_pct": round(100 * mapped / len(frame), 1),
        "public_records": public,
        "public_records_pct": round(100 * public / len(frame), 1),
        "average_completeness_pct": round(float(frame["record_completeness_pct"].mean()), 1),
        "top_states": Counter(frame["state"]).most_common(10),
        "facility_types": Counter(frame["facility_type"]).most_common(),
        "location_types": Counter(frame["location_type"]).most_common(),
    }
    SUMMARY.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return summary


if __name__ == "__main__":
    print(json.dumps(build_outputs(), indent=2))
