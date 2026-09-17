import json

from agent.ai.base import AIResearchProvider
from agent.ai.grok.client import GrokClient
from agent.ai.schemas import AIAnalysis, EventResearchInput


class GrokAnalyzer(AIResearchProvider):
    provider_name = "grok"

    def __init__(self, client: GrokClient | None = None) -> None:
        self.client = client or GrokClient()

    def analyze(self, event: EventResearchInput) -> AIAnalysis:
        """Use Grok web search for current evidence, then validate its JSON locally."""
        prompt = (
            "Analyze this sports event for research and forecasting. Verify current facts "
            "with web sources when available. Never invent facts or citations. Return only "
            "JSON matching the requested schema.\n\n"
            + json.dumps(event.model_dump(), ensure_ascii=False)
        )
        response = self.client.client.responses.create(
            model=self.client.model,
            input=prompt,
            tools=[{"type": "web_search"}],
            store=False,
        )
        text = getattr(response, "output_text", None)
        if not text:
            raise RuntimeError("Grok returned no structured text output")
        return AIAnalysis.model_validate_json(text).model_copy(
            update={"provider": self.provider_name, "model": self.client.model}
        )
