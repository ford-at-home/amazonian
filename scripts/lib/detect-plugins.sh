#!/usr/bin/env bash
# detect-plugins.sh — Look for adjacent plugin caches and report what is present.
#
# Only `superpowers` materially affects the suite's runtime behavior (the
# navigator delegates question-driven UX to superpowers:brainstorming when
# present; falls back to a native loop when not). Other plugins are reported
# informationally to help operators understand their environment.
#
# Sets the following shell variables on completion:
#   SUPERPOWERS_STATUS  one of: "detected", "not detected", "unverified"
#   SUPERPOWERS_PATH    path to the superpowers plugin cache, or empty

# Plugin cache roots checked, in priority order. Different platforms install
# plugins to different locations; treat detection as best-effort.
PLUGIN_CACHE_ROOTS=(
    "$HOME/.cursor/plugins/cache"
    "$HOME/.cursor/skills-cursor"
    "$HOME/.claude/plugins"
)

# Skill suites we look for. Only superpowers is load-bearing for navigator
# behavior; the others are informational.
RELEVANT_PLUGINS=(
    "superpowers"
    "cli-for-agents"
    "parallel"
    "firecrawl"
    "context7"
)

# Search recursively (but bounded) under each cache root for a directory whose
# name matches the plugin. Returns the first match.
find_plugin() {
    local plugin_name="$1"
    local root
    for root in "${PLUGIN_CACHE_ROOTS[@]}"; do
        [[ -d "$root" ]] || continue
        local found
        found="$(find "$root" -maxdepth 4 -type d -name "$plugin_name" 2>/dev/null | head -n 1)"
        if [[ -n "$found" ]]; then
            echo "$found"
            return 0
        fi
    done
    return 1
}

detect_plugins() {
    SUPERPOWERS_STATUS="not detected"
    SUPERPOWERS_PATH=""

    local plugin path
    for plugin in "${RELEVANT_PLUGINS[@]}"; do
        if path="$(find_plugin "$plugin")"; then
            case "$plugin" in
                superpowers)
                    # Confirm brainstorming skill is present — superpowers
                    # without brainstorming is not load-bearing for us.
                    if find "$path" -maxdepth 5 -name "brainstorming" -type d 2>/dev/null | grep -q .; then
                        SUPERPOWERS_STATUS="detected"
                        SUPERPOWERS_PATH="$path"
                        echo "       superpowers: detected (brainstorming present)"
                    else
                        SUPERPOWERS_STATUS="unverified"
                        echo "       superpowers: [Unverified] cache found but brainstorming skill not located"
                    fi
                    ;;
                *)
                    echo "       $plugin: detected (informational)"
                    ;;
            esac
        fi
    done

    if [[ "$SUPERPOWERS_STATUS" == "not detected" ]]; then
        echo "       superpowers: not detected (navigator will use native questioning loop)"
    fi
}
