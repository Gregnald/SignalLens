from pathlib import Path

from sqlalchemy.orm import Session

from app.models.incident import Incident
from app.schemas.incident import ActionReport, ActionReportOut
from app.services.evidence_service import collect_evidence
from app.services.llm_service import LLMGenerationError, get_llm_provider
from app.models.evidence import Evidence

_PROMPT_PATH = Path(__file__).resolve().parent.parent / "prompts" / "action_report.txt"
_TEMPLATE = _PROMPT_PATH.read_text()


def generate_action_report(db: Session, incident: Incident) -> ActionReportOut:
    evidence_items = (
        db.query(Evidence)
        .filter(Evidence.incident_id == incident.id, Evidence.evidence_type == "representative_review")
        .limit(6)
        .all()
    )
    if not evidence_items:
        collect_evidence(db, incident.dataset_id)
        evidence_items = (
            db.query(Evidence)
            .filter(
                Evidence.incident_id == incident.id, Evidence.evidence_type == "representative_review"
            )
            .limit(6)
            .all()
        )

    affected_segments = ", ".join(
        f"{k} {v}%"
        for d in (incident.affected_platforms, incident.affected_versions, incident.affected_devices)
        if d
        for k, v in d.items()
    )

    prompt = _TEMPLATE.format(
        theme_name=incident.title,
        severity=incident.severity,
        impact_score=incident.impact_score,
        volume=sum(1 for _ in evidence_items) or "unknown",
        growth_percent=incident.growth_percent if incident.growth_percent is not None else "unknown",
        likely_driver=incident.likely_driver or "insufficient evidence",
        root_cause_confidence=incident.root_cause_confidence or 0,
        affected_segments=affected_segments or "not available",
        examples="\n".join(f"- {e.evidence_text}" for e in evidence_items),
    )

    provider = get_llm_provider()
    try:
        report = provider.generate_structured(prompt, ActionReport)
    except LLMGenerationError:
        report = ActionReport(
            title=incident.title,
            problem=incident.summary or "See incident summary.",
            impact=f"{incident.impact_score} impact score, {incident.growth_percent or 0}% growth.",
            affected_users=affected_segments or "Segment data unavailable.",
            likely_driver=incident.likely_driver or "Insufficient evidence to identify a likely driver.",
            representative_evidence_summary="See evidence tab for supporting reviews.",
            severity=incident.severity,
            recommended_owner=incident.recommended_owner or "Product Engineering",
            priority=incident.recommended_priority or "P2",
            next_steps=["Investigate affected segment logs.", "Reproduce on affected version."],
        )

    incident.action_report = report.model_dump()
    db.commit()

    return ActionReportOut(
        incident_id=incident.id, report=report, generated_by=provider.name
    )
