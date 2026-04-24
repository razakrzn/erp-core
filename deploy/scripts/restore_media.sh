#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 1 ]]; then
  echo "Usage: $0 <media_backup.tar.gz> --force" >&2
  exit 1
fi

ARCHIVE_FILE="$1"
MEDIA_DIR="/var/www/media"

if [[ ! -f "$ARCHIVE_FILE" ]]; then
  echo "Media archive not found: $ARCHIVE_FILE" >&2
  exit 1
fi

if [[ "${2:-}" != "--force" ]]; then
  echo "Refusing to restore media without confirmation." >&2
  echo "Run with: $0 <media_backup.tar.gz> --force" >&2
  exit 1
fi

mkdir -p "$MEDIA_DIR"

echo "Restoring media from: $ARCHIVE_FILE"
rm -rf "${MEDIA_DIR:?}/"*
tar -C "$MEDIA_DIR" -xzf "$ARCHIVE_FILE"

echo "Media restore completed."
