from app.utils.metrics import (
    clamp,
    cosine_similarity,
    growth_percent,
    impact_score,
    normalize,
    safe_mean,
    z_score,
)


def test_clamp_bounds():
    assert clamp(150) == 100
    assert clamp(-10) == 0
    assert clamp(50) == 50


def test_normalize_linear_mapping():
    assert normalize(50, 0, 100) == 50
    assert normalize(0, 0, 100) == 0
    assert normalize(100, 0, 100) == 100
    assert normalize(5, 10, 0) == 0  # degenerate range -> 0


def test_growth_percent_from_architecture_example():
    # ARCHITECTURE.md §16 demo example: 149 -> 487 is roughly +227%
    g = growth_percent(149, 487)
    assert 220 <= g <= 235


def test_growth_percent_zero_baseline():
    assert growth_percent(0, 0) is None
    assert growth_percent(0, 10) == 999.0


def test_z_score_zero_std_is_zero():
    assert z_score(10, 5, 0) == 0.0


def test_cosine_similarity_identical_vectors():
    v = [1.0, 2.0, 3.0]
    assert abs(cosine_similarity(v, v) - 1.0) < 1e-9


def test_cosine_similarity_orthogonal_vectors():
    assert abs(cosine_similarity([1.0, 0.0], [0.0, 1.0])) < 1e-9


def test_impact_score_weights_sum_and_range():
    # all inputs maxed out -> must hit 100
    assert impact_score(100, 100, 100, 100, 100, 100) == 100.0
    # all inputs zero -> must be 0
    assert impact_score(0, 0, 0, 0, 0, 0) == 0.0


def test_impact_score_architecture_example():
    # ARCHITECTURE.md §22 example: Payment Failure -> impact ~94
    score = impact_score(
        volume_score=82,
        growth_score=97,
        severity_score=100,
        negative_sentiment_score=94,
        reach_score=88,
        confidence_score=95,
    )
    assert 90 <= score <= 97


def test_safe_mean_ignores_none_and_nan():
    assert safe_mean([1.0, None, 3.0]) == 2.0
    assert safe_mean([]) is None
