from pydantic import BaseModel


class DuplicateGroupOut(BaseModel):
    duplicate_group_id: int
    review_count: int
    avg_similarity: float
    sample_texts: list[str]


class BurstOut(BaseModel):
    window_start: str
    window_end: str
    review_count: int
    dominant_rating: float | None
    sample_texts: list[str]


class ConflictOut(BaseModel):
    review_id: int
    rating: float | None
    text: str


class IntegrityOut(BaseModel):
    dataset_id: int
    total_reviews: int
    flagged_percent: float
    duplicate_groups: list[DuplicateGroupOut]
    bursts: list[BurstOut]
    rating_text_conflicts: list[ConflictOut]
