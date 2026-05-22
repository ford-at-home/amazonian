# Amazonian Observability (localhost-only)

A read-mostly observability stack over `governance.yaml`. Tails the manifest, ingests skill-emitted events, persists both to SQLite, and renders them in a browser at `http://127.0.0.1:8765/`.

**The stack is strictly optional.** The Amazonian skill suite is fully functional without it. Skills write canonical state to `governance.yaml`; this server observes that file and adds an event log alongside. See [RFC-001 §3.2](../../docs/rfcs/RFC-001-deployment-and-orchestration.md) for the source-of-truth contract.

## Why it exists

To make the data flow visible: which skill emitted which event, what manifest field changed as a result, and how `evidence` tags evolve over a session. The suite is intentionally text-first; this view is for *watching the agent work* in real time, not for replacing the manifest.

## What's in v1 (B5–B7 of RFC-002)

- Backend: FastAPI + SQLite + WebSocket
- Manifest file watcher with content-hash dedupe
- `POST /api/events` for skill emission
- Frontend with three tabs:
  - **Timeline**: snapshots + events, newest first, live updates
  - **Topology**: skill DAG from `lifecycle.yaml` with hover-to-highlight
  - **Manifest**: indented tree with evidence-tag color coding
- `scripts/lib/emit-event.sh`: best-effort POST helper for skills
- `make up` / `make down` / `make smoke` workflow
- `tools/observability/scripts/seed-demo.sh`: scripted ChangeLens walkthrough

## Quick start

```bash
cd tools/observability
make up-bg                                 # start server in background
open http://127.0.0.1:8765/                # or visit manually
./scripts/seed-demo.sh                     # replay a worked ChangeLens session
```

What the seed walkthrough does (paced; pass `--fast` for no pacing):

1. Drops `skills/00-repo-state-import/examples/example-bootstrap.yaml` into the repo root as `governance.yaml`. **Snapshot 1** lands; the watcher picks it up.
2. Emits a `00-repo-state-import end` event recording the bootstrap.
3. Emits a `14-lifecycle-navigator start` event.
4. Emits a `progress` event recording the state-machine match (position: `operating-wbr-due`).
5. Emits a `progress` event recording the phase-laundering finding on `live_mechanisms[wbr-monday]` (it's `evidence: assumption`).
6. Emits an `end` event with `routing_decision: upstream_remediation` and `recommended_skill: 04-mechanism-designer`.
7. Emits a `04-mechanism-designer end` event recording the spec being written.
8. Rewrites the manifest's WBR mechanism to `evidence: fact` and a real `spec_path`. **Snapshot 2** lands.

Watch the three tabs as it runs:

- **Timeline** fills in with the alternating snapshots and events.
- **Topology** is static for this demo (it's a property of the suite, not the bet) but the DAG you see makes the data flow legible.
- **Manifest** updates twice: first when snapshot 1 arrives (you can see `live_mechanisms[wbr-monday]` with a yellow `assumption` border), then again at snapshot 2 (the border goes green and the badge flips to `fact`).

Tear down with `./scripts/teardown-demo.sh && make down`.

## Manual exercise

If you'd rather drive it yourself:

```bash
# Edit the manifest — the timeline will pick it up.
$EDITOR governance.yaml

# Or post a synthetic event:
curl -fsS -X POST http://127.0.0.1:8765/api/events \
  -H 'Content-Type: application/json' \
  -d '{
    "skill_id": "00-repo-state-import",
    "phase": "end",
    "bet_id": "changelens",
    "manifest_field": "tenets[0].statement",
    "evidence_after": "fact",
    "payload": {"source": "docs/principles.md"}
  }'
```

## Skill integration via emit-event.sh

Skills emit events into this stack by sourcing the helper:

```bash
source scripts/lib/emit-event.sh
amazonian_emit_event <skill_id> <phase> [manifest_field] [evidence_before] [evidence_after]
```

The helper is a silent no-op when `AMAZONIAN_OBSERVABILITY_URL` is unset OR when the server is unreachable (1-second timeout). The skill suite is required to work regardless — emit-event.sh is observability sugar.

Verified failure modes (real tests, not [Unverified]):
- Unset `AMAZONIAN_OBSERVABILITY_URL` → returns 0; no DB write.
- Set URL but unreachable port → returns 0 within ~1s; no DB write.
- Reachable server → POSTs the event; broadcasts to live WebSocket clients.

## API surface

| Method | Path | Purpose |
|---|---|---|
| `GET` | `/healthz` | Liveness probe |
| `GET` | `/api/state` | Current snapshot summary + counts |
| `GET` | `/api/snapshots?limit=N` | Recent manifest snapshots, newest first |
| `GET` | `/api/events?since_id=N&limit=N` | Events; `since_id` returns ascending after that id, otherwise descending newest first |
| `POST` | `/api/events` | Ingest a skill event (see schema below) |
| `GET` | `/api/topology` | DAG nodes + edges (stub in B5; populated in B6) |
| `WS` | `/api/live` | Push notifications: `{"type": "snapshot"\|"event"\|"hello", "data": ...}` |

The server **refuses all non-loopback connections** in addition to binding `127.0.0.1` only.

### Event ingest schema

```json
{
  "skill_id": "string (required)",
  "phase": "start | progress | end | error (required)",
  "bet_id": "string (optional)",
  "manifest_field": "string (optional; dotted path, e.g. tenets[0].statement)",
  "evidence_before": "fact | assumption | inference | open_question | null",
  "evidence_after":  "fact | assumption | inference | open_question | null",
  "occurred_at": "ISO-8601 timestamp (optional; server fills in current time if absent)",
  "operator_handle": "string (optional)",
  "payload": "object (optional; arbitrary per-event context)"
}
```

## Configuration

Environment variables (set in the shell or via the Makefile):

| Var | Default | Purpose |
|---|---|---|
| `AMAZONIAN_OBS_MANIFEST_PATH` | `<repo-root>/governance.yaml` | Manifest to watch |
| `AMAZONIAN_OBS_DB_PATH` | `tools/observability/data/observability.db` | SQLite file |
| `AMAZONIAN_OBS_LOG_LEVEL` | `INFO` | Python logging level |

CLI flags pass to uvicorn through the Makefile: `HOST`, `PORT`, etc.

```bash
make up PORT=9000
```

## Data model (SQLite)

```text
manifest_snapshots(id, captured_at, source_path, bet_id, schema_version, content_hash UNIQUE, manifest_json)
events            (id, received_at, occurred_at, bet_id, skill_id, phase, manifest_field,
                   evidence_before, evidence_after, operator_handle, payload_json)
```

Both tables are append-only by design. `content_hash` is `UNIQUE`, which is the dedupe mechanism for noisy editor save events.

## Architectural commitments (do not break)

1. **Manifest is the source of truth.** This server reads it; never writes it.
2. **Localhost only.** No remote access, ever. Both the bind and a defense-in-depth request check enforce this.
3. **Optional.** Skills must work when this server isn't running. The event-emit helper (B7) is best-effort with a hard timeout and silent failure mode.
4. **No agent state lives only here.** If a piece of governance state matters, it goes in `governance.yaml`. This DB is a projection plus an event log; it is regeneratable.
