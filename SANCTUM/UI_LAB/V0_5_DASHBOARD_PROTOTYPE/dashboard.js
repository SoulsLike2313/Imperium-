'use strict';

const REQUIRED_BUTTON_IDS = [
  'btn-toggle-orbit-animation',
  'btn-show-all-organs',
  'btn-show-guide-organs',
  'btn-show-warnings',
  'btn-filter-assets-accepted',
  'btn-filter-assets-candidate',
  'btn-filter-assets-rejected',
  'btn-clear-asset-filters',
  'btn-show-route-policy',
  'btn-show-action-registry',
  'btn-show-reports',
  'btn-compact-mode-toggle',
  'btn-clear-console'
];

const GUIDE_ORGANS = ['DOCTRINARIUM', 'ADMINISTRATUM', 'ASTRONOMICON', 'OFFICIO_AGENTIS'];

const FALLBACK_DATA = {
  schema_version: 'imperium.sanctum_dashboard_data.v0_5.fallback',
  task_id: 'TASK-20260513-SANCTUM-DASHBOARD-V0_5-WORKING-PROTOTYPE',
  generated_at: new Date().toISOString(),
  git_truth_snapshot: {
    expected_head: 'b06d312bc2dc666523468cba727e4c8e4520dc8e',
    local_head: 'UNKNOWN',
    latest_commit: 'UNKNOWN'
  },
  gate_truth: {
    ready_for_agent: false,
    act5_execution_ready: false
  },
  organ_index: [
    { organ_id: 'CUSTODES', display_name: 'Custodes', role_summary: 'Protection contour guard.', status: 'UNKNOWN', readiness_level: 'UNKNOWN', primary_files: [], related_reports: [], available_actions: [], warnings: ['fallback_data_only'] },
    { organ_id: 'INQUISITION', display_name: 'Inquisition', role_summary: 'Audit/drift detector.', status: 'NOT_BUILT', readiness_level: 'UNKNOWN', primary_files: [], related_reports: [], available_actions: [], warnings: ['future_target'] },
    { organ_id: 'MECHANICUS', display_name: 'Mechanicus', role_summary: 'Tooling and machinery contracts.', status: 'UNKNOWN', readiness_level: 'UNKNOWN', primary_files: [], related_reports: [], available_actions: [], warnings: ['fallback_data_only'] },
    { organ_id: 'ADMINISTRATUM', display_name: 'Administratum', role_summary: 'Continuity and ACK lane.', status: 'PARTIAL', readiness_level: 'LEVEL_5_ACT5_GUIDE_MINIMAL_READY', primary_files: [], related_reports: [], available_actions: [], warnings: [] },
    { organ_id: 'ASTRONOMICON', display_name: 'Astronomicon', role_summary: 'Planning and registration corridor.', status: 'PARTIAL', readiness_level: 'LEVEL_5_ACT5_GUIDE_MINIMAL_READY', primary_files: [], related_reports: [], available_actions: [], warnings: [] },
    { organ_id: 'STRATEGIUM', display_name: 'Strategium', role_summary: 'Improvement advisory research.', status: 'UNKNOWN', readiness_level: 'UNKNOWN', primary_files: [], related_reports: [], available_actions: [], warnings: ['fallback_data_only'] },
    { organ_id: 'OFFICIO_AGENTIS', display_name: 'Officio Agentis', role_summary: 'Authority and role limits.', status: 'PARTIAL', readiness_level: 'LEVEL_4_CHECKABLE', primary_files: [], related_reports: [], available_actions: [], warnings: ['below_target_level_5'] },
    { organ_id: 'THRONE', display_name: 'Throne', role_summary: 'Owner acceptance boundary.', status: 'UNKNOWN', readiness_level: 'UNKNOWN', primary_files: [], related_reports: [], available_actions: [], warnings: ['fallback_data_only'] },
    { organ_id: 'SCHOLA_IMPERIALIS', display_name: 'Schola Imperialis', role_summary: 'Lessons and training continuity.', status: 'UNKNOWN', readiness_level: 'UNKNOWN', primary_files: [], related_reports: [], available_actions: [], warnings: ['fallback_data_only'] },
    { organ_id: 'DOCTRINARIUM', display_name: 'Doctrinarium', role_summary: 'Doctrine and law guard.', status: 'PARTIAL', readiness_level: 'LEVEL_5_ACT5_GUIDE_MINIMAL_READY', primary_files: [], related_reports: [], available_actions: [], warnings: [] }
  ],
  action_index: [],
  bundle_route: {
    canonical_vm2_outbox: '/home/vboxuser2/IMPERIUM_WORK/VM2_BUNDLES/',
    canonical_pc_inbox: 'E:\\IMPERIUM\\INBOX\\VM2_BUNDLES\\',
    legacy_scan_dirs: [
      '/home/vboxuser2/IMPERIUM_WORK/_handoff_out/',
      '/home/vboxuser2/IMPERIUM_PRIVATE/OUTBOX/'
    ],
    source_priority_order: [
      '/home/vboxuser2/IMPERIUM_WORK/VM2_BUNDLES/',
      '/home/vboxuser2/IMPERIUM_WORK/_handoff_out/',
      '/home/vboxuser2/IMPERIUM_PRIVATE/OUTBOX/'
    ],
    owner_rule: 'canonical VM2_BUNDLES is mandatory primary source'
  },
  asset_summary: {
    total_assets: 0,
    proposed_accepted: 0,
    proposed_rejected: 0,
    proposed_candidate: 0,
    owner_confirmation_required: true,
    top_categories: [],
    interpretation_cards_count: 0
  },
  asset_cards: [],
  reports_index: [],
  warnings: ['Fallback mode active: dashboard_data.json could not be loaded.'],
  ui_capabilities: {
    implemented_buttons: REQUIRED_BUTTON_IDS,
    disabled_or_planned: ['real_backend_fetch_bundle_bridge']
  },
  visual_rules_tokens_summary: {
    rules_preview: 'No rules loaded in fallback mode.',
    tokens_status: 'missing_or_unknown',
    tokens_roles: []
  }
};

