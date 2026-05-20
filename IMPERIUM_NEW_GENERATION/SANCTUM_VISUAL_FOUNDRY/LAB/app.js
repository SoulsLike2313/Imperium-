const I18N = {
  en: {
    mission:
      "Visual Foundry slice: truth first, work visibility, command clarity, and secondary technical output.",
    workTitle: "WORK ZONE // CURRENT ACTIVITY",
    workNote: "Prototype feed for operator context, warnings, and gate-relevant transitions.",
    registryTitle: "TOOL REGISTRY // CAPABILITY OVERVIEW",
    eventsTitle: "LATEST REPORT / RECEIPT / EVENT",
    commandTitle: "COMMAND RAIL // OPERATOR PALETTE",
    commandNote: "Primary actions are explicit. RAW mode is opt-in and secondary.",
    rawTitle: "RAW / TECHNICAL MODE (SECONDARY)",
    rawOff: "RAW OFF",
    rawOn: "RAW ON",
    statusLabel: "status",
    ownerLabel: "owner",
    footerReport: "LATEST REPORT",
    footerReceipt: "LATEST RECEIPT",
    footerEvent: "EVENT SUMMARY",
    footerHealth: "COMMAND HEALTH",
    cmdStatus: "View current truth strip values.",
    cmdTools: "Open tool availability summary.",
    cmdCheck: "Simulate local gate check pass.",
    cmdWhere: "Show active scope and path lock.",
    cmdRaw: "Toggle raw technical panel.",
    scope: "Scope",
    head: "HEAD",
    visual: "Visual",
    gates: "Gates",
    line: "line",
    cmdExecuted: "Command executed",
    uiReady: "Mechanicus console slice is ready for owner review."
  },
  ru: {
    mission:
      "Срез Visual Foundry: сначала truth, затем рабочая видимость, команды и только вторичный technical-режим.",
    workTitle: "WORK ZONE // CURRENT ACTIVITY",
    workNote: "Прототип ленты операторского контекста, предупреждений и gate-переходов.",
    registryTitle: "TOOL REGISTRY // CAPABILITY OVERVIEW",
    eventsTitle: "LATEST REPORT / RECEIPT / EVENT",
    commandTitle: "COMMAND RAIL // OPERATOR PALETTE",
    commandNote: "Первичные действия явные. RAW режим включается только по запросу.",
    rawTitle: "RAW / TECHNICAL MODE (SECONDARY)",
    rawOff: "RAW OFF",
    rawOn: "RAW ON",
    statusLabel: "статус",
    ownerLabel: "владелец",
    footerReport: "ПОСЛЕДНИЙ ОТЧЕТ",
    footerReceipt: "ПОСЛЕДНИЙ RECEIPT",
    footerEvent: "СВОДКА СОБЫТИЙ",
    footerHealth: "ЗДОРОВЬЕ КОМАНД",
    cmdStatus: "Показать текущие значения truth-strip.",
    cmdTools: "Открыть сводку доступности инструментов.",
    cmdCheck: "Симуляция PASS по локальному gate-check.",
    cmdWhere: "Показать активный scope и блок path-границ.",
    cmdRaw: "Переключить техническую RAW-панель.",
    scope: "Scope",
    head: "HEAD",
    visual: "Visual",
    gates: "Gates",
    line: "линия",
    cmdExecuted: "Команда выполнена",
    uiReady: "Срез Mechanicus console готов для owner-проверки."
  }
};

