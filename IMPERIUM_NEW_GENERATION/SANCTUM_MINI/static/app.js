const SAFE_MECHANICUS_ORGAN = "MECHANICUS_AGENT";
const BRAIN_LINKS = [
  ["ADMINISTRATUM_AGENT", "OFFICIO_AGENTIS_AGENT"],
  ["OFFICIO_AGENTIS_AGENT", "ASTRONOMICON_AGENT"],
  ["ASTRONOMICON_AGENT", "INQUISITION_AGENT"],
  ["INQUISITION_AGENT", "DOCTRINARIUM_AGENT"],
  ["DOCTRINARIUM_AGENT", "MECHANICUS_AGENT"],
  ["MECHANICUS_AGENT", "STRATEGIUM_AGENT"],
  ["STRATEGIUM_AGENT", "SCHOLA_IMPERIALIS_AGENT"],
  ["SCHOLA_IMPERIALIS_AGENT", "CUSTODES"],
  ["CUSTODES", "THRONE"],
  ["THRONE", "MECHANICUS_AGENT"],
  ["OFFICIO_AGENTIS_AGENT", "MECHANICUS_AGENT"],
  ["ADMINISTRATUM_AGENT", "MECHANICUS_AGENT"],
];

const BRAIN_LAYOUT = {
  ADMINISTRATUM_AGENT: { x: 16, y: 26 },
  OFFICIO_AGENTIS_AGENT: { x: 31, y: 14 },
  ASTRONOMICON_AGENT: { x: 50, y: 10 },
  INQUISITION_AGENT: { x: 69, y: 14 },
  DOCTRINARIUM_AGENT: { x: 84, y: 26 },
  STRATEGIUM_AGENT: { x: 84, y: 56 },
  SCHOLA_IMPERIALIS_AGENT: { x: 69, y: 74 },
  CUSTODES: { x: 50, y: 82 },
  THRONE: { x: 31, y: 74 },
  MECHANICUS_AGENT: { x: 16, y: 56 },
};

