from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class ThemeTrendPoint(BaseModel):
    date: str
    volume: int
    avg_rating: Optional[float] = None


class ThemeOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    dataset_id: int
    name: str
    category: Optional[str] = None
    description: Optional[str] = None
    volume: int
    growth_percent: Optional[float] = None
    avg_sentiment: Optional[float] = None
    negative_percent: Optional[float] = None
    severity: Optional[str] = None
    impact_score: Optional[float] = None
    confidence: Optional[float] = None
    is_emerging: bool = False
    created_at: datetime
    updated_at: datetime


class ThemeDetailOut(ThemeOut):
    trend: list[ThemeTrendPoint] = []
    affected_segments: dict[str, dict[str, float]] = {}
    representative_reviews: list[str] = []


class ThemeLabel(BaseModel):
    """Structured output schema the LLM must fill for a cluster."""

    theme_name: str
    category: str
    description: str
    severity: str  # critical | high | medium | low
