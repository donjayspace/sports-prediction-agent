from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Sequence


@dataclass(frozen=True)
class TableTennisRecord:
    player: str
    won: bool
    games_won: int
    games_lost: int


def win_rate(history: Sequence[TableTennisRecord], window: int = 10) -> float:
    recent = list(history)[-window:]
    if not recent:
        return 0.5
    return sum(1 for r in recent if r.won) / len(recent)


def build_table_tennis_features(
    match: Mapping[str, object],
    home_history: Sequence[TableTennisRecord],
    away_history: Sequence[TableTennisRecord],
) -> dict[str, float]:
    home_wr = win_rate(home_history)
    away_wr = win_rate(away_history)

    home_margin = sum(
        r.games_won - r.games_lost for r in home_history[-5:]
    ) / max(len(home_history[-5:]), 1)
    away_margin = sum(
        r.games_won - r.games_lost for r in away_history[-5:]
    ) / max(len(away_history[-5:]), 1)

    return {
        "home_win_rate": home_wr,
        "away_win_rate": away_wr,
        "home_game_margin": home_margin,
        "away_game_margin": away_margin,
        "win_rate_diff": home_wr - away_wr,
    }
