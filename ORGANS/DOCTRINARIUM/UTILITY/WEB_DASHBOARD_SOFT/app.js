let DATA = null;
let lastFrame = performance.now();
let fps = 60;

const $ = (id) => document.getElementById(id);

function showToast(text) {
  const t = $("toast");
  t.textContent = text;
  t.classList.remove("hidden");
  setTimeout(() => t.classList.add("hidden"), 3200);
}

async function loadData() {
  const res = await fetch("/api/data?ts=" + Date.now());
  DATA = await res.json();
  renderAll();
}

async function runRefresh() {
  showToast("Running Doctrinarium refresh...");
  const res = await fetch("/api/refresh", { method: "POST" });
  const data = await res.json();
  if (data.ok) showToast("Refresh complete");
  else showToast("Refresh failed: " + (data.error || data.exit_code));
  await loadData();
}

async function openTarget(target) {
  await fetch("/api/open?target=" + encodeURIComponent(target), { method: "POST" });
}

function setText(id, value) {
  const el = $(id);
  if (el) el.textContent = value;
}

function pct(n, d) {
  if (!d || d <= 0) return 0;
  return Math.max(0, Math.min(100, Math.round((n / d) * 100)));
}

function setBar(id, p) {
  const el = $(id);
  if (el) el.style.width = p + "%";
}

function ring(id, p) {
  const c = $(id);
  if (!c) return;
  const circ = 2 * Math.PI * 48;
  c.style.strokeDasharray = circ;
  c.style.strokeDashoffset = circ - (circ * p / 100);
}

function severityClass(blockers) {
  if (blockers >= 9) return "critical";
  if (blockers >= 4) return "risk";
  return "ok";
}

function boolMark(v) {
  return v ? "OK" : "MISS";
}

function renderAll() {
  const s = DATA.status || {};
  const g = DATA.gaps || {};
  const u = DATA.utility || {};
  const laws = DATA.laws || {};
  const paths = DATA.paths || {};

  const totalLaws = s?.law_registry_status?.total_laws || 0;
  const notEnforced = s?.law_registry_status?.not_fully_enforced_count || 0;
  const hardOpen = s?.law_registry_status?.hard_not_fully_enforced_count || 0;

  const organsChecked = g.total_organs_checked || 0;
  const blockers = g.total_blockers_found || 0;

  const uBacked = u?.summary?.script_backed_count || 0;
  const uDeclared = u?.summary?.utility_declared_count || 0;
  const uWarnings = u?.summary?.warnings_count || 0;

  setText("mRealTask", s.real_task_execution_allowed ? "ALLOWED" : "BLOCKED");
  setText("mBootstrap", s.bootstrap_review_allowed ? "ALLOWED" : "TRUE");
  setText("mDoctrine", "OWNER REVIEW");
  setText("mLaws", `${notEnforced} / ${totalLaws}`);
  setText("mOrgans", `${organsChecked} / ${organsChecked}`);
  setText("mBlockers", blockers);
  setText("mUtilities", `${uBacked} / ${uDeclared || 0}`);

  setText("orbText", s.real_task_execution_allowed ? "PASS" : "BLOCKED");

  const doctrinePct = (s.passport_status && s.constitution_status && s.codex_status) ? 68 : 0;
  const lawsPct = totalLaws ? 100 - pct(notEnforced, totalLaws) : 0;
  const organPct = organsChecked ? Math.max(0, 100 - Math.min(100, blockers * 2)) : 0;
  const utilityPct = pct(uBacked, organsChecked);

  setBar("barDoctrine", doctrinePct);
  setBar("barLaws", lawsPct);
  setBar("barOrgans", organPct);
  setBar("barUtility", utilityPct);
  setText("pctDoctrine", doctrinePct + "%");
  setText("pctLaws", lawsPct + "%");
  setText("pctOrgans", organPct + "%");
  setText("pctUtility", utilityPct + "%");

  const healthy = (g.organs || []).filter(o => (o.blockers || []).length === 0).length;
  const risk = (g.organs || []).filter(o => (o.blockers || []).length > 0 && (o.blockers || []).length < 9).length;
  const critical = (g.organs || []).filter(o => (o.blockers || []).length >= 9).length;
  const health = pct(healthy, organsChecked);

  setText("healthPct", health + "%");
  setText("healthGood", healthy);
  setText("healthRisk", risk);
  setText("healthCritical", critical);
  setText("healthVerdict", g.verdict || "unknown");
  setText("statusTotal", `${organsChecked} total`);

  $("lineGood").style.width = pct(healthy, organsChecked) + "%";
  $("lineRisk").style.width = pct(risk, organsChecked) + "%";
  $("lineCritical").style.width = pct(critical, organsChecked) + "%";
  ring("healthRing", health);

  setText("utilityVerdict", u.verdict || "unknown");
  setText("utilityPct", utilityPct + "%");
  setText("uDeclared", uDeclared);
  setText("uBacked", uBacked);
  setText("uWarnings", uWarnings);
  ring("utilityRing", utilityPct);

  setText("lTotal", totalLaws);
  setText("lOpen", notEnforced);
  setText("lHard", hardOpen);
  setText("lawZero", (100 - pct(notEnforced, totalLaws)) + "%");

  renderTopOrganRows(g.organs || []);
  renderOrganCards(g.organs || []);
  renderGapList(g.major_gaps || []);
  renderUtilityCards(u.organs || []);
  renderLawList(laws);
  renderPaths(paths);
  drawStatusDonut(g);
  drawRadar(g);
  drawTrend();
}

