// Amazonian observability frontend.
// Pulls /api/state for initial render, subscribes to /api/live for push
// updates. No build step; everything is browser-native.
//
// State is intentionally minimal: a single in-memory `entries` array
// rendered as an HTML list. We don't reach for a framework because the
// observability stack has to clone-and-run with zero deps.

(() => {
  "use strict";

  const $ = (id) => document.getElementById(id);

  const ui = {
    wsDot: $("ws-status"),
    wsLabel: $("ws-label"),
    manifestPath: $("manifest-path"),
    snapshotCount: $("snapshot-count"),
    eventCount: $("event-count"),
    timeline: $("timeline"),
    manifestRaw: $("manifest-raw"),
  };

  // Tab switching.
  document.querySelectorAll(".tab").forEach((btn) => {
    btn.addEventListener("click", () => {
      document.querySelectorAll(".tab").forEach((t) => t.classList.remove("active"));
      document.querySelectorAll(".tab-panel").forEach((p) => p.classList.remove("active"));
      btn.classList.add("active");
      $(`tab-${btn.dataset.tab}`).classList.add("active");
    });
  });

  // ---- in-memory timeline ----
  // entries: { kind: "snapshot" | "event", id, time, payload }
  const entries = [];
  let counts = { snapshots: 0, events: 0 };

  const renderTimeline = () => {
    if (entries.length === 0) {
      ui.timeline.innerHTML = '<li class="empty">No events yet. Edit governance.yaml or POST to /api/events to populate.</li>';
      return;
    }
    ui.timeline.innerHTML = "";
    entries
      .slice()
      .sort((a, b) => (b.time || "").localeCompare(a.time || ""))
      .forEach((e, idx) => {
        const li = document.createElement("li");
        if (e.isNew && idx === 0) li.classList.add("new");
        li.appendChild(renderEntry(e));
        ui.timeline.appendChild(li);
      });
    entries.forEach((e) => (e.isNew = false));
  };

  const renderEntry = (e) => {
    const wrap = document.createElement("div");
    const row = document.createElement("div");
    row.className = "tl-row";

    const time = document.createElement("span");
    time.className = "tl-time";
    time.textContent = shortTime(e.time);
    row.appendChild(time);

    const kind = document.createElement("span");
    kind.className = `tl-kind tl-kind-${e.kind}`;
    kind.textContent = e.kind;
    row.appendChild(kind);

    if (e.kind === "snapshot") {
      const skill = document.createElement("span");
      skill.className = "tl-skill";
      skill.textContent = `bet:${e.payload.bet_id}`;
      row.appendChild(skill);
      const detail = document.createElement("span");
      detail.className = "tl-detail";
      detail.textContent = `manifest updated (hash ${e.payload.content_hash.slice(0, 7)})`;
      row.appendChild(detail);
    } else {
      const skill = document.createElement("span");
      skill.className = "tl-skill";
      skill.textContent = e.payload.skill_id;
      row.appendChild(skill);

      const detail = document.createElement("span");
      detail.className = "tl-detail";
      detail.textContent = `${e.payload.phase}${e.payload.manifest_field ? ` → ${e.payload.manifest_field}` : ""}`;
      row.appendChild(detail);

      if (e.payload.evidence_after) {
        row.appendChild(evidenceBadge(e.payload.evidence_before, e.payload.evidence_after));
      }
    }

    wrap.appendChild(row);

    if (e.kind === "event" && e.payload.payload && Object.keys(e.payload.payload).length) {
      const meta = document.createElement("span");
      meta.className = "tl-meta";
      meta.textContent = JSON.stringify(e.payload.payload);
      wrap.appendChild(meta);
    }
    return wrap;
  };

  const evidenceBadge = (before, after) => {
    const span = document.createElement("span");
    if (before && before !== after) {
      const b = document.createElement("span");
      b.className = `evidence evidence-${before}`;
      b.textContent = before;
      span.appendChild(b);
      span.appendChild(document.createTextNode(" → "));
    }
    const a = document.createElement("span");
    a.className = `evidence evidence-${after}`;
    a.textContent = after;
    span.appendChild(a);
    return span;
  };

  const shortTime = (iso) => {
    if (!iso) return "?";
    const d = new Date(iso);
    return isNaN(d) ? iso : d.toISOString().replace("T", " ").slice(11, 19);
  };

  const updateCounts = () => {
    ui.snapshotCount.textContent = `snapshots: ${counts.snapshots}`;
    ui.eventCount.textContent = `events: ${counts.events}`;
  };

  const setWs = (up) => {
    ui.wsDot.className = `ws-dot ws-${up ? "up" : "down"}`;
    ui.wsLabel.textContent = up ? "live" : "reconnecting…";
  };

  // ---- initial fetch ----
  const init = async () => {
    try {
      const state = await fetch("/api/state").then((r) => r.json());
      ui.manifestPath.textContent = `manifest: ${state.manifest_path}${state.manifest_present ? "" : " (missing)"}`;
      counts.snapshots = state.snapshot_count;
      counts.events = state.event_count;
      updateCounts();
      if (state.latest_snapshot) {
        entries.push({
          kind: "snapshot",
          id: state.latest_snapshot.id,
          time: state.latest_snapshot.captured_at,
          payload: state.latest_snapshot,
        });
        ui.manifestRaw.textContent = JSON.stringify(state.latest_snapshot.manifest, null, 2);
      }
      const events = await fetch("/api/events?limit=200").then((r) => r.json());
      for (const ev of events) {
        entries.push({ kind: "event", id: ev.id, time: ev.occurred_at, payload: ev });
      }
      renderTimeline();
    } catch (err) {
      console.error("init failed", err);
    }
  };

  // ---- live WebSocket ----
  const connectWs = () => {
    const proto = location.protocol === "https:" ? "wss:" : "ws:";
    const ws = new WebSocket(`${proto}//${location.host}/api/live`);
    ws.addEventListener("open", () => setWs(true));
    ws.addEventListener("close", () => {
      setWs(false);
      setTimeout(connectWs, 1500);
    });
    ws.addEventListener("error", () => ws.close());
    ws.addEventListener("message", (ev) => {
      const msg = JSON.parse(ev.data);
      if (msg.type === "hello") return;
      if (msg.type === "snapshot") {
        counts.snapshots += 1;
        entries.push({
          kind: "snapshot",
          id: msg.data.id,
          time: msg.data.captured_at,
          payload: msg.data,
          isNew: true,
        });
        ui.manifestRaw.textContent = JSON.stringify(msg.data.manifest, null, 2);
      } else if (msg.type === "event") {
        counts.events += 1;
        entries.push({
          kind: "event",
          id: msg.data.id,
          time: msg.data.occurred_at,
          payload: msg.data,
          isNew: true,
        });
      }
      updateCounts();
      renderTimeline();
    });
  };

  init().then(connectWs);
})();
