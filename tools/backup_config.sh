#!/usr/bin/env bash
# ====================================================================
# Home Assistant Config Snapshot Tool
# Creates a lightweight timestamped tarball backup of all yaml packages,
# dashboards, and core configurations before applying major changes.
# ====================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BASE_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
BACKUP_DIR="${BASE_DIR}/.backups"
TIMESTAMP="$(date +%Y%m%d_%H%M%S)"
ARCHIVE_NAME="ha_config_${TIMESTAMP}.tar.gz"

mkdir -p "${BACKUP_DIR}"

echo "Creating snapshot: ${ARCHIVE_NAME}..."
tar -czf "${BACKUP_DIR}/${ARCHIVE_NAME}" \
  -C "${BASE_DIR}" \
  --exclude='.storage' \
  --exclude='.cache' \
  --exclude='deps' \
  --exclude='tts' \
  --exclude='image' \
  --exclude='*.db' \
  --exclude='*.log*' \
  --exclude='.backups' \
  configuration.yaml \
  automations.yaml \
  scripts.yaml \
  scenes.yaml \
  GEMINI.md \
  README.md \
  include \
  dashboards \
  themes

echo "✅ Backup created successfully: ${BACKUP_DIR}/${ARCHIVE_NAME} ($(du -h "${BACKUP_DIR}/${ARCHIVE_NAME}" | cut -f1))"

# Keep the most recent 10 snapshots
cd "${BACKUP_DIR}"
ls -tp ha_config_*.tar.gz 2>/dev/null | grep -v '/$' | tail -n +11 | xargs -I {} rm -f -- {} || true
echo "Retention policy: Kept the latest 10 backups in .backups/"