const I18N = {
  en: {
    brandSub: "Mechanicus Live Terminal V0.3",
    actionsTitle: "Owner Actions",
    leftNote: "Action buttons run allowlisted Mechanicus actions and stream output to LIVE terminal.",
    organTitle: "Brain Zones",
    truthTitle: "Global Truth",
    logTitle: "Micro Log",
    tabLive: "LIVE",
    tabEvidence: "EVIDENCE",
    tabReports: "REPORTS",
    tabRaw: "RAW JSON",
    tabActionHistory: "ACTION HISTORY",
    liveTerminalTitle: "LIVE TERMINAL",
    liveIdle: "No terminal events yet.",
    liveEmpty: "Terminal stream is empty. Use actions or type an allowlisted command.",
    terminalPrompt: "Command",
    terminalPlaceholder: "status | tools | check | identity | where | help | raw | screenshot | clear",
    terminalRun: "Run",
    terminalClear: "Clear",
    terminalCleared: "Terminal stream cleared locally.",
    server: "Server",
    apiHealth: "API",
    repoHead: "HEAD",
    worktree: "Worktree",
    active: "Active",
    lastRefresh: "Last refresh",
    quality: "Quality",
    missing: "MISSING",
    evidenceHeader: "Mechanicus Evidence",
    viewportMissing: "No screenshot found. Run screenshot action/command and refresh.",
    placeholderFocus: "This organ is placeholder in V0.3.",
    lockedFocus: "This organ is locked in V0.3.",
    reportsSummary: "Reports and paths",
    rawPreview: "Raw JSON Preview",
    actionHistoryTitle: "Executed/Blocked Actions",
    emptyList: "None",
    latestEvidence: "Latest evidence",
    latestReport: "Latest report",
    latestScreenshot: "Latest screenshot",
    receipts: "Latest receipts",
    reports: "Latest reports",
    screenshots: "Latest screenshots",
    connectedCount: "Connected",
    placeholderCount: "Placeholders",
    lockedCount: "Locked",
    warningsCount: "Warnings",
    errorsCount: "Errors",
    blockersCount: "Blockers",
    freshness: "Freshness reference",
    realPlaceholder: "Real vs placeholder",
    fakeGreenNote: "Truth mode: only Mechanicus is connected. Other organs are explicit placeholders/locked.",
    brainLegendTitle: "Sanctum Brain Truth Zones",
    brainLegendReal: "Real link",
    brainLegendPlaceholder: "Placeholder cortex",
    brainLegendLocked: "Locked nuclei",
    brainNeuralFlow: "Neural flow",
    brainCoreTitle: "Neural Core",
    brainCoreSubtitle: "Internal communication nexus",
    brainCoreSignal: "Signal bus",
    brainCoreConnected: "Connected lanes",
    brainCorePlaceholder: "Placeholder lanes",
    brainCoreLocked: "Locked lanes",
    brainCoreActive: "Active anchor",
    truthModeLabel: "truth-mode",
    truthModeReal: "REAL",
    truthModePlaceholder: "PLACEHOLDER",
    truthModeLocked: "LOCKED",
    fetchError: "API fetch failed",
    source: "source",
    status: "status",
    safety: "safety",
    exitCode: "exit",
    duration: "duration",
    allowlist: "allowlist",
  },
  ru: {
    brandSub: "Mechanicus Live Terminal V0.3",
    actionsTitle: "Действия владельца",
    leftNote: "Кнопки слева запускают allowlisted-действия Mechanicus, полный вывод идёт в LIVE-терминал по центру.",
    organTitle: "Зоны мозга",
    truthTitle: "Блок истины",
    logTitle: "Микро-лог",
    tabLive: "LIVE",
    tabEvidence: "EVIDENCE",
    tabReports: "REPORTS",
    tabRaw: "RAW JSON",
    tabActionHistory: "ACTION HISTORY",
    liveTerminalTitle: "LIVE TERMINAL",
    liveIdle: "Событий терминала пока нет.",
    liveEmpty: "Поток терминала пуст. Используйте кнопки действий или введите allowlisted-команду.",
    terminalPrompt: "Команда",
    terminalPlaceholder: "status | tools | check | identity | where | help | raw | screenshot | clear",
    terminalRun: "Запуск",
    terminalClear: "Очистить",
    terminalCleared: "Поток терминала очищен локально.",
    server: "Сервер",
    apiHealth: "API",
    repoHead: "HEAD",
    worktree: "Дерево",
    active: "Активный",
    lastRefresh: "Обновление",
    quality: "Качество",
    missing: "ОТСУТСТВУЕТ",
    evidenceHeader: "Evidence Mechanicus",
    viewportMissing: "Скриншот не найден. Запустите screenshot-действие/команду и обновите данные.",
    placeholderFocus: "Этот орган в режиме placeholder в V0.3.",
    lockedFocus: "Этот орган заблокирован в V0.3.",
    reportsSummary: "Отчёты и пути",
    rawPreview: "Просмотр Raw JSON",
    actionHistoryTitle: "История действий (выполнено/заблокировано)",
    emptyList: "Нет",
    latestEvidence: "Последний evidence",
    latestReport: "Последний отчёт",
    latestScreenshot: "Последний скриншот",
    receipts: "Последние receipts",
    reports: "Последние отчёты",
    screenshots: "Последние скриншоты",
    connectedCount: "Подключено",
    placeholderCount: "Placeholder",
    lockedCount: "Locked",
    warningsCount: "Предупреждения",
    errorsCount: "Ошибки",
    blockersCount: "Блокеры",
    freshness: "Референс свежести",
    realPlaceholder: "Реальные данные vs placeholder",
    fakeGreenNote: "Режим истины: подключён только Mechanicus. Остальные органы явно placeholder/locked.",
    brainLegendTitle: "Зоны истины Sanctum Brain",
    brainLegendReal: "Реальный контур",
    brainLegendPlaceholder: "Placeholder-кортекс",
    brainLegendLocked: "Заблокированные ядра",
    brainNeuralFlow: "Нейросигнал",
    brainCoreTitle: "Нейроядро",
    brainCoreSubtitle: "Зона внутренней связности",
    brainCoreSignal: "Сигнальная шина",
    brainCoreConnected: "Реальные линии",
    brainCorePlaceholder: "Placeholder-линии",
    brainCoreLocked: "Locked-линии",
    brainCoreActive: "Активный якорь",
    truthModeLabel: "режим",
    truthModeReal: "REAL",
    truthModePlaceholder: "PLACEHOLDER",
    truthModeLocked: "LOCKED",
    fetchError: "Ошибка API-запроса",
    source: "источник",
    status: "статус",
    safety: "безопасность",
    exitCode: "код",
    duration: "время",
    allowlist: "allowlist",
  },
};

