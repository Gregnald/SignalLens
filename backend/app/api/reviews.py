from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.feedback_unit import FeedbackUnit
from app.models.review import Review
from app.schemas.review import FeedbackUnitOut, ReviewDetailOut, ReviewListResponse, ReviewOut

router = APIRouter(prefix="/api/reviews", tags=["reviews"])


@router.get("/{dataset_id}", response_model=ReviewListResponse)
def list_reviews(
    dataset_id: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=200),
    platform: str | None = Query(None),
    severity_theme_id: int | None = Query(None),
    min_rating: float | None = Query(None),
    max_rating: float | None = Query(None),
    db: Session = Depends(get_db),
) -> ReviewListResponse:
    query = db.query(Review).filter(Review.dataset_id == dataset_id)
    if platform:
        query = query.filter(Review.platform == platform)
    if min_rating is not None:
        query = query.filter(Review.rating >= min_rating)
    if max_rating is not None:
        query = query.filter(Review.rating <= max_rating)
    if severity_theme_id is not None:
        query = query.join(FeedbackUnit, FeedbackUnit.review_id == Review.id).filter(
            FeedbackUnit.theme_id == severity_theme_id
        )

    total = query.count()
    items = (
        query.order_by(Review.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    return ReviewListResponse(
        total=total,
        page=page,
        page_size=page_size,
        items=[ReviewOut.model_validate(r) for r in items],
    )


@router.get("/{dataset_id}/{review_id}", response_model=ReviewDetailOut)
def get_review(dataset_id: int, review_id: int, db: Session = Depends(get_db)) -> ReviewDetailOut:
    review = db.query(Review).filter(Review.id == review_id, Review.dataset_id == dataset_id).first()
    if not review:
        raise HTTPException(404, "Review not found")
    units = db.query(FeedbackUnit).filter(FeedbackUnit.review_id == review_id).all()
    return ReviewDetailOut(
        **ReviewOut.model_validate(review).model_dump(),
        feedback_units=[FeedbackUnitOut.model_validate(u) for u in units],
    )
