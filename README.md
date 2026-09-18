# Sports Prediction Agent

A full-stack sports prediction system that combines classical statistical models
with LLM-driven research to produce calibrated probabilistic forecasts for
football, basketball, tennis, and table tennis.

## Architecture

- **`apps/dashboard`** — Next.js 15 App Router UI. Server components for
  initial render, client components for live updates.
- **`apps/api`** — Fastify + Prisma. Owns the database schema, exposes the
  public REST API, and calls the agent over HTTP with a service token.
- **`agent`** — Stateless FastAPI service. Runs statistical models, queries
  Grok or Gemini, blends outputs, and returns probabilities. Never touches
  the database.
- **`jobs`** — Python orchestration scripts that drive the pipeline on a
  schedule.

## Prerequisites

- Node.js ≥ 20, pnpm ≥ 9
- Python ≥ 3.11
- Docker + Docker Compose
- An xAI API key (Grok) and/or a Gemini API key

## Quick start

```bash
# 1. Install workspace dependencies
pnpm install

# 2. Create and fill in the env file
cp .env.example .env
$EDITOR .env

# 3. Start infrastructure and services
./scripts/dev.sh

## Then visit:

· Dashboard: http://localhost:3000
· API: http://localhost:3001
· Agent: http://localhost:8000/docs

Full pipeline

```bash
# Collect upcoming fixtures
python jobs/collect-events.py football 7

# Run the agent on all upcoming fixtures
python jobs/analyze-events.py

# Refresh stale fixture statuses
python jobs/refresh-events.py

# Evaluate resolved predictions
python jobs/evaluate-results.py FOOTBALL 30
```

## Testing

```bash
# TypeScript
pnpm typecheck
pnpm --filter api test
pnpm --filter dashboard typecheck

# Python
cd agent
pytest -q
mypy --strict .
ruff check .
```

## Critical rules

1. Prisma owns the schema. Python never touches the database.
2. The agent is stateless. Everything it needs is in the request payload.
3. Calibration beats accuracy. A well-calibrated 60% model beats a
   miscalibrated 70% model for expected value.
4. LLM weight is capped at 0.4. Research shows LLM sports predictions
   are systematically overconfident by ~5.6 percentage points.
5. Feature leakage is the #1 model killer. Every feature must be computed
   strictly before kickoff.

## Deployment

· Dashboard → Vercel (pnpm --filter dashboard build)
· API → Railway / Fly.io (apps/api/Dockerfile)
· Agent → Railway / Fly.io (agent/Dockerfile)
· Postgres → Supabase / Neon
· Redis → Upstash

Set AGENT_URL in the API environment to the deployed agent URL, and set
NEXT_PUBLIC_API_URL in the dashboard to the deployed API URL.

```

## Final Bootstrap Sequence

After dropping every file into place:

```bash
# 1. Create all __init__.py files in the agent
find agent -type d -not -path "*/__pycache__*" -not -path "*/.venv*" \
  -exec touch {}/__init__.py \;

# 2. Make scripts executable
chmod +x scripts/*.sh

# 3. Install JS dependencies
pnpm install

# 4. Create Python virtual environment
cd agent
python3.12 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -e ".[dev]"
deactivate
cd ..

# 5. Copy env files
cp .env.example .env
cp agent/.env.example agent/.env
cp apps/dashboard/.env.example apps/dashboard/.env

# 6. Start infrastructure
docker compose up -d postgres redis

# 7. Run the initial migration
pnpm db:generate
pnpm db:migrate --name init

# 8. Seed fixtures
pnpm db:seed

# 9. Start everything
./scripts/dev.sh
```

---
