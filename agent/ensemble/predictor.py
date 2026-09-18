from __future__ import annotations

from dataclasses import dataclass

from agent.ai.schemas import ProbabilityTriple


@dataclass(frozen=True)
class EnsembleWeights:
    stat_weight: float
    llm_weight: float

    @classmethod
    def from_llm_confidence(
        cls, llm_confidence: float, max_llm_weight: float = 0.4
    ) -> "EnsembleWeights":
        llm_w = max(0.0, min(llm_confidence, max_llm_weight))
        return cls(stat_weight=1.0 - llm_w, llm_weight=llm_w)


def blend_probabilities(
    stat: ProbabilityTriple,
    llm: ProbabilityTriple,
    weights: EnsembleWeights,
) -> ProbabilityTriple:
    blended = ProbabilityTriple(
        home=weights.stat_weight * stat.home + weights.llm_weight * llm.home,
        draw=weights.stat_weight * stat.draw + weights.llm_weight * llm.draw,
        away=weights.stat_weight * stat.away + weights.llm_weight * llm.away,
    )
    return blended.normalised()
