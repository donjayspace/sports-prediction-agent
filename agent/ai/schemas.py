from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator

Outcome = Literal["home", "away", "draw", "player_a", "player_b"]


class ResearchEvidence(BaseModel):
    """A source-backed observation returned by an AI research provider."""

    claim: str
    source: str | None = None
    source_url: str | None = None
    reliability: Literal["high", "medium", "low", "unknown"] = "unknown"


class AIAnalysis(BaseModel):
    """Strict contract between AI providers and the deterministic analyzer."""

    provider: str
    model: str
    summary: str
    evidence: list[ResearchEvidence] = Field(default_factory=list)
    uncertainties: list[str] = Field(default_factory=list)
    probabilities: dict[str, float] = Field(default_factory=dict)
    confidence: float = Field(ge=0, le=1)

    @field_validator("probabilities")
    @classmethod
    def validate_probabilities(cls, value: dict[str, float]) -> dict[str, float]:
        if not value:
            return value
        if any(v < 0 or v > 1 for v in value.values()):
            raise ValueError("probabilities must be between 0 and 1")
        total = sum(value.values())
        if abs(total - 1.0) > 0.02:
            raise ValueError("probabilities must sum to approximately 1")
        return value


class EventResearchInput(BaseModel):
    """Point-in-time event snapshot passed to an AI provider."""

    event_id: str
    sport: str
    competition: str
    start_time: str
    participants: list[str]
    structured_data: dict[str, Any] = Field(default_factory=dict)
    research_context: list[ResearchEvidence] = Field(default_factory=list)
