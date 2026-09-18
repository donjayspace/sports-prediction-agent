from __future__ import annotations

from typing import Protocol, Sequence

from agent.features.football import build_football_features


class SupportsPredictProba(Protocol):
    def predict_proba(self, X: Sequence[Sequence[float]]) -> Sequence[Sequence[float]]: ...


class FootballXGBoostModel:
    """Thin wrapper that converts engineered features into class probabilities."""

    FEATURE_ORDER: tuple[str, ...] = (
        "home_ppg_l5",
        "away_ppg_l5",
        "home_goals_for_l5",
        "home_goals_against_l5",
        "away_goals_for_l5",
        "away_goals_against_l5",
        "h2h_home_win_rate",
        "home_attack_strength",
        "away_attack_strength",
    )

    def __init__(self, estimator: SupportsPredictProba) -> None:
        self._estimator = estimator

    def predict_from_features(self, features: dict[str, float]) -> dict[str, float]:
        row = [features[name] for name in self.FEATURE_ORDER]
        proba = self._estimator.predict_proba([row])[0]
        return {
            "home": float(proba[0]),
            "draw": float(proba[1]),
            "away": float(proba[2]),
        }


def build_feature_matrix(
    matches: Sequence[dict[str, object]],
    home_histories: dict[str, list[object]],
    away_histories: dict[str, list[object]],
) -> list[list[float]]:
    matrix: list[list[float]] = []
    for m in matches:
        home_team = str(m["home_team"])
        away_team = str(m["away_team"])
        features = build_football_features(
            m,
            home_histories.get(home_team, []),  # type: ignore[arg-type]
            away_histories.get(away_team, []),  # type: ignore[arg-type]
            [],  # type: ignore[arg-type]
        )
        matrix.append([features[name] for name in FootballXGBoostModel.FEATURE_ORDER])
    return matrix
