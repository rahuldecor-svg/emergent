#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════════════════
# Fire Compliance OS — Restore MongoDB from backup
# Usage: ./restore.sh /opt/fireos/backups/fireos-YYYYMMDD-HHMMSS.gz
# ═══════════════════════════════════════════════════════════════════════
set -euo pipefail

ARCHIVE="${1:-}"
if [ -z "$ARCHIVE" ] || [ ! -f "$ARCHIVE" ]; then
  echo "Usage: $0 <archive.gz>"
  echo "Available backups:"
  ls -lh /opt/fireos/backups/ 2>/dev/null | grep -E "fireos-.*\.gz" | tail -10
  exit 1
fi

ENV_FILE="/opt/fireos/app/backend/.env"
export $(grep -E '^(MONGO_URL|DB_NAME)=' "$ENV_FILE" | sed 's/^/export /; s/"//g')

echo "⚠️  WARNING: This will DROP and REPLACE database '$DB_NAME'."
echo "Archive: $ARCHIVE ($(du -h "$ARCHIVE" | cut -f1))"
read -p "Type DB name to confirm: " confirm
if [ "$confirm" != "$DB_NAME" ]; then
  echo "Aborted."
  exit 1
fi

echo "[$(date)] Restoring..."
mongorestore --uri="$MONGO_URL" --db="$DB_NAME" --gzip --archive="$ARCHIVE" --drop --quiet

echo "[$(date)] Restore complete. Restarting backend..."
sudo supervisorctl restart fireos-backend
sleep 3
curl -sf "http://localhost:8001/api/health" && echo "[$(date)] ✅ Health check passed"
