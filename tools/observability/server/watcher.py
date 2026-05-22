"""Manifest file watcher.

Watches the configured governance.yaml path. On every change (including the
file appearing for the first time), reads + hashes the content and inserts
a new manifest_snapshots row when the hash differs from the latest.

The hash dedupe matters because editor save patterns (vim, VS Code) often
emit multiple inotify events per logical save. Without dedupe we'd churn
out duplicate snapshots that don't represent real state changes.
"""
from __future__ import annotations

import asyncio
import hashlib
import logging
from pathlib import Path
from typing import Any, Callable, Awaitable

import yaml
from watchfiles import awatch

from . import db

log = logging.getLogger(__name__)

SnapshotCallback = Callable[[dict[str, Any]], Awaitable[None]]


class ManifestWatcher:
    """Async watcher that mirrors governance.yaml into the snapshots table.

    Calls `on_new_snapshot` whenever a non-duplicate snapshot is recorded.
    The watcher is fault-tolerant: it does not crash on parse errors or on
    the file being missing — both are observable states it reports through
    structured log lines.
    """

    def __init__(
        self,
        manifest_path: Path,
        conn,
        on_new_snapshot: SnapshotCallback,
    ) -> None:
        self.manifest_path = manifest_path.resolve()
        self.conn = conn
        self.on_new_snapshot = on_new_snapshot
        self._stop = asyncio.Event()

    async def run(self) -> None:
        await self._capture_initial()
        watch_target = self._watch_target()
        log.info("watcher: starting; target=%s", watch_target)
        try:
            async for _changes in awatch(
                watch_target, stop_event=self._stop, recursive=False
            ):
                await self._capture_if_changed()
        except Exception:
            log.exception("watcher: terminated unexpectedly")
            raise

    def stop(self) -> None:
        self._stop.set()

    def _watch_target(self) -> Path:
        if self.manifest_path.exists():
            return self.manifest_path
        return self.manifest_path.parent

    async def _capture_initial(self) -> None:
        if self.manifest_path.exists():
            await self._capture_if_changed()
        else:
            log.info(
                "watcher: manifest not present yet at %s; watching parent dir",
                self.manifest_path,
            )

    async def _capture_if_changed(self) -> None:
        if not self.manifest_path.exists():
            return
        try:
            raw = self.manifest_path.read_bytes()
        except OSError as exc:
            log.warning("watcher: could not read manifest: %s", exc)
            return

        content_hash = hashlib.sha256(raw).hexdigest()

        try:
            manifest = yaml.safe_load(raw)
        except yaml.YAMLError as exc:
            log.warning("watcher: manifest parse error: %s", exc)
            return
        if not isinstance(manifest, dict):
            log.warning("watcher: manifest root is not a mapping; skipping")
            return

        bet = manifest.get("bet") or {}
        bet_id = bet.get("id") or "<unknown>"
        schema_version = manifest.get("schema_version", 0)

        snapshot_id = await asyncio.to_thread(
            db.insert_snapshot,
            self.conn,
            source_path=str(self.manifest_path),
            bet_id=bet_id,
            schema_version=schema_version,
            content_hash=content_hash,
            manifest=manifest,
        )

        if snapshot_id is None:
            return

        log.info(
            "watcher: snapshot %d captured; bet_id=%s hash=%s...",
            snapshot_id,
            bet_id,
            content_hash[:8],
        )

        snapshot = await asyncio.to_thread(db.latest_snapshot, self.conn)
        if snapshot is not None:
            await self.on_new_snapshot(snapshot)
