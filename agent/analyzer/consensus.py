from __future__ import annotations

from agent.ai.base import BaseAnalyzer
from agent.ai.factory import get_analyzer
from agent.ai.schemas import (
    AnalyzeResponse,
    ProbabilityTriple,
    ResearchRequest,
)
from agent.analyzer.evidence_analyzer import EvidenceAnalyzer
from agent.analyzer.feature_analyzer import FeatureAnalyzer
from agent.analyzer.model_analyzer import ModelAnalyzer
from agent.core.config import LLMProvider, settings
from agent.core.logging import get_logger
from agent.ensemble.predictor import EnsembleWeights, blend_probabilities
from agent.validation.data_quality import validate_research_request

logger = get_logger(__name__)


class ConsensusBuilder:
    """Orchestrates statistical + LLM analysis into a single prediction."""

    def __init__(self, provider: LLMProvider | str | None = None) -> None:
        self._model_analyzer = ModelAnalyzer()
        self._evidence_analyzer = EvidenceAnalyzer()
        self._feature_analyzer = FeatureAnalyzer()
        self._llm: BaseAnalyzer = get_analyzer(provider)

    async def run(self, req: ResearchRequest) -> AnalyzeResponse:
        validate_research_request(req)

        stat = await self._model_analyzer.predict(req)
        research = await self._llm.research(req)
        llm_pred = await self._llm.synthesize(req, research, stat)

        evidence_score = self._evidence_analyzer.score(research)

        adjusted_confidence = min(
            max(llm_pred.confidence * (0.5 + 0.5 * evidence_score), 0.0),
            1.0,
        )

        weights = EnsembleWeights.from_llm_confidence(
            adjusted_confidence, max_llm_weight=settings.llm_max_weight
        )

        stat_triple = ProbabilityTriple(
            home=stat["home"], draw=stat["draw"], away=stat["away"]
        ).normalised()
        llm_triple = llm_pred.to_triple()
        final_triple = blend_probabilities(stat_triple, llm_triple, weights)

        logger.info(
            "consensus.computed",
            fixture_id=req.fixture_id,
            provider=self._llm.provider_name,
            llm_weight=weights.llm_weight,
            stat_weight=weights.stat_weight,
        )

        return AnalyzeResponse(
            stat_probs=stat_triple,
            llm_probs=llm_triple,
            llm_confidence=adjusted_confidence,
            llm_provider=self._llm.provider_name,
            llm_research={
                "injuries": research.injuries,
                "form_notes": research.form_notes,
                "tactical_observations": research.tactical_observations,
                "risk_factors": research.risk_factors,
                "raw_text": research.raw_text,
            },
            final_probs=final_triple,
            model_version=self._model_analyzer.version,
            agent_version=settings.agent_version,
        )
