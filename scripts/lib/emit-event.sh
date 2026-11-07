#!/usr/bin/env bash
# emit-event.sh — best-effort observability event emitter.
#
# Sourced (not executed) by skills that want to record events to the
# optional localhost observability stack at tools/observability/.
#
# Contract:
#   - If AMAZONIAN_OBSERVABILITY_URL is unset, the function is a silent no-op.
#   - If the URL is set but unreachable, the function fails silently
#     (1-second timeout, no error propagation).
#   - The skill suite must work regardless of whether this function runs.
#     Skills write canonical state to governance.yaml; emitted events are
#     observability sugar, not source of truth. See
#     tools/observability/README.md#architectural-commitments.
#
# Usage:
#   source scripts/lib/emit-event.sh
#   amazonian_emit_event <skill_id> <phase> [manifest_field] [evidence_before] [evidence_after]
#
# Optional environment:
#   AMAZONIAN_OBSERVABILITY_URL   e.g., http://127.0.0.1:8765
#   AMAZONIAN_BET_ID              attached as bet_id
#   AMAZONIAN_OPERATOR_HANDLE     attached as operator_handle
#
# Optional stdin: a JSON object included as the event's `payload`. Pipe in
# with `echo '{"key":"value"}' | amazonian_emit_event ...`.

amazonian_emit_event() {
    [[ -z "${AMAZONIAN_OBSERVABILITY_URL:-}" ]] && return 0
    [[ "$#" -ge 2 ]] || return 0

    local payload_stdin=""
    if [[ ! -t 0 ]] && [[ -p /dev/stdin || -f /dev/stdin ]]; then
        payload_stdin=$(cat)
    fi

    AMAZONIAN_PAYLOAD_STDIN="$payload_stdin" python3 - "$@" <<'PYEOF' 2>/dev/null || return 0
import json
import os
import sys
import urllib.error
import urllib.request

skill = sys.argv[1]
phase = sys.argv[2]
field   = sys.argv[3] if len(sys.argv) > 3 else None
before  = sys.argv[4] if len(sys.argv) > 4 else None
after   = sys.argv[5] if len(sys.argv) > 5 else None

payload_raw = os.environ.get("AMAZONIAN_PAYLOAD_STDIN", "").strip()
try:
    payload = json.loads(payload_raw) if payload_raw else {}
except json.JSONDecodeError:
    payload = {"_raw_stdin": payload_raw}

body = {
    "skill_id": skill,
    "phase": phase,
    "manifest_field": field or None,
    "evidence_before": before or None,
    "evidence_after": after or None,
    "bet_id": os.environ.get("AMAZONIAN_BET_ID") or None,
    "operator_handle": os.environ.get("AMAZONIAN_OPERATOR_HANDLE") or None,
    "payload": payload,
}
body = {k: v for k, v in body.items() if v not in (None, "")}

url = os.environ["AMAZONIAN_OBSERVABILITY_URL"].rstrip("/") + "/api/events"
req = urllib.request.Request(
    url,
    data=json.dumps(body).encode("utf-8"),
    headers={"Content-Type": "application/json"},
    method="POST",
)
try:
    urllib.request.urlopen(req, timeout=1.0)
except (urllib.error.URLError, TimeoutError, OSError):
    sys.exit(0)
PYEOF
}
