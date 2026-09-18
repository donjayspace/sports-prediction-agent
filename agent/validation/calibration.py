from __future__ import annotations

from collections.abc import Iterable


def multiclass_brier(probabilities: dict[str, float], actual: str) -> float:
    """Multiclass Brier score; lower values indicate better probabilistic forecasts."""
    if not probabilities:
        raise ValueError("probabilities cannot be empty")
    return sum((p - (1.0 if outcome == actual else 0.0)) ** 2 for outcome, p in probabilities.items())


def multiclass_log_loss(probabilities: dict[str, float], actual: str, floor: float = 1e-15) -> float:
    """Log loss with a small floor to avoid undefined log(0)."""
    import math
    probability = max(float(probabilities.get(actual, 0.0)), floor)
    return -math.log(probability)


def reliability_bins(records: Iterable[tuple[float, bool]], bins: int = 10) -> list[dict[str, float | int]]:
    """Build confidence/reliability bins for calibration inspection."""
    if bins < 1:
        raise ValueError("bins must be positive")
    grouped = [[] for _ in range(bins)]
    for confidence, correct in records:
        index = min(int(confidence * bins), bins - 1)
        grouped[index].append((confidence, correct))
    output = []
    for index, group in enumerate(grouped):
        if not group:
            continue
        output.append({
            "bin": index,
            "count": len(group),
            "mean_confidence": sum(x for x, _ in group) / len(group),
            "observed_accuracy": sum(1 for _, ok in group if ok) / len(group),
        })
    return output
