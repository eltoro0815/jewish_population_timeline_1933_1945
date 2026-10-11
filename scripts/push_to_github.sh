#!/usr/bin/env bash
# Create private GitHub repo from this directory and push main.
set -euo pipefail
cd "$(dirname "$0")/.."

if ! gh auth status >/dev/null 2>&1; then
  echo "Not authenticated. Run: gh auth login -h github.com -p ssh -w"
  echo "Or:  export GH_TOKEN=<PAT with repo scope>"
  exit 1
fi

gh repo create jewish_population_timeline_1933_1945 \
  --private \
  --source=. \
  --remote=origin \
  --push

gh repo view --web 2>/dev/null || gh repo view
