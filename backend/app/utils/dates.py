from datetime import date, timedelta

from app.utils.metrics import z_score


def daily_volume(dates: list[date]) -> dict[date, int]:
    counts: dict[date, int] = {}
    for d in dates:
        if d is None:
            continue
        counts[d] = counts.get(d, 0) + 1
    return counts


def rolling_baseline_and_current(
    counts: dict[date, int], baseline_days: int, current_days: int = 7
) -> tuple[float, float, float]:
    """Returns (baseline_mean, baseline_std, current_window_total)."""
    if not counts:
        return 0.0, 0.0, 0.0

    all_dates = sorted(counts.keys())
    latest = all_dates[-1]

    current_start = latest - timedelta(days=current_days - 1)
    baseline_start = current_start - timedelta(days=baseline_days)
    baseline_end = current_start - timedelta(days=1)

    baseline_series = []
    d = baseline_start
    while d <= baseline_end:
        baseline_series.append(counts.get(d, 0))
        d += timedelta(days=1)

    current_total = sum(
        counts.get(current_start + timedelta(days=i), 0) for i in range(current_days)
    )

    if not baseline_series:
        return 0.0, 0.0, float(current_total)

    mean = sum(baseline_series) / len(baseline_series)
    variance = sum((x - mean) ** 2 for x in baseline_series) / max(len(baseline_series), 1)
    std = variance**0.5

    baseline_total_equivalent = mean * current_days
    return baseline_total_equivalent, std * current_days, float(current_total)


def detect_change_point(counts: dict[date, int]) -> date | None:
    """Naive change-point: first day where volume jumps >2 std above the running mean."""
    if len(counts) < 4:
        return None
    all_dates = sorted(counts.keys())
    values = [counts[d] for d in all_dates]

    for i in range(3, len(values)):
        window = values[:i]
        mean = sum(window) / len(window)
        std = (sum((x - mean) ** 2 for x in window) / len(window)) ** 0.5

        if std <= 1e-9:
            # Perfectly flat baseline: z-score is undefined, so fall back to an
            # absolute-jump check rather than silently reporting "no change".
            if values[i] > mean and values[i] >= max(3, mean + 2):
                return all_dates[i]
            continue

        z = z_score(values[i], mean, std)
        if z >= 2.0 and values[i] >= 3:
            return all_dates[i]
    return None
