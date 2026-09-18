from __future__ import annotations

from agent.ai.schemas import ResearchResult


class EvidenceAnalyzer:
    """Scores the strength of LLM research evidence."""

    POSITIVE_KEYWORDS = ("return", "fit", "recovered", "available", "confident", "strong")
    NEGATIVE_KEYWORDS = ("injury", "suspension", "out", "doubtful", "fatigue", "travel")

    def score(self, research: ResearchResult) -> float:
        text = " ".join(
            research.injuries
            + research.form_notes
            + research.tactical_observations
            + research.risk_factors
        ).lower()

        pos = sum(text.count(k) for k in self.POSITIVE_KEYWORDS)
        neg = sum(text.count(k) for k in self.NEGATIVE_KEYWORDS)

        total = pos + neg
        if total == 0:
            return 0.5
        return pos / total
