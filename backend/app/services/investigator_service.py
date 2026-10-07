from pathlib import Path

from sqlalchemy.orm import Session

from app.models.evidence import Evidence
from app.models.incident import Incident
from app.schemas.chat import ChatAnswer, ChatMetric, ChatResponse
from app.services.dashboard_service import get_dashboard
from app.services.llm_service import LLMGenerationError, get_llm_provider

_PROMPT_PATH = Path(__file__).resolve().parent.parent / "prompts" / "investigator.txt"
_TEMPLATE = _PROMPT_PATH.read_text()


def _build_facts(db: Session, dataset_id: int) -> tuple[str, list[ChatMetric], dict[int, Evidence]]:
    dashboard = get_dashboard(db, dataset_id)
    incidents = (
        db.query(Incident)
        .filter(Incident.dataset_id == dataset_id)
        .order_by(Incident.impact_score.desc())
        .limit(6)
        .all()
    )

    lines = [
        f"Total reviews: {dashboard.total_reviews}",
        f"Average rating: {dashboard.average_rating}",
        f"Negative %: {dashboard.negative_percent}",
        f"Critical incidents: {dashboard.critical_incidents}",
        f"Emerging issues: {dashboard.emerging_issues}",
        "",
        "Top incidents by impact:",
    ]

    evidence_by_id: dict[int, Evidence] = {}
    for incident in incidents:
        lines.append(
            f"- Incident #{incident.id}: {incident.title} | severity={incident.severity} | "
            f"impact={incident.impact_score} | growth={incident.growth_percent}% | "
            f"likely_driver={incident.likely_driver} (confidence {incident.root_cause_confidence}%)"
        )
        evidence_items = (
            db.query(Evidence).filter(Evidence.incident_id == incident.id).limit(3).all()
        )
        for ev in evidence_items:
            evidence_by_id[ev.id] = ev
            lines.append(f"    evidence #{ev.id}: {ev.evidence_text}")

    metrics = [
        ChatMetric(label="Total reviews", value=str(dashboard.total_reviews)),
        ChatMetric(label="Average rating", value=str(dashboard.average_rating)),
        ChatMetric(label="Negative %", value=f"{dashboard.negative_percent}%"),
        ChatMetric(label="Critical incidents", value=str(dashboard.critical_incidents)),
    ]

    return "\n".join(lines), metrics, evidence_by_id


def answer_question(db: Session, dataset_id: int, question: str) -> ChatResponse:
    facts, metrics, evidence_by_id = _build_facts(db, dataset_id)
    prompt = _TEMPLATE.format(question=question, facts=facts)

    provider = get_llm_provider()
    try:
        result = provider.generate_structured(prompt, ChatAnswer)
        answer = result.answer
        incident_ids = result.cited_incident_ids
        evidence_ids = [eid for eid in result.cited_evidence_ids if eid in evidence_by_id]
    except LLMGenerationError:
        answer = (
            "I couldn't generate a grounded answer right now. Here are the current facts: \n"
            + facts
        )
        incident_ids = []
        evidence_ids = []

    return ChatResponse(
        answer=answer,
        evidence_ids=evidence_ids,
        metrics=metrics,
        incident_ids=incident_ids,
        generated_by=provider.name,
    )
