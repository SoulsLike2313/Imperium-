const TOOL_SNAPSHOT = [
  { tool_id: "git", owner_organ: "ADMINISTRATUM_AGENT", pc_status: "AVAILABLE_PC", combined_status: "AVAILABLE_BOTH" },
  { tool_id: "ripgrep", owner_organ: "INQUISITION_AGENT", pc_status: "AVAILABLE_PC", combined_status: "AVAILABLE_BOTH" },
  { tool_id: "ruff", owner_organ: "MECHANICUS_AGENT", pc_status: "NOT_FOUND_ON_PC", combined_status: "AVAILABLE_VM2" },
  { tool_id: "pytest", owner_organ: "MECHANICUS_AGENT", pc_status: "AVAILABLE_PC", combined_status: "AVAILABLE_PC" },
  { tool_id: "jsonschema", owner_organ: "DOCTRINARIUM_AGENT", pc_status: "NOT_FOUND_ON_PC", combined_status: "AVAILABLE_VM2" },
  { tool_id: "jq", owner_organ: "ADMINISTRATUM_AGENT", pc_status: "AVAILABLE_PC", combined_status: "AVAILABLE_BOTH" },
  { tool_id: "yq", owner_organ: "ADMINISTRATUM_AGENT", pc_status: "AVAILABLE_PC", combined_status: "AVAILABLE_BOTH" },
  { tool_id: "gitleaks", owner_organ: "INQUISITION_AGENT", pc_status: "NOT_FOUND_ON_PC", combined_status: "KNOWN_NOT_INSTALLED" },
  { tool_id: "semgrep", owner_organ: "INQUISITION_AGENT", pc_status: "NOT_FOUND_ON_PC", combined_status: "KNOWN_NOT_INSTALLED" },
  { tool_id: "bandit", owner_organ: "INQUISITION_AGENT", pc_status: "NOT_FOUND_ON_PC", combined_status: "KNOWN_NOT_INSTALLED" }
];

const COMMANDS = [
  { cmd: "status", detail: "Show organ status and health", key: "F1" },
  { cmd: "tools", detail: "List tool registry and capabilities", key: "F2" },
  { cmd: "identity", detail: "Show organ identity and mission", key: "F3" },
  { cmd: "check", detail: "Run validations and integrity checks", key: "F4" },
  { cmd: "where", detail: "Show paths and active worktree", key: "F5" },
  { cmd: "help", detail: "Show admitted command lanes", key: "F6" },
  { cmd: "raw", detail: "Open explicit raw detail lane", key: "F7" },
  { cmd: "screenshot", detail: "Capture visual evidence lane", key: "F8" },
  { cmd: "clear", detail: "Reset command output lane", key: "ESC" }
];

const ACTIVITY_BY_STATE = {
  idle: [
    ["12:54:01", "G", "Registry sync", "Tool index loaded from snapshot", "IDLE"],
    ["12:54:03", "T", "Truth lane", "Backend source remains CANDIDATE", "UNKNOWN"],
    ["12:54:05", "S", "SSE", "Live stream is intentionally STUB", "STUB"],
    ["12:54:08", "C", "Command zone", "Allowlist is ready, no active dispatch", "IDLE"]
  ],
  active: [
    ["12:56:10", "W", "where", "Mechanicus path summary validated", "ACTIVE"],
    ["12:56:15", "S", "status", "Visual slice state transitioned to ACTIVE", "ACTIVE"],
    ["12:56:17", "T", "tools", "Registry counters refreshed", "ACTIVE"],
    ["12:56:21", "R", "raw", "Diagnostic lane returned bounded output", "ACTIVE"]
  ],
  warn: [
    ["12:58:02", "A", "allowlist", "One requested command is not admitted", "WARN"],
    ["12:58:05", "B", "backend", "State source is candidate, not real", "WARN"],
    ["12:58:08", "E", "evidence", "Latest report path unresolved", "UNKNOWN"],
    ["12:58:11", "S", "transport", "SSE remains STUB in this isolated lab", "STUB"]
  ],
  blocked: [
    ["13:01:44", "X", "git status", "Blocked: command not in allowlist", "BLOCKED"],
    ["13:01:46", "L", "privileged lane", "LOCKED command class requires owner gate", "LOCKED"],
    ["13:01:49", "T", "truth", "No fake PASS emitted under blocked state", "OK"],
    ["13:01:52", "S", "safety", "Scope boundary preserved", "OK"]
  ],
  unknown: [
    ["13:05:14", "?", "state source", "No fresh runtime payload", "UNKNOWN"],
    ["13:05:18", "?", "activity", "Last signal timestamp unavailable", "UNKNOWN"],
    ["13:05:22", "?", "evidence", "Latest receipt unresolved", "UNKNOWN"],
    ["13:05:28", "I", "operator", "Fallback static mode enabled", "IDLE"]
  ]
};

const body = document.body;
const statePill = document.getElementById("statePill");
const activityList = document.getElementById("activityList");
const commandGrid = document.getElementById("commandGrid");
const toolRows = document.getElementById("toolRows");
const motionToggle = document.getElementById("motionToggle");
const chargeField = document.getElementById("chargeField");

