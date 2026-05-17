const SNAPSHOT_PATH = "../reports/neural_base_snapshot_v0_4.json";

function esc(s) {
  return String(s ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll("\"", "&quot;");
}

function pill(status) {
  const safe = esc(status || "UNKNOWN");
  return `<span class="status-pill ${safe}">${safe}</span>`;
}

function kv(target, key, value) {
  target.insertAdjacentHTML(
    "beforeend",
    `<div class="k">${esc(key)}</div><div class="v">${esc(value)}</div>`
  );
}

function renderMeta(snapshot) {
  const node = document.getElementById("snapshot-meta");
  node.innerHTML = "";
  kv(node, "Snapshot Timestamp", snapshot.timestamp_utc || "UNKNOWN");
  kv(node, "Scope", snapshot.scope_policy || "UNKNOWN");
  kv(node, "Feature Count", String(snapshot.features?.length || 0));
  kv(node, "Action Count", String(snapshot.actions?.length || 0));
  kv(node, "Truth Entries", String(snapshot.truth_mappings?.length || 0));
  kv(node, "Missing Sources", String(snapshot.metrics?.missing_sources_count ?? "UNKNOWN"));
}

function renderFeatures(snapshot) {
  const box = document.getElementById("feature-list");
  box.innerHTML = "";
  (snapshot.features || []).forEach((f) => {
    box.insertAdjacentHTML(
      "beforeend",
      `<article class="card">
        <h3>${esc(f.title)} ${pill(f.status)}</h3>
        <div class="line">id: ${esc(f.id)}</div>
        <div class="line">zone: ${esc(f.visual_zone)}</div>
        <div class="line">truth: ${pill(f.backend_truth_status || "UNKNOWN")}</div>
        <div class="line">limitations: ${(f.current_limitations || []).map(esc).join(" | ")}</div>
      </article>`
    );
  });
}

function renderTruth(snapshot) {
  const box = document.getElementById("truth-list");
  box.innerHTML = "";
  (snapshot.truth_mappings || []).forEach((m) => {
    box.insertAdjacentHTML(
      "beforeend",
      `<article class="card">
        <h3>${esc(m.ui_element)}</h3>
        <div class="line">${esc(m.description || "")}</div>
        <div class="line">sources: ${(m.source_patterns || []).map(esc).join(" ; ")}</div>
        <div class="line">missing count: ${esc(String(m.missing_sources_count ?? 0))}</div>
      </article>`
    );
  });
}

function renderActions(snapshot) {
  const box = document.getElementById("action-list");
  box.innerHTML = "";
  (snapshot.actions || []).forEach((a) => {
    box.insertAdjacentHTML(
      "beforeend",
      `<article class="card">
        <h3>${esc(a.label)} ${pill(a.type)}</h3>
        <div class="line">id: ${esc(a.action_id)}</div>
        <div class="line">status: ${esc(a.status)}</div>
        <div class="line">owner gate: ${esc(String(a.owner_gate_required))}</div>
        <div class="line">writes receipt: ${esc(String(a.writes_receipt))}</div>
      </article>`
    );
  });
}

function renderEvidence(snapshot) {
  const box = document.getElementById("evidence-list");
  box.innerHTML = "";
  const m = snapshot.metrics || {};
  box.insertAdjacentHTML(
    "beforeend",
    `<article class="card">
      <h3>Runtime Evidence</h3>
      <div class="line">source paths checked: ${esc(String(m.total_source_paths ?? 0))}</div>
      <div class="line">source paths present: ${esc(String(m.present_sources_count ?? 0))}</div>
      <div class="line">source paths missing: ${esc(String(m.missing_sources_count ?? 0))}</div>
      <div class="line">receipts found: ${esc(String(m.receipts_count ?? 0))}</div>
      <div class="line">exports found: ${esc(String(m.exports_count ?? 0))}</div>
    </article>`
  );

  const missing = snapshot.missing_sources || [];
  box.insertAdjacentHTML(
    "beforeend",
    `<article class="card">
      <h3>Missing Source Paths</h3>
      <div class="line">${missing.length ? missing.map(esc).join(" ; ") : "none"}</div>
    </article>`
  );
}

function render(snapshot) {
  renderMeta(snapshot);
  renderFeatures(snapshot);
  renderTruth(snapshot);
  renderActions(snapshot);
  renderEvidence(snapshot);
}

async function loadSnapshot() {
  try {
    const res = await fetch(SNAPSHOT_PATH, { cache: "no-store" });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    render(data);
  } catch (err) {
    const fallback = {
      timestamp_utc: "UNAVAILABLE",
      scope_policy: "IMPERIUM_TEST_VERSION_ONLY",
      features: [],
      actions: [],
      truth_mappings: [],
      metrics: {
        total_source_paths: 0,
        present_sources_count: 0,
        missing_sources_count: 0,
        receipts_count: 0,
        exports_count: 0
      },
      missing_sources: [],
      note: "Snapshot fetch failed. Run local server or build snapshot."
    };
    render(fallback);
    const meta = document.getElementById("snapshot-meta");
    kv(meta, "Load Error", err.message);
    kv(meta, "Fallback", "Snapshot fetch blocked or missing");
  }
}

document.addEventListener("DOMContentLoaded", loadSnapshot);

