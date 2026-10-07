from sqlalchemy.orm import Session

from app.models.dataset import Dataset
from app.models.feedback_unit import FeedbackUnit
from app.models.incident import Incident
from app.models.review import Review
from app.models.theme import Theme
from app.schemas.dashboard import DashboardOut, TopIssueItem, WhatChangedItem
from app.schemas.incident import IncidentOut
from app.utils.metrics import safe_mean


def get_dashboard(db: Session, dataset_id: int) -> DashboardOut:
    dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    total_reviews = dataset.total_reviews if dataset else 0

    reviews = db.query(Review).filter(Review.dataset_id == dataset_id).all()
    ratings = [r.rating for r in reviews if r.rating is not None]
    average_rating = safe_mean(ratings)

    units = (
        db.query(FeedbackUnit)
        .join(Review, FeedbackUnit.review_id == Review.id)
        .filter(Review.dataset_id == dataset_id)
        .all()
    )
    negative_units = sum(1 for u in units if u.sentiment == "negative")
    negative_percent = round(100.0 * negative_units / len(units), 1) if units else 0.0

    sentiment_breakdown = {
        "positive": sum(1 for u in units if u.sentiment == "positive"),
        "neutral": sum(1 for u in units if u.sentiment == "neutral"),
        "negative": negative_units,
    }

    themes = db.query(Theme).filter(Theme.dataset_id == dataset_id).all()
    emerging_issues = sum(1 for t in themes if t.is_emerging)

    incidents = (
        db.query(Incident)
        .filter(Incident.dataset_id == dataset_id)
        .order_by(Incident.impact_score.desc())
        .all()
    )
    critical_incidents = sum(1 for i in incidents if i.severity == "critical")

    what_changed = [
        WhatChangedItem(
            theme_id=t.id, theme_name=t.name, growth_percent=t.growth_percent, severity=t.severity or "low"
        )
        for t in sorted(themes, key=lambda t: -(t.growth_percent or 0))
        if t.growth_percent and t.growth_percent > 0
    ][:5]

    top_issues = [
        TopIssueItem(theme_id=t.id, theme_name=t.name, impact_score=t.impact_score or 0, severity=t.severity or "low")
        for t in sorted(themes, key=lambda t: -(t.impact_score or 0))
    ][:5]

    growth_values = [t.growth_percent for t in themes if t.growth_percent]
    complaint_increase_multiplier = (
        round(1 + max(growth_values) / 100.0, 1) if growth_values else None
    )

    return DashboardOut(
        dataset_id=dataset_id,
        total_reviews=total_reviews,
        average_rating=round(average_rating, 2) if average_rating is not None else None,
        negative_percent=negative_percent,
        emerging_issues=emerging_issues,
        critical_incidents=critical_incidents,
        complaint_increase_multiplier=complaint_increase_multiplier,
        sentiment_breakdown=sentiment_breakdown,
        what_changed=what_changed,
        top_issues=top_issues,
        recent_incidents=[IncidentOut.model_validate(i) for i in incidents[:10]],
    )
