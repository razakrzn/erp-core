#!/usr/bin/env bash
# Push the generated Postman collection JSON to your Postman workspace via the Postman API.
# Use after postman-sync.sh (or whenever postman/collection.json exists).
#
# Required env:
#   POSTMAN_API_KEY  - Postman API key (X-API-Key). Generate at: Postman → Settings → API Keys.
#
# For update (replace existing collection):
#   POSTMAN_COLLECTION_UID  - UID of the collection to replace (from collection info in Postman, or API).
#
# For create (new collection in workspace):
#   POSTMAN_WORKSPACE_ID   - Workspace ID (from postman/ or workspace URL in Postman).
#
# Optional:
#   POSTMAN_API_BASE_URL   - Default https://api.getpostman.com (use https://api.eu.getpostman.com for EU).
#   POSTMAN_COLLECTION_JSON - Path to collection JSON; default: postman/collection.json
#
# Usage:
#   POSTMAN_API_KEY=xxx POSTMAN_COLLECTION_UID=yyy bash scripts/postman-push.sh
#   POSTMAN_API_KEY=xxx POSTMAN_WORKSPACE_ID=zzz bash scripts/postman-push.sh
#   bash scripts/postman-push.sh   # uses env from .env or shell
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

COLLECTION_JSON="${POSTMAN_COLLECTION_JSON:-postman/collection.json}"
API_BASE="${POSTMAN_API_BASE_URL:-https://api.getpostman.com}"
API_KEY="${POSTMAN_API_KEY:-}"

die() {
  echo "[postman-push] ERROR: $*" >&2
  exit 1
}

info() {
  echo "[postman-push] $*"
}

if [[ -z "$API_KEY" ]]; then
  die "POSTMAN_API_KEY is not set. Generate one at Postman → Settings → API Keys."
fi

if [[ ! -f "$COLLECTION_JSON" ]]; then
  die "Collection file not found: $COLLECTION_JSON. Run scripts/postman-sync.sh first."
fi

# Postman API expects body: { "collection": <collection object> }
# We have the raw collection JSON; wrap it.
if ! command -v jq >/dev/null 2>&1; then
  die "jq is required to wrap the collection JSON. Install jq or set POSTMAN_COLLECTION_UID and use a pre-wrapped payload."
fi

BODY_FILE="$(mktemp)"
cleanup() {
  rm -f "$BODY_FILE"
}
trap cleanup EXIT

if ! jq -n --slurpfile c "$COLLECTION_JSON" '{collection: $c[0]}' > "$BODY_FILE"; then
  die "jq failed to build request body from $COLLECTION_JSON"
fi

if [[ ! -s "$BODY_FILE" ]]; then
  die "Generated request body is empty: $BODY_FILE"
fi

if [[ -z "${POSTMAN_COLLECTION_UID:-}" && -n "${POSTMAN_WORKSPACE_ID:-}" ]]; then
  COLL_NAME=$(jq -r '.info.name' "$COLLECTION_JSON")
  info "POSTMAN_COLLECTION_UID not provided. Searching workspace $POSTMAN_WORKSPACE_ID for '$COLL_NAME'..."
  WS_DATA=$(curl -s -H "X-API-Key: $API_KEY" "$API_BASE/workspaces/$POSTMAN_WORKSPACE_ID")
  FOUND_UID=$(echo "$WS_DATA" | jq -r --arg n "$COLL_NAME" '.workspace.collections[]? | select(.name == $n) | .uid' | head -n1)
  
  if [[ -n "$FOUND_UID" ]]; then
    info "Found existing collection '$COLL_NAME' with UID: $FOUND_UID. Will update it instead of creating duplicates."
    POSTMAN_COLLECTION_UID="$FOUND_UID"
  fi
fi

if [[ -n "${POSTMAN_COLLECTION_UID:-}" ]]; then
  # Update existing collection
  info "Updating collection (UID: $POSTMAN_COLLECTION_UID)..."
  RESP=$(curl -s -w "\n%{http_code}" -X PUT \
    -H "X-API-Key: $API_KEY" \
    -H "Content-Type: application/json" \
    --data-binary "@$BODY_FILE" \
    "$API_BASE/collections/$POSTMAN_COLLECTION_UID")
  HTTP_CODE=$(echo "$RESP" | tail -n1)
  BODY_RESP=$(echo "$RESP" | sed '$d')
  if [[ "$HTTP_CODE" -ge 200 && "$HTTP_CODE" -lt 300 ]]; then
    info "Collection updated successfully."
    echo "$BODY_RESP" | jq -r '.collection | "  name: \(.name), uid: \(.uid)"' 2>/dev/null || true
  else
    echo "$BODY_RESP" | jq -r '.error.message // .' 2>/dev/null || echo "$BODY_RESP"
    die "Update failed (HTTP $HTTP_CODE)."
  fi
elif [[ -n "${POSTMAN_WORKSPACE_ID:-}" ]]; then
  # Create new collection in workspace
  info "Creating collection in workspace ($POSTMAN_WORKSPACE_ID)..."
  RESP=$(curl -s -w "\n%{http_code}" -X POST \
    -H "X-API-Key: $API_KEY" \
    -H "Content-Type: application/json" \
    --data-binary "@$BODY_FILE" \
    "$API_BASE/collections?workspace=$POSTMAN_WORKSPACE_ID")
  HTTP_CODE=$(echo "$RESP" | tail -n1)
  BODY_RESP=$(echo "$RESP" | sed '$d')
  if [[ "$HTTP_CODE" -ge 200 && "$HTTP_CODE" -lt 300 ]]; then
    info "Collection created successfully."
    echo "$BODY_RESP" | jq -r '.collection | "  name: \(.name), uid: \(.uid)"' 2>/dev/null || true
    echo "[postman-push] To update this collection next time, set POSTMAN_COLLECTION_UID to the uid above."
  else
    echo "$BODY_RESP" | jq -r '.error.message // .' 2>/dev/null || echo "$BODY_RESP"
    die "Create failed (HTTP $HTTP_CODE)."
  fi
else
  die "Set either POSTMAN_COLLECTION_UID (to update) or POSTMAN_WORKSPACE_ID (to create). See .postman/resources.yaml for workspace id."
fi
