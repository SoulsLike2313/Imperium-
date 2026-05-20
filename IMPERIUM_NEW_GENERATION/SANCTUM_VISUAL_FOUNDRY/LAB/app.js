const I18N = {
  en: {
    eyebrow: "IMPERIUM VISUAL FOUNDRY / CONTRACT TO TOKENS",
    title: "MECHANICUS OPERATOR SLICE // NEURAL SPLIT MODE",
    mission:
      "Brain context remains primary on the left, active organ panel remains actionable on the right, raw mode stays secondary.",
    brainTitle: "BRAIN FIELD // ORGAN ZONES",
    brainNote: "Click a zone to update the right-side context panel.",
    brainStatus: "neural pulse: active",
    workTitle: "WORK REPORT // CURRENT ACTIVITY",
    panelTitle: "ACTIVE ORGAN PANEL",
    panelNote: "Operational controls are separated from internal TUI details.",
    toolsTitle: "APPROVED TOOLS",
    contourTitle: "CONTOUR / READINESS",
    actionsTitle: "SANCTUM-LEVEL ACTIONS",
    rawTitle: "RAW TECHNICAL MODE (SECONDARY)",
    rawOff: "RAW OFF",
    rawOn: "RAW ON",
    state: "state",
    scope: "scope",
    visual: "visual",
    branch: "branch",
    head: "head",
    footerReport: "LATEST REPORT",
    footerReceipt: "LATEST RECEIPT",
    footerEvent: "EVENT SUMMARY",
    footerHealth: "COMMAND HEALTH",
    actionRun: "Run action",
    actionNote: "This is a prototype action surface.",
    unknown: "unknown",
    active: "active",
    placeholder: "placeholder"
  },
  ru: {
    eyebrow: "IMPERIUM VISUAL FOUNDRY / CONTRACT TO TOKENS",
    title: "MECHANICUS OPERATOR SLICE // NEURAL SPLIT MODE",
    mission:
      "Контекст мозга остаётся первичным слева, активная панель органа справа управляемая, raw-режим строго вторичный.",
    brainTitle: "BRAIN FIELD // ORGAN ZONES",
    brainNote: "Нажмите на зону, чтобы обновить правую contextual-панель.",
    brainStatus: "нейропульс: активен",
    workTitle: "WORK REPORT // CURRENT ACTIVITY",
    panelTitle: "ACTIVE ORGAN PANEL",
    panelNote: "Операционные контролы отделены от внутренних TUI-деталей.",
    toolsTitle: "APPROVED TOOLS",
    contourTitle: "CONTOUR / READINESS",
    actionsTitle: "SANCTUM-LEVEL ACTIONS",
    rawTitle: "RAW TECHNICAL MODE (SECONDARY)",
    rawOff: "RAW OFF",
    rawOn: "RAW ON",
    state: "статус",
    scope: "scope",
    visual: "visual",
    branch: "ветка",
    head: "head",
    footerReport: "ПОСЛЕДНИЙ ОТЧЕТ",
    footerReceipt: "ПОСЛЕДНИЙ RECEIPT",
    footerEvent: "СВОДКА СОБЫТИЙ",
    footerHealth: "ЗДОРОВЬЕ КОМАНД",
    actionRun: "Запуск действия",
    actionNote: "Это прототипный action-surface.",
    unknown: "unknown",
    active: "active",
    placeholder: "placeholder"
  }
};

const ORGANS = [
  { id: "MECHANICUS", title: "MECHANICUS", hint: "tooling corridor", left: 14, top: 58, active: true },
  { id: "ADMINISTRATUM", title: "ADMINISTRATUM", hint: "truth receipts", left: 14, top: 24 },
  { id: "OFFICIO", title: "OFFICIO", hint: "agent control", left: 39, top: 12 },
  { id: "INQUISITION", title: "INQUISITION", hint: "gate audits", left: 68, top: 18 },
  { id: "STRATEGIUM", title: "STRATEGIUM", hint: "runtime plans", left: 70, top: 62 },
  { id: "CUSTODES", title: "CUSTODES", hint: "guard layer", left: 39, top: 74 }
];

const TOOLS = {
  MECHANICUS: [
    ["git", "ok"],
    ["node", "ok"],
    ["npm", "ok"],
    ["playwright", "warn"],
    ["jsonschema", "warn"]
  ],
  ADMINISTRATUM: [
    ["receipt_checker", "ok"],
    ["scope_audit", "ok"],
    ["delta_report", "warn"]
  ],
  OFFICIO: [
    ["agent_registry", "ok"],
    ["role_guard", "ok"],
    ["observer_pack", "warn"]
  ],
  INQUISITION: [
    ["gate_lint", "ok"],
    ["fake_green_scan", "ok"],
    ["deep_perf_probe", "warn"]
  ],
  STRATEGIUM: [
    ["timeline_planner", "ok"],
    ["impact_matrix", "warn"],
    ["rollback_map", "ok"]
  ],
  CUSTODES: [
    ["boundary_guard", "ok"],
    ["owner_gate_lock", "ok"],
    ["risk_ledger", "warn"]
  ]
};

