from app.services.ingestion_service import detect_columns


def test_detects_standard_column_names():
    columns = detect_columns(["review_id", "review", "rating", "date", "app_version", "platform"])
    assert columns["text"] == "review"
    assert columns["rating"] == "rating"
    assert columns["date"] == "date"
    assert columns["app_version"] == "app_version"
    assert columns["platform"] == "platform"
    assert columns["external_review_id"] == "review_id"


def test_detects_alternate_column_names_case_insensitive():
    columns = detect_columns(["Content", "Stars", "Timestamp", "OS"])
    assert columns["text"] == "Content"
    assert columns["rating"] == "Stars"
    assert columns["date"] == "Timestamp"
    assert columns["platform"] == "OS"


def test_missing_optional_columns_are_none():
    columns = detect_columns(["review"])
    assert columns["text"] == "review"
    assert columns["rating"] is None
    assert columns["device"] is None
    assert columns["country"] is None
