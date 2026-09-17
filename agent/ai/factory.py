import os

from agent.ai.base import AIResearchProvider
from agent.ai.gemini.analyzer import GeminiAnalyzer
from agent.ai.grok.analyzer import GrokAnalyzer


def create_providers() -> list[AIResearchProvider]:
    """Build enabled providers from environment without coupling callers to SDKs."""
    names = [x.strip().lower() for x in os.getenv("AI_PROVIDERS", "gemini,grok").split(",") if x.strip()]
    providers: list[AIResearchProvider] = []
    for name in names:
        if name == "gemini" and os.getenv("GEMINI_API_KEY"):
            providers.append(GeminiAnalyzer())
        elif name == "grok" and os.getenv("XAI_API_KEY"):
            providers.append(GrokAnalyzer())
    if not providers:
        raise RuntimeError("No configured AI providers. Set AI_PROVIDERS and provider API keys.")
    return providers
