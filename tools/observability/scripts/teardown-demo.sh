#!/usr/bin/env bash
# teardown-demo.sh — undo seed-demo.sh.
#
# Removes the demo manifest from the repo root and clears the observability
# DB so the next seed-demo invocation starts fresh. Does NOT stop the server
# (use `make down` for that).

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OBS_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
REPO_ROOT="$(cd "$OBS_DIR/../.." && pwd)"

rm -f "$REPO_ROOT/governance.yaml"
rm -f "$OBS_DIR/data/observability.db" \
      "$OBS_DIR/data/observability.db-shm" \
      "$OBS_DIR/data/observability.db-wal"

echo "demo torn down. Restart the server (make down && make up-bg) so it"
echo "recreates the SQLite schema before the next seed."
