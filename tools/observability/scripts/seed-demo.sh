#!/usr/bin/env bash
# seed-demo.sh — populate the observability UI with a worked example.
#
# Drops the ChangeLens bootstrap manifest into the repo root, then replays
# the sequence a real lifecycle-navigator session would emit: detection of
# the phase-laundering risk on live_mechanisms[wbr-monday], demotion of
# the routing decision, operator acting on the recommendation, and the
# evidence tag flipping from assumption -> fact.
#
# Pause between events so the user watching at http://127.0.0.1:8765/
# sees the timeline fill in incrementally.
#
# Usage:
#   ./seed-demo.sh                  # 0.8s pacing
#   ./seed-demo.sh --fast           # no pacing
#   ./seed-demo.sh --pace 2.0       # custom pacing in seconds

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
MANIFEST_SRC="$REPO_ROOT/skills/00-repo-state-import/examples/example-bootstrap.yaml"
MANIFEST_DEST="$REPO_ROOT/governance.yaml"
URL="${AMAZONIAN_OBSERVABILITY_URL:-http://127.0.0.1:8765}"
PACE="0.8"

while [[ $# -gt 0 ]]; do
    case "$1" in
        --fast) PACE="0"; shift ;;
        --pace) PACE="$2"; shift 2 ;;
        *) echo "seed-demo: unknown arg: $1" >&2; exit 1 ;;
    esac
done

export AMAZONIAN_OBSERVABILITY_URL="$URL"
export AMAZONIAN_BET_ID="changelens"
export AMAZONIAN_OPERATOR_HANDLE="demo"

# shellcheck source=../../../scripts/lib/emit-event.sh
source "$REPO_ROOT/scripts/lib/emit-event.sh"

if ! curl -fsS -m 1 "$URL/healthz" >/dev/null 2>&1; then
    echo "seed-demo: observability not reachable at $URL"
    echo "  start it first with: cd tools/observability && make up-bg"
    exit 1
fi

pause() { [[ "$PACE" != "0" ]] && sleep "$PACE" || true; }

echo "[1/8] dropping ChangeLens manifest into $MANIFEST_DEST"
cp "$MANIFEST_SRC" "$MANIFEST_DEST"
pause

echo "[2/8] emit: 00-repo-state-import end (manifest bootstrapped)"
echo '{"declined_groups":["dissent_log"],"bootstrap_mode":"partial"}' \
    | amazonian_emit_event 00-repo-state-import end "" "" ""
pause

echo "[3/8] emit: 14-lifecycle-navigator start"
echo '{"session_intent":null}' \
    | amazonian_emit_event 14-lifecycle-navigator start
pause

echo "[4/8] emit: 14-lifecycle-navigator progress — position matched: operating-wbr-due"
echo '{"matched_position":"operating-wbr-due","upstream_fields":["live_mechanisms","success_metrics"]}' \
    | amazonian_emit_event 14-lifecycle-navigator progress
pause

echo "[5/8] emit: 14-lifecycle-navigator progress — phase-laundering check fired"
echo '{"phase_laundering_finding":"live_mechanisms[wbr-monday] evidence=assumption; mechanism has no written spec"}' \
    | amazonian_emit_event 14-lifecycle-navigator progress "live_mechanisms[wbr-monday]" "" ""
pause

echo "[6/8] emit: 14-lifecycle-navigator end — routing demoted"
echo '{"routing_decision":"upstream_remediation","recommended_skill":"04-mechanism-designer","rationale":"WBR mechanism is evidence=assumption; design it before inspecting against it"}' \
    | amazonian_emit_event 14-lifecycle-navigator end
pause

echo "[7/8] operator acts: 04-mechanism-designer end — WBR mechanism specced"
echo '{"spec_path":"docs/mechanisms/wbr-monday.md"}' \
    | amazonian_emit_event 04-mechanism-designer end "live_mechanisms[wbr-monday].spec_path" "" "fact"
pause

echo "[8/8] manifest edit: upgrade live_mechanisms[wbr-monday].evidence assumption -> fact"
python3 - "$MANIFEST_DEST" <<'PYEOF'
import sys, yaml
path = sys.argv[1]
with open(path) as f:
    m = yaml.safe_load(f)
for mech in m.get("live_mechanisms", []):
    if mech.get("id") == "wbr-monday":
        mech["evidence"] = "fact"
        mech["spec_path"] = "docs/mechanisms/wbr-monday.md"
        mech["inferred_from"] = None
with open(path, "w") as f:
    yaml.safe_dump(m, f, sort_keys=False)
PYEOF

echo ""
echo "Demo seeded. Open http://127.0.0.1:8765/ — you should see:"
echo "  - Timeline tab:  2 snapshots + 6 events"
echo "  - Topology tab:  the suite's full DAG (hover a node to highlight)"
echo "  - Manifest tab:  live_mechanisms[wbr-monday] now green (evidence=fact)"
