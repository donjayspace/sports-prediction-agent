# Sports Prediction Agent

Stateless FastAPI service that combines statistical models with LLM-driven research
to produce calibrated probabilistic sports predictions.

## Responsibilities

- Run per-sport statistical models (Dixon-Coles for football, feature-driven
  estimators for basketball, tennis, and table tennis).
- Query an LLM provider (Grok or Gemini) for real-time research on injuries,
  form, tactics, and risk factors.
- Blend statistical and LLM predictions using confidence-weighted ensembling
  with a capped LLM weight to prevent overconfidence.
- Return a validated `AnalyzeResponse` payload to `apps/api`.

## What it does NOT do

- It does not connect to PostgreSQL or Prisma.
- It does not persist anything. `apps/api` is the sole writer.

## Endpoints

```text
| Method | Path          | Auth                    | Description                              |
|--------|---------------|-------------------------|------------------------------------------|
| GET    | `/health`     | none                    | Liveness check                           |
| GET    | `/providers`  | none                    | List available LLM providers             |
| POST   | `/analyze`    | `X-Service-Token` header| Run the full analysis pipeline           |
```
## Local development

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
uvicorn api.main:app --reload --port 8000
