import logging
from datetime import datetime, timezone
from pathlib import Path

from sqlalchemy.orm import Session

from app.models.feedback_unit import FeedbackUnit
from app.models.incident import Incident
from app.models.review import Review
from app.models.theme import Theme
from app.services.llm_service import LLMGenerationError, get_llm_provider
from app.services.theme_service import get_theme_avg_rating, get_theme_representative_reviews
from app.utils.metrics import clamp, safe_mean
from pydantic import BaseModel

logger = logging.getLogger(__name__)

_SUMMARY_PROMPT_PATH = Path(__file__).resolve().parent.parent / "prompts" / "incident_summary.txt"
_SUMMARY_TEMPLATE = _SUMMARY_PROMPT_PATH.read_text()

_SEVERITY_TO_OWNER = {
    "Payments": "Payments Engineering",
    "Performance": "Platform Engineering",
    "Login/Auth": "Auth Team",
    "UI/UX": "Frontend/Design",
    "Support": "Customer Support Ops",
    "Notifications": "Platform Engineering",
    "Search": "Search/Relevance Team",
    "Reliability": "Platform Engineering",
}
_SEVERITY_TO_PRIORITY = {"critical": "P0", "high": "P1", "medium": "P2", "low": "P3"}

INCIDENT_IMPACT_THRESHOLD = 35.0


class _SummaryOut(BaseModel):
    summary: str


def _compute_likely_driver(db: Session, theme_id: int) -> tuple[str | None, float, dict, dict, dict]:
    """Pure algorithmic likely-driver + confidence from segment concentration.
    Never an LLM output — see ARCHITECTURE.md §13/§23.
    """
    units = db.query(FeedbackUnit).filter(FeedbackUnit.theme_id == theme_id).all()
    review_ids = [u.review_id for u in units]
    reviews = db.query(Review).filter(Review.id.in_(review_ids)).all() if review_ids else []

    total = len(reviews) or 1

    def concentration(field: str) -> tuple[str | None, float, dict]:
        counts: dict[str, int] = {}
        for r in reviews:
            value = getattr(r, field)
            if value:
                counts[value] = counts.get(value, 0) + 1
        if not counts:
            return None, 0.0, {}
        top_value, top_count = max(counts.items(), key=lambda kv: kv[1])
        pct_map = {k: round(100.0 * v / total, 1) for k, v in counts.items()}
        return top_value, round(100.0 * top_count / total, 1), pct_map

    top_platform, platform_pct, platform_map = concentration("platform")
    top_version, version_pct, version_map = concentration("app_version")
    top_device, device_pct, device_map = concentration("device")

    driver_parts = [p for p in (top_platform, top_version) if p]
    strong_signal = version_pct >= 50.0 or platform_pct >= 70.0

    if driver_parts and strong_signal:
        likely_driver = " ".join(driver_parts)
        confidence = clamp(0.5 * version_pct + 0.3 * platform_pct + 0.2 * device_pct, 0, 100)
    else:
        likely_driver = None
        confidence = clamp(0.3 * version_pct + 0.2 * platform_pct, 0, 60)

    return (
        likely_driver,
        round(confidence, 1),
        {top_platform: platform_pct} if top_platform else platform_map,
        {top_version: version_pct} if top_version else version_map,
        {top_device: device_pct} if top_device else device_map,
    )


def _generate_summary(theme: Theme, avg_rating: float | None, examples: list[str]) -> str:
    prompt = _SUMMARY_TEMPLATE.format(
        theme_name=theme.name,
        category=theme.category or "Other",
        severity=theme.severity or "medium",
        volume=theme.volume,
        growth_percent=theme.growth_percent if theme.growth_percent is not None else "unknown",
        avg_rating=round(avg_rating, 2) if avg_rating is not None else "unknown",
        impact_score=theme.impact_score,
        examples="\n".join(f"- {t}" for t in examples),
    )
    provider = get_llm_provider()
    try:
        result = provider.generate_structured(prompt, _SummaryOut)
        return result.summary
    except LLMGenerationError as exc:
        logger.error("Incident summary generation failed for theme %s: %s", theme.id, exc)
        return (
            f"{theme.name}: {theme.volume} reports, "
            f"{theme.growth_percent or 0}% growth, severity {theme.severity}."
        )


def generate_incidents(db: Session, dataset_id: int) -> list[Incident]:
    themes = (
        db.query(Theme)
        .filter(Theme.dataset_id == dataset_id, Theme.impact_score >= INCIDENT_IMPACT_THRESHOLD)
        .all()
    )

    created = []
    for theme in themes:
        examples = get_theme_representative_reviews(db, theme.id)
        avg_rating = get_theme_avg_rating(db, theme.id)
        summary = _generate_summary(theme, avg_rating, examples)

        likely_driver, confidence, platforms, versions, devices = _compute_likely_driver(db, theme.id)

        owner = _SEVERITY_TO_OWNER.get(theme.category or "", "Product Engineering")
        priority = _SEVERITY_TO_PRIORITY.get((theme.severity or "low").lower(), "P3")

        incident = Incident(
            dataset_id=dataset_id,
            theme_id=theme.id,
            title=theme.name,
            summary=summary,
            severity=theme.severity or "low",
            impact_score=theme.impact_score or 0.0,
            first_detected_at=datetime.now(timezone.utc),
            last_detected_at=datetime.now(timezone.utc),
            growth_percent=theme.growth_percent,
            likely_driver=likely_driver,
            root_cause_confidence=confidence,
            affected_platforms=platforms,
            affected_versions=versions,
            affected_devices=devices,
            recommended_owner=owner,
            recommended_priority=priority,
            status="open",
        )
        db.add(incident)
        created.append(incident)

    db.commit()
    for incident in created:
        db.refresh(incident)
    return created


def get_incident_rating_impact(db: Session, incident: Incident) -> float | None:
    avg_rating = get_theme_avg_rating(db, incident.theme_id)
    if avg_rating is None:
        return None
    overall_avg = safe_mean(
        [r.rating for r in db.query(Review).filter(Review.dataset_id == incident.dataset_id).all() if r.rating is not None]
    )
    if overall_avg is None:
        return None
    return round(avg_rating - overall_avg, 2)
