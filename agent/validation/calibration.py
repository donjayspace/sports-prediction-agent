from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from sklearn.isotonic import IsotonicRegression


@dataclass
class _Calibrator:
    home: IsotonicRegression
    draw: IsotonicRegression
    away: IsotonicRegression


class ProbabilityCalibrator:
    """Per-class isotonic calibration for 1X2 probability triples."""

    def __init__(self) -> None:
        self._calibrator: _Calibrator | None = None

    def fit(
        self,
        y_home: np.ndarray,
        y_draw: np.ndarray,
        y_away: np.ndarray,
        p_home: np.ndarray,
        p_draw: np.ndarray,
        p_away: np.ndarray,
    ) -> None:
        def _fit(y: np.ndarray, p: np.ndarray) -> IsotonicRegression:
            model = IsotonicRegression(out_of_bounds="clip")
            model.fit(p, y)
            return model

        self._calibrator = _Calibrator(
            home=_fit(y_home, p_home),
            draw=_fit(y_draw, p_draw),
            away=_fit(y_away, p_away),
        )

    def calibrate(self, home: float, draw: float, away: float) -> tuple[float, float, float]:
        if self._calibrator is None:
            raise RuntimeError("Calibrator has not been fitted")

        c_home = float(self._calibrator.home.predict(np.array([home]))[0])
        c_draw = float(self._calibrator.draw.predict(np.array([draw]))[0])
        c_away = float(self._calibrator.away.predict(np.array([away]))[0])

        total = c_home + c_draw + c_away
        if total <= 0:
            return home, draw, away
        return c_home / total, c_draw / total, c_away / total