let locale = "ru";
let selectedOrganId = SAFE_MECHANICUS_ORGAN;
let centerTab = "live";

let stateCache = null;
let actionsCache = [];
let actionHistoryCache = [];
let terminalHistoryCache = [];
let terminalAllowlist = [];

const el = {
  brandSub: document.getElementById("brandSub"),
  actionsTitle: document.getElementById("actionsTitle"),
  leftNote: document.getElementById("leftNote"),
  organTitle: document.getElementById("organTitle"),
  truthTitle: document.getElementById("truthTitle"),
  logTitle: document.getElementById("logTitle"),
  tabLive: document.getElementById("tabLive"),
  tabEvidence: document.getElementById("tabEvidence"),
  tabReports: document.getElementById("tabReports"),
  tabRaw: document.getElementById("tabRaw"),
  tabActionHistory: document.getElementById("tabActionHistory"),
  headerMetrics: document.getElementById("headerMetrics"),
  actionList: document.getElementById("actionList"),
  organGrid: document.getElementById("organGrid"),
  brainLegend: document.getElementById("brainLegend"),
  brainLinksSvg: document.getElementById("brainLinksSvg"),
  brainCoreZone: document.getElementById("brainCoreZone"),
  centerTabButtons: Array.from(document.querySelectorAll(".center-tab")),
  centerPanels: Array.from(document.querySelectorAll(".center-panel")),
  liveHeaderTitle: document.getElementById("liveHeaderTitle"),
  liveHeaderMeta: document.getElementById("liveHeaderMeta"),
  terminalStream: document.getElementById("terminalStream"),
  terminalForm: document.getElementById("terminalForm"),
  terminalPromptLabel: document.getElementById("terminalPromptLabel"),
  terminalInput: document.getElementById("terminalInput"),
  terminalRunBtn: document.getElementById("terminalRunBtn"),
  terminalClearBtn: document.getElementById("terminalClearBtn"),
  evidenceViewportHeader: document.getElementById("evidenceViewportHeader"),
  evidenceViewportImage: document.getElementById("evidenceViewportImage"),
  evidenceViewportEmpty: document.getElementById("evidenceViewportEmpty"),
  reportsPanel: document.getElementById("reportsPanel"),
  rawPanel: document.getElementById("rawPanel"),
  actionHistoryPanel: document.getElementById("actionHistoryPanel"),
  truthBlock: document.getElementById("truthBlock"),
  microLog: document.getElementById("microLog"),
  langSwitch: document.getElementById("langSwitch"),
};

