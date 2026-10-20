#!/bin/bash
set -euo pipefail

DB_PATH="/opt/cloudshield/data/cloudshield.db"
BACKUP_DIR="/tmp/cloudshield_backups"
BUCKET_NAME="cloudshield-artifacts-206238482111-ap-southeast-2"
TIMESTAMP=$(date -u +%Y%m%d_%H%M%SZ)
BACKUP_FILE="${BACKUP_DIR}/cloudshield_${TIMESTAMP}.db"

mkdir -p "${BACKUP_DIR}"

if [ -f "${DB_PATH}" ]; then
    echo "[$(date -u)] Creating consistent SQLite backup..."
    sqlite3 "${DB_PATH}" ".backup '${BACKUP_FILE}'"
    
    echo "[$(date -u)] Uploading backup to s3://${BUCKET_NAME}/backups/..."
    aws s3 cp "${BACKUP_FILE}" "s3://${BUCKET_NAME}/backups/cloudshield_${TIMESTAMP}.db" --region ap-southeast-2
    
    rm -f "${BACKUP_FILE}"
    echo "[$(date -u)] Backup completed and local temp file cleaned."
else
    echo "[$(date -u)] Warning: Database file ${DB_PATH} not found. Skipping backup."
fi
