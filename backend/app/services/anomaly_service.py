import numpy as np
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models.feedback_unit import FeedbackUnit
from app.models.theme import Theme
from app.utils.metrics import cosine_similarity

settings = get_settings()

_EMERGING_GROWTH_THRESHOLD = 90.0  # percent


def _theme_centroid(db: Session, theme_id: int) -> list[float] | None:
    units = (
        db.query(FeedbackUnit)
        .filter(FeedbackUnit.theme_id == theme_id, FeedbackUnit.embedding.isnot(None))
        .all()
    )
    if not units:
        return None
    vectors = np.array([u.embedding for u in units])
    return vectors.mean(axis=0).tolist()


def detect_emerging_issues(db: Session, dataset_id: int) -> int:
    """ARCHITECTURE.md §9: new semantic cluster + low similarity to existing themes +
    increasing frequency. At single-dataset scale, 'existing themes' = other themes already
    discovered in this run; 'new' is approximated by low centroid similarity to all of them.
    """
    themes = db.query(Theme).filter(Theme.dataset_id == dataset_id).all()
    if len(themes) < 2:
        for theme in themes:
            theme.is_emerging = bool(
                theme.growth_percent and theme.growth_percent >= _EMERGING_GROWTH_THRESHOLD
            )
        db.commit()
        return sum(1 for t in themes if t.is_emerging)

    centroids = {t.id: _theme_centroid(db, t.id) for t in themes}
    flagged = 0

    for theme in themes:
        centroid = centroids.get(theme.id)
        if centroid is None:
            theme.is_emerging = False
            continue

        max_similarity = max(
            (
                cosine_similarity(centroid, other_centroid)
                for other_id, other_centroid in centroids.items()
                if other_id != theme.id and other_centroid is not None
            ),
            default=0.0,
        )

        high_growth = bool(theme.growth_percent and theme.growth_percent >= _EMERGING_GROWTH_THRESHOLD)
        low_similarity = max_similarity < settings.emerging_issue_similarity_threshold

        theme.is_emerging = high_growth and low_similarity
        if theme.is_emerging:
            flagged += 1

    db.commit()
    return flagged
