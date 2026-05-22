(function () {
  const DATA_PATH = "../DATA/sanctum_ng_state.generated.json";

  const I18N = {
    en: {
      kicker: "IMPERIUM NEW GENERATION",
      title: "Sanctum Truth Shell V0.1",
      subtitle: "Read-only foundation truth surface over phases 1-10.",
      labels: {
        task: "Task",
        head: "HEAD",
        mode: "Mode",
        worktree: "Worktree",
        generated: "Generated"
      },
      railTitle: "Pipeline Zones",
      warningsTitle: "Known Warnings",
      commTitle: "Communication Gate",
      pipelineTitle: "Foundation Pipeline 1-10",
      inspectorTitle: "Phase Inspector",
      inspectorEmpty: "Select a phase to inspect details.",
      inspectorPaths: "Paths",
      inspectorReports: "Report paths",
      inspectorLimits: "Limitations",
      inspectorSnapshot: "JSON snapshot",
      actionsTitle: "Action Strip",
      worktreeClean: "clean",
      worktreeDirty: "dirty",
      loadWarn: "Local file fetch blocked; fallback snapshot is shown.",
      actionNames: {
        refresh_truth: "Refresh Truth",
        open_reports: "Open Reports",
        validate: "Validate",
        create_task: "Create Task",
        consult_organs: "Consult Organs"
      }
    },
    ru: {
      kicker: "IMPERIUM НОВОЕ ПОКОЛЕНИЕ",
      title: "Sanctum Truth Shell V0.1",
      subtitle: "Read-only foundation truth surface over phases 1-10.",
      labels: {
        task: "Задача",
        head: "HEAD",
        mode: "Режим",
        worktree: "Дерево",
        generated: "Сгенерировано"
      },
      railTitle: "Зоны контура",
      warningsTitle: "Известные предупреждения",
      commTitle: "Гейт коммуникации",
      pipelineTitle: "Фундаментальный конвейер 1-10",
      inspectorTitle: "Инспектор фазы",
      inspectorEmpty: "Выберите фазу для просмотра деталей.",
      inspectorPaths: "Пути",
      inspectorReports: "Пути отчётов",
      inspectorLimits: "Ограничения",
      inspectorSnapshot: "JSON-снимок",
      actionsTitle: "Панель действий",
      worktreeClean: "чисто",
      worktreeDirty: "грязно",
      loadWarn: "Чтение local file через fetch заблокировано; показан резервный снимок.",
      actionNames: {
        refresh_truth: "Обновить правду",
        open_reports: "Открыть отчёты",
        validate: "Проверить",
        create_task: "Создать задачу",
        consult_organs: "Консультация органов"
      }
    }
  };

  const FALLBACK_STATE = {
    schema_id: "SANCTUM_NG_STATE_V0_1",
    task_id: "TASK-20260522-NEWGEN-SANCTUM-TRUTH-SHELL-RUNNER-AND-OFFICIO-REPAIR-VM3-V0_1",
    mode: "READ_ONLY_FOUNDATION",
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
      AUTHORITY_SOURCE: ["FALLBACK"],
      STATUS: "WARN_FOUNDATION_ONLY",
      KNOWN_LIMITATION: "Fallback state is active."
    },
    phases: [
      { phase_no: 1, name: "Architecture", status: "FOUNDATION", summary: "Fallback snapshot.", evidence_refs: ["FALLBACK"], paths: [], report_paths: [], limitations: ["CLI builder state not loaded."] },
      { phase_no: 2, name: "Organ Packets", status: "FOUNDATION", summary: "Fallback snapshot.", evidence_refs: ["FALLBACK"], paths: [], report_paths: [], limitations: ["CLI builder state not loaded."] },
      { phase_no: 3, name: "Task Kernel", status: "FOUNDATION", summary: "Fallback snapshot.", evidence_refs: ["FALLBACK"], paths: [], report_paths: [], limitations: ["CLI builder state not loaded."] },
      { phase_no: 4, name: "Astronomicon", status: "FOUNDATION", summary: "Fallback snapshot.", evidence_refs: ["FALLBACK"], paths: [], report_paths: [], limitations: ["CLI builder state not loaded."] },
      { phase_no: 5, name: "Authority Gates", status: "WARN", summary: "Fallback snapshot.", evidence_refs: ["FALLBACK"], paths: [], report_paths: [], limitations: ["CLI builder state not loaded."] },
      { phase_no: 6, name: "Servitor Loop", status: "FOUNDATION", summary: "Fallback snapshot.", evidence_refs: ["FALLBACK"], paths: [], report_paths: [], limitations: ["CLI builder state not loaded."] },
      { phase_no: 7, name: "Evidence Binder", status: "FOUNDATION", summary: "Fallback snapshot.", evidence_refs: ["FALLBACK"], paths: [], report_paths: [], limitations: ["CLI builder state not loaded."] },
      { phase_no: 8, name: "Visual Brain", status: "FOUNDATION", summary: "Fallback snapshot.", evidence_refs: ["FALLBACK"], paths: [], report_paths: [], limitations: ["CLI builder state not loaded."] },
      { phase_no: 9, name: "Skill Growth", status: "FOUNDATION", summary: "Fallback snapshot.", evidence_refs: ["FALLBACK"], paths: [], report_paths: [], limitations: ["CLI builder state not loaded."] },
      { phase_no: 10, name: "Tool Admission", status: "FOUNDATION", summary: "Fallback snapshot.", evidence_refs: ["FALLBACK"], paths: [], report_paths: [], limitations: ["CLI builder state not loaded."] }
    ],
    actions: {
      refresh_truth: "NOT_WIRED_LOCAL_FILE_ONLY",
      open_reports: "PREVIEW_ONLY",
      validate: "RUN_CLI_NOT_FROM_BROWSER",
      create_task: "NOT_WIRED",
      consult_organs: "NOT_WIRED"
    }
  };

  const state = {
    lang: "en",
    data: null,
    selectedPhaseNo: null
  };

  function statusClass(status) {
    return `status-${String(status || "").toLowerCase()}`;
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

  function setText(id, text) {
    const el = document.getElementById(id);
    if (el) {
      el.textContent = text;
    }
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
    setText("pipeline-title", t.pipelineTitle);
    setText("inspector-title", t.inspectorTitle);
    setText("inspector-empty", t.inspectorEmpty);
    setText("inspector-paths-label", t.inspectorPaths);
    setText("inspector-reports-label", t.inspectorReports);
    setText("inspector-limits-label", t.inspectorLimits);
    setText("inspector-snapshot-label", t.inspectorSnapshot);
    setText("actions-title", t.actionsTitle);

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
      card.addEventListener("click", () => {
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

  function renderActions() {
    const t = I18N[state.lang];
    const actions = state.data.actions || {};
    const container = document.getElementById("action-buttons");
    container.innerHTML = "";

    const order = ["refresh_truth", "open_reports", "validate", "create_task", "consult_organs"];
    order.forEach((key) => {
      const card = document.createElement("div");
      card.className = "action-card";
      card.innerHTML = `<strong>${t.actionNames[key]}</strong><span>${actions[key] || "NOT_WIRED"}</span>`;
      container.appendChild(card);
    });
  }

  function renderAll() {
    setLabels();
    renderTruthBar();
    renderRail();
    renderCommunicationGate();
    renderPipeline();
    renderInspector();
    renderActions();
  }

  async function loadData() {
    try {
      const response = await fetch(DATA_PATH, { cache: "no-store" });
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }
      const json = await response.json();
      state.data = normalizeData(json);
    } catch (error) {
      state.data = normalizeData({ ...FALLBACK_STATE });
      state.data.warnings = state.data.warnings || [];
      state.data.warnings.push(I18N[state.lang].loadWarn);
      state.data.warnings.push(`LOAD_ERROR:${String(error)}`);
    }
  }

  async function bootstrap() {
    const langBtn = document.getElementById("lang-toggle");
    langBtn.addEventListener("click", function () {
      state.lang = state.lang === "en" ? "ru" : "en";
      renderAll();
    });

    await loadData();
    if (!state.selectedPhaseNo) {
      state.selectedPhaseNo = 1;
    }
    renderAll();
  }

  bootstrap();
})();
