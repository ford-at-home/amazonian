#!/usr/bin/env bash
# install.sh — Deploy the Amazonian skills suite onto a repo.
#
# Copies the suite's skills into the chosen scope (project or personal),
# scaffolds a governance.yaml manifest stub if one does not already exist,
# and reports whether superpowers was detected. Idempotent: re-running
# with no flags on an already-deployed repo is a no-op.
#
# See docs/rfcs/RFC-001-deployment-and-orchestration.md §8 for the design.

set -euo pipefail

# ---------------------------------------------------------------------------
# Locate the suite root (where this script lives) and load helper libraries.
# ---------------------------------------------------------------------------
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SUITE_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
LIB_DIR="$SCRIPT_DIR/lib"
TEMPLATE_DIR="$SCRIPT_DIR/templates"

# shellcheck source=lib/detect-plugins.sh
source "$LIB_DIR/detect-plugins.sh"
# shellcheck source=lib/scaffold-manifest.sh
source "$LIB_DIR/scaffold-manifest.sh"

# ---------------------------------------------------------------------------
# Defaults and argument parsing.
# ---------------------------------------------------------------------------
SCOPE="personal"
MANIFEST_PATH=""
REIMPORT="false"
TARGET_REPO="$(pwd)"

usage() {
    cat <<EOF
Usage: install.sh [OPTIONS]

OPTIONS:
  --scope SCOPE              project | personal   (default: personal)
  --manifest-path PATH       Where governance.yaml lives  (default: <repo-root>/governance.yaml)
  --reimport                 Overwrite an existing governance.yaml
  --target-repo PATH         The repo to deploy onto  (default: current working dir)
  -h, --help                 Show this help

EXAMPLES:
  install.sh                                 # personal scope, current dir, no reimport
  install.sh --scope project                 # store skills in ./.cursor/skills/
  install.sh --reimport                      # rebuild a stale manifest

EXIT CODES:
  0  Deployment succeeded (or was a no-op because nothing changed)
  1  Argument error
  2  Target repo is not a git repo
  3  Manifest already exists and --reimport was not passed
  4  Skill copy failed
EOF
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        --scope)            SCOPE="$2"; shift 2 ;;
        --manifest-path)    MANIFEST_PATH="$2"; shift 2 ;;
        --reimport)         REIMPORT="true"; shift ;;
        --target-repo)      TARGET_REPO="$2"; shift 2 ;;
        -h|--help)          usage; exit 0 ;;
        *)                  echo "install.sh: unknown option: $1" >&2; usage >&2; exit 1 ;;
    esac
done

case "$SCOPE" in
    project|personal) ;;
    *) echo "install.sh: --scope must be 'project' or 'personal' (got: $SCOPE)" >&2; exit 1 ;;
esac

if [[ -z "$MANIFEST_PATH" ]]; then
    MANIFEST_PATH="$TARGET_REPO/governance.yaml"
fi

# ---------------------------------------------------------------------------
# Step 1: Validate target is a git repo.
# ---------------------------------------------------------------------------
if ! git -C "$TARGET_REPO" rev-parse --git-dir >/dev/null 2>&1; then
    echo "install.sh: target ($TARGET_REPO) is not a git repository" >&2
    echo "  Initialize it with 'git init' first, then re-run install." >&2
    exit 2
fi

echo "[1/4] Target verified: $TARGET_REPO is a git repo"

# ---------------------------------------------------------------------------
# Step 2: Detect adjacent plugin caches (informational; only superpowers
#         influences the navigator's questioning mode).
# ---------------------------------------------------------------------------
echo "[2/4] Detecting adjacent plugins..."
detect_plugins

# ---------------------------------------------------------------------------
# Step 3: Copy skills/* into the chosen scope.
# ---------------------------------------------------------------------------
case "$SCOPE" in
    personal) SKILLS_DEST="$HOME/.cursor/skills" ;;
    project)  SKILLS_DEST="$TARGET_REPO/.cursor/skills" ;;
esac

mkdir -p "$SKILLS_DEST"

echo "[3/4] Copying skills to $SKILLS_DEST"

# Use rsync for idempotent copy (no-op when destination already matches).
# Falls back to cp -R if rsync is unavailable.
if command -v rsync >/dev/null 2>&1; then
    if ! rsync -a --delete "$SUITE_ROOT/skills/" "$SKILLS_DEST/"; then
        echo "install.sh: skill copy failed" >&2
        exit 4
    fi
else
    rm -rf "$SKILLS_DEST"
    if ! cp -R "$SUITE_ROOT/skills" "$SKILLS_DEST"; then
        echo "install.sh: skill copy failed" >&2
        exit 4
    fi
fi

# Count what we deployed for the operator's confirmation.
SKILL_COUNT="$(find "$SKILLS_DEST" -maxdepth 2 -name SKILL.md | wc -l | tr -d ' ')"
echo "       Deployed $SKILL_COUNT skill(s)."

# ---------------------------------------------------------------------------
# Step 4: Scaffold governance.yaml if it does not already exist (or --reimport).
# ---------------------------------------------------------------------------
echo "[4/4] Scaffolding governance.yaml..."

if [[ -f "$MANIFEST_PATH" && "$REIMPORT" != "true" ]]; then
    echo "       Manifest already exists at $MANIFEST_PATH"
    echo "       Pass --reimport to overwrite, or run 00-repo-state-import to revise field-by-field."
    MANIFEST_CREATED="false"
else
    scaffold_manifest "$TEMPLATE_DIR/governance-template.yaml" "$MANIFEST_PATH"
    MANIFEST_CREATED="true"
fi

# ---------------------------------------------------------------------------
# Final report.
# ---------------------------------------------------------------------------
echo ""
echo "==============================================================="
echo "  Amazonian suite deployed."
echo "==============================================================="
echo "  Scope:           $SCOPE"
echo "  Skills at:       $SKILLS_DEST"
echo "  Skill count:     $SKILL_COUNT"
echo "  Manifest at:     $MANIFEST_PATH"
echo "  Manifest state:  $([ "$MANIFEST_CREATED" = "true" ] && echo "scaffolded (stub)" || echo "preserved (already existed)")"
echo "  Superpowers:     $SUPERPOWERS_STATUS"
echo ""
echo "Next steps:"
if [[ "$MANIFEST_CREATED" == "true" ]]; then
    echo "  1. Run skill 00-repo-state-import to populate the manifest."
    echo "  2. Run skill 14-lifecycle-navigator to see the next required action."
else
    echo "  1. Run skill 14-lifecycle-navigator to see the next required action."
    echo "     (or pass --reimport to rebuild the manifest from scratch)"
fi
echo ""
