from __future__ import annotations

from typing import Any

import httpx


class BackendClient:
    """Async HTTP client for the internal apps/api endpoints."""

    def __init__(
        self,
        base_url: str,
        service_token: str,
        timeout: float = 30.0,
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._service_token = service_token
        self._timeout = timeout

    def _headers(self) -> dict[str, str]:
        return {
            "Content-Type": "application/json",
            "X-Service-Token": self._service_token,
        }

    async def persist_prediction(
        self, fixture_id: str, payload: dict[str, Any]
    ) -> dict[str, Any]:
        async with httpx.AsyncClient(timeout=self._timeout) as client:
            resp = await client.post(
                f"{self._base_url}/api/internal/predictions/{fixture_id}",
                json=payload,
                headers=self._headers(),
            )
            resp.raise_for_status()
            return resp.json()

    async def upcoming_fixtures(self) -> list[dict[str, Any]]:
        async with httpx.AsyncClient(timeout=self._timeout) as client:
            resp = await client.get(f"{self._base_url}/api/fixtures/upcoming")
            resp.raise_for_status()
            data = resp.json()
            return data if isinstance(data, list) else []