function renderTopOrganRows(organs) {
  const tb = $("topOrganRows");
  tb.innerHTML = "";
  const sorted = [...organs].sort((a,b) => (b.blockers || []).length - (a.blockers || []).length).slice(0, 7);
  for (const o of sorted) {
    const blockers = (o.blockers || []).length;
    const tr = document.createElement("tr");
    const topGap = (o.blockers || [])[0] || "-";
    tr.innerHTML = `
      <td>${o.organ_id}</td>
      <td><span class="badge ${severityClass(blockers)}">${o.classification}</span></td>
      <td>${blockers}</td>
      <td>${boolMark(o.organ_contract_exists)}</td>
      <td>${boolMark(o.self_report_exists)}</td>
      <td>${boolMark(o.receipts_exists)}</td>
      <td>${topGap}</td>
    `;
    tb.appendChild(tr);
  }
}

function renderOrganCards(organs) {
  const root = $("organCards");
  root.innerHTML = "";
  for (const o of organs) {
    const blockers = (o.blockers || []).length;
    const div = document.createElement("div");
    div.className = "organ-card";
    div.innerHTML = `
      <h3>${o.organ_id} <span class="badge ${severityClass(blockers)}">${o.classification}</span></h3>
      <div class="meta">
        <div>Path: ${o.path}</div>
        <div>Blockers: ${blockers}</div>
        <div>Contract: ${boolMark(o.organ_contract_exists)}</div>
        <div>Self-report: ${boolMark(o.self_report_exists)}</div>
        <div>Receipts: ${boolMark(o.receipts_exists)}</div>
        <div>Why not canon: ${(o.why_not_canon || []).join("; ") || "-"}</div>
      </div>
    `;
    root.appendChild(div);
  }
}

function renderGapList(gaps) {
  $("gapCountLabel").textContent = `${gaps.length} gaps`;
  const root = $("gapList");
  root.innerHTML = "";
  for (const gap of gaps) {
    const div = document.createElement("div");
    div.className = "gap-card";
    div.innerHTML = `<h3>${gap.organ}</h3><p>${gap.gap}</p>`;
    root.appendChild(div);
  }
}

