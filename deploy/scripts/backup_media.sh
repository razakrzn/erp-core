#!/usr/bin/env bash
set -euo pipefail

BACKUP_DIR="deploy/backups/media"
MEDIA_DIR="/var/www/media"
RETENTION_DAYS=14

if [[ ! -d "$MEDIA_DIR" ]]; then
  echo "Media directory not found: $MEDIA_DIR" >&2
  exit 1
fi

mkdir -p "$BACKUP_DIR"

timestamp="$(date +%Y%m%d_%H%M%S)"
archive="$BACKUP_DIR/media_${timestamp}.tar.gz"
checksum="${archive}.sha256"

echo "Creating media backup: $archive"
tar -C "$MEDIA_DIR" -czf "$archive" .
sha256sum "$archive" > "$checksum"

echo "Pruning backups older than $RETENTION_DAYS days in $BACKUP_DIR"
find "$BACKUP_DIR" -type f -name "media_*.tar.gz" -mtime "+$RETENTION_DAYS" -delete
find "$BACKUP_DIR" -type f -name "media_*.tar.gz.sha256" -mtime "+$RETENTION_DAYS" -delete

echo "Media backup completed."
