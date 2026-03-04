#!/usr/bin/env bash
set -euo pipefail

# Sync OpenAPI -> Postman artifacts (spec-first)
# - (Optional) Generates OpenAPI spec via drf-spectacular management command
# - Writes to postman/specs/openapi.yaml
# - Generates a deterministic Postman Collection JSON committed in repo:
#     postman/collections-generated/ERP Core API.collection.json
#
# Strategy:
# 1) Generate OpenAPI (unless --no-openapi is passed)
# 2) Generate Collection JSON using Postman CLI if available
#    - If Postman CLI isn't installed, skip collection generation (OpenAPI still succeeds)
# 3) Self-test OpenAPI output (exists + non-empty)

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

SPEC_DIR="postman/specs"
OPENAPI_FILE="$SPEC_DIR/openapi.yaml"

GENERATED_DIR="postman/collections-generated"
PM_COLLECTION_JSON="$GENERATED_DIR/ERP Core API.collection.json"

mkdir -p "$SPEC_DIR" "$GENERATED_DIR"

NO_OPENAPI=0

usage() {
  cat <<'USAGE'
Usage: scripts/postman-sync.sh [--no-openapi]

Regenerates:
  - postman/specs/openapi.yaml (unless --no-openapi)
  - postman/collections-generated/ERP Core API.collection.json (only if Postman CLI is installed)

Options:
  --no-openapi  Skip drf-spectacular generation and use the existing openapi.yaml

Exit codes:
  - 0 success (including when collection generation is skipped because Postman CLI is missing)
  - 1 failure generating or validating OpenAPI
  - 2 invalid arguments
USAGE
}

for arg in "$@"; do
  case "$arg" in
    --no-openapi)
      NO_OPENAPI=1
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "[postman-sync] ERROR: Unknown argument: $arg" >&2
      usage >&2
      exit 2
      ;;
  esac
done

# Allow caller to override DJANGO_SETTINGS_MODULE, otherwise default to project conventional module.
export DJANGO_SETTINGS_MODULE="${DJANGO_SETTINGS_MODULE:-config.settings.base}"

die() {
  echo "[postman-sync] ERROR: $*" >&2
  exit 1
}

info() {
  echo "[postman-sync] $*"
}

has_cmd() {
  command -v "$1" >/dev/null 2>&1
}

detect_python_runner() {
  # Outputs a command prefix suitable for running `manage.py`:
  #   - Local python executable path
  #   - Or `poetry run python`
  #   - Or `pipenv run python`
  #   - Or `docker compose exec ... python`
  if [[ -x "$ROOT_DIR/.venv/bin/python" ]]; then
    echo "$ROOT_DIR/.venv/bin/python"
    return 0
  fi
  if [[ -x "$ROOT_DIR/venv/bin/python" ]]; then
    echo "$ROOT_DIR/venv/bin/python"
    return 0
  fi

  if [[ -f "$ROOT_DIR/poetry.lock" || -f "$ROOT_DIR/pyproject.toml" ]] && has_cmd poetry; then
    echo "poetry run python"
    return 0
  fi

  if [[ -f "$ROOT_DIR/Pipfile" || -f "$ROOT_DIR/Pipfile.lock" ]] && has_cmd pipenv; then
    echo "pipenv run python"
    return 0
  fi

  if has_cmd python3; then
    echo "python3"
    return 0
  fi
  if has_cmd python; then
    echo "python"
    return 0
  fi

  if has_cmd docker && (has_cmd docker-compose || (has_cmd docker && docker compose version >/dev/null 2>&1)); then
    if docker compose -f "$ROOT_DIR/docker-compose.yml" ps --services >/dev/null 2>&1; then
      if docker compose -f "$ROOT_DIR/docker-compose.yml" ps web >/dev/null 2>&1; then
        # Prefer running inside the web container if it's up.
        echo "docker compose -f $ROOT_DIR/docker-compose.yml exec -T web python"
        return 0
      fi
    fi
  fi

  return 1
}

python_runner="$(detect_python_runner || true)"

if [[ "$NO_OPENAPI" == "0" ]]; then
  info "Generating OpenAPI schema -> $OPENAPI_FILE"

  # Only run if manage.py exists.
  [[ -f "$ROOT_DIR/manage.py" ]] || die "manage.py not found at repo root ($ROOT_DIR)."

  [[ -n "$python_runner" ]] || die "Unable to find a Python runner. Tried: .venv/venv, poetry, pipenv, python3/python, docker compose." 

  # Generate the OpenAPI file (idempotent overwrite).
  # shellcheck disable=SC2086
  $python_runner manage.py spectacular --file "$OPENAPI_FILE" >/dev/null
else
  info "--no-openapi specified; using existing $OPENAPI_FILE"
fi

# Basic OpenAPI self-test (exists + non-empty)
if [[ ! -s "$OPENAPI_FILE" ]]; then
  die "OpenAPI file missing or empty: $OPENAPI_FILE (re-run without --no-openapi, or check your spectacular setup)"
fi

# Generate Postman collection JSON using Postman CLI (if installed).
if has_cmd postman; then
  info "Postman CLI detected. Generating collection JSON -> $PM_COLLECTION_JSON"
  # NOTE: this produces a portable Collection JSON artifact for import/CI usage.
  if ! postman api import --file "$OPENAPI_FILE" --format openapi --output "$PM_COLLECTION_JSON" >/dev/null 2>&1; then
    echo "[postman-sync] WARNING: postman api import failed; skipping collection generation." >&2
    exit 0
  fi

  info "OK: OpenAPI generated + collection generated."
else
  info "Postman CLI not found; skipping collection generation. OpenAPI generated at: $OPENAPI_FILE"
  exit 0
fi