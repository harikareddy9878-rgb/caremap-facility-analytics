# Telangana Public Health Facility Analytics

This project turns an official Telangana government health facility map service into a clean analytical dataset and a decision focused dashboard. It examines where public facilities are recorded, which facility types dominate, and where incomplete location fields could weaken planning analysis.

![Dashboard overview](evidence/facility_dashboard.png)

## Problem

Facility records are published across separate map layers. That format is useful for geographic display, but it is not ready for routine analysis. A planner must first combine the layers, standardise district and facility names, remove duplicates, and measure missing values.

## Root cause addressed

The raw source separates each facility category into its own endpoint and contains inconsistent null values. Without a repeatable preparation step, totals can differ between analyses and data quality problems stay hidden.

## Purpose

The project creates one reproducible facility table, a compact KPI dashboard, reusable Power BI measures, and a written analysis report. It is an educational analysis of published records and is not a measure of clinical quality or live capacity.

## Results

The pipeline records the source layer for every row, preserves the raw API responses, removes exact duplicate facilities, and publishes a quality summary. The dashboard shows total facilities, district coverage, mapped coordinates, facility type mix, district concentration, and completeness.

## Repository guide

| Folder | Contents |
| --- | --- |
| `data/raw` | Source responses from the Telangana government ArcGIS service |
| `data/processed` | Clean facility table and quality summary |
| `src` | Collection, cleaning, validation, and dashboard code |
| `dashboards` | Power BI model notes and DAX measures |
| `evidence` | Generated dashboard image |
| `reports` | Detailed project report in PDF format |
| `tests` | Data transformation checks |

## Reproduce

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python src/pipeline.py
python src/dashboard.py
python scripts/build_report.py
pytest
ruff check src scripts tests
```

The source is the [Telangana Remote Sensing Applications Centre Health Facilities Mapping service](https://tgrac.telangana.gov.in/arcgis/rest/services/GovtHospitals_Folder/Health_Facilities_Mapping/MapServer). The extraction date is stored in `data/raw/source_manifest.json`.

## Author

Harika

