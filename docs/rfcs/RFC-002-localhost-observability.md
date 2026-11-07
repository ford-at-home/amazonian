# RFC-002 — Localhost Observability Stack

**Status:** Implemented in commits `e2e42f9` (B5), `5b9050d` (B6), and this commit's B7. Approved by operator on 2026-05-22.

**Relates to:** [RFC-001 — Deployment and Orchestration](RFC-001-deployment-and-orchestration.md).

## Summary

A localhost-only stack that mirrors `governance.yaml` into SQLite, ingests skill-emitted events via HTTP, and renders both in a browser in real time. The stack is **strictly optional**: the Amazonian skill suite remains fully functional without it. Three components:

1. **`tools/observability/server/`** — FastAPI app with SQLite, an async manifest file watcher (`watchfiles`), WebSocket push, and a vanilla-JS frontend with three tabs (Timeline, Topology, Manifest).
2. **`scripts/lib/emit-event.sh`** — best-effort POST helper. Silent no-op when `AMAZONIAN_OBSERVABILITY_URL` is unset or the server is unreachable.
3. **`tools/observability/scripts/seed-demo.sh`** — replays a worked ChangeLens session so a new operator can watch the suite's value pattern unfold.

## Motivation

The operator asked: *"could we launch a test where we see how inputs become outputs that feed into other inputs in a structured way? like a temporal workflow."*

Two latent asks underneath:

