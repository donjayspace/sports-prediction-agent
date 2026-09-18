#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

if [[ ! -f .env ]]; then
  echo "Missing .env — copy .env.example to .env and fill in secrets."
  exit 1
fi

if ! command -v docker >/dev/null 2>&1; then
  echo "Docker is required but not installed."
  exit 1
fi

echo "Starting infrastructure (postgres, redis)..."
docker compose up -d postgres redis

echo "Waiting for postgres..."
until docker compose exec -T postgres pg_isready -U sports -d sports >/dev/null 2>&1; do
  sleep 1
done

echo "Running migrations..."
pnpm db:generate
pnpm db:deploy

echo "Starting api, dashboard, and agent..."
trap 'kill 0' EXIT
pnpm dev:api &
pnpm dev:dashboard &
pnpm agent:dev &

wait
