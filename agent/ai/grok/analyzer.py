from __future__ import annotations

import json

from agent.ai.base import BaseAnalyzer
from agent.ai.grok.client import GrokClient
from agent.ai.schemas import (
    ProviderPrediction,
    ResearchRequest,
    ResearchResult,
)
from agent.core.logging import get_logger

logger = get_logger(__name__)

RESEARCH_SYSTEM = (
    "You are a sports research analyst. Search recent news for injuries, "
    "suspensions, tactical shifts, and morale. Return STRICT JSON only with keys: "
    "injuries (array of strings), form_notes (array of strings), "
    "tactical_observations (array of strings), risk_factors (array of strings). "
    "Do not include any prose outside the JSON object."
)

SYNTH_SYSTEM = (
    "You synthesise sports predictions. You will be given a statistical baseline "
    "and research findings. Return STRICT JSON only with keys: home (float 0-1), "
    "draw (float 0-1), away (float 0-1), confidence (float 0-1), "
    "reasoning (array of strings). Do not include any prose outside the JSON object."
)


def _strip_json_fence(raw: str) -> str:
    text = raw.strip()
    if text.startswith("```"):
        text = text.split("```", 2)[1] if text.count("```") >= 2 else text.lstrip("`")
        if text.startswith("json"):
            text = text[4:]
    return text.strip("` \n")


class GrokAnalyzer(BaseAnalyzer):
    def __init__(self, api_key: str, model: str = "grok-4.6") -> None:
        self._client = GrokClient(api_key=api_key, model=model)

    @property
    def provider_name(self) -> str:
        return "grok"

    async def research(self, req: ResearchRequest) -> ResearchResult:
        prompt = (
            f"Sport: {req.sport}\n"
            f"League: {req.league}\n"
            f"Match: {req.home_team} vs {req.away_team}\n"
            f"Kickoff (UTC): {req.kickoff_utc}"
        )
        raw = await self._client.complete(RESEARCH_SYSTEM, prompt)
        cleaned = _strip_json_fence(raw)
        try:
            data = json.loads(cleaned)
            return ResearchResult(
                injuries=[str(x) for x in data.get("injuries", [])],
                form_notes=[str(x) for x in data.get("form_notes", [])],
                tactical_observations=[str(x) for x in data.get("tactical_observations", [])],
                risk_factors=[str(x) for x in data.get("risk_factors", [])],
                raw_text=raw,
            )
        except (json.JSONDecodeError, TypeError, AttributeError):
            logger.warning("grok.research.parse_failed", raw_len=len(raw))
            return ResearchResult(raw_text=raw)

    async def synthesize(
        self,
        req: ResearchRequest,
        research: ResearchResult,
        stat_prediction: dict[str, float],
    ) -> ProviderPrediction:
        prompt = (
            f"Match: {req.home_team} vs {req.away_team}\n"
            f"Stat baseline (home/draw/away): "
            f"{stat_prediction['home']:.4f}/{stat_prediction['draw']:.4f}/"
            f"{stat_prediction['away']:.4f}\n"
            f"Research findings JSON:\n{research.model_dump_json()}"
        )
        raw = await self._client.complete(SYNTH_SYSTEM, prompt)
        cleaned = _strip_json_fence(raw)
        try:
            data = json.loads(cleaned)
            return ProviderPrediction(
                home=float(data["home"]),
                draw=float(data["draw"]),
                away=float(data["away"]),
                confidence=float(data.get("confidence", 0.5)),
                reasoning=[str(x) for x in data.get("reasoning", [])],
            )
        except (json.JSONDecodeError, KeyError, TypeError, ValueError) as exc:
            logger.error("grok.synth.parse_failed", error=str(exc), raw_len=len(raw))
            return ProviderPrediction(
                home=stat_prediction["home"],
                draw=stat_prediction["draw"],
                away=stat_prediction["away"],
                confidence=0.3,
                reasoning=["LLM synthesis failed; falling back to statistical baseline."],
                                 )
