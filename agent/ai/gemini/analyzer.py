from __future__ import annotations

import asyncio
import json

from agent.ai.base import BaseAnalyzer
from agent.ai.gemini.client import GeminiClient
from agent.ai.schemas import (
    ProviderPrediction,
    ResearchRequest,
    ResearchResult,
)
from agent.core.logging import get_logger

logger = get_logger(__name__)

RESEARCH_SYSTEM = (
    "You are a sports research analyst. Summarise injuries, form, tactics, "
    "and risk factors for the given match. Respond only with the requested JSON."
)

RESEARCH_SCHEMA: dict[str, object] = {
    "type": "object",
    "properties": {
        "injuries": {"type": "array", "items": {"type": "string"}},
        "form_notes": {"type": "array", "items": {"type": "string"}},
        "tactical_observations": {"type": "array", "items": {"type": "string"}},
        "risk_factors": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["injuries", "form_notes", "tactical_observations", "risk_factors"],
}

SYNTH_SCHEMA: dict[str, object] = {
    "type": "object",
    "properties": {
        "home": {"type": "number"},
        "draw": {"type": "number"},
        "away": {"type": "number"},
        "confidence": {"type": "number"},
        "reasoning": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["home", "draw", "away", "confidence", "reasoning"],
}


class GeminiAnalyzer(BaseAnalyzer):
    def __init__(self, api_key: str, model: str = "gemini-2.5-flash") -> None:
        self._client = GeminiClient(api_key=api_key, model=model)

    @property
    def provider_name(self) -> str:
        return "gemini"

    async def research(self, req: ResearchRequest) -> ResearchResult:
        prompt = (
            f"Sport: {req.sport}\nLeague: {req.league}\n"
            f"Match: {req.home_team} vs {req.away_team}\n"
            f"Kickoff (UTC): {req.kickoff_utc}"
        )
        raw = await asyncio.to_thread(
            self._client.generate_json, RESEARCH_SYSTEM, prompt, RESEARCH_SCHEMA
        )
        try:
            data = json.loads(raw)
            return ResearchResult(
                injuries=[str(x) for x in data["injuries"]],
                form_notes=[str(x) for x in data["form_notes"]],
                tactical_observations=[str(x) for x in data["tactical_observations"]],
                risk_factors=[str(x) for x in data["risk_factors"]],
                raw_text=raw,
            )
        except (json.JSONDecodeError, KeyError, TypeError) as exc:
            logger.warning("gemini.research.parse_failed", error=str(exc))
            return ResearchResult(raw_text=raw)

    async def synthesize(
        self,
        req: ResearchRequest,
        research: ResearchResult,
        stat_prediction: dict[str, float],
    ) -> ProviderPrediction:
        prompt = (
            f"Match: {req.home_team} vs {req.away_team}\n"
            f"Stat baseline: {stat_prediction}\n"
            f"Research: {research.model_dump_json()}"
        )
        raw = await asyncio.to_thread(
            self._client.generate_json,
            "Synthesise a final prediction. Respond only with the requested JSON.",
            prompt,
            SYNTH_SCHEMA,
        )
        try:
            data = json.loads(raw)
            return ProviderPrediction(
                home=float(data["home"]),
                draw=float(data["draw"]),
                away=float(data["away"]),
                confidence=float(data["confidence"]),
                reasoning=[str(x) for x in data["reasoning"]],
            )
        except (json.JSONDecodeError, KeyError, TypeError, ValueError) as exc:
            logger.error("gemini.synth.parse_failed", error=str(exc))
            return ProviderPrediction(
                home=stat_prediction["home"],
                draw=stat_prediction["draw"],
                away=stat_prediction["away"],
                confidence=0.3,
                reasoning=["LLM synthesis failed; falling back to statistical baseline."],
    )
