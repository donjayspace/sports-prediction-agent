import os

from google import genai


class GeminiClient:
    """Thin SDK wrapper; domain logic stays in analyzer.py."""

    def __init__(self, model: str | None = None) -> None:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise RuntimeError("GEMINI_API_KEY is required")
        self.model = model or os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
        self.client = genai.Client(api_key=api_key)