function t(key) {
  return (I18N[locale] && I18N[locale][key]) || key;
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function localLabel(organ) {
  return locale === "ru" ? organ.label_ru : organ.label_en;
}

function truthModeLabel(status) {
  if (status === "CONNECTED") {
    return t("truthModeReal");
  }
  if (status === "LOCKED") {
    return t("truthModeLocked");
  }
  return t("truthModePlaceholder");
}

function linkClassByStatus(statusA, statusB) {
  if (statusA === "CONNECTED" || statusB === "CONNECTED") {
    return "is-real";
  }
  if (statusA === "LOCKED" || statusB === "LOCKED") {
    return "is-locked";
  }
  return "is-placeholder";
}

function shortValue(value) {
  if (!value) {
    return t("missing");
  }
  const text = String(value);
  return text.length > 150 ? `${text.slice(0, 147)}...` : text;
}

function listToHtml(items, emptyText) {
  if (!items || !items.length) {
    return `<li>${escapeHtml(emptyText)}</li>`;
  }
  return items.map((item) => `<li>${escapeHtml(item)}</li>`).join("");
}

function setCenterTab(tabId) {
  centerTab = tabId;
  el.centerTabButtons.forEach((button) => {
    const isActive = (button.dataset.centerTab || "") === tabId;
    button.classList.toggle("is-active", isActive);
  });
  el.centerPanels.forEach((panel) => {
    const isActive = (panel.dataset.centerPanel || "") === tabId;
    panel.classList.toggle("is-active", isActive);
  });
}

function renderStaticLabels() {
  el.brandSub.textContent = t("brandSub");
  el.actionsTitle.textContent = t("actionsTitle");
  el.leftNote.textContent = t("leftNote");
  el.organTitle.textContent = t("organTitle");
  el.truthTitle.textContent = t("truthTitle");
  el.logTitle.textContent = t("logTitle");
  el.tabLive.textContent = t("tabLive");
  el.tabEvidence.textContent = t("tabEvidence");
  el.tabReports.textContent = t("tabReports");
  el.tabRaw.textContent = t("tabRaw");
  el.tabActionHistory.textContent = t("tabActionHistory");
  el.terminalPromptLabel.textContent = t("terminalPrompt");
  el.terminalInput.placeholder = t("terminalPlaceholder");
  el.terminalRunBtn.textContent = t("terminalRun");
  el.terminalClearBtn.textContent = t("terminalClear");
  el.langSwitch.textContent = locale === "ru" ? "EN" : "RU";
}

function renderHeader(state) {
  const chips = [
    `${t("server")}: ${state.server.status}`,
    `${t("apiHealth")}: ${state.server.api_status}`,
    `${t("repoHead")}: ${state.repo.head.slice(0, 12)}`,
    `${t("worktree")}: ${state.repo.worktree_state}`,
    `${t("active")}: ${state.server.active_organ}`,
    `${t("quality")}: ${state.server.connection_quality}`,
    `${t("lastRefresh")}: ${state.generated_at_utc}`,
  ];
  el.headerMetrics.innerHTML = chips
    .map((chip) => `<span class="metric-chip">${escapeHtml(chip)}</span>`)
    .join("");
}

function renderActions() {
  if (!actionsCache.length) {
    el.actionList.innerHTML = `<div class="empty-hint">${escapeHtml(t("emptyList"))}</div>`;
    return;
  }

  el.actionList.innerHTML = actionsCache
    .map((action) => {
      const title = locale === "ru" ? action.title_ru : action.title_en;
      return `
      <button class="action-btn" type="button" data-action-id="${escapeHtml(action.action_id)}">
        <span>${escapeHtml(title)}</span>
        <small>${escapeHtml(action.action_id)}</small>
      </button>
    `;
    })
    .join("");

  el.actionList.querySelectorAll(".action-btn").forEach((button) => {
    button.addEventListener("click", async () => {
      const actionId = button.dataset.actionId || "";
      await runActionButton(actionId);
    });
  });
}

async function runActionButton(actionId) {
  if (!actionId) {
    return;
  }
  try {
    const response = await fetch("/api/actions/run", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ action_id: actionId }),
    });
    await response.json();
    await refreshAll();
    setCenterTab("live");
  } catch (error) {
    el.liveHeaderMeta.textContent = `${t("fetchError")}: ${String(error)}`;
  }
}

async function runTerminalCommand(commandText) {
  const command = (commandText || "").trim();
  if (!command) {
    return;
  }

  if (command.toLowerCase() === "clear") {
    terminalHistoryCache = [];
    renderLivePanel();
    el.liveHeaderMeta.textContent = t("terminalCleared");
    return;
  }

  try {
    const response = await fetch("/api/terminal/execute", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ organ: SAFE_MECHANICUS_ORGAN, command }),
    });
    await response.json();
    await refreshAll();
    setCenterTab("live");
  } catch (error) {
    el.liveHeaderMeta.textContent = `${t("fetchError")}: ${String(error)}`;
  }
}

function renderBrainLegend() {
  if (!el.brainLegend) {
    return;
  }
  el.brainLegend.innerHTML = `
    <div class="brain-legend-title">${escapeHtml(t("brainLegendTitle"))}</div>
    <div class="brain-legend-items">
      <span class="legend-chip is-real">${escapeHtml(t("brainLegendReal"))}</span>
      <span class="legend-chip is-placeholder">${escapeHtml(t("brainLegendPlaceholder"))}</span>
      <span class="legend-chip is-locked">${escapeHtml(t("brainLegendLocked"))}</span>
      <span class="legend-flow">${escapeHtml(t("brainNeuralFlow"))}</span>
    </div>
  `;
}

