from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

import httpx
from pydantic import BaseModel, Field, field_validator


class RawFixture(BaseModel):
    external_id: str
    sport: str
    league: str
    home_team: str
    away_team: str
    kickoff_utc: datetime

    @field_validator("home_team", "away_team", "league")
    @classmethod
    def non_empty(cls, v: str) -> str:
        stripped = v.strip()
        if not stripped:
            raise ValueError("Field must not be empty")
        return stripped

    @field_validator("kickoff_utc")
    @classmethod
    def must_be_future(cls, v: datetime) -> datetime:
        if v.tzinfo is None:
            v = v.replace(tzinfo=timezone.utc)
        return v


class FixtureCollector:
    def __init__(self, base_url: str, timeout: float = 15.0) -> None:
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout

    async def fetch_upcoming(self, sport: str, days: int = 7) -> list[RawFixture]:
        async with httpx.AsyncClient(timeout=self._timeout) as client:
            resp = await client.get(
                f"{self._base_url}/matches",
                params={"sport": sport, "status": "upcoming", "days": days},
                headers={"User-Agent": "sports-prediction-agent/0.1"},
            )
            resp.raise_for_status()
            payload: dict[str, Any] = resp.json()

        raw_matches = payload.get("matches", [])
        if not isinstance(raw_matches, list):
            raise ValueError("Unexpected payload shape: 'matches' is not a list")

        fixtures: list[RawFixture] = []
        for item in raw_matches:
            if not isinstance(item, dict):
                continue
            try:
                fixtures.append(
                    RawFixture(
                        external_id=str(item["id"]),
                        sport=sport,
                        league=str(item["league"]),
                        home_team=str(item["home_team"]),
                        away_team=str(item["away_team"]),
                        kickoff_utc=datetime.fromisoformat(str(item["kickoff_utc"])),
                    )
                )
            except (KeyError, ValueError):
                continue
        return fixtures
