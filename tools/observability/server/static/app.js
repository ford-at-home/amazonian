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
    topoSvg: $("topo-svg"),
    topoStats: $("topo-stats"),
    manifestTree: $("manifest-tree"),
    manifestSnapshotPath: $("manifest-snapshot-path"),
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
        renderManifest(state.latest_snapshot);
      }
      const events = await fetch("/api/events?limit=200").then((r) => r.json());
      for (const ev of events) {
        entries.push({ kind: "event", id: ev.id, time: ev.occurred_at, payload: ev });
      }
      renderTimeline();

      const topo = await fetch("/api/topology").then((r) => r.json());
      renderTopology(topo);
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
        renderManifest(msg.data);
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

  // -------------------------------------------------------------------
  // Topology DAG renderer.
  //
  // Layout strategy: columns by lifecycle phase, sorted by skill number
  // within each column. Edges drawn as Bezier curves; self-loops skipped
  // because at this view level they don't add information.
  // -------------------------------------------------------------------
  const NS = "http://www.w3.org/2000/svg";
  const NODE_W = 150, NODE_H = 46, COL_W = 180, ROW_H = 64, PAD_X = 40, PAD_Y = 80;

  const renderTopology = (topo) => {
    const svg = ui.topoSvg;
    while (svg.firstChild) svg.removeChild(svg.firstChild);

    const phases = topo.phase_order;
    const byPhase = new Map(phases.map((p) => [p, []]));
    for (const n of topo.nodes) {
      (byPhase.get(n.phase) || byPhase.get("cross_cutting")).push(n);
    }
    for (const list of byPhase.values()) list.sort((a, b) => a.number.localeCompare(b.number));

    const positions = new Map();
    phases.forEach((phase, colIdx) => {
      const list = byPhase.get(phase) || [];
      list.forEach((node, rowIdx) => {
        positions.set(node.id, {
          x: PAD_X + colIdx * COL_W,
          y: PAD_Y + rowIdx * ROW_H,
        });
      });
    });

    const maxRows = Math.max(...phases.map((p) => (byPhase.get(p) || []).length));
    const width = PAD_X * 2 + phases.length * COL_W;
    const height = PAD_Y + maxRows * ROW_H + 40;
    svg.setAttribute("viewBox", `0 0 ${width} ${height}`);
    svg.setAttribute("width", width);
    svg.setAttribute("height", height);

    const defs = document.createElementNS(NS, "defs");
    defs.innerHTML = `
      <marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
        <path d="M 0 0 L 10 5 L 0 10 z" fill="#5a6371" />
      </marker>
      <marker id="arrow-hi" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
        <path d="M 0 0 L 10 5 L 0 10 z" fill="#d29922" />
      </marker>
    `;
    svg.appendChild(defs);

    phases.forEach((phase, colIdx) => {
      const label = document.createElementNS(NS, "text");
      label.setAttribute("x", PAD_X + colIdx * COL_W + NODE_W / 2);
      label.setAttribute("y", 28);
      label.setAttribute("text-anchor", "middle");
      label.setAttribute("class", "phase-label");
      label.textContent = phase;
      svg.appendChild(label);
    });

    const edgeLayer = document.createElementNS(NS, "g");
    edgeLayer.setAttribute("class", "edges");
    svg.appendChild(edgeLayer);

    const edgeIndex = new Map();
    for (const edge of topo.edges) {
      if (edge.self_loop) continue;
      const a = positions.get(edge.source);
      const b = positions.get(edge.target);
      if (!a || !b) continue;
      const path = document.createElementNS(NS, "path");
      const x1 = a.x + NODE_W, y1 = a.y + NODE_H / 2;
      const x2 = b.x,          y2 = b.y + NODE_H / 2;
      const cx = (x1 + x2) / 2;
      path.setAttribute("d", `M ${x1} ${y1} C ${cx} ${y1}, ${cx} ${y2}, ${x2} ${y2}`);
      path.setAttribute("class", "edge");
      path.setAttribute("marker-end", "url(#arrow)");
      path.dataset.source = edge.source;
      path.dataset.target = edge.target;
      edgeLayer.appendChild(path);

      pushTo(edgeIndex, edge.source, path);
      pushTo(edgeIndex, edge.target, path);
    }

    for (const node of topo.nodes) {
      const pos = positions.get(node.id);
      if (!pos) continue;

      const g = document.createElementNS(NS, "g");
      g.setAttribute("transform", `translate(${pos.x},${pos.y})`);
      g.setAttribute("class", `node node-${node.category}`);

      const rect = document.createElementNS(NS, "rect");
      rect.setAttribute("width", NODE_W);
      rect.setAttribute("height", NODE_H);
      rect.setAttribute("rx", "4");
      g.appendChild(rect);

      const num = document.createElementNS(NS, "text");
      num.setAttribute("x", 10);
      num.setAttribute("y", 18);
      num.setAttribute("class", "node-num");
      num.textContent = node.number;
      g.appendChild(num);

      const name = document.createElementNS(NS, "text");
      name.setAttribute("x", 10);
      name.setAttribute("y", 34);
      name.setAttribute("class", "node-name");
      name.textContent = truncate(node.id, 22);
      g.appendChild(name);

      g.addEventListener("mouseenter", () => highlightNode(node.id, edgeIndex, true));
      g.addEventListener("mouseleave", () => highlightNode(node.id, edgeIndex, false));

      svg.appendChild(g);
    }

    ui.topoStats.textContent = `${topo.stats.node_count} nodes · ${topo.stats.edge_count} edges (${topo.stats.self_loop_count} self-loops hidden)`;
  };

  const pushTo = (map, key, value) => {
    if (!map.has(key)) map.set(key, []);
    map.get(key).push(value);
  };

  const highlightNode = (nodeId, edgeIndex, on) => {
    const edges = edgeIndex.get(nodeId) || [];
    for (const e of edges) {
      if (on) {
        e.classList.add("edge-hi");
        e.setAttribute("marker-end", "url(#arrow-hi)");
      } else {
        e.classList.remove("edge-hi");
        e.setAttribute("marker-end", "url(#arrow)");
      }
    }
  };

  const truncate = (s, n) => (s.length <= n ? s : s.slice(0, n - 1) + "…");

  // -------------------------------------------------------------------
  // Manifest inspector.
  //
  // Renders the manifest as an indented tree. Any object that has an
  // `evidence` key gets a colored left border + an evidence badge.
  // -------------------------------------------------------------------
  const renderManifest = (snapshot) => {
    ui.manifestSnapshotPath.textContent = snapshot.source_path;
    const wrap = document.createElement("div");
    wrap.appendChild(renderNode("", snapshot.manifest, 0));
    ui.manifestTree.innerHTML = "";
    ui.manifestTree.appendChild(wrap);
  };

  const renderNode = (label, value, depth) => {
    const el = document.createElement("div");
    el.className = "mf-row";
    el.style.marginLeft = `${depth * 14}px`;

    if (value === null || value === undefined) {
      el.appendChild(kv(label, "null", "mf-null"));
      return el;
    }
    if (typeof value !== "object") {
      el.appendChild(kv(label, String(value), "mf-scalar"));
      return el;
    }
    if (Array.isArray(value)) {
      const header = kv(label, `[${value.length}]`, "mf-array-head");
      el.appendChild(header);
      value.forEach((item, idx) => {
        el.appendChild(renderNode(`[${idx}]`, item, depth + 1));
      });
      return el;
    }
    const evidence = value.evidence;
    if (evidence) el.classList.add(`evidence-border-${evidence}`);

    if (label !== "") {
      const head = document.createElement("div");
      head.className = "mf-key";
      head.textContent = label;
      if (evidence) {
        const badge = document.createElement("span");
        badge.className = `evidence evidence-${evidence}`;
        badge.textContent = evidence;
        head.appendChild(badge);
      }
      el.appendChild(head);
    }

    for (const [k, v] of Object.entries(value)) {
      el.appendChild(renderNode(k, v, depth + 1));
    }
    return el;
  };

  const kv = (label, val, valClass) => {
    const d = document.createElement("div");
    if (label) {
      const k = document.createElement("span");
      k.className = "mf-key";
      k.textContent = `${label}: `;
      d.appendChild(k);
    }
    const v = document.createElement("span");
    v.className = valClass;
    v.textContent = val;
    d.appendChild(v);
    return d;
  };

  init().then(connectWs);
})();
