import logging

from sqlalchemy.orm import Session

from app.models.review import Review

logger = logging.getLogger(__name__)

_ENTITIES = [
    "PERSON",
    "PHONE_NUMBER",
    "EMAIL_ADDRESS",
    "LOCATION",
    "CREDIT_CARD",
    "IBAN_CODE",
    "US_SSN",
    "US_BANK_NUMBER",
]

_analyzer = None
_anonymizer = None


def _get_engines():
    global _analyzer, _anonymizer
    if _analyzer is None:
        from presidio_analyzer import AnalyzerEngine
        from presidio_analyzer.nlp_engine import NlpEngineProvider
        from presidio_anonymizer import AnonymizerEngine

        # Presidio defaults to en_core_web_lg (400MB) and downloads it at runtime if
        # missing. We already bake en_core_web_sm into the image for spaCy sentence
        # segmentation (feedback_unit_service.py) — reuse it here instead.
        nlp_engine = NlpEngineProvider(
            nlp_configuration={
                "nlp_engine_name": "spacy",
                "models": [{"lang_code": "en", "model_name": "en_core_web_sm"}],
            }
        ).create_engine()

        _analyzer = AnalyzerEngine(nlp_engine=nlp_engine)
        _anonymizer = AnonymizerEngine()
    return _analyzer, _anonymizer


def redact_text(text: str) -> str:
    if not text:
        return text
    try:
        analyzer, anonymizer = _get_engines()
        results = analyzer.analyze(text=text, entities=_ENTITIES, language="en")
        if not results:
            return text
        anonymized = anonymizer.anonymize(text=text, analyzer_results=results)
        return anonymized.text
    except Exception as exc:  # noqa: BLE001 - PII redaction must never crash the pipeline
        logger.warning("PII redaction failed, leaving text as-is: %s", exc)
        return text


def redact_pii(db: Session, dataset_id: int) -> int:
    """Redact PII in clean_text for every review in the dataset. Returns count redacted."""
    reviews = (
        db.query(Review)
        .filter(Review.dataset_id == dataset_id, Review.clean_text.isnot(None))
        .all()
    )
    count = 0
    for review in reviews:
        review.clean_text = redact_text(review.clean_text)
        count += 1
    db.commit()
    return count
