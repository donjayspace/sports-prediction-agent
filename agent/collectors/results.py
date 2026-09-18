from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

import httpx
from pydantic import BaseModel, field_validator


class RawResult(BaseModel):
    external_id: str
    home_score: int
    away_score: int
    completed_at: datetime

    @field_validator("home_score", "away_score")
    @classmethod
    def non_negative(cls, v: int) -> int:
        if v < 0:
            raise ValueError("Scores must be non-negative")
        return v


class ResultCollector:
    def __init__(self, base_url: str, timeout: float = 15.0) -> None:
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout

    async def fetch_completed(self, sport: str, days_back: int = 3) -> list[RawResult]:
        async with httpx.AsyncClient(timeout=self._timeout) as client:
            resp = await client.get(
                f"{self._base_url}/results",
                params={"sport": sport, "days": days_back},
                headers={"User-Agent": "sports-prediction-agent/0.1"},
            )
            resp.raise_for_status()
            payload: dict[str, Any] = resp.json()

        results: list[RawResult] = []
        for item in payload.get("results", []):
            if not isinstance(item, dict):
                continue
            try:
                results.append(
                    RawResult(
                        external_id=str(item["id"]),
                        home_score=int(item["home_score"]),
                        away_score=int(item["away_score"]),
                        completed_at=datetime.fromisoformat(str(item["completed_at"])),
                    )
                )
            except (KeyError, ValueError):
                continue
        return results