1. **Make the data flow visible.** The suite has a precise data dependency graph (each skill's `consumes_from` / `feeds_into` in `lifecycle.yaml`), but until B6 there was no view of it. The topology tab exists to make the DAG legible at a glance.
2. **Make the agent's reasoning visible in real time.** Watching a Claude session emit events as it walks through `14-lifecycle-navigator`'s phase-laundering check is materially more legible than reading transcripts after the fact. The timeline tab exists to surface that progression.

## The architectural tension the RFC resolves

The operator's framing — *"agents are instructed to write their results to and read from for starter context"* — could imply two very different architectures:

| Reading | Implication | Verdict |
|---|---|---|
| Strict: API is canonical | Skills POST results to the API; SQLite is source of truth; `governance.yaml` becomes a generated export | **Rejected.** Undoes the source-of-truth contract from RFC-001 §3.2. Skills become coupled to a running service. The "you can `cat governance.yaml` to know the truth" property goes away. |
| Loose: API is observability | Skills write canonical state to `governance.yaml` (unchanged). They *also* emit structured events to the API for observability. API persists events + mirrors manifest snapshots into SQLite. Frontend renders both. | **Adopted.** |

The adopted reading preserves RFC-001's commitment that `governance.yaml` is the single source of truth, and treats this stack as a query/observability projection plus an append-only event log. The DB is regeneratable from the manifest's `history[]` plus the events captured during emission; nothing in it is load-bearing for the suite's correctness.

## Goals

1. Render the suite's data flow as a DAG, sourced from `lifecycle.yaml`.
2. Render `governance.yaml` snapshots with evidence-tag color coding.
3. Stream events emitted by skills in real time over WebSocket.
4. Be runnable with a single `make up-bg` after `git clone` — no Docker, no Kubernetes, no remote services.
5. Be strictly optional. The skill suite must not regress in any way when this stack is not running.
6. Refuse non-loopback connections at both the bind layer and the request layer.

## Non-goals (v1)

- Multi-bet aggregation. A single observability instance watches a single manifest.
- Authentication. The stack is localhost-only; auth is for the next deployment topology, not this one.
- Historical playback / scrubber UI. The data is in SQLite; you can query it directly until a scrubber proves necessary.
- Production deployment. This is dev/observability, not a runtime dependency.
- Replacing `superpowers:brainstorming` as the questioning UX. The navigator already handles that via the delegation contract in RFC-001 §6.2.

## Architecture

```text
┌────────────────────────────────────────────────────────────────────────┐
│  Repo root                                                             │
│                                                                        │
│    governance.yaml  ◄────────────────────────┐                         │
│       ▲                                      │                         │
│       │ canonical writes (skills, operator)  │ file watcher            │
│                                              │                         │
│    skills/00-repo-state-import/SKILL.md      │                         │
│    skills/14-lifecycle-navigator/SKILL.md ───┘                         │
│       │                                                                │
│       │ POST events (optional, best-effort)                            │
│       ▼                                                                │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │  tools/observability/                                            │  │
│  │                                                                  │  │
│  │    server/app.py        FastAPI; lifespan-managed watcher        │  │
│  │    server/watcher.py    watchfiles-based async mirror            │  │
│  │    server/db.py         SQLite schema (raw sql, no ORM)          │  │
│  │    server/topology.py   lifecycle.yaml → {nodes, edges}          │  │
│  │    server/static/*      vanilla HTML/CSS/JS frontend             │  │
│  │                                                                  │  │
│  │    data/observability.db   ◄── append-only snapshots + events    │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│       ▲                                                                │
│       │ HTTP + WebSocket on 127.0.0.1:8765 (configurable)              │
│       │                                                                │
│  ┌────┴───────────────────┐                                            │
│  │  Browser at /          │                                            │
│  │    Timeline tab        │                                            │
│  │    Topology tab        │                                            │
│  │    Manifest tab        │                                            │
│  └────────────────────────┘                                            │
└────────────────────────────────────────────────────────────────────────┘
```

## Detailed design

### Data model (SQLite)

```sql
CREATE TABLE manifest_snapshots (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    captured_at     TEXT NOT NULL,
    source_path     TEXT NOT NULL,
    bet_id          TEXT NOT NULL,
    schema_version  INTEGER NOT NULL,
    content_hash    TEXT NOT NULL UNIQUE,
    manifest_json   TEXT NOT NULL
);

CREATE TABLE events (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    received_at     TEXT NOT NULL,
    occurred_at     TEXT NOT NULL,
    bet_id          TEXT,
    skill_id        TEXT NOT NULL,
    phase           TEXT NOT NULL,          -- start | progress | end | error
    manifest_field  TEXT,
    evidence_before TEXT,                   -- fact | assumption | inference | open_question | null
    evidence_after  TEXT,                   -- same enum
    operator_handle TEXT,
    payload_json    TEXT NOT NULL
);
```

`manifest_snapshots.content_hash` is `UNIQUE`. The watcher hashes manifest content before insert; identical content (e.g., from editor save patterns that fire multiple inotify events per logical save) is deduplicated.

Both tables are **append-only**. The event log is meant to be replayed, not mutated.

### Event ingest schema

```json
{
  "skill_id": "string (required)",
  "phase": "start | progress | end | error (required)",
  "bet_id": "string (optional)",
  "manifest_field": "dotted path, e.g. tenets[0].statement (optional)",
  "evidence_before": "fact | assumption | inference | open_question | null",
  "evidence_after":  "fact | assumption | inference | open_question | null",
  "occurred_at": "ISO-8601; server fills in if absent",
  "operator_handle": "string (optional)",
  "payload": "object (arbitrary per-event context)"
}
```

Aligned with `vocabulary.yaml`'s `assumption_tags` enum for `evidence_*` fields. `phase` is the suite's first event-level enum — added in this RFC.

### Topology builder

`server/topology.py` reads `lifecycle.yaml` (the suite's canonical machine-readable skill graph) and produces `{nodes, edges, phase_order, stats}`. Edges are the union of every skill's `feeds_into` and every skill's `consumes_from`, deduplicated by `(source, target)` and annotated with which side declared the edge.

Why not also parse `SKILL.md` `## Handoffs` tables? Because the suite's design pattern explicitly designates `lifecycle.yaml` as the skill-level summary source and SKILL.md as the field-level detail. Mixing the two would couple this layer to markdown parsing for marginal gain.

### Frontend (vanilla JS, no build step)

- **Timeline** (B5): chronological list of snapshots + events. Newest first. New entries animate-in via CSS keyframes. WebSocket-driven with a 1.5-second reconnect loop on disconnect.
- **Topology** (B6): SVG DAG. Columns by lifecycle phase from `lifecycle.yaml`; nodes sorted by skill number within column; edges as Bezier curves with arrowhead markers; hover-to-highlight a node's edges. Constructive vs interrogative distinguished by border style.
- **Manifest** (B6): recursive tree renderer. Any object with an `evidence` key gets a colored left border + a badge. Colors map to the suite's existing palette (`fact` green, `inference` blue, `assumption` yellow, `open_question` red).

### emit-event.sh helper

```bash
amazonian_emit_event <skill_id> <phase> [manifest_field] [evidence_before] [evidence_after]
```

Optional stdin: a JSON object becomes the event's `payload`. Optional env:
- `AMAZONIAN_OBSERVABILITY_URL` — when unset, the function returns 0 immediately. When set, posts to `$URL/api/events` with a 1-second timeout.
- `AMAZONIAN_BET_ID` — attached as `bet_id`.
- `AMAZONIAN_OPERATOR_HANDLE` — attached as `operator_handle`.

The shell function shells out to a `python3` heredoc to construct the JSON (avoids the shell-quoting hazards of JSON-by-string-concatenation). All failure modes return 0; nothing about emission is allowed to affect the calling skill's exit code.

### Loopback enforcement

Defense in depth:

1. **Bind**: `uvicorn --host 127.0.0.1` (default in the Makefile).
2. **Request check**: each request handler calls `_refuse_non_loopback(request)` which inspects `request.client.host`. WebSocket handler has the same check.

If either layer fails, the other catches it. Adding both is not redundant if the bind ever drifts to `0.0.0.0` for any reason (Docker mounts, dev tunnel misconfig, etc.).

## Risks

| Risk | Mitigation |
|---|---|
| **Event log replaces the manifest as canonical** | Architectural commitment + README + tests. Skills MUST write to `governance.yaml`; events are sugar. The DB is regeneratable; the manifest is not. |
| **Observability stack drifts from suite schema** | `lifecycle.yaml` is the topology source. When skills change their `consumes_from` / `feeds_into`, the DAG re-renders. Snapshots are stored as raw JSON; schema migrations in v2 will need to migrate forward. |
| **Server runs uninvited on a non-loopback interface** | Two-layer enforcement (bind + per-request check). The Makefile defaults to 127.0.0.1; operators who override must understand the change. |
| **emit-event.sh hangs a long-running skill on a timeout** | Hard 1-second timeout in the Python urllib call. Verified by running with an unreachable URL on port 1: returns within ~1s. |
| **The seed-demo writes to repo root and a developer commits the demo manifest** | Repo root `.gitignore` excludes `/governance.yaml`. The suite itself is not a "bet"; operators get their own manifest in their target repo. |
| **SQLite WAL files clutter the working tree** | Both `.gitignore`s (repo root and `tools/observability/`) exclude the WAL/SHM sidecars. |

## Open questions

1. **Multi-manifest observability** (defer to v2). The current server watches one `governance.yaml`. For portfolio-level visibility, the watcher needs to scan a configured set of paths. Schema is already designed for this (`source_path` per snapshot, `bet_id` per event).
2. **Manifest-field → event index** (defer to v2). The manifest tree could link each field to the events that touched it. Requires consistent `manifest_field` discipline in emit-event.sh callers; defer until skill integrations beyond 00/14 land.
3. **Edge labels in the DAG** (deferred). 94 edges across 15 nodes is dense; field-name labels would be noisy. Future polish could surface them on edge hover.
4. **Replay** (deferred). Given the append-only event log, replay-from-time-T is mechanically easy. Defer until an operator actually wants it.

## Implementation phasing

| Batch | Commit | Scope |
|---|---|---|
| B5 | `e2e42f9` | Backend skeleton (FastAPI + SQLite + WebSocket), watcher, timeline frontend |
| B6 | `5b9050d` | Topology DAG view, manifest inspector, topology builder, `lifecycle.yaml` extension for skills 00 and 14 |
| B7 | *this commit* | `scripts/lib/emit-event.sh`, `seed-demo.sh` / `teardown-demo.sh`, skill integration notes in 00 and 14, root README mention, this RFC |

## Compliance check

| Rule (from `AGENT.md` and the suite's existing design patterns) | Compliance |
|---|---|
| Manifest is the source of truth | ✓ Server reads `governance.yaml`; never writes. |
| Skill suite is functional without observability | ✓ Verified: `make down` then run any skill — no regression. |
| Loopback-only | ✓ Bind + per-request check. |
| Best-effort emission | ✓ emit-event.sh returns 0 on unset URL and unreachable URL. Tested. |
| Append-only event log | ✓ No UPDATE/DELETE statements in `db.py`. |
| Schema is documented | ✓ This RFC, plus `tools/observability/README.md`. |
| Evidence-tag discipline applies to event payloads | ✓ `evidence_before` / `evidence_after` constrained to the suite's `assumption_tags` enum. |

## Approval

Approved by operator: 2026-05-22.
Implemented: 2026-05-22, batches B5–B7.
