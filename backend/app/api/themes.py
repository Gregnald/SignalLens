from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.theme import Theme
from app.schemas.theme import ThemeDetailOut, ThemeOut
from app.services.theme_service import (
    get_theme_affected_segments,
    get_theme_representative_reviews,
    get_theme_trend,
)

router = APIRouter(prefix="/api/themes", tags=["themes"])


@router.get("/{dataset_id}", response_model=list[ThemeOut])
def list_themes(
    dataset_id: int,
    platform: str | None = Query(None),
    severity: str | None = Query(None),
    db: Session = Depends(get_db),
) -> list[ThemeOut]:
    query = db.query(Theme).filter(Theme.dataset_id == dataset_id)
    if severity:
        query = query.filter(Theme.severity == severity)
    themes = query.order_by(Theme.impact_score.desc().nullslast()).all()
    return [ThemeOut.model_validate(t) for t in themes]


@router.get("/{dataset_id}/{theme_id}", response_model=ThemeDetailOut)
def get_theme(dataset_id: int, theme_id: int, db: Session = Depends(get_db)) -> ThemeDetailOut:
    theme = db.query(Theme).filter(Theme.id == theme_id, Theme.dataset_id == dataset_id).first()
    if not theme:
        raise HTTPException(404, "Theme not found")

    return ThemeDetailOut(
        **ThemeOut.model_validate(theme).model_dump(),
        trend=get_theme_trend(db, theme_id),
        affected_segments=get_theme_affected_segments(db, theme_id),
        representative_reviews=get_theme_representative_reviews(db, theme_id),
    )
