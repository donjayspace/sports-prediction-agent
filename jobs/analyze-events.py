from __future__ import annotations

import asyncio
import os
from datetime import datetime, timezone

import httpx

API_URL = os.environ.get("API_PUBLIC_URL", "http://localhost:3001")
AGENT_URL = os.environ.get("AGENT_URL", "http://localhost:8000")
SERVICE_TOKEN = os.environ.get("AGENT_SERVICE_TOKEN", "")

CONCURRENCY = 4


async def analyze_one(client: httpx.AsyncClient, fixture: dict[str, object]) -> bool:
    payload = {
        "fixture_id": fixture["id"],
        "sport": str(fixture["sport"]).lower(),
        "home_team": fixture["homeTeam"]["name"],  # type: ignore[index]
        "away_team": fixture["awayTeam"]["name"],  # type: ignore[index]
        "kickoff_utc": fixture["kickoffUtc"],
        "league": fixture["league"],
    }

    try:
        resp = await client.post(
            f"{AGENT_URL}/analyze",
            json=payload,
            headers={"X-Service-Token": SERVICE_TOKEN},
            timeout=120.0,
        )
        resp.raise_for_status()
        result = resp.json()

        await client.post(
            f"{API_URL}/api/internal/predictions/{fixture['id']}",
            json=result,
            headers={"X-Service-Token": SERVICE_TOKEN},
            timeout=30.0,
        )
        return True
    except httpx.HTTPError:
        return False


async def main() -> None:
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{API_URL}/api/fixtures/upcoming", timeout=30.0)
        resp.raise_for_status()
        fixtures: list[dict[str, object]] = resp.json()

    started = datetime.now(timezone.utc)
    sem = asyncio.Semaphore(CONCURRENCY)

    async def bounded(f: dict[str, object]) -> bool:
        async with sem:
            return await analyze_one(client, f)

    results = await asyncio.gather(*(bounded(f) for f in fixtures), return_exceptions=False)

    succeeded = sum(1 for r in results if r)
    elapsed = (datetime.now(timezone.utc) - started).total_seconds()
    print(
        f"[analyze-events] total={len(fixtures)} ok={succeeded} "
        f"failed={len(fixtures) - succeeded} elapsed={elapsed:.2f}s"
    )


if __name__ == "__main__":
    asyncio.run(main())