const state = {
  data: FALLBACK_DATA,
  usingFallback: true,
  selectedOrganId: null,
  showGuideOnly: false,
  actionFilterMode: 'all',
  actionSearch: '',
  assetFilterStatus: 'all',
  routeFilterMode: 'all',
  compact: false
};

function ts() {
  return new Date().toISOString();
}

function logConsole(message) {
  const consoleEl = document.getElementById('evidence-console');
  if (!consoleEl) {
    return;
  }
  consoleEl.textContent += `[${ts()}] ${message}\n`;
  consoleEl.scrollTop = consoleEl.scrollHeight;
}

function summarizeWarningsCount(data) {
  const topWarnings = Array.isArray(data.warnings) ? data.warnings.length : 0;
  const organWarnings = Array.isArray(data.organ_index)
    ? data.organ_index.reduce((acc, organ) => acc + (Array.isArray(organ.warnings) ? organ.warnings.length : 0), 0)
    : 0;
  return topWarnings + organWarnings;
}

function escapeHtml(value) {
  return String(value)
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#39;');
}

function renderTruthBar() {
  const data = state.data;
  const headEl = document.getElementById('truth-head');
  const taskEl = document.getElementById('truth-task');
  const warnEl = document.getElementById('truth-warnings');

  if (taskEl) {
    taskEl.textContent = data.task_id || 'UNKNOWN_TASK';
  }
  if (headEl) {
    headEl.textContent = (data.git_truth_snapshot && data.git_truth_snapshot.expected_head) || 'UNKNOWN';
  }
  if (warnEl) {
    warnEl.textContent = String(summarizeWarningsCount(data));
  }
}

