from __future__ import annotations

import math
from typing import Sequence

EPSILON = 1e-12


def log_loss(
    predictions: Sequence[dict[str, float]],
    actuals: Sequence[str],
) -> float:
    if not predictions:
        return 0.0

    total = 0.0
    for probs, actual in zip(predictions, actuals, strict=True):
        p = max(min(probs[actual], 1.0 - EPSILON), EPSILON)
        total -= math.log(p)
    return total / len(predictions)
