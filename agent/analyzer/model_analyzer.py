from agent.ai.base import AIResearchProvider
from agent.ai.schemas import EventResearchInput
from agent.analyzer.consensus import build_consensus


class ModelAnalyzer:
    """Orchestrates multiple AI research providers and produces an auditable consensus."""

    def __init__(self, providers: list[AIResearchProvider]) -> None:
        if not providers:
            raise ValueError("At least one provider is required")
        self.providers = providers

    def analyze(self, event: EventResearchInput) -> dict:
        analyses = []
        errors = []
        for provider in self.providers:
            try:
                analyses.append(provider.analyze(event))
            except Exception as exc:  # One provider failure must not hide other evidence.
                errors.append({"provider": provider.provider_name, "error": str(exc)})
        if not analyses:
            raise RuntimeError(f"All AI providers failed: {errors}")
        return {
            "event_id": event.event_id,
            "analyses": [analysis.model_dump() for analysis in analyses],
            "consensus": build_consensus(analyses),
            "errors": errors,
        }
