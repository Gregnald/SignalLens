import logging
from pathlib import Path

from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models.feedback_unit import FeedbackUnit
from app.models.review import Review
from app.models.theme import Theme
from app.schemas.theme import ThemeLabel
from app.services.clustering_service import ClusterResult, discover_clusters
from app.services.llm_service import LLMGenerationError, get_llm_provider
from app.services.severity_service import validate_severity
from app.utils.dates import daily_volume, rolling_baseline_and_current
from app.utils.metrics import growth_percent, safe_mean

logger = logging.getLogger(__name__)
settings = get_settings()

_PROMPT_PATH = Path(__file__).resolve().parent.parent / "prompts" / "theme_labeling.txt"
_PROMPT_TEMPLATE = _PROMPT_PATH.read_text()


def _label_cluster(cluster: ClusterResult) -> ThemeLabel:
    prompt = _PROMPT_TEMPLATE.format(
        cluster_size=len(cluster.unit_ids),
        avg_sentiment=round(cluster.avg_sentiment_score, 2),
        examples="\n".join(f"- {t}" for t in cluster.representative_texts),
    )
    provider = get_llm_provider()
    try:
        return provider.generate_structured(prompt, ThemeLabel)
    except LLMGenerationError as exc:
        logger.error("Theme labeling failed for cluster %s: %s", cluster.cluster_id, exc)
        return ThemeLabel(
            theme_name=f"Unlabeled cluster {cluster.cluster_id}",
            category="Other",
            description="Automatic labeling failed; manual review needed.",
            severity="medium",
        )


def _theme_confidence(cluster: ClusterResult, labeling_confidence: float, total_units: int) -> float:
    """ARCHITECTURE.md §37: 0.40 cohesion + 0.20 cluster size + 0.20 labeling + 0.20 evidence agreement."""
    cohesion_score = max(0.0, min(1.0, cluster.cohesion))
    size_score = min(1.0, len(cluster.unit_ids) / max(total_units * 0.05, 10))
    evidence_agreement = min(1.0, len(cluster.representative_texts) / 5.0)
    confidence = (
        0.40 * cohesion_score
        + 0.20 * size_score
        + 0.20 * labeling_confidence
        + 0.20 * evidence_agreement
    )
    return round(max(0.0, min(1.0, confidence)), 2)


def discover_and_label_themes(db: Session, dataset_id: int) -> list[Theme]:
    clusters = discover_clusters(db, dataset_id)
    if not clusters:
        return []

    total_units = (
        db.query(FeedbackUnit)
        .join(Review, FeedbackUnit.review_id == Review.id)
        .filter(Review.dataset_id == dataset_id)
        .count()
    )

    created_themes = []
    for cluster in clusters:
        label = _label_cluster(cluster)
        severity = validate_severity(label.severity, cluster.representative_texts)

        theme = Theme(
            dataset_id=dataset_id,
            name=label.theme_name,
            category=label.category,
            description=label.description,
            cluster_id=cluster.cluster_id,
            severity=severity,
            volume=len(cluster.unit_ids),
            avg_sentiment=round(cluster.avg_sentiment_score, 3),
            confidence=_theme_confidence(cluster, labeling_confidence=0.8, total_units=total_units),
        )
        db.add(theme)
        db.flush()  # get theme.id

        db.query(FeedbackUnit).filter(FeedbackUnit.id.in_(cluster.unit_ids)).update(
            {FeedbackUnit.theme_id: theme.id}, synchronize_session=False
        )
        created_themes.append(theme)

    db.commit()
    for theme in created_themes:
        db.refresh(theme)
    return created_themes


def calculate_temporal_metrics(db: Session, dataset_id: int) -> None:
    themes = db.query(Theme).filter(Theme.dataset_id == dataset_id).all()

    for theme in themes:
        units = (
            db.query(FeedbackUnit)
            .join(Review, FeedbackUnit.review_id == Review.id)
            .filter(FeedbackUnit.theme_id == theme.id)
            .all()
        )
        if not units:
            continue

        dates = []
        ratings = []
        negative_count = 0
        for unit in units:
            review = db.query(Review).filter(Review.id == unit.review_id).first()
            if review and review.review_date:
                dates.append(review.review_date)
            if review and review.rating is not None:
                ratings.append(review.rating)
            if unit.sentiment == "negative":
                negative_count += 1

        counts = daily_volume(dates)
        baseline_days = settings.rolling_baseline_days if len(counts) >= settings.rolling_baseline_days else settings.short_baseline_days
        baseline, _std, current = rolling_baseline_and_current(counts, baseline_days)

        theme.growth_percent = growth_percent(baseline, current) if baseline or current else None
        theme.negative_percent = round(100.0 * negative_count / len(units), 1) if units else 0.0
        theme.volume = len(units)

    db.commit()


def get_theme_avg_rating(db: Session, theme_id: int) -> float | None:
    units = db.query(FeedbackUnit).filter(FeedbackUnit.theme_id == theme_id).all()
    review_ids = [u.review_id for u in units]
    if not review_ids:
        return None
    ratings = [
        r.rating
        for r in db.query(Review).filter(Review.id.in_(review_ids)).all()
        if r.rating is not None
    ]
    return safe_mean(ratings)


def get_theme_representative_reviews(db: Session, theme_id: int, limit: int = 8) -> list[str]:
    units = (
        db.query(FeedbackUnit)
        .filter(FeedbackUnit.theme_id == theme_id)
        .order_by(FeedbackUnit.sentiment_score.asc())
        .limit(limit)
        .all()
    )
    return [u.text for u in units]


def get_theme_trend(db: Session, theme_id: int) -> list[dict]:
    units = db.query(FeedbackUnit).filter(FeedbackUnit.theme_id == theme_id).all()
    review_ids = [u.review_id for u in units]
    reviews = db.query(Review).filter(Review.id.in_(review_ids)).all() if review_ids else []

    by_day: dict = {}
    for r in reviews:
        if not r.review_date:
            continue
        bucket = by_day.setdefault(r.review_date, {"volume": 0, "ratings": []})
        bucket["volume"] += 1
        if r.rating is not None:
            bucket["ratings"].append(r.rating)

    return [
        {
            "date": day.isoformat(),
            "volume": data["volume"],
            "avg_rating": safe_mean(data["ratings"]),
        }
        for day, data in sorted(by_day.items())
    ]


def get_theme_affected_segments(db: Session, theme_id: int) -> dict[str, dict[str, float]]:
    theme = db.query(Theme).filter(Theme.id == theme_id).first()
    if not theme:
        return {}
    units = db.query(FeedbackUnit).filter(FeedbackUnit.theme_id == theme_id).all()
    review_ids = [u.review_id for u in units]
    reviews = db.query(Review).filter(Review.id.in_(review_ids)).all()

    total = len(reviews) or 1
    segments: dict[str, dict[str, float]] = {"platform": {}, "app_version": {}, "device": {}, "country": {}}
    for field_name in segments:
        counter: dict[str, int] = {}
        for r in reviews:
            value = getattr(r, field_name)
            if value:
                counter[value] = counter.get(value, 0) + 1
        segments[field_name] = {
            k: round(100.0 * v / total, 1) for k, v in sorted(counter.items(), key=lambda kv: -kv[1])
        }
    return segments
