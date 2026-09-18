from __future__ import annotations

from agent.ai.schemas import ProbabilityTriple


def is_valid(triple: ProbabilityTriple, tolerance: float = 1e-4) -> bool:
    total = triple.home + triple.draw + triple.away
    return abs(total - 1.0) < tolerance and min(triple.home, triple.draw, triple.away) >= 0.0


def normalise_or_raise(triple: ProbabilityTriple) -> ProbabilityTriple:
    total = triple.home + triple.draw + triple.away
    if total <= 0:
        raise ValueError("Probability triple sums to zero")
    return ProbabilityTriple(
        home=triple.home / total,
        draw=triple.draw / total,
        away=triple.away / total,
    )
