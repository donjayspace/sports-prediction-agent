from __future__ import annotations


def weighted_average(distributions: list[tuple[dict[str, float], float]]) -> dict[str, float]:
    """Combine compatible probability distributions using normalized model weights."""
    if not distributions:
        raise ValueError("at least one distribution is required")
    total_weight = sum(weight for _, weight in distributions)
    if total_weight <= 0:
        raise ValueError("model weights must contain positive mass")
    outcomes = set().union(*(distribution.keys() for distribution, _ in distributions))
    combined = {
        outcome: sum(distribution.get(outcome, 0.0) * weight for distribution, weight in distributions) / total_weight
        for outcome in outcomes
    }
    total = sum(combined.values())
    return {outcome: probability / total for outcome, probability in combined.items()}
