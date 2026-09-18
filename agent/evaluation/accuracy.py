from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

OUTCOMES: tuple[str, ...] = ("home", "draw", "away")


def argmax_outcome(probs: dict[str, float]) -> str:
    return max(OUTCOMES, key=lambda o: probs[o])


@dataclass(frozen=True)
class AccuracyResult:
    n: int
    correct: int
    accuracy: float


def compute_accuracy(
    predictions: Sequence[dict[str, float]],
    actuals: Sequence[str],
) -> AccuracyResult:
    if len(predictions) != len(actuals):
        raise ValueError("Predictions and actuals must be same length")

    correct = sum(
        1
        for probs, actual in zip(predictions, actuals, strict=True)
        if argmax_outcome(probs) == actual
    )
    n = len(actuals)
    return AccuracyResult(n=n, correct=correct, accuracy=correct / n if n else 0.0)