function organListFiltered() {
  const organs = Array.isArray(state.data.organ_index) ? state.data.organ_index : [];
  if (!state.showGuideOnly) {
    return organs;
  }
  return organs.filter((organ) => GUIDE_ORGANS.includes(organ.organ_id));
}

function renderOrbitMap() {
  const nodeLayer = document.getElementById('organ-nodes');
  const svg = document.getElementById('orbit-lines');
  if (!nodeLayer || !svg) {
    return;
  }

  nodeLayer.innerHTML = '';
  svg.innerHTML = '';

  const organs = organListFiltered();
  const centerX = 50;
  const centerY = 50;
  const radius = 38;

  organs.forEach((organ, idx) => {
    const angle = (Math.PI * 2 * idx) / organs.length;
    const x = centerX + radius * Math.cos(angle);
    const y = centerY + radius * Math.sin(angle);

    const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
    line.setAttribute('x1', `${centerX}%`);
    line.setAttribute('y1', `${centerY}%`);
    line.setAttribute('x2', `${x}%`);
    line.setAttribute('y2', `${y}%`);
    line.setAttribute('stroke', GUIDE_ORGANS.includes(organ.organ_id) ? 'rgba(117,243,210,0.35)' : 'rgba(117,185,236,0.25)');
    line.setAttribute('stroke-width', '1');
    svg.appendChild(line);

    const node = document.createElement('button');
    node.type = 'button';
    node.className = `organ-node${GUIDE_ORGANS.includes(organ.organ_id) ? ' guide' : ''}${state.selectedOrganId === organ.organ_id ? ' selected' : ''}`;
    node.style.left = `${x}%`;
    node.style.top = `${y}%`;
    node.innerHTML = `<div>${escapeHtml(organ.display_name || organ.organ_id)}</div><div class="id">${escapeHtml(organ.status || 'UNKNOWN')}</div>`;
    node.addEventListener('click', () => {
      state.selectedOrganId = organ.organ_id;
      renderOrbitMap();
      renderOrganDetail();
      logConsole(`Organ selected: ${organ.organ_id} (${organ.status || 'UNKNOWN'})`);
    });
    nodeLayer.appendChild(node);
  });

  if (!state.selectedOrganId && organs.length > 0) {
    state.selectedOrganId = organs[0].organ_id;
    renderOrganDetail();
  }
}

function renderOrganDetail() {
  const target = document.getElementById('organ-detail');
  if (!target) {
    return;
  }
  const organs = Array.isArray(state.data.organ_index) ? state.data.organ_index : [];
  const organ = organs.find((item) => item.organ_id === state.selectedOrganId) || organs[0];
  if (!organ) {
    target.innerHTML = '<div class="card">No organ data available.</div>';
    return;
  }

  const files = Array.isArray(organ.primary_files) ? organ.primary_files : [];
  const actions = Array.isArray(organ.available_actions) ? organ.available_actions : [];
  const warnings = Array.isArray(organ.warnings) ? organ.warnings : [];
  const reports = Array.isArray(organ.related_reports) ? organ.related_reports : [];

  target.innerHTML = `
    <div class="card">
      <div class="title"><strong>${escapeHtml(organ.display_name || organ.organ_id)}</strong></div>
      <div class="meta">ID: ${escapeHtml(organ.organ_id || 'UNKNOWN')}</div>
      <div class="meta">Status: ${escapeHtml(organ.status || 'UNKNOWN')}</div>
      <div class="meta">Readiness: ${escapeHtml(organ.readiness_level || 'UNKNOWN')}</div>
      <p>${escapeHtml(organ.role_summary || 'No role summary')}</p>
      <div class="meta"><strong>Primary files:</strong><br>${files.map((path) => escapeHtml(path)).join('<br>') || '(none)'}</div>
      <div class="meta"><strong>Available actions:</strong> ${actions.join(', ') || '(none)'}</div>
      <div class="meta"><strong>Related reports:</strong><br>${reports.map((path) => escapeHtml(path)).join('<br>') || '(none)'}</div>
      <div class="warn-list"><strong>Warnings:</strong> ${warnings.join('; ') || 'none'}</div>
    </div>
  `;
}

