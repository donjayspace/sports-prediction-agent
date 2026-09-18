from __future__ import annotations

from pydantic import BaseModel, Field, field_validator


class ResearchRequest(BaseModel):
    fixture_id: str = Field(min_length=1)
    sport: str = Field(min_length=1)
    home_team: str = Field(min_length=1)
    away_team: str = Field(min_length=1)
    kickoff_utc: str = Field(min_length=1)
    league: str = Field(min_length=1)

    @field_validator("sport")
    @classmethod
    def normalise_sport(cls, v: str) -> str:
        return v.strip().lower()


class ResearchResult(BaseModel):
    injuries: list[str] = Field(default_factory=list)
    form_notes: list[str] = Field(default_factory=list)
    tactical_observations: list[str] = Field(default_factory=list)
    risk_factors: list[str] = Field(default_factory=list)
    raw_text: str | None = None


class ProbabilityTriple(BaseModel):
    home: float = Field(ge=0.0, le=1.0)
    draw: float = Field(ge=0.0, le=1.0)
    away: float = Field(ge=0.0, le=1.0)

    @field_validator("away")
    @classmethod
    def _validate_sum(cls, v: float, info: object) -> float:
        return v

    def normalised(self) -> "ProbabilityTriple":
        total = self.home + self.draw + self.away
        if total <= 0:
            raise ValueError("Probabilities sum to zero")
        return ProbabilityTriple(
            home=self.home / total,
            draw=self.draw / total,
            away=self.away / total,
        )


class ProviderPrediction(BaseModel):
    home: float = Field(ge=0.0, le=1.0)
    draw: float = Field(ge=0.0, le=1.0)
    away: float = Field(ge=0.0, le=1.0)
    confidence: float = Field(ge=0.0, le=1.0)
    reasoning: list[str] = Field(default_factory=list)

    def to_triple(self) -> ProbabilityTriple:
        return ProbabilityTriple(home=self.home, draw=self.draw, away=self.away).normalised()


class AnalyzeResponse(BaseModel):
    stat_probs: ProbabilityTriple
    llm_probs: ProbabilityTriple
    llm_confidence: float
    llm_provider: str
    llm_research: dict[str, object]
    final_probs: ProbabilityTriple
    model_version: str
    agent_version: str
