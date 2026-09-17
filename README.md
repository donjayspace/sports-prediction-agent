# Sports Prediction Agent

A production-oriented sports research and forecasting platform for football, basketball, tennis, and table tennis.

> **Scope:** This repository is designed for sports research, statistical forecasting, model evaluation, and historical analysis. It does not implement wagering, staking, bookmaker integration, or bankroll optimization.

## Architecture

```text
Scheduler
   ↓
Event Collectors → Data Validation → Feature Engineering
   ↓                         ↓
Structured Sports Data     News / Research Evidence
   └──────────────┬──────────────┘
                  ↓
        Statistical / ML Models
                  ↓
          AI Research Providers
          ├── Gemini
          └── Grok
                  ↓
          Model Analyzer / Consensus
                  ↓
       Probability Validation + Calibration
                  ↓
             Database / Reports
                  ↓
              Dashboard / API
```

## Supported sports

- Football / soccer
- Basketball
- Tennis
- Table tennis

## AI providers

The AI layer is provider-agnostic. Gemini and Grok implement the same research-provider interface so providers can be enabled, disabled, or compared without changing the forecasting core.

## Development status

Initial production scaffold. Sport-specific collectors, feature pipelines, statistical models, evaluation, API, and dashboard are being implemented incrementally.

## Environment

Copy `.env.example` to `.env` and provide the required API credentials. Never commit secrets.

## Run

```bash
python -m scripts.run_sports_analysis
```

## Quality principles

- Preserve point-in-time information to prevent data leakage.
- Validate structured data before AI analysis.
- Never invent fixtures, statistics, injuries, lineups, or citations.
- Keep AI-generated research separate from deterministic model outputs.
- Store model, prompt, feature, and data versions with every forecast.
- Evaluate forecasts out-of-sample using Brier score, log loss, calibration, and accuracy.
- Treat uncertainty as a first-class output.