function renderBrainCore(state) {
  if (!el.brainCoreZone) {
    return;
  }
  const truth = state.global_truth || {};
  const connected = truth.connected_organs_count ?? 0;
  const placeholders = truth.placeholders_count ?? 0;
  const locked = truth.locked_count ?? 0;
  const activeAnchor = state.server?.active_organ || SAFE_MECHANICUS_ORGAN;

  el.brainCoreZone.innerHTML = `
    <div class="brain-core-gridline"></div>
    <div class="brain-core-ring brain-core-ring-a"></div>
    <div class="brain-core-ring brain-core-ring-b"></div>
    <div class="brain-core-ring brain-core-ring-c"></div>
    <div class="brain-core-node brain-core-node-a"></div>
    <div class="brain-core-node brain-core-node-b"></div>
    <div class="brain-core-node brain-core-node-c"></div>
    <div class="brain-core-title">${escapeHtml(t("brainCoreTitle"))}</div>
    <div class="brain-core-subtitle">${escapeHtml(t("brainCoreSubtitle"))}</div>
    <div class="brain-core-chip-row">
      <span class="brain-core-chip is-real">${escapeHtml(t("brainCoreConnected"))}: ${escapeHtml(String(connected))}</span>
      <span class="brain-core-chip is-placeholder">${escapeHtml(t("brainCorePlaceholder"))}: ${escapeHtml(String(placeholders))}</span>
      <span class="brain-core-chip is-locked">${escapeHtml(t("brainCoreLocked"))}: ${escapeHtml(String(locked))}</span>
    </div>
    <div class="brain-core-footer">${escapeHtml(t("brainCoreSignal"))} :: ${escapeHtml(t("brainCoreActive"))} = ${escapeHtml(activeAnchor)}</div>
  `;
}

function renderBrainLinks(state) {
  if (!el.brainLinksSvg) {
    return;
  }
  const organMap = {};
  (state.organs || []).forEach((organ) => {
    organMap[organ.id] = organ;
  });

  const centerX = 50;
  const centerY = 48;
  const paths = BRAIN_LINKS.map(([fromId, toId], idx) => {
    const from = BRAIN_LAYOUT[fromId];
    const to = BRAIN_LAYOUT[toId];
    if (!from || !to) {
      return "";
    }
    const organA = organMap[fromId] || {};
    const organB = organMap[toId] || {};
    const cls = linkClassByStatus(organA.status, organB.status);

    const x1 = from.x * 10;
    const y1 = from.y * 5.6;
    const x2 = to.x * 10;
    const y2 = to.y * 5.6;
    const midX = (x1 + x2) / 2;
    const midY = (y1 + y2) / 2;
    const pull = idx % 2 === 0 ? 24 : -24;
    const cx = midX + (centerX * 10 - midX) * 0.13;
    const cy = midY + (centerY * 5.6 - midY) * 0.13 + pull;
    return `<path class="brain-link ${cls}" d="M ${x1} ${y1} Q ${cx} ${cy} ${x2} ${y2}" />`;
  })
    .filter(Boolean)
    .join("");

  el.brainLinksSvg.innerHTML = paths;
}

function renderOrgans(state) {
  const organs = state.organs || [];
  renderBrainLegend();
  renderBrainCore(state);
  renderBrainLinks(state);
  el.organGrid.innerHTML = organs
    .map((organ) => {
      const isActive = organ.id === selectedOrganId;
      const pos = BRAIN_LAYOUT[organ.id] || { x: 50, y: 50 };
      const truthMode = truthModeLabel(organ.status);
      return `
      <article
        class="organ-card brain-zone ${isActive ? "active" : ""}"
        data-organ-id="${escapeHtml(organ.id)}"
        style="--zone-x:${pos.x}%; --zone-y:${pos.y}%;"
      >
        <span class="zone-pulse" aria-hidden="true"></span>
        <h3>${escapeHtml(localLabel(organ))}</h3>
        <div class="zone-id">${escapeHtml(organ.id)}</div>
        <span class="status-badge status-${escapeHtml(organ.status)}">${escapeHtml(organ.status)}</span>
        <span class="truth-mode-chip">${escapeHtml(t("truthModeLabel"))}: ${escapeHtml(truthMode)}</span>
      </article>
    `;
    })
    .join("");

  el.organGrid.querySelectorAll(".organ-card").forEach((card) => {
    card.addEventListener("click", () => {
      selectedOrganId = card.dataset.organId || SAFE_MECHANICUS_ORGAN;
      renderOrgans(state);
      renderCenterPanels(state);
    });
  });
}

