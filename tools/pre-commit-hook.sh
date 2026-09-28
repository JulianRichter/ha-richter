#!/usr/bin/env bash
# ====================================================================
# Git Pre-Commit Hook for Home Assistant
# Runs tools/validate_config.py before allowing git commit.
# Blocks commits if syntax errors, missing secrets, or broken scripts exist.
# ====================================================================
set -e

SCRIPT_DIR="$(git rev-parse --show-toplevel)"
VALIDATOR="${SCRIPT_DIR}/tools/validate_config.py"

if [ -f "${VALIDATOR}" ]; then
  echo "🔍 Running Home Assistant pre-commit validation..."
  python3 "${VALIDATOR}"
  if [ $? -ne 0 ]; then
    echo "❌ Git commit blocked: Pre-flight validation failed."
    exit 1
  fi
fi

exit 0
