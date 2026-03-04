#!/usr/bin/env bash
set -euo pipefail

# Sync OpenAPI -> Postman artifacts (spec-first)
# - (Optional) Generates OpenAPI spec via drf-spectacular management command
# - Writes to postman/specs/openapi.yaml
# - Generates a deterministic Postman Collection JSON artifact (local-only by default):
#     postman/collections-generated/ERP Core API (Generated).collection.json
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
PM_COLLECTION_JSON="$GENERATED_DIR/ERP Core API (Generated).collection.json"

mkdir -p "$SPEC_DIR" "$GENERATED_DIR"

NO_OPENAPI=0

usage() {
  cat <<'USAGE'
Usage: scripts/postman-sync.sh [--no-openapi]

Regenerates:
  - postman/specs/openapi.yaml (unless --no-openapi)
  - postman/collections-generated/ERP Core API (Generated).collection.json (only if Postman CLI is installed)

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

detect_compose_cmd() {
  # Prefer Docker Compose v2 (`docker compose`). Fall back to legacy `docker-compose`.
  if has_cmd docker && docker compose version >/dev/null 2>&1; then
    echo "docker compose"
    return 0
  fi
  if has_cmd docker-compose; then
    echo "docker-compose"
    return 0
  fi
  return 1
}

compose_cmd="$(detect_compose_cmd || true)"
compose_file="$ROOT_DIR/docker-compose.yml"
compose_project_args=()
if [[ -n "$compose_cmd" && -f "$compose_file" ]]; then
  compose_project_args=(-f "$compose_file")
fi

detect_python_runner() {
  # Outputs a command prefix suitable for running `manage.py`:
  #   - Local python executable path
  #   - Or `poetry run python`
  #   - Or `pipenv run python`
  #   - Or `python3`/`python`
  #
  # NOTE: We intentionally do NOT auto-fall back to Docker here; OpenAPI generation is handled
  # by a docker-compose path (more reliable when dev runs via docker compose).
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

  return 1
}

detect_django_service_name() {
  # Best-effort: prefer common Django service names.
  # In this repo's docker-compose.yml the service is `web`.
  [[ -n "$compose_cmd" ]] || return 1

  local services
  # `config --services` does not require running containers and works in CI.
  services="$($compose_cmd "${compose_project_args[@]}" config --services 2>/dev/null || true)"
  if [[ -z "$services" ]]; then
    services="$($compose_cmd "${compose_project_args[@]}" ps --services 2>/dev/null || true)"
  fi
  [[ -n "$services" ]] || return 1

  for candidate in web api app backend django; do
    if echo "$services" | tr ' ' '\n' | grep -qx "$candidate"; then
      echo "$candidate"
      return 0
    fi
  done

  # Fallback: if there's exactly one service built from the repo root, user likely meant that.
  # (We keep it simple and just fall back to `web` if present; otherwise error.)
  return 1
}

is_compose_service_running() {
  local service="$1"
  [[ -n "$compose_cmd" ]] || return 1

  # `ps -q` returns container id(s) for running services.
  local cid
  cid="$($compose_cmd "${compose_project_args[@]}" ps -q "$service" 2>/dev/null || true)"
  [[ -n "$cid" ]]
}

generate_openapi_via_docker_compose() {
  local service="$1"

  [[ -n "$compose_cmd" ]] || return 1
  [[ -f "$compose_file" ]] || return 1

  if ! is_compose_service_running "$service"; then
    echo "[postman-sync] docker compose service '$service' is not running." >&2
    echo "[postman-sync] Start it with: $compose_cmd ${compose_project_args[*]} up -d $service" >&2
    echo "[postman-sync] Will try local python fallback for OpenAPI generation." >&2
    return 2
  fi

  info "Generating OpenAPI via docker compose -> $OPENAPI_FILE"
  # Because the repo is volume-mounted into the container (.:/app), writing to /app/postman/... writes to host.
  $compose_cmd "${compose_project_args[@]}" exec -T "$service" python manage.py spectacular --file "$OPENAPI_FILE" >/dev/null
}

python_runner="$(detect_python_runner || true)"

generate_openapi_locally() {
  [[ -n "$python_runner" ]] || return 1
  info "Generating OpenAPI schema locally -> $OPENAPI_FILE"
  # Generate the OpenAPI file (idempotent overwrite).
  # shellcheck disable=SC2086
  $python_runner manage.py spectacular --file "$OPENAPI_FILE" >/dev/null
}

if [[ "$NO_OPENAPI" == "0" ]]; then
  # Only run if manage.py exists.
  [[ -f "$ROOT_DIR/manage.py" ]] || die "manage.py not found at repo root ($ROOT_DIR)."

  # Prefer docker-compose based generation when available (more reliable when dev runs via docker compose).
  if [[ -n "$compose_cmd" && -f "$compose_file" ]]; then
    django_service="$(detect_django_service_name || true)"
    if [[ -z "$django_service" ]]; then
      echo "[postman-sync] docker compose detected but couldn't determine Django service name." >&2
      echo "[postman-sync] Expected one of: web, api, app, backend, django" >&2
      if [[ -n "$python_runner" ]]; then
        generate_openapi_locally
      else
        echo "[postman-sync] Skipping OpenAPI generation (no local python fallback found)." >&2
      fi
    else
      docker_gen_rc=0
      generate_openapi_via_docker_compose "$django_service" || docker_gen_rc=$?
      if [[ "$docker_gen_rc" -ne 0 ]]; then
        if [[ "$docker_gen_rc" -eq 2 ]] && [[ -n "$python_runner" ]]; then
          generate_openapi_locally
        elif [[ "$docker_gen_rc" -eq 2 ]]; then
          echo "[postman-sync] OpenAPI generation skipped: docker service not running and no local python runner found." >&2
          echo "[postman-sync] Leaving existing $OPENAPI_FILE as-is." >&2
        else
          die "Docker compose OpenAPI generation failed."
        fi
      fi
    fi
  elif [[ -n "$python_runner" ]]; then
    generate_openapi_locally
  else
    echo "[postman-sync] OpenAPI generation skipped: docker compose not available and no local python runner found." >&2
    echo "[postman-sync] To enable generation:" >&2
    echo "[postman-sync]  - Install Docker Desktop (or docker engine) and ensure '$compose_file' exists; then run: docker compose up -d web" >&2
    echo "[postman-sync]  - OR create a local venv and install dependencies." >&2
    echo "[postman-sync] Leaving existing $OPENAPI_FILE as-is." >&2
  fi
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

  # Option B: Auto-push to Postman workspace via Postman API (if env is configured)
  if [[ -n "${POSTMAN_API_KEY:-}" && ( -n "${POSTMAN_COLLECTION_UID:-}" || -n "${POSTMAN_WORKSPACE_ID:-}" ) ]]; then
    export POSTMAN_COLLECTION_JSON="$PM_COLLECTION_JSON"
    if "$ROOT_DIR/scripts/postman-push.sh"; then
      info "Postman workspace updated."
    else
      echo "[postman-sync] WARNING: postman-push failed; collection file was still generated locally." >&2
    fi
  fi
else
  info "Postman CLI not found; skipping collection generation. OpenAPI generated at: $OPENAPI_FILE"
  exit 0
fi