function actionVisible(action) {
  if (state.actionFilterMode === 'high') {
    return String(action.risk_level || '').startsWith('HIGH');
  }
  if (state.actionFilterMode === 'blocked') {
    const status = String(action.status || '').toUpperCase();
    return status.includes('BLOCKED') || status.includes('NEEDS') || status.includes('CONCEPT');
  }
  return true;
}

function actionSearchHit(action) {
  if (!state.actionSearch) {
    return true;
  }
  const hay = [
    action.action_id,
    action.title,
    action.risk_level,
    action.category,
    action.status,
    action.handler_reference
  ].join(' ').toLowerCase();
  return hay.includes(state.actionSearch.toLowerCase());
}

function renderActionList() {
  const target = document.getElementById('action-list');
  if (!target) {
    return;
  }
  const actions = Array.isArray(state.data.action_index) ? state.data.action_index : [];
  const filtered = actions.filter((item) => actionVisible(item) && actionSearchHit(item));

  if (filtered.length === 0) {
    target.innerHTML = '<div class="card">No actions for current filter.</div>';
    return;
  }

  target.innerHTML = '';
  filtered.forEach((action) => {
    const row = document.createElement('div');
    row.className = 'list-row';
    row.innerHTML = `
      <div class="id">${escapeHtml(action.action_id || 'UNKNOWN_ACTION')}</div>
      <div class="title">${escapeHtml(action.title || 'Untitled action')}</div>
      <div class="meta">status=${escapeHtml(action.status || 'UNKNOWN')} | risk=${escapeHtml(action.risk_level || 'UNKNOWN')} | category=${escapeHtml(action.category || 'UNKNOWN')}</div>
      <div class="meta">handler=${escapeHtml(action.handler_reference || 'UNKNOWN')}</div>
      <div class="meta">test=${escapeHtml(action.test_status || 'UNKNOWN')}</div>
    `;
    row.addEventListener('click', () => {
      logConsole(`Action selected: ${action.action_id} | risk=${action.risk_level} | status=${action.status}`);
    });
    target.appendChild(row);
  });
}

function renderBundleRoute() {
  const target = document.getElementById('bundle-route');
  if (!target) {
    return;
  }

  const route = state.data.bundle_route || {};
  const legacy = Array.isArray(route.legacy_scan_dirs) ? route.legacy_scan_dirs : [];
  const sourcePriority = Array.isArray(route.source_priority_order) ? route.source_priority_order : [];

  let visibleSources = sourcePriority;
  if (state.routeFilterMode === 'canonical') {
    visibleSources = sourcePriority.slice(0, 1);
  }
  if (state.routeFilterMode === 'legacy') {
    visibleSources = sourcePriority.filter((path) => path !== route.canonical_vm2_outbox);
  }

  target.innerHTML = `
    <div class="card">
      <div><strong>Canonical VM2 outbox</strong><br>${escapeHtml(route.canonical_vm2_outbox || 'UNKNOWN')}</div>
      <div class="meta"><strong>Canonical PC inbox</strong><br>${escapeHtml(route.canonical_pc_inbox || 'UNKNOWN')}</div>
      <div class="meta"><strong>Owner rule</strong><br>${escapeHtml(route.owner_rule || 'UNKNOWN')}</div>
      <div class="meta"><strong>Legacy scan dirs</strong><br>${legacy.map((item) => escapeHtml(item)).join('<br>') || '(none)'}</div>
      <div class="meta"><strong>Source priority shown</strong><br>${visibleSources.map((item) => escapeHtml(item)).join('<br>') || '(none)'}</div>
    </div>
  `;
}

