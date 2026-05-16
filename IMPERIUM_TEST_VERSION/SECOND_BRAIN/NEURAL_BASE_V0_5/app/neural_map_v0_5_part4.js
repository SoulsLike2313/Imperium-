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
