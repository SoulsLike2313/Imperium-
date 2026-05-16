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
