from sqlalchemy.orm import Session

from app.models.evidence import Evidence
from app.models.feedback_unit import FeedbackUnit
from app.models.incident import Incident


def collect_evidence(db: Session, dataset_id: int, max_per_incident: int = 8) -> int:
    incidents = db.query(Incident).filter(Incident.dataset_id == dataset_id).all()
    created = 0

    for incident in incidents:
        units = (
            db.query(FeedbackUnit)
            .filter(FeedbackUnit.theme_id == incident.theme_id, FeedbackUnit.sentiment == "negative")
            .order_by(FeedbackUnit.sentiment_score.desc())
            .limit(max_per_incident)
            .all()
        )
        if not units:
            units = (
                db.query(FeedbackUnit)
                .filter(FeedbackUnit.theme_id == incident.theme_id)
                .limit(max_per_incident)
                .all()
            )

        for unit in units:
            db.add(
                Evidence(
                    incident_id=incident.id,
                    review_id=unit.review_id,
                    feedback_unit_id=unit.id,
                    evidence_type="representative_review",
                    evidence_text=unit.text,
                    relevance_score=unit.sentiment_score,
                )
            )
            created += 1

        if incident.growth_percent is not None:
            db.add(
                Evidence(
                    incident_id=incident.id,
                    evidence_type="temporal_statistic",
                    evidence_text=f"{incident.title} volume grew {incident.growth_percent}% vs baseline.",
                    relevance_score=None,
                )
            )
            created += 1

        if incident.likely_driver:
            db.add(
                Evidence(
                    incident_id=incident.id,
                    evidence_type="segment_concentration",
                    evidence_text=(
                        f"Likely driver: {incident.likely_driver} "
                        f"(confidence {incident.root_cause_confidence}%)."
                    ),
                    relevance_score=incident.root_cause_confidence / 100.0
                    if incident.root_cause_confidence
                    else None,
                )
            )
            created += 1

    db.commit()
    return created
