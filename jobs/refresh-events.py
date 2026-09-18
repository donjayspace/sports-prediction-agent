from __future__ import annotations

import asyncio
import os

import httpx

API_URL = os.environ.get("API_PUBLIC_URL", "http://localhost:3001")
SERVICE_TOKEN = os.environ.get("AGENT_SERVICE_TOKEN", "")


async def refresh() -> int:
    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.post(
            f"{API_URL}/api/fixtures/refresh",
            headers={"X-Service-Token": SERVICE_TOKEN},
        )
        resp.raise_for_status()
        data = resp.json()
        return int(data.get("updated", 0))


async def main() -> None:
    updated = await refresh()
    print(f"[refresh-events] updated={updated}")


if __name__ == "__main__":
    asyncio.run(main())
