"""SQLite schema + helpers.

Raw sqlite3, no ORM. Schema is tiny and stable. Async-friendly via
asyncio.to_thread wrappers in app.py; this module is pure sync.

The dedupe contract: manifest_snapshots.content_hash is UNIQUE. The watcher
hashes the file's content; if the hash matches the latest snapshot, we skip
the insert. This prevents double-snapshots from editor save patterns that
fire multiple inotify events.
"""
from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SCHEMA = """
CREATE TABLE IF NOT EXISTS manifest_snapshots (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    captured_at     TEXT NOT NULL,
    source_path     TEXT NOT NULL,
    bet_id          TEXT NOT NULL,
    schema_version  INTEGER NOT NULL,
    content_hash    TEXT NOT NULL UNIQUE,
    manifest_json   TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_snapshots_bet_captured
    ON manifest_snapshots(bet_id, captured_at);

CREATE TABLE IF NOT EXISTS events (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    received_at     TEXT NOT NULL,
    occurred_at     TEXT NOT NULL,
    bet_id          TEXT,
    skill_id        TEXT NOT NULL,
    phase           TEXT NOT NULL,
    manifest_field  TEXT,
    evidence_before TEXT,
    evidence_after  TEXT,
    operator_handle TEXT,
    payload_json    TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_events_bet_occurred
    ON events(bet_id, occurred_at);
CREATE INDEX IF NOT EXISTS idx_events_skill
    ON events(skill_id);
"""


def connect(db_path: Path) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path, isolation_level=None, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode = WAL;")
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def init_schema(conn: sqlite3.Connection) -> None:
    conn.executescript(SCHEMA)


def insert_snapshot(
    conn: sqlite3.Connection,
    *,
    source_path: str,
    bet_id: str,
    schema_version: int,
    content_hash: str,
    manifest: dict[str, Any],
) -> int | None:
    """Insert a snapshot. Returns the new row id, or None if the hash was
    already present (dedupe path)."""
    try:
        cur = conn.execute(
            """
            INSERT INTO manifest_snapshots
                (captured_at, source_path, bet_id, schema_version, content_hash, manifest_json)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                _now_iso(),
                source_path,
                bet_id,
                schema_version,
                content_hash,
                json.dumps(manifest, default=str, sort_keys=True),
            ),
        )
        return cur.lastrowid
    except sqlite3.IntegrityError:
        return None


def insert_event(
    conn: sqlite3.Connection,
    *,
    occurred_at: datetime,
    skill_id: str,
    phase: str,
    bet_id: str | None,
    manifest_field: str | None,
    evidence_before: str | None,
    evidence_after: str | None,
    operator_handle: str | None,
    payload: dict[str, Any],
) -> int:
    cur = conn.execute(
        """
        INSERT INTO events
            (received_at, occurred_at, bet_id, skill_id, phase,
             manifest_field, evidence_before, evidence_after,
             operator_handle, payload_json)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            _now_iso(),
            occurred_at.isoformat(),
            bet_id,
            skill_id,
            phase,
            manifest_field,
            evidence_before,
            evidence_after,
            operator_handle,
            json.dumps(payload, default=str),
        ),
    )
    assert cur.lastrowid is not None
    return cur.lastrowid


def latest_snapshot(conn: sqlite3.Connection) -> dict[str, Any] | None:
    row = conn.execute(
        "SELECT * FROM manifest_snapshots ORDER BY id DESC LIMIT 1"
    ).fetchone()
    return _snapshot_row_to_dict(row) if row else None


def list_snapshots(conn: sqlite3.Connection, limit: int = 100) -> list[dict[str, Any]]:
    rows = conn.execute(
        "SELECT * FROM manifest_snapshots ORDER BY id DESC LIMIT ?",
        (limit,),
    ).fetchall()
    return [_snapshot_row_to_dict(r) for r in rows]


def list_events(
    conn: sqlite3.Connection,
    *,
    since_id: int | None = None,
    limit: int = 200,
) -> list[dict[str, Any]]:
    if since_id is not None:
        rows = conn.execute(
            "SELECT * FROM events WHERE id > ? ORDER BY id ASC LIMIT ?",
            (since_id, limit),
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT * FROM events ORDER BY id DESC LIMIT ?",
            (limit,),
        ).fetchall()
    return [_event_row_to_dict(r) for r in rows]


def get_event(conn: sqlite3.Connection, event_id: int) -> dict[str, Any] | None:
    row = conn.execute("SELECT * FROM events WHERE id = ?", (event_id,)).fetchone()
    return _event_row_to_dict(row) if row else None


def counts(conn: sqlite3.Connection) -> dict[str, int]:
    snap = conn.execute("SELECT COUNT(*) AS c FROM manifest_snapshots").fetchone()
    evt = conn.execute("SELECT COUNT(*) AS c FROM events").fetchone()
    return {"snapshot_count": snap["c"], "event_count": evt["c"]}


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _snapshot_row_to_dict(row: sqlite3.Row) -> dict[str, Any]:
    return {
        "id": row["id"],
        "captured_at": row["captured_at"],
        "source_path": row["source_path"],
        "bet_id": row["bet_id"],
        "schema_version": row["schema_version"],
        "content_hash": row["content_hash"],
        "manifest": json.loads(row["manifest_json"]),
    }


def _event_row_to_dict(row: sqlite3.Row) -> dict[str, Any]:
    return {
        "id": row["id"],
        "received_at": row["received_at"],
        "occurred_at": row["occurred_at"],
        "bet_id": row["bet_id"],
        "skill_id": row["skill_id"],
        "phase": row["phase"],
        "manifest_field": row["manifest_field"],
        "evidence_before": row["evidence_before"],
        "evidence_after": row["evidence_after"],
        "operator_handle": row["operator_handle"],
        "payload": json.loads(row["payload_json"]),
    }
