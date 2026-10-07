from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class EvidenceOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    incident_id: int
    review_id: Optional[int] = None
    feedback_unit_id: Optional[int] = None
    evidence_type: str
    evidence_text: str
    relevance_score: Optional[float] = None


class IncidentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    dataset_id: int
    theme_id: int
    title: str
    summary: Optional[str] = None
    severity: str
    impact_score: float
    first_detected_at: Optional[datetime] = None
    last_detected_at: Optional[datetime] = None
    growth_percent: Optional[float] = None
    likely_driver: Optional[str] = None
    root_cause_confidence: Optional[float] = None
    affected_platforms: Optional[dict] = None
    affected_versions: Optional[dict] = None
    affected_devices: Optional[dict] = None
    recommended_owner: Optional[str] = None
    recommended_priority: Optional[str] = None
    status: str
    created_at: datetime


class IncidentDetailOut(IncidentOut):
    evidence: list[EvidenceOut] = []
    rating_impact: Optional[float] = None


class ActionReport(BaseModel):
    """Structured output schema the LLM must fill for the engineering report."""

    title: str
    problem: str
    impact: str
    affected_users: str
    likely_driver: str
    representative_evidence_summary: str
    severity: str
    recommended_owner: str
    priority: str
    next_steps: list[str]


class ActionReportOut(BaseModel):
    incident_id: int
    report: ActionReport
    generated_by: str  # "gemini" | "groq" | "mock"
