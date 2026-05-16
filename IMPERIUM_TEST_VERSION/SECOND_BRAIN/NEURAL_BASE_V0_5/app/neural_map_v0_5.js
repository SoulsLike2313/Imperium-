/* ═══════════════════════════════════════════════════════════════
   Second Brain Neural Map V0.5 — JS Part 1: Core, API, State
   PROTOTYPE_INTERACTIVE | RULE_BASED_ONLY | NO_LOCAL_LLM
   ═══════════════════════════════════════════════════════════════ */

"use strict";

// ── State ──────────────────────────────────────────────────────────────────────
const STATE = {
  snapshot: null,
  tasks: [],
  comments: [],
  links: [],
  activeTab: "tasks",
  activeZone: null,
  serverOnline: false,
  fps: 60,
  lastReceiptCount: 0
};

// ── Color map ──────────────────────────────────────────────────────────────────
const TOKEN_COLOR = {
  accent_cyan:    "#00d7ff",
  accent_amber:   "#ffb347",
  accent_magenta: "#ff4fd8",
  accent_green:   "#29c272",
  accent_red:     "#ff5d66",
  accent_violet:  "#7a84ff",
  text_muted:     "#3d5a78"
};

const HEALTH_COLOR = {
  WORKING:      "#00d7ff",
  PARTIAL:      "#ffb347",
  BLOCKED:      "#ff5d66",
  MISSING:      "#3d5a78",
  DISABLED:     "#2a3a50",
  EXPERIMENTAL: "#ff4fd8",
  TEST_ONLY:    "#7a84ff"
};

const HEALTH_PULSE_CLASS = {
  WORKING:      "pulse-working",
  PARTIAL:      "pulse-partial",
  BLOCKED:      "pulse-blocked",
  MISSING:      "pulse-missing",
  EXPERIMENTAL: "pulse-experimental",
  TEST_ONLY:    "pulse-experimental",
  DISABLED:     ""
};

const ZONE_ICONS = {
  core_brain:          "🧠",
  task_intake:         "📋",
  owner_comments:      "💬",
  memory_threads:      "🧵",
  progress_spine:      "📈",
  evidence_receipts:   "🔬",
  action_control:      "⚡",
  agent_exchange:      "🤖",
  delta_verification:  "🔍",
  testing_field:       "🧪",
  export_bundle_gate:  "📦",
  feature_module_dock: "🔌"
};

// ── API ────────────────────────────────────────────────────────────────────────
async function apiFetch(path, options = {}) {
  const res = await fetch(path, { cache: "no-store", ...options });
  if (!res.ok) throw new Error(`HTTP ${res.status} ${path}`);
  return res.json();
}

async function loadSnapshot() {
  try {
    STATE.snapshot = await apiFetch("/api/snapshot");
    return STATE.snapshot;
  } catch (e) {
    console.warn("Snapshot load failed:", e.message);
    return null;
  }
}

async function loadStatus() {
  try {
    const s = await apiFetch("/api/status");
    STATE.serverOnline = true;
    updateStatsBar(s);
    return s;
  } catch (e) {
    STATE.serverOnline = false;
    setServerBadge(false);
    return null;
  }
}

async function loadTasks() {
  try {
    STATE.tasks = await apiFetch("/api/tasks");
  } catch (e) {
    STATE.tasks = [];
  }
}

async function loadComments() {
  try {
    STATE.comments = await apiFetch("/api/comments");
  } catch (e) {
    STATE.comments = [];
  }
}

async function loadLinks() {
  try {
    STATE.links = await apiFetch("/api/links");
  } catch (e) {
    STATE.links = [];
  }
}

async function rebuildSnapshot() {
  notify("Пересборка snapshot…", "info");
  try {
    const r = await apiFetch("/api/rebuild_snapshot", { method: "POST", headers: {"Content-Type":"application/json"}, body: "{}" });
    if (r.status === "REBUILT") {
      notify("Snapshot пересобран", "success");
      await fullRefresh();
    } else {
      notify("Ошибка пересборки snapshot", "error");
    }
  } catch (e) {
    notify("Сервер недоступен", "error");
  }
}

async function doExport() {
  try {
    const r = await apiFetch("/api/export", { method: "POST", headers: {"Content-Type":"application/json"}, body: "{}" });
    notify(`Экспорт создан: ${r.export_id}`, "success");
    await fullRefresh();
  } catch (e) {
    notify("Ошибка экспорта", "error");
  }
}

async function fullRefresh() {
  await Promise.all([loadSnapshot(), loadStatus(), loadTasks(), loadComments(), loadLinks()]);
  renderNeuralCanvas();
  renderActiveTab();
}

// ── Stats bar ──────────────────────────────────────────────────────────────────
function updateStatsBar(status) {
  const c = status.counts || {};
  setText("stat-tasks",    c.tasks    ?? "—");
  setText("stat-comments", c.comments ?? "—");
  setText("stat-links",    c.links    ?? "—");
  setText("stat-receipts", c.receipts ?? "—");
  setText("health-score",  status.health_score || (STATE.snapshot ? STATE.snapshot.health_score : "—"));
  setServerBadge(true);

  // Receipt spark if new receipts
  const newCount = c.receipts || 0;
  if (newCount > STATE.lastReceiptCount && STATE.lastReceiptCount > 0) {
    triggerReceiptSpark();
  }
  STATE.lastReceiptCount = newCount;
}

function setServerBadge(online) {
  const badge = document.getElementById("server-badge");
  const dot   = document.getElementById("live-dot");
  if (online) {
    badge.textContent = "ONLINE";
    badge.className = "badge badge-working";
    dot.className = "live-dot";
  } else {
    badge.textContent = "OFFLINE";
    badge.className = "badge badge-blocked";
    dot.className = "live-dot offline";
  }
}

// ── Utilities ──────────────────────────────────────────────────────────────────
function setText(id, val) {
  const el = document.getElementById(id);
  if (el) el.textContent = val;
}

