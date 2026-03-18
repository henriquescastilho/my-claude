#!/usr/bin/env bash
set -euo pipefail

BASE_DIR="$HOME/.claude-mem-hybrid"
COMPOSE_FILE="$BASE_DIR/docker-compose.yml"

if ! docker info >/dev/null 2>&1; then
  if command -v open >/dev/null 2>&1; then
    open -a Docker >/dev/null 2>&1 || true
    for _ in {1..60}; do
      docker info >/dev/null 2>&1 && break
      sleep 2
    done
  fi
fi

docker info >/dev/null 2>&1 || {
  echo "Docker daemon is not available" >&2
  exit 1
}

docker compose -f "$COMPOSE_FILE" up -d >/dev/null
exec python3 "$BASE_DIR/mcp_memory_server.py"
