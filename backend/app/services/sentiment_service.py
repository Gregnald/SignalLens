import logging

from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

_pipeline = None

_LABEL_MAP = {
    "LABEL_0": "negative",
    "LABEL_1": "neutral",
    "LABEL_2": "positive",
    "negative": "negative",
    "neutral": "neutral",
    "positive": "positive",
}

SENTIMENT_TO_SCORE = {"negative": -1.0, "neutral": 0.0, "positive": 1.0}


def _get_pipeline():
    global _pipeline
    if _pipeline is None:
        from transformers import pipeline

        logger.info("Loading sentiment model %s", settings.sentiment_model)
        _pipeline = pipeline(
            "sentiment-analysis", model=settings.sentiment_model, tokenizer=settings.sentiment_model
        )
    return _pipeline


def analyze_sentiment_batch(texts: list[str], batch_size: int = 32) -> list[tuple[str, float]]:
    """Returns list of (label, confidence) for each text, label in {negative, neutral, positive}."""
    if not texts:
        return []
    pipe = _get_pipeline()
    truncated = [t[:512] for t in texts]
    results = pipe(truncated, batch_size=batch_size, truncation=True)
    out = []
    for r in results:
        label = _LABEL_MAP.get(r["label"], r["label"].lower())
        out.append((label, float(r["score"])))
    return out


def signed_sentiment_score(label: str, confidence: float) -> float:
    """Signed score in [-1, 1] combining polarity direction with model confidence."""
    direction = SENTIMENT_TO_SCORE.get(label, 0.0)
    return direction * confidence
