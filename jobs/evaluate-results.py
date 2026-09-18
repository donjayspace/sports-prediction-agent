from __future__ import annotations

import asyncio
import os
import sys
from datetime import datetime, timedelta, timezone

import httpx

API_URL = os.environ.get("API_PUBLIC_URL", "http://localhost:3001")
SERVICE_TOKEN = os.environ.get("AGENT_SERVICE_TOKEN", "")


async def evaluate(sport: str, days: int) -> dict[str, object]:
    async with httpx.AsyncClient(timeout=60.0) as client:
        resp = await client.get(
            f"{API_URL}/api/performance/summary",
            params={"sport": sport, "days": days},
            headers={"X-Service-Token": SERVICE_TOKEN},
        )
        resp.raise_for_status()
        return resp.json()


async def main() -> None:
    sport = sys.argv[1] if len(sys.argv) > 1 else "FOOTBALL"
    days = int(sys.argv[2]) if len(sys.argv) > 2 else 30

    summary = await evaluate(sport, days)
    ts = datetime.now(timezone.utc).isoformat()
    print(f"[evaluate-results] {ts} sport={sport} window={days}d summary={summary}")


if __name__ == "__main__":
    asyncio.run(main())
