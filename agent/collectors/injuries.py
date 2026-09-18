from __future__ import annotations

import httpx
from pydantic import BaseModel


class Injury(BaseModel):
    team: str
    player: str
    status: str
    note: str | None = None


class InjuryCollector:
    def __init__(self, base_url: str, timeout: float = 15.0) -> None:
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout

    async def fetch(self, sport: str, team: str) -> list[Injury]:
        async with httpx.AsyncClient(timeout=self._timeout) as client:
            resp = await client.get(
                f"{self._base_url}/injuries",
                params={"sport": sport, "team": team},
                headers={"User-Agent": "sports-prediction-agent/0.1"},
            )
            resp.raise_for_status()
            data = resp.json()

        injuries: list[Injury] = []
        for entry in data.get("injuries", []):
            try:
                injuries.append(
                    Injury(
                        team=team,
                        player=str(entry["player"]),
                        status=str(entry["status"]),
                        note=str(entry["note"]) if entry.get("note") else None,
                    )
                )
            except (KeyError, ValueError, TypeError):
                continue
        return injuries