function esc(s) {
  return String(s ?? "").replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;").replace(/"/g,"&quot;");
}

function notify(msg, type = "info") {
  const box = document.getElementById("notifications");
  const el = document.createElement("div");
  el.className = `notif notif-${type}`;
  el.textContent = msg;
  box.appendChild(el);
  setTimeout(() => el.remove(), 3500);
}

function statusBadgeHtml(status) {
  const cls = {
    WORKING: "badge-working", PARTIAL: "badge-partial",
    BLOCKED: "badge-blocked", MISSING: "badge-missing",
    TASK_ACCEPTED: "badge-working", COMMENT_CAPTURED: "badge-working",
    LINKED: "badge-working", LINK_CREATED: "badge-working",
    NEEDS_INTERPRETATION: "badge-partial", NEEDS_OWNER_CLARIFICATION: "badge-partial"
  }[status] || "badge-no-llm";
  return `<span class="badge ${cls}" style="font-size:0.62rem">${esc(status)}</span>`;
}

function timeAgo(isoStr) {
  if (!isoStr) return "—";
  try {
    const diff = Math.floor((Date.now() - new Date(isoStr).getTime()) / 1000);
    if (diff < 60) return `${diff}s ago`;
    if (diff < 3600) return `${Math.floor(diff/60)}m ago`;
    if (diff < 86400) return `${Math.floor(diff/3600)}h ago`;
    return `${Math.floor(diff/86400)}d ago`;
  } catch { return "—"; }
}

/* ═══════════════════════════════════════════════════════════════
   JS Part 2: Neural Canvas — SVG rendering, zones, strands
   ═══════════════════════════════════════════════════════════════ */

const SVG_NS = "http://www.w3.org/2000/svg";

function svgEl(tag, attrs = {}) {
  const el = document.createElementNS(SVG_NS, tag);
  for (const [k, v] of Object.entries(attrs)) el.setAttribute(k, v);
  return el;
}

