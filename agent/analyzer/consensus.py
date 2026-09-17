from statistics import mean

from agent.ai.schemas import AIAnalysis


def build_consensus(analyses: list[AIAnalysis]) -> dict:
    """Aggregate provider probabilities without treating any single AI as ground truth."""
    if not analyses:
        raise ValueError("At least one AI analysis is required")
    outcomes = sorted({k for analysis in analyses for k in analysis.probabilities})
    probabilities = {
        outcome: mean(analysis.probabilities.get(outcome, 0.0) for analysis in analyses)
        for outcome in outcomes
    }
    total = sum(probabilities.values())
    if total:
        probabilities = {k: v / total for k, v in probabilities.items()}
    return {
        "probabilities": probabilities,
        "provider_count": len(analyses),
        "provider_agreement": {
            outcome: max(a.probabilities.get(outcome, 0.0) for a in analyses)
            - min(a.probabilities.get(outcome, 0.0) for a in analyses)
            for outcome in outcomes
        },
        "uncertainties": sorted({u for a in analyses for u in a.uncertainties}),
    }