function assetVisible(card) {
  if (state.assetFilterStatus === 'all') {
    return true;
  }
  return String(card.proposed_status || '').toLowerCase() === state.assetFilterStatus;
}

function renderAssetSummary() {
  const target = document.getElementById('asset-summary');
  if (!target) {
    return;
  }
  const summary = state.data.asset_summary || {};
  const categories = Array.isArray(summary.top_categories) ? summary.top_categories : [];

  target.innerHTML = `
    <div class="card">
      <div><strong>Total assets:</strong> ${escapeHtml(summary.total_assets ?? '0')}</div>
      <div class="meta">proposed accepted=${escapeHtml(summary.proposed_accepted ?? '0')} | proposed candidate=${escapeHtml(summary.proposed_candidate ?? '0')} | proposed rejected=${escapeHtml(summary.proposed_rejected ?? '0')}</div>
      <div class="meta">interpretation cards=${escapeHtml(summary.interpretation_cards_count ?? '0')}</div>
      <div class="meta">owner confirmation required=${escapeHtml(String(summary.owner_confirmation_required))}</div>
      <div class="meta">top categories: ${categories.map((item) => `${escapeHtml(item.category)}(${escapeHtml(item.count)})`).join(', ') || '(none)'}</div>
    </div>
  `;
}

function renderAssetCards() {
  const listEl = document.getElementById('asset-cards');
  const detailEl = document.getElementById('asset-detail');
  if (!listEl || !detailEl) {
    return;
  }

  const cards = Array.isArray(state.data.asset_cards) ? state.data.asset_cards : [];
  const filtered = cards.filter((card) => assetVisible(card));

  if (filtered.length === 0) {
    listEl.innerHTML = '<div class="card">No asset cards for current filter.</div>';
    detailEl.innerHTML = '<div class="card">Select a card to inspect interpretation details.</div>';
    return;
  }

  listEl.innerHTML = '';
  filtered.forEach((card, idx) => {
    const row = document.createElement('div');
    row.className = 'list-row';
    const status = String(card.proposed_status || 'candidate');
    row.innerHTML = `
      <div class="id">${escapeHtml(card.card_file || `CARD_${idx}`)}</div>
      <div class="title">${escapeHtml(card.image_path || 'UNKNOWN_IMAGE')}</div>
      <div>
        <span class="asset-tag ${escapeHtml(status)}">${escapeHtml(status)}</span>
        <span class="asset-tag">${escapeHtml(card.confidence || 'unknown')}</span>
      </div>
      <div class="meta">categories: ${(Array.isArray(card.categories) ? card.categories : []).map((c) => escapeHtml(c)).join(', ') || '(none)'}</div>
    `;

    row.addEventListener('click', () => {
      detailEl.innerHTML = `
        <div class="card">
          <div><strong>Card:</strong> ${escapeHtml(card.card_file || '')}</div>
          <div class="meta"><strong>Image path:</strong> ${escapeHtml(card.image_path || '')}</div>
          <div class="meta"><strong>Source type:</strong> ${escapeHtml(card.source_type || 'unknown')}</div>
          <div class="meta"><strong>Detected markings:</strong> ${escapeHtml(card.detected_markings || 'unknown')}</div>
          <div class="meta"><strong>Liked (suspected):</strong> ${escapeHtml(card.suspected_liked_elements || '')}</div>
          <div class="meta"><strong>Disliked (suspected):</strong> ${escapeHtml(card.suspected_disliked_elements || '')}</div>
          <div class="meta"><strong>Questions for Owner:</strong> ${escapeHtml(card.questions_for_owner || '')}</div>
          <div class="warn-list">Interpretation proposal only. Owner confirmation required before canon promotion.</div>
        </div>
      `;
      logConsole(`Asset card opened: ${card.card_file}`);
    });
    listEl.appendChild(row);
  });

  if (!detailEl.innerHTML.trim()) {
    detailEl.innerHTML = '<div class="card">Select a card to inspect interpretation details.</div>';
  }
}

