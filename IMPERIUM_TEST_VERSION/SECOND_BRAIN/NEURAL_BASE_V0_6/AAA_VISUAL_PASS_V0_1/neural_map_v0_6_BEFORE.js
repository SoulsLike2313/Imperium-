/* ═══════════════════════════════════════════════════════════════
   Second Brain Neural Map V0.6 — JS Part 1: State, API, Utils
   PROTOTYPE_INTERACTIVE | RULE_BASED_ONLY | NO_LOCAL_LLM
   ═══════════════════════════════════════════════════════════════ */
"use strict";

// ── State ──────────────────────────────────────────────────────────────────────
const STATE = {
  snapshot: null,
  status: null,
  tasks: [],
  comments: [],
  links: [],
  receiptsStatus: null,
  exportStatus: null,
  taskPackages: null,
  activeTab: "tasks",
  activeZone: null,
  corridorOpen: false,
  corridorStage: 0,
  corridorData: {},       // form data accumulated across stages
  corridorResult: null,   // result from /api/tasks/register
  launchResult: null,     // result from /api/tasks/launch
  serverOnline: false,
  lastReceiptCount: 0,
  lastPackageCount: 0
};

// ── Color maps ─────────────────────────────────────────────────────────────────
const TOKEN_COLOR = {
  accent_cyan:    "#00d7ff",
  accent_amber:   "#ffb347",
  accent_magenta: "#ff4fd8",
  accent_green:   "#29c272",
  accent_red:     "#ff5d66",
  accent_violet:  "#7a84ff",
  text_muted:     "#2e4a68"
};

const HEALTH_COLOR = {
  WORKING:      "#00d7ff",
  PARTIAL:      "#ffb347",
  BLOCKED:      "#ff5d66",
  MISSING:      "#2e4a68",
  DISABLED:     "#1e3352",
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

const GLOW_FILTER = {
  "#00d7ff": "url(#glow-cyan)",
  "#ffb347": "url(#glow-amber)",
  "#ff4fd8": "url(#glow-magenta)",
  "#29c272": "url(#glow-green)",
  "#7a84ff": "url(#glow-violet)",
  "#ff5d66": "url(#glow-cyan)"
};

// ── API ────────────────────────────────────────────────────────────────────────
async function apiFetch(path, options = {}) {
  const res = await fetch(path, { cache: "no-store", ...options });
  if (!res.ok) throw new Error(`HTTP ${res.status} ${path}`);
  return res.json();
}

async function loadSnapshot() {
  try { STATE.snapshot = await apiFetch("/api/snapshot"); return STATE.snapshot; }
  catch (e) { console.warn("Snapshot:", e.message); return null; }
}

async function loadStatus() {
  try {
    const s = await apiFetch("/api/status");
    STATE.status = s; STATE.serverOnline = true;
    updateStatsBar(s); return s;
  } catch (e) {
    STATE.status = null; STATE.serverOnline = false;
    setServerBadge(false); return null;
  }
}

async function loadTasks()    { try { STATE.tasks    = await apiFetch("/api/tasks");    } catch { STATE.tasks = []; } }
async function loadComments() { try { STATE.comments = await apiFetch("/api/comments"); } catch { STATE.comments = []; } }
async function loadLinks()    { try { STATE.links    = await apiFetch("/api/links");    } catch { STATE.links = []; } }

async function loadReceiptsStatus() {
  try { STATE.receiptsStatus = await apiFetch("/api/receipts"); } catch { STATE.receiptsStatus = null; }
}

async function loadExportStatus() {
  try { STATE.exportStatus = await apiFetch("/api/export/status"); } catch { STATE.exportStatus = null; }
}

async function loadTaskPackages() {
  try { STATE.taskPackages = await apiFetch("/api/task_packages"); } catch { STATE.taskPackages = null; }
}

async function fullRefresh() {
  await Promise.all([
    loadSnapshot(), loadStatus(), loadTasks(), loadComments(),
    loadLinks(), loadReceiptsStatus(), loadExportStatus(), loadTaskPackages()
  ]);
  renderNeuralCanvas();
  renderActiveTab();
}

async function rebuildSnapshot() {
  notify("Rebuilding snapshot…", "info");
  try {
    const r = await apiFetch("/api/rebuild_snapshot", { method: "POST", headers: {"Content-Type":"application/json"}, body: "{}" });
    if (r.status === "REBUILT") { notify("Snapshot rebuilt", "success"); await fullRefresh(); }
    else notify("Snapshot rebuild failed", "error");
  } catch { notify("Server unavailable", "error"); }
}

async function doExport() {
  try {
    const r = await apiFetch("/api/export", { method: "POST", headers: {"Content-Type":"application/json"}, body: "{}" });
    notify(`Export created: ${r.export_id}`, "success");
    await fullRefresh();
  } catch { notify("Export failed", "error"); }
}

// ── Stats bar ──────────────────────────────────────────────────────────────────
function updateStatsBar(status) {
  const c = status.counts || {};
  setText("stat-tasks",         c.tasks         ?? "—");
  setText("stat-task-packages", c.task_packages  ?? "—");
  setText("stat-comments",      c.comments       ?? "—");
  setText("stat-links",         c.links          ?? "—");
  setText("stat-receipts",      c.receipts       ?? "—");
  setText("health-score", status.health_score || (STATE.snapshot ? STATE.snapshot.health_score : "—"));
  setServerBadge(true);
  updateTruthLockBar(status);
  updateHonestyBadges(status);

  // Sparks on new receipts
  const newRcp = c.receipts || 0;
  if (newRcp > STATE.lastReceiptCount && STATE.lastReceiptCount > 0) triggerReceiptSpark();
  STATE.lastReceiptCount = newRcp;

  // Particle on new package
  const newPkg = c.task_packages || 0;
  if (newPkg > STATE.lastPackageCount && STATE.lastPackageCount > 0) {
    triggerParticle("task_intake", "core_brain", "#00d7ff");
    triggerParticle("task_intake", "evidence_receipts", "#29c272");
  }
  STATE.lastPackageCount = newPkg;
}

function updateTruthLockBar(status) {
  const snap = STATE.snapshot || {};
  setText("stat-partial",    status.partial_count        ?? snap.partial_count        ?? "—");
  setText("stat-blocked",    status.blocked_count        ?? snap.blocked_count        ?? "—");
  setText("stat-missing",    status.missing_source_count ?? snap.total_missing_sources ?? "—");
  setText("stat-warnings",   status.warning_count        ?? snap.warning_count        ?? "—");
  setText("stat-stale",      status.stale_count          ?? snap.stale_count          ?? "—");
  const freshness = status.snapshot_freshness_state ?? snap.snapshot_freshness_state ?? "—";
  const freshnessEl = document.getElementById("snapshot-freshness");
  if (freshnessEl) { freshnessEl.textContent = freshness; freshnessEl.dataset.state = freshness; }
  setText("snapshot-id",      status.snapshot_id        ?? snap.snapshot_id        ?? "—");
  setText("truth-lock-run-id", status.truth_lock_run_id ?? snap.truth_lock_run_id  ?? "—");
  setText("snapshot-ts",      status.snapshot_timestamp ?? snap.timestamp_utc      ?? "—");
  setText("snapshot-age-sec", status.snapshot_age_seconds ?? snap.snapshot_age_seconds ?? "—");
}

function updateHonestyBadges(status) {
  const set = (id, v) => { const el = document.getElementById(id); if (el) el.textContent = v; };
  set("badge-runtime-mode",  status.mode || "PROTOTYPE_INTERACTIVE");
  set("badge-rule-based",    status.rule_based    ? "RULE_BASED_ONLY"   : "RULE_BASED_FALSE");
  set("badge-no-llm",        status.no_local_llm  ? "NO_LOCAL_LLM"      : "LOCAL_LLM_UNKNOWN");
  set("badge-no-agent",      status.no_agent_api  ? "NO_AGENT_API"      : "AGENT_API_UNKNOWN");
  set("badge-not-production",status.not_production_ready ? "NOT_RELEASE_READY" : "RELEASE_STATE_UNKNOWN");
}

function setServerBadge(online) {
  const badge = document.getElementById("server-badge");
  const dot   = document.getElementById("live-dot");
  if (online) {
    badge.textContent = "ONLINE"; badge.className = "badge badge-working";
    dot.className = "live-dot";
  } else {
    badge.textContent = "OFFLINE"; badge.className = "badge badge-blocked";
    dot.className = "live-dot offline";
  }
}

// ── Utilities ──────────────────────────────────────────────────────────────────
function setText(id, val) { const el = document.getElementById(id); if (el) el.textContent = val; }

function esc(s) {
  return String(s ?? "").replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;").replace(/"/g,"&quot;");
}

function sanitizePlaceholders(text) {
  return String(text || "").replace(/\{[a-zA-Z0-9_]+\}/g, "UNAVAILABLE");
}

function notify(msg, type = "info") {
  const box = document.getElementById("notifications");
  const el = document.createElement("div");
  el.className = `notif notif-${type}`;
  el.textContent = msg;
  box.appendChild(el);
  setTimeout(() => el.remove(), 3800);
}

