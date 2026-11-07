"""FastAPI app for the Amazonian observability stack.

Reads `governance.yaml` via a file watcher, ingests skill events via
POST /api/events, persists both to SQLite, and pushes change notifications
to connected WebSocket clients.

Architectural commitment: this server is OPTIONAL. The Amazonian skill suite
remains fully functional without it. Skills write canonical state to
governance.yaml; this server observes that file and adds an event log.
See docs/rfcs/RFC-001-deployment-and-orchestration.md and the user-facing
discussion at tools/observability/README.md.
"""
from __future__ import annotations

import asyncio
import contextlib
import logging
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from fastapi import (
    FastAPI,
    HTTPException,
    Request,
    WebSocket,
    WebSocketDisconnect,
    status,
)
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from . import db
from .models import EventIn, EventOut, LiveMessage, SnapshotOut, StateOut
from .topology import build_topology
from .watcher import ManifestWatcher

log = logging.getLogger(__name__)
logging.basicConfig(
    level=os.environ.get("AMAZONIAN_OBS_LOG_LEVEL", "INFO"),
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)


def _resolve_paths() -> tuple[Path, Path]:
    """Resolve manifest + DB paths from env, with sane defaults relative to
    the observability dir."""
    obs_root = Path(__file__).resolve().parent.parent
    repo_root = obs_root.parent.parent

    manifest_env = os.environ.get("AMAZONIAN_OBS_MANIFEST_PATH")
    manifest_path = (
        Path(manifest_env).expanduser().resolve()
        if manifest_env
        else (repo_root / "governance.yaml").resolve()
    )

    db_env = os.environ.get("AMAZONIAN_OBS_DB_PATH")
    db_path = (
        Path(db_env).expanduser().resolve()
        if db_env
        else (obs_root / "data" / "observability.db").resolve()
    )

    return manifest_path, db_path


class ConnectionManager:
    """Tracks active WebSocket clients and broadcasts LiveMessages."""

    def __init__(self) -> None:
        self._clients: set[WebSocket] = set()
        self._lock = asyncio.Lock()

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        async with self._lock:
            self._clients.add(websocket)
        log.info("ws: client connected (total=%d)", len(self._clients))

    async def disconnect(self, websocket: WebSocket) -> None:
        async with self._lock:
            self._clients.discard(websocket)
        log.info("ws: client disconnected (total=%d)", len(self._clients))

    async def broadcast(self, msg: LiveMessage) -> None:
        async with self._lock:
            clients = list(self._clients)
        dead: list[WebSocket] = []
        for ws in clients:
            try:
                await ws.send_json(msg.model_dump(mode="json"))
            except Exception:
                dead.append(ws)
        if dead:
            async with self._lock:
                for ws in dead:
                    self._clients.discard(ws)


MANIFEST_PATH, DB_PATH = _resolve_paths()
SERVER_STARTED_AT = datetime.now(timezone.utc)

connections = ConnectionManager()
_conn = db.connect(DB_PATH)
db.init_schema(_conn)


async def _on_new_snapshot(snapshot: dict[str, Any]) -> None:
    await connections.broadcast(LiveMessage(type="snapshot", data=snapshot))


async def _watcher_task() -> None:
    watcher = ManifestWatcher(MANIFEST_PATH, _conn, _on_new_snapshot)
    try:
        await watcher.run()
    except asyncio.CancelledError:
        watcher.stop()
        raise


@contextlib.asynccontextmanager
async def lifespan(_app: FastAPI):
    task = asyncio.create_task(_watcher_task())
    log.info(
        "startup: manifest=%s db=%s", MANIFEST_PATH, DB_PATH,
    )
    try:
        yield
    finally:
        task.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await task


app = FastAPI(title="Amazonian Observability", lifespan=lifespan)

STATIC_DIR = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/", response_class=HTMLResponse)
async def index() -> HTMLResponse:
    return HTMLResponse((STATIC_DIR / "index.html").read_text())


@app.get("/healthz")
async def healthz() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/state", response_model=StateOut)
async def get_state() -> StateOut:
    latest = await asyncio.to_thread(db.latest_snapshot, _conn)
    c = await asyncio.to_thread(db.counts, _conn)
    return StateOut(
        manifest_present=MANIFEST_PATH.exists(),
        manifest_path=str(MANIFEST_PATH),
        latest_snapshot=SnapshotOut(**latest) if latest else None,
        snapshot_count=c["snapshot_count"],
        event_count=c["event_count"],
        server_started_at=SERVER_STARTED_AT,
    )


@app.get("/api/snapshots", response_model=list[SnapshotOut])
async def get_snapshots(limit: int = 100) -> list[SnapshotOut]:
    if limit < 1 or limit > 1000:
        raise HTTPException(status_code=400, detail="limit must be 1..1000")
    rows = await asyncio.to_thread(db.list_snapshots, _conn, limit)
    return [SnapshotOut(**r) for r in rows]


@app.get("/api/events", response_model=list[EventOut])
async def get_events(
    since_id: int | None = None, limit: int = 200,
) -> list[EventOut]:
    if limit < 1 or limit > 1000:
        raise HTTPException(status_code=400, detail="limit must be 1..1000")
    rows = await asyncio.to_thread(
        db.list_events, _conn, since_id=since_id, limit=limit,
    )
    return [EventOut(**r) for r in rows]


@app.post(
    "/api/events", response_model=EventOut, status_code=status.HTTP_201_CREATED,
)
async def post_event(payload: EventIn, request: Request) -> EventOut:
    _refuse_non_loopback(request)
    occurred = payload.occurred_at or datetime.now(timezone.utc)
    new_id = await asyncio.to_thread(
        db.insert_event,
        _conn,
        occurred_at=occurred,
        skill_id=payload.skill_id,
        phase=payload.phase,
        bet_id=payload.bet_id,
        manifest_field=payload.manifest_field,
        evidence_before=payload.evidence_before,
        evidence_after=payload.evidence_after,
        operator_handle=payload.operator_handle,
        payload=payload.payload,
    )
    row = await asyncio.to_thread(db.get_event, _conn, new_id)
    assert row is not None
    event = EventOut(**row)
    await connections.broadcast(LiveMessage(type="event", data=row))
    return event


@app.get("/api/topology")
async def get_topology() -> dict[str, Any]:
    """Returns the suite's skill DAG derived from lifecycle.yaml.
    Cached by lru_cache in topology._load_lifecycle; cheap to call."""
    return await asyncio.to_thread(build_topology)


@app.websocket("/api/live")
async def ws_live(websocket: WebSocket) -> None:
    _refuse_non_loopback_ws(websocket)
    await connections.connect(websocket)
    try:
        await websocket.send_json(
            LiveMessage(
                type="hello",
                data={"server_started_at": SERVER_STARTED_AT.isoformat()},
            ).model_dump(mode="json")
        )
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        await connections.disconnect(websocket)


def _refuse_non_loopback(request: Request) -> None:
    """Refuse any request that did not come in over a loopback interface.
    The observability stack is localhost-only by contract; this is a
    defense-in-depth check on top of binding 127.0.0.1 only."""
    if not request.client or request.client.host not in {"127.0.0.1", "::1", "localhost"}:
        raise HTTPException(
            status_code=403,
            detail="observability API is localhost-only",
        )


def _refuse_non_loopback_ws(websocket: WebSocket) -> None:
    if not websocket.client or websocket.client.host not in {"127.0.0.1", "::1", "localhost"}:
        raise HTTPException(status_code=403, detail="observability WS is localhost-only")