let reducedMotion = false;

function stateClassName(state) {
  return `state-${state.toLowerCase()}`;
}

function chipClass(status) {
  const normalized = status.toLowerCase();
  if (normalized === "active" || normalized === "ok") return "chip-active";
  if (normalized === "idle") return "chip-idle";
  if (normalized === "warn") return "chip-warn";
  if (normalized === "blocked" || normalized === "error" || normalized === "locked") return "chip-blocked";
  if (normalized === "stub") return "chip-warn";
  return "chip-unknown";
}

function renderCommands() {
  commandGrid.innerHTML = "";
  for (const row of COMMANDS) {
    const card = document.createElement("article");
    card.className = "command-card";
    card.innerHTML = [
      `<strong>${row.cmd}</strong>`,
      `<small>${row.detail}</small>`,
      `<span class="keycap">${row.key}</span>`
    ].join("");
    commandGrid.appendChild(card);
  }
  document.getElementById("metricCmds").textContent = String(COMMANDS.length);
}

function renderTools() {
  const declaredRegisteredCount = 20;
  const snapshotRowsCount = TOOL_SNAPSHOT.length;
  const available = TOOL_SNAPSHOT.filter((tool) => tool.pc_status === "AVAILABLE_PC").length;
  const warnings = TOOL_SNAPSHOT.filter((tool) => tool.pc_status !== "AVAILABLE_PC").length;
  const errors = TOOL_SNAPSHOT.filter((tool) => tool.combined_status === "KNOWN_NOT_INSTALLED").length;

  document.getElementById("countRegistered").textContent = `${declaredRegisteredCount} (rows:${snapshotRowsCount})`;
  document.getElementById("countAvailable").textContent = String(available);
  document.getElementById("countWarnings").textContent = String(warnings);
  document.getElementById("countErrors").textContent = String(errors);

  toolRows.innerHTML = "";
  for (const row of TOOL_SNAPSHOT) {
    const tr = document.createElement("tr");
    tr.innerHTML = [
      `<td>${row.tool_id}</td>`,
      `<td>${row.owner_organ}</td>`,
      `<td>${row.pc_status}</td>`,
      `<td>${row.combined_status}</td>`
    ].join("");
    toolRows.appendChild(tr);
  }
}

function renderActivity(state) {
  activityList.innerHTML = "";
  const entries = ACTIVITY_BY_STATE[state] ?? ACTIVITY_BY_STATE.unknown;
  let warnCount = 0;
  let blockedCount = 0;

  for (const [time, glyph, item, detail, status] of entries) {
    const lowered = status.toLowerCase();
    if (lowered === "warn" || lowered === "stub" || lowered === "unknown") warnCount += 1;
    if (lowered === "blocked" || lowered === "locked") blockedCount += 1;

    const li = document.createElement("li");
    li.innerHTML = [
      `<span class="time-tag">${time}</span>`,
      `<span class="item-glyph">${glyph}</span>`,
      `<div><p class="item-title">${item}</p><p class="item-detail">${detail}</p></div>`,
      `<span class="state-chip ${chipClass(status)}">${status}</span>`
    ].join("");
    activityList.appendChild(li);
  }

  document.getElementById("metricWarn").textContent = String(warnCount);
  document.getElementById("metricBlock").textContent = String(blockedCount);
}

function setState(nextState) {
  body.classList.remove("state-idle", "state-active", "state-warn", "state-blocked", "state-unknown");
  body.classList.add(stateClassName(nextState));
  statePill.textContent = `STATE: ${nextState.toUpperCase()}`;
  renderActivity(nextState);
}

function setupStateButtons() {
  for (const button of document.querySelectorAll("[data-state]")) {
    button.addEventListener("click", () => setState(button.dataset.state || "unknown"));
  }
}

function setupReducedMotionToggle() {
  motionToggle.addEventListener("click", () => {
    reducedMotion = !reducedMotion;
    body.classList.toggle("reduced-motion", reducedMotion);
    motionToggle.textContent = `Reduced Motion: ${reducedMotion ? "ON" : "OFF"}`;
  });
}

function renderChargeField() {
  if (!chargeField) return;
  chargeField.innerHTML = "";
  const nodeCount = 24;
  for (let i = 0; i < nodeCount; i += 1) {
    const node = document.createElement("span");
    node.className = "charge-node";
    const x = 8 + (Math.random() * 84);
    const y = 22 + (Math.random() * 72);
    const dur = 10 + (Math.random() * 8);
    const delay = -(Math.random() * 12);
    node.style.setProperty("--x", `${x}%`);
    node.style.setProperty("--y", `${y}%`);
    node.style.setProperty("--dur", `${dur.toFixed(2)}s`);
    node.style.setProperty("--delay", `${delay.toFixed(2)}s`);
    chargeField.appendChild(node);
  }
}

renderCommands();
renderTools();
renderChargeField();
renderActivity("active");
setupStateButtons();
setupReducedMotionToggle();