function renderNeuralCanvas() {
  const svg = document.getElementById("neural-canvas");
  const W = svg.clientWidth  || svg.parentElement.clientWidth  || 800;
  const H = svg.clientHeight || svg.parentElement.clientHeight || 600;

  svg.setAttribute("viewBox", `0 0 ${W} ${H}`);

  const strandsLayer = document.getElementById("strands-layer");
  const zonesLayer   = document.getElementById("zones-layer");
  strandsLayer.innerHTML = "";
  zonesLayer.innerHTML   = "";

  if (!STATE.snapshot || !STATE.snapshot.zones) {
    renderOfflineState(svg, W, H);
    return;
  }

  const zones = STATE.snapshot.zones;
  const strands = STATE.snapshot.strands || [];

  // Build zone position map
  const posMap = {};
  for (const z of zones) {
    const layout = z.layout || {};
    posMap[z.zone_id] = {
      cx: (layout.x / 100) * W,
      cy: (layout.y / 100) * H,
      r:  layout.r || 28
    };
  }

  // ── Render strands ──────────────────────────────────────────────────────────
  for (const strand of strands) {
    const from = posMap[strand.from];
    const to   = posMap[strand.to];
    if (!from || !to) continue;

    const fromZone = zones.find(z => z.zone_id === strand.from);
    const toZone   = zones.find(z => z.zone_id === strand.to);

    // Determine strand color based on zone health
    let strandColor = "rgba(0,215,255,0.15)";
    let strandClass = "strand-primary";
    if (strand.type === "data") {
      strandColor = "rgba(255,179,71,0.12)";
      strandClass = "strand-data";
    } else if (strand.type === "secondary") {
      strandColor = "rgba(122,132,255,0.1)";
      strandClass = "strand-secondary";
    }

    // Dim strand if either zone is MISSING/BLOCKED
    const fromHealth = fromZone ? fromZone.health : "WORKING";
    const toHealth   = toZone   ? toZone.health   : "WORKING";
    if (fromHealth === "MISSING" || toHealth === "MISSING") {
      strandColor = "rgba(61,90,120,0.08)";
    }

    // Calculate control point for curved strand
    const mx = (from.cx + to.cx) / 2;
    const my = (from.cy + to.cy) / 2;
    const dx = to.cx - from.cx;
    const dy = to.cy - from.cy;
    const len = Math.sqrt(dx*dx + dy*dy);
    const curve = len * 0.15;
    const cpx = mx - (dy / len) * curve;
    const cpy = my + (dx / len) * curve;

    // Start/end points on circle edges
    const angle1 = Math.atan2(to.cy - from.cy, to.cx - from.cx);
    const angle2 = Math.atan2(from.cy - to.cy, from.cx - to.cx);
    const sx = from.cx + Math.cos(angle1) * from.r;
    const sy = from.cy + Math.sin(angle1) * from.r;
    const ex = to.cx   + Math.cos(angle2) * to.r;
    const ey = to.cy   + Math.sin(angle2) * to.r;

    const path = svgEl("path", {
      d: `M ${sx} ${sy} Q ${cpx} ${cpy} ${ex} ${ey}`,
      stroke: strandColor,
      "stroke-width": strand.type === "primary" ? "1.5" : "1",
      fill: "none",
      class: strandClass
    });
    strandsLayer.appendChild(path);
  }

  // ── Render zones ────────────────────────────────────────────────────────────
  for (const zone of zones) {
    const pos = posMap[zone.zone_id];
    if (!pos) continue;

    const color = HEALTH_COLOR[zone.health] || "#3d5a78";
    const token = TOKEN_COLOR[zone.visual_token] || color;
    const pulseClass = HEALTH_PULSE_CLASS[zone.health] || "";
    const icon = ZONE_ICONS[zone.zone_id] || "●";
    const isCore = zone.zone_id === "core_brain";

    const g = svgEl("g", {
      class: "zone-node",
      "data-zone-id": zone.zone_id,
      transform: `translate(0,0)`
    });

    if (isCore) {
      // ── Core brain special rendering ──────────────────────────────────────
      // Outer glow
      const outerGlow = svgEl("circle", {
        cx: pos.cx, cy: pos.cy, r: pos.r + 20,
        fill: "url(#grad-core)",
        class: "core-glow-ring",
        opacity: "0.5"
      });
      g.appendChild(outerGlow);

      // Spinning rings
      const ring1 = svgEl("circle", {
        cx: pos.cx, cy: pos.cy, r: pos.r + 8,
        fill: "none",
        stroke: "rgba(0,215,255,0.25)",
        "stroke-width": "1",
        "stroke-dasharray": "4 6",
        class: "ring-spin-cw"
      });
      const ring2 = svgEl("circle", {
        cx: pos.cx, cy: pos.cy, r: pos.r + 16,
        fill: "none",
        stroke: "rgba(255,79,216,0.15)",
        "stroke-width": "1",
        "stroke-dasharray": "3 8",
        class: "ring-spin-ccw"
      });
      g.appendChild(ring1);
      g.appendChild(ring2);

      // Core fill
      const coreFill = svgEl("circle", {
        cx: pos.cx, cy: pos.cy, r: pos.r,
        fill: "url(#grad-core)",
        stroke: "rgba(0,215,255,0.5)",
        "stroke-width": "1.5",
        filter: "url(#glow-strong)",
        class: "zone-circle"
      });
      g.appendChild(coreFill);

      // Health indicator dots around core
      const healthScore = parseInt((STATE.snapshot.health_score || "0/12").split("/")[0]) || 0;
      for (let i = 0; i < 12; i++) {
        const angle = (i / 12) * Math.PI * 2 - Math.PI / 2;
        const dotR = pos.r + 4;
        const dx = pos.cx + Math.cos(angle) * dotR;
        const dy = pos.cy + Math.sin(angle) * dotR;
        const dotColor = i < healthScore ? "#29c272" : "#1a2d4a";
        const dot = svgEl("circle", {
          cx: dx, cy: dy, r: "3",
          fill: dotColor,
          opacity: i < healthScore ? "0.9" : "0.4"
        });
        g.appendChild(dot);
      }

    } else {
      // ── Regular zone ──────────────────────────────────────────────────────
      // Pulse ring (animated)
      if (pulseClass) {
        const pulseRing = svgEl("circle", {
          cx: pos.cx, cy: pos.cy, r: "0",
          fill: color,
          opacity: "0",
          class: pulseClass
        });
        g.appendChild(pulseRing);
      }

      // Zone fill
      const fill = svgEl("circle", {
        cx: pos.cx, cy: pos.cy, r: pos.r,
        fill: `rgba(${hexToRgb(color)},0.12)`,
        stroke: color,
        "stroke-width": zone.health === "WORKING" ? "1.5" : "1",
        opacity: zone.health === "DISABLED" ? "0.3" : "0.85",
        class: "zone-circle"
      });
      g.appendChild(fill);

      // Status dot (top-right)
      const sdAngle = -Math.PI / 4;
      const sdx = pos.cx + Math.cos(sdAngle) * pos.r;
      const sdy = pos.cy + Math.sin(sdAngle) * pos.r;
      const statusDot = svgEl("circle", {
        cx: sdx, cy: sdy, r: "5",
        fill: color,
        stroke: "#04080f",
        "stroke-width": "1.5",
        class: "zone-status-dot"
      });
      g.appendChild(statusDot);
    }

    // Icon text
    const iconText = svgEl("text", {
      x: pos.cx, y: pos.cy + (isCore ? 6 : 5),
      "text-anchor": "middle",
      "dominant-baseline": "middle",
      "font-size": isCore ? "28" : "18",
      "pointer-events": "none",
      opacity: zone.health === "DISABLED" ? "0.3" : "1"
    });
    iconText.textContent = icon;
    g.appendChild(iconText);

    // Label
    const labelY = pos.cy + pos.r + 16;
    const label = svgEl("text", {
      x: pos.cx, y: labelY,
      class: "zone-label",
      fill: zone.health === "DISABLED" ? "#2a3a50" : color,
      "font-size": isCore ? "11" : "9"
    });
    label.textContent = zone.display_name.toUpperCase().replace(" / ", "/");
    g.appendChild(label);

    // Invisible hit area
    const hitArea = svgEl("circle", {
      cx: pos.cx, cy: pos.cy, r: pos.r + 10,
      fill: "transparent",
      cursor: "pointer"
    });
    hitArea.addEventListener("click",      () => openZoneDetail(zone.zone_id));
    hitArea.addEventListener("mouseenter", (e) => showTooltip(e, zone));
    hitArea.addEventListener("mousemove",  (e) => moveTooltip(e));
    hitArea.addEventListener("mouseleave", ()  => hideTooltip());
    g.appendChild(hitArea);

    zonesLayer.appendChild(g);
  }
}

function hexToRgb(hex) {
  const r = parseInt(hex.slice(1,3),16);
  const g = parseInt(hex.slice(3,5),16);
  const b = parseInt(hex.slice(5,7),16);
  return `${r},${g},${b}`;
}

function renderOfflineState(svg, W, H) {
  const zonesLayer = document.getElementById("zones-layer");
  const text = svgEl("text", {
    x: W/2, y: H/2,
    "text-anchor": "middle",
    fill: "#3d5a78",
    "font-size": "16",
    "font-family": "Segoe UI, sans-serif"
  });
  text.textContent = "Сервер недоступен. Запустите server_v0_5.py";
  zonesLayer.appendChild(text);
}

function triggerReceiptSpark() {
  const svg = document.getElementById("neural-canvas");
  const sparksLayer = document.getElementById("sparks-layer");
  const W = svg.clientWidth || 800;
  const H = svg.clientHeight || 600;
  // Find evidence_receipts zone position
  if (STATE.snapshot && STATE.snapshot.zones) {
    const ez = STATE.snapshot.zones.find(z => z.zone_id === "evidence_receipts");
    if (ez && ez.layout) {
      const cx = (ez.layout.x / 100) * W;
      const cy = (ez.layout.y / 100) * H;
      const spark = svgEl("circle", {
        cx, cy, r: "0",
        fill: "rgba(41,194,114,0.5)",
        stroke: "#29c272",
        "stroke-width": "1",
        class: "receipt-spark"
      });
      sparksLayer.appendChild(spark);
      setTimeout(() => spark.remove(), 700);
    }
  }
}

