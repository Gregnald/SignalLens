import logging
from dataclasses import dataclass, field

import numpy as np
from sqlalchemy.orm import Session

from app.models.feedback_unit import FeedbackUnit
from app.models.review import Review

logger = logging.getLogger(__name__)


@dataclass
class ClusterResult:
    cluster_id: int
    unit_ids: list[int]
    centroid: list[float]
    representative_texts: list[str] = field(default_factory=list)
    avg_sentiment_score: float = 0.0
    cohesion: float = 0.0


def discover_clusters(db: Session, dataset_id: int, min_cluster_size: int = 8) -> list[ClusterResult]:
    """Embeddings -> UMAP -> HDBSCAN over negative/neutral feedback units (issue candidates).
    Clusters are candidate themes only — never shown to the user raw (see theme_service).
    """
    units = (
        db.query(FeedbackUnit)
        .join(Review, FeedbackUnit.review_id == Review.id)
        .filter(
            Review.dataset_id == dataset_id,
            FeedbackUnit.embedding.isnot(None),
            FeedbackUnit.sentiment.in_(["negative", "neutral"]),
        )
        .all()
    )

    if len(units) < min_cluster_size:
        logger.info("Not enough negative/neutral units (%d) to cluster", len(units))
        return []

    vectors = np.array([u.embedding for u in units])

    import hdbscan
    import umap

    n_neighbors = min(15, max(2, len(units) - 1))
    reducer = umap.UMAP(
        n_neighbors=n_neighbors, n_components=min(10, len(units) - 2), metric="cosine", random_state=42
    )
    reduced = reducer.fit_transform(vectors)

    clusterer = hdbscan.HDBSCAN(min_cluster_size=min_cluster_size, metric="euclidean")
    labels = clusterer.fit_predict(reduced)

    clusters: dict[int, list[int]] = {}
    for idx, label in enumerate(labels):
        if label == -1:
            continue  # noise, not a theme
        clusters.setdefault(int(label), []).append(idx)

    sentiment_scores = {
        "negative": -1.0,
        "neutral": 0.0,
        "positive": 1.0,
    }

    results = []
    for cluster_id, indices in clusters.items():
        cluster_vectors = vectors[indices]
        centroid = cluster_vectors.mean(axis=0)

        dists = np.linalg.norm(cluster_vectors - centroid, axis=1)
        closest_order = np.argsort(dists)[:5]
        representative_texts = [units[indices[i]].text for i in closest_order]

        # np.linalg.norm(..., axis=1) returns an array, so `array or default` is invalid
        # (ambiguous truth value) — add a tiny epsilon instead to avoid div-by-zero.
        centroid_norm = centroid / (np.linalg.norm(centroid) + 1e-9)
        unit_norms = cluster_vectors / (np.linalg.norm(cluster_vectors, axis=1, keepdims=True) + 1e-9)
        cohesion = float(np.mean(unit_norms @ centroid_norm))

        unit_ids = [units[i].id for i in indices]
        avg_sentiment = float(
            np.mean(
                [
                    sentiment_scores.get(units[i].sentiment, 0.0) * (units[i].sentiment_score or 0.5)
                    for i in indices
                ]
            )
        )

        results.append(
            ClusterResult(
                cluster_id=cluster_id,
                unit_ids=unit_ids,
                centroid=centroid.tolist(),
                representative_texts=representative_texts,
                avg_sentiment_score=avg_sentiment,
                cohesion=cohesion,
            )
        )

    return results
