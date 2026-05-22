(function () {
  const REQUIRED_ACTION_ORDER = [
    "REFRESH_TRUTH_STATE",
    "VALIDATE_TRUTH_STATE",
    "READ_PHASE_REGISTRY",
    "READ_ACTION_REGISTRY",
    "READ_LATEST_REPORT_SUMMARY"
  ];

  const ACTION_LAYER_STATE_MODEL = {
    action: ["ACTION_ALLOWED", "ACTION_DISABLED"],
    result: [
      "ACTION_RESULT_PASS",
      "ACTION_RESULT_WARN",
      "ACTION_RESULT_BLOCK",
      "ACTION_RESULT_PARTIAL"
    ]
  };

  const I18N = {
    en: {
      kicker: "IMPERIUM NEW GENERATION",
      title: "Sanctum Truth Shell V0.1",
      subtitle: "Foundation truth surface with file-backed action layer.",
      labels: {
        task: "Task",
        head: "HEAD",
        mode: "Mode",
        worktree: "Worktree",
        generated: "Generated",
        registryStatus: "Registry Status",
        reportSummaryStatus: "Report Summary",
        resultModelState: "Result Model",
        lastActionStatus: "Last Action Status",
        lastActionPath: "Result Path",
        lastActionSummary: "Result Summary"
      },
      railTitle: "Pipeline Zones",
      warningsTitle: "Known Warnings",
      commTitle: "Communication Gate",
      truthIndexTitle: "Current Truth Index",
      truthIndexLabels: {
        status: "STATUS",
        currentTruthRoot: "CURRENT_TRUTH_ROOT",
        reportStatusIndex: "REPORT_STATUS_INDEX",
        evidenceSourceMap: "EVIDENCE_SOURCE_MAP",
        evidenceMapUnified: "EVIDENCE_MAP_UNIFIED",
        evidenceFreshnessIndex: "EVIDENCE_FRESHNESS_INDEX",
        sync: "SYNC"
      },
      pipelineTitle: "Foundation Pipeline 1-10",
      inspectorTitle: "Phase Inspector",
      inspectorEmpty: "Select a phase to inspect details.",
      inspectorPaths: "Paths",
      inspectorReports: "Report paths",
      inspectorLimits: "Limitations",
      inspectorSnapshot: "JSON snapshot",
      actionsTitle: "Action Layer",
      lastActionJsonTitle: "Last Action Result JSON",
      foundationNote: "Foundation-only layer. No production/autonomous claim.",
      worktreeClean: "clean",
      worktreeDirty: "dirty",
      serverConnected: "CONNECTED",
      serverNotConnected: "NOT_CONNECTED",
      serverUnknown: "UNKNOWN",
      serverNotConnectedFile: "ACTION_SERVER_NOT_CONNECTED (file:// mode)",
      serverNotConnectedRuntime: "ACTION_SERVER_NOT_CONNECTED",
      serverConnectedNote: "Local action server is connected.",
      runAction: "Run",
      previewOnly: "Preview only",
      unavailable: "Unavailable",
      running: "RUNNING",
      statusUnknown: "UNKNOWN",
      noResult: "No action result yet.",
      noEvidenceDowngrade: "PASS_WITHOUT_EVIDENCE_DOWNGRADED_TO_WARN"
    },
    ru: {
      kicker: "IMPERIUM НОВОЕ ПОКОЛЕНИЕ",
      title: "Sanctum Truth Shell V0.1",
      subtitle: "Foundation truth surface with file-backed action layer.",
      labels: {
        task: "Задача",
        head: "HEAD",
        mode: "Режим",
        worktree: "Дерево",
        generated: "Сгенерировано",
        registryStatus: "Статус реестра",
        reportSummaryStatus: "Сводка отчётов",
        resultModelState: "Модель результата",
        lastActionStatus: "Статус последнего действия",
        lastActionPath: "Путь результата",
        lastActionSummary: "Сводка результата"
      },
      railTitle: "Зоны контура",
      warningsTitle: "Известные предупреждения",
      commTitle: "Гейт коммуникации",
      truthIndexTitle: "Индекс текущей правды",
      truthIndexLabels: {
        status: "СТАТУС",
        currentTruthRoot: "CURRENT_TRUTH_ROOT",
        reportStatusIndex: "REPORT_STATUS_INDEX",
        evidenceSourceMap: "EVIDENCE_SOURCE_MAP",
        evidenceMapUnified: "EVIDENCE_MAP_UNIFIED",
        evidenceFreshnessIndex: "EVIDENCE_FRESHNESS_INDEX",
        sync: "СИНХРОН"
      },
      pipelineTitle: "Фундаментальный конвейер 1-10",
      inspectorTitle: "Инспектор фазы",
      inspectorEmpty: "Выберите фазу для просмотра деталей.",
      inspectorPaths: "Пути",
      inspectorReports: "Пути отчётов",
      inspectorLimits: "Ограничения",
      inspectorSnapshot: "JSON-снимок",
      actionsTitle: "Слой действий",
      lastActionJsonTitle: "JSON последнего результата",
      foundationNote: "Только foundation-слой. Без production/autonomous claim.",
      worktreeClean: "чисто",
      worktreeDirty: "грязно",
      serverConnected: "CONNECTED",
      serverNotConnected: "NOT_CONNECTED",
      serverUnknown: "UNKNOWN",
      serverNotConnectedFile: "ACTION_SERVER_NOT_CONNECTED (file:// режим)",
      serverNotConnectedRuntime: "ACTION_SERVER_NOT_CONNECTED",
      serverConnectedNote: "Локальный action server подключен.",
      runAction: "Запустить",
      previewOnly: "Только превью",
      unavailable: "Недоступно",
      running: "ВЫПОЛНЯЕТСЯ",
      statusUnknown: "UNKNOWN",
      noResult: "Результат действия пока отсутствует.",
      noEvidenceDowngrade: "PASS без evidence понижен до WARN"
    }
  };

  const FALLBACK_STATE = {
    schema_id: "SANCTUM_NG_STATE_V0_1",
    task_id: "TASK-20260522-NEWGEN-SANCTUM-ACTION-LAYER-HARDENING-VM3-V0_1",
    mode: "ACTION_LAYER_FOUNDATION_ONLY",
    generated_at_utc: "FALLBACK",
    git: {
      head: "UNKNOWN",
      branch: "UNKNOWN",
      worktree_dirty: false
    },
    warnings: ["FALLBACK_STATE_ACTIVE"],
    communication_gate: {
      LIVE_LANGUAGE_COMPLIANCE: "RUSSIAN_OWNER_PROGRESS_REQUIRED",
      FINAL_REPORT_LANGUAGE: "RUSSIAN_REQUIRED",
      TECHNICAL_ARTIFACT_LANGUAGE: "ENGLISH_ALLOWED",
      AUTHORITY_SOURCE: [
        "IMPERIUM_NEW_GENERATION/AUTHORITY_DRAFTS/OFFICIO_LIVE_COMMUNICATION_ENFORCEMENT_V0_1.md"
      ],
      STATUS: "WARN_FOUNDATION_ONLY",
      KNOWN_LIMITATION: "Fallback state is active; runtime hard-block is not claimed."
    },
    current_truth_index: {
      current_truth_root_path: "IMPERIUM_NEW_GENERATION/TRUTH/CURRENT_TRUTH_ROOT_V0_1.json",
      report_status_index_path: "IMPERIUM_NEW_GENERATION/TRUTH/REPORT_STATUS_INDEX_V0_1.json",
      evidence_source_map_path: "IMPERIUM_NEW_GENERATION/TRUTH/EVIDENCE_SOURCE_MAP_V0_1.json",
      evidence_map_unified_path: "IMPERIUM_NEW_GENERATION/TRUTH/EVIDENCE_MAP_UNIFIED_V0_1.json",
      evidence_freshness_index_path: "IMPERIUM_NEW_GENERATION/TRUTH/EVIDENCE_FRESHNESS_INDEX_V0_1.json",
      status: "UNKNOWN",
      last_sync_utc: "UNKNOWN"
    },
    phases: [
      { phase_no: 1, name: "Architecture", status: "FOUNDATION", summary: "Fallback snapshot.", evidence_refs: ["FALLBACK"], paths: [], report_paths: [], limitations: ["State API unavailable."] },
      { phase_no: 2, name: "Organ Packets", status: "FOUNDATION", summary: "Fallback snapshot.", evidence_refs: ["FALLBACK"], paths: [], report_paths: [], limitations: ["State API unavailable."] },
      { phase_no: 3, name: "Task Kernel", status: "FOUNDATION", summary: "Fallback snapshot.", evidence_refs: ["FALLBACK"], paths: [], report_paths: [], limitations: ["State API unavailable."] },
      { phase_no: 4, name: "Astronomicon", status: "FOUNDATION", summary: "Fallback snapshot.", evidence_refs: ["FALLBACK"], paths: [], report_paths: [], limitations: ["State API unavailable."] },
      { phase_no: 5, name: "Authority Gates", status: "WARN", summary: "Fallback snapshot.", evidence_refs: ["FALLBACK"], paths: [], report_paths: [], limitations: ["State API unavailable."] },
      { phase_no: 6, name: "Servitor Loop", status: "FOUNDATION", summary: "Fallback snapshot.", evidence_refs: ["FALLBACK"], paths: [], report_paths: [], limitations: ["State API unavailable."] },
      { phase_no: 7, name: "Evidence Binder", status: "FOUNDATION", summary: "Fallback snapshot.", evidence_refs: ["FALLBACK"], paths: [], report_paths: [], limitations: ["State API unavailable."] },
      { phase_no: 8, name: "Visual Brain", status: "FOUNDATION", summary: "Fallback snapshot.", evidence_refs: ["FALLBACK"], paths: [], report_paths: [], limitations: ["State API unavailable."] },
      { phase_no: 9, name: "Skill Growth", status: "FOUNDATION", summary: "Fallback snapshot.", evidence_refs: ["FALLBACK"], paths: [], report_paths: [], limitations: ["State API unavailable."] },
      { phase_no: 10, name: "Tool Admission", status: "FOUNDATION", summary: "Fallback snapshot.", evidence_refs: ["FALLBACK"], paths: [], report_paths: [], limitations: ["State API unavailable."] }
    ]
  };

  const FALLBACK_ACTIONS = [
    {
      action_id: "REFRESH_TRUTH_STATE",
      title: "Refresh Sanctum Truth State",
      description: "Requires local action server.",
      status: "NOT_WIRED",
      safety_level: "SAFE_LOCAL_SCRIPT_ONLY",
      allowed_commands: [],
      allowed_paths: [],
      forbidden_paths: ["*"],
      writes_files: [],
      evidence_refs: [],
      known_limitations: ["ACTION_SERVER_NOT_CONNECTED"]
    },
    {
      action_id: "VALIDATE_TRUTH_STATE",
      title: "Validate Sanctum Truth State",
      description: "Requires local action server.",
      status: "NOT_WIRED",
      safety_level: "SAFE_LOCAL_SCRIPT_ONLY",
      allowed_commands: [],
      allowed_paths: [],
      forbidden_paths: ["*"],
      writes_files: [],
      evidence_refs: [],
      known_limitations: ["ACTION_SERVER_NOT_CONNECTED"]
    },
    {
      action_id: "READ_PHASE_REGISTRY",
      title: "Read Phase Registry",
      description: "Requires local action server.",
      status: "NOT_WIRED",
      safety_level: "SAFE_READ_FIXED_PATH",
      allowed_commands: [],
      allowed_paths: [],
      forbidden_paths: ["*"],
      writes_files: [],
      evidence_refs: [],
      known_limitations: ["ACTION_SERVER_NOT_CONNECTED"]
    },
    {
      action_id: "READ_ACTION_REGISTRY",
      title: "Read Action Registry",
      description: "Requires local action server.",
      status: "NOT_WIRED",
      safety_level: "SAFE_READ_FIXED_PATH",
      allowed_commands: [],
      allowed_paths: [],
      forbidden_paths: ["*"],
      writes_files: [],
      evidence_refs: [],
      known_limitations: ["ACTION_SERVER_NOT_CONNECTED"]
    },
    {
      action_id: "READ_LATEST_REPORT_SUMMARY",
      title: "Read Latest Report Summary",
      description: "Requires local action server.",
      status: "NOT_WIRED",
      safety_level: "SAFE_READ_FIXED_REPORT_SET",
      allowed_commands: [],
      allowed_paths: [],
      forbidden_paths: ["*"],
      writes_files: [],
      evidence_refs: [],
      known_limitations: ["ACTION_SERVER_NOT_CONNECTED"]
    }
  ];

  const state = {
    lang: "en",
    data: null,
    actions: [],
    selectedPhaseNo: null,
    serverStatus: "UNKNOWN",
    connectionNote: "",
    lastActionResult: null,
    registryStatus: "UNKNOWN",
    reportSummaryState: "UNKNOWN",
    reportSummaryReason: "-",
    lastActionModelState: "ACTION_RESULT_WARN",
    actionLayerStateModel: null
  };

  function byOrder(actions) {
    const order = new Map(REQUIRED_ACTION_ORDER.map((id, idx) => [id, idx]));
    return actions.slice().sort((a, b) => {
      const ax = order.has(a.action_id) ? order.get(a.action_id) : 999;
      const bx = order.has(b.action_id) ? order.get(b.action_id) : 999;
      return ax - bx;
    });
  }

  function normalizeData(rawData) {
    const data = rawData && typeof rawData === "object" ? rawData : FALLBACK_STATE;
    const phases = Array.isArray(data.phases) ? data.phases.slice() : [];
    phases.sort((a, b) => Number(a.phase_no) - Number(b.phase_no));

    const warnings = Array.isArray(data.warnings) ? data.warnings.slice() : [];

    phases.forEach((phase) => {
      const refs = Array.isArray(phase.evidence_refs) ? phase.evidence_refs : [];
      if (phase.status === "PROVED" && refs.length === 0) {
        phase.status = "WARN";
        warnings.push(`PHASE_${phase.phase_no}_PROVED_WITHOUT_EVIDENCE_DOWNGRADED`);
      }
    });

    if (!data.communication_gate || typeof data.communication_gate !== "object") {
      data.communication_gate = { ...FALLBACK_STATE.communication_gate };
      warnings.push("COMMUNICATION_GATE_FALLBACK_ACTIVE");
    }

    data.phases = phases;
    data.warnings = warnings;
    return data;
  }

  function normalizeActions(rawActions) {
    const source = Array.isArray(rawActions) ? rawActions : FALLBACK_ACTIONS;
    const actions = source
      .filter((item) => item && typeof item === "object")
      .map((item) => ({
        action_id: String(item.action_id || "UNKNOWN_ACTION"),
        title: String(item.title || item.action_id || "Unknown Action"),
        description: String(item.description || ""),
        status: String(item.status || "NOT_WIRED"),
        availability_state: String(item.availability_state || "ACTION_DISABLED"),
        safety_level: String(item.safety_level || "UNKNOWN"),
        allowed_commands: Array.isArray(item.allowed_commands) ? item.allowed_commands : [],
        allowed_paths: Array.isArray(item.allowed_paths) ? item.allowed_paths : [],
        forbidden_paths: Array.isArray(item.forbidden_paths) ? item.forbidden_paths : [],
        writes_files: Array.isArray(item.writes_files) ? item.writes_files : [],
        evidence_refs: Array.isArray(item.evidence_refs) ? item.evidence_refs : [],
        known_limitations: Array.isArray(item.known_limitations) ? item.known_limitations : []
      }));

    return byOrder(actions);
  }

  function applyReportSummary(summaryPayload) {
    const payload = summaryPayload && typeof summaryPayload === "object" ? summaryPayload : {};
    const inner = payload.payload && typeof payload.payload === "object" ? payload.payload : {};
    state.reportSummaryState = String(inner.summary_state || "UNKNOWN");
    state.reportSummaryReason = String(inner.reason || "-");
  }

  function applyLatestActionResult(resultPayload) {
    if (!resultPayload || typeof resultPayload !== "object") {
      return;
    }
    state.lastActionResult = resultPayload;
    const model = resultPayload.state_model && typeof resultPayload.state_model === "object" ? resultPayload.state_model : {};
    state.lastActionModelState = String(model.result_state || "ACTION_RESULT_WARN");

    if (String(resultPayload.action_id || "") === "READ_LATEST_REPORT_SUMMARY") {
      applyReportSummary(resultPayload);
    }
  }

  function setText(id, text) {
    const el = document.getElementById(id);
    if (el) {
      el.textContent = text;
    }
  }

  function setStatusValue(id, value) {
    const el = document.getElementById(id);
    if (!el) {
      return;
    }
    const text = String(value || "UNKNOWN");
    el.textContent = text;
    el.className = `status-pill ${statusClass(text)}`;
  }

  function statusClass(status) {
    return `status-${String(status || "").toLowerCase().replace(/[^a-z0-9]+/g, "-")}`;
  }

  function setLabels() {
    const t = I18N[state.lang];
    setText("app-kicker", t.kicker);
    setText("app-title", t.title);
    setText("app-subtitle", t.subtitle);

    setText("label-task", t.labels.task);
    setText("label-head", t.labels.head);
    setText("label-mode", t.labels.mode);
    setText("label-worktree", t.labels.worktree);
    setText("label-generated", t.labels.generated);

    setText("rail-title", t.railTitle);
    setText("warnings-title", t.warningsTitle);
    setText("comm-title", t.commTitle);
    setText("truth-index-title", t.truthIndexTitle);
    setText("pipeline-title", t.pipelineTitle);

    setText("inspector-title", t.inspectorTitle);
    setText("inspector-empty", t.inspectorEmpty);
    setText("inspector-paths-label", t.inspectorPaths);
    setText("inspector-reports-label", t.inspectorReports);
    setText("inspector-limits-label", t.inspectorLimits);
    setText("inspector-snapshot-label", t.inspectorSnapshot);

    setText("actions-title", t.actionsTitle);
    setText("label-registry-status", t.labels.registryStatus);
    setText("label-report-summary-status", t.labels.reportSummaryStatus);
    setText("label-result-model-state", t.labels.resultModelState);
    setText("label-last-action-status", t.labels.lastActionStatus);
    setText("label-last-action-path", t.labels.lastActionPath);
    setText("label-last-action-summary", t.labels.lastActionSummary);
    setText("last-action-json-title", t.lastActionJsonTitle);
    setText("foundation-note", t.foundationNote);

    const langBtn = document.getElementById("lang-toggle");
    if (langBtn) {
      langBtn.textContent = state.lang === "en" ? "RU" : "EN";
    }
  }

  function renderTruthBar() {
    const t = I18N[state.lang];
    const data = state.data;
    const git = data.git || {};

    setText("truth-task", data.task_id || "-");
    setText("truth-head", git.head || "-");
    setText("truth-mode", data.mode || "-");
    setText("truth-worktree", git.worktree_dirty ? t.worktreeDirty : t.worktreeClean);
    setText("truth-generated", data.generated_at_utc || "-");
  }

  function renderRail() {
    const rail = document.getElementById("phase-rail");
    rail.innerHTML = "";

    state.data.phases.forEach((phase) => {
      const li = document.createElement("li");
      li.textContent = `${phase.phase_no}. ${phase.name}`;
      rail.appendChild(li);
    });

    const warnings = document.getElementById("warnings-list");
    warnings.innerHTML = "";
    (state.data.warnings || []).forEach((warning) => {
      const li = document.createElement("li");
      li.textContent = warning;
      warnings.appendChild(li);
    });
  }

  function renderPipeline() {
    const list = document.getElementById("pipeline-list");
    list.innerHTML = "";

    state.data.phases.forEach((phase) => {
      const card = document.createElement("button");
      card.type = "button";
      card.className = "phase-card";
      card.innerHTML = `
        <div class="phase-card__top">
          <span class="phase-name">${phase.phase_no}. ${phase.name}</span>
          <span class="status-pill ${statusClass(phase.status)}">${phase.status}</span>
        </div>
        <p class="phase-summary">${phase.summary || ""}</p>
      `;
      card.addEventListener("click", function () {
        state.selectedPhaseNo = phase.phase_no;
        renderInspector();
      });
      list.appendChild(card);
    });
  }

  function renderCommunicationGate() {
    const node = document.getElementById("comm-gate-list");
    node.innerHTML = "";

    const gate = state.data.communication_gate || {};
    const ordered = [
      "STATUS",
      "LIVE_LANGUAGE_COMPLIANCE",
      "FINAL_REPORT_LANGUAGE",
      "TECHNICAL_ARTIFACT_LANGUAGE",
      "KNOWN_LIMITATION"
    ];

    ordered.forEach((key) => {
      const li = document.createElement("li");
      li.textContent = `${key}: ${String(gate[key] || "-")}`;
      node.appendChild(li);
    });

    const sources = Array.isArray(gate.AUTHORITY_SOURCE) ? gate.AUTHORITY_SOURCE : [];
    if (sources.length > 0) {
      const li = document.createElement("li");
      li.textContent = `AUTHORITY_SOURCE: ${sources.join(" | ")}`;
      node.appendChild(li);
    }
  }

  function renderTruthIndex() {
    const t = I18N[state.lang];
    const data = state.data || {};
    const truthIndex = data.current_truth_index && typeof data.current_truth_index === "object"
      ? data.current_truth_index
      : {};

    setText("truth-root-status", `${t.truthIndexLabels.status}: ${String(truthIndex.status || "-")}`);
    setText(
      "truth-root-path",
      `${t.truthIndexLabels.currentTruthRoot}: ${String(truthIndex.current_truth_root_path || "-")}`
    );
    setText(
      "report-index-path",
      `${t.truthIndexLabels.reportStatusIndex}: ${String(truthIndex.report_status_index_path || "-")}`
    );
    setText(
      "evidence-map-path",
      `${t.truthIndexLabels.evidenceSourceMap}: ${String(truthIndex.evidence_source_map_path || "-")}`
    );
    setText(
      "evidence-map-unified-path",
      `${t.truthIndexLabels.evidenceMapUnified}: ${String(truthIndex.evidence_map_unified_path || "-")}`
    );
    setText(
      "freshness-index-path",
      `${t.truthIndexLabels.evidenceFreshnessIndex}: ${String(truthIndex.evidence_freshness_index_path || "-")}`
    );
    setText("truth-sync-utc", `${t.truthIndexLabels.sync}: ${String(truthIndex.last_sync_utc || "-")}`);
  }

  function renderInspector() {
    const phase = state.data.phases.find((item) => item.phase_no === state.selectedPhaseNo);
    const empty = document.getElementById("inspector-empty");
    const body = document.getElementById("inspector-body");

    if (!phase) {
      empty.classList.remove("hidden");
      body.classList.add("hidden");
      return;
    }

    empty.classList.add("hidden");
    body.classList.remove("hidden");

    setText("inspector-phase-name", `${phase.phase_no}. ${phase.name} [${phase.status}]`);
    setText("inspector-summary", phase.summary || "");

    renderList("inspector-paths", phase.paths || []);
    renderList("inspector-reports", phase.report_paths || []);
    renderList("inspector-limits", phase.limitations || []);

    const jsonBox = document.getElementById("inspector-json");
    jsonBox.textContent = JSON.stringify(phase, null, 2);
  }

  function renderList(id, items) {
    const node = document.getElementById(id);
    node.innerHTML = "";

    if (!Array.isArray(items) || items.length === 0) {
      const li = document.createElement("li");
      li.textContent = "-";
      node.appendChild(li);
      return;
    }

    items.forEach((item) => {
      const li = document.createElement("li");
      li.textContent = String(item);
      node.appendChild(li);
    });
  }

  function renderConnection() {
    const t = I18N[state.lang];
    const pill = document.getElementById("connection-status-pill");

    let label = t.serverUnknown;
    let note = state.connectionNote || "";

    if (state.serverStatus === "CONNECTED") {
      label = t.serverConnected;
      if (!note) {
        note = t.serverConnectedNote;
      }
    } else if (state.serverStatus === "NOT_CONNECTED") {
      label = t.serverNotConnected;
      if (!note) {
        note = t.serverNotConnectedRuntime;
      }
    }

    pill.className = `status-pill ${statusClass(label)}`;
    pill.textContent = label;
    setText("connection-note", note || t.serverUnknown);
  }

  function safeActionStatus(result) {
    if (!result || typeof result !== "object") {
      return I18N[state.lang].statusUnknown;
    }

    const status = String(result.status || I18N[state.lang].statusUnknown);
    const evidence = Array.isArray(result.evidence_refs) ? result.evidence_refs : [];

    if (status === "PASS" && evidence.length === 0) {
      return "WARN";
    }
    return status;
  }

  function renderLastActionResult() {
    const t = I18N[state.lang];
    const result = state.lastActionResult;

    setStatusValue("registry-status", state.registryStatus || "UNKNOWN");
    setStatusValue("report-summary-status", state.reportSummaryState || "UNKNOWN");
    setStatusValue("result-model-state", state.lastActionModelState || "ACTION_RESULT_WARN");

    if (!result || typeof result !== "object") {
      setStatusValue("last-action-status", "UNKNOWN");
      setText("last-action-path", "-");
      setText("last-action-summary", t.noResult);
      setText("last-action-json", "-");
      return;
    }

    const safeStatus = safeActionStatus(result);
    const evidence = Array.isArray(result.evidence_refs) ? result.evidence_refs : [];
    const downgrade = String(result.status) === "PASS" && evidence.length === 0;

    setStatusValue("last-action-status", safeStatus);
    setText("last-action-path", String(result.result_record_path || "-"));
    setText(
      "last-action-summary",
      downgrade ? `${String(result.output_summary || "")}; ${t.noEvidenceDowngrade}` : String(result.output_summary || "-")
    );
    setText("last-action-json", JSON.stringify(result, null, 2));
  }

  function renderActionCards() {
    const t = I18N[state.lang];
    const container = document.getElementById("action-cards");
    container.innerHTML = "";

    state.actions.forEach((action) => {
      const card = document.createElement("article");
      card.className = "action-card";

      const runEnabled =
        state.serverStatus === "CONNECTED" &&
        action.status === "WIRED" &&
        action.availability_state === "ACTION_ALLOWED";
      let buttonLabel = t.unavailable;
      if (action.status === "PREVIEW_ONLY") {
        buttonLabel = t.previewOnly;
      } else if (runEnabled) {
        buttonLabel = t.runAction;
      }

      const limits = Array.isArray(action.known_limitations) ? action.known_limitations : [];
      const evidence = Array.isArray(action.evidence_refs) ? action.evidence_refs : [];

      card.innerHTML = `
        <div class="action-card__top">
          <h3>${action.title}</h3>
          <span class="status-pill ${statusClass(action.status)}">${action.status}</span>
        </div>
        <p class="action-id">${action.action_id}</p>
        <p class="action-desc">${action.description}</p>
        <p class="action-safety">${action.availability_state}</p>
        <p class="action-safety">${action.safety_level}</p>
        <p class="action-evidence">evidence refs: ${evidence.length}</p>
        <ul class="action-limits"></ul>
      `;

      const limitsNode = card.querySelector(".action-limits");
      if (limits.length === 0) {
        const li = document.createElement("li");
        li.textContent = "-";
        limitsNode.appendChild(li);
      } else {
        limits.slice(0, 3).forEach((item) => {
          const li = document.createElement("li");
          li.textContent = String(item);
          limitsNode.appendChild(li);
        });
      }

      const btn = document.createElement("button");
      btn.type = "button";
      btn.className = "btn action-run";
      btn.textContent = buttonLabel;
      btn.disabled = !runEnabled;

      btn.addEventListener("click", async function () {
        await runAction(action.action_id);
      });

      card.appendChild(btn);
      container.appendChild(card);
    });
  }

  async function runAction(actionId) {
    const t = I18N[state.lang];
    if (state.serverStatus !== "CONNECTED") {
      state.connectionNote = t.serverNotConnectedRuntime;
      renderConnection();
      return;
    }

    state.lastActionResult = {
      status: t.running,
      result_record_path: "-",
      output_summary: `${actionId}: ${t.running}`,
      evidence_refs: []
    };
    renderLastActionResult();

    try {
      const response = await fetch(`/api/actions/${encodeURIComponent(actionId)}`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          requester: "SANCTUM_NG_UI",
          dry_run: false,
          input: {
            origin: "UI"
          }
        })
      });

      const payload = await response.json();
      applyLatestActionResult(payload && typeof payload === "object" ? payload : {
        status: "ERROR",
        result_record_path: "-",
        output_summary: "Invalid action response payload.",
        evidence_refs: [],
        state_model: {
          result_state: "ACTION_RESULT_BLOCK"
        }
      });
    } catch (error) {
      applyLatestActionResult({
        status: "ERROR",
        result_record_path: "-",
        output_summary: `ACTION_REQUEST_ERROR: ${String(error)}`,
        evidence_refs: [],
        state_model: {
          result_state: "ACTION_RESULT_BLOCK"
        }
      });
    }

    renderLastActionResult();
  }

  function renderAll() {
    setLabels();
    renderTruthBar();
    renderRail();
    renderCommunicationGate();
    renderTruthIndex();
    renderPipeline();
    renderInspector();
    renderConnection();
    renderActionCards();
    renderLastActionResult();
  }

  async function bootstrapData() {
    const t = I18N[state.lang];

    if (window.location.protocol === "file:") {
      state.serverStatus = "NOT_CONNECTED";
      state.connectionNote = t.serverNotConnectedFile;
      state.data = normalizeData({ ...FALLBACK_STATE });
      state.data.warnings.push("ACTION_SERVER_NOT_CONNECTED");
      state.actions = normalizeActions(FALLBACK_ACTIONS);
      state.registryStatus = "ACTION_DISABLED";
      state.reportSummaryState = "NOT_READY";
      state.reportSummaryReason = "file_mode_no_server";
      state.lastActionModelState = "ACTION_RESULT_WARN";
      return;
    }

    try {
      const stateRes = await fetch("/api/state", { cache: "no-store" });
      const actionsRes = await fetch("/api/actions", { cache: "no-store" });

      if (!stateRes.ok || !actionsRes.ok) {
        throw new Error(`api_status:${stateRes.status}/${actionsRes.status}`);
      }

      const statePayload = await stateRes.json();
      const actionsPayload = await actionsRes.json();

      state.data = normalizeData(statePayload && typeof statePayload === "object" ? statePayload.state : null);
      state.actions = normalizeActions(actionsPayload && typeof actionsPayload === "object" ? actionsPayload.actions : null);
      state.serverStatus = String((statePayload || {}).status || "CONNECTED");
      state.connectionNote = t.serverConnectedNote;
      state.registryStatus = String((((actionsPayload || {}).registry) || {}).status || "UNKNOWN");
      state.actionLayerStateModel = (statePayload || {}).action_layer_state_model || (actionsPayload || {}).action_layer_state_model || null;

      applyReportSummary((statePayload || {}).latest_report_summary || null);
      applyLatestActionResult((statePayload || {}).latest_action_result || null);
    } catch (error) {
      state.data = normalizeData({ ...FALLBACK_STATE });
      state.actions = normalizeActions(FALLBACK_ACTIONS);
      state.serverStatus = "NOT_CONNECTED";
      state.connectionNote = `${t.serverNotConnectedRuntime}; ${String(error)}`;
      state.data.warnings.push(`ACTION_LAYER_API_LOAD_ERROR:${String(error)}`);
      state.registryStatus = "ACTION_DISABLED";
      state.reportSummaryState = "NOT_READY";
      state.reportSummaryReason = "api_unreachable";
      state.lastActionModelState = "ACTION_RESULT_WARN";
    }
  }

  async function bootstrap() {
    const langBtn = document.getElementById("lang-toggle");
    langBtn.addEventListener("click", function () {
      state.lang = state.lang === "en" ? "ru" : "en";
      renderAll();
    });

    await bootstrapData();

    if (!state.selectedPhaseNo) {
      state.selectedPhaseNo = 1;
    }

    renderAll();
  }

  bootstrap();
})();
