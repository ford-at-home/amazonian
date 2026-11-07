"""Pydantic models for the observability API.

These are the wire formats. SQLite stores the same data but in flatter form
(JSON-encoded blobs for the parts where structure is variable).
"""
from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field

EvidenceTag = Literal["fact", "assumption", "inference", "open_question"]
EventPhase = Literal["start", "progress", "end", "error"]


class EventIn(BaseModel):
    """Wire format for POST /api/events. Skills emit these via emit-event.sh.

    The only required fields are `skill_id` and `phase`. Everything else is
    optional context the skill happens to know at emit time.
    """

    skill_id: str = Field(..., min_length=1, max_length=100)
    phase: EventPhase
    bet_id: str | None = None
    manifest_field: str | None = None
    evidence_before: EvidenceTag | None = None
    evidence_after: EvidenceTag | None = None
    occurred_at: datetime | None = None
    operator_handle: str | None = None
    payload: dict[str, Any] = Field(default_factory=dict)


class EventOut(BaseModel):
    id: int
    received_at: datetime
    occurred_at: datetime
    skill_id: str
    phase: EventPhase
    bet_id: str | None
    manifest_field: str | None
    evidence_before: EvidenceTag | None
    evidence_after: EvidenceTag | None
    operator_handle: str | None
    payload: dict[str, Any]


class SnapshotOut(BaseModel):
    id: int
    captured_at: datetime
    source_path: str
    bet_id: str
    schema_version: int
    content_hash: str
    manifest: dict[str, Any]


class StateOut(BaseModel):
    """Summary of current observability state, surfaced at /api/state."""

    manifest_present: bool
    manifest_path: str
    latest_snapshot: SnapshotOut | None
    snapshot_count: int
    event_count: int
    server_started_at: datetime


class LiveMessage(BaseModel):
    """WebSocket push payload."""

    type: Literal["snapshot", "event", "hello"]
    data: dict[str, Any]
