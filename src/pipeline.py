"""Collect and prepare Telangana public health facility records."""

from __future__ import annotations

import csv
import json
import re
import ssl
import urllib.parse
import urllib.request
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

import certifi

ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "data" / "raw"
PROCESSED_DIR = ROOT / "data" / "processed"
SERVICE = (
    "https://tgrac.telangana.gov.in/arcgis/rest/services/"
    "GovtHospitals_Folder/Health_Facilities_Mapping/MapServer"
)
LAYERS = {
    7: "Central Medical Stores",
    8: "Medical Colleges",
    9: "District Hospital",
    10: "Area Hospital",
    11: "Civil Dispensary",
    12: "Maternity Community Health Centre",
    13: "Basti Dawakhana",
    14: "Urban Community Health Centre",
    15: "Urban Primary Health Centre",
    16: "Community Health Centre",
    17: "Primary Health Centre",
    18: "Health Sub Centre",
}
FIELDS = [
    "facility_id",
    "facility_name",
    "facility_type",
    "district",
    "mandal",
    "village",
    "latitude",
    "longitude",
    "department",
    "source_layer",
    "record_completeness_pct",
]


def clean_text(value: object) -> str:
    """Return a stable single spaced string for a source value."""
    if value is None:
        return ""
    return re.sub(r"\s+", " ", str(value)).strip()


def normalise_district(value: object) -> str:
    text = clean_text(value).replace("_", " ").title()
    replacements = {"Medchal Malkajgiri": "Medchal–Malkajgiri", "Rangareddy": "Ranga Reddy"}
    return replacements.get(text, text or "Unknown")


def fetch_layer(layer_id: int) -> dict:
    query = urllib.parse.urlencode(
        {"where": "1=1", "outFields": "*", "returnGeometry": "true", "f": "json"}
    )
    request = urllib.request.Request(
        f"{SERVICE}/{layer_id}/query?{query}", headers={"User-Agent": "HarikaDataProject/1.0"}
    )
    context = ssl.create_default_context(cafile=certifi.where())
    with urllib.request.urlopen(request, timeout=60, context=context) as response:  # noqa: S310
        return json.load(response)


def transform_feature(feature: dict, layer_id: int, layer_name: str) -> dict:
    attributes = feature.get("attributes", {})
    geometry = feature.get("geometry", {})
    latitude = attributes.get("Latitude") or geometry.get("y")
    longitude = attributes.get("Longitude") or geometry.get("x")
    row = {
        "facility_id": f"TG-{layer_id}-{attributes.get('OBJECTID', '')}",
        "facility_name": clean_text(attributes.get("Facility_Name")) or "Unnamed facility",
        "facility_type": clean_text(attributes.get("Facility_Type")) or layer_name,
        "district": normalise_district(attributes.get("District") or attributes.get("District_1")),
        "mandal": clean_text(attributes.get("Mandal") or attributes.get("Mandal_1")),
        "village": clean_text(attributes.get("Village")),
        "latitude": round(float(latitude), 6) if latitude not in (None, "") else "",
        "longitude": round(float(longitude), 6) if longitude not in (None, "") else "",
        "department": clean_text(attributes.get("Department")),
        "source_layer": layer_name,
    }
    assessed = ["facility_name", "facility_type", "district", "mandal", "latitude", "longitude"]
    completed = sum(bool(row[field]) and row[field] != "Unknown" for field in assessed)
    row["record_completeness_pct"] = round(100 * completed / len(assessed), 1)
    return row


def deduplicate(rows: list[dict]) -> tuple[list[dict], int]:
    seen: set[tuple] = set()
    clean_rows: list[dict] = []
    for row in rows:
        key = (
            row["facility_name"].casefold(),
            row["district"].casefold(),
            row["latitude"],
            row["longitude"],
        )
        if key in seen:
            continue
        seen.add(key)
        clean_rows.append(row)
    return clean_rows, len(rows) - len(clean_rows)


def build_outputs() -> dict:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    rows: list[dict] = []
    layer_counts: dict[str, int] = {}
    for layer_id, layer_name in LAYERS.items():
        payload = fetch_layer(layer_id)
        (RAW_DIR / f"layer_{layer_id}.json").write_text(
            json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8"
        )
        features = payload.get("features", [])
        layer_counts[layer_name] = len(features)
        rows.extend(transform_feature(item, layer_id, layer_name) for item in features)

    clean_rows, duplicate_count = deduplicate(rows)
    clean_rows.sort(key=lambda item: (item["district"], item["facility_type"], item["facility_name"]))
    with (PROCESSED_DIR / "telangana_health_facilities.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(clean_rows)

    districts = Counter(row["district"] for row in clean_rows if row["district"] != "Unknown")
    mapped = sum(row["latitude"] != "" and row["longitude"] != "" for row in clean_rows)
    complete = sum(row["record_completeness_pct"] >= 83.3 for row in clean_rows)
    summary = {
        "raw_records": len(rows),
        "clean_records": len(clean_rows),
        "duplicates_removed": duplicate_count,
        "districts": len(districts),
        "mapped_records": mapped,
        "mapped_records_pct": round(100 * mapped / len(clean_rows), 1) if clean_rows else 0,
        "records_at_least_83_pct_complete": complete,
        "top_districts": districts.most_common(8),
        "facility_types": Counter(row["facility_type"] for row in clean_rows).most_common(),
        "source_layer_counts": layer_counts,
    }
    (PROCESSED_DIR / "quality_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    manifest = {
        "source": SERVICE,
        "publisher": "Telangana Remote Sensing Applications Centre",
        "retrieved_utc": datetime.now(timezone.utc).isoformat(),
        "layer_ids": list(LAYERS),
        "license_note": "Use is subject to the publisher's terms and source availability.",
    }
    (RAW_DIR / "source_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return summary


if __name__ == "__main__":
    print(json.dumps(build_outputs(), indent=2))
