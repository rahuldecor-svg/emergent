#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════════════════
# Fire Compliance OS — Daily MongoDB Backup
# Place at: /opt/fireos/ops/backup.sh
# Cron:    30 21 * * * /opt/fireos/ops/backup.sh  >> /var/log/fireos/backup.log 2>&1
#          (21:00 UTC = 02:30 IST)
# ═══════════════════════════════════════════════════════════════════════
set -euo pipefail

# ── Config ────────────────────────────────────────────────────────────
BACKUP_DIR="/opt/fireos/backups"
RETENTION_DAYS=30
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
ENV_FILE="/opt/fireos/app/backend/.env"

# ── Load MONGO_URL + DB_NAME from .env ───────────────────────────────
if [ ! -f "$ENV_FILE" ]; then
  echo "[$(date)] ERROR: .env not found at $ENV_FILE"
  exit 1
fi
export $(grep -E '^(MONGO_URL|DB_NAME)=' "$ENV_FILE" | sed 's/^/export /; s/"//g')

mkdir -p "$BACKUP_DIR"

# ── 1. Dump MongoDB ───────────────────────────────────────────────────
ARCHIVE="$BACKUP_DIR/fireos-${TIMESTAMP}.gz"
echo "[$(date)] Starting backup → $ARCHIVE"

mongodump --uri="$MONGO_URL" --db="$DB_NAME" --gzip --archive="$ARCHIVE" --quiet

if [ ! -s "$ARCHIVE" ]; then
  echo "[$(date)] ERROR: Backup file is empty!"
  exit 2
fi

SIZE=$(du -h "$ARCHIVE" | cut -f1)
echo "[$(date)] Backup complete: $ARCHIVE ($SIZE)"

# ── 2. Upload to R2 archive bucket (optional) ────────────────────────
# Requires `rclone config` setup with remote name "r2"
if command -v rclone &> /dev/null && rclone listremotes 2>/dev/null | grep -q "^r2:"; then
  echo "[$(date)] Uploading to R2..."
  rclone copy "$ARCHIVE" "r2:fireos-backups/$(date +%Y/%m)/" --quiet && \
    echo "[$(date)] R2 upload OK" || \
    echo "[$(date)] WARNING: R2 upload failed (local copy retained)"
else
  echo "[$(date)] R2 not configured — local copy only"
fi

# ── 3. Prune old backups ──────────────────────────────────────────────
find "$BACKUP_DIR" -name "fireos-*.gz" -mtime +"$RETENTION_DAYS" -delete -print \
  | while read f; do echo "[$(date)] Pruned: $f"; done

# ── 4. Disk usage report ──────────────────────────────────────────────
TOTAL=$(du -sh "$BACKUP_DIR" | cut -f1)
echo "[$(date)] Total backup dir: $TOTAL"

# ── 5. Verify (last 5 backups present) ────────────────────────────────
COUNT=$(find "$BACKUP_DIR" -name "fireos-*.gz" | wc -l)
if [ "$COUNT" -lt 5 ]; then
  echo "[$(date)] WARNING: Only $COUNT backup(s) on disk — investigate retention"
fi

echo "[$(date)] === BACKUP CYCLE COMPLETE ==="
