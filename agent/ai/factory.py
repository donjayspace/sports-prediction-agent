from __future__ import annotations

from agent.ai.base import BaseAnalyzer
from agent.ai.gemini.analyzer import GeminiAnalyzer
from agent.ai.grok.analyzer import GrokAnalyzer
from agent.core.config import LLMProvider, settings


def get_analyzer(provider: LLMProvider | str | None = None) -> BaseAnalyzer:
    resolved = provider if provider is not None else settings.default_llm_provider
    if isinstance(resolved, str):
        resolved = LLMProvider(resolved.lower())

    if resolved == LLMProvider.GROK:
        return GrokAnalyzer(api_key=settings.xai_api_key, model=settings.grok_model)
    if resolved == LLMProvider.GEMINI:
        return GeminiAnalyzer(api_key=settings.gemini_api_key, model=settings.gemini_model)
    raise ValueError(f"Unsupported provider: {resolved!r}")