// ── Resize handler ─────────────────────────────────────────────────────────────
let resizeTimer;
window.addEventListener("resize", () => {
  clearTimeout(resizeTimer);
  resizeTimer = setTimeout(renderNeuralCanvas, 150);
});

/* ═══════════════════════════════════════════════════════════════
   JS Part 3: Tooltip, Zone Detail Panel, Operator Panels
   ═══════════════════════════════════════════════════════════════ */

// ── Tooltip ────────────────────────────────────────────────────────────────────
function showTooltip(e, zone) {
  const tt = document.getElementById("zone-tooltip");
  const title = document.getElementById("tt-title");
  const summary = document.getElementById("tt-summary");
  const telDiv = document.getElementById("tt-telemetry");

  const color = HEALTH_COLOR[zone.health] || "#3d5a78";
  title.style.color = color;
  title.textContent = `${ZONE_ICONS[zone.zone_id] || "●"} ${zone.display_name}`;

  // Build summary from template
  let summaryText = zone.hover_summary_template || "";
  const tel = zone.telemetry || {};
  summaryText = summaryText
    .replace("{task_count}",         tel.task_count ?? "—")
    .replace("{comment_count}",      tel.comment_count ?? "—")
    .replace("{link_count}",         tel.link_count ?? "—")
    .replace("{receipt_count}",      tel.receipt_count ?? "—")
    .replace("{health_score}",       STATE.snapshot ? STATE.snapshot.health_score : "—")
    .replace("{snapshot_age}",       "—")
    .replace("{warning_count}",      STATE.snapshot ? STATE.snapshot.warning_count : "—")
    .replace("{last_task_age}",      tel.last_task_age_seconds ?? "—")
    .replace("{last_task_status}",   "—")
    .replace("{linked_count}",       tel.linked_count ?? "—")
    .replace("{unlinked_count}",     tel.unlinked_count ?? "—")
    .replace("{orphaned_task_count}",tel.orphaned_task_count ?? "—")
    .replace("{orphaned_comment_count}", tel.orphaned_comment_count ?? "—")
    .replace("{last_event_age}",     tel.last_event_age_seconds ?? "—")
    .replace("{export_count}",       tel.export_count ?? "—")
    .replace("{no_llm_rate}",        tel.no_llm_rate ?? "—")
    .replace("{enabled_count}",      tel.enabled_action_count ?? "—")
    .replace("{disabled_count}",     tel.disabled_action_count ?? "—")
    .replace("{last_action_age}",    "—")
    .replace("{exchange_state}",     tel.exchange_state ?? "—")
    .replace("{thread_count}",       tel.thread_count ?? "—")
    .replace("{last_exchange_age}",  "—")
    .replace("{last_verdict}",       tel.last_verdict ?? "—")
    .replace("{last_run_age}",       "—")
    .replace("{smoke_status}",       tel.smoke_status ?? "—")
    .replace("{last_smoke_age}",     "—")
    .replace("{organ_coverage}",     tel.organ_coverage_count ?? "—")
    .replace("{last_export_age}",    "—")
    .replace("{gate_status}",        tel.gate_status ?? "—")
    .replace("{module_count}",       tel.module_count ?? "—")
    .replace("{working_count}",      tel.working_count ?? "—")
    .replace("{blocked_count}",      tel.blocked_count ?? "—");

  summary.textContent = summaryText || `Status: ${zone.health}`;

  // Telemetry chips
  telDiv.innerHTML = "";
  const chips = [
    { label: `Health: ${zone.health}`, cls: zone.health === "WORKING" ? "good" : zone.health === "PARTIAL" ? "warn" : "bad" },
    { label: `Sources: ${zone.source_present_count}/${zone.source_present_count + zone.source_missing_count}`, cls: zone.source_missing_count === 0 ? "good" : "warn" }
  ];
  if (tel.receipt_count !== undefined) chips.push({ label: `Receipts: ${tel.receipt_count}`, cls: "good" });
  if (tel.task_count !== undefined)    chips.push({ label: `Tasks: ${tel.task_count}`, cls: "good" });
  if (tel.comment_count !== undefined) chips.push({ label: `Comments: ${tel.comment_count}`, cls: "good" });
  if (tel.link_count !== undefined)    chips.push({ label: `Links: ${tel.link_count}`, cls: "good" });

  for (const chip of chips) {
    const el = document.createElement("span");
    el.className = `tel-chip ${chip.cls}`;
    el.textContent = chip.label;
    telDiv.appendChild(el);
  }

  tt.classList.add("visible");
  moveTooltip(e);
}

function moveTooltip(e) {
  const tt = document.getElementById("zone-tooltip");
  const x = e.clientX + 16;
  const y = e.clientY - 10;
  const maxX = window.innerWidth  - tt.offsetWidth  - 10;
  const maxY = window.innerHeight - tt.offsetHeight - 10;
  tt.style.left = `${Math.min(x, maxX)}px`;
  tt.style.top  = `${Math.min(y, maxY)}px`;
}

function hideTooltip() {
  document.getElementById("zone-tooltip").classList.remove("visible");
}

