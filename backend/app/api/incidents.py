from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.evidence import Evidence
from app.models.incident import Incident
from app.schemas.incident import ActionReportOut, EvidenceOut, IncidentDetailOut, IncidentOut
from app.services.action_service import generate_action_report
from app.services.incident_service import get_incident_rating_impact

router = APIRouter(prefix="/api/incidents", tags=["incidents"])


@router.get("/{dataset_id}", response_model=list[IncidentOut])
def list_incidents(dataset_id: int, db: Session = Depends(get_db)) -> list[IncidentOut]:
    incidents = (
        db.query(Incident)
        .filter(Incident.dataset_id == dataset_id)
        .order_by(Incident.impact_score.desc())
        .all()
    )
    return [IncidentOut.model_validate(i) for i in incidents]


@router.get("/{dataset_id}/{incident_id}", response_model=IncidentDetailOut)
def get_incident(dataset_id: int, incident_id: int, db: Session = Depends(get_db)) -> IncidentDetailOut:
    incident = (
        db.query(Incident)
        .filter(Incident.id == incident_id, Incident.dataset_id == dataset_id)
        .first()
    )
    if not incident:
        raise HTTPException(404, "Incident not found")

    evidence = db.query(Evidence).filter(Evidence.incident_id == incident_id).all()
    rating_impact = get_incident_rating_impact(db, incident)

    return IncidentDetailOut(
        **IncidentOut.model_validate(incident).model_dump(),
        evidence=[EvidenceOut.model_validate(e) for e in evidence],
        rating_impact=rating_impact,
    )


@router.post("/{incident_id}/generate-action", response_model=ActionReportOut)
def generate_action(incident_id: int, db: Session = Depends(get_db)) -> ActionReportOut:
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(404, "Incident not found")
    return generate_action_report(db, incident)


evidence_router = APIRouter(prefix="/api/incidents", tags=["evidence"])


@evidence_router.get("/{incident_id}/evidence", response_model=list[EvidenceOut])
def get_evidence(incident_id: int, db: Session = Depends(get_db)) -> list[EvidenceOut]:
    evidence = db.query(Evidence).filter(Evidence.incident_id == incident_id).all()
    return [EvidenceOut.model_validate(e) for e in evidence]
