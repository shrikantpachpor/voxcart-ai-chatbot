#!/usr/bin/env bash
# Helper to purge sensitive files from git history using git-filter-repo.
# Run from the repository root (one level above `app/`).
# WARNING: This will rewrite git history. Create a backup clone before running.

set -euo pipefail

PATHS_TO_REMOVE=("app/.env" "app/chatbot_logs.log")

if ! command -v git >/dev/null 2>&1; then
  echo "git is not installed or not in PATH. Aborting."
  exit 1
fi

if ! command -v git-filter-repo >/dev/null 2>&1; then
  echo "git-filter-repo not found. Installing via pip..."
  python -m pip install --user git-filter-repo
fi

echo "This script will rewrite git history and remove: ${PATHS_TO_REMOVE[*]}"
echo "Create a backup clone before proceeding. Example: git clone --mirror . ../repo-backup.git"
read -p "Continue? (y/N) " c
if [[ "$c" != "y" ]]; then
  echo "Aborted by user."
  exit 0
fi

ARGS=()
for p in "${PATHS_TO_REMOVE[@]}"; do
  ARGS+=(--path "$p")
done
ARGS+=(--invert-paths)

echo "Running git-filter-repo..."
git filter-repo "${ARGS[@]}"

echo "Filter complete. You must force-push cleaned branches to remote:"
echo "git push --force --all"
echo "git push --force --tags"
echo "Also revoke and rotate any exposed keys immediately (OpenAI, LangSmith, DB password)."