// ── Zone Detail Panel ──────────────────────────────────────────────────────────
function openZoneDetail(zoneId) {
  if (!STATE.snapshot) return;
  const zone = STATE.snapshot.zones.find(z => z.zone_id === zoneId);
  if (!zone) return;

  STATE.activeZone = zoneId;
  const color = HEALTH_COLOR[zone.health] || "#3d5a78";
  const icon  = ZONE_ICONS[zoneId] || "●";

  // Header
  const iconEl = document.getElementById("zdp-icon");
  iconEl.textContent = icon;
  iconEl.style.background = `rgba(${hexToRgb(color)},0.15)`;
  iconEl.style.borderColor = `rgba(${hexToRgb(color)},0.4)`;

  document.getElementById("zdp-name").textContent = zone.display_name;
  document.getElementById("zdp-name").style.color = color;
  document.getElementById("zdp-purpose").textContent = zone.honest_limitations ? zone.honest_limitations.join(" | ") : "";

  // Body
  const body = document.getElementById("zdp-body");
  body.innerHTML = buildZoneDetailHtml(zone);

  document.getElementById("zone-detail-panel").classList.add("open");
}

function closeZoneDetail() {
  document.getElementById("zone-detail-panel").classList.remove("open");
  STATE.activeZone = null;
}

function buildZoneDetailHtml(zone) {
  const tel = zone.telemetry || {};
  const color = HEALTH_COLOR[zone.health] || "#3d5a78";
  let html = "";

  // Status card
  html += `<div class="card">
    <div class="card-title">📊 Статус зоны</div>
    <div class="card-row"><span>Health</span><span class="val">${statusBadgeHtml(zone.health)}</span></div>
    <div class="card-row"><span>Capability</span><span class="val">${statusBadgeHtml(zone.capability_state)}</span></div>
    <div class="card-row"><span>Sources present</span><span class="val" style="color:var(--green)">${zone.source_present_count}</span></div>
    <div class="card-row"><span>Sources missing</span><span class="val" style="color:${zone.source_missing_count > 0 ? 'var(--amber)' : 'var(--green)'}">${zone.source_missing_count}</span></div>
  </div>`;

  // Telemetry card
  if (Object.keys(tel).length > 0) {
    html += `<div class="card"><div class="card-title">📡 Telemetry</div>`;
    for (const [k, v] of Object.entries(tel)) {
      html += `<div class="card-row"><span>${esc(k)}</span><span class="val">${esc(String(v))}</span></div>`;
    }
    html += `</div>`;
  }

  // Limitations
  if (zone.honest_limitations && zone.honest_limitations.length > 0) {
    html += `<div class="card"><div class="card-title">⚠️ Ограничения</div>
      <div class="limitations-list">`;
    for (const lim of zone.honest_limitations) {
      html += `<span class="limit-chip">${esc(lim)}</span>`;
    }
    html += `</div></div>`;
  }

  // Missing capabilities
  if (zone.missing_capabilities && zone.missing_capabilities.length > 0) {
    html += `<div class="card"><div class="card-title">🔮 Не реализовано</div>
      <div class="limitations-list">`;
    for (const mc of zone.missing_capabilities) {
      html += `<span class="missing-chip">${esc(mc)}</span>`;
    }
    html += `</div></div>`;
  }

  // Missing sources
  if (zone.missing_sources && zone.missing_sources.length > 0) {
    html += `<div class="card"><div class="card-title" style="color:var(--amber)">⚠️ Отсутствующие источники</div>`;
    for (const ms of zone.missing_sources) {
      html += `<div class="card-row"><span style="font-size:0.7rem;color:var(--amber);word-break:break-all">${esc(ms)}</span></div>`;
    }
    html += `</div>`;
  }

  // Zone-specific action buttons
  html += buildZoneActions(zone.zone_id);

  return html;
}

function buildZoneActions(zoneId) {
  let html = `<div class="card"><div class="card-title">⚡ Действия</div>`;
  if (zoneId === "task_intake") {
    html += `<button class="btn btn-primary btn-full" style="margin-top:8px" onclick="switchTab('tasks');closeZoneDetail()">📋 Открыть Task Intake</button>`;
  } else if (zoneId === "owner_comments") {
    html += `<button class="btn btn-amber btn-full" style="margin-top:8px" onclick="switchTab('comments');closeZoneDetail()">💬 Открыть Comments</button>`;
  } else if (zoneId === "memory_threads") {
    html += `<button class="btn btn-purple btn-full" style="margin-top:8px" onclick="switchTab('links');closeZoneDetail()">🔗 Открыть Links</button>`;
    html += `<button class="btn btn-primary btn-full" style="margin-top:6px" onclick="switchTab('thread');closeZoneDetail()">🧵 Открыть Thread View</button>`;
  } else if (zoneId === "evidence_receipts") {
    html += `<button class="btn btn-success btn-full" style="margin-top:8px" onclick="switchTab('evidence');closeZoneDetail()">🔬 Открыть Evidence</button>`;
    html += `<button class="btn btn-amber btn-full" style="margin-top:6px" onclick="doExport();closeZoneDetail()">📦 Экспорт пакета</button>`;
  } else if (zoneId === "core_brain") {
    html += `<button class="btn btn-primary btn-full" style="margin-top:8px" onclick="rebuildSnapshot();closeZoneDetail()">⚡ Пересобрать Snapshot</button>`;
  } else {
    html += `<div style="color:var(--text-muted);font-size:0.75rem;margin-top:8px">Действия для этой зоны: READ_ONLY</div>`;
  }
  html += `</div>`;
  return html;
}

// ── Tab switching ──────────────────────────────────────────────────────────────
function switchTab(tab) {
  STATE.activeTab = tab;
  document.querySelectorAll(".panel-tab").forEach(t => {
    t.classList.toggle("active", t.dataset.tab === tab);
  });
  renderActiveTab();
}

function renderActiveTab() {
  const content = document.getElementById("panel-content");
  switch (STATE.activeTab) {
    case "tasks":    content.innerHTML = renderTasksTab();    break;
    case "comments": content.innerHTML = renderCommentsTab(); break;
    case "links":    content.innerHTML = renderLinksTab();    break;
    case "thread":   content.innerHTML = renderThreadTab();   break;
    case "evidence": content.innerHTML = renderEvidenceTab(); break;
  }
  // Re-attach form handlers after innerHTML replacement
  attachFormHandlers();
}

/* ═══════════════════════════════════════════════════════════════
   JS Part 4: Tab renderers, Forms, Thread View, Evidence, Init
   ═══════════════════════════════════════════════════════════════ */

