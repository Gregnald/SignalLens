"""The core orchestration pipeline — ARCHITECTURE.md §6.

process_dataset() is intentionally a thin, readable sequence of service calls; all actual
logic lives in the individual services. Each stage updates Dataset.processing_stage /
processing_progress so the frontend can show real progress, not a fake spinner.
"""

import logging

from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.models.dataset import Dataset
from app.services import (
    anomaly_service,
    cleaning_service,
    evidence_service,
    feedback_unit_service,
    impact_service,
    incident_service,
    integrity_service,
    pii_service,
    theme_service,
)

logger = logging.getLogger(__name__)

_STAGES = [
    ("cleaning", 5.0),
    ("pii_redaction", 15.0),
    ("duplicate_detection", 25.0),
    ("feedback_units", 35.0),
    ("sentiment", 50.0),
    ("embeddings", 65.0),
    ("theme_discovery", 80.0),
    ("temporal_analysis", 85.0),
    ("emerging_issues", 88.0),
    ("impact_scoring", 92.0),
    ("incident_generation", 96.0),
    ("evidence_collection", 100.0),
]


def _set_stage(db: Session, dataset: Dataset, stage: str, progress: float) -> None:
    dataset.processing_stage = stage
    dataset.processing_progress = progress
    db.commit()
    logger.info("Dataset %s: stage=%s progress=%.0f%%", dataset.id, stage, progress)


def process_dataset(dataset_id: int) -> None:
    """Runs synchronously inside a FastAPI BackgroundTask / worker process."""
    db = SessionLocal()
    try:
        dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
        if not dataset:
            return

        dataset.status = "processing"
        db.commit()

        _set_stage(db, dataset, *_STAGES[0])
        cleaning_service.clean_reviews(db, dataset_id)

        _set_stage(db, dataset, *_STAGES[1])
        pii_service.redact_pii(db, dataset_id)

        _set_stage(db, dataset, *_STAGES[2])
        integrity_service.detect_duplicates(db, dataset_id)
        integrity_service.detect_rating_text_conflicts(db, dataset_id)

        _set_stage(db, dataset, *_STAGES[3])
        feedback_unit_service.create_feedback_units(db, dataset_id)

        _set_stage(db, dataset, *_STAGES[4])
        feedback_unit_service.run_sentiment(db, dataset_id)

        _set_stage(db, dataset, *_STAGES[5])
        feedback_unit_service.generate_embeddings(db, dataset_id)

        _set_stage(db, dataset, *_STAGES[6])
        theme_service.discover_and_label_themes(db, dataset_id)

        _set_stage(db, dataset, *_STAGES[7])
        theme_service.calculate_temporal_metrics(db, dataset_id)

        _set_stage(db, dataset, *_STAGES[8])
        anomaly_service.detect_emerging_issues(db, dataset_id)

        _set_stage(db, dataset, *_STAGES[9])
        impact_service.calculate_impact_scores(db, dataset_id)

        _set_stage(db, dataset, *_STAGES[10])
        incident_service.generate_incidents(db, dataset_id)

        _set_stage(db, dataset, *_STAGES[11])
        evidence_service.collect_evidence(db, dataset_id)

        dataset.status = "processed"
        dataset.processing_error = None
        db.commit()

    except Exception as exc:  # noqa: BLE001 - must never leave status stuck at "processing"
        logger.exception("Pipeline failed for dataset %s", dataset_id)
        db.rollback()
        dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
        if dataset:
            dataset.status = "failed"
            dataset.processing_error = str(exc)
            db.commit()
    finally:
        db.close()
