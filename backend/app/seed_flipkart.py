"""Seeds the pre-loaded Flipkart marketplace dataset on first backend startup.

Per the product brief: this is an enterprise analytics tool where data is already loaded —
there is no "upload a CSV" step for the demo persona. Source: Kaggle
niraliivaghani/flipkart-product-customer-reviews-dataset (Dataset-SA.csv, 205k rows, 6
columns: product_name, product_price, Rate, Review, Summary, Sentiment).

Disclosed adaptations (the source dataset does not have these fields at all):
- product_category: derived from product_name via keyword heuristics (app.utils.product_category).
  Not ground truth — Flipkart's own taxonomy isn't in this dataset.
- review_date: the source has NO date column whatsoever. Dates are synthetically assigned,
  spread uniformly over the last 180 days, purely so the temporal-trend features
  (growth %, change-point detection, "What Changed?") have something to compute over.
- There is no seller/company column either — every review is of a product sold via
  Flipkart's own marketplace, so the demo persona represents Flipkart itself (the single
  highest-volume, highest-product-variety "enterprise" actually present in this data).

To keep the ML pipeline (sentence segmentation, sentiment, embeddings, clustering) runtime
reasonable on CPU, a stratified sample is ingested rather than all 205k rows — capped per
product so no single product swamps the sample, then capped to FLIPKART_SAMPLE_SIZE overall.
The full raw CSV stays on disk for anyone who wants to process the complete corpus.
"""

import logging
import random
import subprocess
import sys
from datetime import date, timedelta
from pathlib import Path

import pandas as pd

from app.core.config import get_settings
from app.core.database import SessionLocal
from app.models.dataset import Dataset
from app.models.review import Review
from app.utils.product_category import categorize_product, clean_product_name
from app.utils.text import is_empty_review

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Baked into the image at build time (backend/data_seed/) rather than bind-mounted — some
# Docker Desktop installs restrict volume mounts to paths under the user's home directory,
# so a bind mount of a sibling data/ folder can silently resolve to an empty directory.
CSV_PATH = Path(__file__).resolve().parent.parent / "data_seed" / "Dataset-SA.csv"
SAMPLE_SIZE = 10000
MAX_PER_PRODUCT = 60
DATE_WINDOW_DAYS = 180
DATASET_NAME = "Flipkart Marketplace Catalog"

random.seed(7)


def _load_and_clean() -> pd.DataFrame:
    df = pd.read_csv(CSV_PATH, dtype=str)

    # The source CSV has some rows where unescaped commas during scraping shifted columns —
    # Rate must be an integer 1-5; anything else means the row is malformed. Drop those.
    df = df[df["Rate"].isin(["1", "2", "3", "4", "5"])]

    df["text"] = df["Review"].fillna("").str.strip()
    needs_fallback = df["text"].str.len() < 2
    df.loc[needs_fallback, "text"] = df.loc[needs_fallback, "Summary"].fillna("").str.strip()
    df = df[df["text"].str.len() >= 2]

    df["product_price"] = pd.to_numeric(df["product_price"], errors="coerce")
    return df


def _stratified_sample(df: pd.DataFrame) -> pd.DataFrame:
    capped = df.groupby("product_name", group_keys=False).apply(
        lambda g: g.sample(n=min(len(g), MAX_PER_PRODUCT), random_state=7)
    )
    if len(capped) > SAMPLE_SIZE:
        capped = capped.sample(n=SAMPLE_SIZE, random_state=7)
    return capped


def _random_date() -> date:
    today = date.today()
    offset = random.randint(0, DATE_WINDOW_DAYS)
    return today - timedelta(days=offset)


def ingest_if_needed() -> int | None:
    db = SessionLocal()
    try:
        existing = db.query(Dataset).filter(Dataset.name == DATASET_NAME).first()
        if existing:
            logger.info("Flipkart dataset already seeded (id=%s), skipping ingestion.", existing.id)
            return existing.id if existing.status != "processed" else None

        if not CSV_PATH.exists():
            logger.warning(
                "Flipkart CSV not found at %s — skipping auto-seed. "
                "Run data/demo/... or mount data/raw/Dataset-SA.csv to seed it.",
                CSV_PATH,
            )
            return None

        logger.info("Loading and cleaning %s ...", CSV_PATH)
        df = _load_and_clean()
        logger.info("Cleaned rows: %d (from source file)", len(df))

        sample = _stratified_sample(df)
        logger.info("Stratified sample: %d rows across %d products", len(sample), sample["product_name"].nunique())

        dataset = Dataset(
            name=DATASET_NAME,
            source="Kaggle: niraliivaghani/flipkart-product-customer-reviews-dataset",
            file_name="Dataset-SA.csv",
            status="uploaded",
        )
        db.add(dataset)
        db.flush()

        buffer = []
        count = 0
        for _, row in sample.iterrows():
            text = row["text"]
            if is_empty_review(text):
                continue
            raw_name = row["product_name"]
            # A small number of scraped titles are keyword-stuffed well past any real
            # product name (one is 650+ chars) — truncate to fit the column and stay usable.
            clean_name = clean_product_name(raw_name)[:500]
            buffer.append(
                Review(
                    dataset_id=dataset.id,
                    raw_text=text,
                    rating=float(row["Rate"]),
                    review_date=_random_date(),
                    product_name=clean_name,
                    product_category=categorize_product(raw_name),
                    product_price=float(row["product_price"]) if pd.notna(row["product_price"]) else None,
                    source="flipkart",
                )
            )
            count += 1
            if len(buffer) >= 500:
                db.bulk_save_objects(buffer)
                buffer = []
        if buffer:
            db.bulk_save_objects(buffer)

        dataset.total_reviews = count
        db.commit()
        logger.info("Seeded Flipkart dataset id=%s with %d reviews.", dataset.id, count)
        return dataset.id
    finally:
        db.close()


def _trigger_background_processing(dataset_id: int) -> None:
    """Runs the ML pipeline in a detached subprocess so startup doesn't block on it —
    the dataset shows status=processing in the UI until it finishes.
    """
    logger.info("Starting background processing for dataset %s ...", dataset_id)
    subprocess.Popen(
        [
            sys.executable,
            "-c",
            f"from app.services.pipeline_service import process_dataset; process_dataset({dataset_id})",
        ],
        start_new_session=True,
    )


if __name__ == "__main__":
    settings = get_settings()
    new_dataset_id = ingest_if_needed()
    if new_dataset_id is not None:
        _trigger_background_processing(new_dataset_id)