// ── Tasks Tab ──────────────────────────────────────────────────────────────────
function renderTasksTab() {
  let html = `<div class="section-header">📋 Новая задача</div>
  <form id="form-task" autocomplete="off">
    <div class="form-group">
      <label>Текст задачи *</label>
      <textarea id="task-source-text" placeholder="Опишите задачу…" required></textarea>
    </div>
    <div class="form-group">
      <label>Цель владельца</label>
      <input id="task-owner-goal" type="text" placeholder="Что должно получиться?">
    </div>
    <div class="form-group">
      <label>Приоритет</label>
      <select id="task-priority">
        <option value="LOW">LOW</option>
        <option value="MEDIUM" selected>MEDIUM</option>
        <option value="HIGH">HIGH</option>
        <option value="CRITICAL">CRITICAL</option>
      </select>
    </div>
    <div class="form-group">
      <label>Теги (через запятую)</label>
      <input id="task-tags" type="text" placeholder="v0.5, neural, …">
    </div>
    <button type="submit" class="btn btn-primary btn-full">⚡ Принять задачу</button>
  </form>
  <div class="section-header" style="margin-top:16px">📋 Принятые задачи (${STATE.tasks.length})</div>
  <div class="item-list" id="tasks-list">`;

  if (STATE.tasks.length === 0) {
    html += `<div class="empty-state"><div class="empty-icon">📋</div>Задач пока нет</div>`;
  } else {
    for (const t of [...STATE.tasks].reverse()) {
      const isSeed = t.seed_demo ? ' <span class="badge badge-no-llm" style="font-size:0.58rem">SEED</span>' : "";
      html += `<div class="item-card">
        <div class="item-id">${esc(t.task_id)}</div>
        <div class="item-text">${esc(t.source_text)}</div>
        <div class="item-meta">
          ${statusBadgeHtml(t.status)}
          <span class="badge badge-no-llm" style="font-size:0.62rem">${esc(t.priority)}</span>
          ${isSeed}
          <span style="font-size:0.65rem;color:var(--text-muted);margin-left:auto">${timeAgo(t.created_at)}</span>
        </div>
        <div style="margin-top:6px">
          <button class="btn btn-primary btn-sm" onclick="loadThreadForTask('${esc(t.task_id)}')">🧵 Thread</button>
        </div>
      </div>`;
    }
  }
  html += `</div>`;
  return html;
}

// ── Comments Tab ───────────────────────────────────────────────────────────────
function renderCommentsTab() {
  let html = `<div class="section-header">💬 Новый комментарий</div>
  <form id="form-comment" autocomplete="off">
    <div class="form-group">
      <label>Текст комментария *</label>
      <textarea id="comment-text" placeholder="Введите Owner-комментарий…" required></textarea>
    </div>
    <div class="form-group">
      <label>Тип комментария</label>
      <select id="comment-type">
        <option value="OBSERVATION" selected>OBSERVATION</option>
        <option value="INSTRUCTION">INSTRUCTION</option>
        <option value="QUESTION">QUESTION</option>
        <option value="FEEDBACK">FEEDBACK</option>
        <option value="BLOCKER">BLOCKER</option>
        <option value="APPROVAL">APPROVAL</option>
      </select>
    </div>
    <div class="form-group">
      <label>Интерпретация (опционально)</label>
      <input id="comment-interpreted" type="text" placeholder="Что означает этот комментарий?">
    </div>
    <button type="submit" class="btn btn-success btn-full">💬 Захватить комментарий</button>
  </form>
  <div class="section-header" style="margin-top:16px">💬 Захваченные комментарии (${STATE.comments.length})</div>
  <div class="item-list">`;

  if (STATE.comments.length === 0) {
    html += `<div class="empty-state"><div class="empty-icon">💬</div>Комментариев пока нет</div>`;
  } else {
    for (const c of [...STATE.comments].reverse()) {
      const isSeed = c.seed_demo ? ' <span class="badge badge-no-llm" style="font-size:0.58rem">SEED</span>' : "";
      html += `<div class="item-card">
        <div class="item-id">${esc(c.comment_id)}</div>
        <div class="item-text">${esc(c.original_text)}</div>
        <div class="item-meta">
          ${statusBadgeHtml(c.status)}
          <span class="badge badge-no-llm" style="font-size:0.62rem">${esc(c.comment_type)}</span>
          ${isSeed}
          <span style="font-size:0.65rem;color:var(--text-muted);margin-left:auto">${timeAgo(c.created_at)}</span>
        </div>
      </div>`;
    }
  }
  html += `</div>`;
  return html;
}

// ── Links Tab ──────────────────────────────────────────────────────────────────
function renderLinksTab() {
  const taskOptions = STATE.tasks.map(t =>
    `<option value="${esc(t.task_id)}">${esc(t.task_id.slice(0,20))} — ${esc(t.source_text.slice(0,30))}</option>`
  ).join("");
  const commentOptions = STATE.comments.map(c =>
    `<option value="${esc(c.comment_id)}">${esc(c.comment_id.slice(0,20))} — ${esc(c.original_text.slice(0,30))}</option>`
  ).join("");

  let html = `<div class="section-header">🔗 Создать связь</div>
  <form id="form-link" autocomplete="off">
    <div class="form-group">
      <label>Задача (source) *</label>
      <select id="link-task-select">
        <option value="">— выберите задачу —</option>
        ${taskOptions}
      </select>
    </div>
    <div class="form-group">
      <label>Комментарий (target) *</label>
      <select id="link-comment-select">
        <option value="">— выберите комментарий —</option>
        ${commentOptions}
      </select>
    </div>
    <div class="form-group">
      <label>Причина связи</label>
      <input id="link-reason" type="text" placeholder="Почему эти объекты связаны?">
    </div>
    <button type="submit" class="btn btn-purple btn-full">🔗 Создать связь</button>
  </form>
  <div class="section-header" style="margin-top:16px">🔗 Активные связи (${STATE.links.length})</div>
  <div class="item-list">`;

  if (STATE.links.length === 0) {
    html += `<div class="empty-state"><div class="empty-icon">🔗</div>Связей пока нет</div>`;
  } else {
    for (const l of [...STATE.links].reverse()) {
      const isSeed = l.seed_demo ? ' <span class="badge badge-no-llm" style="font-size:0.58rem">SEED</span>' : "";
      html += `<div class="item-card">
        <div class="item-id">${esc(l.link_id)}</div>
        <div class="item-text" style="font-size:0.75rem">
          <span style="color:var(--cyan)">${esc(l.source_id.slice(0,24))}</span>
          <span style="color:var(--text-muted)"> → </span>
          <span style="color:var(--amber)">${esc(l.target_id.slice(0,24))}</span>
        </div>
        <div class="item-meta">
          ${statusBadgeHtml(l.status)}
          ${isSeed}
          <span style="font-size:0.65rem;color:var(--text-muted);margin-left:auto">${timeAgo(l.created_at)}</span>
        </div>
        ${l.link_reason ? `<div style="font-size:0.72rem;color:var(--text-dim);margin-top:4px">${esc(l.link_reason)}</div>` : ""}
      </div>`;
    }
  }
  html += `</div>`;
  return html;
}