const model = {
  truthChips: [
    { key: "scope", value: "IMPERIUM_NEW_GENERATION", state: "ok" },
    { key: "head", value: "5acae4b3", state: "warn" },
    { key: "visual", value: "FOUNDRY_SLICE_V0_1", state: "ok" },
    { key: "gates", value: "U00/U01/U02/U04/U05", state: "ok" }
  ],
  workFeed: [
    { time: "14:02", title: "Admission", state: "ok", text: "GATE_ACK completed with scope and stop conditions." },
    { time: "14:07", title: "Foundry Scaffold", state: "ok", text: "Pipeline folders created inside allowed root only." },
    { time: "14:18", title: "Contract + Tokens", state: "ok", text: "Visual contract and tokens linked to component lab." },
    { time: "14:24", title: "Raw Mode Rule", state: "warn", text: "Raw drawer remains secondary and hidden by default." },
    { time: "14:31", title: "Screenshot Proof", state: "ok", text: "1366x768 and 1920x1080 capture targets configured." }
  ],
  tools: [
    { name: "git", owner: "ADMINISTRATUM", status: "available" },
    { name: "node", owner: "MECHANICUS", status: "available" },
    { name: "npm", owner: "MECHANICUS", status: "available" },
    { name: "playwright", owner: "MECHANICUS", status: "partial" },
    { name: "jsonschema", owner: "DOCTRINARIUM", status: "missing" }
  ],
  events: [
    { title: "Latest Report", body: "validation_report.json refreshed with schema checks and scope truth." },
    { title: "Latest Receipt", body: "FINAL_RECEIPT.json tracks gates, screenshots, and known limitations." },
    { title: "Event Summary", body: "No forbidden-scope writes detected. Existing dirty baseline left untouched." },
    { title: "UI Readiness", body: "Mechanicus slice available in isolated lab for visual review." }
  ],
  footer: [
    { id: "report", value: "validation_report.json" },
    { id: "receipt", value: "FINAL_RECEIPT.json" },
    { id: "event", value: "WARN=1 ERROR=0 BLOCK=0" },
    { id: "health", value: "COMMANDS SAFE / RAW SECONDARY" }
  ],
  raw: {
    scope: "IMPERIUM_NEW_GENERATION/SANCTUM_VISUAL_FOUNDRY/**",
    forbidden: ["ORGANS/**", "SANCTUM/**", "IMPERIUM_TEST_VERSION/**"],
    proof_targets: ["1366x768", "1920x1080", "top_strip", "work_zone", "command_zone", "raw_secondary"]
  }
};

const commands = [
  { id: "status", label: "STATUS", note: "cmdStatus" },
  { id: "tools", label: "TOOLS", note: "cmdTools" },
  { id: "check", label: "CHECK", note: "cmdCheck" },
  { id: "where", label: "WHERE", note: "cmdWhere" },
  { id: "raw", label: "RAW", note: "cmdRaw" }
];

let locale = "ru";
let rawVisible = false;

const el = {
  missionLine: document.getElementById("missionLine"),
  truthChips: document.getElementById("truthChips"),
  langSwitch: document.getElementById("langSwitch"),
  rawToggle: document.getElementById("rawToggle"),
  workZoneTitle: document.getElementById("workZoneTitle"),
  workZoneNote: document.getElementById("workZoneNote"),
  workFeed: document.getElementById("workFeed"),
  registryTitle: document.getElementById("registryTitle"),
  registrySummary: document.getElementById("registrySummary"),
  toolTable: document.getElementById("toolTable"),
  eventsTitle: document.getElementById("eventsTitle"),
  eventGrid: document.getElementById("eventGrid"),
  commandTitle: document.getElementById("commandTitle"),
  commandNote: document.getElementById("commandNote"),
  commandGrid: document.getElementById("commandGrid"),
  rawPanel: document.getElementById("rawPanel"),
  rawTitle: document.getElementById("rawTitle"),
  rawText: document.getElementById("rawText"),
  footerStrip: document.getElementById("footerStrip")
};

function t(key) {
  return I18N[locale][key] ?? key;
}

function statusClass(status) {
  if (status === "available" || status === "ok") return "ok";
  if (status === "partial" || status === "warn") return "warn";
  return "error";
}

function renderTruthChips() {
  el.truthChips.innerHTML = "";
  model.truthChips.forEach((chip) => {
    const div = document.createElement("div");
    div.className = `chip ${statusClass(chip.state)}`;
    div.textContent = `${t(chip.key)}: ${chip.value}`;
    el.truthChips.appendChild(div);
  });
}

function renderWorkFeed() {
  el.workFeed.innerHTML = "";
  model.workFeed.forEach((item, idx) => {
    const card = document.createElement("article");
    card.className = "feed-item";
    card.style.animationDelay = `${idx * 50}ms`;
    card.innerHTML = `
      <div class="feed-head">
        <strong>${item.time} · ${item.title}</strong>
        <span class="feed-state ${statusClass(item.state)}">${item.state.toUpperCase()}</span>
      </div>
      <div class="feed-text">${item.text}</div>
    `;
    el.workFeed.appendChild(card);
  });
}