function renderReports() {
  const listEl = document.getElementById('reports-list');
  const detailEl = document.getElementById('report-detail');
  if (!listEl || !detailEl) {
    return;
  }

  const reports = Array.isArray(state.data.reports_index) ? state.data.reports_index : [];
  if (reports.length === 0) {
    listEl.innerHTML = '<div class="card">No reports indexed.</div>';
    detailEl.innerHTML = '<div class="card">No report details available.</div>';
    return;
  }

  listEl.innerHTML = '';
  reports.forEach((report) => {
    const row = document.createElement('div');
    row.className = 'list-row';
    row.innerHTML = `
      <div class="title">${escapeHtml(report.title || 'Untitled report')}</div>
      <div class="meta">${escapeHtml(report.path || '')}</div>
    `;
    row.addEventListener('click', () => {
      detailEl.innerHTML = `
        <div class="card">
          <div><strong>${escapeHtml(report.title || 'Untitled report')}</strong></div>
          <div class="meta">Path: ${escapeHtml(report.path || '')}</div>
          <p>${escapeHtml(report.summary || 'No summary')}</p>
        </div>
      `;
      logConsole(`Report selected: ${report.path || report.title}`);
    });
    listEl.appendChild(row);
  });

  detailEl.innerHTML = '<div class="card">Click a report to inspect path and summary.</div>';
}

function renderRulesPanel() {
  const rules = state.data.visual_rules_tokens_summary || {};
  const target = document.getElementById('rules-panel');
  if (!target) {
    return;
  }
  target.innerHTML = `
    <div class="card">
      <div><strong>Tokens status:</strong> ${escapeHtml(rules.tokens_status || 'unknown')}</div>
      <div class="meta"><strong>Token roles:</strong> ${(Array.isArray(rules.tokens_roles) ? rules.tokens_roles : []).map((item) => escapeHtml(item)).join(', ') || '(none)'}</div>
      <div class="meta"><strong>Rules preview:</strong></div>
      <pre class="console">${escapeHtml(rules.rules_preview || 'No rules preview available')}</pre>
    </div>
  `;
}

