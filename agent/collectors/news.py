from __future__ import annotations

import httpx
from pydantic import BaseModel


class NewsItem(BaseModel):
    title: str
    url: str
    published_at: str
    summary: str | None = None


class NewsCollector:
    def __init__(self, base_url: str, timeout: float = 15.0) -> None:
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout

    async def fetch(self, query: str, limit: int = 20) -> list[NewsItem]:
        async with httpx.AsyncClient(timeout=self._timeout) as client:
            resp = await client.get(
                f"{self._base_url}/news",
                params={"q": query, "limit": limit},
                headers={"User-Agent": "sports-prediction-agent/0.1"},
            )
            resp.raise_for_status()
            data = resp.json()

        items: list[NewsItem] = []
        for entry in data.get("articles", []):
            try:
                items.append(
                    NewsItem(
                        title=str(entry["title"]),
                        url=str(entry["url"]),
                        published_at=str(entry["publishedAt"]),
                        summary=str(entry["description"]) if entry.get("description") else None,
                    )
                )
            except (KeyError, ValueError, TypeError):
                continue
        return items