function renderLivePanel() {
  el.liveHeaderTitle.textContent = `${SAFE_MECHANICUS_ORGAN} :: ${t("liveTerminalTitle")}`;

  const latest = terminalHistoryCache[0];
  if (latest) {
    const meta = [
      `${t("status")}: ${latest.status}`,
      `${t("safety")}: ${latest.safety}`,
      `${t("exitCode")}: ${latest.exit_code ?? ""}`,
      `${t("duration")}: ${latest.duration_ms ?? 0}ms`,
      latest.finished_at_utc || latest.started_at_utc || "",
    ];
    el.liveHeaderMeta.textContent = meta.join(" | ");
  } else {
    const allow = terminalAllowlist.length ? terminalAllowlist.join(", ") : t("missing");
    el.liveHeaderMeta.textContent = `${t("liveIdle")} ${t("allowlist")}: ${allow}`;
  }

  const rows = terminalHistoryCache.slice(0, 40);
  if (!rows.length) {
    el.terminalStream.innerHTML = `<div class="terminal-empty">${escapeHtml(t("liveEmpty"))}</div>`;
    return;
  }

  el.terminalStream.innerHTML = rows
    .map((row) => {
      const status = String(row.status || "UNKNOWN").toUpperCase();
      const header = `${row.organ || SAFE_MECHANICUS_ORGAN} :: ${row.command || row.action_id || ""}`;
      const meta = [
        `${t("source")}: ${row.source || "unknown"}`,
        `${t("safety")}: ${row.safety || ""}`,
        `${t("exitCode")}: ${row.exit_code ?? ""}`,
        `${t("duration")}: ${row.duration_ms ?? 0}ms`,
        row.finished_at_utc || row.started_at_utc || "",
      ]
        .filter(Boolean)
        .join(" | ");
      const stdout = row.stdout ? `<pre class="entry-stdout">${escapeHtml(row.stdout)}</pre>` : "";
      const stderr = row.stderr ? `<pre class="entry-stderr">${escapeHtml(row.stderr)}</pre>` : "";
      return `
      <article class="terminal-entry">
        <div class="entry-top">
          <span>${escapeHtml(header)}</span>
          <span class="entry-chip status-${escapeHtml(status)}">${escapeHtml(status)}</span>
        </div>
        <div class="entry-meta">${escapeHtml(meta)}</div>
        ${stdout}
        ${stderr}
      </article>
    `;
    })
    .join("");
}

function renderEvidencePanel(state) {
  const selected = (state.organs || []).find((organ) => organ.id === selectedOrganId);
  if (!selected) {
    return;
  }

  el.evidenceViewportHeader.textContent = `${t("evidenceHeader")} :: ${localLabel(selected)} :: ${selected.status}`;
  if (selected.id !== SAFE_MECHANICUS_ORGAN) {
    el.evidenceViewportImage.style.display = "none";
    el.evidenceViewportEmpty.style.display = "block";
    el.evidenceViewportEmpty.textContent = selected.status === "LOCKED" ? t("lockedFocus") : t("placeholderFocus");
    return;
  }

  const shots = state.mechanicus?.latest_screenshots || [];
  if (!shots.length) {
    el.evidenceViewportImage.style.display = "none";
    el.evidenceViewportEmpty.style.display = "block";
    el.evidenceViewportEmpty.textContent = t("viewportMissing");
    return;
  }

  const url = `/api/mechanicus/screenshot/latest?ts=${encodeURIComponent(state.generated_at_utc)}`;
  el.evidenceViewportImage.style.display = "block";
  el.evidenceViewportEmpty.style.display = "none";
  el.evidenceViewportImage.src = url;
  el.evidenceViewportImage.onerror = () => {
    el.evidenceViewportImage.style.display = "none";
    el.evidenceViewportEmpty.style.display = "block";
    el.evidenceViewportEmpty.textContent = t("viewportMissing");
  };
}

