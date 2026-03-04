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

HOOKS=(post-merge post-checkout)

chmod +x "$ROOT_DIR/scripts/postman-sync.sh"

for hook in "${HOOKS[@]}"; do
  SRC_HOOK="$ROOT_DIR/scripts/git-hooks/$hook"
  DST_HOOK="$ROOT_DIR/.git/hooks/$hook"

  if [[ ! -f "$SRC_HOOK" ]]; then
    echo "ERROR: source hook not found: $SRC_HOOK" >&2
    exit 1
  fi

  chmod +x "$SRC_HOOK"

  if [[ -f "$DST_HOOK" ]]; then
    if cmp -s "$SRC_HOOK" "$DST_HOOK"; then
      echo "$hook hook already installed."
      continue
    fi
    cp "$DST_HOOK" "$DST_HOOK.bak.$(date +%s)"
  fi

  # Try symlink first, fall back to copy.
  ln -sf "../../scripts/git-hooks/$hook" "$DST_HOOK" 2>/dev/null || cp "$SRC_HOOK" "$DST_HOOK"
  chmod +x "$DST_HOOK"

  echo "Installed .git/hooks/$hook"
done
