from datetime import date, timedelta

from app.utils.dates import daily_volume, detect_change_point, rolling_baseline_and_current


def _dates_from_offsets(offsets: list[int], start: date) -> list[date]:
    return [start + timedelta(days=o) for o in offsets]


def test_daily_volume_counts_per_day():
    start = date(2026, 9, 1)
    dates = _dates_from_offsets([0, 0, 1, 2, 2, 2], start)
    counts = daily_volume(dates)
    assert counts[start] == 2
    assert counts[start + timedelta(days=1)] == 1
    assert counts[start + timedelta(days=2)] == 3


def test_rolling_baseline_detects_spike():
    start = date(2026, 9, 1)
    counts = {}
    # 28 days of low, steady baseline volume (~2/day)
    for i in range(28):
        counts[start + timedelta(days=i)] = 2
    # then a 7-day spike window
    spike_start = start + timedelta(days=28)
    for i in range(7):
        counts[spike_start + timedelta(days=i)] = 15

    baseline, std, current = rolling_baseline_and_current(counts, baseline_days=28, current_days=7)
    assert current == 105  # 15 * 7
    assert baseline < current


def test_detect_change_point_finds_jump():
    start = date(2026, 9, 1)
    counts = {start + timedelta(days=i): 3 for i in range(10)}
    counts[start + timedelta(days=10)] = 40  # sharp jump
    change_point = detect_change_point(counts)
    assert change_point == start + timedelta(days=10)


def test_detect_change_point_none_when_flat():
    start = date(2026, 9, 1)
    counts = {start + timedelta(days=i): 5 for i in range(15)}
    assert detect_change_point(counts) is None
