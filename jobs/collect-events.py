from __future__ import annotations

import asyncio
import os
import sys
from datetime import datetime, timezone

import httpx

API_URL = os.environ.get("API_PUBLIC_URL", "http://localhost:3001")
SPORTSCORE_BASE = os.environ.get("SPORTSCORE_API_BASE", "https://sportscore.com/api")
SERVICE_TOKEN = os.environ.get("AGENT_SERVICE_TOKEN", "")


async def collect(sport: str, days: int) -> int:
    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.get(
            f"{SPORTSCORE_BASE}/matches",
            params={"sport": sport, "status": "upcoming", "days": days},
        )
        resp.raise_for_status()
        payload = resp.json()

    matches = payload.get("matches", [])
    created = 0

    async with httpx.AsyncClient(timeout=30.0) as client:
        for m in matches:
            try:
                body = {
                    "externalId": str(m["id"]),
                    "sport": sport.upper(),
                    "league": str(m["league"]),
                    "homeTeamName": str(m["home_team"]),
                    "awayTeamName": str(m["away_team"]),
                    "kickoffUtc": str(m["kickoff_utc"]),
                }
                resp = await client.post(
                    f"{API_URL}/api/fixtures/ingest",
                    json=body,
                    headers={"X-Service-Token": SERVICE_TOKEN},
                )
                if resp.status_code in (200, 201):
                    created += 1
            except (KeyError, httpx.HTTPError):
                continue

    return created


async def main() -> None:
    sport = sys.argv[1] if len(sys.argv) > 1 else "football"
    days = int(sys.argv[2]) if len(sys.argv) > 2 else 7

    started = datetime.now(timezone.utc)
    count = await collect(sport, days)
    elapsed = (datetime.now(timezone.utc) - started).total_seconds()

    print(f"[collect-events] sport={sport} days={days} created={count} elapsed={elapsed:.2f}s")


if __name__ == "__main__":
    asyncio.run(main())
