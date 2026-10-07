from pydantic import BaseModel

from app.schemas.incident import IncidentOut


class WhatChangedItem(BaseModel):
    theme_id: int
    theme_name: str
    growth_percent: float
    severity: str


class TopIssueItem(BaseModel):
    theme_id: int
    theme_name: str
    impact_score: float
    severity: str


class DashboardOut(BaseModel):
    dataset_id: int
    total_reviews: int
    average_rating: float | None
    negative_percent: float
    emerging_issues: int
    critical_incidents: int
    complaint_increase_multiplier: float | None
    sentiment_breakdown: dict[str, int]
    what_changed: list[WhatChangedItem]
    top_issues: list[TopIssueItem]
    recent_incidents: list[IncidentOut]
