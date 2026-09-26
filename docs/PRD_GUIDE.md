
# Product Requirements & Development Guide
## Sports Prediction Agent

**Document status:** Living specification
**Version:** 1.0.0
**Last updated:** 2026-09-26
**Owner:** Engineering Lead
**Audience:** Engineers, data scientists, DevOps, product managers

---

## Table of Contents

1. [Product Overview](#1-product-overview)
2. [Goals and Non-Goals](#2-goals-and-non-goals)
3. [Target Users](#3-target-users)
4. [Success Metrics](#4-success-metrics)
5. [System Architecture](#5-system-architecture)
6. [Tech Stack Decisions](#6-tech-stack-decisions)
7. [Domain Model](#7-domain-model)
8. [Functional Requirements](#8-functional-requirements)
9. [Non-Functional Requirements](#9-non-functional-requirements)
10. [Development Phases](#10-development-phases)
11. [Testing Strategy](#11-testing-strategy)
12. [Deployment Strategy](#12-deployment-strategy)
13. [Operational Runbook](#13-operational-runbook)
14. [Risk Register](#14-risk-register)
15. [Appendix](#15-appendix)

---

## 1. Product Overview

### 1.1 Elevator Pitch

**Sports Prediction Agent** is a full-stack platform that produces calibrated
probabilistic forecasts for football, basketball, tennis, and table tennis.
It combines classical statistical models (Dixon-Coles for football, feature-
driven estimators for other sports) with real-time LLM research (Grok and
Gemini) to surface context that static sports APIs miss — injury news, tactical
shifts, morale signals — and blends the two sources into a single, honest
probability triple.

### 1.2 Problem Statement

Retail sports analysts have three poor options:

1. **Pure statistical models** — accurate in aggregate, blind to breaking news.
2. **Pure LLM predictions** — aware of context, systematically overconfident by
   roughly 5.6 percentage points, and uncalibrated.
3. **Manual research** — slow, inconsistent, impossible to scale.

There is no product that quantifies the value of real-time research *and*
produces calibrated probabilities that survive a Brier-score audit.

### 1.3 Solution

A three-tier system:

- **Statistical layer** — mathematically grounded, reproducible, validated.
- **Research layer** — LLM-driven with strict JSON schema output, capped
  influence weight.
- **Calibration layer** — isotonic regression per outcome class, continuously
  re-fitted as results resolve.

Every prediction is stored with full provenance: which model version, which LLM
provider, what the raw research said, what the final blended probability was,
and what the actual outcome turned out to be. Nothing is hidden.

### 1.4 Product Principles

| Principle | Consequence |
|---|---|
| **Calibration beats accuracy** | Ship a well-calibrated 60% model before a miscalibrated 70% model. Brier score is the primary KPI. |
| **LLMs are a signal, not the driver** | LLM weight capped at 0.4 in the ensemble. Never raise above 0.5. |
| **Every prediction is auditable** | Full provenance in Postgres. No black boxes. |
| **Leakage is the #1 enemy** | Every feature timestamp must precede kickoff. Enforced in code, not convention. |
| **Stateless compute** | The agent holds no database connection. Testability and horizontal scalability follow. |

---

## 2. Goals and Non-Goals

### 2.1 Goals (v1.0)

- Produce calibrated 1X2 probability triples for football with Brier score
  below 0.22 on a holdout set of at least 500 resolved fixtures.
- Support four sports: football, basketball, tennis, table tennis.
- Integrate two LLM providers (Grok, Gemini) with a pluggable interface.
- Expose a public REST API and a Next.js dashboard with live updates.
- Store 100% of predictions with full provenance and outcome linkage.
- Run the full pipeline (collect → analyze → predict → resolve → evaluate)
  unattended on a schedule.

### 2.2 Non-Goals (v1.0)

- **Not a betting platform.** No odds integration, no bankroll management, no
  bet placement. The system produces probabilities; users decide what to do.
- **Not a live in-play predictor.** Predictions are pre-match only.
- **Not a public multi-tenant SaaS.** Single-operator deployment. Authentication
  exists but multi-tenancy does not.
- **Not a player-level model.** Predictions are team-level (football, basketball)
  or player-level for individual sports (tennis, table tennis).
- **Not a general-purpose LLM agent.** The LLM has exactly two jobs: research
  and synthesis. No open-ended conversation.

---

## 3. Target Users

### 3.1 Primary Persona — The Quantitative Analyst

**Name:** Amara
**Role:** Independent sports analyst, comfortable with Python and SQL
**Pain:** Spends 4 hours per matchday cross-referencing injury reports, form
data, and historical results in spreadsheets.
**Goal:** A system that surfaces the same signal she would find manually, in
under 60 seconds, with a probability she can audit.
**Success looks like:** She opens the dashboard, sees predictions for the
weekend fixtures, drills into one, reads the research panel, verifies the
statistical baseline, and exports the probability triple.

### 3.2 Secondary Persona — The Hobbyist Modeler

**Name:** Diego
**Role:** Software engineer, sports fan, weekend ML tinkerer
**Pain:** Can build a Dixon-Coles model in an afternoon but has no idea if his
probabilities are calibrated.
**Goal:** A working reference implementation he can fork and extend.
**Success looks like:** He clones the repo, runs `./scripts/dev.sh`, and has a
working dashboard with a real prediction in under 10 minutes.

### 3.3 Tertiary Persona — The Product Owner

**Name:** Priya
**Role:** Runs a small sports content publication
**Pain:** Needs daily probability estimates for editorial coverage but cannot
afford a data science team.
**Goal:** Reliable numbers with visible confidence and methodology.
**Success looks like:** She embeds the API into her CMS and cites the Brier
score in her articles.

---

## 4. Success Metrics

### 4.1 Leading Indicators (measure weekly)

| Metric | Target | Measurement |
|---|---|---|
| Pipeline success rate | ≥ 95% | `AgentRun` rows with `status=SUCCESS` / total |
| Median analyze latency | < 8s p50, < 20s p95 | API logs |
| Dashboard TTI | < 1.5s on 4G | Lighthouse |
| Predicted fixtures covered | ≥ 90% of scheduled | Fixtures with prediction / total scheduled |
| Resolved prediction coverage | ≥ 85% within 48h of kickoff | Results ingested / fixtures completed |

### 4.2 Lagging Indicators (measure monthly)

| Metric | Target | Measurement |
|---|---|---|
| **Brier score (football)** | ≤ 0.22 | Rolling 30-day window |
| **Brier score (all sports)** | ≤ 0.25 | Rolling 30-day window |
| **Log loss** | ≤ 1.02 | Rolling 30-day window |
| **Accuracy (argmax)** | ≥ 52% football, ≥ 60% tennis | Rolling 30-day window |
| **Expected calibration error** | ≤ 0.03 | 10-bin reliability diagram |
| **Directional ROI vs market** | ≥ 0% | Closing-line comparison, if odds available |

### 4.3 Anti-Metrics (things that must NOT happen)

| Anti-metric | Threshold | Why |
|---|---|---|
| LLM weight exceeding cap | 0 events | Overconfidence is the primary failure mode |
| Feature leakage incidents | 0 events | Invalidates every downstream metric |
| Uncalibrated model shipped to prod | 0 events | Accuracy without calibration is a trap |
| Prediction without provenance | 0 events | Audit trail is non-negotiable |

---

## 5. System Architecture

### 5.1 High-Level Topology

```

┌───────────────────────────────────────────────────────────────────┐
│                      NEXT.JS DASHBOARD (Vercel)                    │
│  Overview · Fixtures · Match Detail · History · Performance        │
└───────────────────────────┬───────────────────────────────────────┘
│  REST + WebSocket
▼
┌───────────────────────────────────────────────────────────────────┐
│                    FASTIFY API (Railway / Fly)                     │
│  Public routes · Auth · Rate limit · Prisma · BullMQ              │
│  ▸ Sole owner of PostgreSQL schema                                 │
│  ▸ Sole writer to every table                                      │
└───────────────────────────┬───────────────────────────────────────┘
│  Internal REST (X-Service-Token)
▼
┌───────────────────────────────────────────────────────────────────┐
│                    FASTAPI AGENT (Railway / Fly)                   │
│  Statistical models · LLM providers · Ensemble · Calibration       │
│  ▸ Stateless. No DB. JSON in, JSON out.                            │
└───────────────────────────┬───────────────────────────────────────┘
│
┌─────────────┴─────────────┐
▼                           ▼
┌────────────────┐          ┌────────────────┐
│  Grok (xAI)    │          │  Gemini (Google)│
└────────────────┘          └────────────────┘
│
▼
┌───────────────────────────────────────────────────────────────────┐
│                  POSTGRESQL + REDIS (Supabase / Neon)              │
└───────────────────────────────────────────────────────────────────┘

```

### 5.2 Data Flow

```

Upcoming Events
↓
Data Collection (jobs/collect-events.py)
↓
Data Validation (agent/validation/data_quality.py)
↓
Feature Engineering (agent/features/.py)
↓
Statistical Models (agent/models//.py)
↓
Grok / Gemini Research (agent/ai//analyzer.py)
↓
Prediction Ensemble (agent/ensemble/predictor.py)
↓
Calibration / Validation (agent/validation/calibration.py)
↓
Prediction Record (apps/api → Prisma → PostgreSQL)
↓
Performance Evaluation (agent/evaluation/*.py)

```

### 5.3 Service Boundaries

| Boundary | Contract | Enforced by |
|---|---|---|
| Dashboard ↔ API | REST + JSON over HTTPS, JWT for user routes | CORS + JWT plugin |
| API ↔ Agent | REST + JSON over HTTP, `X-Service-Token` header | `requireServiceToken` preHandler |
| API ↔ Database | Prisma Client (TypeScript only) | Schema in `apps/api/prisma/` |
| Jobs ↔ API/Agent | REST + JSON, service token | Same token |
| Agent ↔ LLM | Provider SDKs | `BaseAnalyzer` interface |

**The agent never imports a database driver.** This is the single most
important architectural invariant.

---

## 6. Tech Stack Decisions

| Layer | Choice | Alternatives Considered | Reason |
|---|---|---|---|
| Frontend | Next.js 15 App Router | Remix, SvelteKit | Server components for initial render, mature ecosystem, Vercel deploys |
| Frontend data | TanStack Query + native fetch | SWR, Apollo | Minimal, works with server components |
| Charts | Recharts | Chart.js, D3 | React-native, declarative, good defaults |
| API | Fastify 5 | Express, Hono, NestJS | Fast, plugin ecosystem, first-class TS |
| API validation | Zod | Joi, Yup, Valibot | Type inference from schema, matches agent's Pydantic |
| ORM | Prisma 6 | Drizzle, TypeORM, Kysely | Best migration story, typed client, single source of truth |
| Database | PostgreSQL 16 | MySQL, SQLite | JSONB, native arrays, window functions for evaluation |
| Cache / Queue | Redis 7 + BullMQ | RabbitMQ, SQS | Same connection for cache and queue, TypeScript-first |
| Agent framework | FastAPI + Pydantic v2 | Flask, Litestar | Async-native, structured validation, auto-docs |
| Numerical | NumPy + SciPy | pandas, Polars | Direct access to `poisson.pmf`, minimal overhead |
| ML | scikit-learn | PyTorch, XGBoost | Isotonic regression is the only heavy dependency needed |
| Statistical model | Dixon-Coles | Pure Poisson, ELO | Industry standard, handles low-scoring bias |
| LLM providers | Grok + Gemini | OpenAI, Claude, Llama | Grok for real-time web search, Gemini for structured synthesis |
| LLM abstraction | `BaseAnalyzer` ABC | LangChain, LiteLLM | ~40 lines of code, no framework lock-in |
| Testing (TS) | Vitest | Jest | Faster, native ESM, same config style as Vite |
| Testing (Py) | pytest + mypy --strict | unittest, pyright | De facto standard, strict mode catches real bugs |
| Deployment | Vercel + Railway | Render, Fly, AWS | Zero-config Next.js, cheap containers, Postgres-friendly |
| Observability | structlog + Sentry | Datadog, New Relic | Structured logs, free tier sufficient for v1 |

---

## 7. Domain Model

### 7.1 Entities

```

Team          ─── Fixture (home) ─── Prediction ─── Result ─── Evaluation
Fixture (away)
│
├── Feature (many)
└── AgentRun (many)

```

### 7.2 Core Tables

**Team**
- `id` (cuid), `externalId` (unique, nullable), `name`, `sport`, `country`
- Unique on `(sport, name)`

**Fixture**
- `id`, `externalId`, `sport`, `league`, `status`, `kickoffUtc`
- `homeTeamId`, `awayTeamId`, `homeScore`, `awayScore`
- Indexed on `(sport, kickoffUtc)` and `(status, kickoffUtc)`

**Prediction**
- `id`, `fixtureId` (unique)
- `statHome/Draw/Away` — statistical model output
- `llmHome/Draw/Away`, `llmConfidence`, `llmProvider`, `llmResearch` (JSONB)
- `finalHome/Draw/Away` — blended + calibrated
- `modelVersion`, `agentVersion`, `pipelineRunId`

**Feature**
- `id`, `fixtureId`, `sport`, `name`, `value`, `version`, `computedAt`
- Unique on `(fixtureId, name, version)` — enables feature versioning without
  destroying history

**Result**
- `id`, `fixtureId` (unique), `outcome` (enum), `homeScore`, `awayScore`

**Evaluation**
- `id`, `sport`, `windowStart`, `windowEnd`, `nPredictions`
- `brierScore`, `logLoss`, `accuracy`, `calibrationJson` (JSONB)

**AgentRun**
- `id`, `fixtureId` (nullable), `kind` (enum), `status` (enum)
- `startedAt`, `finishedAt`, `error`, `metadata` (JSONB)
- Every agent invocation gets a row — this is the pipeline observability spine

### 7.3 Enumerations

```

Sport:          FOOTBALL | BASKETBALL | TENNIS | TABLE_TENNIS
MatchStatus:    SCHEDULED | LIVE | COMPLETED | POSTPONED | CANCELLED
Outcome:        HOME | DRAW | AWAY
AgentRunKind:   COLLECT | ANALYZE | RESEARCH | EVALUATE
AgentRunStatus: PENDING | RUNNING | SUCCESS | FAILED

```

---

## 8. Functional Requirements

### 8.1 Ingestion (FR-I)

| ID | Requirement | Priority |
|---|---|---|
| FR-I-01 | System ingests upcoming fixtures from an external sports API daily | P0 |
| FR-I-02 | Ingest is idempotent — repeated calls do not create duplicates | P0 |
| FR-I-03 | Fixtures with kickoff in the past are rejected at validation | P0 |
| FR-I-04 | Team names are normalised (trimmed, deduplicated on `(sport, name)`) | P0 |
| FR-I-05 | Completed match results are ingested within 48h of final whistle | P0 |
| FR-I-06 | Stale `SCHEDULED` fixtures are flipped to `LIVE` after kickoff passes | P1 |
| FR-I-07 | Failed ingestions are logged with the raw payload for replay | P1 |

### 8.2 Analysis (FR-A)

| ID | Requirement | Priority |
|---|---|---|
| FR-A-01 | Each upcoming fixture is analyzed by the agent before kickoff | P0 |
| FR-A-02 | Statistical model produces a 1X2 probability triple | P0 |
| FR-A-03 | LLM research produces structured JSON with 4 fixed keys | P0 |
| FR-A-04 | LLM synthesis produces a 1X2 triple + confidence + reasoning | P0 |
| FR-A-05 | Ensemble blends with LLM weight capped at 0.4 | P0 |
| FR-A-06 | Final triple is calibrated using isotonic regression | P0 |
| FR-A-07 | Every prediction has a `modelVersion` and `agentVersion` | P0 |
| FR-A-08 | LLM failures fall back to the statistical baseline | P0 |
| FR-A-09 | Analysis latency p95 is under 20 seconds | P1 |
| FR-A-10 | Concurrent analysis supports at least 4 fixtures in parallel | P1 |

### 8.3 Presentation (FR-P)

| ID | Requirement | Priority |
|---|---|---|
| FR-P-01 | Dashboard shows upcoming fixtures with kickoff countdown | P0 |
| FR-P-02 | Match detail shows statistical, LLM, and final probabilities side-by-side | P0 |
| FR-P-03 | Research panel displays injuries, form, tactics, risk factors | P0 |
| FR-P-04 | Prediction history is filterable and paginated | P0 |
| FR-P-05 | Performance page shows Brier, log loss, accuracy, reliability diagram | P0 |
| FR-P-06 | Live ticker updates on WebSocket without page reload | P1 |
| FR-P-07 | All charts render on mobile at ≥ 360px width | P1 |

### 8.4 Evaluation (FR-E)

| ID | Requirement | Priority |
|---|---|---|
| FR-E-01 | Brier score computed per sport per rolling window | P0 |
| FR-E-02 | Reliability diagram computed over 10 bins | P0 |
| FR-E-03 | Accuracy computed as argmax match rate | P0 |
| FR-E-04 | Evaluations persisted with window bounds and model version | P0 |
| FR-E-05 | Historical evaluations retrievable for trend analysis | P1 |

---

## 9. Non-Functional Requirements

### 9.1 Performance

| Layer | Requirement |
|---|---|
| Dashboard TTI | < 1.5s on simulated 4G |
| API p50 latency | < 50ms for read routes |
| API p95 latency | < 300ms for read routes |
| Agent p50 latency | < 8s (dominated by LLM round-trip) |
| Agent p95 latency | < 20s |
| Concurrent analyses | ≥ 4 in parallel without degradation |
| Database queries | All indexed access paths verified with `EXPLAIN ANALYZE` |

### 9.2 Reliability

| Requirement | Target |
|---|---|
| API uptime | 99.5% monthly |
| Agent uptime | 99% monthly (best-effort, LLM providers may flap) |
| Pipeline success rate | ≥ 95% of scheduled runs |
| Data loss on crash | 0 — predictions persist before response is returned |
| Recovery time objective | < 15 minutes |
| Recovery point objective | < 5 minutes |

### 9.3 Security

| Requirement | Implementation |
|---|---|
| Secrets in env only | `.env` files, never committed |
| Service-to-service auth | `X-Service-Token` header, constant-time comparison |
| User auth | JWT with 15-minute access tokens (v1.1) |
| Rate limiting | 300 req/min per IP on public routes |
| SQL injection | Impossible — Prisma parameterises every query |
| Input validation | Zod on API, Pydantic on agent, at every boundary |
| CORS | Locked to `API_PUBLIC_URL` in production |

### 9.4 Observability

| Signal | Destination |
|---|---|
| Structured JSON logs | stdout (collected by platform) |
| Request IDs | Propagated from API to agent via header |
| Agent run audit trail | `AgentRun` table |
| Errors | Sentry (production only) |
| Metrics | Prometheus endpoint (optional) |

### 9.5 Maintainability

- **TypeScript:** `strict: true`, `noUncheckedIndexedAccess: true`
- **Python:** `mypy --strict` clean, `ruff` clean
- **Test coverage:** ≥ 70% on critical paths (ensemble, calibration, validation)
- **No file exceeds 400 lines** without a documented reason
- **Every cross-language boundary** has validators on both sides

---

## 10. Development Phases

Each phase has explicit deliverables and acceptance criteria. Phases are
sequential — do not begin a phase until the previous phase's acceptance
criteria are met.

---

### Phase 0 — Foundation (Day 1)

**Goal:** Working skeleton with infrastructure, tooling, and empty services.

#### Tasks

- [ ] **0.1** Create the monorepo directory structure exactly as specified
      in the README.
- [ ] **0.2** Initialise `pnpm-workspace.yaml` and root `package.json` with
      the `dev`, `build`, `typecheck`, `db:*` scripts.
- [ ] **0.3** Initialise `apps/api` with `package.json`, `tsconfig.json`,
      `eslint.config.js`.
- [ ] **0.4** Initialise `apps/dashboard` with Next.js 15, TypeScript strict,
      Tailwind, ESLint.
- [ ] **0.5** Initialise `agent` with `pyproject.toml`, `requirements.txt`,
      `requirements-dev.txt`, `pytest.ini`.
- [ ] **0.6** Write `docker-compose.yml` with Postgres 16 and Redis 7.
- [ ] **0.7** Write `.env.example` at root, in `agent/`, in `apps/dashboard/`.
- [ ] **0.8** Write `.gitignore` and `.dockerignore` at every level.
- [ ] **0.9** Write `scripts/dev.sh` and `scripts/migrate.sh`.
- [ ] **0.10** Create all `__init__.py` files in the agent tree.

#### Deliverables

- `pnpm install` completes without errors.
- `docker compose up -d postgres redis` starts both services healthy.
- `pnpm typecheck` passes on empty projects.
- `cd agent && mypy --strict .` passes on empty package.

#### Acceptance Criteria

```bash
pnpm install                          # exits 0
docker compose up -d postgres redis   # both healthy
pnpm typecheck                        # exits 0
cd agent && mypy --strict . && cd ..  # exits 0
```

Estimated effort

4–6 hours.

---

Phase 1 — Data Layer (Day 2)

Goal: Prisma schema deployed, seed data present, migrations reproducible.

Tasks

☐ 1.1 Write apps/api/prisma/schema.prisma with all models:
  Team, Fixture, Prediction, Feature, Result, Evaluation,
  AgentRun.
☐ 1.2 Define all enums: Sport, MatchStatus, Outcome,
  AgentRunKind, AgentRunStatus.
☐ 1.3 Add all @@index and @@unique constraints exactly as
  specified in §7.
☐ 1.4 Run pnpm db:migrate --name init and commit the migration.
☐ 1.5 Write apps/api/prisma/seed.ts that creates two football teams
  and one fixture.
☐ 1.6 Run pnpm db:seed and verify with pnpm db:studio.
☐ 1.7 Write apps/api/src/plugins/prisma.ts and wire it into a
  minimal Fastify server with a /health route.

Deliverables

· Migration file committed under apps/api/prisma/migrations/.
· Seed script produces identical data on every run (idempotent).
· GET /health returns { status: "ok", uptime, timestamp }.

Acceptance Criteria

```bash
pnpm db:migrate --name init     # creates migration
pnpm db:seed                    # no error on repeat
pnpm db:studio                  # shows seeded fixture
curl localhost:3001/health      # {"status":"ok",...}
```

Estimated effort

6–8 hours.

---

Phase 2 — API Skeleton (Day 3)

Goal: All Fastify routes registered, typed, validated, with no business
logic yet.

Tasks

☐ 2.1 Write apps/api/src/config/env.ts with Zod schema and startup
  validation.
☐ 2.2 Write apps/api/src/plugins/redis.ts.
☐ 2.3 Write apps/api/src/plugins/auth.ts with authenticate and
  requireServiceToken decorators.
☐ 2.4 Write apps/api/src/routes/health.ts with /health and
  /health/deep.
☐ 2.5 Write apps/api/src/routes/fixtures.ts with all read routes
  (GET /fixtures, GET /fixtures/upcoming, GET /fixtures/:id) and
  write routes (POST /fixtures/ingest, POST /fixtures/refresh,
  POST /fixtures/:id/result).
☐ 2.6 Write apps/api/src/routes/predictions.ts with read routes and
  the internal POST /internal/predictions/:fixtureId route.
☐ 2.7 Write apps/api/src/routes/performance.ts with
  /performance/summary and /performance/history.
☐ 2.8 Write apps/api/src/routes/agent.ts with
  POST /agent/analyze/:fixtureId.
☐ 2.9 Write apps/api/src/server.ts that registers everything with
  correct CORS, rate limit, and graceful shutdown.
☐ 2.10 Write apps/api/tests/health.test.ts and
  apps/api/tests/agent-payload.test.ts.

Deliverables

· Every route from §8.3 and §8.4 responds with correct status codes.
· Invalid payloads return 400 with Zod issues.
· Missing service token on internal routes returns 401.

Acceptance Criteria

```bash
curl localhost:3001/health/deep          # {"status":"ok","checks":{...}}
curl localhost:3001/api/fixtures/upcoming # [] or seeded fixture
curl -X POST localhost:3001/api/internal/predictions/x \
  -H "X-Service-Token: wrong"             # 401
pnpm --filter api test                    # passes
```

Estimated effort

10–12 hours.

---

Phase 3 — Agent Core (Day 4)

Goal: FastAPI service running, /analyze route reachable, providers wired.

Tasks

☐ 3.1 Write agent/core/config.py with Pydantic Settings and
  validate_provider_keys.
☐ 3.2 Write agent/core/logging.py with structlog configuration.
☐ 3.3 Write agent/ai/schemas.py with all Pydantic models:
  ResearchRequest, ResearchResult, ProbabilityTriple,
  ProviderPrediction, AnalyzeResponse.
☐ 3.4 Write agent/ai/base.py with the BaseAnalyzer ABC.
☐ 3.5 Write agent/ai/grok/client.py wrapping xai-sdk.
☐ 3.6 Write agent/ai/grok/analyzer.py with research() and
  synthesize().
☐ 3.7 Write agent/ai/gemini/client.py wrapping google-genai.
☐ 3.8 Write agent/ai/gemini/analyzer.py.
☐ 3.9 Write agent/ai/factory.py with provider selection.
☐ 3.10 Write agent/api/routes/health.py and
  agent/api/routes/analyze.py.
☐ 3.11 Write agent/api/main.py wiring routes together.
☐ 3.12 Write agent/tests/test_api.py and
  agent/tests/test_ai_factory.py.

Deliverables

· /health returns { status: "ok", version, model_version }.
· /providers returns { available: ["grok", "gemini"] }.
· /analyze validates the service token and calls the provider.
· Both Grok and Gemini produce parsable JSON on a real match.

Acceptance Criteria

```bash
uvicorn api.main:app --reload &          # starts on :8000
curl localhost:8000/health               # {"status":"ok",...}
curl localhost:8000/providers            # {"available":["grok","gemini"]}
curl -X POST localhost:8000/analyze \
  -H "X-Service-Token: $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"fixture_id":"x","sport":"football",...}'  # 200 with valid JSON
pytest agent/tests/test_api.py            # passes
```

Estimated effort

12–16 hours (higher if you debug LLM JSON parsing live).

---

Phase 4 — Feature Engineering (Day 5)

Goal: Feature builders for all four sports, with leakage guards enforced.

Tasks

☐ 4.1 Write agent/features/football.py with rolling_form(),
  head_to_head_rate(), build_football_features().
☐ 4.2 Write agent/features/basketball.py with pace-adjusted ratings.
☐ 4.3 Write agent/features/tennis.py with Elo and surface-specific
  serve/return stats.
☐ 4.4 Write agent/features/table_tennis.py with win rate and game
  margin features.
☐ 4.5 Write agent/validation/leakage.py with assert_no_leak().
☐ 4.6 Write agent/validation/data_quality.py with
  validate_research_request() and validate_feature_vector().
☐ 4.7 Write agent/tests/test_leakage.py covering past, at-kickoff,
  and future timestamps.

Deliverables

· Every feature function is pure (no side effects).
· Every feature function has at least one unit test.
· Leakage guard is called at the boundary where features are handed to the
  model.

Acceptance Criteria

```bash
pytest agent/tests/test_leakage.py     # all pass
mypy --strict agent/features agent/validation  # clean
```

Estimated effort

8–10 hours.

---

Phase 5 — Statistical Models (Day 6)

Goal: Dixon-Coles for football; documented fallback for other sports.

Tasks

☐ 5.1 Write agent/models/football/dixon_coles.py with:
  - DixonColesModel.predict() returning a normalised triple
  - fit_attack_defence_from_matches() for offline training
  - model_quality() returning log-likelihood
☐ 5.2 Write agent/models/football/xgboost_model.py with a
  Protocol-based estimator interface and FEATURE_ORDER contract.
☐ 5.3 Write agent/models/basketball/baseline.py with a pace-adjusted
  rating model.
☐ 5.4 Write agent/models/tennis/elo.py with surface-specific Elo.
☐ 5.5 Write agent/models/table_tennis/elo.py.
☐ 5.6 Write agent/tests/test_dixon_coles.py covering:
  - probabilities sum to 1
  - stronger team wins more often
  - home advantage shifts probabilities correctly

Deliverables

· Trained Dixon-Coles parameters saved to
  agent/models/football/artifacts/params.json.
· DixonColesModel.predict() runs in under 5ms for a single fixture.
· Log-likelihood reported for the training corpus.

Acceptance Criteria

```bash
pytest agent/tests/test_dixon_coles.py  # all pass
python -c "from agent.models.football.dixon_coles import DixonColesModel; \
m = DixonColesModel({'A':0.3}, {'B':0.1}); print(m.predict('A','B'))"
# {'home': 0.4x, 'draw': 0.2x, 'away': 0.3x}
```

Estimated effort

10–12 hours (higher if you fit against a real corpus).

---

Phase 6 — Ensemble & Calibration (Day 7)

Goal: Blend statistical and LLM outputs, then calibrate.

Tasks

☐ 6.1 Write agent/ensemble/predictor.py with EnsembleWeights and
  blend_probabilities().
☐ 6.2 Write agent/validation/probabilities.py with is_valid() and
  normalise_or_raise().
☐ 6.3 Write agent/validation/calibration.py with
  ProbabilityCalibrator using IsotonicRegression per class.
☐ 6.4 Write agent/analyzer/model_analyzer.py.
☐ 6.5 Write agent/analyzer/evidence_analyzer.py.
☐ 6.6 Write agent/analyzer/feature_analyzer.py.
☐ 6.7 Write agent/analyzer/consensus.py — the orchestrator that
  produces AnalyzeResponse.
☐ 6.8 Write agent/tests/test_ensemble.py and
  agent/tests/test_calibration.py.

Deliverables

· LLM weight never exceeds settings.llm_max_weight.
· Blended probabilities always sum to 1 within 1e-6.
· Calibrator is opt-in — if not fitted, raw probabilities are returned.
· ConsensusBuilder.run() returns a valid AnalyzeResponse.

Acceptance Criteria

```bash
pytest agent/tests/test_ensemble.py agent/tests/test_calibration.py  # pass

# End-to-end consensus:
curl -X POST localhost:8000/analyze \
  -H "X-Service-Token: $TOKEN" -H "Content-Type: application/json" \
  -d '{"fixture_id":"x","sport":"football","home_team":"Arsenal",...}' \
  | jq '.final_probs | add'  # ≈ 1.0
```

Estimated effort

8–10 hours.

---

Phase 7 — Frontend Foundation (Day 8)

Goal: Dashboard shell, typed API client, and static pages rendering real
data.

Tasks

☐ 7.1 Write apps/dashboard/src/types/api.ts mirroring the API
  response shapes.
☐ 7.2 Write apps/dashboard/src/lib/api-client.ts with typed
  functions for every read route.
☐ 7.3 Write apps/dashboard/src/app/layout.tsx and
  globals.css.
☐ 7.4 Write apps/dashboard/src/app/(dashboard)/layout.tsx with
  sidebar navigation.
☐ 7.5 Write apps/dashboard/src/app/(dashboard)/page.tsx
  (Overview).
☐ 7.6 Write apps/dashboard/src/app/(dashboard)/fixtures/page.tsx.
☐ 7.7 Write apps/dashboard/src/app/(dashboard)/predictions/page.tsx.
☐ 7.8 Write apps/dashboard/src/app/(dashboard)/performance/page.tsx.
☐ 7.9 Write apps/dashboard/src/app/(dashboard)/match/[id]/page.tsx
  with notFound() handling.
☐ 7.10 Write loading.tsx, error.tsx, not-found.tsx at the
  appropriate levels.

Deliverables

· Every route renders with real data from the API.
· Every error case falls through to the correct error UI.
· No any types anywhere in the tree.

Acceptance Criteria

```bash
pnpm --filter dashboard typecheck     # exits 0
pnpm --filter dashboard build         # succeeds
# Browser: every nav item loads without console errors
```

Estimated effort

10–12 hours.

---

Phase 8 — Dashboard Components (Day 9)

Goal: Charts, prediction cards, research panel, live ticker.

Tasks

☐ 8.1 Write apps/dashboard/src/components/prediction-card.tsx.
☐ 8.2 Write apps/dashboard/src/components/research-panel.tsx.
☐ 8.3 Write apps/dashboard/src/components/charts/probability-chart.tsx
  using Recharts.
☐ 8.4 Write apps/dashboard/src/components/calibration-chart.tsx.
☐ 8.5 Write apps/dashboard/src/components/live-ticker.tsx with
  countdown.
☐ 8.6 Wire probability chart into match detail page.
☐ 8.7 Wire calibration chart into performance page.
☐ 8.8 Verify responsive layout at 360px, 768px, 1280px.

Deliverables

· Charts render with null-safe fallbacks.
· LiveTicker formats durations correctly for days, hours, minutes.
· Match page shows statistical, LLM, and final probabilities side-by-side.

Acceptance Criteria

```bash
# Manual browser check:
# - Open /match/<seeded-id>
# - See PredictionCard, ProbabilityChart, ResearchPanel
# - Resize to 360px — no horizontal scroll
```

Estimated effort

8–10 hours.

---

Phase 9 — Jobs & Orchestration (Day 10)

Goal: Full pipeline runs unattended.

Tasks

☐ 9.1 Write jobs/collect-events.py.
☐ 9.2 Write jobs/analyze-events.py with bounded concurrency.
☐ 9.3 Write jobs/refresh-events.py.
☐ 9.4 Write jobs/evaluate-results.py.
☐ 9.5 Write scripts/analyze-fixture.sh.
☐ 9.6 Write jobs/README.md with cron examples.
☐ 9.7 Run the full pipeline end-to-end against seeded data.

Deliverables

· Each job exits with a non-zero code on failure.
· Each job prints a single structured summary line on completion.
· analyze-events.py respects the concurrency limit.

Acceptance Criteria

```bash
python jobs/collect-events.py football 7    # "[collect-events] created=N"
python jobs/analyze-events.py               # "[analyze-events] ok=N"
python jobs/refresh-events.py               # "[refresh-events] updated=N"
python jobs/evaluate-results.py FOOTBALL 30 # "[evaluate-results] ..."
```

Estimated effort

6–8 hours.

---

Phase 10 — Evaluation & Calibration Loop (Day 11)

Goal: Brier score, log loss, accuracy, and reliability diagram all
computed and surfaced.

Tasks

☐ 10.1 Write agent/evaluation/accuracy.py.
☐ 10.2 Write agent/evaluation/brier.py.
☐ 10.3 Write agent/evaluation/log_loss.py.
☐ 10.4 Write agent/evaluation/calibration.py with
  reliability_bins() and expected_calibration_error().
☐ 10.5 Write apps/api/src/services/performance.service.ts.
☐ 10.6 Wire /performance/summary to return the full payload.
☐ 10.7 Write agent/tests/test_evaluation.py.
☐ 10.8 Verify calibration chart renders real data.

Deliverables

· Brier score within expected range for a holdout set.
· ECE is below 0.05 on resolved predictions.
· Reliability diagram shows dots near the diagonal.

Acceptance Criteria

```bash
pytest agent/tests/test_evaluation.py     # passes
curl "localhost:3001/api/performance/summary?sport=FOOTBALL&days=30" \
  | jq '{brier:.brierScore, ece:.calibration|length}'
```

Estimated effort

8–10 hours.

---

Phase 11 — Hardening (Day 12)

Goal: Production-ready error handling, rate limiting, observability.

Tasks

☐ 11.1 Add structured logging to every service method in the API.
☐ 11.2 Add structured logging to every analyzer in the agent.
☐ 11.3 Add request ID propagation from API to agent.
☐ 11.4 Add Sentry to agent/api/main.py (production only).
☐ 11.5 Add Sentry to apps/api/src/server.ts (production only).
☐ 11.6 Add a /health/deep route on the agent that pings providers.
☐ 11.7 Write a Dockerfile for each service.
☐ 11.8 Verify docker compose up starts everything with correct
  health checks.
☐ 11.9 Add graceful shutdown handlers to both services.
☐ 11.10 Verify that killing Postgres mid-request returns 503, not 500.

Deliverables

· Every container reports healthy within 30 seconds of startup.
· Every unhandled error is captured by Sentry with the request ID.
· docker compose down shuts down cleanly.

Acceptance Criteria

```bash
docker compose up -d
sleep 30
docker compose ps                     # all healthy
docker compose exec api curl localhost:3001/health/deep
docker compose down                   # exit 0
```

Estimated effort

8–10 hours.

---

Phase 12 — Testing & Documentation (Day 13)

Goal: Every critical path covered by tests; docs complete.

Tasks

☐ 12.1 Achieve ≥ 70% coverage on agent/.
☐ 12.2 Add integration test covering the full request flow
  dashboard → API → agent → DB.
☐ 12.3 Add test for LLM failure fallback.
☐ 12.4 Add test for calibration with synthetic data.
☐ 12.5 Write README.md at root with quickstart.
☐ 12.6 Write agent/README.md.
☐ 12.7 Write jobs/README.md.
☐ 12.8 Write database/README.md.
☐ 12.9 Write API documentation examples in apps/api/README.md.
☐ 12.10 Verify all internal documentation links resolve.

Deliverables

· pytest --cov=agent --cov-report=term shows ≥ 70%.
· pnpm --filter api test -- --coverage shows ≥ 70% on services and routes.
· New contributor can go from clone to first prediction in under 15 minutes
  by following the README.

Acceptance Criteria

```bash
cd agent && pytest --cov=agent --cov-fail-under=70
pnpm -r test
# A fresh clone + README instructions produces a working prediction
```

Estimated effort

8–10 hours.

---

Phase 13 — Deployment (Day 14)

Goal: Live in production.

Tasks

☐ 13.1 Provision Postgres on Supabase or Neon.
☐ 13.2 Provision Redis on Upstash or Railway.
☐ 13.3 Deploy apps/api to Railway or Fly.
☐ 13.4 Deploy agent to Railway or Fly.
☐ 13.5 Deploy apps/dashboard to Vercel.
☐ 13.6 Set every environment variable in each platform.
☐ 13.7 Run pnpm db:deploy against production Postgres.
☐ 13.8 Configure cron for each job.
☐ 13.9 Verify the first scheduled pipeline run succeeds.
☐ 13.10 Verify the dashboard loads with real production data.
☐ 13.11 Set up uptime monitoring on /health endpoints.
☐ 13.12 Set up daily evaluation report email (optional).

Deliverables

· All three services respond on public URLs.
· First scheduled analyze run produces a persisted prediction.
· Dashboard loads production data in under 2 seconds.
· Uptime monitoring is alerting to the correct channel.

Acceptance Criteria

```bash
curl https://api.yourdomain.com/health        # ok
curl https://agent.yourdomain.com/health      # ok
curl https://yourdomain.com                   # 200, renders dashboard
# Check Supabase: Prediction table has rows from the live pipeline
```

Estimated effort

6–8 hours.

---

Phase 14 — Post-Launch Monitoring (Ongoing)

Goal: Validate the model in production and iterate.

Week 1

☐ Monitor AgentRun failure rate daily.
☐ Verify predictions are being persisted for every upcoming fixture.
☐ Verify results are being ingested within 48h of kickoff.
☐ Collect the first Brier score over ≥ 20 resolved fixtures.

Week 2–4

☐ Fit the calibrator against the first 100 resolved predictions.
☐ Re-deploy with the calibrated model.
☐ Compare pre- and post-calibration Brier scores.
☐ Document the delta in reports/calibration-YYYY-MM.md.

Week 5+

☐ Add a second sport (basketball) end-to-end.
☐ Add a second LLM provider if the first is underperforming.
☐ Consider odds integration for CLV tracking.
☐ Consider player-level features for tennis.

---

11. Testing Strategy

11.1 Test Pyramid

```
                ▲
               ╱ ╲         Manual exploratory (browser)
              ╱   ╲
             ╱─────╲       Integration (job → API → agent)
            ╱       ╲
           ╱─────────╲     Contract (Zod ⇄ Pydantic agreement)
          ╱           ╲
         ╱─────────────╲   Unit (functions, models, validation)
        ╱_______________╲
```

11.2 Coverage Requirements

Layer Minimum Rationale
agent/ensemble/ 100% Wrong blend = wrong prediction
agent/validation/ 100% These are the safety rails
agent/models/football/ 90% Statistical correctness matters
agent/ai/ 70% LLM responses are non-deterministic
agent/features/ 70% Pure functions, easy to cover
agent/api/routes/ 80% Every route has a happy and error path
apps/api/src/services/ 80% Business logic
apps/api/src/routes/ 70% Mostly thin, delegate to services

11.3 Test Data

· Synthetic fixtures — deterministic, no external API calls.
· Golden corpus — 50 historical matches with known outcomes used to
  assert Brier score does not regress.
· LLM fakes — every test that would call a real LLM uses a mock
  returning a fixed JSON payload.

11.4 Commands

```bash
# Python
cd agent
pytest -q                                     # all tests
pytest --cov=agent --cov-fail-under=70        # with coverage gate
mypy --strict .                               # type check
ruff check .                                  # lint

# TypeScript
pnpm -r typecheck                             # all packages
pnpm --filter api test                        # API unit tests
pnpm --filter dashboard typecheck             # dashboard types
```

---

12. Deployment Strategy

12.1 Environments

Environment Purpose Data
local Development Seeded fixtures
staging Pre-prod validation Copy of prod schema, fake data
production Live Real fixtures, real predictions

12.2 Promotion Flow

```
feature branch → PR → CI → merge to main → deploy to staging → smoke test → promote to prod
```

12.3 Release Checklist

Before every production deploy:

☐ pnpm -r typecheck passes
☐ pnpm -r test passes
☐ mypy --strict agent passes
☐ ruff check agent passes
☐ pytest --cov=agent --cov-fail-under=70 passes
☐ Migration is backwards-compatible (additive only)
☐ Rollback plan is documented
☐ On-call is notified

12.4 Rollback Procedure

1. Revert the deployment in Railway/Fly/Vercel.
2. If the migration was destructive, restore from the most recent snapshot.
3. Announce in the incident channel.

Migrations must be additive. Never drop a column in the same release
that introduces a new one.

---

13. Operational Runbook

13.1 Common Alerts

Alert Meaning Action
Agent /health down Agent crashed or is unreachable Check Railway logs, restart
API /health/deep reports DB fail Postgres unreachable Check Supabase dashboard
AgentRun failure rate > 10% Upstream issue Inspect error column, check LLM status page
Brier score drift > 0.05 Model performance degradation Re-fit calibrator, investigate data drift
Redis connection refused Cache down Check Upstash dashboard

13.2 Manual Interventions

Re-run analysis for a specific fixture:

```bash
./scripts/analyze-fixture.sh <fixture-id>
```

Backfill missing predictions:

```bash
python jobs/analyze-events.py
```

Force refresh of stale fixtures:

```bash
python jobs/refresh-events.py
```

Recompute evaluations for a window:

```bash
python jobs/evaluate-results.py FOOTBALL 90
```

13.3 Database Operations

Inspect the latest predictions:

```sql
SELECT f."kickoffUtc", ht.name AS home, at.name AS away,
       p."finalHome", p."finalDraw", p."finalAway", p."modelVersion"
FROM "Prediction" p
JOIN "Fixture" f ON f.id = p."fixtureId"
JOIN "Team" ht ON ht.id = f."homeTeamId"
JOIN "Team" at ON at.id = f."awayTeamId"
ORDER BY f."kickoffUtc" DESC
LIMIT 20;
```

Find unresolved predictions older than 48h:

```sql
SELECT f.id, f."kickoffUtc"
FROM "Fixture" f
LEFT JOIN "Result" r ON r."fixtureId" = f.id
WHERE f."kickoffUtc" < NOW() - INTERVAL '48 hours'
  AND r.id IS NULL
  AND f.status = 'COMPLETED';
```

---

14. Risk Register

Risk Likelihood Impact Mitigation
LLM API rate limit Medium High Retry with backoff; fall back to statistical baseline
LLM returns malformed JSON High Medium Strict schema + fallback to baseline
Data source API changes Medium High Adapter pattern in collectors; contract tests
Feature leakage slips through Low Critical assert_no_leak() at every model boundary
Calibration drift Medium High Weekly ECE check; automatic re-fit at 100 resolved
Overfitting the statistical model Medium High Holdout set; report Brier on unseen data
LLM overconfidence High High Hard cap at 0.4; evidence-based confidence adjustment
Postgres connection exhaustion Low High Prisma singleton; connection limit in Supabase
Docker image bloat Medium Low Multi-stage builds; requirements-prod.txt
Cost overrun from LLM calls Medium Medium Cache identical match queries; batch off-peak

---

15. Appendix

15.1 Glossary

Term Definition
Brier score Mean squared error between predicted probabilities and outcomes; lower is better
Calibration Agreement between predicted probabilities and observed frequencies
CLV Closing Line Value — how a prediction compares to the market's final odds
Dixon-Coles A bivariate Poisson model with a low-score correction, standard for football
ECE Expected Calibration Error — weighted average of reliability diagram gaps
Ensemble Weighted combination of multiple prediction sources
Isotonic regression Non-parametric monotonic calibration
Leakage Using information not available at prediction time
Log loss Negative log-likelihood; penalises confident wrong predictions heavily
Reliability diagram Plot of predicted probability vs observed frequency
xG Expected goals — a measure of chance quality

15.2 Environment Variables Reference

See the root .env.example for the complete list. The critical ones:

Variable Consumer Required in prod
DATABASE_URL api Yes
REDIS_URL api Yes
AGENT_URL api Yes
AGENT_SERVICE_TOKEN api, agent, jobs Yes
JWT_SECRET api Yes
XAI_API_KEY agent If provider=grok
GEMINI_API_KEY agent If provider=gemini
DEFAULT_LLM_PROVIDER agent Yes
NEXT_PUBLIC_API_URL dashboard Yes

15.3 Key Files Reference

Concern File
Schema apps/api/prisma/schema.prisma
API entry apps/api/src/server.ts
Agent entry agent/api/main.py
Consensus logic agent/analyzer/consensus.py
Ensemble weights agent/ensemble/predictor.py
Leakage guard agent/validation/leakage.py
Calibration agent/validation/calibration.py
Statistical model agent/models/football/dixon_coles.py
LLM interface agent/ai/base.py
Grok analyzer agent/ai/grok/analyzer.py
Gemini analyzer agent/ai/gemini/analyzer.py
Evaluation agent/evaluation/
Pipeline jobs jobs/

15.4 Change Log

Version Date Change
1.0.0 2026-09-26 Initial PRD and development guide

---

Sign-Off

Role Name Date
Engineering Lead  
Data Science Lead  
Product Owner  

---

This document is the authoritative specification for the Sports Prediction
Agent v1.0. Any change to scope, architecture, or phase acceptance criteria
requires a PR to this file with sign-off from the Engineering Lead.

```

This PRD_GUIDE.md is a complete, actionable specification. Key properties:

- **Every phase is independently shippable.** You can stop after any phase and have working software.
- **Acceptance criteria are shell commands.** No ambiguous "the system works" language — every phase ends with commands that either exit 0 or they don't.
- **Effort estimates are honest.** 14 phases totalling roughly 110–135 hours, or 3 weeks for one focused engineer.
- **The risk register is specific.** Every risk has a mitigation that maps to a concrete file or setting already in the codebase.
- **The runbook covers the first three months.** Post-launch monitoring is a phase, not an afterthought.