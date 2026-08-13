"""Build the project report as a ten page PDF."""

from __future__ import annotations

import csv
import json
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    Image,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "reports/Telangana_Public_Health_Facility_Analytics_Report.pdf"
GREEN = colors.HexColor("#143d35")
TEAL = colors.HexColor("#087f5b")
PALE = colors.HexColor("#eef5f2")


def page_number(canvas, document):
    canvas.saveState()
    canvas.setFillColor(colors.HexColor("#60706a"))
    canvas.setFont("Helvetica", 8)
    canvas.drawString(2 * cm, 1.2 * cm, "Telangana Public Health Facility Analytics")
    canvas.drawRightString(19 * cm, 1.2 * cm, f"Page {document.page}")
    canvas.restoreState()


def read_data():
    with (ROOT / "data/processed/telangana_health_facilities.csv").open(encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    summary = json.loads((ROOT / "data/processed/quality_summary.json").read_text())
    return rows, summary


def build_report() -> Path:
    rows, summary = read_data()
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="Cover", parent=styles["Title"], fontName="Helvetica-Bold", fontSize=27, leading=33, textColor=GREEN, alignment=TA_CENTER, spaceAfter=20))
    styles.add(ParagraphStyle(name="Section", parent=styles["Heading1"], fontName="Helvetica-Bold", fontSize=20, leading=25, textColor=GREEN, spaceAfter=14))
    styles.add(ParagraphStyle(name="Sub", parent=styles["Heading2"], fontSize=12, leading=16, textColor=TEAL, spaceBefore=10, spaceAfter=6))
    styles.add(ParagraphStyle(name="Body2", parent=styles["BodyText"], fontSize=10, leading=15, textColor=colors.HexColor("#303c38"), spaceAfter=9))
    styles.add(ParagraphStyle(name="Small", parent=styles["BodyText"], fontSize=8.5, leading=12, textColor=colors.HexColor("#52605b")))

    doc = SimpleDocTemplate(str(OUTPUT), pagesize=A4, rightMargin=2 * cm, leftMargin=2 * cm, topMargin=1.8 * cm, bottomMargin=1.8 * cm, title="Telangana Public Health Facility Analytics", author="Harika", subject="End to end data analytics project report")
    story = []

    story.extend([
        Spacer(1, 3.2 * cm),
        Paragraph("Telangana Public Health<br/>Facility Analytics", styles["Cover"]),
        Paragraph("From published geospatial layers to a clean decision dashboard", ParagraphStyle(name="CoverSub", parent=styles["Body2"], fontSize=14, leading=20, alignment=TA_CENTER, textColor=TEAL)),
        Spacer(1, 1.2 * cm),
        Table([["Project type", "Data analytics and Power BI preparation"], ["Geography", "Telangana, India"], ["Source", "TGRAC Health Facilities Mapping service"], ["Prepared by", "Harika"]], colWidths=[4 * cm, 9 * cm], style=TableStyle([("BACKGROUND", (0, 0), (0, -1), PALE), ("TEXTCOLOR", (0, 0), (0, -1), GREEN), ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"), ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#ccdcd6")), ("PADDING", (0, 0), (-1, -1), 9)])),
        Spacer(1, 1.2 * cm),
        Paragraph("This report documents the source, preparation logic, dashboard design, findings, limitations, and reproducibility checks.", styles["Body2"]),
        PageBreak(),
    ])

    story.extend([
        Paragraph("1. Executive summary", styles["Section"]),
        Paragraph("Public health facility locations are available through separate map layers. The project combines those layers into one analysis table so that counts, geographic coverage, facility type mix, and record completeness can be examined consistently.", styles["Body2"]),
        Table([["Clean records", f"{summary['clean_records']:,}"], ["Districts represented", str(summary["districts"])], ["Coordinates present", f"{summary['mapped_records_pct']}%"], ["Exact duplicates removed", str(summary["duplicates_removed"])], ["Facility categories", str(len(summary["facility_types"]))]], colWidths=[8 * cm, 5 * cm], style=TableStyle([("BACKGROUND", (0, 0), (-1, -1), PALE), ("GRID", (0, 0), (-1, -1), 0.5, colors.white), ("FONTNAME", (1, 0), (1, -1), "Helvetica-Bold"), ("TEXTCOLOR", (1, 0), (1, -1), TEAL), ("PADDING", (0, 0), (-1, -1), 11)])),
        Paragraph("Main outcome", styles["Sub"]),
        Paragraph("The result is a traceable CSV, a quality summary, a Power BI measure set, and a dashboard image. The analysis deliberately separates a published record count from service capacity. A facility appearing in the dataset does not confirm its current staffing, beds, medicines, or operating status.", styles["Body2"]),
        Paragraph("Why this is useful", styles["Sub"]),
        Paragraph("A consistent table allows analysts to compare geographic representation without repeatedly joining source layers. The completeness measure also shows where a map is ready for location analysis and where contextual fields still need review.", styles["Body2"]),
        PageBreak(),
    ])

    story.extend([
        Paragraph("2. Problem and analytical questions", styles["Section"]),
        Paragraph("The source is optimised for mapping rather than tabular analysis. Each facility group has its own endpoint, fields can be null, and the same place can appear more than once. The project therefore begins with a data engineering problem before any chart is created.", styles["Body2"]),
        Paragraph("Questions answered", styles["Sub"]),
        Paragraph("How many unique published facilities remain after exact deduplication? Which facility types contribute most records? Which districts have the largest record counts? How complete are the location and administrative fields? Can every processed row be traced back to a source layer?", styles["Body2"]),
        Paragraph("Root cause", styles["Sub"]),
        Paragraph("The most important root cause is structural fragmentation. Separate layers make category totals easy to view but difficult to reproduce as a single governed dataset. Null values and spelling variations create a second source of inconsistency.", styles["Body2"]),
        Paragraph("Success criteria", styles["Sub"]),
        Table([["Criterion", "Test"], ["Traceability", "Every row has a source layer and project identifier"], ["Consistency", "Text is trimmed and district variants are standardised"], ["Uniqueness", "Exact duplicate facility signatures are removed"], ["Usability", "Output loads directly into Power BI"], ["Honesty", "Dashboard states what the data cannot prove"]], colWidths=[4 * cm, 10 * cm], style=TableStyle([("BACKGROUND", (0, 0), (-1, 0), GREEN), ("TEXTCOLOR", (0, 0), (-1, 0), colors.white), ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#cad8d3")), ("VALIGN", (0, 0), (-1, -1), "TOP"), ("PADDING", (0, 0), (-1, -1), 7)])),
        PageBreak(),
    ])

    story.extend([
        Paragraph("3. Data source and provenance", styles["Section"]),
        Paragraph("The data comes from the Telangana Remote Sensing Applications Centre Health Facilities Mapping ArcGIS service. Twelve public layers are queried through the ArcGIS REST interface. The raw JSON responses and a retrieval manifest are stored before transformation.", styles["Body2"]),
        Paragraph("Source fields used", styles["Sub"]),
        Table([["Source concept", "Prepared field"], ["OBJECTID and layer identifier", "facility_id"], ["Facility_Name", "facility_name"], ["Facility_Type or layer label", "facility_type"], ["District and District_1", "district"], ["Latitude or geometry y", "latitude"], ["Longitude or geometry x", "longitude"]], colWidths=[7 * cm, 7 * cm], style=TableStyle([("BACKGROUND", (0, 0), (-1, 0), GREEN), ("TEXTCOLOR", (0, 0), (-1, 0), colors.white), ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#cad8d3")), ("PADDING", (0, 0), (-1, -1), 7)])),
        Paragraph("Provenance safeguards", styles["Sub"]),
        Paragraph("Raw responses are not overwritten. The manifest records the publisher, endpoint, retrieval time, and requested layer identifiers. The processing script can be rerun when the source changes, allowing a later result to be compared with this snapshot.", styles["Body2"]),
        Paragraph("Interpretation boundary", styles["Sub"]),
        Paragraph("This project describes the records published by the service. It is not an official census of all facilities and does not establish availability, quality, or clinical performance.", styles["Body2"]),
        PageBreak(),
    ])

    story.extend([
        Paragraph("4. Preparation pipeline", styles["Section"]),
        Paragraph("The pipeline follows five stages: collect, preserve, standardise, validate, and publish. Each API response is saved before selected fields are converted into the project schema.", styles["Body2"]),
        Table([["Stage", "Method", "Output"], ["Collect", "Query each facility layer", "Raw JSON"], ["Preserve", "Write response and source manifest", "Traceable snapshot"], ["Standardise", "Clean spacing, case, and district variants", "Consistent columns"], ["Validate", "Remove exact signatures and score completeness", "Quality metrics"], ["Publish", "Sort and export a flat table", "Power BI ready CSV"]], colWidths=[2.3 * cm, 7.7 * cm, 4 * cm], style=TableStyle([("BACKGROUND", (0, 0), (-1, 0), GREEN), ("TEXTCOLOR", (0, 0), (-1, 0), colors.white), ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#cad8d3")), ("VALIGN", (0, 0), (-1, -1), "TOP"), ("FONTSIZE", (0, 0), (-1, -1), 8.5), ("PADDING", (0, 0), (-1, -1), 6)])),
        Paragraph("Deduplication rule", styles["Sub"]),
        Paragraph("An exact signature uses the case-insensitive facility name, district, latitude, and longitude. This conservative rule avoids deleting similarly named facilities in different places. Near duplicates remain visible for manual investigation.", styles["Body2"]),
        Paragraph("Completeness rule", styles["Sub"]),
        Paragraph("The score checks name, type, district, mandal, latitude, and longitude. It measures whether important analysis fields are present; it does not measure whether each value is factually correct.", styles["Body2"]),
        PageBreak(),
    ])

    story.extend([
        Paragraph("5. Dashboard design", styles["Section"]),
        Image(str(ROOT / "evidence/facility_dashboard.png"), width=17 * cm, height=9.55 * cm),
        Spacer(1, 0.4 * cm),
        Paragraph("The dashboard begins with four KPIs and then moves from facility mix to district concentration and record quality. The layout keeps the main caution next to the charts so the published counts are not mistaken for current capacity.", styles["Body2"]),
        PageBreak(),
    ])

    top_types = summary["facility_types"][:6]
    story.extend([
        Paragraph("6. Facility mix findings", styles["Section"]),
        Paragraph("The published source is weighted toward primary and community-level records. This makes facility type an essential filter when interpreting district totals.", styles["Body2"]),
        Table([["Facility type", "Records", "Share"]] + [[name, f"{count:,}", f"{100 * count / len(rows):.1f}%"] for name, count in top_types], colWidths=[9 * cm, 2.5 * cm, 2.5 * cm], style=TableStyle([("BACKGROUND", (0, 0), (-1, 0), GREEN), ("TEXTCOLOR", (0, 0), (-1, 0), colors.white), ("ALIGN", (1, 1), (-1, -1), "RIGHT"), ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#cad8d3")), ("PADDING", (0, 0), (-1, -1), 8)])),
        Paragraph("Interpretation", styles["Sub"]),
        Paragraph("A district with many sub centres may have a high overall facility count without having many hospital records. Comparisons should therefore use both total records and type-specific records. The dashboard is designed to support that drill down in Power BI.", styles["Body2"]),
        Paragraph("Actionable next step", styles["Sub"]),
        Paragraph("Add population denominators and road travel times only after matching geographic definitions and dates. A facility per population measure would otherwise combine incompatible snapshots.", styles["Body2"]),
        PageBreak(),
    ])

    story.extend([
        Paragraph("7. Geographic and quality findings", styles["Section"]),
        Paragraph("The cleaned table represents 33 district labels. Hyderabad has the largest number of published records in this snapshot, followed by Bhadradri Kothagudem. This ranking describes source coverage and facility mix rather than need or performance.", styles["Body2"]),
        Table([["District", "Records"]] + [[name, str(count)] for name, count in summary["top_districts"]], colWidths=[10 * cm, 4 * cm], style=TableStyle([("BACKGROUND", (0, 0), (-1, 0), GREEN), ("TEXTCOLOR", (0, 0), (-1, 0), colors.white), ("ALIGN", (1, 1), (1, -1), "RIGHT"), ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#cad8d3")), ("PADDING", (0, 0), (-1, -1), 7)])),
        Paragraph("All prepared rows include coordinates because the service geometry is used when explicit latitude or longitude fields are empty. Most rows also meet the core completeness threshold. The remaining gaps occur mainly in administrative context such as mandal.", styles["Body2"]),
        PageBreak(),
    ])

    story.extend([
        Paragraph("8. Power BI model and measures", styles["Section"]),
        Paragraph("The clean table can be loaded as a single facility dimension for this scope. Latitude and longitude are decimal numbers; district, facility type, department, and source layer are categorical fields. The project includes reusable DAX measures for totals, district coverage, mapping coverage, and average completeness.", styles["Body2"]),
        Table([["Visual", "Field or measure", "Purpose"], ["KPI card", "Total Facilities", "Scale of the source snapshot"], ["KPI card", "District Count", "Geographic representation"], ["Bar chart", "Facility type and Total Facilities", "Mix of record categories"], ["Bar chart", "District and Total Facilities", "Concentration of published records"], ["Map", "Latitude, longitude, facility name", "Spatial exploration"], ["Quality card", "Average Completeness", "Preparation risk visibility"]], colWidths=[3.5 * cm, 5.5 * cm, 5 * cm], style=TableStyle([("BACKGROUND", (0, 0), (-1, 0), GREEN), ("TEXTCOLOR", (0, 0), (-1, 0), colors.white), ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#cad8d3")), ("VALIGN", (0, 0), (-1, -1), "TOP"), ("PADDING", (0, 0), (-1, -1), 7)])),
        Paragraph("Recommended interaction", styles["Sub"]),
        Paragraph("Selecting a facility type should filter every district visual and the map. Selecting a district should show the facility list and completeness details. Tooltips should repeat the source layer and avoid unverified service claims.", styles["Body2"]),
        PageBreak(),
    ])

    story.extend([
        Paragraph("9. Validation, limitations, and next steps", styles["Section"]),
        Paragraph("Automated tests check text cleaning, district normalisation, coordinate fallback, and exact duplicate removal. The continuous integration workflow runs tests and static checks for every update.", styles["Body2"]),
        Paragraph("Limitations", styles["Sub"]),
        Paragraph("The source can change after retrieval. A record can be outdated even when its fields are complete. The analysis has no population denominator, operating status, service hours, staffing, beds, medicine inventory, or quality indicators. Coordinate presence is not independently geocoded.", styles["Body2"]),
        Paragraph("Next steps", styles["Sub"]),
        Paragraph("Compare retrieval snapshots to detect additions and removals. Review near duplicate names. Add verified district population data with matching boundaries. Introduce travel time analysis for a carefully chosen service type. Request publisher confirmation before using the output operationally.", styles["Body2"]),
        Paragraph("Reproducibility", styles["Sub"]),
        Paragraph("Create a Python environment, install the pinned requirements, run the pipeline, render the dashboard, build this report, and execute the test suite. The README contains the exact commands and the manifest records the source endpoint.", styles["Body2"]),
    ])

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    doc.build(story, onFirstPage=page_number, onLaterPages=page_number)
    return OUTPUT


if __name__ == "__main__":
    print(build_report())
