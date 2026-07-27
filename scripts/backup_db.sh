#!/bin/bash
# =============================================================================
# Mithrava Database Backup Script
# Creates a timestamped pg_dump of the PostgreSQL database.
#
# Usage:
#   ./backup_db.sh                           # Uses env vars
#   ./backup_db.sh mydb postgres localhost    # Override connection params
#
# Requires: pg_dump (installed with postgresql-client)
# =============================================================================

set -euo pipefail

# ---------------------------------------------------------------------------
# Configuration (override via args or env vars)
# ---------------------------------------------------------------------------

DB_HOST="${1:-${POSTGRES_HOST:-localhost}}"
DB_PORT="${POSTGRES_PORT:-5432}"
DB_USER="${POSTGRES_USER:-mithrava}"
DB_NAME="${POSTGRES_DB:-mithrava}"
BACKUP_DIR="${BACKUP_DIR:-./backups}"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="${BACKUP_DIR}/${DB_NAME}_${TIMESTAMP}.sql.gz"

# ---------------------------------------------------------------------------
# Pre-flight checks
# ---------------------------------------------------------------------------

if ! command -v pg_dump &> /dev/null; then
    echo "ERROR: pg_dump not found. Install postgresql-client."
    echo "  Ubuntu/Debian: apt-get install postgresql-client"
    echo "  macOS: brew install postgresql"
    exit 1
fi

if [ -z "${POSTGRES_PASSWORD:-}" ]; then
    echo "WARNING: POSTGRES_PASSWORD not set. Trying passwordless connection."
fi

mkdir -p "$BACKUP_DIR"

# ---------------------------------------------------------------------------
# Backup
# ---------------------------------------------------------------------------

echo "Backing up database: ${DB_NAME}"
echo "  Host: ${DB_HOST}:${DB_PORT}"
echo "  User: ${DB_USER}"
echo "  Output: ${BACKUP_FILE}"
echo ""

PGPASSWORD="${POSTGRES_PASSWORD:-}" pg_dump \
    -h "$DB_HOST" \
    -p "$DB_PORT" \
    -U "$DB_USER" \
    -d "$DB_NAME" \
    --no-owner \
    --no-privileges \
    --clean \
    --if-exists \
    -F p \
    | gzip > "$BACKUP_FILE"

# ---------------------------------------------------------------------------
# Verify
# ---------------------------------------------------------------------------

FILE_SIZE=$(stat -f%z "$BACKUP_FILE" 2>/dev/null || stat -c%s "$BACKUP_FILE" 2>/dev/null || echo "0")

if [ "$FILE_SIZE" -gt 100 ]; then
    echo ""
    echo "Backup successful!"
    echo "  File: ${BACKUP_FILE}"
    echo "  Size: $(numfmt --to=iec-i --suffix=B "$FILE_SIZE" 2>/dev/null || echo "${FILE_SIZE} bytes")"
else
    echo ""
    echo "ERROR: Backup file is suspiciously small (${FILE_SIZE} bytes)."
    echo "  Check connection parameters and database status."
    exit 1
fi

# ---------------------------------------------------------------------------
# Cleanup old backups (keep last 7)
# ---------------------------------------------------------------------------

BACKUP_COUNT=$(ls -1 "${BACKUP_DIR}"/${DB_NAME}_*.sql.gz 2>/dev/null | wc -l)
if [ "$BACKUP_COUNT" -gt 7 ]; then
    DELETE_COUNT=$((BACKUP_COUNT - 7))
    ls -1t "${BACKUP_DIR}"/${DB_NAME}_*.sql.gz | tail -n "$DELETE_COUNT" | xargs rm -f
    echo "  Cleaned up ${DELETE_COUNT} old backup(s). Keeping last 7."
fi
