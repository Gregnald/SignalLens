import math

import numpy as np


def clamp(value: float, low: float = 0.0, high: float = 100.0) -> float:
    return max(low, min(high, value))


def normalize(value: float, min_value: float, max_value: float) -> float:
    """Linearly map value into [0, 100] given an expected [min_value, max_value] range."""
    if max_value <= min_value:
        return 0.0
    return clamp(100.0 * (value - min_value) / (max_value - min_value))


def growth_percent(baseline: float, current: float) -> float | None:
    if baseline <= 0:
        return None if current == 0 else 999.0
    return round(100.0 * (current - baseline) / baseline, 1)


def z_score(value: float, mean: float, std: float) -> float:
    if std <= 1e-9:
        return 0.0
    return (value - mean) / std


def cosine_similarity(a: list[float], b: list[float]) -> float:
    va, vb = np.array(a), np.array(b)
    denom = (np.linalg.norm(va) * np.linalg.norm(vb)) or 1e-9
    return float(np.dot(va, vb) / denom)


SEVERITY_WEIGHT = {"critical": 100.0, "high": 75.0, "medium": 45.0, "low": 15.0}


def impact_score(
    volume_score: float,
    growth_score: float,
    severity_score: float,
    negative_sentiment_score: float,
    reach_score: float,
    confidence_score: float,
) -> float:
    """ARCHITECTURE.md §12 — weighted 0-100 impact score."""
    score = (
        0.25 * volume_score
        + 0.20 * growth_score
        + 0.25 * severity_score
        + 0.10 * negative_sentiment_score
        + 0.10 * reach_score
        + 0.10 * confidence_score
    )
    return round(clamp(score), 1)


def safe_mean(values: list[float]) -> float | None:
    values = [v for v in values if v is not None and not math.isnan(v)]
    if not values:
        return None
    return sum(values) / len(values)
