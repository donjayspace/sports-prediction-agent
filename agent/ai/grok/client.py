import os

from openai import OpenAI


class GrokClient:
    """OpenAI-compatible xAI client kept isolated from domain logic."""

    def __init__(self, model: str | None = None) -> None:
        api_key = os.getenv("XAI_API_KEY")
        if not api_key:
            raise RuntimeError("XAI_API_KEY is required")
        self.model = model or os.getenv("XAI_MODEL", "grok-4.6")
        self.client = OpenAI(
            api_key=api_key,
            base_url="https://api.x.ai/v1",
            timeout=120,
            max_retries=2,
        )