function renderUtilityCards(organs) {
  const root = $("utilityCards");
  root.innerHTML = "";
  for (const o of organs) {
    const warnings = [...(o.warnings || []), ...(o.blockers || [])];
    const div = document.createElement("div");
    div.className = "organ-card";
    div.innerHTML = `
      <h3>${o.organ_id} <span class="badge ${o.script_backed ? "ok" : "risk"}">${o.script_backed ? "script-backed" : "not backed"}</span></h3>
      <div class="meta">
        <div>Status: ${o.organ_status}</div>
        <div>Utility declared: ${o.utility_declared}</div>
        <div>Utility path: ${o.utility_path || "-"}</div>
        <div>Warnings: ${warnings.join("; ") || "-"}</div>
      </div>
    `;
    root.appendChild(div);
  }
}

function getLawArray(laws) {
  if (!laws) return [];
  if (Array.isArray(laws.laws)) return laws.laws;
  if (Array.isArray(laws.mandatory_laws)) return laws.mandatory_laws;
  if (Array.isArray(laws.entries)) return laws.entries;
  return [];
}

function renderLawList(laws) {
  const arr = getLawArray(laws);
  $("lawCountLabel").textContent = `${arr.length} laws`;
  const root = $("lawList");
  root.innerHTML = "";
  for (const law of arr) {
    const div = document.createElement("div");
    div.className = "law-card";
    div.innerHTML = `
      <h3><span class="law-id">${law.law_id || "LAW"}</span> - ${law.title || ""}</h3>
      <div class="meta">
        <div>Severity: ${law.severity || "-"}</div>
        <div>Status: ${law.status || "-"}</div>
        <div>Enforcement: ${law.enforcement_status || "-"}</div>
        <div>Verdict: ${law.violation_verdict || "-"}</div>
        <div>Source: ${law.source_document_path || "-"}</div>
      </div>
    `;
    root.appendChild(div);
  }
}

function renderPaths(paths) {
  $("pathsText").textContent = Object.entries(paths || {}).map(([k,v]) => `${k}:\n  ${v}`).join("\n\n");
}

function drawStatusDonut(g) {
  const canvas = $("statusDonut");
  const ctx = canvas.getContext("2d");
  const r = canvas.getBoundingClientRect();
  canvas.width = r.width * devicePixelRatio;
  canvas.height = r.height * devicePixelRatio;
  ctx.scale(devicePixelRatio, devicePixelRatio);
  ctx.clearRect(0,0,r.width,r.height);

  const summary = g.classification_summary || {};
  const entries = Object.entries(summary);
  const total = entries.reduce((s, [,v]) => s + Number(v), 0) || 1;
  const colors = ["#45d483", "#ffd45a", "#ff4f6d", "#b45cff", "#53a7ff"];

  let start = -Math.PI/2;
  const cx = r.width/2, cy = r.height/2, rad = Math.min(r.width,r.height)/2 - 18;

  entries.forEach(([key,val], i) => {
    const a = (Number(val)/total) * Math.PI * 2;
    ctx.beginPath();
    ctx.arc(cx, cy, rad, start, start+a);
    ctx.lineWidth = 28;
    ctx.strokeStyle = colors[i % colors.length];
    ctx.stroke();
    start += a;
  });

  ctx.fillStyle = "#edf2ff";
  ctx.font = "bold 24px Segoe UI";
  ctx.textAlign = "center";
  ctx.fillText(total, cx, cy);
  ctx.font = "11px Segoe UI";
  ctx.fillStyle = "#9ca8c3";
  ctx.fillText("TOTAL", cx, cy + 20);

  const legend = $("statusLegend");
  legend.innerHTML = "";
  entries.forEach(([key,val], i) => {
    const div = document.createElement("div");
    div.innerHTML = `<span><i style="background:${colors[i % colors.length]}"></i>${key}</span><b>${val}</b>`;
    legend.appendChild(div);
  });
}

