from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Sequence


@dataclass(frozen=True)
class TennisRecord:
    player: str
    surface: str
    won: bool
    serve_points_won: float
    return_points_won: float
    elo: float


def surface_win_rate(
    history: Sequence[TennisRecord], surface: str, window: int = 20
) -> float:
    relevant = [r for r in history if r.surface == surface][-window:]
    if not relevant:
        return 0.5
    return sum(1 for r in relevant if r.won) / len(relevant)


def build_tennis_features(
    match: Mapping[str, object],
    home_history: Sequence[TennisRecord],
    away_history: Sequence[TennisRecord],
    surface: str,
) -> dict[str, float]:
    home_elo = home_history[-1].elo if home_history else 1500.0
    away_elo = away_history[-1].elo if away_history else 1500.0

    home_srv = (
        sum(r.serve_points_won for r in home_history[-5:]) / max(len(home_history[-5:]), 1)
    )
    away_srv = (
        sum(r.serve_points_won for r in away_history[-5:]) / max(len(away_history[-5:]), 1)
    )
    home_ret = (
        sum(r.return_points_won for r in home_history[-5:]) / max(len(home_history[-5:]), 1)
    )
    away_ret = (
        sum(r.return_points_won for r in away_history[-5:]) / max(len(away_history[-5:]), 1)
    )

    return {
        "home_elo": home_elo,
        "away_elo": away_elo,
        "elo_diff": home_elo - away_elo,
        "home_surface_wr": surface_win_rate(home_history, surface),
        "away_surface_wr": surface_win_rate(away_history, surface),
        "home_serve_pts_won": home_srv,
        "away_serve_pts_won": away_srv,
        "home_return_pts_won": home_ret,
        "away_return_pts_won": away_ret,
    }