const CONTOUR = {
  MECHANICUS: [
    ["Windows readiness", "ok"],
    ["Ubuntu parity", "warn"],
    ["Contour verification", "ok"]
  ],
  ADMINISTRATUM: [
    ["Receipt binding", "ok"],
    ["Path truth", "ok"],
    ["Output budget", "ok"]
  ],
  OFFICIO: [
    ["Role admission", "ok"],
    ["Agent trace", "warn"],
    ["Stop conditions", "ok"]
  ],
  INQUISITION: [
    ["Gate audit", "ok"],
    ["No fake green", "ok"],
    ["Alert density", "warn"]
  ],
  STRATEGIUM: [
    ["Roadmap fit", "ok"],
    ["Risk projection", "warn"],
    ["Execution lane", "ok"]
  ],
  CUSTODES: [
    ["Boundary lock", "ok"],
    ["Guard relay", "ok"],
    ["Escalation route", "warn"]
  ]
};

const ACTIONS = [
  "send_prompt_to_vm",
  "fetch_bundle",
  "build_continuity",
  "run_audit",
  "dirty_state_inspection",
  "contour_verification"
];

const WORK_FEED = [
  ["18:20", "Seed import completed", "owner intake + visual contract materialized"],
  ["18:24", "Tokenization completed", "style mix applied to token layer and CSS export"],
  ["18:29", "Component state mapping", "brain field + right panel + contour cards wired"],
  ["18:33", "Proof preparation", "playwright screenshot set configured"],
  ["18:36", "Gate ack pass", "stop conditions and scope boundaries acknowledged"]
];

const FOOTER = [
  ["footerReport", "validation_report.json"],
  ["footerReceipt", "FINAL_RECEIPT.json"],
  ["footerEvent", "WARN=2 ERROR=0 BLOCK=0"],
  ["footerHealth", "RAW SECONDARY / SPLIT-SCREEN ACTIVE"]
];

let locale = "ru";
let rawVisible = false;
let activeOrgan = "MECHANICUS";

const el = {
  eyebrow: document.getElementById("eyebrow"),
  mainTitle: document.getElementById("mainTitle"),
  mission: document.getElementById("mission"),
  truthChips: document.getElementById("truthChips"),
  langSwitch: document.getElementById("langSwitch"),
  rawToggle: document.getElementById("rawToggle"),
  brainTitle: document.getElementById("brainTitle"),
  brainNote: document.getElementById("brainNote"),
  brainStatus: document.getElementById("brainStatus"),
  organGrid: document.getElementById("organGrid"),
  workTitle: document.getElementById("workTitle"),
  workFeed: document.getElementById("workFeed"),
  panelTitle: document.getElementById("panelTitle"),
  panelTag: document.getElementById("panelTag"),
  panelNote: document.getElementById("panelNote"),
  toolsTitle: document.getElementById("toolsTitle"),
  contourTitle: document.getElementById("contourTitle"),
  actionsTitle: document.getElementById("actionsTitle"),
  toolList: document.getElementById("toolList"),
  contourList: document.getElementById("contourList"),
  actionGrid: document.getElementById("actionGrid"),
  rawMode: document.getElementById("rawMode"),
  rawTitle: document.getElementById("rawTitle"),
  rawText: document.getElementById("rawText"),
  footerStrip: document.getElementById("footerStrip")
};

function t(key) {
  return I18N[locale][key] ?? key;
}

function stateClass(value) {
  if (value === "ok") return "ok";
  if (value === "warn") return "warn";
  return "error";
}

function renderTruth() {
  const chips = [
    [t("scope"), "IMPERIUM_NEW_GENERATION"],
    [t("branch"), "master"],
    [t("head"), "f74e73c7"],
    [t("visual"), "contract_to_tokens_v0_1"]
  ];
  el.truthChips.innerHTML = "";
  chips.forEach(([k, v], index) => {
    const item = document.createElement("div");
    item.className = `chip ${index === 2 ? "warn" : "ok"}`;
    item.textContent = `${k}: ${v}`;
    el.truthChips.appendChild(item);
  });
}