function drawRadar(g) {
  const canvas = $("radarCanvas");
  const ctx = canvas.getContext("2d");
  const r = canvas.getBoundingClientRect();
  canvas.width = r.width * devicePixelRatio;
  canvas.height = r.height * devicePixelRatio;
  ctx.scale(devicePixelRatio, devicePixelRatio);
  ctx.clearRect(0,0,r.width,r.height);

  const labels = ["FOLDER", "UNKNOWN", "SCAFFOLD", "CONTRACT", "GAPS"];
  const summary = g.classification_summary || {};
  const vals = [
    summary.FOLDER_ONLY || 0,
    summary.UNKNOWN || 0,
    summary.SCAFFOLD || 0,
    (g.major_gaps || []).filter(x => String(x.gap).includes("ORGAN_CONTRACT")).length,
    Math.min(10, Math.round((g.total_blockers_found || 0)/6))
  ];
  const max = Math.max(1, ...vals);
  const cx = r.width/2, cy = r.height/2 + 10;
  const rad = Math.min(r.width, r.height)/2 - 35;

  ctx.strokeStyle = "rgba(255,255,255,.12)";
  ctx.fillStyle = "rgba(180,92,255,.16)";
  for (let layer=1; layer<=4; layer++) {
    ctx.beginPath();
    for (let i=0; i<labels.length; i++) {
      const a = -Math.PI/2 + (i/labels.length)*Math.PI*2;
      const rr = rad * layer/4;
      const x = cx + Math.cos(a)*rr, y = cy + Math.sin(a)*rr;
      if (i===0) ctx.moveTo(x,y); else ctx.lineTo(x,y);
    }
    ctx.closePath(); ctx.stroke();
  }

  ctx.beginPath();
  vals.forEach((v,i) => {
    const a = -Math.PI/2 + (i/labels.length)*Math.PI*2;
    const rr = rad * v/max;
    const x = cx + Math.cos(a)*rr, y = cy + Math.sin(a)*rr;
    if (i===0) ctx.moveTo(x,y); else ctx.lineTo(x,y);
  });
  ctx.closePath();
  ctx.fillStyle = "rgba(180,92,255,.35)";
  ctx.fill();
  ctx.strokeStyle = "#ff4fd8";
  ctx.lineWidth = 2;
  ctx.stroke();

  ctx.fillStyle = "#9ca8c3";
  ctx.font = "11px Segoe UI";
  ctx.textAlign = "center";
  labels.forEach((label,i) => {
    const a = -Math.PI/2 + (i/labels.length)*Math.PI*2;
    ctx.fillText(label, cx + Math.cos(a)*(rad+22), cy + Math.sin(a)*(rad+22));
  });
}

function drawTrend() {
  const canvas = $("trendCanvas");
  const ctx = canvas.getContext("2d");
  const r = canvas.getBoundingClientRect();
  canvas.width = r.width * devicePixelRatio;
  canvas.height = r.height * devicePixelRatio;
  ctx.scale(devicePixelRatio, devicePixelRatio);
  ctx.clearRect(0,0,r.width,r.height);

  const pts = Array.from({length: 28}, (_,i) => {
    return 0.45 + Math.sin(i*0.55)*0.12 + Math.random()*0.08;
  });

  ctx.beginPath();
  pts.forEach((p,i) => {
    const x = (i/(pts.length-1))*r.width;
    const y = r.height - p*r.height;
    if (i===0) ctx.moveTo(x,y); else ctx.lineTo(x,y);
  });
  ctx.strokeStyle = "#b45cff";
  ctx.lineWidth = 2;
  ctx.stroke();

  const grad = ctx.createLinearGradient(0,0,0,r.height);
  grad.addColorStop(0, "rgba(180,92,255,.45)");
  grad.addColorStop(1, "rgba(180,92,255,0)");
  ctx.lineTo(r.width,r.height);
  ctx.lineTo(0,r.height);
  ctx.closePath();
  ctx.fillStyle = grad;
  ctx.fill();
}

