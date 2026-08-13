"""Download the All India Health Centres Directory from Kaggle."""

from __future__ import annotations

import io
import json
import ssl
import urllib.request
import zipfile
from pathlib import Path

import certifi

ROOT = Path(__file__).resolve().parents[1]
SOURCE_URL = "https://www.kaggle.com/api/v1/datasets/download/akshatuppal/all-india-health-centres-directory"
SOURCE_PAGE = "https://www.kaggle.com/datasets/akshatuppal/all-india-health-centres-directory"
RAW_CSV = ROOT / "data/raw/geocode_health_centre.csv"
MANIFEST = ROOT / "data/raw/source_manifest.json"


def acquire() -> dict:
    request = urllib.request.Request(SOURCE_URL, headers={"User-Agent": "HarikaHealthAnalytics/2.0"})
    context = ssl.create_default_context(cafile=certifi.where())
    with urllib.request.urlopen(request, timeout=180, context=context) as response:  # noqa: S310
        archive = zipfile.ZipFile(io.BytesIO(response.read()))
    payload = archive.read("geocode_health_centre.csv")
    RAW_CSV.parent.mkdir(parents=True, exist_ok=True)
    RAW_CSV.write_bytes(payload)
    rows = payload.count(b"\n") - 1
    summary = {
        "source": SOURCE_PAGE,
        "upstream": "Open Government Data Platform India",
        "license": "CC0 as stated on the Kaggle dataset page",
        "snapshot_note": "Directory described as at 7 October 2016; not a live operating-status feed.",
        "raw_rows": rows,
        "file": "geocode_health_centre.csv",
    }
    MANIFEST.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return summary


if __name__ == "__main__":
    print(json.dumps(acquire(), indent=2))
