from src.pipeline import clean_coordinate, clean_text, deduplicate, normalise_facility_type, transform_row


def test_clean_text_collapses_whitespace_and_nulls():
    assert clean_text("  Area   Hospital ") == "Area Hospital"
    assert clean_text("NA") == "Unknown"


def test_coordinate_validation_keeps_only_india_range():
    assert clean_coordinate("17.385", 6, 38) == 17.385
    assert clean_coordinate("170", 6, 38) is None


def test_facility_type_standardisation():
    assert normalise_facility_type("phc") == "Primary Health Centre"


def test_transform_and_deduplication():
    source = {
        "State Name": "Telangana",
        "District Name": "Hyderabad",
        "Subdistrict Name": "Nampally",
        "Facility Type": "phc",
        "Facility Name": "PHC Test",
        "Latitude": "17.38",
        "Longitude": "78.48",
        "Type Of Facility": "Public",
    }
    row = transform_row(source, 1)
    clean, removed = deduplicate([row, row.copy()])
    assert row["facility_type"] == "Primary Health Centre"
    assert len(clean) == 1
    assert removed == 1
