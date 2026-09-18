from __future__ import annotations

import httpx
from pydantic import BaseModel


class Ranking(BaseModel):
    team: str
    rank: int
    points: float


class RankingCollector:
    def __init__(self, base_url: str, timeout: float = 15.0) -> None:
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout

    async def fetch(self, sport: str) -> list[Ranking]:
        async with httpx.AsyncClient(timeout=self._timeout) as client:
            resp = await client.get(
                f"{self._base_url}/rankings",
                params={"sport": sport},
                headers={"User-Agent": "sports-prediction-agent/0.1"},
            )
            resp.raise_for_status()
            data = resp.json()

        rankings: list[Ranking] = []
        for entry in data.get("rankings", []):
            try:
                rankings.append(
                    Ranking(
                        team=str(entry["team"]),
                        rank=int(entry["rank"]),
                        points=float(entry.get("points", 0.0)),
                    )
                )
            except (KeyError, ValueError, TypeError):
                continue
        return rankings
