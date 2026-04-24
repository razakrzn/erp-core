#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
COMPOSE_FILE="$ROOT_DIR/docker-compose.yml"
BACKUP_DIR="$ROOT_DIR/deploy/backups/db"
RETENTION_DAYS=14
DB_NAME="emrdb"
DB_USER="root"

if [[ ! -f "$COMPOSE_FILE" ]]; then
  echo "Compose file not found: $COMPOSE_FILE" >&2
  exit 1
fi

mkdir -p "$BACKUP_DIR"

timestamp="$(date +%Y%m%d_%H%M%S)"
backup_file="$BACKUP_DIR/${DB_NAME}_${timestamp}.dump"
checksum_file="${backup_file}.sha256"

echo "Creating PostgreSQL backup: $backup_file"
docker compose -f "$COMPOSE_FILE" exec -T db pg_dump -U "$DB_USER" -d "$DB_NAME" -Fc > "$backup_file"

sha256sum "$backup_file" > "$checksum_file"
echo "Checksum written: $checksum_file"

echo "Pruning backups older than $RETENTION_DAYS days in $BACKUP_DIR"
find "$BACKUP_DIR" -type f -name "*.dump" -mtime "+$RETENTION_DAYS" -delete
find "$BACKUP_DIR" -type f -name "*.dump.sha256" -mtime "+$RETENTION_DAYS" -delete

echo "DB backup completed."
