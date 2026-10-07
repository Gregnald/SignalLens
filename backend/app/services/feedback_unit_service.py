import logging

from sqlalchemy.orm import Session

from app.models.feedback_unit import FeedbackUnit
from app.models.review import Review
from app.services.embedding_service import embed_texts
from app.services.sentiment_service import analyze_sentiment_batch

logger = logging.getLogger(__name__)

_nlp = None


def _get_nlp():
    global _nlp
    if _nlp is None:
        import spacy

        try:
            _nlp = spacy.load("en_core_web_sm", exclude=["ner", "lemmatizer"])
        except OSError:
            logger.warning("en_core_web_sm not found, falling back to blank English sentencizer")
            _nlp = spacy.blank("en")
            _nlp.add_pipe("sentencizer")
    return _nlp


def split_sentences(text: str) -> list[tuple[str, int, int]]:
    """Returns list of (sentence_text, start_offset, end_offset)."""
    if not text:
        return []
    nlp = _get_nlp()
    doc = nlp(text)
    sentences = []
    for sent in doc.sents:
        cleaned = sent.text.strip()
        if len(cleaned) >= 3:
            sentences.append((cleaned, sent.start_char, sent.end_char))
    return sentences or [(text, 0, len(text))]


def create_feedback_units(db: Session, dataset_id: int) -> int:
    """Sentence-segment every review's clean_text into feedback units."""
    reviews = (
        db.query(Review)
        .filter(Review.dataset_id == dataset_id, Review.clean_text.isnot(None))
        .all()
    )

    created = 0
    for review in reviews:
        for text, start, end in split_sentences(review.clean_text):
            db.add(
                FeedbackUnit(
                    review_id=review.id,
                    text=text,
                    start_offset=start,
                    end_offset=end,
                )
            )
            created += 1
    db.commit()
    return created


def run_sentiment(db: Session, dataset_id: int, batch_size: int = 64) -> int:
    units = (
        db.query(FeedbackUnit)
        .join(Review, FeedbackUnit.review_id == Review.id)
        .filter(Review.dataset_id == dataset_id)
        .all()
    )
    if not units:
        return 0

    texts = [u.text for u in units]
    updated = 0
    for i in range(0, len(units), batch_size):
        batch = units[i : i + batch_size]
        batch_texts = texts[i : i + batch_size]
        results = analyze_sentiment_batch(batch_texts, batch_size=batch_size)
        for unit, (label, confidence) in zip(batch, results):
            unit.sentiment = label
            unit.sentiment_score = confidence
            updated += 1
    db.commit()
    return updated


def generate_embeddings(db: Session, dataset_id: int, batch_size: int = 64) -> int:
    units = (
        db.query(FeedbackUnit)
        .join(Review, FeedbackUnit.review_id == Review.id)
        .filter(Review.dataset_id == dataset_id)
        .all()
    )
    if not units:
        return 0

    updated = 0
    for i in range(0, len(units), batch_size):
        batch = units[i : i + batch_size]
        vectors = embed_texts([u.text for u in batch], batch_size=batch_size)
        for unit, vector in zip(batch, vectors):
            unit.embedding = vector
            updated += 1
    db.commit()
    return updated
