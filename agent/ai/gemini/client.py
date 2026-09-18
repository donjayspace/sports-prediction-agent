from __future__ import annotations

from google import genai
from google.genai import types


class GeminiClient:
    """Wrapper around google-genai with structured JSON output."""

    def __init__(self, api_key: str, model: str = "gemini-2.5-flash") -> None:
        if not api_key:
            raise ValueError("Gemini API key is required")
        self._client = genai.Client(api_key=api_key)
        self._model = model

    def generate_json(
        self,
        system_prompt: str,
        user_prompt: str,
        schema: dict[str, object],
    ) -> str:
        response = self._client.models.generate_content(
            model=self._model,
            contents=types.Part.from_text(text=user_prompt),
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                response_mime_type="application/json",
                response_json_schema=schema,
                temperature=0.2,
            ),
        )
        if response.text is None:
            raise RuntimeError("Gemini returned empty response")
        return response.text
