#!/usr/bin/env bash
set -euo pipefail

# Installs repo hook templates into .git/hooks
# Idempotent + safe: backs up existing hook if it differs.

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

if [[ ! -d .git ]]; then
  echo "ERROR: .git directory not found. Run this from inside the repo." >&2
  exit 1
fi

SRC_HOOK="$ROOT_DIR/scripts/git-hooks/post-merge"
DST_HOOK="$ROOT_DIR/.git/hooks/post-merge"

if [[ ! -f "$SRC_HOOK" ]]; then
  echo "ERROR: source hook not found: $SRC_HOOK" >&2
  exit 1
fi

chmod +x "$ROOT_DIR/scripts/postman-sync.sh" "$SRC_HOOK"

if [[ -f "$DST_HOOK" ]]; then
  if cmp -s "$SRC_HOOK" "$DST_HOOK"; then
    echo "post-merge hook already installed."
    exit 0
  fi
  cp "$DST_HOOK" "$DST_HOOK.bak.$(date +%s)"
fi

# Try symlink first, fall back to copy.
ln -sf "../../scripts/git-hooks/post-merge" "$DST_HOOK" 2>/dev/null || cp "$SRC_HOOK" "$DST_HOOK"
chmod +x "$DST_HOOK"

echo "Installed .git/hooks/post-merge"
