"""Topology builder.

Reads lifecycle.yaml (the suite's machine-readable skill graph) and produces
a (nodes, edges) DAG description for the frontend to render.

Why lifecycle.yaml is the only source we read:
  - It is the canonical declared form: per-skill `consumes_from` and
    `feeds_into` lists, primary phase, category.
  - Pulling from individual SKILL.md `## Handoffs` tables would be richer
    but each table is free-form markdown — parsing it reliably is a
    research project. The suite's design pattern explicitly designates
    lifecycle.yaml as the skill-level summary and SKILL.md as the
    field-level detail; this layer wants the summary.

Edges are directional: A → B means "A produces something B reads."
We synthesize them from the union of A's `feeds_into` and B's
`consumes_from` — this is intentionally redundant; the data should agree,
and disagreement is itself a finding the UI should surface.
"""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
LIFECYCLE_PATH = REPO_ROOT / "lifecycle.yaml"

# Phase ordering for the frontend's column layout. Build is intentionally
# present so the empty column reads as a deliberate omission, not a missing
# value. `cross_cutting` sits as its own column to the right of `learn`.
PHASE_ORDER = [
    "deploy",
    "discover",
    "define",
    "design",
    "build",
    "launch",
    "operate",
    "learn",
    "cross_cutting",
]


@lru_cache(maxsize=1)
def _load_lifecycle() -> dict[str, Any]:
    return yaml.safe_load(LIFECYCLE_PATH.read_text())


def build_topology() -> dict[str, Any]:
    data = _load_lifecycle()
    skills_by_name = {s["name"]: s for s in data.get("skills", [])}

    nodes = [_skill_to_node(s) for s in data.get("skills", [])]

    edges: dict[tuple[str, str], dict[str, Any]] = {}
    for skill in data.get("skills", []):
        src = skill["name"]
        for target in skill.get("feeds_into", []) or []:
            target_clean = _strip_placeholder(target)
            if target_clean is None or target_clean not in skills_by_name:
                continue
            key = (src, target_clean)
            edges.setdefault(key, {"source": src, "target": target_clean, "via": []})
            edges[key]["via"].append("declared by source.feeds_into")

        for source in skill.get("consumes_from", []) or []:
            source_clean = _strip_placeholder(source)
            if source_clean is None or source_clean not in skills_by_name:
                continue
            key = (source_clean, src)
            edges.setdefault(key, {"source": source_clean, "target": src, "via": []})
            edges[key]["via"].append("declared by target.consumes_from")

    edge_list = [
        {
            "source": e["source"],
            "target": e["target"],
            "self_loop": e["source"] == e["target"],
            "declared_by": sorted(set(e["via"])),
        }
        for e in edges.values()
    ]

    return {
        "nodes": nodes,
        "edges": edge_list,
        "phase_order": PHASE_ORDER,
        "stats": {
            "node_count": len(nodes),
            "edge_count": len(edge_list),
            "self_loop_count": sum(1 for e in edge_list if e["self_loop"]),
        },
    }


def _skill_to_node(skill: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": skill["name"],
        "number": skill.get("number"),
        "category": skill.get("category"),
        "phase": skill.get("primary_phase", "cross_cutting"),
        "secondary_phases": skill.get("secondary_phases", []),
        "skill_md": skill.get("skill_md"),
        "named_failure_mode": skill.get("named_failure_mode"),
        "named_risk_informal": skill.get("named_risk_informal"),
    }


def _strip_placeholder(name: str) -> str | None:
    """Reject angle-bracket placeholders like '<originating authoring skill>'
    that lifecycle.yaml uses to mean 'whichever skill called me'."""
    if name.startswith("<") and name.endswith(">"):
        return None
    return name
