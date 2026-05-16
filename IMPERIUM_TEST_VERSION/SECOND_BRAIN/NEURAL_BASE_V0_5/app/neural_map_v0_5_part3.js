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