function statusBadgeHtml(status) {
  const cls = {
    WORKING: "badge-working", PARTIAL: "badge-partial",
    BLOCKED: "badge-blocked", MISSING: "badge-missing",
    TASK_ACCEPTED: "badge-working", TASK_REGISTERED: "badge-working",
    TASK_READY_FOR_SERVITOR: "badge-launch",
    COMMENT_CAPTURED: "badge-working", LINKED: "badge-working",
    LINK_CREATED: "badge-working",
    NEEDS_INTERPRETATION: "badge-partial"
  }[status] || "badge-dim";
  return `<span class="badge ${cls}" style="font-size:0.6rem">${esc(status)}</span>`;
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

function hexToRgb(hex) {
  const r = parseInt(hex.slice(1,3),16);
  const g = parseInt(hex.slice(3,5),16);
  const b = parseInt(hex.slice(5,7),16);
  return `${r},${g},${b}`;
}


/* ═══════════════════════════════════════════════════════════════
   JS Part 2: Neural Canvas — SVG rendering, zones, strands, particles
   ═══════════════════════════════════════════════════════════════ */

const SVG_NS = "http://www.w3.org/2000/svg";

function svgEl(tag, attrs = {}) {
  const el = document.createElementNS(SVG_NS, tag);
  for (const [k, v] of Object.entries(attrs)) el.setAttribute(k, v);
  return el;
}

// Zone position cache for particle travel
const ZONE_POS_CACHE = {};

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
    renderOfflineState(svg, W, H); return;
  }

  const zones   = STATE.snapshot.zones;
  const strands = STATE.snapshot.strands || [];

  // Build position map
  for (const z of zones) {
    const layout = z.layout || {};
    ZONE_POS_CACHE[z.zone_id] = {
      cx: (layout.x / 100) * W,
      cy: (layout.y / 100) * H,
      r:  layout.r || 28
    };
  }

  // ── Render strands ──────────────────────────────────────────────────────────
  for (const strand of strands) {
    const from = ZONE_POS_CACHE[strand.from];
    const to   = ZONE_POS_CACHE[strand.to];
    if (!from || !to) continue;

    const fromZone = zones.find(z => z.zone_id === strand.from);
    const toZone   = zones.find(z => z.zone_id === strand.to);

    let strandColor = "rgba(0,215,255,0.12)";
    let strandClass = "strand-primary";
    let strokeW = "1.5";

    if (strand.type === "data") {
      strandColor = "rgba(255,179,71,0.1)"; strandClass = "strand-data"; strokeW = "1";
    } else if (strand.type === "secondary") {
      strandColor = "rgba(122,132,255,0.08)"; strandClass = "strand-secondary"; strokeW = "0.8";
    }

    const fromHealth = fromZone ? fromZone.health : "WORKING";
    const toHealth   = toZone   ? toZone.health   : "WORKING";
    if (fromHealth === "MISSING" || toHealth === "MISSING") {
      strandColor = "rgba(46,74,104,0.06)";
    }

    // Active corridor zone — brighten connected strands
    if (STATE.corridorOpen && STATE.activeZone &&
        (strand.from === STATE.activeZone || strand.to === STATE.activeZone)) {
      strandColor = strandColor.replace(/[\d.]+\)$/, "0.45)");
      strokeW = String(parseFloat(strokeW) + 0.5);
    }

    const mx = (from.cx + to.cx) / 2;
    const my = (from.cy + to.cy) / 2;
    const dx = to.cx - from.cx;
    const dy = to.cy - from.cy;
    const len = Math.sqrt(dx*dx + dy*dy);
    const curve = len * 0.14;
    const cpx = mx - (dy / len) * curve;
    const cpy = my + (dx / len) * curve;

    const angle1 = Math.atan2(to.cy - from.cy, to.cx - from.cx);
    const angle2 = Math.atan2(from.cy - to.cy, from.cx - to.cx);
    const sx = from.cx + Math.cos(angle1) * from.r;
    const sy = from.cy + Math.sin(angle1) * from.r;
    const ex = to.cx   + Math.cos(angle2) * to.r;
    const ey = to.cy   + Math.sin(angle2) * to.r;

    const path = svgEl("path", {
      d: `M ${sx} ${sy} Q ${cpx} ${cpy} ${ex} ${ey}`,
      stroke: strandColor, "stroke-width": strokeW,
      fill: "none", class: strandClass,
      "data-from": strand.from, "data-to": strand.to
    });
    strandsLayer.appendChild(path);
  }

  // ── Render zones ────────────────────────────────────────────────────────────
  for (const zone of zones) {
    const pos = ZONE_POS_CACHE[zone.zone_id];
    if (!pos) continue;

    const color = HEALTH_COLOR[zone.health] || "#2e4a68";
    const pulseClass = HEALTH_PULSE_CLASS[zone.health] || "";
    const icon = ZONE_ICONS[zone.zone_id] || "●";
    const isCore = zone.zone_id === "core_brain";
    const isActive = STATE.corridorOpen && STATE.activeZone === zone.zone_id;
    const glowFilter = GLOW_FILTER[color] || "url(#glow-cyan)";

    const g = svgEl("g", {
      class: "zone-node",
      "data-zone-id": zone.zone_id
    });

    if (isCore) {
      // ── Core Brain — premium rendering ────────────────────────────────────
      // Outer nebula halo
      const halo = svgEl("circle", {
        cx: pos.cx, cy: pos.cy, r: pos.r + 40,
        fill: "url(#grad-core-halo)",
        class: "core-halo"
      });
      g.appendChild(halo);

      // Hex pattern fill (inner detail)
      const hexFill = svgEl("circle", {
        cx: pos.cx, cy: pos.cy, r: pos.r - 4,
        fill: "url(#hex-pattern)", opacity: "0.6"
      });
      g.appendChild(hexFill);

      // Outer glow ring
      const outerGlow = svgEl("circle", {
        cx: pos.cx, cy: pos.cy, r: pos.r + 18,
        fill: "url(#grad-core)",
        class: "core-glow-ring"
      });
      g.appendChild(outerGlow);

      // Slow outer ring
      const ring0 = svgEl("circle", {
        cx: pos.cx, cy: pos.cy, r: pos.r + 26,
        fill: "none", stroke: "rgba(122,132,255,0.08)",
        "stroke-width": "1", "stroke-dasharray": "2 12",
        class: "ring-spin-slow"
      });
      g.appendChild(ring0);

      // Spinning rings
      const ring1 = svgEl("circle", {
        cx: pos.cx, cy: pos.cy, r: pos.r + 10,
        fill: "none", stroke: "rgba(0,215,255,0.3)",
        "stroke-width": "1", "stroke-dasharray": "5 7",
        class: "ring-spin-cw"
      });
      const ring2 = svgEl("circle", {
        cx: pos.cx, cy: pos.cy, r: pos.r + 18,
        fill: "none", stroke: "rgba(255,79,216,0.18)",
        "stroke-width": "1", "stroke-dasharray": "3 9",
        class: "ring-spin-ccw"
      });
      g.appendChild(ring1);
      g.appendChild(ring2);

      // Core fill
      const coreFill = svgEl("circle", {
        cx: pos.cx, cy: pos.cy, r: pos.r,
        fill: "url(#grad-core)",
        stroke: "rgba(0,215,255,0.55)", "stroke-width": "1.5",
        filter: "url(#glow-strong)",
        class: "zone-body"
      });
      g.appendChild(coreFill);

      // Health dots
      const healthScore = parseInt((STATE.snapshot.health_score || "0/12").split("/")[0]) || 0;
      for (let i = 0; i < 12; i++) {
        const angle = (i / 12) * Math.PI * 2 - Math.PI / 2;
        const dotR = pos.r + 5;
        const dx = pos.cx + Math.cos(angle) * dotR;
        const dy = pos.cy + Math.sin(angle) * dotR;
        const dotColor = i < healthScore ? "#29c272" : "#152238";
        const dot = svgEl("circle", {
          cx: dx, cy: dy, r: "3.5",
          fill: dotColor,
          opacity: i < healthScore ? "1" : "0.5",
          filter: i < healthScore ? "url(#glow-green)" : ""
        });
        g.appendChild(dot);
      }

    } else {
      // ── Regular zone — premium rendering ──────────────────────────────────

      // Outer glow halo (very subtle)
      const halo = svgEl("circle", {
        cx: pos.cx, cy: pos.cy, r: pos.r + 14,
        fill: `rgba(${hexToRgb(color)},0.04)`,
        opacity: zone.health === "DISABLED" ? "0" : "1"
      });
      g.appendChild(halo);

      // Pulse ring
      if (pulseClass) {
        const pulseRing = svgEl("circle", {
          cx: pos.cx, cy: pos.cy, r: "0",
          fill: color, opacity: "0", class: pulseClass
        });
        g.appendChild(pulseRing);
      }

      // Active corridor ring
      if (isActive) {
        const activeRing = svgEl("circle", {
          cx: pos.cx, cy: pos.cy, r: pos.r + 6,
          fill: "none", stroke: color, "stroke-width": "2",
          "stroke-dasharray": "4 4",
          class: "zone-active-ring",
          filter: glowFilter
        });
        g.appendChild(activeRing);
      }

      // Zone body — radial gradient fill
      const gradId = {
        "#00d7ff": "grad-cyan", "#ffb347": "grad-amber",
        "#ff4fd8": "grad-magenta", "#29c272": "grad-green",
        "#7a84ff": "grad-violet", "#ff5d66": "grad-red"
      }[color] || "grad-cyan";

      // Inner fill with gradient
      const innerFill = svgEl("circle", {
        cx: pos.cx, cy: pos.cy, r: pos.r - 2,
        fill: `url(#${gradId})`,
        opacity: zone.health === "DISABLED" ? "0.15" : "0.35"
      });
      g.appendChild(innerFill);

      // Zone border circle
      const border = svgEl("circle", {
        cx: pos.cx, cy: pos.cy, r: pos.r,
        fill: `rgba(${hexToRgb(color)},0.08)`,
        stroke: color,
        "stroke-width": zone.health === "WORKING" ? "1.8" : "1",
        opacity: zone.health === "DISABLED" ? "0.25" : "0.9",
        filter: isActive ? glowFilter : "",
        class: "zone-body"
      });
      g.appendChild(border);

      // Inner detail ring (thin)
      const innerRing = svgEl("circle", {
        cx: pos.cx, cy: pos.cy, r: pos.r - 6,
        fill: "none", stroke: `rgba(${hexToRgb(color)},0.2)`,
        "stroke-width": "0.5",
        opacity: zone.health === "DISABLED" ? "0" : "0.7"
      });
      g.appendChild(innerRing);

      // Status dot (top-right)
      const sdAngle = -Math.PI / 4;
      const sdx = pos.cx + Math.cos(sdAngle) * pos.r;
      const sdy = pos.cy + Math.sin(sdAngle) * pos.r;
      const statusDot = svgEl("circle", {
        cx: sdx, cy: sdy, r: "4.5",
        fill: color, stroke: "#03060d", "stroke-width": "1.5",
        filter: glowFilter
      });
      g.appendChild(statusDot);
    }

    // Icon
    const iconText = svgEl("text", {
      x: pos.cx, y: pos.cy + (isCore ? 7 : 5),
      "text-anchor": "middle", "dominant-baseline": "middle",
      "font-size": isCore ? "30" : "17",
      "pointer-events": "none",
      opacity: zone.health === "DISABLED" ? "0.25" : "1"
    });
    iconText.textContent = icon;
    g.appendChild(iconText);

    // Label
    const labelY = pos.cy + pos.r + 15;
    const label = svgEl("text", {
      x: pos.cx, y: labelY,
      class: "zone-label",
      fill: zone.health === "DISABLED" ? "#1e3352" : color,
      "font-size": isCore ? "10" : "8.5",
      opacity: "0.85"
    });
    label.textContent = zone.display_name.toUpperCase().replace(" / ", "/");
    g.appendChild(label);

    // Hit area
    const hitArea = svgEl("circle", {
      cx: pos.cx, cy: pos.cy, r: pos.r + 12,
      fill: "transparent", cursor: "pointer"
    });
    hitArea.addEventListener("click",      () => handleZoneClick(zone.zone_id, zone));
    hitArea.addEventListener("mouseenter", (e) => showTooltip(e, zone));
    hitArea.addEventListener("mousemove",  (e) => moveTooltip(e));
    hitArea.addEventListener("mouseleave", ()  => hideTooltip());
    g.appendChild(hitArea);

    zonesLayer.appendChild(g);
  }
}

