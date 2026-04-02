#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

"$ROOT_DIR/deploy/scripts/backup_db.sh"
"$ROOT_DIR/deploy/scripts/backup_media.sh"

echo "All backups completed."
