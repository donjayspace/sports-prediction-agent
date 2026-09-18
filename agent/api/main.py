from fastapi import FastAPI
from agent.core.logging import configure_logging

configure_logging()

app = FastAPI(title="Sports Research Agent", version="0.1.0")

@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}

@app.post("/analyze")
async def analyze(payload: dict) -> dict:
    # Keep the first endpoint transport-only; domain analysis remains in agent/analyzer.
    return {"status": "accepted", "event_id": str(payload.get("event_id", ""))}

@app.post("/research")
async def research(payload: dict) -> dict:
    return {"status": "accepted", "event_id": str(payload.get("event_id", ""))}