function handleZoneClick(zoneId, zone) {
  // Task intake → open corridor
  if (zoneId === "task_intake") {
    openCorridor(zoneId);
    return;
  }
  // Others → zone detail
  openZoneDetail(zoneId);
}

function renderOfflineState(svg, W, H) {
  const zonesLayer = document.getElementById("zones-layer");
  const text = svgEl("text", {
    x: W/2, y: H/2, "text-anchor": "middle",
    fill: "#2e4a68", "font-size": "15",
    "font-family": "Segoe UI, sans-serif"
  });
  text.textContent = "Server unavailable. Run server_v0_6.py";
  zonesLayer.appendChild(text);
}

// ── Particle travel ────────────────────────────────────────────────────────────
function triggerParticle(fromZoneId, toZoneId, color) {
  const from = ZONE_POS_CACHE[fromZoneId];
  const to   = ZONE_POS_CACHE[toZoneId];
  if (!from || !to) return;

  const particlesLayer = document.getElementById("particles-layer");
  const dur = 0.85;

  // Build quadratic bezier path
  const mx = (from.cx + to.cx) / 2;
  const my = (from.cy + to.cy) / 2;
  const dx = to.cx - from.cx;
  const dy = to.cy - from.cy;
  const len = Math.sqrt(dx*dx + dy*dy);
  const curve = len * 0.14;
  const cpx = mx - (dy / len) * curve;
  const cpy = my + (dx / len) * curve;

  const pathEl = svgEl("path", {
    d: `M ${from.cx} ${from.cy} Q ${cpx} ${cpy} ${to.cx} ${to.cy}`,
    fill: "none", stroke: "none"
  });
  particlesLayer.appendChild(pathEl);

  const particle = svgEl("circle", {
    r: "3.5", fill: color,
    filter: GLOW_FILTER[color] || "url(#glow-cyan)",
    opacity: "0"
  });
  particlesLayer.appendChild(particle);

  // Animate along path using requestAnimationFrame
  const startTime = performance.now();
  const totalMs = dur * 1000;
  const pathLen = pathEl.getTotalLength ? pathEl.getTotalLength() : len;

  function animateParticle(now) {
    const t = Math.min((now - startTime) / totalMs, 1);
    const eased = t < 0.5 ? 2*t*t : -1+(4-2*t)*t; // ease-in-out
    const pt = pathEl.getPointAtLength ? pathEl.getPointAtLength(eased * pathLen) : {
      x: from.cx + (to.cx - from.cx) * eased,
      y: from.cy + (to.cy - from.cy) * eased
    };
    particle.setAttribute("cx", pt.x);
    particle.setAttribute("cy", pt.y);
    // Fade in/out
    const opacity = t < 0.15 ? t/0.15 : t > 0.85 ? (1-t)/0.15 : 1;
    particle.setAttribute("opacity", opacity.toFixed(2));
    if (t < 1) {
      requestAnimationFrame(animateParticle);
    } else {
      particle.remove();
      pathEl.remove();
      // Zone flash at destination
      triggerZoneFlash(toZoneId, color);
    }
  }
  requestAnimationFrame(animateParticle);
}

function triggerZoneFlash(zoneId, color) {
  const pos = ZONE_POS_CACHE[zoneId];
  if (!pos) return;
  const sparksLayer = document.getElementById("sparks-layer");
  const flash = svgEl("circle", {
    cx: pos.cx, cy: pos.cy, r: "0",
    fill: color, opacity: "0.7",
    class: "zone-flash"
  });
  sparksLayer.appendChild(flash);
  setTimeout(() => flash.remove(), 600);
}

function triggerReceiptSpark() {
  const pos = ZONE_POS_CACHE["evidence_receipts"];
  if (!pos) return;
  const sparksLayer = document.getElementById("sparks-layer");
  const spark = svgEl("circle", {
    cx: pos.cx, cy: pos.cy, r: "0",
    fill: "rgba(41,194,114,0.5)", stroke: "#29c272", "stroke-width": "1",
    class: "receipt-spark"
  });
  sparksLayer.appendChild(spark);
  setTimeout(() => spark.remove(), 800);
}

let resizeTimer;
window.addEventListener("resize", () => {
  clearTimeout(resizeTimer);
  resizeTimer = setTimeout(renderNeuralCanvas, 150);
});


/* ═══════════════════════════════════════════════════════════════
   JS Part 3: Tooltip, Zone Detail, Tab switching
   ═══════════════════════════════════════════════════════════════ */

