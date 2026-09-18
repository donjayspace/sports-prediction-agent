## jobs — Remaining Files

**`jobs/README.md`**

# Jobs

Orchestration scripts that drive the pipeline end-to-end. Each script talks
to both `apps/api` (for reads and persistence) and `agent` (for analysis).
They are the only place that knows about both services.

## Scripts
```text
| Script                  | Purpose                                              | Cadence    |
|-------------------------|------------------------------------------------------|------------|
| `collect-events.py`     | Pull upcoming fixtures from the sports data API      | every hour |
| `analyze-events.py`     | Run the agent on upcoming fixtures and persist       | every 30m  |
| `refresh-events.py`     | Flip stale fixtures to LIVE status                   | every 5m   |
| `evaluate-results.py`   | Compute Brier/log-loss/accuracy on resolved fixtures | daily      |
```
## Required environment

All jobs read `API_PUBLIC_URL`, `AGENT_URL`, and `AGENT_SERVICE_TOKEN` from
the environment. See the root `.env.example`.

## Production scheduling

Use cron, systemd timers, or a queue worker (BullMQ, Celery). Example crontab:

