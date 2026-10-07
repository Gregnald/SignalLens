import logging
from collections import defaultdict
from datetime import timedelta

import numpy as np
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models.review import Review
from app.schemas.integrity import BurstOut, ConflictOut, DuplicateGroupOut, IntegrityOut
from app.services.embedding_service import embed_texts

logger = logging.getLogger(__name__)
settings = get_settings()

_NEGATIVE_WORDS = {
    "worst",
    "terrible",
    "awful",
    "broken",
    "useless",
    "horrible",
    "hate",
    "garbage",
    "nothing works",
    "doesn't work",
}
_POSITIVE_WORDS = {"amazing", "excellent", "love", "perfect", "great", "best"}


class _UnionFind:
    def __init__(self, n: int) -> None:
        self.parent = list(range(n))

    def find(self, x: int) -> int:
        while self.parent[x] != x:
            self.parent[x] = self.parent[self.parent[x]]
            x = self.parent[x]
        return x

    def union(self, a: int, b: int) -> None:
        ra, rb = self.find(a), self.find(b)
        if ra != rb:
            self.parent[rb] = ra


_MIN_DUPLICATE_TEXT_LENGTH = 15


def detect_duplicates(db: Session, dataset_id: int, block_size: int = 1000) -> int:
    """Near-duplicate detection via cosine similarity on review-level embeddings.
    Uses blocked matrix multiplication (not an O(n^2) Python loop or a full n x n
    matrix) so it stays fast and memory-bounded at the ~10k-review demo scale.

    Two safeguards against false positives, both learned from running this against a
    real multi-product marketplace dataset instead of a single-app one:
    - Comparison is scoped per product (when product_name is set) — two different
      customers independently praising two unrelated products in similar words are not
      duplicates of each other. Reviews with no product_name fall back to one global
      group, preserving the original single-app-dataset behavior.
    - Very short text (<15 chars, e.g. "wonderful", "good") is excluded entirely —
      embedding similarity on a couple of common words is not meaningful signal and
      flagged ~94% of a real dataset as "duplicate" before this fix.

    Sets is_duplicate / duplicate_group_id. Returns number of reviews flagged.
    """
    all_reviews = (
        db.query(Review)
        .filter(Review.dataset_id == dataset_id, Review.clean_text.isnot(None))
        .all()
    )
    reviews = [r for r in all_reviews if len(r.clean_text.strip()) >= _MIN_DUPLICATE_TEXT_LENGTH]
    if len(reviews) < 2:
        return 0

    groups_by_product: dict[str | None, list[Review]] = defaultdict(list)
    for r in reviews:
        groups_by_product[r.product_name].append(r)

    threshold = settings.duplicate_similarity_threshold
    next_group_id = 1
    flagged = 0

    for product_reviews in groups_by_product.values():
        n = len(product_reviews)
        if n < 2:
            continue

        texts = [r.clean_text for r in product_reviews]
        vectors = np.array(embed_texts(texts))
        norms = np.linalg.norm(vectors, axis=1, keepdims=True)
        norms[norms == 0] = 1e-9
        normalized = (vectors / norms).astype(np.float32)

        uf = _UnionFind(n)
        for start in range(0, n, block_size):
            end = min(start + block_size, n)
            block_sim = normalized[start:end] @ normalized.T  # (block, n)
            rows, cols = np.where(block_sim >= threshold)
            for r, c in zip(rows, cols):
                i, j = start + int(r), int(c)
                if i < j:
                    uf.union(i, j)

        group_sizes: dict[int, int] = defaultdict(int)
        for idx in range(n):
            group_sizes[uf.find(idx)] += 1

        root_to_group_id: dict[int, int] = {}
        for idx, review in enumerate(product_reviews):
            root = uf.find(idx)
            if group_sizes[root] < 2:
                continue
            if root not in root_to_group_id:
                root_to_group_id[root] = next_group_id
                next_group_id += 1
            review.is_duplicate = True
            review.duplicate_group_id = root_to_group_id[root]
            review.integrity_risk = max(review.integrity_risk, 0.6)
            flagged += 1

    db.commit()
    return flagged


def detect_rating_text_conflicts(db: Session, dataset_id: int) -> int:
    reviews = (
        db.query(Review)
        .filter(Review.dataset_id == dataset_id, Review.clean_text.isnot(None))
        .all()
    )
    flagged = 0
    for review in reviews:
        if review.rating is None:
            continue
        text_lower = review.clean_text.lower()
        has_negative_words = any(w in text_lower for w in _NEGATIVE_WORDS)
        has_positive_words = any(w in text_lower for w in _POSITIVE_WORDS)

        conflict = (review.rating >= 4 and has_negative_words and not has_positive_words) or (
            review.rating <= 2 and has_positive_words and not has_negative_words
        )
        if conflict:
            review.rating_text_conflict = True
            review.integrity_risk = max(review.integrity_risk, 0.5)
            flagged += 1
    db.commit()
    return flagged


def _detect_bursts(reviews: list[Review], window_minutes: int = 60, min_count: int = 15) -> list[BurstOut]:
    """Group reviews by day; if many duplicate-flagged reviews share a day, call it a burst.
    Demo-scale heuristic: review_date has day granularity in most datasets, so we use the day
    as the window and flag days where duplicate-group reviews cluster densely.
    """
    by_day: dict = defaultdict(list)
    for r in reviews:
        if r.review_date and r.is_duplicate:
            by_day[r.review_date].append(r)

    bursts = []
    for day, group in by_day.items():
        if len(group) >= min_count:
            ratings = [r.rating for r in group if r.rating is not None]
            dominant_rating = max(set(ratings), key=ratings.count) if ratings else None
            bursts.append(
                BurstOut(
                    window_start=day.isoformat(),
                    window_end=(day + timedelta(days=1)).isoformat(),
                    review_count=len(group),
                    dominant_rating=dominant_rating,
                    sample_texts=[g.clean_text for g in group[:5]],
                )
            )
    return sorted(bursts, key=lambda b: b.review_count, reverse=True)[:10]


def get_integrity_report(db: Session, dataset_id: int) -> IntegrityOut:
    reviews = db.query(Review).filter(Review.dataset_id == dataset_id).all()
    total = len(reviews)

    groups: dict[int, list[Review]] = defaultdict(list)
    for r in reviews:
        if r.duplicate_group_id:
            groups[r.duplicate_group_id].append(r)

    duplicate_groups = [
        DuplicateGroupOut(
            duplicate_group_id=gid,
            review_count=len(members),
            avg_similarity=settings.duplicate_similarity_threshold,
            sample_texts=[m.clean_text for m in members[:5] if m.clean_text],
        )
        for gid, members in sorted(groups.items(), key=lambda kv: -len(kv[1]))[:10]
    ]

    conflicts = [
        ConflictOut(review_id=r.id, rating=r.rating, text=r.clean_text or r.raw_text)
        for r in reviews
        if r.rating_text_conflict
    ][:20]

    bursts = _detect_bursts(reviews)

    flagged = sum(1 for r in reviews if r.is_duplicate or r.rating_text_conflict)
    flagged_percent = round(100.0 * flagged / total, 1) if total else 0.0

    return IntegrityOut(
        dataset_id=dataset_id,
        total_reviews=total,
        flagged_percent=flagged_percent,
        duplicate_groups=duplicate_groups,
        bursts=bursts,
        rating_text_conflicts=conflicts,
    )
