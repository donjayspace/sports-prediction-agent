from __future__ import annotations

import asyncio

from xai_sdk import Client
from xai_sdk.chat import Chat, system, user


class GrokClient:
    """Thin async-friendly wrapper around the xAI SDK chat API."""

    def __init__(self, api_key: str, model: str, timeout_seconds: float = 60.0) -> None:
        if not api_key:
            raise ValueError("xAI API key is required")
        self._client = Client(api_key=api_key)
        self._model = model
        self._timeout = timeout_seconds

    def _build_chat(self, system_prompt: str, user_prompt: str) -> Chat:
        chat = self._client.chat.create(model=self._model)
        chat.append(system(system_prompt))
        chat.append(user(user_prompt))
        return chat

    async def complete(self, system_prompt: str, user_prompt: str) -> str:
        def _run() -> str:
            chat = self._build_chat(system_prompt, user_prompt)
            response = chat.sample()
            return response.content

        return await asyncio.wait_for(
            asyncio.to_thread(_run),
            timeout=self._timeout,
        )