// ── Thread Tab ─────────────────────────────────────────────────────────────────
function renderThreadTab() {
  const taskOptions = STATE.tasks.map(t =>
    `<option value="${esc(t.task_id)}">${esc(t.task_id.slice(0,20))} — ${esc(t.source_text.slice(0,35))}</option>`
  ).join("");

  let html = `<div class="section-header">🧵 Memory Thread View</div>
  <div style="display:flex;gap:8px;margin-bottom:14px;align-items:flex-end">
    <div class="form-group" style="flex:1;margin-bottom:0">
      <label>Выберите задачу</label>
      <select id="thread-task-select">
        <option value="">— выберите задачу —</option>
        ${taskOptions}
      </select>
    </div>
    <button class="btn btn-primary" onclick="loadThreadFromSelect()">🧵 Загрузить</button>
  </div>
  <div id="thread-content">
    <div class="empty-state"><div class="empty-icon">🧵</div>Выберите задачу для просмотра memory thread</div>
  </div>`;
  return html;
}

async function loadThreadForTask(taskId) {
  switchTab("thread");
  setTimeout(async () => {
    const sel = document.getElementById("thread-task-select");
    if (sel) sel.value = taskId;
    await renderThread(taskId);
  }, 50);
}

async function loadThreadFromSelect() {
  const sel = document.getElementById("thread-task-select");
  if (!sel || !sel.value) { notify("Выберите задачу", "warn"); return; }
  await renderThread(sel.value);
}

async function renderThread(taskId) {
  const content = document.getElementById("thread-content");
  if (!content) return;
  content.innerHTML = `<div class="empty-state">Загрузка…</div>`;
  try {
    const data = await apiFetch(`/api/thread/${encodeURIComponent(taskId)}`);
    const t = data.task;
    let html = `<div class="thread-task-card">
      <div style="font-size:0.65rem;color:var(--text-muted);margin-bottom:4px">${esc(t.task_id)}</div>
      <div style="font-size:0.85rem;font-weight:600;margin-bottom:6px">${esc(t.source_text)}</div>
      <div class="item-meta">
        ${statusBadgeHtml(t.status)}
        <span class="badge badge-no-llm" style="font-size:0.62rem">${esc(t.priority)}</span>
        <span style="font-size:0.65rem;color:var(--text-muted);margin-left:auto">${timeAgo(t.created_at)}</span>
      </div>
      ${t.owner_goal ? `<div style="font-size:0.75rem;color:var(--text-dim);margin-top:6px">Цель: ${esc(t.owner_goal)}</div>` : ""}
    </div>`;

    if (data.comments && data.comments.length > 0) {
      html += `<div style="font-size:0.7rem;color:var(--text-dim);margin-bottom:8px;letter-spacing:0.06em">LINKED COMMENTS (${data.comments.length})</div>`;
      for (const c of data.comments) {
        html += `<div class="thread-comment-card">
          <div style="font-size:0.65rem;color:var(--text-muted);margin-bottom:3px">${esc(c.comment_id)}</div>
          <div style="font-size:0.8rem;margin-bottom:5px">${esc(c.original_text)}</div>
          <div class="item-meta">
            ${statusBadgeHtml(c.status)}
            <span class="badge badge-no-llm" style="font-size:0.62rem">${esc(c.comment_type)}</span>
          </div>
        </div>`;
      }
    } else {
      html += `<div class="empty-state" style="padding:12px"><div class="empty-icon" style="font-size:1.2rem">🔗</div>Нет связанных комментариев</div>`;
    }

    if (data.receipts && data.receipts.length > 0) {
      html += `<div style="font-size:0.7rem;color:var(--text-dim);margin:10px 0 6px;letter-spacing:0.06em">RECEIPTS (${data.receipts.length})</div>`;
      for (const r of data.receipts) {
        html += `<div class="item-card" style="padding:8px 10px">
          <div style="font-size:0.65rem;color:var(--text-muted)">${esc(r.receipt_id)} · ${esc(r.event_type)}</div>
          <div style="font-size:0.7rem;color:var(--green);margin-top:2px">no_llm_used: ${r.no_llm_used}</div>
        </div>`;
      }
    }

    content.innerHTML = html;
  } catch (e) {
    content.innerHTML = `<div class="empty-state"><div class="empty-icon">⚠️</div>${esc(e.message)}</div>`;
  }
}

