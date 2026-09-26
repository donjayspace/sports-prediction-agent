#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

# 1. Ensure the docs tree exists
mkdir -p docs/assets
touch docs/assets/.gitkeep

# 2. Move an existing PRD_GUIDE.md into docs/ if it's at the repo root
if [[ -f PRD_GUIDE.md && ! -f docs/PRD_GUIDE.md ]]; then
  mv PRD_GUIDE.md docs/PRD_GUIDE.md
  echo "Moved PRD_GUIDE.md → docs/PRD_GUIDE.md"
fi

if [[ ! -f docs/PRD_GUIDE.md ]]; then
  echo "ERROR: docs/PRD_GUIDE.md not found. Place the PRD content there first."
  exit 1
fi

# 3. Write docs/README.md if it doesn't exist
if [[ ! -f docs/README.md ]]; then
  cat > docs/README.md << 'DOCS_EOF'
# Documentation

[![Download PRD](https://img.shields.io/badge/Download-PRD__GUIDE.md-blue?style=for-the-badge&logo=markdown)](https://raw.githubusercontent.com/donjayspace/sports-prediction-agent/main/docs/PRD_GUIDE.md)

## Contents

| Document | Description |
|---|---|
| [PRD_GUIDE.md](./PRD_GUIDE.md) | Product requirements and 14-phase development guide |
| [../agent/README.md](../agent/README.md) | Agent service overview and provider configuration |
| [../jobs/README.md](../jobs/README.md) | Pipeline orchestration scripts and cron examples |
| [../database/README.md](../database/README.md) | Prisma schema location and migration policy |
DOCS_EOF
  echo "Created docs/README.md"
fi

# 4. Stage everything
git add docs/README.md docs/PRD_GUIDE.md docs/assets/.gitkeep

echo ""
echo "Staged files:"
git status --short docs/

echo ""
echo "Next steps:"
echo "  git commit -m 'docs: add PRD and development guide'"
echo "  git push origin main"