function renderOrgans() {
  el.organGrid.innerHTML = "";
  ORGANS.forEach((organ) => {
    const node = document.createElement("button");
    node.type = "button";
    node.className = `organ-node ${activeOrgan === organ.id ? "is-active" : ""}`;
    node.style.left = `${organ.left}%`;
    node.style.top = `${organ.top}%`;
    node.innerHTML = `<strong>${organ.title}</strong><span>${organ.hint}</span>`;
    node.addEventListener("click", () => {
      activeOrgan = organ.id;
      renderOrgans();
      renderPanel();
    });
    el.organGrid.appendChild(node);
  });
}

function renderWorkFeed() {
  el.workFeed.innerHTML = "";
  WORK_FEED.forEach((item) => {
    const row = document.createElement("article");
    row.className = "feed-item";
    row.innerHTML = `
      <div class="line"><strong>${item[0]}</strong><span>${activeOrgan}</span></div>
      <p>${item[1]}: ${item[2]}</p>
    `;
    el.workFeed.appendChild(row);
  });
}

function renderPanel() {
  el.panelTag.textContent = `${t("state")}: ${t("active")}`;

  el.toolList.innerHTML = "";
  (TOOLS[activeOrgan] ?? []).forEach(([name, status]) => {
    const row = document.createElement("div");
    row.className = "tool-row";
    row.innerHTML = `<span>${name}</span><span class="state ${stateClass(status)}">${status.toUpperCase()}</span>`;
    el.toolList.appendChild(row);
  });

  el.contourList.innerHTML = "";
  (CONTOUR[activeOrgan] ?? []).forEach(([name, status]) => {
    const row = document.createElement("div");
    row.className = "contour-row";
    row.innerHTML = `<span>${name}</span><span class="state ${stateClass(status)}">${status.toUpperCase()}</span>`;
    el.contourList.appendChild(row);
  });

  el.actionGrid.innerHTML = "";
  ACTIONS.forEach((action) => {
    const btn = document.createElement("button");
    btn.type = "button";
    btn.className = "action-btn";
    btn.innerHTML = `<strong>${action}</strong><span>${t("actionNote")}</span>`;
    btn.addEventListener("click", () => {
      WORK_FEED.unshift([
        new Date().toLocaleTimeString(locale === "ru" ? "ru-RU" : "en-US", { hour: "2-digit", minute: "2-digit" }),
        `${t("actionRun")}: ${action}`,
        `${activeOrgan} panel updated`
      ]);
      WORK_FEED.splice(5);
      renderWorkFeed();
    });
    el.actionGrid.appendChild(btn);
  });

  const rawPayload = {
    active_organ: activeOrgan,
    scope: "IMPERIUM_NEW_GENERATION/SANCTUM_VISUAL_FOUNDRY/**",
    raw_mode: rawVisible ? "visible_secondary" : "hidden_secondary",
    forbidden_roots: ["ORGANS", "SANCTUM", "IMPERIUM_TEST_VERSION"],
    proof_targets: ["1366x768", "1920x1080", "right_panel", "top_truth_strip", "raw_secondary"]
  };
  el.rawText.textContent = JSON.stringify(rawPayload, null, 2);
}

function renderFooter() {
  el.footerStrip.innerHTML = "";
  FOOTER.forEach(([key, value]) => {
    const card = document.createElement("div");
    card.className = "footer-card";
    card.innerHTML = `<span class="k">${t(key)}</span><span class="v">${value}</span>`;
    el.footerStrip.appendChild(card);
  });
}

function renderText() {
  el.eyebrow.textContent = t("eyebrow");
  el.mainTitle.textContent = t("title");
  el.mission.textContent = t("mission");
  el.brainTitle.textContent = t("brainTitle");
  el.brainNote.textContent = t("brainNote");
  el.brainStatus.textContent = t("brainStatus");
  el.workTitle.textContent = t("workTitle");
  el.panelTitle.textContent = `${t("panelTitle")} // ${activeOrgan}`;
  el.panelNote.textContent = t("panelNote");
  el.toolsTitle.textContent = t("toolsTitle");
  el.contourTitle.textContent = t("contourTitle");
  el.actionsTitle.textContent = t("actionsTitle");
  el.rawTitle.textContent = t("rawTitle");
  el.langSwitch.textContent = locale === "ru" ? "EN" : "RU";
  el.rawToggle.textContent = rawVisible ? t("rawOn") : t("rawOff");
}

function setRawMode(next) {
  rawVisible = next;
  el.rawMode.classList.toggle("is-hidden", !rawVisible);
  el.rawToggle.textContent = rawVisible ? t("rawOn") : t("rawOff");
  renderPanel();
}

function render() {
  renderText();
  renderTruth();
  renderOrgans();
  renderWorkFeed();
  renderPanel();
  renderFooter();
}

el.langSwitch.addEventListener("click", () => {
  locale = locale === "ru" ? "en" : "ru";
  render();
});

el.rawToggle.addEventListener("click", () => setRawMode(!rawVisible));

setRawMode(false);
render();
