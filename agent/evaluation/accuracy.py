from __future__ import annotations


def accuracy(predictions: list[str], actuals: list[str]) -> float:
    if len(predictions) != len(actuals) or not actuals:
        raise ValueError("predictions and actuals must have equal non-zero length")
    return sum(p == a for p, a in zip(predictions, actuals)) / len(actuals)
