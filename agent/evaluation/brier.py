from __future__ import annotations

from typing import Sequence

OUTCOMES: tuple[str, ...] = ("home", "draw", "away")


def brier_score(
    predictions: Sequence[dict[str, float]],
    actuals: Sequence[str],
) -> float:
    if not predictions:
        return 0.0

    total = 0.0
    for probs, actual in zip(predictions, actuals, strict=True):
        for outcome in OUTCOMES:
            y = 1.0 if outcome == actual else 0.0
            total += (probs[outcome] - y) ** 2
    return total / len(predictions)
