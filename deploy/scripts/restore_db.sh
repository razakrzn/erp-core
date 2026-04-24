#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
COMPOSE_FILE="$ROOT_DIR/docker-compose.yml"
DB_NAME="emrdb"
DB_USER="root"

if [[ $# -lt 1 ]]; then
  echo "Usage: $0 <backup_file.dump>" >&2
  exit 1
fi

BACKUP_FILE="$1"

if [[ ! -f "$BACKUP_FILE" ]]; then
  echo "Backup file not found: $BACKUP_FILE" >&2
  exit 1
fi

if [[ "${2:-}" != "--force" ]]; then
  echo "Refusing to restore without confirmation." >&2
  echo "Run with: $0 <backup_file.dump> --force" >&2
  exit 1
fi

if [[ ! -f "$COMPOSE_FILE" ]]; then
  echo "Compose file not found: $COMPOSE_FILE" >&2
  exit 1
fi

echo "Stopping web and celery to avoid writes during restore..."
docker compose -f "$COMPOSE_FILE" stop web celery

echo "Restoring PostgreSQL backup: $BACKUP_FILE"
docker compose -f "$COMPOSE_FILE" exec -T db psql -U "$DB_USER" -d postgres \
  -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname='${DB_NAME}' AND pid <> pg_backend_pid();" >/dev/null

docker compose -f "$COMPOSE_FILE" exec -T db pg_restore \
  -U "$DB_USER" -d "$DB_NAME" \
  --clean --if-exists --no-owner --no-privileges < "$BACKUP_FILE"

echo "Running migrations..."
docker compose -f "$COMPOSE_FILE" run --rm web python manage.py migrate

echo "Starting services..."
docker compose -f "$COMPOSE_FILE" up -d web celery nginx

echo "DB restore completed."
