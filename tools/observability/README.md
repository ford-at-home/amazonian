# Amazonian Observability (localhost-only)

A read-mostly observability stack over `governance.yaml`. Tails the manifest, ingests skill-emitted events, persists both to SQLite, and renders them in a browser at `http://127.0.0.1:8765/`.

**The stack is strictly optional.** The Amazonian skill suite is fully functional without it. Skills write canonical state to `governance.yaml`; this server observes that file and adds an event log alongside. See [RFC-001 §3.2](../../docs/rfcs/RFC-001-deployment-and-orchestration.md) for the source-of-truth contract.

## Why it exists

To make the data flow visible: which skill emitted which event, what manifest field changed as a result, and how `evidence` tags evolve over a session. The suite is intentionally text-first; this view is for *watching the agent work* in real time, not for replacing the manifest.

## What's in v0 (B5 of RFC-001)

- Backend: FastAPI + SQLite + WebSocket
- Manifest file watcher with content-hash dedupe
- `POST /api/events` for skill emission
- Frontend timeline view with live updates
- `make up` / `make down` / `make smoke` workflow

What's not here yet (lands in B6): topology DAG view, colorized manifest inspector. Lands in B7: `scripts/lib/emit-event.sh` helper, skill integration, demo seed.

## Quick start

```bash
cd tools/observability
make up
# Visit http://127.0.0.1:8765/
```

Then, from another terminal in the repo root:

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

You should see both the snapshot (from the manifest edit) and the event appear in the timeline within ~1 second.

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
