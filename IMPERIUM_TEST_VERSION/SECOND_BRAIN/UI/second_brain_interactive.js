/**
 * Second Brain V0.3 — Interactive UI Logic
 * Mode: PROTOTYPE_INTERACTIVE | RULE_BASED_ONLY | NO_LOCAL_LLM | NO_AGENT_API
 * Communicates with server.py at /api/*
 */

const API_BASE = '';  // same origin — served by server.py at /api/status etc.

// ── State ─────────────────────────────────────────────────────────────────────
let state = {
  tasks: [],
  comments: [],
  links: [],
  status: null,
  loading: false
};

// ── API helpers ───────────────────────────────────────────────────────────────

async function apiFetch(path, options = {}) {
  const res = await fetch(API_BASE + path, {
    headers: { 'Content-Type': 'application/json' },
    ...options
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.error || `HTTP ${res.status}`);
  return data;
}

async function apiGet(path)       { return apiFetch(path); }
async function apiPost(path, body){ return apiFetch(path, { method: 'POST', body: JSON.stringify(body) }); }

// ── Notifications ─────────────────────────────────────────────────────────────

function notify(type, message, id = null) {
  const icons = { success: '✅', error: '❌', info: 'ℹ️' };
  const container = document.getElementById('notifications');
  const el = document.createElement('div');
  el.className = `notif notif-${type}`;
  el.innerHTML = `
    <span class="notif-icon">${icons[type] || 'ℹ️'}</span>
    <div>
      <div class="notif-text">${escHtml(message)}</div>
      ${id ? `<div class="notif-id">${escHtml(id)}</div>` : ''}
    </div>`;
  container.appendChild(el);
  setTimeout(() => el.remove(), 5000);
}

// ── Utilities ─────────────────────────────────────────────────────────────────

function escHtml(s) {
  if (!s) return '';
  return String(s)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

function fmtTime(iso) {
  if (!iso) return '';
  try {
    const d = new Date(iso);
    return d.toLocaleString('ru-RU', { dateStyle: 'short', timeStyle: 'short' });
  } catch { return iso; }
}

function statusBadge(s) {
  return `<span class="s-badge s-${escHtml(s)}">${escHtml(s)}</span>`;
}

function priorityBadge(p) {
  return `<span class="s-badge p-${escHtml(p)}">${escHtml(p)}</span>`;
}

// ── Load all data ─────────────────────────────────────────────────────────────

async function loadAll() {
  try {
    const [status, tasks, comments, links] = await Promise.all([
      apiGet('/api/status'),
      apiGet('/api/tasks'),
      apiGet('/api/comments'),
      apiGet('/api/links')
    ]);
    state.status   = status;
    state.tasks    = Array.isArray(tasks)    ? tasks    : [];
    state.comments = Array.isArray(comments) ? comments : [];
    state.links    = Array.isArray(links)    ? links    : [];
    renderAll();
  } catch (e) {
    notify('error', 'Ошибка загрузки данных: ' + e.message);
  }
}

// ── Render ────────────────────────────────────────────────────────────────────

function renderAll() {
  renderStats();
  renderTasks();
  renderComments();
  renderLinks();
  populateSelects();
}

function renderStats() {
  const s = state.status;
  if (!s) return;
  const c = s.counts || {};
  document.getElementById('stat-tasks').textContent    = c.tasks    ?? state.tasks.length;
  document.getElementById('stat-comments').textContent = c.comments ?? state.comments.length;
  document.getElementById('stat-links').textContent    = c.links    ?? state.links.length;
  document.getElementById('stat-receipts').textContent = c.receipts ?? '—';

  const serverBadge = document.getElementById('server-status-badge');
  if (serverBadge) {
    serverBadge.className = 'status-badge badge-ok';
    serverBadge.textContent = 'SERVER OK';
  }
}

function renderTasks() {
  const container = document.getElementById('tasks-list');
  if (!container) return;
  if (state.tasks.length === 0) {
    container.innerHTML = `<div class="empty-state"><div class="empty-icon">📋</div>Задач пока нет. Введите первую задачу.</div>`;
    return;
  }
  container.innerHTML = state.tasks.map(t => `
    <div class="card">
      <div class="card-id">${escHtml(t.task_id)}</div>
      <div class="card-text">${escHtml(t.source_text)}</div>
      ${t.owner_goal ? `<div class="card-text" style="color:var(--text-secondary);font-size:12px">🎯 ${escHtml(t.owner_goal)}</div>` : ''}
      <div class="card-meta">
        ${statusBadge(t.status)}
        ${priorityBadge(t.priority || 'MEDIUM')}
        <span class="card-time">${fmtTime(t.created_at)}</span>
        ${t.seed_demo ? '<span class="s-badge" style="color:var(--text-muted);border-color:var(--text-muted)">SEED</span>' : ''}
        <button class="btn btn-sm btn-primary" onclick="loadThread('${escHtml(t.task_id)}')">🧵 Thread</button>
      </div>
      ${t.tags && t.tags.length ? `<div class="tag-list">${t.tags.map(tag => `<span class="tag">${escHtml(tag)}</span>`).join('')}</div>` : ''}
    </div>`).join('');
}

function renderComments() {
  const container = document.getElementById('comments-list');
  if (!container) return;
  if (state.comments.length === 0) {
    container.innerHTML = `<div class="empty-state"><div class="empty-icon">💬</div>Комментариев пока нет.</div>`;
    return;
  }
  container.innerHTML = state.comments.map(c => `
    <div class="card">
      <div class="card-id">${escHtml(c.comment_id)}</div>
      <div class="card-text">${escHtml(c.original_text)}</div>
      ${c.interpreted_meaning ? `<div class="card-text" style="color:var(--text-secondary);font-size:12px">🔍 ${escHtml(c.interpreted_meaning)}</div>` : ''}
      <div class="card-meta">
        ${statusBadge(c.status)}
        <span class="s-badge" style="color:var(--accent-purple);border-color:var(--accent-purple)">${escHtml(c.comment_type || 'OBSERVATION')}</span>
        <span class="card-time">${fmtTime(c.created_at)}</span>
        ${c.seed_demo ? '<span class="s-badge" style="color:var(--text-muted);border-color:var(--text-muted)">SEED</span>' : ''}
      </div>
      ${c.linked_tasks && c.linked_tasks.length ? `<div style="font-size:11px;color:var(--text-muted);margin-top:6px">🔗 Linked: ${c.linked_tasks.map(id => `<span class="tag">${escHtml(id)}</span>`).join(' ')}</div>` : ''}
    </div>`).join('');
}

function renderLinks() {
  const container = document.getElementById('links-list');
  if (!container) return;
  if (state.links.length === 0) {
    container.innerHTML = `<div class="empty-state"><div class="empty-icon">🔗</div>Связей пока нет.</div>`;
    return;
  }
  container.innerHTML = state.links.map(l => `
    <div class="card">
      <div class="card-id">${escHtml(l.link_id)}</div>
      <div class="card-text" style="font-size:12px">
        <span style="color:var(--accent-cyan)">${escHtml(l.source_type)}</span>
        <span style="color:var(--text-muted)"> ${escHtml(l.source_id)} </span>
        <span style="color:var(--accent-purple)">→</span>
        <span style="color:var(--accent-green)"> ${escHtml(l.target_type)}</span>
        <span style="color:var(--text-muted)"> ${escHtml(l.target_id)}</span>
      </div>
      ${l.link_reason ? `<div class="card-text" style="color:var(--text-secondary);font-size:12px">📎 ${escHtml(l.link_reason)}</div>` : ''}
      <div class="card-meta">
        ${statusBadge(l.status)}
        <span class="s-badge" style="color:var(--text-muted);border-color:var(--text-muted)">${escHtml(l.verification_status || 'UNVERIFIED')}</span>
        <span class="card-time">${fmtTime(l.created_at)}</span>
        ${l.seed_demo ? '<span class="s-badge" style="color:var(--text-muted);border-color:var(--text-muted)">SEED</span>' : ''}
      </div>
    </div>`).join('');
}

function populateSelects() {
  // Task select for link creation
  const taskSel = document.getElementById('link-task-select');
  if (taskSel) {
    const cur = taskSel.value;
    taskSel.innerHTML = '<option value="">— выберите задачу —</option>' +
      state.tasks.map(t => `<option value="${escHtml(t.task_id)}">${escHtml(t.task_id.slice(0,22))} — ${escHtml(t.source_text.slice(0,30))}…</option>`).join('');
    if (cur) taskSel.value = cur;
  }

  // Comment select for link creation
  const commentSel = document.getElementById('link-comment-select');
  if (commentSel) {
    const cur = commentSel.value;
    commentSel.innerHTML = '<option value="">— выберите комментарий —</option>' +
      state.comments.map(c => `<option value="${escHtml(c.comment_id)}">${escHtml(c.comment_id.slice(0,22))} — ${escHtml(c.original_text.slice(0,30))}…</option>`).join('');
    if (cur) commentSel.value = cur;
  }

  // Thread task select
  const threadSel = document.getElementById('thread-task-select');
  if (threadSel) {
    const cur = threadSel.value;
    threadSel.innerHTML = '<option value="">— выберите задачу —</option>' +
      state.tasks.map(t => `<option value="${escHtml(t.task_id)}">${escHtml(t.task_id.slice(0,22))} — ${escHtml(t.source_text.slice(0,40))}…</option>`).join('');
    if (cur) threadSel.value = cur;
  }
}

// ── Form handlers ─────────────────────────────────────────────────────────────

async function submitTask(e) {
  e.preventDefault();
  const form = e.target;
  const btn = form.querySelector('button[type=submit]');
  const sourceText = form.querySelector('#task-source-text').value.trim();
  const ownerGoal  = form.querySelector('#task-owner-goal').value.trim();
  const priority   = form.querySelector('#task-priority').value;
  const tagsRaw    = form.querySelector('#task-tags').value.trim();
  const tags = tagsRaw ? tagsRaw.split(',').map(t => t.trim()).filter(Boolean) : [];

  if (!sourceText) { notify('error', 'Введите текст задачи'); return; }

  btn.disabled = true;
  btn.innerHTML = '<span class="spinner"></span> Создание…';

  try {
    const task = await apiPost('/api/tasks', { source_text: sourceText, owner_goal: ownerGoal || null, priority, tags });
    state.tasks.push(task);
    renderAll();
    form.reset();
    notify('success', `Задача принята: ${task.status}`, task.task_id);
  } catch (err) {
    notify('error', 'Ошибка создания задачи: ' + err.message);
  } finally {
    btn.disabled = false;
    btn.innerHTML = '⚡ Принять задачу';
  }
}

async function submitComment(e) {
  e.preventDefault();
  const form = e.target;
  const btn = form.querySelector('button[type=submit]');
  const originalText = form.querySelector('#comment-text').value.trim();
  const commentType  = form.querySelector('#comment-type').value;
  const interpreted  = form.querySelector('#comment-interpreted').value.trim();

  if (!originalText) { notify('error', 'Введите текст комментария'); return; }

  btn.disabled = true;
  btn.innerHTML = '<span class="spinner"></span> Захват…';

  try {
    const comment = await apiPost('/api/comments', {
      original_text: originalText,
      comment_type: commentType,
      interpreted_meaning: interpreted || null
    });
    state.comments.push(comment);
    renderAll();
    form.reset();
    notify('success', `Комментарий захвачен: ${comment.status}`, comment.comment_id);
  } catch (err) {
    notify('error', 'Ошибка создания комментария: ' + err.message);
  } finally {
    btn.disabled = false;
    btn.innerHTML = '💬 Захватить комментарий';
  }
}

async function submitLink(e) {
  e.preventDefault();
  const form = e.target;
  const btn = form.querySelector('button[type=submit]');
  const taskId    = form.querySelector('#link-task-select').value;
  const commentId = form.querySelector('#link-comment-select').value;
  const reason    = form.querySelector('#link-reason').value.trim();

  if (!taskId || !commentId) { notify('error', 'Выберите задачу и комментарий'); return; }

  btn.disabled = true;
  btn.innerHTML = '<span class="spinner"></span> Связывание…';

  try {
    const link = await apiPost('/api/links', {
      source_type: 'TASK',
      source_id: taskId,
      target_type: 'COMMENT',
      target_id: commentId,
      link_reason: reason || null
    });
    state.links.push(link);
    // Refresh comments to get updated LINKED status
    state.comments = await apiGet('/api/comments');
    state.tasks    = await apiGet('/api/tasks');
    renderAll();
    form.reset();
    notify('success', `Связь создана: ${link.status}`, link.link_id);
  } catch (err) {
    notify('error', 'Ошибка создания связи: ' + err.message);
  } finally {
    btn.disabled = false;
    btn.innerHTML = '🔗 Создать связь';
  }
}

// ── Thread view ───────────────────────────────────────────────────────────────

async function loadThread(taskId) {
  if (!taskId) {
    taskId = document.getElementById('thread-task-select')?.value;
  }
  if (!taskId) { notify('info', 'Выберите задачу для просмотра thread'); return; }

  const container = document.getElementById('thread-content');
  if (!container) return;
  container.innerHTML = '<div style="color:var(--text-muted);padding:16px"><span class="spinner"></span> Загрузка thread…</div>';

  try {
    const thread = await apiGet(`/api/thread/${encodeURIComponent(taskId)}`);
    renderThread(thread, container);
  } catch (err) {
    container.innerHTML = `<div class="empty-state"><div class="empty-icon">⚠️</div>${escHtml(err.message)}</div>`;
  }
}

function renderThread(thread, container) {
  const t = thread.task;
  const links = thread.links || [];
  const comments = thread.comments || [];
  const receipts = thread.receipts || [];

  let html = `
    <div class="thread-task-header">
      <div class="card-id">${escHtml(t.task_id)}</div>
      <div class="card-text" style="font-size:15px;font-weight:600">${escHtml(t.source_text)}</div>
      ${t.owner_goal ? `<div style="color:var(--text-secondary);font-size:12px;margin-top:4px">🎯 ${escHtml(t.owner_goal)}</div>` : ''}
      <div class="card-meta" style="margin-top:8px">
        ${statusBadge(t.status)}
        ${priorityBadge(t.priority || 'MEDIUM')}
        <span class="card-time">${fmtTime(t.created_at)}</span>
      </div>
    </div>`;

  if (links.length > 0) {
    html += `<div class="thread-section-title">🔗 Memory Links (${links.length})</div>`;
    html += links.map(l => `
      <div class="card" style="margin-bottom:8px">
        <div class="card-id">${escHtml(l.link_id)}</div>
        <div class="card-text" style="font-size:12px">
          ${escHtml(l.source_type)} <span style="color:var(--text-muted)">${escHtml(l.source_id)}</span>
          <span style="color:var(--accent-purple)"> → </span>
          ${escHtml(l.target_type)} <span style="color:var(--text-muted)">${escHtml(l.target_id)}</span>
        </div>
        <div class="card-meta">${statusBadge(l.status)}<span class="card-time">${fmtTime(l.created_at)}</span></div>
      </div>`).join('');
  }

  if (comments.length > 0) {
    html += `<div class="thread-section-title">💬 Owner Comments (${comments.length})</div>`;
    html += comments.map(c => `
      <div class="card" style="margin-bottom:8px">
        <div class="card-id">${escHtml(c.comment_id)}</div>
        <div class="card-text">${escHtml(c.original_text)}</div>
        ${c.interpreted_meaning ? `<div style="color:var(--text-secondary);font-size:12px">🔍 ${escHtml(c.interpreted_meaning)}</div>` : ''}
        <div class="card-meta">${statusBadge(c.status)}<span class="card-time">${fmtTime(c.created_at)}</span></div>
      </div>`).join('');
  }

  if (receipts.length > 0) {
    html += `<div class="thread-section-title">🧾 Receipts (${receipts.length})</div>`;
    html += receipts.map(r => `
      <div class="receipt-item">
        <span class="receipt-icon">✅</span>
        <span class="receipt-id">${escHtml(r.receipt_id)}</span>
        <span class="receipt-event">${escHtml(r.event_type)}</span>
        <span class="receipt-time">${fmtTime(r.created_at)}</span>
      </div>`).join('');
  }

  if (links.length === 0 && comments.length === 0) {
    html += `<div class="thread-empty">Нет связанных комментариев. Создайте связь через панель Memory Links.</div>`;
  }

  container.innerHTML = html;
}

// ── Export ────────────────────────────────────────────────────────────────────

async function doExport() {
  const btn = document.getElementById('btn-export');
  if (btn) { btn.disabled = true; btn.innerHTML = '<span class="spinner"></span> Экспорт…'; }
  try {
    const result = await apiPost('/api/export', {});
    notify('success', `Экспорт создан: ${result.export_id}`, result.export_id);
  } catch (err) {
    notify('error', 'Ошибка экспорта: ' + err.message);
  } finally {
    if (btn) { btn.disabled = false; btn.innerHTML = '📦 Экспорт пакета'; }
  }
}

// ── Refresh ───────────────────────────────────────────────────────────────────

async function doRefresh() {
  const btn = document.getElementById('btn-refresh');
  if (btn) { btn.disabled = true; }
  await loadAll();
  if (btn) { btn.disabled = false; }
  notify('info', 'Данные обновлены');
}

// ── Init ──────────────────────────────────────────────────────────────────────

document.addEventListener('DOMContentLoaded', () => {
  // Attach form handlers
  const taskForm    = document.getElementById('form-task');
  const commentForm = document.getElementById('form-comment');
  const linkForm    = document.getElementById('form-link');

  if (taskForm)    taskForm.addEventListener('submit', submitTask);
  if (commentForm) commentForm.addEventListener('submit', submitComment);
  if (linkForm)    linkForm.addEventListener('submit', submitLink);

  // Load initial data
  loadAll();

  // Auto-refresh every 30s
  setInterval(loadAll, 30000);
});
