"""Build a ten page report for India public health facility access analytics."""

from __future__ import annotations

import json
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import Image, PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "reports/India_Public_Health_Facility_Access_Analytics_Report.pdf"
GREEN = colors.HexColor("#143d35")
TEAL = colors.HexColor("#087f5b")
PALE = colors.HexColor("#eef5f2")


def footer(canvas, document):
    canvas.saveState()
    canvas.setFillColor(colors.HexColor("#60706a"))
    canvas.setFont("Helvetica", 8)
    canvas.drawString(2 * cm, 1.1 * cm, "India Public Health Facility Access Analytics")
    canvas.drawRightString(19 * cm, 1.1 * cm, f"Page {document.page}")
    canvas.restoreState()


def build_report() -> Path:
    summary = json.loads((ROOT / "data/processed/quality_summary.json").read_text())
    manifest = json.loads((ROOT / "data/raw/source_manifest.json").read_text())
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="CoverTitle", parent=styles["Title"], fontSize=27, leading=33, textColor=GREEN, alignment=TA_CENTER, spaceAfter=18))
    styles.add(ParagraphStyle(name="Section", parent=styles["Heading1"], fontSize=19, leading=24, textColor=GREEN, spaceAfter=13))
    styles.add(ParagraphStyle(name="Sub", parent=styles["Heading2"], fontSize=12, leading=16, textColor=TEAL, spaceBefore=8, spaceAfter=5))
    styles.add(ParagraphStyle(name="BodyR", parent=styles["BodyText"], fontSize=10, leading=15, textColor=colors.HexColor("#303c38"), spaceAfter=9))
    doc = SimpleDocTemplate(str(OUTPUT), pagesize=A4, leftMargin=2 * cm, rightMargin=2 * cm, topMargin=1.8 * cm, bottomMargin=1.8 * cm, title="India Public Health Facility Access Analytics", author="Harika")
    story = []
    table_style = TableStyle([("BACKGROUND", (0, 0), (-1, 0), GREEN), ("TEXTCOLOR", (0, 0), (-1, 0), colors.white), ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#cad8d3")), ("VALIGN", (0, 0), (-1, -1), "TOP"), ("PADDING", (0, 0), (-1, -1), 7)])
    story.extend([Spacer(1, 3.0 * cm), Paragraph("India Public Health Facility<br/>Access Analytics", styles["CoverTitle"]), Paragraph("From a historical national directory to a governed Power BI model", ParagraphStyle(name="CoverSub", parent=styles["BodyR"], fontSize=14, leading=20, textColor=TEAL, alignment=TA_CENTER)), Spacer(1, 1.2 * cm), Table([["Project type", "Data analytics and Power BI preparation"], ["Raw records", f"{summary['raw_records']:,}"], ["Geography", "36 states and union territories"], ["Prepared by", "Harika"]], colWidths=[4 * cm, 9 * cm], style=TableStyle([("BACKGROUND", (0, 0), (0, -1), PALE), ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"), ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#cad8d3")), ("PADDING", (0, 0), (-1, -1), 9)])), PageBreak()])

    sections = [
        ("1. Executive summary", [f"The pipeline prepares {summary['raw_records']:,} health-centre directory rows and publishes {summary['clean_records']:,} clean facility records after removing {summary['duplicates_removed']:,} exact duplicate signatures.", f"The result covers {summary['states_and_union_territories']} state and union territory labels, {summary['districts']} state-district combinations, and {summary['mapped_records_pct']}% valid coordinates.", "The project produces a governed table, quality summary, DAX measures, a four-page Power BI build guide, visual evidence, tests, and this report."]),
        ("2. Problem and analytical purpose", ["A large directory is not automatically analysis-ready. Null markers, facility aliases, invalid coordinates, outdated geography labels, and duplicate signatures can change totals and map behaviour.", "The project asks how published facility distribution can be compared while keeping data age and interpretation limits visible.", "The intended use is educational facility-distribution analysis. The output is not a live service locator or a statement about healthcare capacity or quality."]),
        ("3. Data source and provenance", ["The All India Health Centres Directory is downloaded from Kaggle. Its description states that attributes were collected from data.gov.in and that the snapshot reflects 7 October 2016.", f"The Kaggle page states a {manifest['license'].split(' as ')[0]} licence. The acquisition script stores the source URL, upstream attribution, file name, raw row count, and snapshot note.", "The historical date is shown in the README, dashboard guidance, and report because directory age materially limits interpretation."]),
        ("4. Data preparation", ["The pipeline standardises nulls and five facility categories, merges the source label Andhra Pradesh Old into Andhra Pradesh, validates latitude and longitude against a broad India range, and calculates completeness across eight analytical fields.", "Exact duplicate signatures use state, district, facility name, facility type, latitude, and longitude. This avoids deleting similarly named facilities in different places.", "The clean table preserves state, district, subdistrict, type, name, address, coordinates, activity flag, physical status, location type, ownership label, and NIN."]),
    ]
    for title, paragraphs in sections:
        story.append(Paragraph(title, styles["Section"]))
        for paragraph in paragraphs:
            story.append(Paragraph(paragraph, styles["BodyR"]))
        if title.startswith("4."):
            story.append(Table([["Quality output", "Result"], ["Clean records", f"{summary['clean_records']:,}"], ["Duplicates removed", f"{summary['duplicates_removed']:,}"], ["Valid coordinates", f"{summary['mapped_records_pct']}%"], ["Average completeness", f"{summary['average_completeness_pct']}%"]], colWidths=[8 * cm, 5 * cm], style=table_style))
        story.append(PageBreak())

    story.extend([Paragraph("5. Dashboard overview", styles["Section"]), Image(str(ROOT / "evidence/facility_dashboard.png"), width=17 * cm, height=9.55 * cm), Spacer(1, 0.35 * cm), Paragraph("The dashboard moves from scale and geographic coverage to facility type mix, state concentration, and data quality. A dark interpretation panel keeps the historical snapshot warning beside the findings.", styles["BodyR"]), PageBreak()])

    facility_rows = [["Facility type", "Records", "Share"]] + [[name, f"{count:,}", f"{100 * count / summary['clean_records']:.1f}%"] for name, count in summary["facility_types"]]
    state_rows = [["State", "Directory records"]] + [[name, f"{count:,}"] for name, count in summary["top_states"]]
    final = [
        ("6. Facility type findings", ["Sub Centres dominate the directory, followed by Primary Health Centres and Community Health Centres. District and Sub-District Hospitals represent a much smaller share.", "A state total therefore mainly reflects the distribution of lower-level facilities. Facility type must remain a filter in every state or district comparison.", "The directory does not provide current service availability, staffing, medicines, beds, clinical outcomes, or opening hours."], facility_rows),
        ("7. Geographic and quality findings", ["Uttar Pradesh has the largest number of directory records in this snapshot. The top-state table describes source coverage and administrative scale, not health need or current access.", f"Valid coordinates are present for {summary['mapped_records_pct']}% of clean records. Average core-field completeness is {summary['average_completeness_pct']}%.", "Coordinate presence is not the same as independently verified location accuracy. A mapped point may still be outdated or incorrectly classified."], state_rows),
        ("8. Power BI model", ["The clean CSV loads as a single facility table. Latitude and longitude use geographic data categories while state, district, subdistrict, type, location type, and ownership remain dimensions.", "Page one provides national scale and coverage. Page two is a geographic explorer. Page three compares states. Page four exposes duplicates, missing values, and coordinate quality.", "The included DAX calculates total facilities, state count, district count, mapped percentage, public percentage, and average completeness."], [["Page", "Decision supported"], ["National overview", "Understand scale and source mix"], ["Geographic explorer", "Inspect mapped facilities with filters"], ["State comparison", "Compare counts and quality consistently"], ["Data quality", "Review preparation risk before interpretation"]]),
        ("9. Limitations, reproducibility, and next steps", ["The snapshot is historical and largely public-facility focused. It has no matched population denominator or travel-time network and should not be used for current resource allocation.", "The repository contains acquisition, preparation, dashboard generation, DAX, tests, a data dictionary, and this report. The README lists a complete rebuild sequence.", "Next steps are to obtain a current authoritative facility register, validate a sample of coordinates, join boundaries and population from a compatible year, and calculate travel-time coverage for one carefully selected service level."], [["Risk", "Control"], ["Historical data presented as current", "Date shown beside every result"], ["Facility count presented as capacity", "Explicit interpretation warning"], ["Duplicate totals", "Reproducible signature rule"], ["Invalid map positions", "Coordinate range validation"]]),
    ]
    for title, paragraphs, rows in final:
        story.append(Paragraph(title, styles["Section"]))
        for paragraph in paragraphs:
            story.append(Paragraph(paragraph, styles["BodyR"]))
        story.append(Table(rows, colWidths=[9 * cm, 3 * cm, 2 * cm] if len(rows[0]) == 3 else [5 * cm, 9 * cm], style=table_style))
        if not title.startswith("9."):
            story.append(PageBreak())
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    doc.build(story, onFirstPage=footer, onLaterPages=footer)
    return OUTPUT


if __name__ == "__main__":
    print(build_report())