function renderReportsPanel(state) {
  const selected = (state.organs || []).find((organ) => organ.id === selectedOrganId);
  if (!selected || selected.id !== SAFE_MECHANICUS_ORGAN) {
    const text = selected && selected.status === "LOCKED" ? t("lockedFocus") : t("placeholderFocus");
    el.reportsPanel.innerHTML = `<p>${escapeHtml(text)}</p>`;
    return;
  }

  const truth = state.global_truth || {};
  const mechanicus = state.mechanicus || {};
  const reportItems = (mechanicus.latest_reports || []).slice(0, 8).map((item) => `${item.task_id} :: ${item.path_repo_relative || item.path}`);
  const screenshotItems = (mechanicus.latest_screenshots || []).slice(0, 8).map((item) => `${item.file_name} :: ${item.path_repo_relative || item.path}`);
  const receiptItems = (mechanicus.latest_receipts || []).slice(0, 10);

  el.reportsPanel.innerHTML = `
    <h3>${escapeHtml(t("reportsSummary"))}</h3>
    <p><strong>${escapeHtml(t("latestEvidence"))}:</strong> ${escapeHtml(truth.latest_evidence_path || t("missing"))}</p>
    <p><strong>${escapeHtml(t("latestReport"))}:</strong> ${escapeHtml(truth.latest_report_path || t("missing"))}</p>
    <p><strong>${escapeHtml(t("latestScreenshot"))}:</strong> ${escapeHtml(truth.latest_screenshot_path || t("missing"))}</p>
    <p><strong>${escapeHtml(t("reports"))}</strong></p>
    <ul>${listToHtml(reportItems, t("emptyList"))}</ul>
    <p><strong>${escapeHtml(t("screenshots"))}</strong></p>
    <ul>${listToHtml(screenshotItems, t("emptyList"))}</ul>
    <p><strong>${escapeHtml(t("receipts"))}</strong></p>
    <ul>${listToHtml(receiptItems, t("emptyList"))}</ul>
  `;
}

function renderRawPanel(state) {
  const selected = (state.organs || []).find((organ) => organ.id === selectedOrganId);
  const payload =
    selected && selected.id === SAFE_MECHANICUS_ORGAN
      ? { mechanicus: state.mechanicus || {}, global_truth: state.global_truth || {} }
      : { selected_organ: selected || null };
  const raw = JSON.stringify(payload, null, 2);

  el.rawPanel.innerHTML = `
    <h3>${escapeHtml(t("rawPreview"))}</h3>
    <pre>${escapeHtml(raw.length > 18000 ? `${raw.slice(0, 18000)}\n...<truncated>` : raw)}</pre>
  `;
}

function renderActionHistoryPanel() {
  const rows = actionHistoryCache.slice(0, 40);
  if (!rows.length) {
    el.actionHistoryPanel.innerHTML = `<div class="empty-hint">${escapeHtml(t("emptyList"))}</div>`;
    return;
  }

  el.actionHistoryPanel.innerHTML = `
    <h3>${escapeHtml(t("actionHistoryTitle"))}</h3>
    ${rows
      .map((row) => {
        const status = String(row.status || "UNKNOWN").toUpperCase();
        const label = `${row.action_id || ""} :: ${row.command || ""}`;
        const meta = [
          `${t("source")}: ${row.source || "unknown"}`,
          `${t("safety")}: ${row.safety || ""}`,
          `${t("exitCode")}: ${row.exit_code ?? ""}`,
          row.finished_at_utc || row.started_at_utc || "",
        ]
          .filter(Boolean)
          .join(" | ");
        return `
        <div class="history-card">
          <div class="history-top">
            <span>${escapeHtml(label)}</span>
            <span class="entry-chip status-${escapeHtml(status)}">${escapeHtml(status)}</span>
          </div>
          <div class="history-meta">${escapeHtml(meta)}</div>
        </div>
      `;
      })
      .join("")}
  `;
}

function renderCenterPanels(state) {
  renderLivePanel();
  renderEvidencePanel(state);
  renderReportsPanel(state);
  renderRawPanel(state);
  renderActionHistoryPanel();
}

