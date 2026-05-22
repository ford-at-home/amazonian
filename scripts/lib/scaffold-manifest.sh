#!/usr/bin/env bash
# scaffold-manifest.sh — Write a governance.yaml stub from the template.
#
# This produces a SCHEMA-INVALID manifest by design: bet.id is empty, which
# fails the kebab-case pattern in governance.schema.json. The stub is meant
# to be populated by 00-repo-state-import, which runs the structured interview
# and writes a valid manifest on completion. install.sh's job is only to put
# the stub in place so the operator knows where to find it.

scaffold_manifest() {
    local template_path="$1"
    local destination="$2"

    if [[ ! -f "$template_path" ]]; then
        echo "scaffold_manifest: template not found at $template_path" >&2
        return 1
    fi

    # Refuse to overwrite without explicit confirmation upstream.
    if [[ -f "$destination" ]]; then
        echo "scaffold_manifest: destination $destination already exists" >&2
        return 1
    fi

    mkdir -p "$(dirname "$destination")"
    cp "$template_path" "$destination"
    echo "       Scaffolded $destination"
    echo "       (this stub is intentionally schema-invalid until 00-repo-state-import runs)"
}
