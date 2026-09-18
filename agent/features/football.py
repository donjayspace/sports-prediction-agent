from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Sequence


@dataclass(frozen=True)
class TeamMatchRecord:
    team: str
    date_iso: str
    goals_for: int
    goals_against: int
    points: int


def rolling_form(history: Sequence[TeamMatchRecord], window: int = 5) -> dict[str, float]:
    recent = list(history)[-window:]
    if not recent:
        return {"points_per_game": 0.0, "goals_for": 0.0, "goals_against": 0.0}

    n = len(recent)
    return {
        "points_per_game": sum(m.points for m in recent) / n,
        "goals_for": sum(m.goals_for for m in recent) / n,
        "goals_against": sum(m.goals_against for m in recent) / n,
    }


def head_to_head_rate(
    history: Sequence[TeamMatchRecord],
    home_team: str,
    away_team: str,
    window: int = 10,
) -> float:
    """Fraction of recent H2H matches won by the given home team."""
    h2h = [m for m in history if m.team in (home_team, away_team)][-window:]
    if not h2h:
        return 0.5
    wins = sum(1 for m in h2h if m.team == home_team and m.points == 3)
    return wins / len(h2h)


def build_football_features(
    match: Mapping[str, object],
    home_history: Sequence[TeamMatchRecord],
    away_history: Sequence[TeamMatchRecord],
    full_history: Sequence[TeamMatchRecord],
) -> dict[str, float]:
    home_form = rolling_form(home_history)
    away_form = rolling_form(away_history)

    home_team = str(match["home_team"])
    away_team = str(match["away_team"])

    return {
        "home_ppg_l5": home_form["points_per_game"],
        "away_ppg_l5": away_form["points_per_game"],
        "home_goals_for_l5": home_form["goals_for"],
        "home_goals_against_l5": home_form["goals_against"],
        "away_goals_for_l5": away_form["goals_for"],
        "away_goals_against_l5": away_form["goals_against"],
        "h2h_home_win_rate": head_to_head_rate(full_history, home_team, away_team),
        "home_attack_strength": max(home_form["goals_for"] - away_form["goals_against"], 0.1),
        "away_attack_strength": max(away_form["goals_for"] - home_form["goals_against"], 0.1),
    }
