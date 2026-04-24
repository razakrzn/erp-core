#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
COMPOSE_FILE="$ROOT_DIR/docker-compose.yml"

if [[ $# -lt 1 ]]; then
  echo "Usage: $0 <media_backup.tar.gz>" >&2
  exit 1
fi

ARCHIVE_FILE="$1"

if [[ ! -f "$ARCHIVE_FILE" ]]; then
  echo "Media archive not found: $ARCHIVE_FILE" >&2
  exit 1
fi

if [[ "${2:-}" != "--force" ]]; then
  echo "Refusing to restore media without confirmation." >&2
  echo "Run with: $0 <media_backup.tar.gz> --force" >&2
  exit 1
fi

if [[ ! -f "$COMPOSE_FILE" ]]; then
  echo "Compose file not found: $COMPOSE_FILE" >&2
  exit 1
fi

echo "Stopping web and celery while restoring media..."
docker compose -f "$COMPOSE_FILE" stop web celery

echo "Restoring media from: $ARCHIVE_FILE"
docker compose -f "$COMPOSE_FILE" run --rm -T nginx \
  sh -c 'rm -rf /var/www/media/* && tar -C /var/www/media -xzf -' < "$ARCHIVE_FILE"

echo "Starting services..."
docker compose -f "$COMPOSE_FILE" up -d web celery nginx

echo "Media restore completed."
