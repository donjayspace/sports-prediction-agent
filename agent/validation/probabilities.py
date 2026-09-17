from math import isfinite


def validate_distribution(probabilities: dict[str, float], tolerance: float = 1e-6) -> dict[str, float]:
    """Reject invalid probability distributions before persistence or evaluation."""
    if not probabilities:
        raise ValueError("probability distribution cannot be empty")
    if any(not isfinite(v) or v < 0 or v > 1 for v in probabilities.values()):
        raise ValueError("probabilities must be finite values between 0 and 1")
    total = sum(probabilities.values())
    if abs(total - 1.0) > tolerance:
        raise ValueError(f"probabilities must sum to 1; received {total}")
    return probabilities
