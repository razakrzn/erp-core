#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
COMPOSE_FILE="${COMPOSE_FILE:-$ROOT_DIR/docker-compose.yml}"
BACKUP_DIR="${BACKUP_DIR:-$ROOT_DIR/deploy/backups/media}"
RETENTION_DAYS="${RETENTION_DAYS:-30}"

if [[ ! -f "$COMPOSE_FILE" ]]; then
  echo "Compose file not found: $COMPOSE_FILE" >&2
  exit 1
fi

mkdir -p "$BACKUP_DIR"

timestamp="$(date +%Y%m%d_%H%M%S)"
archive_file="$BACKUP_DIR/media_${timestamp}.tar.gz"
checksum_file="${archive_file}.sha256"

echo "Creating media backup: $archive_file"
docker compose -f "$COMPOSE_FILE" run --rm -T nginx \
  sh -c 'tar -C /var/www/media -czf - .' > "$archive_file"

sha256sum "$archive_file" > "$checksum_file"
echo "Checksum written: $checksum_file"

echo "Pruning media backups older than $RETENTION_DAYS days in $BACKUP_DIR"
find "$BACKUP_DIR" -type f -name "media_*.tar.gz" -mtime "+$RETENTION_DAYS" -delete
find "$BACKUP_DIR" -type f -name "media_*.tar.gz.sha256" -mtime "+$RETENTION_DAYS" -delete

echo "Media backup completed."
