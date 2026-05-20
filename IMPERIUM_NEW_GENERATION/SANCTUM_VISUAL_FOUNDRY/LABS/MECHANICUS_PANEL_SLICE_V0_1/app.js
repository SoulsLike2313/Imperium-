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
  ["status", "Show organ status & health"],
  ["tools", "List tool registry & capabilities"],
  ["identity", "Show organ identity & mission"],
  ["check", "Run validations & integrity checks"],
  ["where", "Show paths & active worktree"],
  ["help", "Show admitted command lanes"],
  ["raw", "Open explicit raw detail lane"],
  ["screenshot", "Capture visual evidence lane"],
  ["clear", "Reset command output lane"]
];

const ACTIVITY_BY_STATE = {
  idle: [
    ["12:54:01", "Registry sync", "Tool index loaded from snapshot", "IDLE"],
    ["12:54:03", "Truth lane", "Backend source remains CANDIDATE", "UNKNOWN"],
    ["12:54:05", "SSE", "Live stream is intentionally STUB", "STUB"],
    ["12:54:08", "Command zone", "Allowlist is ready, no active dispatch", "IDLE"]
  ],
  active: [
    ["12:56:10", "where", "Mechanicus path summary validated", "ACTIVE"],
    ["12:56:15", "status", "Visual slice state transitioned to ACTIVE", "ACTIVE"],
    ["12:56:17", "tools", "Registry counters refreshed", "ACTIVE"],
    ["12:56:21", "raw", "Diagnostic lane returned bounded output", "ACTIVE"]
  ],
  warn: [
    ["12:58:02", "allowlist", "One requested command is not admitted", "WARN"],
    ["12:58:05", "backend", "State source is candidate, not real", "WARN"],
    ["12:58:08", "evidence", "Latest report path unresolved", "UNKNOWN"],
    ["12:58:11", "transport", "SSE remains STUB in this isolated lab", "STUB"]
  ],
  blocked: [
    ["13:01:44", "git status", "Blocked: command not in allowlist", "BLOCKED"],
    ["13:01:46", "privileged lane", "LOCKED command class requires owner gate", "LOCKED"],
    ["13:01:49", "truth", "No fake PASS emitted under blocked state", "OK"],
    ["13:01:52", "safety", "Scope boundary preserved", "OK"]
  ],
  unknown: [
    ["13:05:14", "state source", "No fresh runtime payload", "UNKNOWN"],
    ["13:05:18", "activity", "Last signal timestamp unavailable", "UNKNOWN"],
    ["13:05:22", "evidence", "Latest receipt unresolved", "UNKNOWN"],
    ["13:05:28", "operator", "Fallback static mode enabled", "IDLE"]
  ]
};

const body = document.body;
const statePill = document.getElementById("statePill");
const activityList = document.getElementById("activityList");
const commandGrid = document.getElementById("commandGrid");
const toolRows = document.getElementById("toolRows");
const motionToggle = document.getElementById("motionToggle");

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
  for (const [cmd, description] of COMMANDS) {
    const card = document.createElement("article");
    card.className = "command-card";
    card.innerHTML = `<strong>${cmd}</strong><small>${description}</small>`;
    commandGrid.appendChild(card);
  }
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
  for (const [time, item, detail, status] of entries) {
    const li = document.createElement("li");
    li.innerHTML = [
      `<span class="time-tag">${time}</span>`,
      `<div><p class="item-title">${item}</p><p class="item-detail">${detail}</p></div>`,
      `<span class="state-chip ${chipClass(status)}">${status}</span>`
    ].join("");
    activityList.appendChild(li);
  }
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

renderCommands();
renderTools();
renderActivity("active");
setupStateButtons();
setupReducedMotionToggle();
