# ARCHITECTURE STRUCTURE 

```text
‎sports-prediction-agent/
‎│
‎├── apps/
‎│   │
‎│   ├── api/                       # Node.js + Fastify + Prisma
‎│   │   ├── src/
‎│   │   │   ├── server.ts          # Fastify entrypoint
‎│   │   │   ├── config/
‎│   │   │   │   └── env.ts
‎│   │   │   ├── plugins/
‎│   │   │   │   ├── prisma.ts         # Prisma client singleton
‎│   │   │   │   ├── auth.ts           # JWT / service tokens
‎│   │   │   │   └── cors.ts
‎│   │   │   ├── routes/
‎│   │   │   │   ├── fixtures.ts
‎│   │   │   │   ├── predictions.ts
‎│   │   │   │   ├── performance.ts
‎│   │   │   │   ├── agent.ts        # Internal agent callback routes
‎│   │   │   │   └── health.ts
‎│   │   │   ├── services/
‎│   │   │   │   ├── fixture.service.ts
‎│   │   │   │   ├── prediction.service.ts
‎│   │   │   │   ├── agent.service.ts  # Calls Python agent
‎│   │   │   │   └── performance.service.ts
‎│   │   │   ├── queues/
‎│   │   │   │   ├── bullmq.ts
‎│   │   │   │   └── jobs.ts
‎│   │   │   └── types/
‎│   │   ├── prisma/
‎│   │   │   ├── schema.prisma
‎│   │   │   └── migrations/
‎│   │   ├── tests/
‎│   │   ├── package.json
‎│   │   ├── tsconfig.json
‎│   │   └── Dockerfile
‎│   │
‎│   └── dashboard/                 # Next.js 15 (App Router)
‎│       ├── src/
‎│       │   ├── app/
‎│       │   │   ├── (dashboard)/
‎│       │   │   │   ├── page.tsx
‎│       │   │   │   ├── fixtures/page.tsx
‎│       │   │   │   ├── match/[id]/page.tsx
‎│       │   │   │   ├── predictions/page.tsx
‎│       │   │   │   └── performance/page.tsx
‎│       │   │   └── layout.tsx
‎│       │   ├── components/
‎│       │   │   ├── charts/
‎│       │   │   ├── prediction-card.tsx
‎│       │   │   └── research-panel.tsx
‎│       │   ├── lib/
‎│       │   │   ├── api-client.ts     # Typed client for apps/api
‎│       │   │   └── websocket.ts
‎│       │   └── types/
‎│       │       └── api.ts            # Shared types 
‎│       ├── package.json
‎│       ├── next.config.js
‎│       └── Dockerfile
‎│
‎├── agent/                        # Python FastAPI service
‎│   │
‎│   ├── ai/
‎│   │   ├── base.py               # Abstract Analyzer interface
‎│   │   ├── factory.py            # Provider selection from config
‎│   │   ├── schemas.py            # Pydantic request/response models
‎│   │   │
‎│   │   ├── gemini/
‎│   │   │   ├── client.py             # google-genai wrapper
‎│   │   │   └── analyzer.py           # Gemini research analyzer
‎│   │   │
‎│   │   └── grok/
‎│   │       ├── client.py             # xai-sdk wrapper
‎│   │       └── analyzer.py           # Grok web-research analyzer
‎│   │
‎│   ├── analyzer/
‎│   │   ├── model_analyzer.py       # Runs statistical models
‎│   │   ├── evidence_analyzer.py    # Weighs LLM research evidence
‎│   │   ├── feature_analyzer.py     # Interprets engineered features
‎│   │   └── consensus.py            # Combines analyzer outputs
‎│   │
‎│   ├── collectors/
‎│   │   ├── fixtures.py
‎│   │   ├── results.py
‎│   │   ├── rankings.py
‎│   │   ├── injuries.py
‎│   │   └── news.py
‎│   │
‎│   ├── features/
‎│   │   ├── football.py
‎│   │   ├── basketball.py
‎│   │   ├── tennis.py
‎│   │   └── table_tennis.py
‎│   │
‎│   ├── models/
‎│   │   ├── football/
‎│   │   │   ├── dixon_coles.py
‎│   │   │   ├── xgboost_model.py
‎│   │   │   └── artifacts/
‎│   │   ├── basketball/
‎│   │   ├── tennis/
‎│   │   └── table_tennis/
‎│   │
‎│   ├── ensemble/
‎│   │   └── predictor.py              # Confidence-weighted blend
‎│   │
‎│   ├── validation/
‎│   │   ├── probabilities.py          # Sums to 1, no negatives
‎│   │   ├── calibration.py            # Isotonic / Platt
‎│   │   ├── data_quality.py           # Missing fields, outliers
‎│   │   └── leakage.py                # Timestamp guards
‎│   │
‎│   ├── evaluation/
‎│   │   ├── accuracy.py
‎│   │   ├── brier.py
‎│   │   ├── log_loss.py
‎│   │   └── calibration.py
‎│   │
‎│   ├── api/                          # FastAPI app
‎│   │   ├── main.py
‎│   │   ├── routes/
‎│   │   │   ├── analyze.py
‎│   │   │   ├── research.py
‎│   │   │   └── health.py
‎│   │   └── clients/
‎│   │       └── backend_client.py     # httpx client → apps/api
‎│   │
‎│   ├── core/
‎│   │   ├── config.py                 # Pydantic Settings
‎│   │   └── logging.py
‎│   │
‎│   └── pyproject.toml
‎│
‎├── database/
‎│   ├── seed/
‎│   │   └── seed.ts               # Runs via apps/api
‎│   └── README.md                 # Points to apps/api/prisma
‎│
‎├── jobs/                         # Scheduled tasks (cron / BullMQ)
‎│   ├── collect-events.py
‎│   ├── analyze-events.py
‎│   ├── refresh-events.py
‎│   └── evaluate-results.py
‎│
‎├── reports/
‎├── scripts/
‎│   ├── dev.sh
‎│   └── migrate.sh
‎│
‎├── tests/
‎│   ├── agent/
‎│   └── api/
‎│
‎├── docker-compose.yml
‎├── .env.example
‎├── package.json                      # Root workspace
‎├── pnpm-workspace.yaml
‎└── README.md
```


