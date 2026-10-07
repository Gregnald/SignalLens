from sqlalchemy.orm import Session

from app.models.feedback_unit import FeedbackUnit
from app.models.review import Review
from app.models.theme import Theme
from app.utils.metrics import SEVERITY_WEIGHT, impact_score, normalize


def _reach_score(db: Session, theme_id: int) -> float:
    """Breadth of impact: how many distinct platforms/devices/countries are affected."""
    units = db.query(FeedbackUnit).filter(FeedbackUnit.theme_id == theme_id).all()
    review_ids = [u.review_id for u in units]
    if not review_ids:
        return 0.0
    reviews = db.query(Review).filter(Review.id.in_(review_ids)).all()

    distinct_platforms = len({r.platform for r in reviews if r.platform})
    distinct_devices = len({r.device for r in reviews if r.device})
    distinct_countries = len({r.country for r in reviews if r.country})

    breadth = distinct_platforms + distinct_devices + distinct_countries
    return normalize(breadth, min_value=0, max_value=9)


def calculate_impact_scores(db: Session, dataset_id: int) -> None:
    themes = db.query(Theme).filter(Theme.dataset_id == dataset_id).all()
    if not themes:
        return

    max_volume = max((t.volume for t in themes), default=1) or 1

    for theme in themes:
        volume_score = normalize(theme.volume, min_value=0, max_value=max_volume)
        growth_score = normalize(theme.growth_percent or 0, min_value=0, max_value=300)
        severity_score = SEVERITY_WEIGHT.get((theme.severity or "low").lower(), 15.0)
        negative_sentiment_score = theme.negative_percent or 0.0
        reach_score = _reach_score(db, theme.id)
        confidence_score = (theme.confidence or 0.0) * 100.0

        theme.impact_score = impact_score(
            volume_score=volume_score,
            growth_score=growth_score,
            severity_score=severity_score,
            negative_sentiment_score=negative_sentiment_score,
            reach_score=reach_score,
            confidence_score=confidence_score,
        )

    db.commit()
