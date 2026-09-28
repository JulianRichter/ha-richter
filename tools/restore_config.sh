#!/usr/bin/env bash
# ====================================================================
# Home Assistant Config Rollback Tool
# Restores configurations from a designated .backups tarball.
# Usage: ./tools/restore_config.sh [optional_tarball_name]
# If no argument is provided, restores the most recent snapshot.
# ====================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BASE_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
BACKUP_DIR="${BASE_DIR}/.backups"

if [ ! -d "${BACKUP_DIR}" ]; then
  echo "❌ Error: No .backups directory found."
  exit 1
fi

if [ $# -ge 1 ]; then
  TARGET_ARCHIVE="$1"
  if [ ! -f "${TARGET_ARCHIVE}" ]; then
    TARGET_ARCHIVE="${BACKUP_DIR}/$1"
  fi
else
  # Select most recent archive
  TARGET_ARCHIVE="$(ls -t "${BACKUP_DIR}"/ha_config_*.tar.gz 2>/dev/null | head -n 1 || true)"
fi

if [ -z "${TARGET_ARCHIVE}" ] || [ ! -f "${TARGET_ARCHIVE}" ]; then
  echo "❌ Error: No backup archive found to restore."
  exit 1
fi

echo "⚠️ Restoring configuration from: ${TARGET_ARCHIVE}"
read -p "Are you sure you want to overwrite current config? (y/N): " -r CONFIRM
if [[ "${CONFIRM}" =~ ^[Yy]$ ]]; then
  tar -xzf "${TARGET_ARCHIVE}" -C "${BASE_DIR}"
  echo "✅ Configuration restored successfully from: ${TARGET_ARCHIVE}"
else
  echo "Aborted."
fi

