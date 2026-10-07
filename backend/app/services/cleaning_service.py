from sqlalchemy.orm import Session

from app.models.review import Review
from app.utils.text import is_empty_review, normalize_text


def clean_reviews(db: Session, dataset_id: int) -> int:
    """Normalize text and drop reviews that are empty after cleaning. Returns count cleaned."""
    reviews = db.query(Review).filter(Review.dataset_id == dataset_id).all()
    cleaned = 0
    to_delete = []
    for review in reviews:
        text = normalize_text(review.raw_text)
        if is_empty_review(text):
            to_delete.append(review)
            continue
        review.clean_text = text
        cleaned += 1
    for review in to_delete:
        db.delete(review)
    db.commit()
    return cleaned
