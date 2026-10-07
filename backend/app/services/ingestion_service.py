import io
from datetime import date

import pandas as pd
from sqlalchemy.orm import Session

from app.models.dataset import Dataset
from app.models.review import Review

_COLUMN_CANDIDATES = {
    "text": ["review", "review_text", "text", "content", "comment", "body", "feedback"],
    "rating": ["rating", "score", "stars", "star_rating"],
    "date": ["date", "review_date", "created_at", "timestamp", "time"],
    "app_version": ["app_version", "version", "appversion"],
    "platform": ["platform", "os"],
    "device": ["device", "device_model", "model"],
    "country": ["country", "region", "locale"],
    "external_review_id": ["review_id", "id", "external_id"],
}


def detect_columns(columns: list[str]) -> dict[str, str | None]:
    lower_cols = {c.lower().strip(): c for c in columns}
    detected: dict[str, str | None] = {}
    for field, candidates in _COLUMN_CANDIDATES.items():
        match = next((lower_cols[c] for c in candidates if c in lower_cols), None)
        detected[field] = match
    return detected


def _parse_date(value) -> date | None:
    if pd.isna(value):
        return None
    try:
        return pd.to_datetime(value).date()
    except Exception:  # noqa: BLE001
        return None


def _parse_rating(value) -> float | None:
    try:
        if pd.isna(value):
            return None
        return float(value)
    except Exception:  # noqa: BLE001
        return None


def parse_upload(filename: str, content: bytes) -> pd.DataFrame:
    if filename.lower().endswith(".xlsx"):
        return pd.read_excel(io.BytesIO(content))
    return pd.read_csv(io.BytesIO(content))


def ingest_dataframe(
    db: Session, dataset: Dataset, df: pd.DataFrame, source: str = "upload"
) -> tuple[int, int, list[str], dict[str, str | None]]:
    columns = detect_columns(list(df.columns))
    warnings: list[str] = []

    if not columns["text"]:
        raise ValueError("Could not detect a review text column in the uploaded file.")

    rows_ingested = 0
    rows_skipped = 0
    buffer = []

    for _, row in df.iterrows():
        text = row.get(columns["text"]) if columns["text"] else None
        if pd.isna(text) or not str(text).strip():
            rows_skipped += 1
            continue

        buffer.append(
            Review(
                dataset_id=dataset.id,
                external_review_id=(
                    str(row.get(columns["external_review_id"]))
                    if columns["external_review_id"] and not pd.isna(row.get(columns["external_review_id"]))
                    else None
                ),
                raw_text=str(text),
                rating=_parse_rating(row.get(columns["rating"])) if columns["rating"] else None,
                review_date=_parse_date(row.get(columns["date"])) if columns["date"] else None,
                app_version=(
                    str(row.get(columns["app_version"]))
                    if columns["app_version"] and not pd.isna(row.get(columns["app_version"]))
                    else None
                ),
                platform=(
                    str(row.get(columns["platform"]))
                    if columns["platform"] and not pd.isna(row.get(columns["platform"]))
                    else None
                ),
                device=(
                    str(row.get(columns["device"]))
                    if columns["device"] and not pd.isna(row.get(columns["device"]))
                    else None
                ),
                country=(
                    str(row.get(columns["country"]))
                    if columns["country"] and not pd.isna(row.get(columns["country"]))
                    else None
                ),
                source=source,
            )
        )
        rows_ingested += 1

        if len(buffer) >= 500:
            db.bulk_save_objects(buffer)
            buffer = []

    if buffer:
        db.bulk_save_objects(buffer)

    for field in ("rating", "date", "app_version", "platform"):
        if not columns[field]:
            warnings.append(f"No '{field}' column detected — related features will be degraded.")

    dataset.total_reviews = rows_ingested
    dataset.status = "uploaded"
    db.commit()

    return rows_ingested, rows_skipped, warnings, columns