// ── Tooltip ────────────────────────────────────────────────────────────────────
function showTooltip(e, zone) {
  const tt      = document.getElementById("zone-tooltip");
  const title   = document.getElementById("tt-title");
  const summary = document.getElementById("tt-summary");
  const telDiv  = document.getElementById("tt-telemetry");

  const color = HEALTH_COLOR[zone.health] || "#2e4a68";
  title.style.color = color;
  title.textContent = `${ZONE_ICONS[zone.zone_id] || "●"} ${zone.display_name}`;

  let summaryText = zone.hover_summary_template || "";
  const tel = zone.telemetry || {};
  const replacements = {
    "{task_count}":          tel.task_count ?? "—",
    "{task_package_count}":  tel.task_package_count ?? "—",
    "{comment_count}":       tel.comment_count ?? "—",
    "{link_count}":          tel.link_count ?? "—",
    "{receipt_count}":       tel.receipt_count ?? "—",
    "{health_score}":        STATE.snapshot ? STATE.snapshot.health_score : "—",
    "{snapshot_age}":        "—",
    "{warning_count}":       STATE.snapshot ? STATE.snapshot.warning_count : "—",
    "{last_task_age}":       tel.last_task_age_seconds ?? "—",
    "{last_task_status}":    "—",
    "{linked_count}":        tel.linked_count ?? "—",
    "{unlinked_count}":      tel.unlinked_count ?? "—",
    "{orphaned_task_count}": tel.orphaned_task_count ?? "—",
    "{orphaned_comment_count}": tel.orphaned_comment_count ?? "—",
    "{event_count}":         tel.event_count ?? tel.receipt_count ?? "—",
    "{last_event_age}":      tel.last_event_age_seconds ?? "—",
    "{export_count}":        tel.export_count ?? "—",
    "{no_llm_rate}":         tel.no_llm_rate ?? "—",
    "{enabled_count}":       tel.enabled_action_count ?? "—",
    "{disabled_count}":      tel.disabled_action_count ?? "—",
    "{last_action_age}":     "—",
    "{exchange_state}":      tel.exchange_state ?? "—",
    "{thread_count}":        tel.thread_count ?? "—",
    "{last_exchange_age}":   "—",
    "{last_verdict}":        tel.last_verdict ?? "—",
    "{last_run_age}":        "—",
    "{smoke_status}":        tel.smoke_status ?? "—",
    "{last_smoke_age}":      "—",
    "{organ_coverage}":      tel.organ_coverage_count ?? "—",
    "{last_export_age}":     "—",
    "{gate_status}":         tel.gate_status ?? "—",
    "{module_count}":        tel.module_count ?? "—",
    "{working_count}":       tel.working_count ?? "—",
    "{blocked_count}":       tel.blocked_count ?? "—"
  };
  for (const [k, v] of Object.entries(replacements)) {
    summaryText = summaryText.replace(k, v);
  }
  summaryText = sanitizePlaceholders(summaryText);
  summary.textContent = summaryText || `Status: ${zone.health}`;

  telDiv.innerHTML = "";
  const chips = [
    { label: `Health: ${zone.health}`, cls: zone.health === "WORKING" ? "good" : zone.health === "PARTIAL" ? "warn" : "bad" },
    { label: `Sources: ${zone.source_present_count}/${zone.source_present_count + zone.source_missing_count}`,
      cls: zone.source_missing_count === 0 ? "good" : "warn" }
  ];
  if (tel.receipt_count !== undefined) chips.push({ label: `Receipts: ${tel.receipt_count}`, cls: "good" });
  if (tel.task_count !== undefined)    chips.push({ label: `Tasks: ${tel.task_count}`, cls: "good" });
  if (tel.task_package_count !== undefined) chips.push({ label: `Packages: ${tel.task_package_count}`, cls: "good" });
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
  tt.style.left = `${Math.min(x, window.innerWidth  - tt.offsetWidth  - 10)}px`;
  tt.style.top  = `${Math.min(y, window.innerHeight - tt.offsetHeight - 10)}px`;
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
  const color = HEALTH_COLOR[zone.health] || "#2e4a68";
  const icon  = ZONE_ICONS[zoneId] || "●";

  const iconEl = document.getElementById("zdp-icon");
  iconEl.textContent = icon;
  iconEl.style.background = `rgba(${hexToRgb(color)},0.15)`;
  iconEl.style.borderColor = `rgba(${hexToRgb(color)},0.4)`;

  document.getElementById("zdp-name").textContent = zone.display_name;
  document.getElementById("zdp-name").style.color = color;
  document.getElementById("zdp-purpose").textContent =
    zone.honest_limitations ? zone.honest_limitations.join(" · ") : "";

  document.getElementById("zdp-body").innerHTML = buildZoneDetailHtml(zone);
  document.getElementById("zone-detail-panel").classList.add("open");
  renderNeuralCanvas();
}

function closeZoneDetail() {
  document.getElementById("zone-detail-panel").classList.remove("open");
  STATE.activeZone = null;
  renderNeuralCanvas();
}

function buildZoneDetailHtml(zone) {
  const tel = zone.telemetry || {};
  const color = HEALTH_COLOR[zone.health] || "#2e4a68";
  let html = "";

  html += `<div class="card">
    <div class="card-title">📊 Zone Status</div>
    <div class="card-row"><span>Health</span><span class="val">${statusBadgeHtml(zone.health)}</span></div>
    <div class="card-row"><span>Capability</span><span class="val">${statusBadgeHtml(zone.capability_state)}</span></div>
    <div class="card-row"><span>Sources present</span><span class="val" style="color:var(--green)">${zone.source_present_count}</span></div>
    <div class="card-row"><span>Sources missing</span><span class="val" style="color:${zone.source_missing_count > 0 ? 'var(--amber)' : 'var(--green)'}">${zone.source_missing_count}</span></div>
  </div>`;

  if (Object.keys(tel).length > 0) {
    html += `<div class="card"><div class="card-title">📡 Telemetry</div>`;
    for (const [k, v] of Object.entries(tel)) {
      html += `<div class="card-row"><span>${esc(k)}</span><span class="val">${esc(String(v))}</span></div>`;
    }
    html += `</div>`;
  }

  if (zone.honest_limitations && zone.honest_limitations.length > 0) {
    html += `<div class="card"><div class="card-title">⚠️ Limitations</div><div class="limitations-list">`;
    for (const lim of zone.honest_limitations) {
      html += `<span class="limit-chip">${esc(lim)}</span>`;
    }
    html += `</div></div>`;
  }

  if (zone.missing_capabilities && zone.missing_capabilities.length > 0) {
    html += `<div class="card"><div class="card-title">🔮 Not implemented</div><div class="limitations-list">`;
    for (const mc of zone.missing_capabilities) {
      html += `<span class="missing-chip">${esc(mc)}</span>`;
    }
    html += `</div></div>`;
  }

  if (zone.missing_sources && zone.missing_sources.length > 0) {
    html += `<div class="card"><div class="card-title" style="color:var(--amber)">⚠️ Missing sources</div>`;
    for (const ms of zone.missing_sources) {
      html += `<div class="card-row"><span style="font-size:0.68rem;color:var(--amber);word-break:break-all">${esc(ms)}</span></div>`;
    }
    html += `</div>`;
  }

  html += buildZoneActions(zone.zone_id);
  return html;
}

