from __future__ import annotations

from agent.ai.schemas import ResearchRequest
from agent.core.config import settings
from agent.models.football.dixon_coles import DixonColesModel


class ModelAnalyzer:
    """Runs the statistical model layer for a given fixture."""

    def __init__(self, dixon_coles: DixonColesModel | None = None) -> None:
        self._dixon_coles = dixon_coles
        self._version = settings.model_version

    @property
    def version(self) -> str:
        return self._version

    async def predict(self, req: ResearchRequest) -> dict[str, float]:
        if req.sport != "football":
            return {"home": 1 / 3, "draw": 1 / 3, "away": 1 / 3}

        if self._dixon_coles is None:
            return {"home": 0.45, "draw": 0.28, "away": 0.27}

        return self._dixon_coles.predict(req.home_team, req.away_team)
