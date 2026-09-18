from __future__ import annotations

from abc import ABC, abstractmethod

from agent.ai.schemas import (
    ProviderPrediction,
    ResearchRequest,
    ResearchResult,
)


class BaseAnalyzer(ABC):
    """Abstract interface for LLM-backed research + synthesis providers."""

    @property
    @abstractmethod
    def provider_name(self) -> str: ...

    @abstractmethod
    async def research(self, req: ResearchRequest) -> ResearchResult: ...

    @abstractmethod
    async def synthesize(
        self,
        req: ResearchRequest,
        research: ResearchResult,
        stat_prediction: dict[str, float],
    ) -> ProviderPrediction: ...