function animateBg(now) {
  const canvas = $("bgCanvas");
  const ctx = canvas.getContext("2d");

  const pixelW = Math.max(1, Math.floor(window.innerWidth * devicePixelRatio));
  const pixelH = Math.max(1, Math.floor(window.innerHeight * devicePixelRatio));

  if (canvas.width !== pixelW || canvas.height !== pixelH) {
    canvas.width = pixelW;
    canvas.height = pixelH;
  }

  ctx.setTransform(devicePixelRatio, 0, 0, devicePixelRatio, 0, 0);

  const W = window.innerWidth;
  const H = window.innerHeight;

  ctx.clearRect(0, 0, W, H);

  for (let wave = 0; wave < 2; wave++) {
    ctx.beginPath();
    const yBase = H - 110 - wave * 24;

    for (let x = 0; x <= W; x += 10) {
      const y =
        yBase +
        Math.sin(x * 0.009 + now * 0.00065 + wave) * 10 +
        Math.sin(x * 0.019 + now * 0.00045) * 4;
      if (x === 0) ctx.moveTo(x, y);
      else ctx.lineTo(x, y);
    }

    ctx.strokeStyle = `rgba(185, 150, 255, ${0.10 + wave * 0.04})`;
    ctx.lineWidth = 1.1;
    ctx.shadowBlur = 10;
    ctx.shadowColor = "rgba(185,150,255,0.22)";
    ctx.stroke();
  }

  for (let i = 0; i < 26; i++) {
    const x = ((Math.sin(i * 41.7 + now * 0.00008) + 1) / 2) * W;
    const y = ((Math.cos(i * 27.3 + now * 0.00011) + 1) / 2) * H;
    const a = 0.04 + (Math.sin(now * 0.0008 + i) + 1) * 0.03;
    ctx.fillStyle = `rgba(217, 140, 255, ${a})`;
    ctx.fillRect(x, y, 1.2, 1.2);
  }

  const dt = now - lastFrame;
  lastFrame = now;
  fps = Math.round(1000 / Math.max(1, dt));
  $("fpsValue").textContent = Math.min(99, fps);

  requestAnimationFrame(animateBg);
}

function animateSpark(now) {
  const canvas = $("sparkCanvas");
  const ctx = canvas.getContext("2d");
  const r = canvas.getBoundingClientRect();

  const pixelW = Math.max(1, Math.floor(r.width * devicePixelRatio));
  const pixelH = Math.max(1, Math.floor(r.height * devicePixelRatio));

  if (canvas.width !== pixelW || canvas.height !== pixelH) {
    canvas.width = pixelW;
    canvas.height = pixelH;
  }

  ctx.setTransform(devicePixelRatio, 0, 0, devicePixelRatio, 0, 0);
  ctx.clearRect(0, 0, r.width, r.height);

  ctx.beginPath();
  for (let x = 0; x < r.width; x += 8) {
    const y =
      r.height / 2 +
      Math.sin(x * 0.03 + now * 0.0022) * 5 +
      Math.sin(x * 0.11 + now * 0.0012) * 2;
    if (x === 0) ctx.moveTo(x, y);
    else ctx.lineTo(x, y);
  }

  ctx.strokeStyle = "rgba(185,150,255,0.60)";
  ctx.lineWidth = 1.2;
  ctx.shadowBlur = 6;
  ctx.shadowColor = "rgba(185,150,255,0.30)";
  ctx.stroke();

  requestAnimationFrame(animateSpark);
}

document.querySelectorAll(".nav-item").forEach(btn => {
  btn.addEventListener("click", () => {
    document.querySelectorAll(".nav-item").forEach(b => b.classList.remove("active"));
    btn.classList.add("active");
    const view = btn.dataset.view;
    document.querySelectorAll(".view").forEach(v => v.classList.remove("active"));
    $(`view-${view}`).classList.add("active");
  });
});

document.querySelectorAll("[data-view-jump]").forEach(btn => {
  btn.addEventListener("click", () => {
    const v = btn.dataset.viewJump;
    document.querySelector(`.nav-item[data-view="${v}"]`)?.click();
  });
});

document.querySelectorAll("[data-open]").forEach(btn => {
  btn.addEventListener("click", () => openTarget(btn.dataset.open));
});

$("btnRefresh").addEventListener("click", runRefresh);
$("btnReload").addEventListener("click", loadData);

loadData().catch(err => showToast("Load failed: " + err.message));
requestAnimationFrame(animateBg);
requestAnimationFrame(animateSpark);