function buildZoneActions(zoneId) {
  let html = `<div class="card"><div class="card-title">⚡ Actions</div>`;
  if (zoneId === "task_intake") {
    html += `<button class="btn btn-primary btn-full" style="margin-top:8px" onclick="openCorridor('task_intake');closeZoneDetail()">📋 Open Task Intake Corridor</button>`;
    html += `<button class="btn btn-sm btn-full" style="margin-top:6px;color:var(--text-dim);border-color:var(--border)" onclick="switchTab('tasks');closeZoneDetail()">View task list</button>`;
  } else if (zoneId === "owner_comments") {
    html += `<button class="btn btn-amber btn-full" style="margin-top:8px" onclick="switchTab('comments');closeZoneDetail()">💬 Open Comments</button>`;
  } else if (zoneId === "memory_threads") {
    html += `<button class="btn btn-full" style="margin-top:8px;color:var(--magenta);border-color:rgba(255,79,216,0.4);background:rgba(255,79,216,0.08)" onclick="switchTab('links');closeZoneDetail()">🔗 Open Links</button>`;
    html += `<button class="btn btn-primary btn-full" style="margin-top:6px" onclick="switchTab('thread');closeZoneDetail()">🧵 Open Thread View</button>`;
  } else if (zoneId === "evidence_receipts") {
    html += `<button class="btn btn-success btn-full" style="margin-top:8px" onclick="switchTab('evidence');closeZoneDetail()">🔬 Open Evidence</button>`;
    html += `<button class="btn btn-amber btn-full" style="margin-top:6px" onclick="doExport();closeZoneDetail()">📦 Export Pack</button>`;
  } else if (zoneId === "core_brain") {
    html += `<button class="btn btn-primary btn-full" style="margin-top:8px" onclick="rebuildSnapshot();closeZoneDetail()">⚡ Rebuild Snapshot</button>`;
  } else {
    html += `<div style="color:var(--text-muted);font-size:0.72rem;margin-top:8px">Actions for this zone: READ_ONLY</div>`;
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
  attachFormHandlers();
}


/* ═══════════════════════════════════════════════════════════════
   JS Part 4: Tab renderers — Tasks, Comments, Links
   ═══════════════════════════════════════════════════════════════ */

function renderTasksTab() {
  const pkgCount = STATE.taskPackages ? STATE.taskPackages.task_package_count : 0;
  let html = `<div class="section-header">📋 Tasks
    <span class="badge badge-working" style="font-size:0.6rem">${STATE.tasks.length}</span>
    <span class="badge badge-prototype" style="font-size:0.6rem;margin-left:4px">${pkgCount} packages</span>
  </div>`;

  html += `<button class="btn btn-register btn-full" style="margin-bottom:12px"
    onclick="openCorridor('task_intake')">
    📋 Open Task Intake Corridor
  </button>`;

  if (STATE.tasks.length === 0) {
    html += `<div class="empty-state"><div class="empty-icon">📋</div>No tasks yet.<br>Use the corridor to register your first task.</div>`;
    return html;
  }

  html += `<div class="item-list">`;
  for (const t of [...STATE.tasks].reverse().slice(0, 20)) {
    const hasPkg = t.package_exists || false;
    const verdict = t.machine_readiness_verdict || "";
    html += `<div class="item-card">
      <div class="item-id">${esc(t.task_id)}</div>
      <div class="item-text">${esc(t.task_title || t.source_text || "—")}</div>
      <div class="item-meta">
        ${statusBadgeHtml(t.status)}
        ${verdict ? `<span class="badge badge-dim" style="font-size:0.58rem">${esc(verdict)}</span>` : ""}
        ${hasPkg ? `<span class="badge badge-working" style="font-size:0.58rem">PKG</span>` : ""}
        <span style="font-size:0.65rem;color:var(--text-muted);margin-left:auto">${timeAgo(t.created_at)}</span>
      </div>
    </div>`;
  }
  html += `</div>`;
  return html;
}

function renderCommentsTab() {
  let html = `<div class="section-header">💬 Owner Comments
    <span class="badge badge-amber" style="font-size:0.6rem">${STATE.comments.length}</span>
  </div>`;

  html += `<div class="card" style="margin-bottom:10px">
    <div class="card-title">Add Comment</div>
    <div class="form-group">
      <label>Text <span class="req-mark">*</span></label>
      <textarea id="new-comment-text" placeholder="Write your comment…" rows="3"></textarea>
    </div>
    <div class="form-group">
      <label>Type</label>
      <select id="new-comment-type">
        <option value="OBSERVATION">OBSERVATION</option>
        <option value="REQUIREMENT">REQUIREMENT</option>
        <option value="CONCERN">CONCERN</option>
        <option value="DECISION">DECISION</option>
        <option value="NOTE">NOTE</option>
      </select>
    </div>
    <button class="btn btn-amber btn-full" onclick="submitComment()">💬 Add Comment</button>
  </div>`;

  if (STATE.comments.length === 0) {
    html += `<div class="empty-state"><div class="empty-icon">💬</div>No comments yet.</div>`;
    return html;
  }

  html += `<div class="item-list">`;
  for (const c of [...STATE.comments].reverse().slice(0, 20)) {
    html += `<div class="item-card">
      <div class="item-id">${esc(c.comment_id)}</div>
      <div class="item-text">${esc(c.original_text || "—")}</div>
      <div class="item-meta">
        ${statusBadgeHtml(c.status)}
        <span class="badge badge-dim" style="font-size:0.58rem">${esc(c.comment_type || "—")}</span>
        <span style="font-size:0.65rem;color:var(--text-muted);margin-left:auto">${timeAgo(c.created_at)}</span>
      </div>
    </div>`;
  }
  html += `</div>`;
  return html;
}

function renderLinksTab() {
  let html = `<div class="section-header">🔗 Memory Links
    <span class="badge badge-magenta" style="font-size:0.6rem">${STATE.links.length}</span>
  </div>`;

  html += `<div class="card" style="margin-bottom:10px">
    <div class="card-title">Create Link</div>
    <div class="form-group">
      <label>Task ID <span class="req-mark">*</span></label>
      <input type="text" id="new-link-source" placeholder="TI-…">
    </div>
    <div class="form-group">
      <label>Comment ID <span class="req-mark">*</span></label>
      <input type="text" id="new-link-target" placeholder="OC-…">
    </div>
    <button class="btn btn-full" style="color:var(--magenta);border-color:rgba(255,79,216,0.4);background:rgba(255,79,216,0.08)"
      onclick="submitLink()">🔗 Create Link</button>
  </div>`;

  if (STATE.links.length === 0) {
    html += `<div class="empty-state"><div class="empty-icon">🔗</div>No links yet.</div>`;
    return html;
  }

  html += `<div class="item-list">`;
  for (const l of [...STATE.links].reverse().slice(0, 20)) {
    html += `<div class="item-card">
      <div class="item-id">${esc(l.link_id)}</div>
      <div class="item-text" style="font-size:0.72rem">
        <span style="color:var(--cyan)">${esc(l.source_id)}</span>
        <span style="color:var(--text-muted)"> → </span>
        <span style="color:var(--amber)">${esc(l.target_id)}</span>
      </div>
      <div class="item-meta">
        ${statusBadgeHtml(l.status)}
        <span style="font-size:0.65rem;color:var(--text-muted);margin-left:auto">${timeAgo(l.created_at)}</span>
      </div>
    </div>`;
  }
  html += `</div>`;
  return html;
}

/* ═══════════════════════════════════════════════════════════════
   JS Part 5: Tab renderers — Thread, Evidence
   ═══════════════════════════════════════════════════════════════ */

function renderThreadTab() {
  let html = `<div class="section-header">🧵 Memory Thread</div>`;
  html += `<div class="card" style="margin-bottom:10px">
    <div class="card-title">Load Thread</div>
    <div class="form-group">
      <label>Task ID</label>
      <input type="text" id="thread-task-id" placeholder="TI-…">
    </div>
    <button class="btn btn-primary btn-full" onclick="loadThread()">🧵 Load Thread</button>
  </div>`;
  html += `<div id="thread-result"></div>`;
  return html;
}

async function loadThread() {
  const taskId = (document.getElementById("thread-task-id")?.value || "").trim();
  if (!taskId) { notify("Enter a task ID", "warn"); return; }
  try {
    const r = await apiFetch(`/api/thread/${taskId}`);
    const el = document.getElementById("thread-result");
    if (!el) return;
    let html = `<div class="thread-task-card">
      <div class="item-id">${esc(r.task.task_id)}</div>
      <div class="item-text">${esc(r.task.task_title || r.task.source_text || "—")}</div>
      <div class="item-meta">${statusBadgeHtml(r.task.status)}</div>
    </div>`;
    if (r.comments.length > 0) {
      html += `<div class="section-header" style="margin-bottom:6px">Linked Comments</div>`;
      for (const c of r.comments) {
        html += `<div class="thread-comment-card">
          <div class="item-id">${esc(c.comment_id)}</div>
          <div class="item-text">${esc(c.original_text || "—")}</div>
        </div>`;
      }
    }
    if (r.receipts.length > 0) {
      html += `<div class="section-header" style="margin-bottom:6px">Receipts (${r.receipts.length})</div>`;
      for (const rc of r.receipts.slice(0, 5)) {
        html += `<div class="card" style="padding:7px 10px;margin-bottom:5px">
          <div style="font-size:0.68rem;color:var(--text-muted);font-family:monospace">${esc(rc.receipt_id)}</div>
          <div style="font-size:0.72rem;color:var(--text-dim)">${esc(rc.event_type)} · ${timeAgo(rc.created_at)}</div>
        </div>`;
      }
    }
    el.innerHTML = html;
  } catch (e) {
    notify(`Thread not found: ${taskId}`, "error");
  }
}

function renderEvidenceTab() {
  const rs = STATE.receiptsStatus;
  const es = STATE.exportStatus;
  const pkgs = STATE.taskPackages;

  let html = `<div class="section-header">🔬 Evidence Vault</div>`;

  // Receipts
  html += `<div class="card">
    <div class="card-title">📄 Receipts
      <span class="badge badge-working" style="font-size:0.6rem">${rs ? rs.receipt_count : "—"}</span>
    </div>
    <div class="card-row"><span>Status</span><span class="val">${esc(rs ? rs.status : "MISSING")}</span></div>
    <div class="card-row"><span>Parse errors</span><span class="val">${rs ? rs.parse_errors : "—"}</span></div>
    <div class="card-row"><span>Read-only</span><span class="val" style="color:var(--green)">TRUE</span></div>
  </div>`;

  // Task packages
  html += `<div class="card">
    <div class="card-title">📦 Task Packages
      <span class="badge badge-prototype" style="font-size:0.6rem">${pkgs ? pkgs.task_package_count : "—"}</span>
    </div>`;
  if (pkgs && pkgs.packages && pkgs.packages.length > 0) {
    for (const p of pkgs.packages.slice(0, 5)) {
      const verdictCls = p.verdict === "READY_FOR_LAUNCH" ? "badge-working" :
                         p.verdict === "OWNER_REVIEW_REQUIRED" ? "badge-partial" : "badge-blocked";
      html += `<div class="card-row">
        <span style="font-size:0.68rem;font-family:monospace;color:var(--text-dim)">${esc(p.task_id)}</span>
        <span class="badge ${verdictCls}" style="font-size:0.58rem">${esc(p.verdict || "—")}</span>
      </div>`;
    }
  } else {
    html += `<div style="font-size:0.72rem;color:var(--text-muted);padding:4px 0">No packages yet</div>`;
  }
  html += `</div>`;

  // Exports
  html += `<div class="card">
    <div class="card-title">📤 Exports
      <span class="badge badge-amber" style="font-size:0.6rem">${es ? es.export_count : "—"}</span>
    </div>
    <div class="card-row"><span>Status</span><span class="val">${esc(es ? es.status : "MISSING")}</span></div>
    <button class="btn btn-amber btn-full" style="margin-top:8px" onclick="doExport()">📦 Create Export</button>
  </div>`;

  // Latest receipts
  if (rs && rs.latest_receipts && rs.latest_receipts.length > 0) {
    html += `<div class="section-header" style="margin-top:4px">Latest Receipts</div>
    <div class="item-list">`;
    for (const r of rs.latest_receipts.slice(0, 8)) {
      html += `<div class="item-card">
        <div class="item-id">${esc(r.receipt_id || r.file)}</div>
        <div class="item-text" style="font-size:0.72rem">${esc(r.event_type || "—")}</div>
        <div class="item-meta">
          <span class="badge badge-working" style="font-size:0.58rem">${esc(r.parse_status)}</span>
          <span style="font-size:0.65rem;color:var(--text-muted);margin-left:auto">${timeAgo(r.created_at)}</span>
        </div>
      </div>`;
    }
    html += `</div>`;
  }

  return html;
}

/* ═══════════════════════════════════════════════════════════════
   JS Part 6: Form handlers — comment, link submit
   ═══════════════════════════════════════════════════════════════ */

async function submitComment() {
  const text = (document.getElementById("new-comment-text")?.value || "").trim();
  const type = document.getElementById("new-comment-type")?.value || "OBSERVATION";
  if (!text) { notify("Comment text is required", "warn"); return; }
  try {
    await apiFetch("/api/comments", {
      method: "POST",
      headers: {"Content-Type":"application/json"},
      body: JSON.stringify({ original_text: text, comment_type: type })
    });
    notify("Comment added", "success");
    await fullRefresh();
  } catch { notify("Failed to add comment", "error"); }
}

async function submitLink() {
  const src = (document.getElementById("new-link-source")?.value || "").trim();
  const tgt = (document.getElementById("new-link-target")?.value || "").trim();
  if (!src || !tgt) { notify("Both IDs are required", "warn"); return; }
  try {
    await apiFetch("/api/links", {
      method: "POST",
      headers: {"Content-Type":"application/json"},
      body: JSON.stringify({ source_id: src, target_id: tgt })
    });
    notify("Link created", "success");
    triggerParticle("task_intake", "memory_threads", "#ff4fd8");
    await fullRefresh();
  } catch { notify("Failed to create link", "error"); }
}

function attachFormHandlers() {
  // Keyboard submit for comment
  const commentEl = document.getElementById("new-comment-text");
  if (commentEl) {
    commentEl.addEventListener("keydown", (e) => {
      if (e.ctrlKey && e.key === "Enter") submitComment();
    });
  }
}

/* ═══════════════════════════════════════════════════════════════
   JS Part 7: Task Intake Corridor — open/close, stage navigation
   ═══════════════════════════════════════════════════════════════ */

function openCorridor(zoneId) {
  STATE.corridorOpen = true;
  STATE.activeZone = zoneId;
  STATE.corridorStage = 0;
  STATE.corridorData = {};
  STATE.corridorResult = null;
  STATE.launchResult = null;

  document.getElementById("corridor-panel").classList.add("open");
  document.getElementById("panel-mode-label").textContent = "CORRIDOR MODE";
  document.getElementById("panel-mode-zone").textContent = "TASK INTAKE";

  updateStageIndicator(0);
  renderCorridorStage(0);
  renderNeuralCanvas();
}

function closeCorridor() {
  STATE.corridorOpen = false;
  STATE.activeZone = null;
  document.getElementById("corridor-panel").classList.remove("open");
  document.getElementById("panel-mode-label").textContent = "OPERATOR SURFACE";
  document.getElementById("panel-mode-zone").textContent = "";
  renderNeuralCanvas();
}

function updateStageIndicator(stage) {
  document.querySelectorAll(".stage-dot").forEach((el, i) => {
    el.classList.remove("active", "done");
    if (i < stage) el.classList.add("done");
    else if (i === stage) el.classList.add("active");
  });
}

function renderCorridorStage(stage) {
  STATE.corridorStage = stage;
  updateStageIndicator(stage);
  const content = document.getElementById("corridor-content");
  switch (stage) {
    case 0: content.innerHTML = renderCorridorCompose(); break;
    case 1: content.innerHTML = renderCorridorComment(); break;
    case 2: content.innerHTML = renderCorridorRegister(); break;
    case 3: content.innerHTML = renderCorridorReview();   break;
    case 4: content.innerHTML = renderCorridorLaunch();   break;
  }
  attachCorridorHandlers(stage);
}

function corridorNext() {
  if (STATE.corridorStage < 4) renderCorridorStage(STATE.corridorStage + 1);
}

function corridorBack() {
  if (STATE.corridorStage > 0) renderCorridorStage(STATE.corridorStage - 1);
}

/* ═══════════════════════════════════════════════════════════════
   JS Part 8: Corridor Stage 0 — COMPOSE form
   ═══════════════════════════════════════════════════════════════ */

function renderCorridorCompose() {
  const d = STATE.corridorData;
  return `
  <div class="card">
    <div class="card-title">📝 Task Definition</div>

    <div class="form-group">
      <label>Task Title <span class="req-mark">*</span>
        <span class="field-indicator ${d.task_title ? 'filled' : ''}" id="ind-title"></span>
      </label>
      <input type="text" id="c-title" placeholder="Short, clear task name (min 5 chars)"
        value="${esc(d.task_title || '')}" maxlength="120">
    </div>

    <div class="form-group">
      <label>Task Description <span class="req-mark">*</span>
        <span class="field-indicator ${d.task_description ? 'filled' : ''}" id="ind-desc"></span>
      </label>
      <textarea id="c-desc" placeholder="Full description of what needs to be done (min 20 chars)" rows="4">${esc(d.task_description || '')}</textarea>
    </div>

    <div class="form-group">
      <label>Pass Criteria <span class="req-mark">*</span>
        <span class="field-indicator ${d.pass_criteria ? 'filled' : ''}" id="ind-pass"></span>
      </label>
      <textarea id="c-pass" placeholder="One criterion per line. What counts as success?" rows="3">${esc(d.pass_criteria || '')}</textarea>
    </div>

    <div class="form-group">
      <label>Fail Criteria <span class="req-mark">*</span>
        <span class="field-indicator ${d.fail_criteria ? 'filled' : ''}" id="ind-fail"></span>
      </label>
      <textarea id="c-fail" placeholder="One criterion per line. What counts as failure?" rows="3">${esc(d.fail_criteria || '')}</textarea>
    </div>

    <div class="form-group">
      <label>Stop Conditions <span class="req-mark">*</span>
        <span class="field-indicator ${d.stop_conditions ? 'filled' : ''}" id="ind-stop"></span>
      </label>
      <textarea id="c-stop" placeholder="When should Servitor stop without completing?" rows="2">${esc(d.stop_conditions || '')}</textarea>
    </div>

    <div class="form-group">
      <label>Scope Paths <span class="req-mark">*</span>
        <span class="field-indicator ${d.scope_paths ? 'filled' : ''}" id="ind-scope"></span>
      </label>
      <textarea id="c-scope" placeholder="One path per line. Must contain IMPERIUM_TEST_VERSION" rows="3">${esc(d.scope_paths || '')}</textarea>
    </div>
  </div>

  <div class="card">
    <div class="card-title">⚙️ Optional Fields</div>

    <div class="form-group">
      <label>Forbidden Paths <span class="opt-mark">(optional)</span></label>
      <textarea id="c-forbidden" placeholder="Paths Servitor must NOT touch" rows="2">${esc(d.forbidden_paths || '')}</textarea>
    </div>

    <div class="form-group">
      <label>Allowed Actions <span class="opt-mark">(optional)</span></label>
      <textarea id="c-allowed" placeholder="Specific actions Servitor may take" rows="2">${esc(d.allowed_actions || '')}</textarea>
    </div>

    <div class="form-group">
      <label>Forbidden Actions <span class="opt-mark">(optional)</span></label>
      <textarea id="c-forbidden-actions" placeholder="Actions Servitor must NOT take" rows="2">${esc(d.forbidden_actions || '')}</textarea>
    </div>

    <div class="form-group">
      <label>Execution Requirements <span class="opt-mark">(optional)</span></label>
      <input type="text" id="c-exec-req" placeholder="e.g. Python 3.12, no Node.js"
        value="${esc(d.execution_requirements || '')}">
    </div>

    <div class="form-group">
      <label>Priority</label>
      <select id="c-priority">
        <option value="LOW"      ${d.priority==='LOW'      ? 'selected':''}>LOW</option>
        <option value="MEDIUM"   ${(!d.priority||d.priority==='MEDIUM') ? 'selected':''}>MEDIUM</option>
        <option value="HIGH"     ${d.priority==='HIGH'     ? 'selected':''}>HIGH</option>
        <option value="CRITICAL" ${d.priority==='CRITICAL' ? 'selected':''}>CRITICAL</option>
      </select>
    </div>

    <div class="form-group">
      <label>Tags <span class="opt-mark">(comma-separated)</span></label>
      <input type="text" id="c-tags" placeholder="v0.6, backend, corridor"
        value="${esc(d.tags || '')}">
    </div>

    <div class="form-group">
      <label>Notes <span class="opt-mark">(optional)</span></label>
      <textarea id="c-notes" placeholder="Free notes for context" rows="2">${esc(d.notes || '')}</textarea>
    </div>
  </div>

  <div style="display:flex;gap:8px;margin-top:4px">
    <button class="btn btn-register btn-full" id="btn-compose-next" onclick="composeNext()">
      Next: Owner Comment →
    </button>
  </div>
  <div style="font-size:0.62rem;color:var(--text-muted);margin-top:6px;text-align:center">
    Fields marked <span style="color:var(--cyan)">*</span> are required
  </div>`;
}

function composeNext() {
  // Collect and validate required fields
  const title = (document.getElementById("c-title")?.value || "").trim();
  const desc  = (document.getElementById("c-desc")?.value  || "").trim();
  const pass  = (document.getElementById("c-pass")?.value  || "").trim();
  const fail  = (document.getElementById("c-fail")?.value  || "").trim();
  const stop  = (document.getElementById("c-stop")?.value  || "").trim();
  const scope = (document.getElementById("c-scope")?.value || "").trim();

  const missing = [];
  if (title.length < 5)  missing.push("Task Title (min 5 chars)");
  if (desc.length < 20)  missing.push("Task Description (min 20 chars)");
  if (!pass)             missing.push("Pass Criteria");
  if (!fail)             missing.push("Fail Criteria");
  if (!stop)             missing.push("Stop Conditions");
  if (!scope)            missing.push("Scope Paths");

  if (missing.length > 0) {
    notify(`Required: ${missing.join(", ")}`, "warn");
    return;
  }

  // Save to state
  STATE.corridorData = {
    task_title:             title,
    task_description:       desc,
    pass_criteria:          pass,
    fail_criteria:          fail,
    stop_conditions:        stop,
    scope_paths:            scope,
    forbidden_paths:        (document.getElementById("c-forbidden")?.value || "").trim(),
    allowed_actions:        (document.getElementById("c-allowed")?.value || "").trim(),
    forbidden_actions:      (document.getElementById("c-forbidden-actions")?.value || "").trim(),
    execution_requirements: (document.getElementById("c-exec-req")?.value || "").trim(),
    priority:               document.getElementById("c-priority")?.value || "MEDIUM",
    tags:                   (document.getElementById("c-tags")?.value || "").trim(),
    notes:                  (document.getElementById("c-notes")?.value || "").trim()
  };

  renderCorridorStage(1);
}

/* ═══════════════════════════════════════════════════════════════
   JS Part 9: Corridor Stage 1 — COMMENT
   ═══════════════════════════════════════════════════════════════ */

function renderCorridorComment() {
  const d = STATE.corridorData;
  return `
  <div class="card">
    <div class="card-title">💬 Owner Comment <span style="color:var(--text-muted);font-weight:400">(optional)</span></div>
    <p style="font-size:0.72rem;color:var(--text-dim);margin-bottom:10px;line-height:1.5">
      Add a comment that will be linked to this task and included in the machine package.
      Write in any language. This becomes part of the Servitor context.
    </p>

    <div class="form-group">
      <label>Comment Text</label>
      <textarea id="c-comment-text" placeholder="Your comment, context, or instructions for Servitor…" rows="5">${esc(d.comment_text || '')}</textarea>
    </div>

    <div class="form-group">
      <label>Comment Type</label>
      <select id="c-comment-type">
        <option value="OBSERVATION"  ${d.comment_type==='OBSERVATION'  ? 'selected':''}>OBSERVATION</option>
        <option value="REQUIREMENT"  ${d.comment_type==='REQUIREMENT'  ? 'selected':''}>REQUIREMENT</option>
        <option value="CONCERN"      ${d.comment_type==='CONCERN'      ? 'selected':''}>CONCERN</option>
        <option value="DECISION"     ${d.comment_type==='DECISION'     ? 'selected':''}>DECISION</option>
        <option value="NOTE"         ${d.comment_type==='NOTE'         ? 'selected':''}>NOTE</option>
      </select>
    </div>
  </div>

  <div style="display:flex;gap:8px;margin-top:4px">
    <button class="btn btn-full" style="color:var(--text-dim);border-color:var(--border)"
      onclick="corridorBack()">← Back</button>
    <button class="btn btn-register btn-full" onclick="commentNext()">
      Next: Register Task →
    </button>
  </div>
  <div style="font-size:0.62rem;color:var(--text-muted);margin-top:6px;text-align:center">
    Skip this step to register without a comment
  </div>`;
}

function commentNext() {
  STATE.corridorData.comment_text  = (document.getElementById("c-comment-text")?.value  || "").trim();
  STATE.corridorData.comment_type  = document.getElementById("c-comment-type")?.value || "OBSERVATION";
  renderCorridorStage(2);
}

/* ═══════════════════════════════════════════════════════════════
   JS Part 10: Corridor Stage 2 — REGISTER (calls API)
   ═══════════════════════════════════════════════════════════════ */

function renderCorridorRegister() {
  const d = STATE.corridorData;
  const hasComment = !!d.comment_text;
  return `
  <div class="card">
    <div class="card-title">📦 Ready to Register</div>
    <div class="card-row"><span>Task Title</span><span class="val" style="max-width:200px;overflow:hidden;text-overflow:ellipsis">${esc(d.task_title)}</span></div>
    <div class="card-row"><span>Priority</span><span class="val">${esc(d.priority)}</span></div>
    <div class="card-row"><span>Pass criteria</span><span class="val">${d.pass_criteria.split('\n').filter(Boolean).length} lines</span></div>
    <div class="card-row"><span>Fail criteria</span><span class="val">${d.fail_criteria.split('\n').filter(Boolean).length} lines</span></div>
    <div class="card-row"><span>Stop conditions</span><span class="val">${d.stop_conditions.split('\n').filter(Boolean).length} lines</span></div>
    <div class="card-row"><span>Scope paths</span><span class="val">${d.scope_paths.split('\n').filter(Boolean).length} paths</span></div>
    <div class="card-row"><span>Owner comment</span><span class="val" style="color:${hasComment ? 'var(--green)' : 'var(--text-muted)'}">${hasComment ? 'PROVIDED' : 'NONE'}</span></div>
  </div>

  <div class="card" style="background:rgba(0,215,255,0.04);border-color:rgba(0,215,255,0.2)">
    <div style="font-size:0.72rem;color:var(--text-dim);line-height:1.6">
      Pressing <strong style="color:var(--cyan)">Register Task</strong> will:
      <ul style="margin:6px 0 0 14px;color:var(--text-muted)">
        <li>Create machine-readable package in RUNTIME/task_packages/</li>
        <li>Generate all 7 package files (manifest, criteria, scope…)</li>
        <li>Create receipts for every action</li>
        <li>Run machine-readiness validation</li>
      </ul>
    </div>
  </div>

  <div id="register-status"></div>

  <div style="display:flex;gap:8px;margin-top:4px">
    <button class="btn btn-full" style="color:var(--text-dim);border-color:var(--border)"
      onclick="corridorBack()">← Back</button>
    <button class="btn btn-register btn-full" id="btn-register" onclick="doRegisterTask()">
      📦 Register Task
    </button>
  </div>`;
}

async function doRegisterTask() {
  const btn = document.getElementById("btn-register");
  const statusEl = document.getElementById("register-status");
  if (btn) { btn.disabled = true; btn.textContent = "Registering…"; }

  try {
    const result = await apiFetch("/api/tasks/register", {
      method: "POST",
      headers: {"Content-Type":"application/json"},
      body: JSON.stringify(STATE.corridorData)
    });

    STATE.corridorResult = result;

    // Visual feedback
    triggerParticle("task_intake", "core_brain", "#00d7ff");
    triggerParticle("task_intake", "evidence_receipts", "#29c272");
    triggerReceiptSpark();
    notify(`Task registered: ${result.task_id}`, "success");

    await fullRefresh();
    renderCorridorStage(3);

  } catch (e) {
    if (statusEl) {
      statusEl.innerHTML = `<div class="verdict-block blocked" style="margin-top:8px">
        <div class="verdict-label" style="color:var(--red)">❌ Registration Failed</div>
        <div class="verdict-score">${esc(e.message)}</div>
      </div>`;
    }
    if (btn) { btn.disabled = false; btn.textContent = "📦 Register Task"; }
    notify("Registration failed", "error");
  }
}

/* ═══════════════════════════════════════════════════════════════
   JS Part 11: Corridor Stage 3 — REVIEW (machine verdict)
   ═══════════════════════════════════════════════════════════════ */

function renderCorridorReview() {
  const r = STATE.corridorResult;
  if (!r) {
    return `<div class="empty-state"><div class="empty-icon">⚠️</div>No registration result. Go back and register first.</div>
    <button class="btn btn-full" style="color:var(--text-dim);border-color:var(--border)" onclick="corridorBack()">← Back</button>`;
  }

  const verdict  = r.machine_readiness_verdict || "UNKNOWN";
  const score    = r.machine_readiness_score ?? 0;
  const warnings = r.warnings || [];
  const blockers = r.blockers || [];
  const launchOk = r.launch_allowed;

  const verdictCls = verdict === "READY_FOR_LAUNCH" ? "ready" :
                     verdict === "OWNER_REVIEW_REQUIRED" ? "review" : "blocked";
  const verdictColor = verdict === "READY_FOR_LAUNCH" ? "var(--green)" :
                       verdict === "OWNER_REVIEW_REQUIRED" ? "var(--amber)" : "var(--red)";

  let html = `
  <div class="verdict-block ${verdictCls}">
    <div class="verdict-label" style="color:${verdictColor}">${
      verdict === "READY_FOR_LAUNCH" ? "🟢" :
      verdict === "OWNER_REVIEW_REQUIRED" ? "🟡" : "🔴"
    } ${esc(verdict)}</div>
    <div class="verdict-score">Machine readiness score: ${score}/10</div>
    ${blockers.length > 0 ? `<div style="font-size:0.68rem;color:var(--red);margin-top:4px">${blockers.length} blocker(s)</div>` : ""}
    ${warnings.length > 0 ? `<div style="font-size:0.68rem;color:var(--amber);margin-top:2px">${warnings.length} warning(s)</div>` : ""}
  </div>`;

  // Task ID
  html += `<div class="card">
    <div class="card-title">📋 Registered Task</div>
    <div class="card-row"><span>Task ID</span><span class="val" style="font-family:monospace;font-size:0.7rem">${esc(r.task_id)}</span></div>
    <div class="card-row"><span>Package path</span><span class="val" style="font-size:0.65rem;color:var(--text-dim);word-break:break-all">${esc(r.package_path || "—")}</span></div>
    <div class="card-row"><span>Receipts created</span><span class="val" style="color:var(--green)">${(r.receipts || []).length}</span></div>
    ${r.comment_id ? `<div class="card-row"><span>Comment ID</span><span class="val" style="font-family:monospace;font-size:0.7rem">${esc(r.comment_id)}</span></div>` : ""}
  </div>`;

  // Warnings
  if (warnings.length > 0) {
    html += `<div class="card" style="border-color:rgba(255,179,71,0.3)">
      <div class="card-title" style="color:var(--amber)">⚠️ Warnings</div>`;
    for (const w of warnings) {
      html += `<div style="font-size:0.72rem;color:var(--amber);padding:3px 0;border-bottom:1px solid rgba(255,179,71,0.1)">${esc(w)}</div>`;
    }
    html += `</div>`;
  }

  // Blockers
  if (blockers.length > 0) {
    html += `<div class="card" style="border-color:rgba(255,93,102,0.3)">
      <div class="card-title" style="color:var(--red)">❌ Blockers</div>`;
    for (const b of blockers) {
      html += `<div style="font-size:0.72rem;color:var(--red);padding:3px 0;border-bottom:1px solid rgba(255,93,102,0.1)">${esc(b)}</div>`;
    }
    html += `</div>`;
  }

  // Actions
  html += `<div style="display:flex;flex-direction:column;gap:7px;margin-top:8px">
    <button class="btn btn-primary btn-full" onclick="downloadPackage()">📥 Download Package</button>
    <button class="btn btn-full" style="color:var(--text-dim);border-color:var(--border)" onclick="viewPackageInline()">🔍 View Package Files</button>
    <div id="package-inline-view"></div>
    <button class="btn btn-launch btn-full" id="btn-launch-task"
      ${launchOk ? '' : 'disabled'}
      onclick="doLaunchTask()">
      🚀 Launch Task ${launchOk ? '' : '(blocked)'}
    </button>
    <button class="btn btn-full" style="color:var(--text-dim);border-color:var(--border)" onclick="corridorBack()">✏️ Back to Edit</button>
  </div>`;

  return html;
}

async function downloadPackage() {
  const r = STATE.corridorResult;
  if (!r || !r.task_id) { notify("No package to download", "warn"); return; }
  try {
    const pkg = await apiFetch(`/api/tasks/${r.task_id}`);
    const blob = new Blob([JSON.stringify(pkg, null, 2)], {type: "application/json"});
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url; a.download = `${r.task_id}_manifest.json`;
    a.click(); URL.revokeObjectURL(url);
    notify("Package downloaded", "success");
  } catch { notify("Download failed", "error"); }
}

async function viewPackageInline() {
  const r = STATE.corridorResult;
  if (!r || !r.task_id) return;
  const el = document.getElementById("package-inline-view");
  if (!el) return;
  try {
    const vr = await apiFetch(`/api/tasks/${r.task_id}/validation`);
    el.innerHTML = `<div class="card" style="margin-top:6px;background:rgba(2,4,10,0.98);border-color:rgba(0,215,255,0.15)">
      <div class="card-title">validation_report.json</div>
      <pre style="font-size:0.62rem;color:var(--cyan);overflow-x:auto;white-space:pre-wrap;line-height:1.5">${esc(JSON.stringify(vr, null, 2))}</pre>
    </div>`;
  } catch { el.innerHTML = `<div style="color:var(--red);font-size:0.72rem;margin-top:6px">Could not load package files</div>`; }
}

/* ═══════════════════════════════════════════════════════════════
   JS Part 12: Corridor Stage 4 — LAUNCH + handoff block
   ═══════════════════════════════════════════════════════════════ */

async function doLaunchTask() {
  const r = STATE.corridorResult;
  if (!r || !r.task_id) { notify("No task to launch", "warn"); return; }

  const btn = document.getElementById("btn-launch-task");
  if (btn) { btn.disabled = true; btn.textContent = "Launching…"; }

  try {
    const result = await apiFetch("/api/tasks/launch", {
      method: "POST",
      headers: {"Content-Type":"application/json"},
      body: JSON.stringify({ task_id: r.task_id })
    });

    STATE.launchResult = result;

    // Visual celebration
    triggerParticle("task_intake", "core_brain", "#00d7ff");
    triggerParticle("task_intake", "export_bundle_gate", "#ffb347");
    triggerParticle("core_brain", "evidence_receipts", "#29c272");
    triggerReceiptSpark();
    notify(`Task launched: ${r.task_id}`, "success");

    await fullRefresh();
    renderCorridorStage(4);

  } catch (e) {
    if (btn) { btn.disabled = false; btn.textContent = "🚀 Launch Task"; }
    notify(`Launch failed: ${e.message}`, "error");
  }
}

function renderCorridorLaunch() {
  const lr = STATE.launchResult;
  if (!lr) {
    return `<div class="empty-state"><div class="empty-icon">🚀</div>Task not yet launched. Go back to Review.</div>
    <button class="btn btn-full" style="color:var(--text-dim);border-color:var(--border)" onclick="corridorBack()">← Back</button>`;
  }

  return `
  <div class="verdict-block ready" style="margin-bottom:12px">
    <div class="verdict-label" style="color:var(--green)">🟢 TASK_READY_FOR_SERVITOR</div>
    <div class="verdict-score">Launched: ${esc(lr.launched_at || "—")}</div>
  </div>

  <div class="card">
    <div class="card-title">📋 Launch Receipt</div>
    <div class="card-row"><span>Task ID</span><span class="val" style="font-family:monospace;font-size:0.7rem">${esc(lr.task_id)}</span></div>
    <div class="card-row"><span>Launch Receipt</span><span class="val" style="font-family:monospace;font-size:0.68rem">${esc(lr.launch_receipt_id)}</span></div>
    <div class="card-row"><span>Package path</span><span class="val" style="font-size:0.65rem;color:var(--text-dim);word-break:break-all">${esc(lr.package_path || "—")}</span></div>
  </div>

  <div class="card">
    <div class="card-title" style="color:var(--cyan)">📋 Servitor Handoff Block</div>
    <p style="font-size:0.68rem;color:var(--text-dim);margin-bottom:8px;line-height:1.5">
      Copy this block and give it to Servitor. Servitor reads the task from Second Brain in machine-readable form.
    </p>
    <textarea class="handoff-textarea" id="corridor-handoff-textarea" readonly>${esc(lr.handoff_block || "")}</textarea>
    <button class="btn btn-primary btn-full" style="margin-top:8px" onclick="copyHandoffBlock()">
      📋 Copy Handoff Block
    </button>
  </div>

  <div class="card" style="background:rgba(41,194,114,0.04);border-color:rgba(41,194,114,0.2)">
    <div style="font-size:0.72rem;color:var(--text-dim);line-height:1.6">
      <strong style="color:var(--green)">Next steps:</strong><br>
      1. Copy the handoff block above<br>
      2. Give it to Servitor in a new conversation<br>
      3. Servitor reads <code style="color:var(--cyan)">task_manifest.json</code> first<br>
      4. Servitor performs the work within scope<br>
      5. Servitor produces receipts and evidence
    </div>
  </div>

  <div style="display:flex;gap:8px;margin-top:8px">
    <button class="btn btn-full" style="color:var(--text-dim);border-color:var(--border)"
      onclick="closeCorridor()">Close Corridor</button>
    <button class="btn btn-register btn-full" onclick="openCorridor('task_intake')">
      + New Task
    </button>
  </div>`;
}

function copyHandoffBlock() {
  const ta = document.getElementById("corridor-handoff-textarea");
  if (!ta) return;
  try {
    navigator.clipboard.writeText(ta.value).then(() => {
      notify("Handoff block copied to clipboard", "success");
    });
  } catch {
    ta.select();
    document.execCommand("copy");
    notify("Handoff block copied", "success");
  }
}

function attachCorridorHandlers(stage) {
  if (stage === 0) {
    // Live field indicators
    const fields = [
      ["c-title", "ind-title", v => v.length >= 5],
      ["c-desc",  "ind-desc",  v => v.length >= 20],
      ["c-pass",  "ind-pass",  v => v.trim().length > 0],
      ["c-fail",  "ind-fail",  v => v.trim().length > 0],
      ["c-stop",  "ind-stop",  v => v.trim().length > 0],
      ["c-scope", "ind-scope", v => v.trim().length > 0]
    ];
    for (const [fieldId, indId, check] of fields) {
      const el = document.getElementById(fieldId);
      const ind = document.getElementById(indId);
      if (el && ind) {
        const update = () => {
          ind.classList.toggle("filled", check(el.value));
        };
        el.addEventListener("input", update);
        update();
      }
    }
  }
}

/* ═══════════════════════════════════════════════════════════════
   JS Part 13: Init — startup, polling
   ═══════════════════════════════════════════════════════════════ */

async function init() {
  // Initial load
  await fullRefresh();

  // Auto-refresh every 30s
  setInterval(async () => {
    if (!STATE.corridorOpen) {
      await fullRefresh();
    } else {
      // In corridor mode — only refresh status/counts, not canvas
      await loadStatus();
      await loadTaskPackages();
    }
  }, 30000);
}

document.addEventListener("DOMContentLoaded", init);
