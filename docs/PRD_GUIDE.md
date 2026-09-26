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