// ── Evidence Tab ───────────────────────────────────────────────────────────────
function renderEvidenceTab() {
  const snap = STATE.snapshot;
  let html = `<div class="section-header">🔬 Evidence Panel</div>`;

  if (snap) {
    html += `<div class="card">
      <div class="card-title">📊 Snapshot</div>
      <div class="card-row"><span>ID</span><span class="val" style="font-size:0.7rem">${esc(snap.snapshot_id || "—")}</span></div>
      <div class="card-row"><span>Timestamp</span><span class="val">${esc(snap.timestamp_utc || "—")}</span></div>
      <div class="card-row"><span>Health</span><span class="val" style="color:var(--green)">${esc(snap.health_score || "—")}</span></div>
      <div class="card-row"><span>Warnings</span><span class="val" style="color:var(--amber)">${snap.warning_count ?? "—"}</span></div>
      <div class="card-row"><span>Missing sources</span><span class="val">${snap.total_missing_sources ?? "—"}</span></div>
      <div class="card-row"><span>Runtime mode</span><span class="val">${esc(snap.runtime_mode || "—")}</span></div>
      <div class="card-row"><span>no_local_llm</span><span class="val" style="color:var(--green)">${snap.no_local_llm}</span></div>
      <div class="card-row"><span>no_agent_api</span><span class="val" style="color:var(--green)">${snap.no_agent_api}</span></div>
    </div>`;

    // Zone health summary
    html += `<div class="card"><div class="card-title">🧠 Зоны</div>`;
    for (const z of (snap.zones || [])) {
      const color = HEALTH_COLOR[z.health] || "#3d5a78";
      html += `<div class="card-row">
        <span>${ZONE_ICONS[z.zone_id] || "●"} ${esc(z.display_name)}</span>
        <span class="val" style="color:${color}">${esc(z.health)}</span>
      </div>`;
    }
    html += `</div>`;
  }

  html += `<div class="card">
    <div class="card-title">📁 Пути</div>
    <div class="card-row"><span>Tasks</span><span class="val" style="font-size:0.65rem;word-break:break-all">MEMORY_ZONES/TASK_INTAKE/accepted_tasks.json</span></div>
    <div class="card-row"><span>Comments</span><span class="val" style="font-size:0.65rem;word-break:break-all">MEMORY_ZONES/OWNER_COMMENTS/owner_comments_runtime.json</span></div>
    <div class="card-row"><span>Links</span><span class="val" style="font-size:0.65rem;word-break:break-all">MEMORY_ZONES/MEMORY_LINKS/task_comment_links.json</span></div>
    <div class="card-row"><span>Receipts</span><span class="val" style="font-size:0.65rem">RUNTIME/receipts/</span></div>
    <div class="card-row"><span>Exports</span><span class="val" style="font-size:0.65rem">RUNTIME/exports/</span></div>
    <div class="card-row"><span>Checker report</span><span class="val" style="font-size:0.65rem">NEURAL_BASE_V0_5/reports/check_report_v0_5.json</span></div>
  </div>`;

  html += `<button class="btn btn-amber btn-full" style="margin-top:8px" onclick="doExport()">📦 Создать экспорт пакета</button>`;
  html += `<button class="btn btn-primary btn-full" style="margin-top:6px" onclick="rebuildSnapshot()">⚡ Пересобрать Snapshot</button>`;

  return html;
}

// ── Form handlers ──────────────────────────────────────────────────────────────
function attachFormHandlers() {
  const formTask = document.getElementById("form-task");
  if (formTask) {
    formTask.onsubmit = async (e) => {
      e.preventDefault();
      const body = {
        source_text: document.getElementById("task-source-text").value.trim(),
        owner_goal:  document.getElementById("task-owner-goal").value.trim() || null,
        priority:    document.getElementById("task-priority").value,
        tags:        document.getElementById("task-tags").value.split(",").map(s=>s.trim()).filter(Boolean)
      };
      try {
        await apiFetch("/api/tasks", { method:"POST", headers:{"Content-Type":"application/json"}, body: JSON.stringify(body) });
        notify("Задача принята ✓", "success");
        formTask.reset();
        await fullRefresh();
      } catch (err) {
        notify("Ошибка: " + err.message, "error");
      }
    };
  }

  const formComment = document.getElementById("form-comment");
  if (formComment) {
    formComment.onsubmit = async (e) => {
      e.preventDefault();
      const body = {
        original_text:      document.getElementById("comment-text").value.trim(),
        comment_type:       document.getElementById("comment-type").value,
        interpreted_meaning:document.getElementById("comment-interpreted").value.trim() || null
      };
      try {
        await apiFetch("/api/comments", { method:"POST", headers:{"Content-Type":"application/json"}, body: JSON.stringify(body) });
        notify("Комментарий захвачен ✓", "success");
        formComment.reset();
        await fullRefresh();
      } catch (err) {
        notify("Ошибка: " + err.message, "error");
      }
    };
  }

  const formLink = document.getElementById("form-link");
  if (formLink) {
    formLink.onsubmit = async (e) => {
      e.preventDefault();
      const source_id = document.getElementById("link-task-select").value;
      const target_id = document.getElementById("link-comment-select").value;
      if (!source_id || !target_id) { notify("Выберите задачу и комментарий", "warn"); return; }
      const body = {
        source_id, target_id,
        source_type: "TASK", target_type: "COMMENT",
        link_reason: document.getElementById("link-reason").value.trim() || null
      };
      try {
        await apiFetch("/api/links", { method:"POST", headers:{"Content-Type":"application/json"}, body: JSON.stringify(body) });
        notify("Связь создана ✓", "success");
        formLink.reset();
        await fullRefresh();
      } catch (err) {
        notify("Ошибка: " + err.message, "error");
      }
    };
  }
}

// ── Init ───────────────────────────────────────────────────────────────────────
async function init() {
  // Initial load
  await fullRefresh();
  renderActiveTab();

  // Auto-refresh every 15 seconds
  setInterval(async () => {
    await loadStatus();
    await loadTasks();
    await loadComments();
    await loadLinks();
    renderActiveTab();
  }, 15000);

  // Snapshot refresh every 60 seconds
  setInterval(async () => {
    await loadSnapshot();
    renderNeuralCanvas();
  }, 60000);
}

document.addEventListener("DOMContentLoaded", init);