function renderTruth(state) {
  const truth = state.global_truth || {};
  const matrix = truth.real_vs_placeholder || {};
  const rows = [
    [t("connectedCount"), truth.connected_organs_count],
    [t("placeholderCount"), truth.placeholders_count],
    [t("lockedCount"), truth.locked_count],
    [t("warningsCount"), truth.warnings_count],
    [t("errorsCount"), truth.errors_count],
    [t("blockersCount"), truth.blockers_count],
    [t("latestEvidence"), shortValue(truth.latest_evidence_path)],
    [t("latestReport"), shortValue(truth.latest_report_path)],
    [t("latestScreenshot"), shortValue(truth.latest_screenshot_path)],
    [t("freshness"), shortValue(truth.freshness_reference)],
    [
      t("realPlaceholder"),
      `real=[${(matrix.real || []).join(", ")}], placeholder=[${(matrix.placeholder || []).join(", ")}], locked=[${(matrix.locked || []).join(", ")}]`,
    ],
    ["NOTE", t("fakeGreenNote")],
  ];

  el.truthBlock.innerHTML = rows
    .map(
      ([key, value]) => `
      <div class="truth-item">
        <div class="truth-key">${escapeHtml(String(key))}</div>
        <div class="truth-value">${escapeHtml(String(value ?? t("missing")))}</div>
      </div>
    `
    )
    .join("");
}

function renderLog(state) {
  const rows = (state.micro_log || []).slice(-18).reverse();
  el.microLog.innerHTML = rows
    .map((row) => {
      const time = (row.timestamp_utc || "").split("T")[1] || row.timestamp_utc || "";
      return `
      <div class="log-row">
        <span>${escapeHtml(time.replace("Z", ""))}</span>
        <span class="log-status ${escapeHtml(row.status || "UNKNOWN")}">${escapeHtml(row.status || "UNKNOWN")}</span>
        <span>${escapeHtml(row.message || "")}</span>
      </div>
    `;
    })
    .join("");
}

function renderAll(state) {
  renderStaticLabels();
  renderHeader(state);
  renderActions();
  renderOrgans(state);
  renderCenterPanels(state);
  renderTruth(state);
  renderLog(state);
}

async function fetchState() {
  const response = await fetch("/api/state", { cache: "no-store" });
  if (!response.ok) {
    throw new Error(`STATE_HTTP_${response.status}`);
  }
  return response.json();
}

async function fetchActions() {
  const response = await fetch("/api/actions", { cache: "no-store" });
  if (!response.ok) {
    throw new Error(`ACTIONS_HTTP_${response.status}`);
  }
  const payload = await response.json();
  return payload.actions || [];
}

async function fetchActionHistory() {
  const response = await fetch("/api/actions/history", { cache: "no-store" });
  if (!response.ok) {
    throw new Error(`ACTION_HISTORY_HTTP_${response.status}`);
  }
  const payload = await response.json();
  return payload.history || [];
}

async function fetchTerminalHistory() {
  const response = await fetch("/api/terminal/history", { cache: "no-store" });
  if (!response.ok) {
    throw new Error(`TERMINAL_HISTORY_HTTP_${response.status}`);
  }
  return response.json();
}

async function refreshAll() {
  try {
    const [state, actions, actionHistory, terminalPayload] = await Promise.all([
      fetchState(),
      fetchActions(),
      fetchActionHistory(),
      fetchTerminalHistory(),
    ]);
    stateCache = state;
    actionsCache = actions;
    actionHistoryCache = actionHistory;
    terminalHistoryCache = terminalPayload.history || [];
    terminalAllowlist = terminalPayload.allowlist || [];

    if (!(state.organs || []).some((organ) => organ.id === selectedOrganId)) {
      selectedOrganId = SAFE_MECHANICUS_ORGAN;
    }

    renderAll(stateCache);
  } catch (error) {
    el.liveHeaderMeta.textContent = `${t("fetchError")}: ${String(error)}`;
  }
}

el.langSwitch.addEventListener("click", () => {
  locale = locale === "ru" ? "en" : "ru";
  if (stateCache) {
    renderAll(stateCache);
  } else {
    renderStaticLabels();
  }
});

el.centerTabButtons.forEach((button) => {
  button.addEventListener("click", () => {
    setCenterTab(button.dataset.centerTab || "live");
  });
});

el.terminalForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const value = el.terminalInput.value;
  el.terminalInput.value = "";
  await runTerminalCommand(value);
});

el.terminalClearBtn.addEventListener("click", () => {
  terminalHistoryCache = [];
  renderLivePanel();
  el.liveHeaderMeta.textContent = t("terminalCleared");
});

renderStaticLabels();
setCenterTab("live");
refreshAll();
setInterval(refreshAll, 20000);
