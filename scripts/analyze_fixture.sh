#!/usr/bin/env bash
set -euo pipefail

if [[ -z "${1:-}" ]]; then
  echo "Usage: $0 <fixture-id>"
  exit 1
fi

FIXTURE_ID="$1"
API_URL="${API_PUBLIC_URL:-http://localhost:3001}"
SERVICE_TOKEN="${AGENT_SERVICE_TOKEN:?AGENT_SERVICE_TOKEN is required}"

echo "Analyzing fixture $FIXTURE_ID..."

curl -fsS -X POST "$API_URL/api/internal/agent/analyze/$FIXTURE_ID" \
  -H "X-Service-Token: $SERVICE_TOKEN" \
  | python -m json.tool