function showPanel(selector) {
  const panel = document.querySelector(selector);
  if (!panel) {
    return;
  }
  panel.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

function bindButtons() {
  const map = {
    'btn-toggle-orbit-animation': () => {
      const orbit = document.getElementById('orbit-map');
      if (!orbit) {
        return;
      }
      orbit.classList.toggle('animate');
      logConsole(`Orbit animation toggled: ${orbit.classList.contains('animate') ? 'ON' : 'OFF'}`);
    },
    'btn-show-all-organs': () => {
      state.showGuideOnly = false;
      renderOrbitMap();
      logConsole('Organ filter set: all organs');
    },
    'btn-show-guide-organs': () => {
      state.showGuideOnly = true;
      renderOrbitMap();
      logConsole('Organ filter set: first four guide organs');
    },
    'btn-show-warnings': () => {
      const warnings = Array.isArray(state.data.warnings) ? state.data.warnings : [];
      logConsole(`Warnings (${warnings.length}): ${warnings.join(' | ') || 'none'}`);
      showPanel('.console-zone');
    },
    'btn-filter-assets-accepted': () => {
      state.assetFilterStatus = 'accepted';
      renderAssetCards();
      logConsole('Asset filter: accepted');
    },
    'btn-filter-assets-candidate': () => {
      state.assetFilterStatus = 'candidate';
      renderAssetCards();
      logConsole('Asset filter: candidate');
    },
    'btn-filter-assets-rejected': () => {
      state.assetFilterStatus = 'rejected';
      renderAssetCards();
      logConsole('Asset filter: rejected');
    },
    'btn-clear-asset-filters': () => {
      state.assetFilterStatus = 'all';
      renderAssetCards();
      logConsole('Asset filter cleared');
    },
    'btn-show-route-policy': () => {
      showPanel('.bundle-zone');
      renderBundleRoute();
      logConsole('Route policy panel focused');
    },
    'btn-show-action-registry': () => {
      showPanel('.action-zone');
      renderActionList();
      logConsole('Action registry panel focused');
    },
    'btn-show-reports': () => {
      showPanel('.reports-zone');
      renderReports();
      logConsole('Reports panel focused');
    },
    'btn-compact-mode-toggle': () => {
      state.compact = !state.compact;
      document.body.classList.toggle('compact', state.compact);
      logConsole(`Compact mode: ${state.compact ? 'ON' : 'OFF'}`);
    },
    'btn-clear-console': () => {
      const consoleEl = document.getElementById('evidence-console');
      if (consoleEl) {
        consoleEl.textContent = '';
      }
      logConsole('Console cleared');
    },
    'btn-refresh-bundle-snapshot': () => {
      renderBundleRoute();
      logConsole('Bundle snapshot refreshed from dashboard_data');
    },
    'btn-filter-route-canonical': () => {
      state.routeFilterMode = 'canonical';
      renderBundleRoute();
      logConsole('Route view: canonical only');
    },
    'btn-filter-route-legacy': () => {
      state.routeFilterMode = 'legacy';
      renderBundleRoute();
      logConsole('Route view: legacy only');
    },
    'btn-filter-route-clear': () => {
      state.routeFilterMode = 'all';
      renderBundleRoute();
      logConsole('Route view: all sources');
    },
    'btn-filter-action-high': () => {
      state.actionFilterMode = 'high';
      renderActionList();
      logConsole('Action filter: high risk');
    },
    'btn-filter-action-blocked': () => {
      state.actionFilterMode = 'blocked';
      renderActionList();
      logConsole('Action filter: blocked/planned');
    },
    'btn-filter-action-clear': () => {
      state.actionFilterMode = 'all';
      renderActionList();
      logConsole('Action filter cleared');
    }
  };

  Object.entries(map).forEach(([id, fn]) => {
    const el = document.getElementById(id);
    if (!el) {
      return;
    }
    el.addEventListener('click', fn);
  });

  const search = document.getElementById('action-search');
  if (search) {
    search.addEventListener('input', () => {
      state.actionSearch = search.value.trim();
      renderActionList();
    });
  }

  return map;
}

async function loadData() {
  try {
    const response = await fetch('dashboard_data.json', { cache: 'no-store' });
    if (!response.ok) {
      throw new Error(`HTTP_${response.status}`);
    }
    const payload = await response.json();
    state.data = payload;
    state.usingFallback = false;
    logConsole('dashboard_data.json loaded successfully');
  } catch (error) {
    state.data = FALLBACK_DATA;
    state.usingFallback = true;
    logConsole(`Fallback data enabled (${String(error)})`);
  }
}

function renderEverything() {
  renderTruthBar();
  renderOrbitMap();
  renderActionList();
  renderBundleRoute();
  renderAssetSummary();
  renderAssetCards();
  renderReports();
  renderRulesPanel();

  if (state.usingFallback) {
    const warnings = state.data.warnings || [];
    warnings.push('Live data unavailable: using fallback snapshot.');
    state.data.warnings = warnings;
    renderTruthBar();
  }
}

async function bootstrap() {
  const handlerMap = bindButtons();
  REQUIRED_BUTTON_IDS.forEach((id) => {
    if (!handlerMap[id]) {
      logConsole(`Missing required handler mapping for ${id}`);
    }
  });

  await loadData();
  renderEverything();

  logConsole('Sanctum Dashboard v0.5 prototype initialized.');
  logConsole(`Gate truth: READY_FOR_AGENT=${state.data.gate_truth?.ready_for_agent} | Act5 execution ready=${state.data.gate_truth?.act5_execution_ready}`);
}

document.addEventListener('DOMContentLoaded', bootstrap);
