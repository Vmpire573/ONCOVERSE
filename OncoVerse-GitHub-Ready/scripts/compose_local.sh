#!/usr/bin/env bash
set -euo pipefail

if command -v docker >/dev/null 2>&1; then
  DOCKER_BIN="$(command -v docker)"
elif [[ -x /Applications/Docker.app/Contents/Resources/bin/docker ]]; then
  DOCKER_BIN=/Applications/Docker.app/Contents/Resources/bin/docker
  export PATH="$(dirname "$DOCKER_BIN"):$PATH"
else
  echo "Docker Desktop is not installed. Install and start it, then retry." >&2
  exit 1
fi

exec "$DOCKER_BIN" "$@"
