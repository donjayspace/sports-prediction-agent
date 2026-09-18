from __future__ import annotations

from enum import Enum

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class LLMProvider(str, Enum):
    GROK = "grok"
    GEMINI = "gemini"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    agent_service_token: str = Field(min_length=16)
    agent_version: str = Field(default="0.1.0")
    model_version: str = Field(default="dc-1.0.0")
    default_llm_provider: LLMProvider = Field(default=LLMProvider.GEMINI)

    xai_api_key: str = Field(default="")
    gemini_api_key: str = Field(default="")

    grok_model: str = Field(default="grok-4.6")
    gemini_model: str = Field(default="gemini-3.5-flash")

    llm_max_weight: float = Field(default=0.4, ge=0.0, le=0.5)
    llm_timeout_seconds: float = Field(default=60.0, gt=0)

    log_level: str = Field(default="info")

    def validate_provider_keys(self) -> None:
        if self.default_llm_provider == LLMProvider.GROK and not self.xai_api_key:
            raise RuntimeError("XAI_API_KEY is required when DEFAULT_LLM_PROVIDER=grok")
        if self.default_llm_provider == LLMProvider.GEMINI and not self.gemini_api_key:
            raise RuntimeError("GEMINI_API_KEY is required when DEFAULT_LLM_PROVIDER=gemini")


settings = Settings()
