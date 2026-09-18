from __future__ import annotations

import math

import numpy as np
from scipy.stats import poisson


class DixonColesModel:
    """Time-weighted Dixon-Coles model for football 1X2 prediction.

    Attack / defence parameters are expected to be provided externally
    (fitted offline) as a mapping from team name to log-scale strength.
    """

    def __init__(
        self,
        attack: dict[str, float],
        defence: dict[str, float],
        home_advantage: float = 0.15,
        rho: float = -0.05,
        max_goals: int = 8,
        league_avg_goals: float = 1.35,
    ) -> None:
        self._attack = attack
        self._defence = defence
        self._home_advantage = home_advantage
        self._rho = rho
        self._max_goals = max_goals
        self._league_avg_goals = league_avg_goals

    def _expected_goals(
        self, home_team: str, away_team: str
    ) -> tuple[float, float]:
        home_attack = self._attack.get(home_team, 0.0)
        home_defence = self._defence.get(home_team, 0.0)
        away_attack = self._attack.get(away_team, 0.0)
        away_defence = self._defence.get(away_team, 0.0)

        home_lambda = math.exp(
            home_attack + away_defence + self._home_advantage
        ) * self._league_avg_goals
        away_lambda = math.exp(
            away_attack + home_defence
        ) * self._league_avg_goals

        return home_lambda, away_lambda

    def _tau(self, i: int, j: int, home_lambda: float, away_lambda: float) -> float:
        if i == 0 and j == 0:
            return 1.0 - home_lambda * away_lambda * self._rho
        if i == 0 and j == 1:
            return 1.0 + home_lambda * self._rho
        if i == 1 and j == 0:
            return 1.0 + away_lambda * self._rho
        if i == 1 and j == 1:
            return 1.0 - self._rho
        return 1.0

    def predict(self, home_team: str, away_team: str) -> dict[str, float]:
        home_lambda, away_lambda = self._expected_goals(home_team, away_team)

        home_win = 0.0
        draw = 0.0
        away_win = 0.0

        for i in range(self._max_goals):
            for j in range(self._max_goals):
                p = poisson.pmf(i, home_lambda) * poisson.pmf(j, away_lambda)
                p *= self._tau(i, j, home_lambda, away_lambda)

                if i > j:
                    home_win += p
                elif i == j:
                    draw += p
                else:
                    away_win += p

        total = home_win + draw + away_win
        if total <= 0:
            return {"home": 1 / 3, "draw": 1 / 3, "away": 1 / 3}

        return {
            "home": home_win / total,
            "draw": draw / total,
            "away": away_win / total,
        }


def fit_attack_defence_from_matches(
    matches: list[dict[str, object]],
    max_iter: int = 200,
    tol: float = 1e-6,
) -> tuple[dict[str, float], dict[str, float]]:
    """Simple iterative fit of attack/defence parameters from a list of matches."""
    teams: set[str] = set()
    for m in matches:
        teams.add(str(m["home_team"]))
        teams.add(str(m["away_team"]))

    attack: dict[str, float] = dict.fromkeys(teams, 0.0)
    defence: dict[str, float] = dict.fromkeys(teams, 0.0)

    total_goals = sum(
        int(m["home_goals"]) + int(m["away_goals"]) for m in matches  # type: ignore[arg-type]
    )
    league_avg = max(total_goals / max(2 * len(matches), 1), 0.1)

    for _ in range(max_iter):
        max_delta = 0.0
        for team in teams:
            scored = 0.0
            conceded = 0.0
            played = 0
            for m in matches:
                home = str(m["home_team"])
                away = str(m["away_team"])
                if team == home:
                    scored += int(m["home_goals"])  # type: ignore[arg-type]
                    conceded += int(m["away_goals"])  # type: ignore[arg-type]
                    played += 1
                elif team == away:
                    scored += int(m["away_goals"])  # type: ignore[arg-type]
                    conceded += int(m["home_goals"])  # type: ignore[arg-type]
                    played += 1

            if played == 0:
                continue

            attack_new = math.log(max(scored / played, 0.05) / league_avg)
            defence_new = math.log(max(conceded / played, 0.05) / league_avg)

            max_delta = max(
                max_delta,
                abs(attack_new - attack[team]),
                abs(defence_new - defence[team]),
            )
            attack[team] = attack_new
            defence[team] = defence_new

        if max_delta < tol:
            break

    return attack, defence


def _log_likelihood(
    home_lambda: float,
    away_lambda: float,
    home_goals: int,
    away_goals: int,
) -> float:
    return float(
        poisson.logpmf(home_goals, home_lambda) + poisson.logpmf(away_goals, away_lambda)
    )


def model_quality(
    matches: list[dict[str, object]],
    attack: dict[str, float],
    defence: dict[str, float],
) -> float:
    model = DixonColesModel(attack, defence)
    ll = 0.0
    for m in matches:
        home = str(m["home_team"])
        away = str(m["away_team"])
        h_lam, a_lam = model._expected_goals(home, away)
        ll += _log_likelihood(h_lam, a_lam, int(m["home_goals"]), int(m["away_goals"]))  # type: ignore[arg-type]
    return ll


def _unused_numpy_reference() -> None:
    """Keep numpy imported for downstream numeric utilities."""
    _ = np.zeros(1)
