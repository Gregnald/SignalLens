import zlib
from datetime import date

import numpy as np

from app.models.dataset import Dataset
from app.models.review import Review
from app.services import integrity_service
from tests.conftest import requires_db


def _fake_embed_texts(texts, batch_size=64):
    """Deterministic stand-in for the real MiniLM model: identical text -> identical
    vector (cosine similarity 1.0), different text -> a near-orthogonal random vector
    (cosine similarity close to 0), so duplicate detection logic is testable without
    downloading a model in CI.

    Earlier versions of this mock used a single dominant scalar bucket value
    (e.g. [bucket, 1.0, 0.0]), which is a bad embedding stand-in: two large,
    differently-valued buckets still produce cosine similarity ~0.9999 since the
    vectors are nearly collinear — it couldn't actually distinguish "different text"
    from "same text" and silently made duplicate-detection tests pass for the wrong
    reason. A 16-dim seeded-random unit vector per distinct text actually behaves like
    real embeddings for this purpose. Seeded from zlib.crc32 (not Python's built-in
    hash(), which is randomized per-process via PYTHONHASHSEED) for determinism.
    """
    vectors = []
    for text in texts:
        seed = zlib.crc32(text.strip().lower().encode()) & 0xFFFFFFFF
        rng = np.random.RandomState(seed)
        vectors.append(rng.normal(size=16).tolist())
    return vectors


@requires_db
def test_detect_duplicates_flags_near_identical_reviews(db_session, monkeypatch):
    monkeypatch.setattr(integrity_service, "embed_texts", _fake_embed_texts)

    dataset = Dataset(name="test-dataset")
    db_session.add(dataset)
    db_session.flush()

    reviews = [
        Review(dataset_id=dataset.id, raw_text="x", clean_text="Payment failed after update", review_date=date(2026, 9, 1)),
        Review(dataset_id=dataset.id, raw_text="x", clean_text="Payment failed after update", review_date=date(2026, 9, 1)),
        Review(dataset_id=dataset.id, raw_text="x", clean_text="Totally unrelated praise for the UI", review_date=date(2026, 9, 1)),
    ]
    db_session.add_all(reviews)
    db_session.commit()

    flagged = integrity_service.detect_duplicates(db_session, dataset.id)

    assert flagged == 2
    refreshed = db_session.query(Review).filter(Review.dataset_id == dataset.id).all()
    duplicate_flags = sorted(r.is_duplicate for r in refreshed)
    assert duplicate_flags == [False, True, True]


@requires_db
def test_detect_duplicates_scopes_comparison_per_product(db_session, monkeypatch):
    """Two different customers independently praising two unrelated products in similar
    words are not duplicates of each other — only same-product near-identical text should
    flag. Regression test for a real bug: without per-product scoping, ~94% of a real
    multi-product marketplace dataset got flagged as "duplicate" from common short praise
    like "wonderful" appearing across hundreds of unrelated products.
    """
    monkeypatch.setattr(integrity_service, "embed_texts", _fake_embed_texts)

    dataset = Dataset(name="test-dataset-products")
    db_session.add(dataset)
    db_session.flush()

    same_text = "Absolutely wonderful product, highly recommend it"
    reviews = [
        Review(dataset_id=dataset.id, raw_text="x", clean_text=same_text, product_name="Product A"),
        Review(dataset_id=dataset.id, raw_text="x", clean_text=same_text, product_name="Product A"),
        Review(dataset_id=dataset.id, raw_text="x", clean_text=same_text, product_name="Product B"),
    ]
    db_session.add_all(reviews)
    db_session.commit()

    flagged = integrity_service.detect_duplicates(db_session, dataset.id)

    # Only the two Product A reviews should flag each other; Product B's copy is
    # independent and must not join that group just because the text matches.
    assert flagged == 2
    refreshed = db_session.query(Review).filter(Review.dataset_id == dataset.id).all()
    product_a_flags = sorted(r.is_duplicate for r in refreshed if r.product_name == "Product A")
    product_b_flags = [r.is_duplicate for r in refreshed if r.product_name == "Product B"]
    assert product_a_flags == [True, True]
    assert product_b_flags == [False]


@requires_db
def test_detect_duplicates_ignores_very_short_text(db_session, monkeypatch):
    """Short generic praise ("wonderful", "good") is excluded from duplicate detection
    entirely — embedding similarity on 1-2 common words isn't meaningful signal.
    """
    monkeypatch.setattr(integrity_service, "embed_texts", _fake_embed_texts)

    dataset = Dataset(name="test-dataset-short")
    db_session.add(dataset)
    db_session.flush()

    reviews = [
        Review(dataset_id=dataset.id, raw_text="x", clean_text="wonderful", product_name="Product A"),
        Review(dataset_id=dataset.id, raw_text="x", clean_text="wonderful", product_name="Product A"),
    ]
    db_session.add_all(reviews)
    db_session.commit()

    flagged = integrity_service.detect_duplicates(db_session, dataset.id)
    assert flagged == 0


@requires_db
def test_rating_text_conflict_detection(db_session):
    dataset = Dataset(name="test-dataset-2")
    db_session.add(dataset)
    db_session.flush()

    review = Review(
        dataset_id=dataset.id,
        raw_text="x",
        clean_text="Worst update ever, nothing works, terrible experience",
        rating=5,
    )
    db_session.add(review)
    db_session.commit()

    flagged = integrity_service.detect_rating_text_conflicts(db_session, dataset.id)
    assert flagged == 1
    db_session.refresh(review)
    assert review.rating_text_conflict is True
