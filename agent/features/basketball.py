from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Sequence


@dataclass(frozen=True)
class BasketballRecord:
    team: str
    date_iso: str
    points_for: int
    points_against: int
    pace: float


def rolling_averages(
    history: Sequence[BasketballRecord], window: int = 5
) -> dict[str, float]:
    recent = list(history)[-window:]
    if not recent:
        return {"points_for": 0.0, "points_against": 0.0, "pace": 0.0, "net": 0.0}

    n = len(recent)
    pf = sum(r.points_for for r in recent) / n
    pa = sum(r.points_against for r in recent) / n
    pace = sum(r.pace for r in recent) / n
    return {"points_for": pf, "points_against": pa, "pace": pace, "net": pf - pa}


def build_basketball_features(
    match: Mapping[str, object],
    home_history: Sequence[BasketballRecord],
    away_history: Sequence[BasketballRecord],
) -> dict[str, float]:
    home = rolling_averages(home_history)
    away = rolling_averages(away_history)

    pace_avg = max((home["pace"] + away["pace"]) / 2.0, 1.0)

    return {
        "home_off_rating": home["points_for"] / pace_avg,
        "away_off_rating": away["points_for"] / pace_avg,
        "home_def_rating": home["points_against"] / pace_avg,
        "away_def_rating": away["points_against"] / pace_avg,
        "home_net_rating": home["net"],
        "away_net_rating": away["net"],
        "expected_pace": pace_avg,
        "home_team": float(hash(str(match["home_team"])) % 100) / 100.0,
    }
