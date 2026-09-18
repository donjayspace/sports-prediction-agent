from __future__ import annotations

import math


def _poisson_pmf(lam: float, goals: int) -> float:
    return math.exp(-lam) * (lam ** goals) / math.factorial(goals)


def outcome_distribution(home_xg: float, away_xg: float, max_goals: int = 8) -> dict[str, float]:
    """Convert expected goals into a normalized 1X2 research forecast.

    This baseline intentionally exposes assumptions rather than pretending to be a
    fitted Dixon-Coles implementation. A trained model can replace this function
    without changing downstream forecast contracts.
    """
    if home_xg <= 0 or away_xg <= 0:
        raise ValueError("expected goals must be positive")
    home = [_poisson_pmf(home_xg, i) for i in range(max_goals + 1)]
    away = [_poisson_pmf(away_xg, i) for i in range(max_goals + 1)]
    home_win = draw = away_win = 0.0
    for h, hp in enumerate(home):
        for a, ap in enumerate(away):
            probability = hp * ap
            if h > a:
                home_win += probability
            elif h == a:
                draw += probability
            else:
                away_win += probability
    total = home_win + draw + away_win
    return {"home": home_win / total, "draw": draw / total, "away": away_win / total}
