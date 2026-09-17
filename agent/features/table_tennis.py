from dataclasses import dataclass


@dataclass(frozen=True)
class TableTennisFeatures:
    """Point-in-time features for table-tennis research models.

    Values must come from data available before prediction_time. Missing fields remain None
    rather than being guessed, which protects the pipeline from silent leakage/hallucination.
    """

    ranking_a: float | None = None
    ranking_b: float | None = None
    elo_a: float | None = None
    elo_b: float | None = None
    recent_match_win_rate_a: float | None = None
    recent_match_win_rate_b: float | None = None
    game_win_rate_a: float | None = None
    game_win_rate_b: float | None = None
    point_win_rate_a: float | None = None
    point_win_rate_b: float | None = None
    rest_hours_a: float | None = None
    rest_hours_b: float | None = None
    h2h_win_rate_a: float | None = None


def to_model_vector(features: TableTennisFeatures) -> list[float | None]:
    """Provide a stable feature ordering for downstream models."""
    return list(features.__dict__.values())
