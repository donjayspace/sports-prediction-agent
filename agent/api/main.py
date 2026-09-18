from __future__ import annotations

from fastapi import FastAPI

from agent.api.routes import analyze, health
from agent.core.config import settings
from agent.core.logging import configure_logging

configure_logging(settings.log_level)

app = FastAPI(
    title="Sports Prediction Agent",
    version=settings.agent_version,
    docs_url="/docs",
    redoc_url=None,
)

app.include_router(health.router)
app.include_router(analyze.router)
