#!/usr/bin/env bash
# Stable stdio entry point for Pi and other MCP clients.
# Resolve paths from this script, not the client's working directory.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
if ! command -v uv >/dev/null 2>&1; then
  printf '%s\n' 'gaggimate-mcp: uv is required; install it and make it available on PATH.' >&2
  exit 127
fi
cd "$ROOT/mcp"
# GaggimateConfig reads .env and resolves local storage from this directory.
# Keep stdout exclusively for the MCP protocol; do not source .env as shell code.
exec uv run --frozen mcp run src/gaggimate_mcp/server.py
