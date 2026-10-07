from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class FeedbackUnitOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    review_id: int
    text: str
    sentiment: Optional[str] = None
    sentiment_score: Optional[float] = None
    theme_id: Optional[int] = None
    confidence: Optional[float] = None


class ReviewOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    dataset_id: int
    raw_text: str
    clean_text: Optional[str] = None
    rating: Optional[float] = None
    review_date: Optional[date] = None
    app_version: Optional[str] = None
    platform: Optional[str] = None
    device: Optional[str] = None
    country: Optional[str] = None
    source: Optional[str] = None
    product_name: Optional[str] = None
    product_category: Optional[str] = None
    product_price: Optional[float] = None
    is_duplicate: bool = False
    duplicate_group_id: Optional[int] = None
    integrity_risk: float = 0.0
    rating_text_conflict: bool = False
    created_at: datetime


class ReviewDetailOut(ReviewOut):
    feedback_units: list[FeedbackUnitOut] = []


class ReviewListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    items: list[ReviewOut]
