import logging

from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

_model = None


def _get_model():
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer

        logger.info("Loading embedding model %s", settings.embedding_model)
        _model = SentenceTransformer(settings.embedding_model)
    return _model


def embed_texts(texts: list[str], batch_size: int = 64) -> list[list[float]]:
    if not texts:
        return []
    model = _get_model()
    embeddings = model.encode(
        texts, batch_size=batch_size, show_progress_bar=False, convert_to_numpy=True
    )
    return [vec.tolist() for vec in embeddings]


def embed_text(text: str) -> list[float]:
    return embed_texts([text])[0]