function renderRegistry() {
  el.registrySummary.innerHTML = "";
  const total = model.tools.length;
  const available = model.tools.filter((item) => item.status === "available").length;
  const partial = model.tools.filter((item) => item.status === "partial").length;
  const missing = model.tools.filter((item) => item.status === "missing").length;

  [
    `TOTAL ${total}`,
    `AVAILABLE ${available}`,
    `PARTIAL ${partial}`,
    `MISSING ${missing}`
  ].forEach((text) => {
    const badge = document.createElement("div");
    badge.className = "summary-badge";
    badge.textContent = text;
    el.registrySummary.appendChild(badge);
  });

  el.toolTable.innerHTML = "";
  model.tools.forEach((tool) => {
    const row = document.createElement("div");
    row.className = "tool-row";
    row.innerHTML = `
      <div>${tool.name}</div>
      <div>${tool.owner}</div>
      <div class="status ${tool.status}">${tool.status.toUpperCase()}</div>
    `;
    el.toolTable.appendChild(row);
  });
}

function renderEvents() {
  el.eventGrid.innerHTML = "";
  model.events.forEach((event) => {
    const card = document.createElement("article");
    card.className = "event-card";
    card.innerHTML = `<h3>${event.title}</h3><p>${event.body}</p>`;
    el.eventGrid.appendChild(card);
  });
}

function renderCommands() {
  el.commandGrid.innerHTML = "";
  commands.forEach((command) => {
    const btn = document.createElement("button");
    btn.type = "button";
    btn.className = "command-btn";
    btn.dataset.command = command.id;
    btn.innerHTML = `<strong>${command.label}</strong><span>${t(command.note)}</span>`;
    btn.addEventListener("click", () => runCommand(command.id));
    el.commandGrid.appendChild(btn);
  });
}

function renderFooter() {
  el.footerStrip.innerHTML = "";
  const keyMap = {
    report: "footerReport",
    receipt: "footerReceipt",
    event: "footerEvent",
    health: "footerHealth"
  };
  model.footer.forEach((item) => {
    const card = document.createElement("div");
    card.className = "footer-card";
    card.innerHTML = `<span class="k">${t(keyMap[item.id])}</span><span class="v">${item.value}</span>`;
    el.footerStrip.appendChild(card);
  });
}

function renderRawText() {
  el.rawText.textContent = JSON.stringify(model.raw, null, 2);
}

function setRawVisibility(nextVisible) {
  rawVisible = nextVisible;
  el.rawPanel.classList.toggle("is-hidden", !rawVisible);
  el.rawToggle.textContent = rawVisible ? t("rawOn") : t("rawOff");
}

function runCommand(commandId) {
  if (commandId === "raw") {
    setRawVisibility(!rawVisible);
    return;
  }
  const timestamp = new Date().toLocaleTimeString(locale === "ru" ? "ru-RU" : "en-US", {
    hour: "2-digit",
    minute: "2-digit"
  });
  model.workFeed.unshift({
    time: timestamp,
    title: `${t("cmdExecuted")} ${commandId.toUpperCase()}`,
    state: "ok",
    text: t("uiReady")
  });
  model.workFeed = model.workFeed.slice(0, 6);
  renderWorkFeed();
}

function renderText() {
  el.missionLine.textContent = t("mission");
  el.workZoneTitle.textContent = t("workTitle");
  el.workZoneNote.textContent = t("workNote");
  el.registryTitle.textContent = t("registryTitle");
  el.eventsTitle.textContent = t("eventsTitle");
  el.commandTitle.textContent = t("commandTitle");
  el.commandNote.textContent = t("commandNote");
  el.rawTitle.textContent = t("rawTitle");
  el.langSwitch.textContent = locale === "ru" ? "EN" : "RU";
  el.rawToggle.textContent = rawVisible ? t("rawOn") : t("rawOff");
}

function renderAll() {
  renderText();
  renderTruthChips();
  renderWorkFeed();
  renderRegistry();
  renderEvents();
  renderCommands();
  renderFooter();
  renderRawText();
}

el.langSwitch.addEventListener("click", () => {
  locale = locale === "ru" ? "en" : "ru";
  renderAll();
});

el.rawToggle.addEventListener("click", () => setRawVisibility(!rawVisible));

setRawVisibility(false);
renderAll();

