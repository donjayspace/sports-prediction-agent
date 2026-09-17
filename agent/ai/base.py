from abc import ABC, abstractmethod

from agent.ai.schemas import AIAnalysis, EventResearchInput


class AIResearchProvider(ABC):
    """Common contract so Gemini, Grok, or future providers are interchangeable."""

    provider_name: str

    @abstractmethod
    def analyze(self, event: EventResearchInput) -> AIAnalysis:
        """Analyze one point-in-time event snapshot."""
        raise NotImplementedError
