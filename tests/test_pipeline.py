from src.pipeline import clean_text, deduplicate, normalise_district, transform_feature


def test_clean_text_collapses_whitespace():
    assert clean_text("  Area   Hospital ") == "Area Hospital"


def test_district_standardisation():
    assert normalise_district("RANGAREDDY") == "Ranga Reddy"


def test_feature_uses_geometry_when_attributes_are_missing():
    feature = {"attributes": {"OBJECTID": 5, "Facility_Name": "PHC Test", "District": "NIRMAL"}, "geometry": {"x": 78.1, "y": 18.2}}
    row = transform_feature(feature, 17, "Primary Health Centre")
    assert row["latitude"] == 18.2
    assert row["district"] == "Nirmal"


def test_deduplication_uses_name_district_and_position():
    row = {"facility_name": "PHC One", "district": "Nirmal", "latitude": 18.0, "longitude": 78.0}
    clean, removed = deduplicate([row, row.copy()])
    assert len(clean) == 1
    assert removed == 1

