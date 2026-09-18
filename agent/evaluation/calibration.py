from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

OUTCOMES: tuple[str, ...] = ("home", "draw", "away")


@dataclass(frozen=True)
class CalibrationBin:
    bin_index: int
    predicted_mean: float
    observed_rate: float
    count: int


def reliability_bins(
    predictions: Sequence[dict[str, float]],
    actuals: Sequence[str],
    n_bins: int = 10,
) -> list[CalibrationBin]:
    buckets: list[list[tuple[float, float]]] = [[] for _ in range(n_bins)]

    for probs, actual in zip(predictions, actuals, strict=True):
        for outcome in OUTCOMES:
            p = probs[outcome]
            y = 1.0 if outcome == actual else 0.0
            idx = min(int(p * n_bins), n_bins - 1)
            buckets[idx].append((p, y))

    result: list[CalibrationBin] = []
    for i, bucket in enumerate(buckets):
        if not bucket:
            continue
        n = len(bucket)
        p_mean = sum(p for p, _ in bucket) / n
        y_rate = sum(y for _, y in bucket) / n
        result.append(
            CalibrationBin(
                bin_index=i,
                predicted_mean=p_mean,
                observed_rate=y_rate,
                count=n,
            )
        )
    return result


def expected_calibration_error(
    predictions: Sequence[dict[str, float]],
    actuals: Sequence[str],
    n_bins: int = 10,
) -> float:
    total = len(predictions) * len(OUTCOMES)
    if total == 0:
        return 0.0

    bins = reliability_bins(predictions, actuals, n_bins)
    ece = sum(
        (b.count / total) * abs(b.predicted_mean - b.observed_rate) for b in bins
    )
    return ece
