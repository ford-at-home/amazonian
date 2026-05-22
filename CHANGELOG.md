# Changelog

All notable changes to the Amazonian suite. Format adapted from [Keep a Changelog](https://keepachangelog.com/en/1.1.0/); the suite is pre-1.0 and does not yet apply strict SemVer.

The current suite version is recorded in [`lifecycle.yaml`](lifecycle.yaml) under `suite.version`.

---

## [Unreleased]

The two RFCs landed in this window are the largest single expansion of the suite to date: from "13 skills that produce artifacts" to "15 skills + a deployment mechanism + a localhost observability stack."

### Added — deployment & orchestration (RFC-001)

- **`schema/governance.schema.json`** — versioned JSON Schema for the manifest. Defines `bet`, `tenets`, `success_metrics`, `live_mechanisms`, `period_goals`, `prior_gradings`, `dissent_log`, `interviews`, `history`, plus the `evidence_tag` enum and the `fact_requires_source` cross-field rule.
  *(commit `e30c687`)*

- **`skills/00-repo-state-import/`** — constructive skill that lifts a brownfield repo's current governance state into a structured `governance.yaml`. Conducts a guided interview; refuses to mark any field `evidence: fact` without a non-null `source`. Informal named risk: `brownfield laundering` — a populated manifest read by downstream skills as if it had passed governance gates when it never did.
  - `SKILL.md`, `interview-questions.yaml`, `examples/example-bootstrap.yaml`
  *(commit `6d06d3d`)*

- **`skills/14-lifecycle-navigator/`** — interrogative skill that reads `governance.yaml`, walks a deterministic state machine, and returns one of `advance` / `upstream_remediation` / `block`. Named failure mode: `phase laundering` — running a downstream skill against `assumption`-tagged inputs and treating its output as authoritative.
  - `SKILL.md`, `state-machine.yaml`, `delegation-contract.md`, `examples/example-navigation.md`
  - Delegates question-driven UX to `superpowers:brainstorming` when that plugin is detected; otherwise handles questioning natively.
  *(commit `1ebedd1`)*

- **`scripts/install.sh`** — idempotent bash installer. Verifies git-repo context, detects target AI client (`.cursor/` vs `.claude/`), copies skills, scaffolds `governance.yaml` from a template, detects the optional `superpowers` plugin, and reports a structured summary. Refuses to overwrite an existing populated manifest.
  - Supporting helpers: `scripts/lib/detect-plugins.sh`, `scripts/lib/scaffold-manifest.sh`, `scripts/templates/governance-template.yaml`
  *(commit `a6cec83`)*

- **`docs/rfcs/RFC-001-deployment-and-orchestration.md`** — 535-line design document recording the schema, the two new skills, the installer, the Superpowers integration strategy, named risks, and the per-rule compliance check.
  *(commit `79c728f`)*

### Added — localhost observability stack (RFC-002)

- **`tools/observability/server/`** — FastAPI + SQLite + WebSocket service that mirrors `governance.yaml` into an append-only snapshot table and ingests skill-emitted events via `POST /api/events`. Refuses non-loopback connections at both the bind layer and the request layer.
  - `app.py`, `models.py`, `db.py`, `watcher.py`, `topology.py`
  - Manifest watcher uses content-hash dedupe to absorb noisy editor save events.
  - Topology endpoint mines `lifecycle.yaml` for the suite's skill DAG (15 nodes, 94 edges, 3 self-loops in the current configuration).
  *(commits `e2e42f9`, `5b9050d`)*

- **`tools/observability/server/static/`** — vanilla-JS / vanilla-CSS frontend with three tabs:
  - **Timeline** — snapshots + events, newest first, WebSocket-driven live updates
  - **Topology** — SVG DAG with columns by lifecycle phase, hover-to-highlight node edges, constructive vs interrogative distinguished by border style
  - **Manifest** — recursive tree inspector with evidence-tag color borders (`fact` green, `inference` blue, `assumption` yellow, `open_question` red)
  - No build step; clones-and-runs.
  *(commits `e2e42f9`, `5b9050d`)*

- **`scripts/lib/emit-event.sh`** — best-effort POST helper that skills can `source`. Silent no-op when `AMAZONIAN_OBSERVABILITY_URL` is unset OR when the URL is set but unreachable (hard 1-second timeout). Verified by direct test: returns 0 in both failure modes with no DB writes.
  *(commit `d11303b`)*

- **`tools/observability/scripts/seed-demo.sh`** — paced replay of the ChangeLens session covering bootstrap → navigator routing → phase-laundering finding → demoted recommendation → operator remediation → evidence-tag flip from `assumption` to `fact`. Produces 2 snapshots + 6 events that demonstrate every UI element.
  - Symmetric `teardown-demo.sh`.
  *(commit `d11303b`)*

- **`docs/rfcs/RFC-002-localhost-observability.md`** — design document recording the architectural tension (API-canonical vs observability-only), the resolution (observability-only; `governance.yaml` remains the single source of truth), the data model, the loopback-enforcement posture, and the deferred-to-v2 items.
  *(commit `d11303b`)*

### Added — documentation

- **`docs/WALKTHROUGH.md`** — 15-minute operator path from `git clone` through a running governance session with optional observability.
  *(this commit)*

- **`CHANGELOG.md`** — this file.
  *(this commit)*

- **`README.md` whiteboard infographics** — two diagrams: the 13-skill lifecycle map (with non-Amazon influences surfaced explicitly), and the composition view showing how the Amazonian governance layer interlocks with external SWE tooling for the deliberately-omitted Build phase.
  *(commits `2e9937f`, `64de8a3`, `ed234b3`)*

### Changed

- **`lifecycle.yaml`** — added the `deploy` phase entry, the `cross_cutting` block, and the skill rows for `repo-state-import` (00) and `lifecycle-navigator` (14). The file had drifted behind `LIFECYCLE.md` in B4; B6 reconciled them.
  *(commit `5b9050d`)*

- **`vocabulary.yaml`** — added enums: `bet_status`, `bet_origin`, `handoff_status`, `routing_decision`, `prefer_superpowers`, `phase_laundering`, `brownfield_laundering`.
  *(commit `e30c687`)*

- **`GLOSSARY.md`** — added definitions for `phase laundering` and `brownfield laundering`; updated the cross-reference table to include `lifecycle-navigator` and to note that constructive skills can carry informal named risks (vs interrogative skills, which carry formal named failure modes).
  *(commit `e30c687`)*

- **`LIFECYCLE.md`** — added the `Deploy` phase (housing `repo-state-import`) and the `Cross-cutting` phase (housing `lifecycle-navigator`).
  *(commit `a6cec83`)*

- **`README.md`** — extended the skill table to include skills 00 and 14; rewrote Quick Start with `install.sh` instructions; added a section pointing at the optional observability stack; updated the repository-layout diagram.
  *(commits `a6cec83`, `d11303b`)*

- **`skills/00-repo-state-import/SKILL.md`**, **`skills/14-lifecycle-navigator/SKILL.md`** — added "Optional observability emission" sections showing how to wire each skill to `emit-event.sh`. Emission is documented as best-effort; skills must complete their work regardless of whether observability is up.
  *(commit `d11303b`)*

### Architectural commitments (unchanged; documented for traceability)

These were established earlier in the suite's lifetime and reaffirmed by both RFCs:

1. **`governance.yaml` is the single source of truth.** Every skill writes there; readers query there; the observability stack mirrors it but never writes to it.
2. **The skill suite must be functional without optional infrastructure.** The observability stack is optional. The `superpowers` plugin is optional. Skills degrade cleanly when either is absent.
3. **Evidence tags on every field.** No populated field may lack one of `{fact, assumption, inference, open_question}`. `fact` requires a non-null `source`.
4. **Named failure modes are first-class.** Interrogative skills declare formal named failure modes (e.g., `founder bias laundering`, `PRFAQ drift`, `phase laundering`). Constructive skills may declare informal named risks (e.g., `brownfield laundering`). Both are documented in [`GLOSSARY.md`](GLOSSARY.md).

---

## Earlier work (selected)

The suite existed before this session at 13 skills (`01` through `13`) plus the supporting documentation infrastructure. Selected milestones:

- `f68ba0a` — `skills/13-portfolio-review/` (cross-bet allocation review).
- `5f0fb4a` — `skills/12-dissent-before-commit/` (execution-time gate with named failure mode `stale dissent reuse`).
- `daa3cfe` — `skills/11-ambitious-goal-grading/` (period-driven, named failure mode `sandbagging laundering`).
- `8e155a4` — codified the named-failure-mode design pattern across the suite; resolved the severity-scale inconsistency between downstream templates.
- `15dbd51` — added `lifecycle.yaml` as the machine-readable companion to `LIFECYCLE.md`.

For the full pre-session history, see `git log` and the per-skill `SKILL.md` files.
