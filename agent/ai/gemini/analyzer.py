import json

from pydantic import TypeAdapter

from agent.ai.base import AIResearchProvider
from agent.ai.gemini.client import GeminiClient
from agent.ai.schemas import AIAnalysis, EventResearchInput


class GeminiAnalyzer(AIResearchProvider):
    provider_name = "gemini"

    def __init__(self, client: GeminiClient | None = None) -> None:
        self.client = client or GeminiClient()

    def analyze(self, event: EventResearchInput) -> AIAnalysis:
        """Request structured research output; deterministic validation happens locally."""
        prompt = (
            "Analyze this sports event for research and forecasting. Use only supplied "
            "facts; identify uncertainty and do not invent missing data. Return JSON.\n\n"
            + json.dumps(event.model_dump(), ensure_ascii=False)
        )
        response = self.client.client.models.generate_content(
            model=self.client.model,
            contents=prompt,
            config={
                "response_mime_type": "application/json",
                "response_schema": AIAnalysis.model_json_schema(),
            },
        )
        result = TypeAdapter(AIAnalysis).validate_json(response.text)
        return result.model_copy(update={"provider": self.provider_name, "model": self.client.model})
