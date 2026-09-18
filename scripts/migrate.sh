#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

ENVIRONMENT="${1:-development}"

case "$ENVIRONMENT" in
  development)
    echo "Running development migration..."
    pnpm db:generate
    pnpm db:migrate
    ;;
  production)
    echo "Applying production migrations..."
    pnpm db:generate
    pnpm db:deploy
    ;;
  seed)
    echo "Seeding database..."
    pnpm db:seed
    ;;
  *)
    echo "Usage: $0 [development|production|seed]"
    exit 1
    ;;
esac

echo "Done."
